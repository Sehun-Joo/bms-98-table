"""Build three independently ranked score tables and a shared offline-capable UI."""
from pathlib import Path
import collections,gzip,hashlib,html,json,math,shutil,zipfile
ROOT=Path(__file__).resolve().parent
SITE=ROOT/'publish'/'bms-98-table'
BASE='https://sehun-joo.github.io/bms-98-table/'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
old=read(SITE/'rankings.json');oldfolders=read(SITE/'folders.json')
metadata={r['md5']:r for r in read(ROOT/'metadata.json')}
def group(rows,width):
    units=collections.defaultdict(list)
    for r in rows:units[math.floor(r['difficulty']/width+1e-9)].append(r)
    groups=[];cur=[]
    for _,items in sorted(units.items()):
        if len(cur)>=8 and abs(len(cur)-15)<=abs(len(cur)+len(items)-15):groups.append(cur);cur=[]
        cur.extend(items)
    if cur:
        if groups and len(cur)<8:groups[-1].extend(cur)
        else:groups.append(cur)
    return groups
targets={}
for slug,label,num,den,code in [('98','98%',98,100,'D98'),('aaa','AAA',8,9,'DAAA'),('max-minus','MAX−',17,18,'DMAX−')]:
    if slug=='98':
        rows=[dict(r,difficulty=r['difficulty98'],achieved=r['achieved98']) for r in old]
        folders=oldfolders;path='';native='insane-98-ranges.bmt';validation='validation-player-holdout.json';width=.05
    else:
        rows=read(ROOT/(slug+'-rankings.json'));path=slug+'/';dest=SITE/slug;dest.mkdir(exist_ok=True)
        choices=[(w,group(rows,w)) for w in [.01,.025,.05]]
        width,groups=min(choices,key=lambda pair:abs(len(rows)/len(pair[1])-15))
        lower=[math.floor(g[0]['difficulty']/width+1e-9)*width for g in groups]
        upper=lower[1:]+[(math.floor(rows[-1]['difficulty']/width+1e-9)+1)*width]
        digits=3 if width==.025 else 2;folders=[];data=[];nativefolders=[]
        for i,(g,lo,hi) in enumerate(zip(groups,lower,upper),1):
            key=f'{i:03}';tag=f'{key} | {lo:.{digits}f}–{hi:.{digits}f}';songs=[]
            folders.append({'id':key,'label':tag,'lower_inclusive':round(lo,8),'upper_exclusive':round(hi,8),'count':len(g),'provisional':sum(r['status']=='provisional' for r in g)})
            for r in g:
                r['folder']=key;r['folder_range']=tag;m=metadata[r['md5']]
                entry={k:m[k] for k in ['md5','sha256','title','artist','url','url_diff'] if m.get(k)}
                entry.update(level=tag,comment=f'{label} rank {r["rank"]}/1035; {code}={r["difficulty"]:.4f}; original ★{r["original_level"]}; {r["achieved"]}/{r["observations"]} achieved; {r["status"]}')
                data.append(entry);songs.append({k:entry[k] for k in ['md5','sha256','title','artist'] if k in entry})
            nativefolders.append({'name':f'{code} {tag} ({len(g)})','songs':songs})
        header={'name':f'Insane {label} — difficulty ranges','symbol':code+' ','data_url':'data.json','level_order':[f['label'] for f in folders]}
        dump(dest/'header.json',header);dump(dest/'data.json',data);dump(dest/'rankings.json',rows);dump(dest/'folders.json',folders)
        native=f'insane-{slug}.bmt'
        with gzip.open(dest/native,'wt',encoding='utf-8') as f:json.dump({'name':header['name'],'url':BASE+path,'tag':code,'folder':nativefolders,'course':[]},f,ensure_ascii=False)
        validation='validation.json';shutil.copy2(ROOT/(slug+'-validation.json'),dest/validation)
        assert len({r['md5'] for r in data})==1035
        for r in rows:
            folder=folders[int(r['folder'])-1];assert folder['lower_inclusive']<=r['difficulty']<folder['upper_exclusive']
    targets[slug]={'id':slug,'label':label,'numerator':num,'denominator':den,'code':code,'path':path,'native':native,
       'validation':validation,'rows':rows,'folders':folders,'base_band_width':width,
       'provisional':sum(r['status']=='provisional' for r in rows),'zero_success':sum(r['achieved']==0 for r in rows)}
    print(label,'folders',len(folders),'average',round(len(rows)/len(folders),2),'provisional',targets[slug]['provisional'],flush=True)
