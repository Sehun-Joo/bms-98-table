# Insane BMS 98% difficulty table

A table of **1,035 Insane BMS charts**, ordered by estimated difficulty of achieving a **98% EX personal best**.

**[Browse the table](https://sehun-joo.github.io/bms-98-table/)** · **[Download the package](https://sehun-joo.github.io/bms-98-table/insane-98-ranges.zip)**

**Table import URL:** `https://sehun-joo.github.io/bms-98-table/`

The table has **68 difficulty-range folders**, averaging **15.2 charts per folder** (9–23). Lower **D98** values are easier. D98 is a fitted player-ability threshold, not a score percentage, BPI, or original star level.

## Use the table

- Open `index.html` to choose a difficulty folder, move to easier or harder ranges, or search charts. It works offline.
- For beatoraja-compatible players, close the game, copy `insane-98-ranges.bmt` into its existing `table` directory, and restart.
- For web table importers, host this directory and register the `index.html` URL. The page contains the standard `bmstable` header pointing to `header.json` and `data.json`.
- `insane-98-ranges.zip` contains the complete downloadable package.

This repository contains chart identifiers and table metadata, **not song files**. It has not been tested inside every BMS player.

## Method and limitations

The ranking uses roughly **7.7 million personal bests from 35,845 players**, drawn from the May 2026 LR2IR archive. A player-adjusted score model estimates ability; a second-stage, regularized logistic model estimates each chart's 98% threshold and slope.

Additional validation on held-out players found that the current model and a simpler shared-slope 98% model performed nearly identically, with a small numerical edge for the simpler model. The ranking is defensible, but is not claimed to be uniquely best.

**366 charts are provisional**, including **91 with no retained 98% achievement**. Their ranks rely more heavily on extrapolation. Repeated practice, score age, chart preference, and input-device differences are not fully corrected. Plays per player are shown as an exposure indicator, not a causal adjustment.

Read [the research review](research-review.html), [installation notes](README.txt), and [player-held-out validation](validation-player-holdout.json) for details and citations.

## Files and reproduction

- `data.json`, `header.json`: standard BMSTable metadata.
- `folders.json`: exact difficulty ranges and chart counts.
- `rankings.json`: fitted difficulty, rank, identifiers, support counts, and effort indicator.
- `insane-98-ranges.bmt`: native beatoraja-compatible table.
- `reproduce/`: model, regrouping, review, and offline picker-check scripts.
- `checksums.json`: checksums of the generated table package files.

The source database is not included. See `README.txt` and `prior-method-notes.txt` for reproduction details. The scripts retain their original build-directory defaults; supply explicit paths where supported.

## Sources and attribution

- [zkldi/lr2ir-dataset](https://github.com/zkldi/lr2ir-dataset): archived scores and chart metadata.
- [Insane table manifest](https://miraiscarlet.github.io/bms/table/genocide_insane/data_insane.json): chart membership, identifiers, and source links.
- Statistical and BPI references are linked in [the research review](research-review.html).

Original chart titles, artists, links, and identifiers are retained. No blanket license is asserted over third-party chart metadata or linked works.
