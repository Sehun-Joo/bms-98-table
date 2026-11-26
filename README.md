# Insane BMS score difficulty tables

**[Open the table selector](https://sehun-joo.github.io/bms-98-table/)**

Choose **AAA**, **MAX−**, or **98% EX** from the same page. Each goal has its own fitted difficulty ranking and value-range folders, averaging roughly 15 charts each. All three contain the same 1,035 Insane charts. Lower difficulty values are easier.

| Target | Exact threshold | Game import URL |
|---|---|---|
| AAA | 8/9 = 88.888…% EX | https://sehun-joo.github.io/bms-98-table/aaa/ |
| MAX− | 17/18 = 94.444…% EX | https://sehun-joo.github.io/bms-98-table/max-minus/ |
| 98% | 98/100 EX | https://sehun-joo.github.io/bms-98-table/ |

The original root import URL still imports the 98% table. The three links at the top navigate to separate importable page addresses. The page displays the appropriate URL and native `.bmt` download for the selected target.

MAX− here means the common 94.44% milestone, not beatoraja's named 26/27 target.

## Downloads

- [All three tables and offline selector](https://sehun-joo.github.io/bms-98-table/insane-score-tables.zip)
- [AAA native table](https://sehun-joo.github.io/bms-98-table/aaa/insane-aaa.bmt)
- [MAX− native table](https://sehun-joo.github.io/bms-98-table/max-minus/insane-max-minus.bmt)
- [98% native table](https://sehun-joo.github.io/bms-98-table/insane-98-ranges.bmt)

For beatoraja-compatible players, close the game, copy the desired `.bmt` into its existing `table` directory, and restart. These files have not been tested in every player. No song files are included.

## Method and limits

Roughly 7.7 million PBs from 35,845 players estimate a common scoring-ability scale. Separate regularized logistic models fit each target's achievement threshold and chart slope. AAA and MAX− were validated on held-out players and beat the tested raw-rate and full-score-curve baselines near their target. This is not a claim of universal optimality.

See [target definitions and validation](score-targets.html), [the 98% research review](research-review.html), and the per-target JSON files. The 98% order and folders are preserved from the previous release. Its research review found a simpler threshold model nearly tied with the current one.

Practice amount, score age, chart preference, device differences, and specialist skills are not fully corrected. Provisional charts may depend on extrapolation. Plays/player is an indicator, not an equal-practice adjustment. Difficulty values are not confidence statements, score percentages, BPI, or original ★ levels.

## Sources and reproduction

- [zkldi/lr2ir-dataset](https://github.com/zkldi/lr2ir-dataset): archived scores and chart metadata.
- [Insane chart manifest](https://miraiscarlet.github.io/bms/table/genocide_insane/data_insane.json): chart membership, identifiers, and original links.
- `reproduce/` contains fitting, export, and test scripts; local source database/cache files are excluded. Scripts retain their original workspace defaults.
- `checksums.json` covers generated public files except ZIPs and itself. ZIP contents contain a corresponding checksum manifest.

Original chart titles, artists, links, and identifiers are retained. No blanket license is asserted over third-party metadata or linked works.
