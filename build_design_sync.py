#!/usr/bin/env python3
"""
Build a Claude Design push bundle from the design system.

    python3 build_design_sync.py

Writes design-sync/ — one preview file per component, plus the foundations
and the stylesheet, ready to push to a claude.ai/design design-system
project with the DesignSync tool.

Every preview is a complete, self-contained HTML document. The Design System
pane renders each card in its own frame, and a card that renders unstyled is
worse than no card, so nothing here depends on a sibling path resolving. The
cost is the stylesheet repeated per file, which is ~50 KB of text that
compresses to nothing and is regenerated on every build anyway. Fonts are the
one exception: 218 KB of base64 per file would be absurd, so previews pull
Figtree and Caveat from Google Fonts, exactly as src/ already does.

The card index comes from each file's first line:

    <!-- @dsCard group="Components" -->

The components are not hand-written here. Each one is lifted from its own
`.spec` block in design-system.html — the same demo the system documents,
so a card can never show something the system does not. Add a component to
the system and it appears here on the next build.
"""
import re, os, json, pathlib

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "design-sync"
doc = (ROOT / "design-system.html").read_text()

head = doc[doc.index("<head>") + 6: doc.index("</head>")]
styles = re.findall(r"<style>(.*?)</style>", head, re.S)
assert len(styles) == 2, f"expected 2 <style> blocks, found {len(styles)}"
fonts_inline, css = styles

FONT_LINK = ('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
             '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
             'family=Figtree:ital,wght@0,300..700;1,300..500&family=Caveat:wght@400..700'
             '&display=swap">')


def close_of(html, start):
    """Index just past the </div> that closes the <div ...> opening at `start`."""
    i, depth = start, 0
    for m in re.finditer(r"<(/?)div\b", html[start:]):
        i = start + m.start()
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return html.index(">", html.index("</div", i)) + 1
    raise ValueError(f"unclosed <div> at {start}")


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def page(title, group, subtitle, body, pad="var(--s-6)"):
    """One card: the marker first, then a complete document."""
    return (f'<!-- @dsCard group="{group}" -->\n'
            "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f"<title>{title}</title>\n{FONT_LINK}\n<style>{css}</style>\n"
            "<style>\n"
            "/* card frame only — never a component style. The pane renders each\n"
            "   preview in its own viewport, so the page supplies the padding the\n"
            "   surrounding document would normally give it. */\n"
            "body{ background:var(--paper); background-image:none }\n"
            f".card-frame{{ padding:{pad} }}\n"
            "</style>\n</head>\n<body>\n"
            f'<div class="card-frame">\n<!-- {subtitle} -->\n{body}\n</div>\n'
            "</body>\n</html>\n")


# The ten cutouts, so the sticker card can be a still rather than an empty box.
STICKERS = dict(re.findall(r"\n      (\w+): '(data:image/png;base64,[^']+)'", doc))
assert len(STICKERS) == 10, f"expected 10 sticker cutouts, found {len(STICKERS)}"

# --- components, lifted from their own spec blocks --------------------------
cards, files = [], {}
for m in re.finditer(r'<div class="spec reveal" id="([^"]+)"', doc):
    block = doc[m.start(): close_of(doc, m.start())]
    label = re.search(r'<div class="spec-label">(.*?)</div>', block, re.S)
    body = re.search(r'<div class="spec-body[^>]*>(.*?)</div>\s*(?:<p class="spec-note")',
                     block, re.S)
    if not (label and body):
        continue
    spans = re.findall(r"<span>(.*?)</span>", label.group(1), re.S)
    name = strip_tags(spans[0]) if spans else m.group(1)
    subtitle = strip_tags(spans[1]) if len(spans) > 1 else ""
    # "05 + 06 — buttons, filled and outline" -> "buttons, filled and outline"
    title = re.sub(r"^[\d\s+/]+—\s*", "", name).strip() or name
    path = f"components/{m.group(1)}-{slug(title)[:40]}.html"
    demo = body.group(1).strip()
    if 'id="stickerStrip"' in demo:
        # The live field is drawn by the page's own script, so lifting the
        # markup alone yields an empty box. A card is a still: paint the ten
        # cutouts straight in, at the size the strip renders them.
        demo = ('<div style="display:flex;flex-wrap:wrap;gap:var(--s-4);align-items:center">\n'
                + "".join(f'  <img src="{src}" alt="{k}" width="72" height="72"\n'
                          f'       style="display:block;filter:drop-shadow(0 3px 3px rgba(23,24,26,.22))">\n'
                          for k, src in STICKERS.items())
                + "</div>")
    files[path] = page(title, "Components", subtitle, demo)
    cards.append({"name": title.capitalize(), "path": path,
                  "subtitle": subtitle, "group": "Components",
                  "viewport": {"width": 900, "height": 420}})

