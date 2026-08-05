#!/usr/bin/env python3
"""
Build the claude.ai/design upload bundle from the design system.

    python3 build_design_sync.py

Writes ds-bundle/ in the layout the Design System pane consumes:

    _ds_bundle.js        empty-bodied — this DS ships no JS components
    _ds_bundle.css       the stylesheet
    styles.css           the import root: tokens + fonts + stylesheet
    tokens/tokens.css    the custom properties on their own
    fonts/fonts.css      @font-face, base64 woff2, no network
    components/<Group>/<Name>/<Name>.html      the preview card
    components/<Group>/<Name>/<Name>.prompt.md how to build with it
    guidelines/          the written rules, for the design agent to read
    README.md  _ds_sync.json  _ds_needs_recompile  .ds-build-meta.json

Two things about this bundle are unusual and deliberate.

**There is no JavaScript.** This design system is CSS and markup — no React,
no props, no compiled dist. So `_ds_bundle.js` is an empty IIFE declaring zero
components, which is the honest description, and no `.d.ts` is emitted: a
props interface for a component that has no props would be fiction, and the
design agent codes against whatever contract it is handed. What the agent
gets instead is the real class vocabulary, in `styles.css` and in each
component's `.prompt.md`.

**The CSS is linked, never inlined.** A rendered design receives only the
transitive `@import` closure of `styles.css` — not whatever a preview card
happens to carry. An earlier version of this script inlined the whole
stylesheet into every card: the cards looked perfect and proved nothing,
because a design built with the system would have received none of it. Every
card now links `styles.css`, so what makes a card render is exactly what
makes a design render.

Nothing here is hand-written. Each component is lifted from its own `.spec`
block in design-system.html — the demo, its label, and its rationale — so a
card can never show something the system does not, and adding a component to
the system adds a card on the next build.
"""
import re, os, json, hashlib, pathlib, shutil

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "ds-bundle"
NAMESPACE = "WendyWongDS"

doc = (ROOT / "design-system.html").read_text()
head = doc[doc.index("<head>") + 6: doc.index("</head>")]
styles = re.findall(r"<style>(.*?)</style>", head, re.S)
assert len(styles) == 2, f"expected 2 <style> blocks, found {len(styles)}"
fonts_css, css = styles

sha12 = lambda s: hashlib.sha256(s.encode() if isinstance(s, str) else s).hexdigest()[:12]
sha256 = lambda s: hashlib.sha256(s.encode() if isinstance(s, str) else s).hexdigest()


def close_of(html, start):
    """Index just past the </div> that closes the <div ...> opening at `start`."""
    depth = 0
    for m in re.finditer(r"<(/?)div\b", html[start:]):
        i = start + m.start()
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return html.index(">", html.index("</div", i)) + 1
    raise ValueError(f"unclosed <div> at {start}")


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


def pascal(s):
    return "".join(w[:1].upper() + w[1:] for w in re.findall(r"[a-z0-9]+", s.lower())) or "Item"


def classes_in(markup):
    """The class vocabulary a component actually uses, in first-seen order."""
    seen = []
    for attr in re.findall(r'class="([^"]+)"', markup):
        for c in attr.split():
            if c not in seen:
                seen.append(c)
    return seen


def tokens_in(markup):
    return sorted(set(re.findall(r"var\((--[\w-]+)\)", markup)))


# Cards whose default frame does not do them justice, each with the reason.
# Graded from the render check's contact sheets, which is what these are for.
CARD_FIT = {
    # a three-column metric grid at 900px wide loses its right-hand column
    "MetricBlock": {"viewport": "1180x380"},
    # the tiles are rotated and half-buried by design, and their captions only
    # appear on hover — which a still card can never do. Give it room, and
    # show the state that carries the information.
    "ObjectCollage": {"viewport": "1100x460", "css": (
        ".card-frame .collage .tile-cap{ opacity:1; transform:translateX(-50%) translateY(0) }")},
    # a full project card is tall before it is wide
    "ProjectCard": {"viewport": "820x900"},
    "WorkCardCarousel": {"viewport": "1180x760"},
    "TypeScale": {"viewport": "1180x1100"},
    "GridAndSpace": {"viewport": "1180x760"},
}


