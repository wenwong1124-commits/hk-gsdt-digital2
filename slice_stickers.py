#!/usr/bin/env python3
"""
Slice the sticker sheets into individual transparent cutouts and inline them
into design-system.html. Nothing is redrawn — this only cuts up artwork you
already made.

    python3 slice_stickers.py assets/stickers/sheet-a.png assets/stickers/sheet-b.png

Each sheet is a 3x4 grid of die-cut stickers on a flat magenta ground. For
each cell it:

  1. floods the magenta away from the edges inward, so magenta *inside* a
     sticker is never punched out by accident,
  2. trims to the remaining artwork, pads it back to a square so the physics
     bounding circle stays honest,
  3. writes a PNG to assets/stickers/cut/ and a base64 data URI into the
     IMAGES map in design-system.html.

Names are assigned in reading order from NAMES below. Edit that list to
change which cell becomes which sticker, or to drop cells you don't want:
a name of None skips the cell entirely.
"""
import sys, os, re, io, base64, pathlib
from collections import deque
from PIL import Image

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "assets" / "stickers" / "cut"
COLS, ROWS = 3, 4
TOL = 60          # colour distance that still counts as background
PAD = 0.06        # padding as a fraction of the square, so edges can breathe
SIZE = 256        # final square px
OVERLAP = 0.045   # crop past the cell edge so spill is recovered. Kept small
                  # on purpose: at 0.14 a sticker's white ring merges with its
                  # neighbour's into one blob whose centroid lands between the
                  # two cells, and the whole ring is discarded as a neighbour.
                  # Measured across all cells, 0.045 only ever adds area.

# Reading order, sheet A then sheet B. None = skip this cell.
NAMES = [
    # ---- sheet A ----
    "mic",   "brain", None,      # speech capture · cognition · (ear, cut)
    None,    "faces", None,      # (pipeline, cut) · two generations · (shield)
    "heart", None,    None,      # health data · (squares) · (magnet)
    "hands", None,    "mind",    # care · (cluster, cut) · human-centred AI
    # ---- sheet B ----
    "eye",   "globe", None,      # observation · reach · (marquee)
    None,    None,    None,      # (flame) · (peace) · (id cards)
    None,    None,    None,      # (asterisk) · (link) · (blend)
    "pen",   None,    "wand",    # design craft · (window) · AI
]


def bg_alpha(im, tol=TOL):
    """Flood the flat background inward from the edges and make it transparent."""
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    # sample the corners to learn the background colour
    corners = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
    bg = tuple(sum(c[i] for c in corners) // 4 for i in range(3))

    seen = bytearray(w * h)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            q.append((x, y))

    while q:
        x, y = q.popleft()
        i = y * w + x
        if seen[i]:
            continue
        r, g, b, a = px[x, y]
        if abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2]) > tol * 3:
            continue
        seen[i] = 1
        px[x, y] = (r, g, b, 0)
        if x > 0:     q.append((x - 1, y))
        if x < w - 1: q.append((x + 1, y))
        if y > 0:     q.append((x, y - 1))
        if y < h - 1: q.append((x, y + 1))
    return im


def keep_largest_blob(im, warn_at=0.35):
    """Keep the biggest connected blob and erase everything else.

    Simpler than it looks, and provably right for this artwork: the white
    die-cut edge fuses every part of a sticker into one blob, so a cell holds
    exactly one large component plus whatever slivers the neighbouring rows
    spill across the boundary. Measured on these sheets the largest component
    is 49k-74k px and every stray is under 13% of it.

    Earlier attempts keyed on position — centroid inside the cell, or not
    running off the padded crop — and both failed, because neighbours spill
    far enough in to move their centre inside our cell, and our own wide
    stickers spill far enough out to run off the crop. Size is the signal
    that actually separates them.

    A second component above `warn_at` would mean a sticker genuinely built
    from detached pieces, which this rule would damage, so it says so.
    """
    px = im.load()
    w, h = im.size
    seen = bytearray(w * h)
    blobs = []

    for sy in range(h):
        for sx in range(w):
            if seen[sy * w + sx] or px[sx, sy][3] <= 8:
                continue
            pts, q = [], deque([(sx, sy)])
            while q:
                x, y = q.popleft()
                i = y * w + x
                if seen[i] or px[x, y][3] <= 8:
                    continue
                seen[i] = 1
                pts.append((x, y))
                if x > 0:     q.append((x - 1, y))
                if x < w - 1: q.append((x + 1, y))
                if y > 0:     q.append((x, y - 1))
                if y < h - 1: q.append((x, y + 1))
            blobs.append(pts)

    if not blobs:
        return im, 0, False
    blobs.sort(key=len, reverse=True)
    suspect = len(blobs) > 1 and len(blobs[1]) > len(blobs[0]) * warn_at
    dropped = 0
    for pts in blobs[1:]:
        for x, y in pts:
            r, g, b, _ = px[x, y]
            px[x, y] = (r, g, b, 0)
        dropped += len(pts)
    return im, dropped, suspect


