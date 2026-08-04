# Wendy Wong — Design System v1.0

**Clinical field notebook.** The design system for a portfolio whose one job is to prove,
to a hiring manager with sixty seconds, that complex AI research becomes scalable digital
health products.

**Live page:** https://claude.ai/code/artifact/f83221d0-a6bd-45be-9d7a-1670724b147f

---

## Files

| File | What it is |
|---|---|
| `design-system.html` | The self-contained build — one file, no build step, no network. Fonts inlined as base64 `woff2`. **The only source of truth.** |
| `build.py` | Regenerates everything below from it. Run after any edit. |
| `slice_stickers.py` | Cuts the sticker sheets into transparent cutouts and inlines them. |
| `src/index.html` | Same page, markup only. Start here when reading the system. |
| `src/design-system.css` | The stylesheet, ~35 KB and readable — no base64 blobs. |
| `src/tokens.css` | The custom properties on their own, for importing elsewhere. |
| `dist/artifact.html` | Publish copy, document skeleton stripped. |

Read `src/`. Ship or share `design-system.html`. Everything except
`design-system.html` is generated — edit the source, then `python3 build.py`.

`design-system.html` opens in any browser straight from disk and renders identically offline
and inside a strict CSP, because every font and graphic is inlined. `src/` is the same page
split for legibility; it pulls Figtree and Caveat from Google Fonts, so it needs a network
connection to typeset correctly. The two are verified equivalent — computed styles match
across 39 selectors once the webfonts load.

Edit `design-system.html`, then run `python3 build.py`. Don't hand-edit anything
under `src/` or `dist/` — it will be overwritten, and the split has two traps the
script already handles (see its docstring).

## The four styles, in strict hierarchy

| Style | Job | Share |
|---|---|---|
| **Rebus** | The voice. Photographic cutouts replace nouns in a sentence. | Hero, section headlines, one line per project card — nowhere else |
| **Utilitarian** | The body and the default. Grid-based, muted, zero decoration. | ~85% of the page |
| **Bento** | The architecture. Modular blocks for cards, metric groups, credential strip. | ~10% |
| **Accent** | The signature. One warm hue on vector marks only. | ~5%, one mark per viewport |

Colour arrives in three places and nowhere else: the terracotta accent on marks, the five
card tints on the work carousel, hero collage and tool chips, and the sticker artwork in the
hero. The tints say *which case*, never *what state* — state stays in the stamp. The two
sticker hues may appear **only inside sticker artwork** — never in text, a border or a fill.

## Foundations

**Two typefaces, no third — but they are not equal partners.** Figtree does all the work:
prose, headlines, buttons, Rebus display lines, and the whole label layer (micro-labels,
captions, tags, stamps, metrics, log entries) set small and uppercase with wide tracking.
Its digits are equal-width, so metric and log columns align without a monospace.

Caveat appears in exactly three places — the notebook plate, the scroll cue, and the footer
wordmark — and nowhere else. That is **3.4% of characters and 3.97% of ink** on the portfolio
page, measured in-browser. It is a signature, not a voice. Handwriting carrying the label
layer turned the page into a notebook pastiche and did not hold up at 11px.

**Display runs light.** Hero and display sit at weight 400, headings at 500, body at 400 —
weight only ever rises as size falls. Past ~64px the scale supplies the presence.

**Colour carries information, never mood.** Pure white ground with a faint 72px ruling
(off in the header and the hero banner). Three ink weights, two hairlines, one warm
terracotta accent spent only on marks.

**Grid.** 8px base unit, 12 columns, 1120px container, 24px gutter, responsive margins at
80 / 48 / 24px. 2px radius by default — squared, not rounded — with a documented exception:
16px on work cards, collage tiles and cover panels, pill on chips. **No drop shadows on any
layout surface** — separation comes from hairline rules and whitespace only. Two exceptions,
both objects rather than panels: a sticker, and a collage card lifted by hover. A shadow is
allowed only where something genuinely claims to sit above the page.

