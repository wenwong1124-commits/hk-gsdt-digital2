# Sticker sheets

Drop the two sheets here. Any filename works — the slicer reads them in
alphabetical order, so name them so sheet A sorts first:

    sheet-a.png
    sheet-b.png

Each sheet is expected to be a 3 × 4 grid of die-cut stickers on a flat
magenta ground. PNG or JPG, any resolution.

Then, from the repo root:

    python3 slice_stickers.py assets/stickers
    python3 build.py

`assets/stickers/cut/` will fill with the individual transparent cutouts,
and the artwork is inlined into `design-system.html`. Nothing is redrawn.
