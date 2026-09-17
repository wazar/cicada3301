import p10 as p
import pathlib,inspect,json,collections,subprocess,io,numpy as np,sys
from PIL import Image
R=p.R.parent/'P13'
def dump(n,x):(R/(n+'.json')).write_text(json.dumps(x,indent=2)+'\n')
def table_summary(tables):
 out={}
 for (cl,tid),tab in tables.items():
  entries=sorted(tab.items());bits=[sum(n==size for (n,code),v in entries) for size in range(1,17)];out[f'{cl}:{tid}']=dict(bits=bits,values=[v for k,v in entries])
 return out
src=inspect.getsource(p.parse);src=src.replace('def parse(d):',"def parse13(d):\n symbolcounts={}\n def rec(br,cl,tid):\n  v=br.symbol(tables[cl,tid]);symbolcounts.setdefault(f'{cl}:{tid}',[0]*256)[v]+=1;return v")
assert src.count("br.symbol(tables[0,s['dc']])")==1 and src.count("br.symbol(tables[1,s['ac']])")==1
src=src.replace("br.symbol(tables[0,s['dc']])","rec(br,0,s['dc'])").replace("br.symbol(tables[1,s['ac']])","rec(br,1,s['ac'])").replace('return meta,bytes(raw),bytes(unstuffed),arrays',"meta['symbol_histograms']=symbolcounts;meta['huffman_tables']=table_summary(tables)\n return meta,bytes(raw),bytes(unstuffed),arrays")
ns=vars(p).copy();ns['table_summary']=table_summary;exec(compile(src,'<instrumented-p10-parser>','exec'),ns);parse13=ns['parse13']
def optimize(hist):
 assert len(hist)==256 and all(x>=0 for x in hist) and sum(hist)<1000000000
 active={i:int(x) for i,x in enumerate(hist) if x};active[256]=1;members={i:[i] for i in active};length={i:0 for i in active};ties=[]
 while len(active)>1:
  ordered=sorted(active,key=lambda x:(active[x],-x));a,b=ordered[:2]
  if sum(v==active[a] for v in active.values())>1 or sum(v==active[b] for v in active.values())>1:ties.append(dict(chosen=[a,b],frequency=[active[a],active[b]],equal_first=[k for k,v in active.items() if v==active[a]],equal_second=[k for k,v in active.items() if v==active[b]]))
  active[a]+=active.pop(b);members[a]+=members.pop(b)
  for symbol in members[a]:length[symbol]+=1
 bits=[0]*33
 for n in length.values():assert n<=32;bits[n]+=1
 original=bits.copy();adjustments=[]
 for i in range(32,16,-1):
  while bits[i]>0:
   j=i-2
   while bits[j]==0:j-=1
   bits[i]-=2;bits[i-1]+=1;bits[j+1]+=2;bits[j]-=1;adjustments.append([i,j])
 largest=max(i for i,n in enumerate(bits) if n);bits[largest]-=1;values=sorted([s for s in length if s!=256],key=lambda s:(length[s],s));return dict(bits=bits[1:17],values=values),dict(ties=ties,original_lengths={str(k):v for k,v in length.items()},length_adjustments=adjustments,original_length_counts=original)
def encoded(table):return bytes(table['bits']+table['values'])
def native(hist,label):
 f=R/(label+'-hist.txt');f.write_text(' '.join(map(str,hist))+'\n');o=R/(label+'-native.bin');cmd=[str(R/'helper'),'hist',str(f),str(o)];r=subprocess.run(cmd,capture_output=True);(R/(label+'-native.stderr')).write_bytes(r.stderr);assert r.returncode==0;return o.read_bytes()
def compare(meta,label):
 rows=[]
 for key,actual in sorted(meta['huffman_tables'].items()):
  hist=meta['symbol_histograms'].get(key,[0]*256);assert sum(hist)>0,'unused table outside frozen comparison';pred,trace=optimize(hist);nb=native(hist,label+'-'+key.replace(':','-'));assert nb==encoded(pred)
  def cost(t):
   pos=0;v=0
   for length,n in enumerate(t['bits'],1):
    for symbol in t['values'][pos:pos+n]:v+=hist[symbol]*length
    pos+=n
   return v
  rows.append(dict(key=key,histogram=hist,actual=actual,predicted=pred,exact_match=actual==pred,count_bytes_match=actual['bits']==pred['bits'],symbol_order_match=actual['values']==pred['values'],actual_weighted_bits=cost(actual),predicted_weighted_bits=cost(pred),trace=trace))
 return rows
