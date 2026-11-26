"""Grouped-player validation: fit charts on 80% of players; use half the other
players' scores ONLY to infer skill, and evaluate on their remaining scores."""
import json,math
from pathlib import Path
import numpy as np
from scipy.special import expit,ndtr
from scipy.optimize import minimize
from build_table import latent,target_fit,metrics,dump,ROOT

rows=np.load(ROOT/'observations.npz')['rows']
ids,cnt=np.unique(rows[:,0],return_counts=True)
rows=rows[np.isin(rows[:,0],ids[cnt>=10])]
ids,p=np.unique(rows[:,0],return_inverse=True); P=len(ids); J=1035
j=rows[:,1]; y=(100*rows[:,2]>=98*rows[:,3]).astype(float)
t=-np.log((rows[:,3]-rows[:,2]+.5)/(rows[:,3]+.5))
rng=np.random.default_rng(20261125)
trainplayers=rng.random(P)<.8; train=trainplayers[p]
reference=(~train)&(rng.random(len(p))<.5); test=(~train)&(~reference)
# Reindex training players so empty held-out accounts do not change the scale.
_,pt=np.unique(p[train],return_inverse=True)
cache=ROOT/'review-model-parameters.npz'
if cache.exists():
    c=np.load(cache);theta,mu,a,sigma,b,aa=[c[k] for k in ['theta','mu','a','sigma','b','aa']]
else:
    theta,mu,a,sigma,it=latent(pt,j[train],t[train],len(np.unique(pt)),J,variable=True)
    b,aa=target_fit(theta,mu,a,pt,j[train],y[train],J)
    np.savez_compressed(cache,theta=theta,mu=mu,a=a,sigma=sigma,b=b,aa=aa)
# Stronger simple comparator: shared slope on the SAME ability, exact 98% outcome.
b0=(-math.log(.02)-mu)/a; x=theta[pt]; jt=j[train]; yt=y[train]
def fg(z):
    bb=z[:J]; loga=z[J]/math.sqrt(J);slope=np.exp(loga); eta=slope*(x-bb[jt]); e=expit(eta)-yt
    loss=np.logaddexp(0,eta).sum()-np.dot(yt,eta)+.5*np.sum((bb-b0)**2)
    loss+=.5*((loga-math.log(2))/.5)**2
    grad=np.r_[np.bincount(jt,weights=-slope*e,minlength=J)+(bb-b0),(np.dot(e,eta)+(loga-math.log(2))/.25)/math.sqrt(J)]
    return loss,grad
fit=minimize(fg,np.r_[b0,math.log(2)*math.sqrt(J)],jac=True,method='L-BFGS-B',bounds=[(-15,50)]*J+[(math.log(.1)*math.sqrt(J),math.log(12)*math.sqrt(J))],options={'maxiter':700,'ftol':1e-9})
assert fit.success,fit.message
print('Shared-slope threshold fitted',flush=True)
# Infer held-out players without using any evaluation score or renormalizing the
# training skill scale. Same ridge/Huber rules as the original ALS player update.
pr,jr,tr=p[reference],j[reference],t[reference]
w=np.ones(len(pr)); skill=np.zeros(P)
for it in range(40):
    old=skill.copy()
    skill=np.bincount(pr,weights=w*a[jr]*(tr-mu[jr]),minlength=P)/(np.bincount(pr,weights=w*a[jr]**2,minlength=P)+.5)
    resid=tr-mu[jr]-a[jr]*skill[pr];w=np.minimum(1,.65/np.maximum(abs(resid),1e-8))
    if np.max(abs(old-skill))<1e-5:break
refcounts=np.bincount(pr,minlength=P)
test &= refcounts[p]>=5
qj=j[test]; qp=p[test]; qy=y[test]
pred={
 'chart_score_curve':ndtr((mu[qj]+a[qj]*skill[qp]+math.log(.02))/sigma[qj]),
 'shared_slope_98':expit(np.exp(fit.x[J]/math.sqrt(J))*(skill[qp]-fit.x[:J][qj])),
 'chart_slope_98':expit(aa[qj]*(skill[qp]-b[qj]))}
n=np.bincount(j[train],minlength=J); win=np.bincount(j[train],weights=y[train],minlength=J)
pred['raw_rate']=((win+.5)/(n+1))[qj]
near=abs(skill[qp]-b0[qj])<1
report={'design':'80% training players; held-out player reference/evaluation score split 50/50; >=5 reference charts',
 'seed':20261125,'training_players':int(trainplayers.sum()),'evaluated_players':len(np.unique(qp)),
 'evaluation_records':int(test.sum()),'near_target_records':int(near.sum()),
 'overall':{k:metrics(qy,v) for k,v in pred.items()},
 'near_target':{k:metrics(qy[near],v[near]) for k,v in pred.items()}}
# Paired differences with player-cluster bootstrap for near-target observations.
names=['chart_score_curve','shared_slope_98']
pn=qp[near];yn=qy[near]
ll=lambda z:-(yn*np.log(np.clip(z,1e-8,1-1e-8))+(1-yn)*np.log1p(-np.clip(z,1e-8,1-1e-8)))
base=ll(pred['chart_slope_98'][near]); unique=np.unique(pn); counts=np.bincount(pn,minlength=P)[unique]
report['paired_player_bootstrap']={}
for k in names:
    delta=base-ll(pred[k][near]); sums=np.bincount(pn,weights=delta,minlength=P)[unique]
    draws=[]
    for z in range(1000):
        sample=rng.integers(0,len(unique),len(unique));draws.append(float(sums[sample].sum()/counts[sample].sum()))
    report['paired_player_bootstrap'][k]={'target_minus_comparator_log_loss':float(delta.mean()),'interval95':np.quantile(draws,[.025,.975]).tolist(),'interpretation':'negative favors existing chart-slope 98% model'}
meta=json.loads((ROOT/'metadata.json').read_text(encoding='utf-8'))
plays=np.array([r['total_plays']/max(r['total_players'],1) for r in meta])
cuts=np.quantile(plays,[0,.25,.5,.75,1]);report['practice_proxy_quartiles']=[]
for k in range(4):
    mask=near&(plays[qj]>=cuts[k])&((plays[qj]<cuts[k+1]) if k<3 else (plays[qj]<=cuts[k+1]))
    report['practice_proxy_quartiles'].append({'range':cuts[k:k+2].tolist(),'n':int(mask.sum()),'metrics':metrics(qy[mask],pred['chart_slope_98'][mask])})
dump(ROOT/'model-review-validation.json',report)
print(json.dumps(report,indent=2),flush=True)
