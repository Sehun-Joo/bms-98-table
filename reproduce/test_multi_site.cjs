const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const base='work/publish/bms-98-table/';
class Element{constructor(){this.children=[];this.value='';this.textContent='';this.disabled=false;this.handlers={};}replaceChildren(...x){this.children=x;}append(...x){this.children.push(...x);}addEventListener(k,f){this.handlers[k]=f;}}
const ids=['target','folder','search','previous','next','folder-total','average','size-range','definition','difficulty-label','achievement-label','native','validation','notes','import-url','caution','rows','range','count'];
function run(path,initial){const page=fs.readFileSync(base+path,'utf8'),elements=Object.fromEntries(ids.map(id=>[id,new Element()]));const document={getElementById:k=>elements[k],createElement:()=>new Element()};vm.runInNewContext(page.match(/<script>([\s\S]*?)<\/script>/)[1],{document});assert.equal(elements.target.value,initial);return elements;}
const ui=run('index.html','98');let checked=0;
for(const [target,folderpath,threshold] of [['98','','98/100'],['aaa','aaa/','8/9'],['max-minus','max-minus/','17/18']]){
 const folders=JSON.parse(fs.readFileSync(base+folderpath+'folders.json','utf8'));
 const rankings=JSON.parse(fs.readFileSync(base+folderpath+'rankings.json','utf8'));
 ui.target.value=target;ui.target.handlers.change();assert.ok(ui.definition.textContent.includes(threshold));
 assert.equal(ui.folder.value,'001');assert.equal(ui.rows.children.length,folders[0].count);assert.equal(ui.previous.disabled,true);
 assert.equal(ui['import-url'].href,'https://sehun-joo.github.io/bms-98-table/'+folderpath);
 ui.next.onclick();assert.equal(ui.folder.value,'002');ui.previous.onclick();assert.equal(ui.folder.value,'001');
 for(const f of folders){ui.folder.value=f.id;ui.folder.handlers.change();assert.equal(ui.rows.children.length,f.count);checked++;}
 assert.equal(ui.next.disabled,true);
 ui.folder.value='all';ui.folder.handlers.change();assert.equal(ui.rows.children.length,1035);
 assert.equal(ui.rows.children[0].children[1].textContent,rankings[0].title);
 ui.search.value='Canon (blazing summer mix)';ui.search.handlers.input();assert.equal(ui.rows.children.length,1);
 ui.search.value='definitely-not-a-chart';ui.search.handlers.input();assert.equal(ui.rows.children.length,0);
}
run('aaa/index.html','aaa');run('max-minus/index.html','max-minus');
console.log('PASS: three target defaults, exact threshold labels, correct import URLs, '+checked+' folder counts, navigation, independent rank orders and search.');
