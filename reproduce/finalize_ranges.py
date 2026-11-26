from pathlib import Path
import html,json,gzip,hashlib,shutil,zipfile
ROOT=Path(__file__).resolve().parent
out=ROOT.parent/'outputs'/'insane-98-ranges'
review=json.loads((ROOT/'model-review-validation.json').read_text(encoding='utf-8'))
checks=json.loads((out/'range-build-checks.json').read_text(encoding='utf-8'))
shutil.copy2(ROOT/'model-review-validation.json',out/'validation-player-holdout.json')
names={'raw_rate':'Raw chart achievement rate','chart_score_curve':'Player-adjusted score curve','shared_slope_98':'98% model, shared chart slope','chart_slope_98':'98% model, separate chart slopes (current)'}
trs=''.join(f'<tr><td>{names[k]}</td><td>{review["near_target"][k]["log_loss"]:.5f}</td><td>{review["near_target"][k]["brier"]:.5f}</td><td>{review["overall"][k]["log_loss"]:.5f}</td></tr>' for k in names)
paired=''.join(f'<li>Compared with {names[k].lower()}: log-loss difference {v["target_minus_comparator_log_loss"]:.5f}; player-bootstrap 95% interval [{v["interval95"][0]:.5f}, {v["interval95"][1]:.5f}]. Negative favors the current model.</li>' for k,v in review['paired_player_bootstrap'].items())
winner=min(review['near_target'],key=lambda k:review['near_target'][k]['log_loss'])
interval=review['paired_player_bootstrap']['shared_slope_98']['interval95']
assert interval[0]<0<interval[1], 'Reassess retention decision if models are clearly separated.'
text=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>98% table · Method review</title><style>body{{font:17px/1.6 system-ui;max-width:950px;margin:40px auto;padding:0 22px;background:#10151e;color:#e7ebf2}}a{{color:#87c5ff}}h1,h2{{line-height:1.2}}p,li{{color:#c3cddd}}table{{border-collapse:collapse;width:100%;font-size:15px}}th,td{{padding:10px;border-bottom:1px solid #364153;text-align:left}}.note{{background:#1c2634;padding:18px;border-radius:8px}}small{{color:#9caec5}}</style>
<a href="index.html">← Pick a folder</a><h1>Was this the best method?</h1>
<p class="note"><strong>A defensible method, but not uniquely best.</strong> The extra player-held-out check favors both 98%-specific models over the full-score curve. The simpler shared-slope model has a small numerical edge over the current chart-slope model; their paired player-bootstrap interval includes zero. I retained the current ordering because this check does not reliably distinguish them, and changed the grouping and browsing. A preference for fewer parameters would also make the shared-slope model a reasonable choice.</p>
<h2>What D98 actually measures</h2><p>98% EX is the target. D98 is our fitted difficulty rating for that target: the estimated player ability at the 50% achievement point of a chart's logistic curve. Ability is standardized internally; D98 is neither an EX percentage nor BPI nor the original ★ level. Lower values are easier.</p>
<p>The implemented model is a <strong>two-stage, regularized model</strong>. First, full scores estimate one player ability and a separate scoring curve for each chart. Then observed 98% achievements and misses fit each chart's threshold and slope, with priors anchored to the first model. It is not a fully Bayesian joint ordinal IRT model. Its uncertainty flags are count-based, not credible intervals.</p>
<h2>Additional validation</h2><p>I fitted chart parameters using 80% of players. For the held-out players, half their scores were used only to infer ability; their remaining scores were evaluated without entering the fit or their ability estimates. Players needed at least five reference charts. This evaluated <strong>{review['evaluation_records']:,} records from {review['evaluated_players']:,} held-out players</strong>, including <strong>{review['near_target_records']:,} records near the target</strong>.</p>
<p>The near-target group was defined from the training score model, before looking at evaluation outcomes. Lower log loss and Brier score are better. The shared-slope comparator here models the exact 98% outcome using the same ability estimates; it is a stronger comparator than the shared-slope full-score curve used in the first release.</p>
<table><thead><tr><th>Model</th><th>Near-target log loss</th><th>Near-target Brier</th><th>Overall log loss</th></tr></thead><tbody>{trs}</tbody></table>
<p>Paired differences were also resampled by player, so repeated chart results from one person stay together:</p><ul>{paired}</ul>
<p>These bootstrap intervals describe predictive-loss differences on this evaluation cohort. They are not confidence intervals for chart difficulty or rank. The current model predicted 32.2% achievement in the near-target group versus 35.9% observed, so calibration is still imperfect for held-out players. This is an additional validation experiment, not a claim that every possible model has been tested. Full metrics and practice-proxy strata are in <a href="validation-player-holdout.json">the validation file</a>.</p>
<h2>What the research supports</h2>
<p>Player/item models can account for overlapping, incomplete results and distinguish ability from chart difficulty. The <a href="https://mc-stan.org/docs/stan-users-guide/regression.html#item-response-theory-models">Stan IRT documentation</a> describes 1PL and multilevel 2PL models. Using separate chart slopes is appropriate to test when score curves differ.</p>
<p>There is also a directly relevant rhythm-game precedent: <a href="https://github.com/BPIManager/BPIManager2/blob/master/docs/bpi-math.md">BPIManager's experimental distribution-based model</a> fits a transformed score deficit against latent player skill with chart-specific coefficients. That supports this as a plausible starting point; performance on IIDX does not establish performance on BMS.</p>
<p>Fixed-ability, second-stage item calibration is sensitive to the ability estimator and slope priors. <a href="https://files.eric.ed.gov/fulltext/EJ1465056.pdf">Fu, Ho and Tan (2025)</a> study those choices and recommend regularized combinations under their tested conditions. Our priors are practical choices, not empirically optimized or uniquely justified settings, and the second stage treats ability estimates as fixed.</p>
<h2>What remains unresolved</h2><p>Ability adjustment does not remove all self-selection. People choose styles they like and charts they can improve. <a href="https://bpspsychub.onlinelibrary.wiley.com/doi/10.1111/bmsp.12097">Liu and Wang's research on examinee-selected items</a> explicitly models selection jointly with performance. Such a model introduces additional assumptions; a sparse archive does not identify the missing results automatically.</p>
<p><strong>Popularity and grinding remain confounded with difficulty.</strong> One PB per person prevents repeat attempts being counted as independent players, but a PB can improve with practice. Aggregate plays/player cannot tell us how many serious scoring attempts each player made. Penalizing popular charts would risk penalizing charts that are actually easy. The table therefore shows the exposure indicator without inventing an equal-practice correction.</p>
<p>The snapshot combines old and recent PBs, device types and individual chart strengths. 366 charts are provisional, including 91 with no retained 98% achievement. Their upper-tail thresholds depend strongly on extrapolation and priors. More records below the target do not eliminate that problem.</p>
<h2>What could improve a future version</h2><p>A joint hierarchical model would propagate player-ability uncertainty. An ordinal model could use several score bands coherently, and a small multidimensional model could represent scratch, timing and density strengths. Those are candidates to test with the same held-out protocol, not automatic upgrades. Repeated player bootstraps/refits could quantify folder stability. The strongest way to study practice bias would be new data with attempt counts and scores at a common attempt budget.</p>
<h2>Why these folders</h2><p>Folder assignment uses D98 itself, not a fixed number of rows. Scores first enter 0.05-wide bands; adjacent bands are merged toward 15 charts, without splitting bands to hit a quota. Result: {checks['folders']} contiguous, nonoverlapping ranges, averaging {checks['average']:.1f} charts (range {checks['min']}–{checks['max']}). Dense parts have narrower ranges; sparse tails have wider ones. This is a usability choice, not a statistical confidence statement.</p>
<small>Review prepared 2026-11-25, America/New_York. Data snapshot: May 2026. Source: <a href="https://github.com/zkldi/lr2ir-dataset">zkldi/lr2ir-dataset</a>.</small></html>'''
(out/'research-review.html').write_text(text,encoding='utf-8')
readme=f'''INSANE 98% — DIFFICULTY RANGES

1,035 charts; {checks['folders']} folders; {checks['average']:.1f} charts per folder on average.
Counts vary from {checks['min']} to {checks['max']}. D98 is our estimated scoring-ability
threshold for a 98% EX personal best; lower is easier. It is not EX%, BPI, or ★ level.
The chart ordering is unchanged from the first release; grouping is now value-based.

PICK A FOLDER
Open index.html. Select a difficulty range, use Easier/Harder, or choose All folders
to search the entire list. The page works offline. Lower bound is inclusive and
upper bound exclusive; displayed chart values are rounded.

GAME TABLE
For beatoraja-compatible players, close the game and place insane-98-ranges.bmt in
its existing table directory, then restart. This version has a different table name
from the previous release. No installation was performed in your running game.
The standard BMSTable files are index.html, header.json, and data.json. Host them
together if you need an import URL for another table importer. No public URL is hosted.

REVIEW
Read research-review.html for citations, limitations, and the new player-held-out
comparison. The two 98%-specific models were not reliably distinguished in the new
comparison, with a small numerical edge for the simpler model. The current order
was retained; it is not claimed to be uniquely best. 366 charts are provisional and 91 have no observed 98% in
the modeling cohort. Practice/popularity effects cannot be fully separated from
difficulty using personal-best snapshots.

FILES
folders.json: exact ranges and counts.
rankings.json: original estimates, ranks, chart identifiers, effort/support indicators.
validation-original.json: first release's score holdout results.
validation-player-holdout.json: additional player-held-out comparison and bootstrap.
range-build-checks.json: coverage, preserved order and folder checks.

REPRODUCTION
reproduce/make_ranges.py contains the exact regrouping rule (source paths in script).
reproduce/review_model.py contains the additional validation experiment.
The prior model generator and source manifest are also included. Scripts require
numpy/scipy and the original archive database; see prior-method-notes.txt.
Offline picker tests passed for all folders, navigation, all charts, and search.
Browser visual verification was unavailable because automated file: navigation was
blocked by the browser URL policy. No claim of in-game testing is made.
'''
(out/'README.txt').write_text(readme,encoding='utf-8')
rep=out/'reproduce';rep.mkdir(exist_ok=True)
for p in (ROOT.parent/'outputs'/'insane-98'/'reproduce').iterdir():
    if p.is_file():shutil.copy2(p,rep/p.name)
for n in ['make_ranges.py','review_model.py','test_ranges.cjs','finalize_ranges.py']:
    shutil.copy2(ROOT/n,rep/n)
shutil.copy2(ROOT.parent/'outputs'/'insane-98'/'README.txt',out/'prior-method-notes.txt')
ranking=json.loads((out/'rankings.json').read_text(encoding='utf-8'))
with gzip.open(out/'insane-98-ranges.bmt','rt',encoding='utf-8') as f:native=json.load(f)
assert [s['md5'] for g in native['folder'] for s in g['songs']]==[r['md5'] for r in ranking]
assert len(native['folder'])==checks['folders']
manifest={str(p.relative_to(out)):hashlib.sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file() and p.name!='checksums.json'}
(out/'checksums.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
with zipfile.ZipFile(out.parent/'insane-98-ranges.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in out.rglob('*'):
        if p.is_file():z.write(p,Path(out.name)/p.relative_to(out))
print('Packaged range table and research review; all hashes and folder counts verified.')