assert len(cards) >= 15, f"only found {len(cards)} component specs — check the parser"

# --- foundations, lifted from their own sections ---------------------------
# Each pattern is applied inside its own <section> and nowhere else. Run
# against the whole document a greedy match happily ran to the last matching
# tag on the page and dragged half the system into one card.
FOUNDATIONS = [
    # ("regex", pattern) slices by match; ("block", opening tag) takes the whole
    # balanced <div>, which is what you want when the demo is a two-column
    # layout rather than one element.
    ("palette", "Colour", "palette", "regex", r'<div class="swatches">.*?</div>\s*</div>\s*</div>'),
    ("type", "Type scale", "type", "regex", r'<div class="tsrow">.*</div>\s*(?=\s*<div class="spec)'),
    ("grid", "Grid and space", "grid", "block", '<div class="grid">'),
]
for key, title, sec_id, mode, pattern in FOUNDATIONS:
    start = doc.find(f'<section class="wrap band" id="{sec_id}"')
    if start < 0:
        print(f"  note: no section #{sec_id} — skipped")
        continue
    end = doc.index("</section>", start)
    section = doc[start:end]
    if mode == "block":
        at = section.find(pattern)
        if at < 0:
            print(f"  note: no {key} block matched — skipped")
            continue
        demo = section[at: close_of(section, at)]
    else:
        found = re.search(pattern, section, re.S)
        if not found:
            print(f"  note: no {key} block matched — skipped")
            continue
        demo = found.group(0)
    path = f"foundations/{key}.html"
    files[path] = page(title, "Foundations", title, demo)
    cards.append({"name": title, "path": path, "subtitle": title,
                  "group": "Foundations", "viewport": {"width": 900, "height": 520}})

# --- the shared stylesheet, for anyone reading rather than rendering -------
roots = re.findall(r"(?m)^:root\{.*?^\}", css, re.S)
files["styles/tokens.css"] = (
    "/* Wendy Wong — design tokens. Generated from design-system.html. */\n\n"
    + "\n\n".join(roots) + "\n")
files["styles/design-system.css"] = (
    "/* Wendy Wong — stylesheet. Generated from design-system.html.\n"
    "   Previews inline this; the copy here is for reading and importing. */\n"
    + css)
files["styles/fonts.css"] = (
    "/* Figtree + Caveat, base64 woff2, no network. Previews use Google Fonts\n"
    "   instead — 218 KB of base64 per card would be absurd. */\n" + fonts_inline)

files["README.md"] = f"""# Wendy Wong — design system

Generated by `build_design_sync.py` from `design-system.html`, which is the only
source of truth. {len(cards)} cards: {sum(1 for c in cards if c['group'] == 'Components')} components
and {sum(1 for c in cards if c['group'] == 'Foundations')} foundations.

Every preview is a complete self-contained document — the pane renders each card in
its own frame, so nothing depends on a sibling path resolving. Fonts come from Google
Fonts; the offline base64 copy is in `styles/fonts.css`.

Do not edit these files. Edit `design-system.html`, then run `python3 build_design_sync.py`.
"""

# --- write ------------------------------------------------------------------
if OUT.exists():
    for p in sorted(OUT.rglob("*"), reverse=True):
        p.unlink() if p.is_file() else p.rmdir()
for path, text in files.items():
    dest = OUT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text)
(OUT / "_cards.json").write_text(json.dumps(cards, indent=2) + "\n")

total = sum(os.path.getsize(OUT / p) for p in files)
print(f"  design-sync/  {len(files) + 1} files, {total // 1024} KB")
for c in cards:
    print(f"    {c['group']:12} {c['path']}")
print("built.")
