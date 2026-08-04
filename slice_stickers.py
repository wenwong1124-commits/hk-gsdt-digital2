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

# Reading order, sheet A then sheet B. None = skip this cell.
NAMES = [
    # sheet A
    "mic", "brain", "ear",
    "pipeline", "faces", None,          # None = shield, too corporate
    "heart", None, None,                # squares, magnet
    "hands", "cluster", "mind",
    # sheet B
    "eye", "globe", None,               # selection marquee
    None, "peace", None,                # flame, id cards
    "asterisk", "link", "blend",
    "pen", "window", "wand",
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


def square(im, size=SIZE, pad=PAD):
    """Trim to artwork, then pad back out to a centred square."""
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    side = int(max(im.size) * (1 + pad * 2))
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(im, ((side - im.width) // 2, (side - im.height) // 2), im)
    return canvas.resize((size, size), Image.LANCZOS)


def cells(path):
    sheet = Image.open(path).convert("RGBA")
    w, h = sheet.width // COLS, sheet.height // ROWS
    for r in range(ROWS):
        for c in range(COLS):
            yield sheet.crop((c * w, r * h, (c + 1) * w, (r + 1) * h))


def main(sheets):
    if not sheets:
        sys.exit("usage: slice_stickers.py <sheet-a.png> [sheet-b.png ...]")
    OUT.mkdir(parents=True, exist_ok=True)

    cut, idx = {}, 0
    for sheet in sheets:
        for cell in cells(sheet):
            name = NAMES[idx] if idx < len(NAMES) else None
            idx += 1
            if not name:
                continue
            art = square(bg_alpha(cell))
            art.save(OUT / f"{name}.png")
            buf = io.BytesIO(); art.save(buf, "PNG", optimize=True)
            cut[name] = base64.b64encode(buf.getvalue()).decode()
            print(f"  {name:9} {len(buf.getvalue())//1024:>4} KB")

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
