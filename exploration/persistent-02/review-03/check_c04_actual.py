"""C04 actual panel statistic/provenance review; controls not repeated."""
import pathlib,json,hashlib,math,random,numpy as np
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];F=R/'exploration/persistent-02/feedback';P=R/'exploration/persistent-02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 prior=json.loads((P/'review-02/runs/20260917T084743.898704Z-C04-independent/command.json').read_text());pins={x['path']:x['sha256'] for x in prior['sources_inputs'] if x.get('exists')}
 for path in ['exploration/persistent-02/feedback/invariant.py','exploration/persistent-02/feedback/C04-PREREG.md']:assert sha(R/path)==pins[path]
 meta=json.loads((F/'C04/actual.json').read_text());assert meta['ks']==list(range(2,35)) and meta['panels']==200 and meta['seedbase']==2026200000
 with np.load(F/'C04/actual.npz') as raw:a={k:raw[k] for k in raw.files}
 c=json.loads((P/'section/section-packet.json').read_text())['body']['runes'];assert len(c)==716 and c==a['cipher'][0].tolist();nums=np.zeros((200,33),dtype=np.int64);dens=[]
 for j in range(200):
  if j==0:cc=c
  else:
   rng=random.Random(2026200000+j-1);cc=[c[0]]
   for i in range(1,len(c)):cc.append(cc[-1] if c[i]==c[i-1] else rng.choice([v for v in range(29) if v!=cc[-1]]))
  assert cc==a['cipher'][j].tolist()
  for col,k in enumerate(range(2,35)):
   q=cc[:k]+[(cc[k]-sum(cc[:k]))%29]
   for i in range(k+1,len(cc)):q.append((q[i-k-1]+cc[i]-cc[i-1])%29)
   h=np.array([np.bincount(q[t::k+1],minlength=29) for t in range(k+1)]);num=int(np.sum(h*(h-1)));nn=h.sum(axis=1);den=int(np.sum(nn*(nn-1)));nums[j,col]=num
   assert np.array_equal(h,a['histograms'][j,col,:k+1]);assert den==a['denominators'][col]
 assert np.array_equal(nums,a['numerators']);frac=nums/a['denominators'];z=np.empty_like(frac)
 for col in range(33):
  values=frac[:,col].tolist();mu=math.fsum(values)/200;sd=math.sqrt(math.fsum((x-mu)**2 for x in values)/200);z[:,col]=[(x-mu)/sd for x in values]
 mx=z.max(axis=1);exceed=sum(x>=mx[0] for x in mx[1:]);rank=(1+exceed)/200;winner=2+int(z[0].argmax())
 assert np.max(np.abs(z-a['z']))<1e-12 and np.max(np.abs(mx-a['family_maximum']))<1e-12;assert rank==meta['rank']==.89 and winner==meta['selected_k']==4
 assert np.max(np.abs(z[0]-meta['actual_standardized']))<1e-12;assert np.array_equal(frac[0],meta['actual_collision_fractions'])
 out=dict(passed=True,unchanged_reviewed_algorithm_and_prereg=True,panels=200,periods=33,exceedances=int(exceed),rank=rank,selected_k=winner,actual_maximum=float(mx[0]),actual_metadata_sha256=sha(F/'C04/actual.json'),section_body_sha256=hashlib.sha256(bytes(c)).hexdigest(),scope='Complete actual200panelmatrix independently reconstructed; prior controls not rerun. Conditional family rank, not global discovery probability.')
 (O/'c04-actual-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