**Measure.** Prose is locked to 65–72 characters via `--prose: 46ch`. The value was set by
measuring rendered lines in the browser, not by arithmetic — `1ch` is the advance of `0`,
which is much wider than Figtree's average lowercase glyph.

## Accessibility

The portfolio's central claim is inclusive design for older adults, so the page cannot
contradict itself.

- **Zero WCAG AA failures.** Lowest measured ratio on the page is 4.88:1; body text is
  17.77:1 (AAA). Audited programmatically across every rendered text node, not by eye.
- **Colour is never the only channel.** Metric families are separated by a solid, dashed or
  dotted rule *first* and tinted second; status by three fill treatments plus its literal
  word. Print it greyscale and nothing is lost.
- **Verified against dichromacy.** The metric trio (terracotta / blue / ink) has a worst-case
  simulated separation of ΔE 38 under both deuteranopia and protanopia. An earlier
  terracotta / blue / olive trio measured ΔE 5 and was discarded.
- **Every pictogram carries `alt` equal to the exact word it replaces.** A sentence built
  from images is hostile to screen readers, so this is mandatory. Accent marks are
  `aria-hidden` or background images — a screen reader hears the sentence, never the swoosh.
- **Text on a card tint is always primary ink** (≥9.07:1). `--ink-2` fails AA on four of
  the five tints, so it is never used on one.
- **`prefers-reduced-motion: reduce`** disables every transform and retains opacity fades
  only — including the card tilt, chip tilt and collage rotation. The hero sticker field is
  removed outright rather than frozen. Verified in both modes.
- **The sticker field is decorative and knows it.** `aria-hidden`, behind all hero content,
  carries no information, and is exempt from the contrast rules precisely because nothing
  depends on reading it.

## Known gaps

**The pictograms are asset slots, not artwork.** Rule 1 of the Rebus system requires
photographic cutouts and photography cannot be authored in code, so every pictogram is a
correctly-sized, baseline-locked placeholder carrying the right `alt` text. Swapping
`<span class="pict slot">` for `<img class="pict" src alt>` changes no layout. The 12-object
shot list is in §04 — shoot all twelve in one session under one light setup, or the set
will not cohere.

**Metrics are `[XX]` placeholders** awaiting real figures. Inventing them would undercut the
evidence the page exists to present.

**The hero stickers are drawn stand-ins.** The real artwork exists but has not reached this
repo yet. To swap it in — no redrawing, no code changes:

```
python3 slice_stickers.py assets/stickers/sheet-a.png assets/stickers/sheet-b.png
python3 build.py
```

That slices each 3x4 sheet into cells, floods the magenta ground away from the edges inward
(so magenta *inside* a sticker survives), trims and squares each cutout, and writes them
straight into the `IMAGES` map in `design-system.html`. Any key present there is used instead
of the drawn SVG; sizing, collision, drag and throw are untouched. Edit `NAMES` in the script
to change which cell becomes which sticker, or set a cell to `None` to skip it.

The pipeline is tested end to end against a synthetic sheet: background knocked to alpha 0,
256x256 RGBA squares, images rendering in the physics field with no errors.

**The hero set is 11 of the 24**, already encoded in both `NAMES` and `ORDER`: microphone,
brain, ear, research-to-product pipeline, two generations, health data, hands, feature
cluster, mind, pen, wand. The other thirteen are rejected — shield, component squares,
magnet, globe, selection marquee, flame, peace hand, ID cards, asterisk, link, blend, browser
window, eye — because they are generic or they say software company. The object vocabulary is
the one place in the system that has to be specific to this work, so a shallower pile of
objects that all mean something beats a deeper one padded with an ID card. `ORDER` skips any
key whose artwork has not arrived, so it names the final set now and renders nine until then.

## Regenerating the hosted version

`python3 build.py` writes `dist/artifact.html`. Publish that file — the wrapper supplies its
own document skeleton, so the copy carries no `<head>`, and it pins the ground to white
because the system is light-mode only and the viewer's theme must not show through.