def preview(name, group, subtitle, demo, depth=3):
    """One card. The CSS is linked, never inlined — see the module docstring."""
    up = "../" * depth
    fit = CARD_FIT.get(name, {})
    vp = f' viewport="{fit["viewport"]}"' if fit.get("viewport") else ""
    extra = ("\n" + fit["css"]) if fit.get("css") else ""
    return (f'<!-- @dsCard group="{group}"{vp} -->\n'
            '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f"<title>{name}</title>\n"
            f'<link rel="stylesheet" href="{up}styles.css">\n'
            "<style>\n"
            "/* card frame only — never a component style. The pane renders each\n"
            "   card in its own viewport, so the page supplies the padding the\n"
            "   surrounding document would otherwise give it. */\n"
            "body{ background:var(--paper); background-image:none; margin:0 }\n"
            ".card-frame{ padding:var(--s-6) }" + extra + "\n"
            "</style>\n</head>\n<body>\n"
            f'<div class="card-frame">\n<!-- {subtitle} -->\n{demo}\n</div>\n'
            "</body>\n</html>\n")


def prompt_md(name, title, subtitle, demo, note):
    """The usage reference the design agent reads. First line must be non-empty."""
    cls, tok = classes_in(demo), tokens_in(demo)
    out = [f"{title}{' — ' + subtitle if subtitle else ''}", ""]
    if note:
        out += ["## Why it is like this", "", note, ""]
    out += ["## Markup", "",
            "Copy this shape. The classes carry the styling — there are no props, and no",
            "component to import; the system is CSS.", "", "```html", demo.strip(), "```", ""]
    if cls:
        out += ["## Classes used here", "",
                "\n".join(f"- `.{c}`" for c in cls), ""]
    if tok:
        out += ["## Tokens referenced here", "",
                "\n".join(f"- `var({t})`" for t in tok), ""]
    out += ["Every class and token above is defined in `styles.css`'s import closure.",
            "Read that file before inventing a name — this system has no utility-class",
            "generator, so a class it does not define does nothing at all.", ""]
    return "\n".join(out)


# --- the sticker cutouts, so that card can be a still rather than an empty box
STICKERS = dict(re.findall(r"\n      (\w+): '(data:image/png;base64,[^']+)'", doc))
assert len(STICKERS) == 10, f"expected 10 sticker cutouts, found {len(STICKERS)}"

files, components = {}, []


def add_component(group, name, title, subtitle, demo, note):
    d = f"components/{group}/{name}"
    files[f"{d}/{name}.html"] = preview(name, group, subtitle, demo)
    files[f"{d}/{name}.prompt.md"] = prompt_md(name, title, subtitle, demo, note)
    components.append({"name": name, "group": group, "title": title,
                       "subtitle": subtitle, "path": f"{d}/{name}.html"})


# --- components, lifted from their own spec blocks --------------------------
for m in re.finditer(r'<div class="spec reveal" id="([^"]+)"', doc):
    block = doc[m.start(): close_of(doc, m.start())]
    label = re.search(r'<div class="spec-label">(.*?)</div>', block, re.S)
    body = re.search(r'<div class="spec-body[^>]*>(.*?)</div>\s*(?:<p class="spec-note")',
                     block, re.S)
    if not (label and body):
        continue
    spans = re.findall(r"<span>(.*?)</span>", label.group(1), re.S)
    raw = strip_tags(spans[0]) if spans else m.group(1)
    subtitle = strip_tags(spans[1]) if len(spans) > 1 else ""
    note = strip_tags(re.search(r'<p class="spec-note">(.*?)</p>', block, re.S).group(1)) \
        if re.search(r'<p class="spec-note">', block) else ""
    title = re.sub(r"^[\d\s+/]+—\s*", "", raw).strip() or raw
    demo = body.group(1).strip()
    if 'id="stickerStrip"' in demo:
        # The live field is drawn by the page's own script, so lifting the
        # markup alone yields an empty box. A card is a still.
        demo = ('<div style="display:flex;flex-wrap:wrap;gap:var(--s-4);align-items:center">\n'
                + "".join(f'  <img src="{src}" alt="{k}" width="72" height="72"\n'
                          f'       style="display:block;filter:drop-shadow(0 3px 3px rgba(23,24,26,.22))">\n'
                          for k, src in STICKERS.items())
                + "</div>")
    add_component("Components", pascal(title), title, subtitle, demo, note)

