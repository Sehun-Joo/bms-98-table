// Offline UI-logic checks; this does not control or emulate a browser session.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const page=fs.readFileSync('outputs/insane-98-ranges/index.html','utf8');
const folders=JSON.parse(fs.readFileSync('outputs/insane-98-ranges/folders.json','utf8'));
const rows=[...page.matchAll(/<tr data-folder="([^"]+)" data-search="([^"]*)"/g)].map(m=>({dataset:{folder:m[1],search:m[2]},hidden:false}));
function control(value=''){return {value,textContent:'',disabled:false,handlers:{},addEventListener(k,f){this.handlers[k]=f;}};}
const controls={folder:control('001'),search:control(),previous:control(),next:control(),range:control(),count:control()};
const document={getElementById:k=>controls[k],querySelectorAll:()=>rows};
const script=page.match(/<script>([\s\S]*?)<\/script>/)[1];
vm.runInNewContext(script,{document});
assert.equal(rows.length,1035);assert.equal(rows.filter(r=>!r.hidden).length,folders[0].count);
assert.equal(controls.previous.disabled,true);
controls.next.onclick();assert.equal(controls.folder.value,'002');assert.equal(rows.filter(r=>!r.hidden).length,folders[1].count);
controls.previous.onclick();assert.equal(controls.folder.value,'001');
for(const f of folders){controls.folder.value=f.id;controls.folder.handlers.change();assert.equal(rows.filter(r=>!r.hidden).length,f.count);}
assert.equal(controls.next.disabled,true);
controls.folder.value='all';controls.folder.handlers.change();assert.equal(rows.filter(r=>!r.hidden).length,1035);
controls.search.value='Canon (blazing summer mix)'.toLowerCase();controls.search.handlers.input();assert.equal(rows.filter(r=>!r.hidden).length,1);
controls.search.value='chart-name-that-does-not-exist';controls.search.handlers.input();assert.equal(rows.filter(r=>!r.hidden).length,0);
assert.match(controls.count.textContent,/0 charts shown/);
console.log('PASS: all 68 folder counts, next/previous boundaries, all-charts selection, title search, empty results.');
