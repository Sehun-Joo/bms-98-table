"""Fit AAA and conventional MAX-minus independently on the same scoring scale."""
import json,math
from pathlib import Path
import numpy as np
from scipy.special import ndtr,expit
from build_table import ROOT,latent,metrics,dump
from fit_target_separable import target_fit

raw=np.load(ROOT/'observations.npz')['rows']
ids,cnt=np.unique(raw[:,0],return_counts=True)
rows=raw[np.isin(raw[:,0],ids[cnt>=10])];del raw
ids,p=np.unique(rows[:,0],return_inverse=True);P=len(ids);J=1035;j=rows[:,1]
t=-np.log((rows[:,3]-rows[:,2]+.5)/(rows[:,3]+.5))
rng=np.random.default_rng(20261125);trainplayers=rng.random(P)<.8;train=trainplayers[p]
reference=(~train)&(rng.random(len(p))<.5);test=(~train)&(~reference)
_,pt=np.unique(p[train],return_inverse=True)
cache=np.load(ROOT/'review-model-parameters.npz');theta,mu,a,sigma=[cache[k] for k in ['theta','mu','a','sigma']]
assert len(theta)==len(np.unique(pt))
pr,jr,tr=p[reference],j[reference],t[reference];w=np.ones(len(pr));skill=np.zeros(P)
for it in range(40):
    old=skill.copy();skill=np.bincount(pr,weights=w*a[jr]*(tr-mu[jr]),minlength=P)/(np.bincount(pr,weights=w*a[jr]**2,minlength=P)+.5)
    resid=tr-mu[jr]-a[jr]*skill[pr];w=np.minimum(1,.65/np.maximum(abs(resid),1e-8))
    if np.max(abs(old-skill))<1e-5:break
test &= np.bincount(pr,minlength=P)[p]>=5
fullcache=ROOT/'full-score-model.npz'
if fullcache.exists():
    c=np.load(fullcache);fulltheta,fullmu,fulla,fullsigma=[c[k] for k in ['theta','mu','a','sigma']]
else:
    fulltheta,fullmu,fulla,fullsigma,it=latent(p,j,t,P,J,variable=True)
    np.savez_compressed(fullcache,theta=fulltheta,mu=fullmu,a=fulla,sigma=fullsigma)
meta=json.loads((ROOT/'metadata.json').read_text(encoding='utf-8'))
n=np.bincount(j,minlength=J)
for slug,label,num,den in [('aaa','AAA',8,9),('max-minus','MAX−',17,18)]:
    if all((ROOT/(slug+suffix)).exists() for suffix in ['-rankings.json','-validation.json','-parameters.npz']):
        print('Reusing completed target:',label,flush=True);continue
    target=num/den;threshold=-math.log1p(-target)
    y=(den*rows[:,2]>=num*rows[:,3]).astype(float)
    print('Fitting held-out-player validation:',label,flush=True)
    bh,ah=target_fit(theta,mu,a,pt,j[train],y[train],J,target)
    qj,qp,qy=j[test],p[test],y[test]
    near=abs(skill[qp]-(threshold-mu[qj])/a[qj])<1
    nh=np.bincount(j[train],minlength=J);wins=np.bincount(j[train],weights=y[train],minlength=J)
    pred={'target_specific':expit(ah[qj]*(skill[qp]-bh[qj])),
          'score_curve':ndtr((mu[qj]+a[qj]*skill[qp]-threshold)/sigma[qj]),
          'raw_rate':((wins+.5)/(nh+1))[qj]}
    validation={'target':label,'numerator':num,'denominator':den,'threshold':target,
      'design':'80% training players; held-out player scores split into ability reference and evaluation; at least 5 reference charts',
      'evaluation_records':int(test.sum()),'evaluated_players':len(np.unique(qp)),'near_target_records':int(near.sum()),
      'overall':{k:metrics(qy,v) for k,v in pred.items()},'near_target':{k:metrics(qy[near],v[near]) for k,v in pred.items()}}
    dump(ROOT/(slug+'-validation.json'),validation)
    print(json.dumps(validation,indent=2),flush=True)
    print('Fitting full-data ranking:',label,flush=True)
    b,aa=target_fit(fulltheta,fullmu,fulla,p,j,y,J,target)
    np.savez_compressed(ROOT/(slug+'-parameters.npz'),b=b,a=aa)
    achieved=np.bincount(j,weights=y,minlength=J).astype(int)
    nearby=np.bincount(j,weights=(abs(fulltheta[p]-b[j])<1),minlength=J).astype(int)
    order=np.argsort(b,kind='stable');ranking=[]
    for rank,k in enumerate(order,1):
        m=meta[k];provisional=n[k]<100 or min(achieved[k],n[k]-achieved[k])<5 or nearby[k]<30
        ranking.append({'rank':rank,'md5':m['md5'],'title':m['title'],'original_level':m['level'],
           'difficulty':float(b[k]),'observations':int(n[k]),'achieved':int(achieved[k]),'nearby_players':int(nearby[k]),
           'status':'provisional' if provisional else 'supported','total_plays':m['total_plays'],'total_players':m['total_players'],
           'plays_per_player':m['total_plays']/max(m['total_players'],1)})
    dump(ROOT/(slug+'-rankings.json'),ranking)
    print('Completed',label,'provisional',sum(r['status']=='provisional' for r in ranking),flush=True)
