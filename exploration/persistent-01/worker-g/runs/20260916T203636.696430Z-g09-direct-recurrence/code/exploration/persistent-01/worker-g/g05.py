from PIL import Image
from scipy.ndimage import label,find_objects
import numpy as np,pathlib,json,hashlib
O=pathlib.Path(__file__).parent;ROOT=O.parents[2];f=ROOT/'liber-primus/data/relikd/p7.jpg';a=np.array(Image.open(f).convert('RGB'));x0,y0,x1,y1=650,2750,1700,3250;mask=np.max(a[y0:y1,x0:x1],axis=2)<50;lab,n=label(mask);pts=[];components=[]
for i,s in enumerate(find_objects(lab),1):
 yy,xx=np.where(lab[s]==i)
 if len(xx)<200:continue
 x=xx+s[1].start+x0;y=yy+s[0].start+y0;pts.append([float(x.mean()),float(y.mean())]);components.append({'bounds':[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)],'pixels':len(xx),'center':pts[-1]})
def score(points):
 p=np.array(points);z=p[:,0]+1j*p[:,1];z-=z.mean();z=z[np.argsort(np.angle(z))];pent=[]
 for sign in [1,-1]:
  t=np.exp(sign*2j*np.pi*np.arange(len(z))/len(z));c=np.vdot(t,z)/np.vdot(t,t);pent.append(float(np.sqrt(np.mean(abs(z-c*t)**2)/np.mean(abs(z)**2))))
 A=np.column_stack([2*p[:,0],2*p[:,1],np.ones(len(p))]);b=(p*p).sum(axis=1);cx,cy,c=np.linalg.lstsq(A,b,rcond=None)[0];r=np.sqrt(c+cx*cx+cy*cy);dist=np.sqrt((p[:,0]-cx)**2+(p[:,1]-cy)**2)
 return {'pentagon_normalized_rms':min(pent),'circle_relative_rms':float(np.sqrt(np.mean((dist-r)**2))/r),'circle_center':[cx,cy],'radius':float(r)}
t=np.arange(5)*2*np.pi/5;control=np.column_stack([np.cos(t),np.sin(t)]);negative=control.copy();negative[0]*=2
assert score(control)['pentagon_normalized_rms']<1e-10
assert score(negative)['pentagon_normalized_rms']>.05
result={'input_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'roi':[x0,y0,x1,y1],'components':components,'geometry':score(pts) if len(pts)==5 else None,'positive':score(control),'negative':score(negative),'threshold':.05}
(O/'g05-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
