# Wendy Wong — Design System v1.0

**Clinical field notebook.** The design system for a portfolio whose one job is to prove,
to a hiring manager with sixty seconds, that complex AI research becomes scalable digital
health products.

**The site:** https://claude.ai/code/artifact/ceff6783-aa9e-4fce-b1e9-0f725ed40bdf
**The design system:** https://claude.ai/code/artifact/f83221d0-a6bd-45be-9d7a-1670724b147f

---

## Files

| File | What it is |
|---|---|
| `design-system.html` | The self-contained build — one file, no build step, no network. Fonts inlined as base64 `woff2`. **The only source of truth.** |
| `build.py` | Regenerates the `src/` and `dist/` copies from it. Run after any edit. |
| `build_site.py` | Regenerates the site's shared assets from it. Run after any edit. |
| `slice_stickers.py` | Cuts the sticker sheets into transparent cutouts and inlines them. |
| `src/index.html` | Same page, markup only. Start here when reading the system. |
| `src/design-system.css` | The stylesheet, ~44 KB and readable — no base64 blobs. |
| `src/tokens.css` | The custom properties on their own, for importing elsewhere. |
| `dist/artifact.html` | Publish copy, document skeleton stripped. |
| `site/` | **The portfolio itself.** See below. |

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

## The site

```
site/
  index.html            /01 work — the landing page
  assets/fonts.css      generated · @font-face, base64 woff2
  assets/site.css       generated · the stylesheet
  assets/site.js        generated · reveal, nav, sticker field
  dist/index.html       generated · self-contained copy, opens from disk
  dist/artifact/        generated · same page for hosts that supply a <head>
```

Open `site/index.html` — it needs its `assets/` siblings. `site/dist/index.html` is the
same page with everything inlined, for sending as one file or hosting anywhere.

**Pages are authored, assets are generated.** `build_site.py` lifts the stylesheet, the
fonts and the runtime out of `design-system.html` so the site can never drift from the
system; the markup under `site/` is written by hand, because a real page is not a specimen
and the two should be allowed to differ. Edit `design-system.html` for anything about how
the site looks or behaves, then run `python3 build_site.py`. Never hand-edit `site/assets/`
or `site/dist/`.

**What is built:** `/01 work`. `/02 about`, `/03 virtual gallery` and `/04 resume` sit in
the nav as inert items — they are the site's shape, so they stay visible, but they carry no
`href` and no hover, because a nav item that goes nowhere is worse than one that waits.
They read one ink weight below a live item (5.28:1, still AA) rather than being greyed out;
the earlier hairline grey measured 1.47:1. `/05 contact` is an anchor on this page.

**Still to wire:** the five work cards and the two "more work" rows link to their own
anchors, so nothing is broken, but nothing navigates either. They get real `href`s when the
case pages exist.

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

The portfolio's central claim is inclusive design — across ages, abilities and contexts — so
the page cannot contradict itself.

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
- **The sticker field is decorative and knows it.** `aria-hidden`, occupying a band below all
  hero content rather than sitting behind it, carries no information, and is exempt from the
  contrast rules precisely because nothing depends on reading it. The band clips the field
  while the pile is falling or at rest, and stops clipping the moment a pointer grabs a
  sticker — so one can be carried up over the headline and put back down, without anything
  ever *settling* on top of a button.
- **It comes to rest and stops.** The pile settles in 3–6s and the animation frame loop then
  exits; measured 0 of 10 transforms still changing at 1440 / 1024 / 768 / 390px, and again
  after a drag-and-throw. Nothing animates indefinitely behind the copy.

## Known gaps

**The pictograms are asset slots, not artwork.** Rule 1 of the Rebus system requires
photographic cutouts and photography cannot be authored in code, so every pictogram is a
correctly-sized, baseline-locked placeholder carrying the right `alt` text. Swapping
`<span class="pict slot">` for `<img class="pict" src alt>` changes no layout. The 12-object
shot list is in §04 — shoot all twelve in one session under one light setup, or the set
will not cohere.

**Metrics are `[XX]` placeholders** awaiting real figures. Inventing them would undercut the
evidence the page exists to present.

**The hero stickers are Wendy's own artwork**, cut from the two sheets in
`assets/stickers/` and inlined as base64 PNGs. To re-cut them after changing a sheet:

```
python3 slice_stickers.py assets/stickers
python3 build.py
```

The slicer splits each 3x4 sheet, floods the magenta ground away from each cell's edges
inward (so magenta *inside* a sticker survives), drops any small blob bleeding in from the
neighbouring row, trims and squares each cutout to 256x256 RGBA, and writes them into the
`IMAGES` map in `design-system.html`. Individual cutouts also land in `assets/stickers/cut/`.
`NAMES` controls which cell becomes which sticker; `None` skips a cell.

**The hero set is 10 of the 24**: microphone, brain, two generations, health data, hands,
mind, eye, globe, pen, wand. The object vocabulary is the one place in the system required to
be specific to this work.

The slicer keeps **the largest connected blob per cell** and erases the rest. That works
because each sticker's white die-cut edge fuses all its parts into one component — measured
at 49k–74k px, with every stray under 13% of it. Two position-based rules were tried first
and both failed: neighbours spill far enough in to move their centroid inside the cell, and
wide stickers spill far enough out to run off the padded crop. Size is the signal that
separates them. `OVERLAP` stays at 0.045 for the same reason — at 0.14 a sticker's white ring
fuses with its neighbour's into a single blob.

A drawn SVG fallback remains in the source for any key without a cutout. With all eleven
present it never renders, and it is the reason the field degrades rather than breaks if a
sheet changes shape.

**Three things about the physics are counter-intuitive and were each a bug first.**

*Rest is measured, not inferred.* A body resting on another carries a permanent ~34px/s of
gravity that the contact cancels again every frame, so no velocity threshold ever reads
zero on a pile. The loop sleeps on how far the artwork actually moved — position plus
rotation weighted at the sticker's own radius — and once nothing is genuinely impacting
any more it deliberately bleeds off the residue that friction alone never finishes.

*A jammed row never stops colliding.* Sizing the row off the sticker's box rather than its
collision diameter packed a 390px banner one sticker tighter than it could hold, and those
collisions are real, so the pile churned behind the copy forever. The row count now comes
from the same numbers the physics uses, and a ten-second deadline stops the loop regardless.

*A rotated square reaches past its own box.* The wall and floor clamp is `size * 0.63`, the
artwork's half-diagonal, not half its side. Clamping on half the side let the band's own
`overflow:hidden` shave the bottom row flat — the same cut-off edge the cutouts were
re-sliced to get rid of. Verified by scanning the band's edge pixels at four widths: no ink
touches any edge.

## Regenerating the hosted version

`python3 build.py` writes `dist/artifact.html`. Publish that file — the wrapper supplies its
own document skeleton, so the copy carries no `<head>`, and it pins the ground to white
because the system is light-mode only and the viewer's theme must not show through.
