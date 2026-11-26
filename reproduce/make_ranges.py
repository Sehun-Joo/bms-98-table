"""Regroup a fitted ranking into value ranges without refitting or rank changes."""
from pathlib import Path
import argparse,collections,gzip,html,json,math,shutil

ROOT=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=ROOT.parent/'outputs'/'insane-98');ap.add_argument('--out',type=Path,default=ROOT.parent/'outputs'/'insane-98-ranges');args=ap.parse_args()
source=args.source;out=args.out
out.mkdir(parents=True,exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def dump(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
rows=read(source/'rankings.json'); original=read(source/'data.json')
byhash={r['md5']:r for r in original}
units=collections.defaultdict(list)
for r in rows:units[math.floor(r['difficulty98']*20+1e-9)].append(dict(r))
groups=[];current=[]
for bucket,members in sorted(units.items()):
    if len(current)>=8 and abs(len(current)-15)<=abs(len(current)+len(members)-15):
        groups.append(current);current=[]
    current.extend(members)
if current:
    if groups and len(current)<8:groups[-1].extend(current)
    else:groups.append(current)
starts=[math.floor(g[0]['difficulty98']*20+1e-9)/20 for g in groups]
ends=starts[1:]+[(math.floor(rows[-1]['difficulty98']*20+1e-9)+1)/20]
foldermeta=[];data=[];nativefolders=[];rankings=[]
for num,(g,lo,hi) in enumerate(zip(groups,starts,ends),1):
    key=f'{num:03}'; label=f'{key} | {lo:.2f}–{hi:.2f}'
    foldermeta.append({'id':key,'label':label,'lower_inclusive':lo,'upper_exclusive':hi,'count':len(g),
                       'provisional':sum(r['status']=='provisional' for r in g)})
    songs=[]
    for r in g:
        r.update(folder=key,folder_range=label);rankings.append(r)
        entry=dict(byhash[r['md5']]);entry['level']=label
        entry['comment']=f'D98={r["difficulty98"]:.4f}; rank {r["rank"]}; {r["status"]}; '+entry.get('comment','')
        data.append(entry)
        songs.append({k:entry[k] for k in ['md5','sha256','title','artist'] if k in entry})
    nativefolders.append({'name':f'D98 {label} ({len(g)})','songs':songs})
name='Insane 98% — difficulty ranges'
dump(out/'header.json',{'name':name,'symbol':'D98 ','data_url':'data.json','level_order':[g['label'] for g in foldermeta]})
dump(out/'data.json',data);dump(out/'rankings.json',rankings);dump(out/'folders.json',foldermeta)
native={'name':name,'url':'','tag':'D98','folder':nativefolders,'course':[]}
dump(out/'insane-98-ranges-native.json',native)
with gzip.open(out/'insane-98-ranges.bmt','wt',encoding='utf-8') as f:json.dump(native,f,ensure_ascii=False)
shutil.copy2(source/'validation.json',out/'validation-original.json')
shutil.copy2(source/'data-audit.json',out/'data-audit.json')
options='<option value="all">All folders · 1,035 charts</option>'+''.join(f'<option value="{g["id"]}" {"selected" if i==0 else ""}>{g["label"]} · {g["count"]} charts</option>' for i,g in enumerate(foldermeta))
table='\n'.join(f'<tr data-folder="{r["folder"]}" data-search="{html.escape(r["title"].lower(),quote=True)}" {"hidden" if r["folder"]!="001" else ""}><td>{r["rank"]}</td><td>{html.escape(r["title"])}</td><td title="{r["difficulty98"]:.8f}">{r["difficulty98"]:.3f}</td><td>★{html.escape(str(r["original_level"]))}</td><td>{r["achieved98"]:,} / {r["observations"]:,}</td><td><span class="{r["status"]}">{r["status"]}</span></td><td>{r["plays_per_player"]:.1f}</td></tr>' for r in rankings)
page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="bmstable" content="header.json"><title>Insane 98% · Difficulty ranges</title>
<style>:root{color-scheme:dark}*{box-sizing:border-box}body{font:16px/1.5 system-ui,sans-serif;margin:0;background:#10151e;color:#e7ebf2}main{max-width:1250px;margin:auto;padding:40px 24px}h1{font-size:34px;line-height:1.15;margin:12px 0}h2{font-size:20px}p{max-width:900px;color:#b4bfd0}.eyebrow{color:#87e2c6;font-size:13px;letter-spacing:.15em}.stats{display:flex;gap:24px;flex-wrap:wrap;margin:24px 0}.stats strong{font-size:25px;color:white}.stats span{display:block;color:#9caec5;font-size:13px}.controls{background:#1a2331;border:1px solid #344154;border-radius:12px;padding:18px;display:flex;gap:14px;align-items:end;flex-wrap:wrap}label{display:grid;gap:6px;font-size:13px;color:#b4bfd0}select,input,button{font:inherit;color:#e7ebf2;background:#111a27;border:1px solid #54647b;border-radius:6px;padding:10px}select{min-width:300px}input{min-width:220px}button{cursor:pointer}button:disabled{opacity:.35;cursor:default}a{color:#87c5ff}table{width:100%;border-collapse:collapse;font-size:14px}td,th{text-align:left;padding:13px 10px;border-bottom:1px solid #2c394b}th{color:#9caec5;font-size:12px;white-space:nowrap}td:first-child{color:#8096b2}td:nth-child(2){min-width:260px}tr[hidden]{display:none}.scroll{overflow:auto}.provisional{color:#f5ca7c}.supported{color:#87e2c6}.note{padding:14px 18px;border-left:3px solid #c79b55;background:#1c2330;font-size:14px}details{margin-top:28px;padding:18px;background:#161e2a;border-radius:10px}summary{cursor:pointer}#count{color:#87e2c6}footer{margin-top:30px;color:#8fa2bc;font-size:13px}@media(max-width:650px){main{padding:24px 14px}select,input{min-width:0;width:100%}label{width:100%}h1{font-size:28px}}</style></head><body><main>
<div class="eyebrow">BMS / INSANE / 98% EX</div><h1>Pick a difficulty range.</h1><p>Charts are ordered by <strong>D98</strong>: the estimated player scoring ability required to reach a 98% personal best. Lower is easier. These values are model units, not ★ levels, BPI, or score percentages.</p>
<div class="stats"><div><strong>1,035</strong><span>charts</span></div><div><strong>68</strong><span>range folders</span></div><div><strong>15.2</strong><span>charts per folder on average</span></div><div><strong>9–23</strong><span>charts per folder</span></div></div>
<div class="controls"><label>Difficulty folder<select id="folder">OPTIONS</select></label><button id="previous" aria-label="Previous easier folder">← Easier</button><button id="next" aria-label="Next harder folder">Harder →</button><label>Find a chart<input id="search" type="search" placeholder="Search selected folder…"></label></div>
<h2 id="range"></h2><p id="count" role="status" aria-live="polite"></p><div class="scroll"><table><thead><tr><th>RANK</th><th>CHART</th><th>D98 ≈</th><th>ORIGINAL</th><th>98% / PLAYERS</th><th>EVIDENCE</th><th>PLAYS / PLAYER</th></tr></thead><tbody>TABLE</tbody></table></div>
<p class="note">366 charts are provisional; 91 have no recorded 98% achievement in the modeling cohort. Their difficulty is extrapolated. Folder boundaries are convenient groupings, not confidence intervals.</p>
<details><summary>How the ranges and rankings work</summary><p>Nearby difficulty values are first grouped into 0.05-wide bands. Adjacent bands are combined to get close to 15 charts, without splitting a band to hit a quota. Ranges include their lower bound and exclude their upper bound; displayed chart values are rounded. This produces 68 folders of 9–23 charts.</p><p>The ranking uses 7.7 million personal bests from 35,845 players, with player ability adjustment and a 98%-specific scoring model. The order is unchanged from the first release. Read the <a href="research-review.html">method review and additional validation</a>.</p><p>Popular charts may be practiced more. Plays/player is an aggregate effort indicator, not a correction. These data cannot estimate equal-practice difficulty or next-attempt success. “Supported” means sufficient observation counts, not certainty.</p></details>
<footer><a href="insane-98-ranges.bmt" download>Native .bmt table</a> · <a href="README.txt">Installation and notes</a> · <a href="research-review.html">Research review</a><br>LR2IR archive: May 2026. All original chart hashes retained.</footer>
</main><script>
const folders=FOLDERS;
const select=document.getElementById('folder'), search=document.getElementById('search');
const rows=[...document.querySelectorAll('tbody tr')];
function render(){const id=select.value,q=search.value.toLowerCase().trim();let n=0;
for(const row of rows){row.hidden=!(id==='all'||row.dataset.folder===id)||!row.dataset.search.includes(q);if(!row.hidden)n++;}
const f=folders.find(f=>f.id===id);document.getElementById('range').textContent=f?`Folder ${f.id} · ${f.lower_inclusive.toFixed(2)} ≤ D98 < ${f.upper_exclusive.toFixed(2)}`:'All difficulty ranges';
document.getElementById('count').textContent=`${n} chart${n===1?'':'s'} shown`+(f?` · ${f.provisional} provisional in this folder`:'');
document.getElementById('previous').disabled=!f||id==='001';document.getElementById('next').disabled=!f||id===folders.at(-1).id;
search.placeholder=f?'Search selected folder…':'Search all charts…';}
select.addEventListener('change',render);search.addEventListener('input',render);
function step(d){const i=folders.findIndex(f=>f.id===select.value);if(i+d>=0&&i+d<folders.length){select.value=folders[i+d].id;render();}}
document.getElementById('previous').onclick=()=>step(-1);document.getElementById('next').onclick=()=>step(1);render();
</script></body></html>'''
page=page.replace('OPTIONS',options).replace('TABLE',table).replace('FOLDERS',json.dumps(foldermeta,ensure_ascii=False).replace('<','\\u003c'))
(out/'index.html').write_text(page,encoding='utf-8')
assert len(rankings)==1035 and len(groups)==68
assert [r['md5'] for r in rankings]==[r['md5'] for r in rows]
assert [r['difficulty98'] for r in rankings]==[r['difficulty98'] for r in rows]
assert len({r['md5'] for r in data})==1035
for g,lo,hi in zip(groups,starts,ends):assert all(lo<=r['difficulty98']<hi for r in g)
assert all(a==b for a,b in zip(ends[:-1],starts[1:]))
dump(out/'range-build-checks.json',{'charts':len(rankings),'folders':len(groups),'average':len(rows)/len(groups),'min':min(map(len,groups)),'max':max(map(len,groups)),'ordering_unchanged':True,'hashes_preserved':True,'nonoverlapping_contiguous_ranges':True,'base_band_width':.05,'target_count':15})
print('Built',len(groups),'ranges; counts',dict(collections.Counter(map(len,groups))),flush=True)