def pixels(data):
 with Image.open(io.BytesIO(data)) as im:return im.mode,im.size,im.tobytes()
def trans(mode,source,dest,label):
 cmd=[str(R/'helper'),mode,str(source),str(dest)];r=subprocess.run(cmd,capture_output=True);(R/(label+'.stderr')).write_bytes(r.stderr);dump(label+'-command',dict(command=cmd,exit_code=r.returncode));assert r.returncode==0;return r.stderr

def controls():
 p.gate();hs=[]
 for name,hist in [('single',[0]*7+[100]+[0]*248),('ties',[1]*128+[0]*128),('skew',[1000000,2,3,4]+[0]*252)]:hs.append((name,hist))
 fib=[1,1]
 while len(fib)<34:fib.append(fib[-1]+fib[-2])
 hs.append(('lengthlimit',fib+[0]*(256-len(fib))));checks=[]
 for name,hist in hs:
  tab,tr=optimize(hist);assert native(hist,'histcontrol-'+name)==encoded(tab);checks.append(dict(name=name,histogram=hist,table=tab,trace=tr))
 assert checks[-1]['trace']['length_adjustments']
 images=[]
 for ix in [0,8]:
  source=p.R/f'control-{ix}-clean.jpg';ordinary=R/f'control-{ix}-optimized.jpg';modified=R/f'control-{ix}-permuted.jpg';trans('opt',source,ordinary,f'control-{ix}-opt');m,_,_,a=parse13(ordinary.read_bytes());baseline=compare(m,f'control-{ix}-base');assert all(x['exact_match'] for x in baseline);change=json.loads(trans('perm',ordinary,modified,f'control-{ix}-perm'));mm,_,_,aa=parse13(modified.read_bytes());covert=compare(mm,f'control-{ix}-changed');assert sum(not x['exact_match'] for x in covert)==1;assert all(x['count_bytes_match'] for x in covert);assert all(x['actual_weighted_bits']==x['predicted_weighted_bits'] for x in covert);assert m['symbol_histograms']==mm['symbol_histograms'];assert all(np.array_equal(a[k],aa[k]) for k in a);assert pixels(ordinary.read_bytes())==pixels(modified.read_bytes());images.append(dict(index=ix,change=change,baseline=baseline,permuted=covert,ordinary_sha256=p.sha(ordinary.read_bytes()),modified_sha256=p.sha(modified.read_bytes()),pixel_sha256=p.sha(pixels(ordinary.read_bytes())[2]),coefficient_hashes=m['coefficient_sha256']))
 dump('controls',dict(status='PASS',histograms=checks,images=images));print('CONTROL PASS',len(checks),len(images))
def actual():
 p.gate();assert json.loads((R/'controls.json').read_text())['status']=='PASS';out=[]
 for page in [0,1]:
  f=p.ROOT/f'liber-primus/data/relikd/p{page}.jpg';data=f.read_bytes();previous=json.loads((p.R/f'actual-{page}.json').read_text());assert p.sha(data)==previous['sha256'];meta,_,_,arrays=parse13(data);assert meta['coefficient_sha256']==previous['metadata']['coefficient_sha256'];rows=compare(meta,f'actual-{page}');dump('actual-'+str(page),dict(page=page,path=str(f.relative_to(p.ROOT)),sha256=p.sha(data),metadata=meta,tables=rows));out.append(dict(page=page,tables=len(rows),exact_matches=sum(x['exact_match'] for x in rows),rows=[dict(key=x['key'],symbols=sum(x['histogram']),exact_match=x['exact_match'],ties=len(x['trace']['ties']),length_adjustments=len(x['trace']['length_adjustments']),actual_weighted_bits=x['actual_weighted_bits'],predicted_weighted_bits=x['predicted_weighted_bits']) for x in rows]));print(json.dumps(out[-1]),flush=True)
 dump('summary',out)
if __name__=='__main__':{'controls':controls,'actual':actual}[sys.argv[1]]()