def square(im, size=SIZE, pad=PAD):
    """Trim to artwork, then pad back out to a centred square."""
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    side = int(max(im.size) * (1 + pad * 2))
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(im, ((side - im.width) // 2, (side - im.height) // 2), im)
    return canvas.resize((size, size), Image.LANCZOS)


def cells(path, overlap=OVERLAP):
    """Yield (crop, cell_box) where crop is padded past the cell edges."""
    sheet = Image.open(path).convert("RGBA")
    W, H = sheet.size
    w, h = W // COLS, H // ROWS
    mx, my = int(w * overlap), int(h * overlap)
    for r in range(ROWS):
        for c in range(COLS):
            l, t = c * w, r * h
            L, T = max(0, l - mx), max(0, t - my)
            R, B = min(W, l + w + mx), min(H, t + h + my)
            # report which sides actually got padding: on the sheet's outer
            # rows and columns the crop is clamped, so a sticker touching that
            # edge is touching the sheet, not running off into a neighbour.
            pads = (l - L, t - T, R - (l + w), B - (t + h))
            yield sheet.crop((L, T, R, B)), (l - L, t - T, l - L + w, t - T + h), pads


def collect(args):
    """Accept files, or a directory to scan. Sorted, so sheet A comes first."""
    found = []
    for a in args:
        p = pathlib.Path(a)
        if p.is_dir():
            found += sorted(
                q for q in p.iterdir()
                if q.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")
                and q.parent.name != "cut"
            )
        elif p.is_file():
            found.append(p)
        else:
            sys.exit(f"not found: {a}")
    return found


def main(args):
    if not args:
        sys.exit("usage: slice_stickers.py <sheet.png ...|assets/stickers>")
    sheets = collect(args)
    if not sheets:
        sys.exit("no images found — put the sheets in assets/stickers/ first")
    print(f"found {len(sheets)} sheet(s):")
    for p in sheets:
        im = Image.open(p)
        print(f"  {p.name}  {im.width}x{im.height}")
        if im.width % COLS or im.height % ROWS:
            print(f"    note: {im.width}x{im.height} does not divide evenly "
                  f"into {COLS}x{ROWS}; edges may be a pixel off")
    print()
    OUT.mkdir(parents=True, exist_ok=True)

    cut, idx = {}, 0
    for sheet in sheets:
        for cell, box, pads in cells(sheet):
            name = NAMES[idx] if idx < len(NAMES) else None
            idx += 1
            if not name:
                continue
            cleaned, dropped, suspect = keep_largest_blob(bg_alpha(cell))
            art = square(cleaned)
            art.save(OUT / f"{name}.png")
            buf = io.BytesIO(); art.save(buf, "PNG", optimize=True)
            cut[name] = base64.b64encode(buf.getvalue()).decode()
            note = f"  (dropped {dropped:,}px of neighbour)" if dropped else ""
            if suspect:
                note += "  ! second blob is large — check this one by eye"
            print(f"  {name:9} {len(buf.getvalue())//1024:>4} KB{note}")

    if not cut:
        sys.exit("no cells matched NAMES — nothing written")

    # inline into the IMAGES map
    src = ROOT / "design-system.html"
    s = src.read_text()
    block = "    var IMAGES = {\n" + "".join(
        f"      {k}: 'data:image/png;base64,{v}',\n" for k, v in cut.items()
    ) + "    };"
    s, n = re.subn(r"    var IMAGES = \{.*?\n    \};", block, s, count=1, flags=re.S)
    if n != 1:
        sys.exit("could not find the IMAGES map in design-system.html")
    src.write_text(s)

    # the drawn stand-ins are now unused for any key we filled
    print(f"\ninlined {len(cut)} stickers into design-system.html")
    print("next: python3 build.py")


if __name__ == "__main__":
    main(sys.argv[1:])
