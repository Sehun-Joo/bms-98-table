from pathlib import Path
import json,html,hashlib,shutil,zipfile
ROOT=Path(__file__).resolve().parent;site=ROOT/'publish'/'bms-98-table'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
targets=read(site/'targets.json'); rows=[]
for key in ['aaa','max-minus']:
    v=read(site/key/'validation.json');t=targets[key];n=v['near_target']
    rows.append(f'<tr><td>{t["label"]}</td><td>{t["numerator"]}/{t["denominator"]}</td><td>{v["evaluation_records"]:,}</td><td>{v["near_target_records"]:,}</td><td>{n["target_specific"]["log_loss"]:.5f}</td><td>{n["score_curve"]["log_loss"]:.5f}</td><td>{n["raw_rate"]["log_loss"]:.5f}</td></tr>')
checks=read(site/'multi-target-checks.json')
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Score targets and validation</title><style>body{font:17px/1.6 system-ui;max-width:1050px;margin:40px auto;padding:0 22px;background:#10151e;color:#e7ebf2}a{color:#87c5ff}p,li{color:#c3cddd}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:10px;border-bottom:1px solid #364153;text-align:left}.scroll{overflow:auto}</style><a href="index.html">← Choose a score goal</a><h1>AAA, MAX− and 98% difficulty tables</h1>
<p>These are three independently fitted target-achievement rankings of the same 1,035 Insane charts. They share a latent scoring-ability scale estimated from actual player scores. Each target then gets its own chart-specific logistic thresholds and slopes. A chart can move relative to other charts when the target changes.</p>
<h2>Exact targets</h2><ul><li>AAA: EX/max ≥ 8/9 (88.888…%). Integer test: 9 × EX ≥ 8 × max.</li><li>MAX−: EX/max ≥ 17/18 (94.444…%). Integer test: 18 × EX ≥ 17 × max.</li><li>98%: EX/max ≥ 98/100. Integer test: 100 × EX ≥ 98 × max.</li></ul>
<p>No rounded displayed percentage is used to classify success. MAX− uses the <a href="https://iidx.org/compendium/exscore">common IIDX-style milestone</a> selected for this table. It is not the 26/27 target that beatoraja labels MAX− in its target menu.</p>
<h2>Validation for the new targets</h2><p>Chart parameters were fitted on 80% of players. For held-out players, half their scores estimated ability; the other half were evaluated, requiring at least five reference charts. The near-target group was defined using training-only score-model parameters. Lower log loss is better. This reuses the established evaluation design; it is not an untouched independent test of every possible modeling choice.</p>
<div class="scroll"><table><thead><tr><th>Target</th><th>Threshold</th><th>Evaluation PBs</th><th>Near-target PBs</th><th>Target model</th><th>Score curve</th><th>Raw rate</th></tr></thead><tbody>ROWS</tbody></table></div>
<p>The target-specific models beat these two comparators on near-target log loss. This does not establish universal optimality. Per-target JSON validation files are linked from the selector. The earlier <a href="research-review.html">98% research review</a> also discusses the nearly tied simpler shared-slope 98% model; that comparison should not be read as a AAA/MAX− experiment.</p>
<h2>Ranges and uncertainty</h2><p>Nearby fitted difficulty values are grouped in small value bands, then neighboring bands are combined toward 15 charts without splitting a band for a quota. Band width is selected from 0.01, 0.025 and 0.05 to put the average near 15; the original 98% folders are unchanged. Range bounds are inclusive below and exclusive above. DAAA, DMAX− and D98 are estimated ability thresholds, not EX percentages or ★ levels.</p>
<p>For the new targets, a chart is provisional if there are fewer than 100 usable PBs, fewer than five successes or five misses, or fewer than 30 players within one ability unit of its threshold. The unchanged 98% flags use the original rule. These are support checks, not confidence intervals. Cross-target threshold crossings found: CROSSINGS. Models are fitted independently; poorly supported estimates are not automatically forced to agree.</p>
<p>Practice amount, age of PBs, individual strengths and input devices remain potential biases. Plays/player is an aggregate indicator, not a correction. The archive does not support an equal-attempt-budget difficulty ranking or next-attempt probabilities.</p>
<h2>Importing into a game</h2><ul><li><a href="https://sehun-joo.github.io/bms-98-table/">98% table URL</a> (unchanged)</li><li><a href="https://sehun-joo.github.io/bms-98-table/aaa/">AAA table URL</a></li><li><a href="https://sehun-joo.github.io/bms-98-table/max-minus/">MAX− table URL</a></li></ul><p>The three links at the top open separate pages. Each page’s address and static BMSTable metadata import that page’s target. The selected target’s native .bmt download is also available on the page.</p>
<p>Source: <a href="https://github.com/zkldi/lr2ir-dataset">May 2026 LR2IR archive</a>. Original chart identities and source links are preserved. No song files are distributed.</p></html>'''
page=page.replace('ROWS',''.join(rows)).replace('CROSSINGS',str(len(checks['cross_target_threshold_crossings'])))
(site/'score-targets.html').write_text(page,encoding='utf-8')
readme='''# Insane BMS score difficulty tables

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
'''
(site/'README.md').write_text(readme,encoding='utf-8')
(site/'README.txt').write_text('INSANE BMS SCORE TABLES\n\nOpen index.html and select AAA, MAX-minus or 98%. Each goal has its own ranking and range folders.\n\nAAA = 8/9 EX. MAX-minus = 17/18 EX. 98% = 98/100 EX.\n\nGame import URLs:\nhttps://sehun-joo.github.io/bms-98-table/aaa/\nhttps://sehun-joo.github.io/bms-98-table/max-minus/\nhttps://sehun-joo.github.io/bms-98-table/\n\nFor beatoraja-compatible players, close the game, copy the desired .bmt from the corresponding folder into its table directory, and restart.\n\nSee score-targets.html for methods and validation; research-review.html covers the original 98% review. Practice bias remains. Original 98% ranks and folders are unchanged.\n',encoding='utf-8')
for name in ['test_multi_site.cjs','test_multi_exports.py','finalize_multi_site.py']:shutil.copy2(ROOT/name,site/'reproduce'/name)
files=[p for p in site.rglob('*') if p.is_file() and '.git' not in p.parts and p.suffix!='.zip' and p.name!='checksums.json']
manifest={p.relative_to(site).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(site/'checksums.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
with zipfile.ZipFile(site/'insane-score-tables.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in files+[site/'checksums.json']:z.write(p,Path('insane-score-tables')/p.relative_to(site))
shutil.copy2(site/'insane-score-tables.zip',ROOT.parent/'outputs'/'insane-score-tables.zip')
print('Prepared shared selector, target documentation, and complete download package.')
