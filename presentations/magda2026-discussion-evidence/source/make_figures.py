from pathlib import Path
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
ROOT=Path(__file__).resolve().parent.parent;out=ROOT/'figures';out.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':170})
fig,ax=plt.subplots(1,2,figsize=(9,3.7),constrained_layout=True)
t=np.array([1.,4.]);S=np.array([.097,.478]);ax[0].plot([0,4.3],[0,.097*4.3],'--',color='#7b8992',label='S = 0.097 t: proportional hypothesis');ax[0].scatter(t,S,s=55,color='#067f8b',zorder=4,label='Values shown on supplied slide')
for x,y in zip(t,S):ax[0].annotate(f'{y:.3f}',(x,y),xytext=(8,8),textcoords='offset points')
ax[0].set(xlabel='Thickness t [mm]',ylabel='Sensitivity magnitude [mT/mm]',xlim=(0,4.5),ylim=(0,.56));ax[0].legend(fontsize=7.5,loc='upper left');ax[0].grid(alpha=.2)
ax[1].bar(['1 mm','4 mm'],S/t,color=['#a3c5cc','#067f8b']);ax[1].set_ylabel('Sensitivity / thickness [mT/mm²]');ax[1].set_ylim(0,.16)
for i,y in enumerate(S/t):ax[1].text(i,y+.004,f'{y:.4f}',ha='center')
ax[1].text(.04,.92,'Difference: +23.2%\nUncertainty / replicate data not provided',transform=ax[1].transAxes,fontsize=9)
fig.savefig(out/'thickness_normalization.png');plt.close(fig)
# Earlier specimen conditions, presented as a mechanics example rather than measured shape.
L=40.;u=np.linspace(0,4,100);fig,ax=plt.subplots(1,2,figsize=(9,3.8),constrained_layout=True)
for z,co in [(15,'#187e8b'),(35,'#df813c')]:
 w=u*z*z*(3*L-z)/(2*L**3);theta=3*u*(2*L*z-z*z)/(2*L**3);ax[0].plot(u,w,color=co,label=f'z = {z} mm');ax[1].plot(u,np.degrees(theta),color=co,label=f'z = {z} mm')
ax[0].set(xlabel='Tip displacement u [mm]',ylabel='Local deflection w(z) [mm]');ax[1].set(xlabel='Tip displacement u [mm]',ylabel='Local angle theta(z) [deg]')
for aa in ax:aa.grid(alpha=.2);aa.legend()
fig.suptitle('Euler-Bernoulli cantilever example: L = 40 mm; not a measured deformation field',fontsize=10);fig.savefig(out/'beam_kinematics.png');plt.close(fig)
fig,ax=plt.subplots(1,2,figsize=(9,4),constrained_layout=True)
for aa in ax:aa.set_xlim(-1,8);aa.set_ylim(-4.8,5.8);aa.axis('off')
for x,h in [(0,1),(4.5,4)]:
 ax[0].add_patch(Rectangle((x,-h),2.8,h,facecolor='#bcd7df',edgecolor='#227b8a'));ax[0].plot([x,x+2.8],[-h/2,-h/2],'--',color='#c6673b');ax[0].scatter([x+1.4],[3],s=90,color='#243f55',marker='s');ax[0].text(x+1.4,3.5,'sensor',ha='center',fontsize=9);ax[0].annotate('',(x+1.4,2.8),(x+1.4,.1),arrowprops=dict(arrowstyle='<->',color='#243f55'));ax[0].text(x+1.6,1.2,'d',fontsize=12);ax[0].text(x+1.4,-h-.65,f't = {h} mm',ha='center',fontsize=9)
ax[0].set_title('Current protocol: fixed surface gap d');ax[0].text(-.3,-4.7,'Center distances: d + 0.5 and d + 2.0 mm',fontsize=9)
for x,h in [(0,1),(4.5,4)]:
 ax[1].add_patch(Rectangle((x,-h/2),2.8,h,facecolor='#bcd7df',edgecolor='#227b8a'));ax[1].plot([x,x+2.8],[0,0],'--',color='#c6673b');ax[1].scatter([x+1.4],[4],s=90,color='#243f55',marker='s');ax[1].annotate('',(x+1.4,3.8),(x+1.4,.1),arrowprops=dict(arrowstyle='<->',color='#243f55'));ax[1].text(x+1.6,2.5,'R',fontsize=12);ax[1].text(x+1.4,-h/2-.65,f't = {h} mm',ha='center',fontsize=9)
ax[1].set_title('Control: fixed center distance R');ax[1].text(-.3,-4.7,'For t = 1 mm, increase surface gap by 1.5 mm\nto match the existing t = 4 mm center distance.',fontsize=9)
fig.savefig(out/'surface_vs_center_distance.png');plt.close(fig)
print('Saved 3 analytical figures')
