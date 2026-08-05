## Building with this system

**There is nothing to import.** No React, no props, no components in `window.*` — this design
system is CSS. The parts are class names on plain HTML. Everything is in `styles.css`'s import
closure (`tokens/tokens.css`, `fonts/fonts.css`, `_ds_bundle.css`); load that one file and every
class below works. There is no utility-class generator, so **a class this system does not define
does nothing at all** — invent `.p-4` or `.text-lg` and you ship unstyled markup.

**No wrapper is required.** Tokens are on `:root`. Two things you must do yourself, because they
live on `body` in the source and a fragment has no body: set `font-family: var(--sans)` and
`color: var(--ink)` on your root element. Light mode only — there is no dark theme; do not add one.

### Type — pick a step, never a font-size

`.t-hero` `.t-display` `.t-h1` `.t-h2` `.t-h3` `.t-sub` `.t-body` `.t-small` `.t-micro`
`.t-caption` `.t-tag` `.t-metric`. Every step carries its own size, weight, leading and tracking.
Weight only ever rises as size falls: hero and display are 400, headings 500, body 400. Prose is
locked to 65–72 characters by `max-width: var(--prose)` — apply it to any paragraph you write.

### Layout

`.wrap` (centred 1120px container with responsive margins) → `.grid` (12 columns) → `.col-2`
… `.col-12`. Space with `var(--s-1)` … `var(--s-10)`, an 8px scale with a 4px half-step. Never
hard-code a pixel gap. `section.band` is the standard vertical rhythm between sections.

### Colour — three inks, two rules, one accent

`var(--ink)` primary, `var(--ink-2)` secondary, `var(--ink-3)` quietest. `var(--rule)` and
`var(--rule-strong)` for hairlines. `var(--paper)` and `var(--paper-sunk)` for ground.
`var(--accent)` and `var(--accent-vivid)` are terracotta and belong on **marks only**, roughly one
per viewport — never on body text, never as a panel fill. `var(--tint-1)` … `var(--tint-5)` tint
cover panels and say *which case*, never *what state*. `var(--sticker-blue)` and
`var(--sticker-lime)` may appear **only inside sticker artwork** — never in text, a border or a fill.

Text on a tint is always `var(--ink)`; `--ink-2` fails contrast on four of the five.

### Components

`.btn` and `.btn--outline`. `.stamp` with `.stamp--shipped` / `.stamp--trial` / `.stamp--nda` —
three fill treatments, so status survives greyscale and colour-blindness. `.card` / `.wcard` for
projects, `.chip` for tools, `.tag` for labels, `.log` + `.logrow` for dated rows, `.metrics` +
`.metric` for figures, `.bleed-rule` for a full-width section break, `.topbar` + `.nav` for the
bar, `.foot` for the footer. Each has a `.prompt.md` next to its preview with the exact markup.

Two classes only work in context, and will look broken alone. `.cover-tint` gets its 4:3 shape
from `.wcard .cover-tint` — outside a work card it is just a tinted div, so use `.cover` for a
standalone image slot. `.chip` only floats over the statement inside `.stack`; anywhere else it is
an ordinary inline pill, which is usually what you want.

### Marks and the hand

`.mk-under` `.mk-ring` `.mk-star` `.mk-arrow` `.mk-bracket` `.mk-wash` are the accent marks — one
per viewport, `aria-hidden`. `var(--hand)` is Caveat and has exactly two jobs: the wordmark
(`.brand`, `.wordmark`) and the scroll cue. It is a signature, roughly 3% of the page. Do not set
it on anything else.

### Motion

`.reveal` fades and rises an element in once, on first intersection. `.reveal-stagger` does the
same for a group's children in sequence. Durations are `var(--dur-confirm)` (120ms, state change),
`var(--dur-reveal)` (200ms), `var(--dur-enter)` (320ms, section), all on `var(--ease)`. Motion
either reveals content or confirms an action — nothing else. Nothing loops except the scroll cue.

### Forbidden, and load-bearing

**No drop shadows on any layout surface.** Separation comes from hairlines and whitespace. The two
exceptions are objects rather than panels: a sticker, and a card lifted by hover. Radius is
`var(--radius)` — 2px, squared not rounded — with `var(--radius-card)` (16px) on cards and cover
panels and `var(--radius-pill)` on chips. No glassmorphism, no gradients, no sketch textures.

### A real example

```html
<section class="wrap band">
  <div class="grid">
    <div class="col-7">
      <h2 class="t-h1">Screening people <span class="mk-under">can finish alone</span></h2>
      <p class="t-body" style="max-width:var(--prose);margin-top:var(--s-3);color:var(--ink-2)">
        The standard test needs a trained administrator in the room.
      </p>
      <a class="btn" href="#work" style="margin-top:var(--s-5)">see the work</a>
    </div>
    <div class="col-5">
      <span class="stamp stamp--shipped">shipped</span>
      <div class="cover" style="margin-top:var(--s-3)">
        <span class="t-micro">the test screen, one screen deep</span>
      </div>
    </div>
  </div>
</section>
```

**Read `styles.css` and the component's `.prompt.md` before styling anything.** The real files beat
this summary, and this system's whole argument is that it is specific rather than generic.