assert len(components) >= 15, f"only found {len(components)} component specs — check the parser"

# --- foundations, each lifted from inside its own section -------------------
# Every pattern is applied within one <section> and nowhere else. Run against
# the whole document, a greedy match happily ran to the last matching tag on
# the page and dragged half the system into one card.
FOUNDATIONS = [
    ("Colour", "palette", "regex", r'<div class="swatches">.*?</div>\s*</div>\s*</div>',
     "The whole palette. Three ink weights, two hairlines, one accent."),
    ("TypeScale", "type", "regex", r'<div class="tsrow">.*</div>\s*(?=\s*<div class="spec)',
     "Every size in the scale, with its weight, clamp, leading and tracking."),
    ("GridAndSpace", "grid", "block", '<div class="grid">',
     "12 columns, 1120px container, and the 8px spacing scale."),
]
for name, sec_id, mode, pattern, note in FOUNDATIONS:
    start = doc.find(f'<section class="wrap band" id="{sec_id}"')
    if start < 0:
        print(f"  note: no section #{sec_id} — skipped")
        continue
    section = doc[start: doc.index("</section>", start)]
    if mode == "block":
        at = section.find(pattern)
        demo = section[at: close_of(section, at)] if at >= 0 else None
    else:
        found = re.search(pattern, section, re.S)
        demo = found.group(0) if found else None
    if demo is None:
        print(f"  note: no {sec_id} block matched — skipped")
        continue
    add_component("Foundations", name, name, note, demo, note)

# --- styles: tokens, fonts, stylesheet, and the one root that imports them ---
# A rendered design receives ONLY this closure. Anything reachable from here
# reaches every design built with the system; anything outside it reaches none.
roots = re.findall(r"(?m)^:root\{.*?^\}", css, re.S)
assert len(roots) >= 3, f"expected >=3 token blocks, found {len(roots)}"
sheet = css
for r in roots:
    sheet = sheet.replace(r, "", 1)
sheet = re.sub(r"\n{3,}", "\n\n", sheet)

files["tokens/tokens.css"] = (
    "/* Wendy Wong — design tokens. Generated from design-system.html.\n"
    "   Colour, type scale, spacing, radius, motion. Everything else builds\n"
    "   on these; nothing in this system hard-codes a value one of these holds. */\n\n"
    + "\n\n".join(roots) + "\n")
files["fonts/fonts.css"] = (
    "/* Figtree (all weights, roman + italic) and Caveat, base64 woff2.\n"
    "   Self-contained on purpose: the system renders identically offline and\n"
    "   under a strict CSP because no font is ever fetched. */\n" + fonts_css)
files["_ds_bundle.css"] = (
    "/* Wendy Wong — the stylesheet. Generated from design-system.html.\n"
    "   Tokens live in tokens/tokens.css; this is everything built on them. */\n"
    + sheet)
files["styles.css"] = (
    "/* The import root. A design built with this system receives this file's\n"
    "   transitive closure and nothing else, so every part of the system that\n"
    "   must reach a design is imported here. Order matters: tokens define the\n"
    "   custom properties the stylesheet consumes, fonts declare the families\n"
    "   it names. */\n"
    '@import "./tokens/tokens.css";\n'
    '@import "./fonts/fonts.css";\n'
    '@import "./_ds_bundle.css";\n')

