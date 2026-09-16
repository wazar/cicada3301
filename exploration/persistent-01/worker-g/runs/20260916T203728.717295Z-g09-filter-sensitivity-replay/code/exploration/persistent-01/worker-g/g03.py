import pathlib,json,numpy as np
O=pathlib.Path(__file__).parent;ROOT=O.parents[2];D=json.loads((ROOT/'audit/parallel-01/inputs/dataset.json').read_text());pages={p['original_page']:p for p in D['pages'] if p['original_page'] in [3,7]};rng=np.random.default_rng(30703)
masks={3:list(range(16))+list(range(119,122)),7:list(range(194,208))}
def stat(v,idx):
 a=np.bincount(v[idx],minlength=29);b=np.bincount(v,minlength=29)-a;t=a+b;n=len(v);e=t*len(idx)/n;f=t-e
 return float(2*(np.sum(a[a>0]*np.log(a[a>0]/e[a>0]))+np.sum(b[b>0]*np.log(b[b>0]/f[b>0]))))
real=0;pos=0;null=np.zeros(10000);pn=np.zeros(10000);records={}
for p,d in pages.items():
 v=np.array(d['indices']);idx=np.array(masks[p]);plant=v.copy();plant[idx]=0
 real+=stat(v,idx);pos+=stat(plant,idx)
 for j,s in enumerate(rng.integers(len(v),size=10000)):
  shifted=(idx+s)%len(v);null[j]+=stat(v,shifted);pn[j]+=stat(plant,shifted)
 records[p]={'red_offsets':idx.tolist(),'red_indices':v[idx].tolist(),'red_source_char_positions':[d['source_char_positions'][i]for i in idx],'black_indices':[int(x) for i,x in enumerate(v) if i not in set(idx)],'statistic':stat(v,idx)}
result={'seed':30703,'pages':records,'statistic':real,'upper_tail':float((1+sum(null>=real))/10001),'null_statistics':null.tolist(),'positive_statistic':pos,'positive_upper_tail':float((1+sum(pn>=pos))/10001),'positive_null':pn.tolist()}
assert result['positive_upper_tail']<=.01
(O/'g03-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['null_statistics','positive_null','pages']},indent=2))
