from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/magda_roadmap_mpl')
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent.parent
out=ROOT/'figures';out.mkdir(exist_ok=True)
facts=json.loads((ROOT/'data/review_facts.json').read_text())
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':170})

z=np.linspace(0,1,101)
shape=z*z*(3-z)/2
fig,ax=plt.subplots(1,2,figsize=(9,3.5),constrained_layout=True)
ax[0].plot(z,shape,color='#137c88',lw=4,label='t = 1 mm')
ax[0].plot(z,shape,color='#dc853d',lw=2,ls='--',label='t = 4 mm (same curve)')
ax[0].set(xlabel='Position z / L',ylabel='Deflection w(z) / u',title='Same imposed tip displacement')
ax[0].legend(fontsize=8);ax[0].grid(alpha=.2)
ax[1].bar(['1 mm','4 mm'],[1,64],color=['#137c88','#dc853d'])
ax[1].set(ylabel='Required force / force at t = 1 mm',title='Same E, width, length and u')
for i,v in enumerate([1,64]):ax[1].text(i,v+1,str(v),ha='center')
ax[1].set_ylim(0,76)
fig.suptitle('Theory example: linear Euler-Bernoulli cantilever; not measured deformation or force',fontsize=10)
fig.savefig(out/'prescribed_displacement.png');plt.close(fig)

t=np.array(facts['displayed_sensitivity_at_z15']['thickness_mm'],dtype=float)
s=np.array(facts['displayed_sensitivity_at_z15']['sensitivity_magnitude_mT_per_mm'])
fig,ax=plt.subplots(1,2,figsize=(9,3.4),constrained_layout=True)
ax[0].bar(t,s,color='#137c88',width=.55)
ax[0].plot([0,4.3],[0,.097*4.3],'--',color='#9f6e43',label='Reference: S = 0.097 t')
ax[0].set(xlabel='Displayed thickness [mm]',ylabel='Sensitivity magnitude [mT/mm]',ylim=(0,.57),xticks=t)
ax[0].legend(fontsize=8)
for x,v in zip(t,s):ax[0].text(x,v+.01,f'{v:.3f}',ha='center',fontsize=10)
ax[1].bar(t,s/t,color='#137c88',width=.55)
ax[1].set(xlabel='Displayed thickness [mm]',ylabel='Sensitivity / thickness [mT/mm²]',ylim=(0,.15),xticks=t)
for x,v in zip(t,s/t):ax[1].text(x,v+.004,f'{v:.4f}',ha='center',fontsize=9)
fig.suptitle('Slide 5: z_s = 15 mm; displayed values, without supplied uncertainty estimates',fontsize=10)
fig.savefig(out/'four_thicknesses.png');plt.close(fig)
print('Created 2 figures: displayed data and a separately labelled theory example')
