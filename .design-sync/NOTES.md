# design-sync notes

## What this repo is

Not a JS package and not a Storybook. The design system is **one hand-authored HTML file**,
`design-system.html`, carrying its own `<style>` blocks — no `package.json`, no `dist/`, no
React, no components to compile. The skill's converter (`package-build.mjs`) cannot run here;
this is the documented off-script case, and `build_design_sync.py` produces the upload layout
directly.

`shape` is recorded as `"css"` rather than `package`/`storybook`, and `componentCount` counts
**preview cards**, not JS exports. `_ds_bundle.js` is an empty IIFE declaring zero components,
which is the honest description and keeps `[BUNDLE_EXPORT]` correctly skipped.

## Re-sync is one command

    python3 build_design_sync.py
    DS_CHROMIUM_PATH=<chromium> node <skill>/package-validate.mjs ds-bundle --render-sample 0

The cards are lifted from the `.spec` blocks in `design-system.html` — label, demo, and the
`spec-note` rationale, which becomes the "Why it is like this" section of each `.prompt.md`.
Add a component to the design system and it appears here on the next build. Nothing in
`ds-bundle/` is hand-maintained.

## Re-sync risks

- **`.spec` block parsing is structural.** `close_of()` counts `<div>` depth, and the demo is
  matched as `<div class="spec-body…>` up to the `</div>` before `<p class="spec-note">`. A spec
  block that loses its note, or gains a nested structure, silently drops out of the bundle. The
  `assert len(components) >= 15` catches a wholesale break, not a single missing card — compare
  the printed list against the design system's component index after any structural edit.
- **Foundation patterns are scoped to their own `<section>`.** They were not, once: run against
  the whole document, a greedy match ran to the last matching tag on the page and pulled half
  the system into one card (16,130px tall). Keep them scoped.
- **The CSS is linked, never inlined.** A rendered design receives only `styles.css`'s
  transitive `@import` closure. An earlier version inlined the stylesheet into every card: the
  cards looked perfect and proved nothing. If a card ever renders styled while a design built
  with the system does not, this is why.
- **The sticker field card is a still.** The live field is drawn by the page's own JavaScript,
  so lifting its markup yields an empty box; the builder bakes the ten cutouts in as `<img>`.
  If `slice_stickers.py` changes the `IMAGES` map, the `assert len(STICKERS) == 10` will fire.

## The landing page card

`components/Pages/LandingPage/` is the whole portfolio page as one card, built from
`site/index.html` with the runtime copied to `_preview/site.js`. It is the strongest usage
reference the bundle carries: every component in its real place and proportion, which no
single-component card can show.

Two things it must do that no other card does, both in `build_design_sync.py`:

- **Force the reveals before the runtime loads.** A card is never scrolled, so the reveal
  observer only ever fires for the first viewport and everything below it stays at opacity 0
  for ever. The first version of this card was 90% blank. Marking them done *before*
  `site.js` also lets the sticker field measure the final layout rather than the collapsed
  one.
- **Accept a mid-fall sticker still.** The pile takes 3-6s to settle and the render check
  screenshots sooner, so the contact sheet catches it in flight. The card is live, so it
  settles for anyone who opens it. Not worth chasing.

If `site/index.html` gains a `<script>` beyond `./assets/site.js`, the strip-and-relink in
the builder will not know about it.

## Known warnings, both benign

- `[FONT_MISSING] "Segoe Script", "Bradley Hand"` — these are *fallbacks* in the `--hand` stack
  after Caveat. Caveat itself ships as base64 in `fonts/fonts.css` and always loads, so the
  fallbacks never render. Not worth chasing.
- `--u` and a few other tokens are defined but unreferenced. Harmless.

## Verification, and what it caught

`package-validate.mjs` exits clean; the render check opens all 23 cards. Two graded `needs-work`
on the first pass and were fixed with per-card `viewport` attributes plus, for the collage, a
card-scoped rule that reveals captions a still can never hover for. See `CARD_FIT` in the
builder — each entry carries its reason.

The `.prompt.md` generation also caught a real bug in the design system itself: `.chip` went
`position:absolute` above 900px for *every* chip on the page, not only those inside `.stack`,
which was scattering the tool chips across the component demo. Now scoped.

## Playwright

This environment has `playwright-core` and a pre-installed chromium, but the validator imports
`playwright`. A one-file shim (`module.exports = require('playwright-core')`) placed in a
`node_modules/` beside the validator, plus `DS_CHROMIUM_PATH`, makes the real render check run.
Without it the validator fails `[RENDER_SKIPPED]`, and `--no-render-check` only downgrades that
to a warning — it does not verify anything.

## Upload

**Never done from this repo yet.** `DesignSync` could not authorize in any session that built
this bundle: `/design-login` needs an interactive terminal, which claude.ai/code sessions do
not have. Four attempts across two skill versions, same error every time. The bundle is built,
validated and graded; only the push is outstanding.

**The target is already decided — do not re-ask.** The user chose a **new design-system
project** (recorded in `config.json` under `target`). Proposed name: *Wendy Wong Design System*.
Check `list_projects` for a collision first, confirm the name, `create_project`, then record
`projectId` in `config.json` **before anything uploads**.

Run it from a local Claude Code session, or from a workspace seeded by Claude Design's
"Send to Claude Code Web". The whole thing is then:

    python3 build_design_sync.py
    DS_CHROMIUM_PATH=<chromium> node <skill>/package-validate.mjs ds-bundle --render-sample 0
    # then /design-sync — it reads config.json, creates the project, uploads ds-bundle/
