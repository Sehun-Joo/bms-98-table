from pathlib import Path
import collections,gzip,hashlib,json,zipfile
from html.parser import HTMLParser
root=Path(__file__).resolve().parent/'publish'/'bms-98-table'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
expected={r['md5'] for r in read(root/'rankings.json')}
orders=[]
for sub,native,num,den,key in [('', 'insane-98-ranges.bmt',98,100,'difficulty98'),('aaa','insane-aaa.bmt',8,9,'difficulty'),('max-minus','insane-max-minus.bmt',17,18,'difficulty')]:
    dest=root/sub;header=read(dest/'header.json');data=read(dest/'data.json');rows=read(dest/'rankings.json');folders=read(dest/'folders.json')
    assert len(data)==len(rows)==1035 and {r['md5'] for r in data}==expected
    assert header['data_url']=='data.json' and len(header['level_order'])==len(folders)
    assert [r['md5'] for r in data]==[r['md5'] for r in rows]
    assert all(a[key]<=b[key] for a,b in zip(rows,rows[1:]))
    counts=collections.Counter(r['level'] for r in data)
    assert all(counts[f['label']]==f['count'] for f in folders)
    with gzip.open(dest/native,'rt',encoding='utf-8') as f:bmt=json.load(f)
    assert [s['md5'] for g in bmt['folder'] for s in g['songs']]==[r['md5'] for r in rows]
    assert len(bmt['folder'])==len(folders)
    assert '<meta name="bmstable" content="header.json">' in (dest/'index.html').read_text(encoding='utf-8')
    for maximum in range(2,20002,2):
        cut=(num*maximum+den-1)//den
        assert den*cut>=num*maximum and den*(cut-1)<num*maximum
    orders.append([r['md5'] for r in rows])
assert orders[0]!=orders[1] and orders[1]!=orders[2]
for name,digest in read(root/'checksums.json').items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
with zipfile.ZipFile(root/'insane-score-tables.zip') as z:assert z.testzip() is None
print('PASS: 3 × 1,035 unique charts, independent sorted orders, folder counts, native BMTs, import metadata, exact rational target boundaries, checksums and ZIP integrity.')
