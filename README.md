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

Colour arrives in two places and nowhere else: the terracotta accent on marks, and
the five card tints on the work carousel, hero collage and tool chips. The tints say
*which case*, never *what state* — state stays in the stamp.

## Foundations

**Two typefaces, no third.** Figtree (geometric-humanist sans) carries prose, headlines,
buttons and all Rebus display lines. Caveat (handwriting) carries labels, metrics, tags,
stamps, captions and log entries. Caveat's digits are natively equal-width, which is why
the monospace it replaced was not needed to keep metric and log columns aligned.

**Display runs light.** Hero and display sit at weight 400, headings at 500, body at 400 —
weight only ever rises as size falls. Past ~64px the scale supplies the presence.

**Colour carries information, never mood.** Pure white ground with a faint 72px ruling
(off in the header and the hero banner). Three ink weights, two hairlines, one warm
terracotta accent spent only on marks.

**Grid.** 8px base unit, 12 columns, 1120px container, 24px gutter, responsive margins at
80 / 48 / 24px. 2px radius by default — squared, not rounded — with a documented exception:
16px on work cards, collage tiles and cover panels, pill on chips. **No drop shadows
anywhere:** separation comes from hairline rules and whitespace only.

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
  only — including the card tilt, chip tilt and collage rotation. Verified in both modes.

## Known gaps

**The pictograms are asset slots, not artwork.** Rule 1 of the Rebus system requires
photographic cutouts and photography cannot be authored in code, so every pictogram is a
correctly-sized, baseline-locked placeholder carrying the right `alt` text. Swapping
`<span class="pict slot">` for `<img class="pict" src alt>` changes no layout. The 12-object
shot list is in §04 — shoot all twelve in one session under one light setup, or the set
will not cohere.

**Metrics are `[XX]` placeholders** awaiting real figures. Inventing them would undercut the
evidence the page exists to present.

## Regenerating the hosted version

`python3 build.py` writes `dist/artifact.html`. Publish that file — the wrapper supplies its
own document skeleton, so the copy carries no `<head>`, and it pins the ground to white
because the system is light-mode only and the viewer's theme must not show through.