assert [r['md5'] for r in targets['98']['rows']]==[r['md5'] for r in old]
for t in targets.values():assert len(t['rows'])==1035 and all(a['difficulty']<=b['difficulty'] for a,b in zip(t['rows'],t['rows'][1:]))
dump(SITE/'targets.json',{key:{k:v for k,v in t.items() if k not in ['rows','folders']} for key,t in targets.items()})
payload=json.dumps(targets,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
style=''' :root{color-scheme:dark}*{box-sizing:border-box}body{font:16px/1.5 system-ui,sans-serif;margin:0;background:#10151e;color:#e7ebf2}main{max-width:1300px;margin:auto;padding:36px 24px}h1{font-size:34px;line-height:1.15;margin:12px 0}h2{font-size:20px}p{max-width:1000px;color:#b4bfd0}.eyebrow{color:#87e2c6;font-size:13px;letter-spacing:.15em}.stats{display:flex;gap:28px;flex-wrap:wrap;margin:24px 0}.stats strong{font-size:25px;color:white}.stats span{display:block;color:#9caec5;font-size:13px}.controls{background:#1a2331;border:1px solid #344154;border-radius:12px;padding:18px;display:flex;gap:14px;align-items:end;flex-wrap:wrap}label{display:grid;gap:6px;font-size:13px;color:#b4bfd0}select,input,button{font:inherit;color:#e7ebf2;background:#111a27;border:1px solid #54647b;border-radius:6px;padding:10px}select{min-width:235px}input{min-width:200px}button{cursor:pointer}button:disabled{opacity:.35;cursor:default}a{color:#87c5ff}table{width:100%;border-collapse:collapse;font-size:14px}td,th{text-align:left;padding:13px 10px;border-bottom:1px solid #2c394b}th{color:#9caec5;font-size:12px;white-space:nowrap}td:first-child{color:#8096b2}td:nth-child(2){min-width:260px}.scroll{overflow:auto}.provisional{color:#f5ca7c}.supported{color:#87e2c6}.note{padding:14px 18px;border-left:3px solid #c79b55;background:#1c2330;font-size:14px}details{margin-top:28px;padding:18px;background:#161e2a;border-radius:10px}summary{cursor:pointer}#count{color:#87e2c6}.links{display:flex;gap:18px;flex-wrap:wrap}.import{font-size:14px;overflow-wrap:anywhere}footer{margin-top:30px;color:#8fa2bc;font-size:13px}@media(max-width:650px){main{padding:24px 14px}select,input{min-width:0;width:100%}label{width:100%}h1{font-size:28px}}'''
template='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="bmstable" content="header.json"><title>Insane BMS · AAA, MAX− and 98% tables</title><style>STYLE</style></head><body><main>
<div class="eyebrow">BMS / INSANE / SCORE DIFFICULTY</div><h1>Pick a score goal. Find your next chart.</h1><p>Each goal has its own player-adjusted difficulty ranking. Lower difficulty values are easier. Values represent estimated scoring ability, not ★ levels, BPI, or score percentages.</p>
<div class="controls"><label>Score goal<select id="target"><option value="aaa">AAA · 88.89% EX</option><option value="max-minus">MAX− · 94.44% EX</option><option value="98">98% EX</option></select></label><label>Difficulty folder<select id="folder"></select></label><button id="previous" aria-label="Previous easier folder">← Easier</button><button id="next" aria-label="Next harder folder">Harder →</button><label>Find a chart<input id="search" type="search" placeholder="Search selected folder…"></label></div>
<div class="stats"><div><strong>1,035</strong><span>charts per goal</span></div><div><strong id="folder-total"></strong><span>range folders</span></div><div><strong id="average"></strong><span>charts per folder on average</span></div><div><strong id="size-range"></strong><span>charts per folder</span></div></div>
<p id="definition"></p><div class="links"><a id="native" download>Download selected .bmt table</a><a id="validation">Selected target validation</a><a id="notes">Methods and target definitions</a></div><p class="import">Selected table import URL: <a id="import-url"></a></p>
<h2 id="range"></h2><p id="count" role="status" aria-live="polite"></p><div class="scroll"><table><thead><tr><th>RANK</th><th>CHART</th><th id="difficulty-label">DIFFICULTY ≈</th><th>ORIGINAL</th><th id="achievement-label">ACHIEVED / PLAYERS</th><th>EVIDENCE</th><th>PLAYS / PLAYER</th></tr></thead><tbody id="rows"></tbody></table></div>
<p class="note" id="caution"></p>
<details><summary>How these tables work</summary><p>The model uses actual EX scores to estimate scoring ability from overlapping players. Each goal then has its own fitted achievement curve, chart difficulty estimates, and sorted folders. AAA means EX/max ≥ 8/9. MAX− here means EX/max ≥ 17/18, the common 94.44% milestone—not beatoraja’s separately named 26/27 target.</p><p>Folders group nearby difficulty values toward an average of 15 charts; they are not forced to equal size. Bounds include the lower value and exclude the upper value. Values on individual rows are rounded.</p><p>These are historical PB rankings. Repeated practice, old scores, input devices and individual strengths can affect them. Plays/player is an exposure indicator, not a correction. Provisional means weak evidence, not a precise ordering. Independent target models may occasionally cross on weakly supported charts.</p><p>For game import, use the URL shown for the selected goal. The original root URL still imports the 98% table; changing the browser selector does not change what a game importer sees at that URL.</p></details>
<footer>Data: LR2IR archive, May 2026. All original chart hashes retained. <a href="https://github.com/Sehun-Joo/bms-98-table">GitHub</a></footer>
</main><script>
const targets=PAYLOAD, defaultTarget=DEFAULT, rootPrefix=PREFIX;
const $=id=>document.getElementById(id), select=$('target'),folder=$('folder'),search=$('search');
function option(value,text){const o=document.createElement('option');o.value=value;o.textContent=text;return o;}
function goalChanged(){const t=targets[select.value];folder.replaceChildren(option('all','All folders · 1,035 charts'),...t.folders.map(f=>option(f.id,`${f.label} · ${f.count} charts`)));folder.value='001';search.value='';
$('folder-total').textContent=t.folders.length;$('average').textContent=(t.rows.length/t.folders.length).toFixed(1);const sizes=t.folders.map(f=>f.count);$('size-range').textContent=`${Math.min(...sizes)}–${Math.max(...sizes)}`;
$('definition').textContent=`${t.label}: EX/max ≥ ${t.numerator}/${t.denominator} (${(100*t.numerator/t.denominator).toFixed(4)}%). ${t.code} estimates the scoring ability needed for this specific goal; lower is easier.`;
$('difficulty-label').textContent=t.code+' ≈';$('achievement-label').textContent=t.label+' / PLAYERS';
$('native').href=rootPrefix+t.path+t.native;$('validation').href=rootPrefix+t.path+t.validation;$('notes').href=rootPrefix+'score-targets.html';const url='https://sehun-joo.github.io/bms-98-table/'+t.path;$('import-url').href=url;$('import-url').textContent=url;
$('caution').textContent=`${t.provisional} charts are provisional; ${t.zero_success} have no recorded target achievement in the modeling cohort. Weakly supported thresholds can depend on extrapolation. Folder boundaries are convenient groups, not confidence intervals.`;render();}
function render(){const t=targets[select.value],id=folder.value,q=search.value.toLowerCase().trim(),f=t.folders.find(f=>f.id===id);const matched=t.rows.filter(r=>(id==='all'||r.folder===id)&&r.title.toLowerCase().includes(q));
const nodes=matched.map(r=>{const tr=document.createElement('tr');const values=[r.rank,r.title,r.difficulty.toFixed(3),'★'+r.original_level,r.achieved.toLocaleString()+' / '+r.observations.toLocaleString(),r.status,r.plays_per_player.toFixed(1)];values.forEach((v,i)=>{const td=document.createElement('td');td.textContent=v;if(i===5)td.className=r.status;if(i===2)td.title=r.difficulty.toFixed(8);tr.append(td);});return tr;});$('rows').replaceChildren(...nodes);
$('range').textContent=f?`${t.label} · Folder ${f.id} · ${f.lower_inclusive.toFixed(3)} ≤ ${t.code} < ${f.upper_exclusive.toFixed(3)}`:`${t.label} · All difficulty ranges`;
$('count').textContent=`${matched.length} chart${matched.length===1?'':'s'} shown`+(f?` · ${f.provisional} provisional in this folder`:'');$('previous').disabled=!f||id==='001';$('next').disabled=!f||id===t.folders.at(-1).id;search.placeholder=f?'Search selected folder…':'Search all charts…';}
select.addEventListener('change',goalChanged);folder.addEventListener('change',render);search.addEventListener('input',render);
function step(d){const fs=targets[select.value].folders,i=fs.findIndex(f=>f.id===folder.value);if(i+d>=0&&i+d<fs.length){folder.value=fs[i+d].id;render();}}
$('previous').onclick=()=>step(-1);$('next').onclick=()=>step(1);
select.value=defaultTarget;goalChanged();
</script></body></html>'''
for slug,t in targets.items():
    dest=SITE/t['path'];prefix='../' if t['path'] else ''
    page=template.replace('STYLE',style).replace('PAYLOAD',payload).replace('DEFAULT',json.dumps(slug)).replace('PREFIX',json.dumps(prefix))
    (dest/'index.html').write_text(page,encoding='utf-8')
# Report cross-target consistency rather than silently altering fitted estimates.
maps={k:{r['md5']:r for r in t['rows']} for k,t in targets.items()}
crossings=[]
for md5 in maps['98']:
    vals=[maps[k][md5]['difficulty'] for k in ['aaa','max-minus','98']]
    if vals[0]>vals[1] or vals[1]>vals[2]:crossings.append({'md5':md5,'values_AAA_MAXminus_98':vals})
dump(SITE/'multi-target-checks.json',{'thresholds':{'aaa':[8,9],'max-minus':[17,18],'98':[98,100]},'charts_each':1035,'existing_98_order_preserved':True,'cross_target_threshold_crossings':crossings})
for name in ['build_extra_targets.py','build_multi_site.py','build_table.py','fit_target_separable.py']:
    shutil.copy2(ROOT/name,SITE/'reproduce'/name)
print('Cross-target threshold crossings:',len(crossings),flush=True)
