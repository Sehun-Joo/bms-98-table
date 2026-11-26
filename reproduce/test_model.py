import numpy as np
from scipy.stats import spearmanr
from build_table import latent,target_fit
rng=np.random.default_rng(45)
P,J=400,25
true_theta=rng.normal(size=P)
mu=np.linspace(4.2,2.3,J)
a=rng.uniform(.4,.8,J)
pp,jj=np.meshgrid(np.arange(P),np.arange(J),indexing='ij')
# Strong players disproportionately play harder charts.
keep=rng.random(pp.shape)<1/(1+np.exp(-(true_theta[:,None]+2-jj/18)))
p,j=pp[keep],jj[keep]
t=mu[j]+a[j]*true_theta[p]+rng.normal(0,.25,len(p))
theta,mm,aa,ss,it=latent(p,j,t,P,J,variable=True)
b=(-np.log(.02)-mm)/aa
truth=(-np.log(.02)-mu)/a
cor=spearmanr(b,truth).statistic
assert cor>.95,cor
y=(t>=-np.log(.02)).astype(float)
b98,a98=target_fit(theta,mm,aa,p,j,y,J)
cor98=spearmanr(b98,truth).statistic
assert cor98>.95,cor98
assert np.isfinite(b98).all() and (a98>0).all()
groups=np.array_split(np.arange(1035),round(1035/12))
assert len(groups)==86 and all(10<=len(g)<=15 for g in groups)
print('PASS: biased-participation synthetic ranking recovery',cor,cor98)
print('PASS: 1035 charts grouped into 86 folders of 12 or 13')
