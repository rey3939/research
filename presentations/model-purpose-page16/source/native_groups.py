@contextmanager
def group(name):
 global cur
 prev=cur;g=cur.shapes.add_group_shape();g.name=name;cur=g
 try:yield g
 finally:g.shapes._recalculate_extents();cur=prev

def particle(x,y,a=0,size=8):
 circle(x,y,size,'teal');r=21;t=math.radians(a)
 arrow(x-5*math.cos(t),y-5*math.sin(t),x+r*math.cos(t),y+r*math.sin(t),'orange',3,8)

def material(x,y,w,h,angles,offsets=None):
 rect(x,y,w,h,'cyan2',line='teal',r=12,lw=2)
 positions=offsets or [(.25,.3),(.69,.37),(.43,.73)]
 for (u,v),a in zip(positions,angles):particle(x+u*w,y+v*h,a,6)

def bent_strip(x,y,w,t,color='gray'):
 # Both strips have the same centerline curvature; only thickness changes.
 pts=[];r=w*.95
 for i in range(33):
  th=-.6+1.2*i/32
  pts.append((x+w/2+r*math.sin(th),y+r*(1-math.cos(th))))
 # A horizontal cylindrical bend represented by a native freeform outline.
 normal=[]
 for i in range(len(pts)):
  p0=pts[max(i-1,0)];p1=pts[min(i+1,len(pts)-1)];dx=p1[0]-p0[0];dy=p1[1]-p0[1];ll=math.hypot(dx,dy);normal.append((-dy/ll,dx/ll))
 outline=[(p[0]+n[0]*t/2,p[1]+n[1]*t/2) for p,n in zip(pts,normal)]
 outline += [(p[0]-n[0]*t/2,p[1]-n[1]*t/2) for p,n in reversed(list(zip(pts,normal)))]
 sh=poly(outline,fill='cyan2',line='teal',lw=2,closed=True);sh.name='曲げた試料の輪郭（同じ中心線曲率）'
 # Centerline is drawn as an editable dashed freeform.
 for k in range(0,31,4):poly(pts[k:k+3],line='muted',lw=1.5)
 return pts