# --- the empty bundle -------------------------------------------------------
# No JS components: this DS is CSS and markup. An empty IIFE declaring zero
# components is the honest description, and it keeps the app's self-check
# happy without inventing exports that do not exist.
header = json.dumps({
    "namespace": NAMESPACE,
    "components": [],
    "sourceHashes": {"design-system.html": sha12(doc)},
    "inlinedExternals": [],
}, separators=(",", ":")).replace("*/", "*\\/")
files["_ds_bundle.js"] = (
    f"/* @ds-bundle: {header} */\n"
    "// This design system ships no JavaScript components. It is CSS and\n"
    "// markup: the parts are class names, documented per component in\n"
    "// components/**/<Name>.prompt.md and defined in styles.css's import\n"
    "// closure. The namespace exists so the app has something to bind.\n"
    f"(function(){{ window.{NAMESPACE} = window.{NAMESPACE} || {{}}; }})();\n")

# --- guidelines: the written rules, verbatim from the repo ------------------
readme = (ROOT / "README.md").read_text()
files["guidelines/design-system.md"] = readme

# The conventions header is prepended to the README and inlined into the design
# agent's system prompt. It is the single most-read file in this bundle: the
# agent gets the README and the artifacts, and nothing else.
CONVENTIONS = ROOT / ".design-sync" / "conventions.md"
header = (CONVENTIONS.read_text().rstrip() + "\n\n---\n\n") if CONVENTIONS.exists() else ""
if not header:
    print("  note: no .design-sync/conventions.md — README ships without the header")

files["README.md"] = header + f"""# Wendy Wong — design system

{len(components)} cards: {sum(1 for c in components if c['group'] == 'Components')} components
and {sum(1 for c in components if c['group'] == 'Foundations')} foundations.

**This system has no JavaScript components.** There is nothing to import and no props to
pass. The parts are class names, defined in `styles.css`'s import closure and documented
one file per component in `components/<group>/<Name>/<Name>.prompt.md`. Read
`styles.css` before inventing a class name: there is no utility-class generator here, so a
name the system does not define does nothing at all.

| File | What it is |
|---|---|
| `styles.css` | The import root. A rendered design receives this closure and nothing else. |
| `tokens/tokens.css` | Colour, type scale, spacing, radius, motion. |
| `fonts/fonts.css` | Figtree and Caveat, base64 woff2 — no network, ever. |
| `_ds_bundle.css` | Everything built on the tokens. |
| `guidelines/` | The written rules, including what the system refuses to do. |

Generated from `design-system.html` by `build_design_sync.py`. Do not edit these files —
edit the design system and rebuild.
"""

# --- write ------------------------------------------------------------------
if OUT.exists():
    shutil.rmtree(OUT)
for path, text in files.items():
    dest = OUT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text)
(OUT / "_ds_needs_recompile").write_text(json.dumps({"by": "build_design_sync.py"}) + "\n")

# --- the verification anchor -------------------------------------------------
# renderHashes are computed from what is actually on disk, so the anchor can
# only ever vouch for this build. No .stories-map.json is emitted: this is an
# off-script layout, and the validator's recompute step is for script builds.
files_on_disk = {c["name"]: (OUT / c["path"]).read_text() for c in components}
(OUT / "_ds_sync.json").write_text(json.dumps({
    "shape": "css",
    "styleSha": sha256(files["styles.css"] + files["_ds_bundle.css"]
                       + files["tokens/tokens.css"] + files["fonts/fonts.css"]),
    "renderHashes": {n: sha256(t) for n, t in files_on_disk.items()},
    "sourceKeys": {c["name"]: sha12(c["path"]) for c in components},
    "keyRecipe": "sha256 of the emitted preview HTML",
    "scriptsSha": sha12(pathlib.Path(__file__).read_text()),
    "sourceHashes": {"design-system.html": sha12(doc)},
    "auxSha": sha12(files["README.md"]),
    "bundleSha12": sha12(files["_ds_bundle.js"]),
}, indent=2) + "\n")

(OUT / ".ds-build-meta.json").write_text(json.dumps({
    "componentCount": len(components),
    "shape": "css",
    "dtsStubbed": False,
    "note": "CSS/markup design system — no JS components, so no .d.ts is emitted.",
}, indent=2) + "\n")

total = sum(os.path.getsize(p) for p in OUT.rglob("*") if p.is_file())
print(f"  ds-bundle/  {sum(1 for p in OUT.rglob('*') if p.is_file())} files, {total // 1024} KB")
for c in components:
    print(f"    {c['group']:12} {c['path']}")
print("built.")
