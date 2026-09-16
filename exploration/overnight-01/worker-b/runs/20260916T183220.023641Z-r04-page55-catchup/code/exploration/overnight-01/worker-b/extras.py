"""Measured search controls, selected literal-F numeric followup, candidate export."""
import argparse,gzip,hashlib,json,pathlib,time
import numpy as np
from search import ROOT,OWNER,ABC,TOK,Score,seqs,fit,dump,record
def beam(c,key,sign,score,width=256):
 # Incremental exact Latin quadgram score; path pruning is heuristic, no truth use.
 states=[(0.,'',[],[],0)]
 for i,ch in enumerate(c):
  children=[]
  for total,t,p,path,used in states:
   for val,literal in [((int(ch)+sign*int(key[used]))%29,False)]+([(0,True)] if ch==0 else []):
    word=TOK[val];new=t+word;v=total+sum(score.d.get(new[j-3:j+1],score.floor) for j in range(max(3,len(t)),len(new)));children.append((v,new,p+[val],path+[i] if literal else path,used+(not literal)))
  children.sort(key=lambda x:x[0]/max(1,len(x[1])-3),reverse=True);states=children[:width]
 out=[]
 for total,t,p,path,used in states[:16]:
  # Exact declared-path re-encryption is a hard gate.
  j=0
  for i,ch in enumerate(c):
   if i in path:assert p[i]==ch==0
   else:assert (p[i]-sign*int(key[j]))%29==ch;j+=1
  out.append({'score':score.exact(p),'rune_indices':p,'transliteration':t,'literal_positions':path,'consumed':used})
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['controls','f','export']);ap.add_argument('--seconds',type=int,default=820);a=ap.parse_args();score=Score();seq=seqs(15000);cfg=json.loads((ROOT/'exploration/overnight-01/config.json').read_text());pages=[p for p in json.loads((ROOT/'audit/parallel-01/inputs/dataset.json').read_text())['pages'] if p['original_page']<=55 and p['original_page'] not in cfg['reserved_original_pages']];plain=np.array([ABC.index(x) for x in (ROOT/'audit/parallel-01/reference/sources/solved_0_welcome.txt').read_text() if x in ABC]);start=time.monotonic()
 if a.mode=='controls':
  results=[]
  for period in [1,3,8,16,32]:
   rng=np.random.default_rng(440000+period);key=rng.integers(0,29,period);c=(plain+key[np.arange(len(plain))%period])%29;split=3*len(c)//4
   for corrupt in [False,True]:
    source=(c+rng.integers(1,29,len(c)))%29 if corrupt else c;best,rows,ev=fit(source[:split],period,score,330104);p=(source-best[1][np.arange(len(c))%period])%29;truth_score=float(score.batch(plain[:split])[0]);results.append({'period':period,'corrupted':corrupt,'evaluations':ev,'planted_key':key.tolist(),'selected_key':best[1].tolist(),'truth_objective':truth_score,'truth_rank_among_final_restarts_plus_truth':1+sum(r['fit_score']>truth_score for r in rows),'truth_found_in_top4_restarts':any(r['key']==key.tolist() for r in rows),'key_errors':int(np.sum(best[1]!=key)),'train_rune_errors':int(np.sum(p[:split]!=plain[:split])),'check_rune_errors':int(np.sum(p[split:]!=plain[split:])),'selected_train':score.exact(p[:split]),'selected_check':score.exact(p[split:]),'restarts':rows})
  dump(OWNER/'r04'/'controls.json',results)
  c=(plain+seq['prime_minus_one'][37:37+len(plain)])%29;literal=[i for i,v in enumerate(plain) if v==0][:3];j=0
  for i,v in enumerate(plain):
   if i in literal:c[i]=0
   else:c[i]=(v+seq['prime_minus_one'][37+j])%29;j+=1
  choices=beam(c,seq['prime_minus_one'][37:],-1,score);dump(OWNER/'r03'/'f-control.json',{'literal':literal,'choices':choices,'truth_survives_top16':any(x['rune_indices']==plain.tolist() for x in choices),'top_rune_errors':sum(a!=b for a,b in zip(choices[0]['rune_indices'],plain)),'width':256})
 elif a.mode=='f':
  lane=OWNER/'r03-f';lane.mkdir(exist_ok=True);statepath=lane/'checkpoint.json';state=json.loads(statepath.read_text()) if statepath.exists() else {'cursor':0,'trials':0,'top':[]};cells=[(p,f,off,sign) for p in pages for f in ['primes','prime_minus_one','fibonacci'] for off in [0,37] for sign in [-1,1]]
  for idx in range(state['cursor'],len(cells)):
   page,f,off,sign=cells[idx];choices=beam(page['indices'],seq[f][off:],sign,score);meta={'id':f'{page["original_page"]}:{f}:{off}:{sign}:F256','page':page['original_page'],'family':f,'offset':off,'sign':sign,'reset':'page','model':'literal-F nonconsumption, beam256 exact prefix Latin score; top16 retained','status':'UNREVIEWED','choices':choices};dump(lane/f'cell-{idx:04}.json',meta);top=state['top'];top.append({**meta,**choices[0]});top.sort(key=lambda r:r['score'],reverse=True);state.update(cursor=idx+1,trials=idx+1,top=top[:20]);dump(statepath,state);print(json.dumps({'cursor':idx+1,'total':len(cells),'best':state['top'][0]['score']}),flush=True)
   if time.monotonic()-start>a.seconds:break
 else:
  pageby={p['original_page']:p for p in pages};rows=[]
  for path in (OWNER/'r03').glob('cell-*.json.gz'):
   with gzip.open(path,'rt') as f:rows+=json.load(f)
  rows.sort(key=lambda r:r[1],reverse=True);top=[];seen=set()
  for ident,value in rows:
   page,reset,f,sign,off=ident.split(':');page=int(page);sign=int(sign);off=int(off);entry=pageby[page];c=np.array(entry['indices']);base=0 if reset=='page' else entry['stream_start'];p=(c+sign*seq[f][base+off:base+off+len(c)])%29;sig=(page,tuple(p))
   if sig in seen:continue
   seen.add(sig);top.append(record(c,p,{'id':ident,'page':page,'positions':[0,len(c)],'family':f,'sign':sign,'offset':off,'reset':reset,'key_start':base+off,'model':'rigid','free_parameters':'six-family,128-offset,2-sign,2-reset selection'},score))
   if len(top)==20:break
  dump(OWNER/'r03'/'top_candidates.json',top)
  rows=[]
  for path in (OWNER/'r04').glob('cell-*.json.gz'):
   with gzip.open(path,'rt') as f:rows.extend(r for r in json.load(f) if not r['control'])
  for r in rows:r.update(positions=[0,len(r['rune_indices'])],free_parameters=f'{r["period"]} mod29 key runes; period selected among1..32; four restarts; <=5 sweeps',validation_limit='Each key frozen on training; ranking candidates by continuation is exploratory selection on that continuation, not unseen evidence')
  dump(OWNER/'r04'/'top_candidates.json',sorted(rows,key=lambda r:r['train_score'],reverse=True)[:20]);dump(OWNER/'r04'/'top_continuation_candidates.json',sorted(rows,key=lambda r:r['continuation_score'],reverse=True)[:20])
 print(json.dumps({'mode':a.mode,'seconds':time.monotonic()-start}))
if __name__=='__main__':main()
