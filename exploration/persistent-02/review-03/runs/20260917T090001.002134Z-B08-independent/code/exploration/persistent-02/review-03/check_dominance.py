"""Independent token-history/state reconstruction of B08; no suffix sweep."""
import pathlib,sys,json,gzip,hashlib,math,re,itertools
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];D=R/'exploration/persistent-02/decoder';sys.path.insert(0,str(D))
from compare import LM
from complementary import LM as OtherLM,keyword_to_indices
TOK='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split()+['BOUNDARY']
def dump(n,x):(O/n).write_text(json.dumps(x,indent=2)+'\n')
def weight(lm,ctx,x):
 v=(lm.c[0][(x,)]+.5)/(lm.t[0][()]+15)
 for n,alpha in [(1,8),(2,5)]:s=ctx[-n:];v=(lm.c[n][s+(x,)]+alpha*v)/(lm.t[n][s]+alpha)
 return math.log(v)
def trace(c,key,sign,periodic,ends,lit,lm,start=0,ctx=(29,29)):
 u=start;tokens=list(ctx);score=0.;out=[]
 for i,cipher in enumerate(c):
  before=[u%len(key) if periodic else u,*tokens[-2:]];literal=i in lit;assert not literal or cipher==0;assert literal or periodic or u<len(key)
  p=0 if literal else (cipher+sign*key[u%len(key)])%29;contrib=[]
  for x in ([p,29] if i in ends else [p]):
   s=tuple(tokens[-2:]);w=weight(lm,s,x);contrib.append(dict(context=list(s),emitted=x,weight=w));tokens.append(x)
  local=sum(x['weight'] for x in contrib);score+=local;u+=not literal
  out.append(dict(i=i,cipher=cipher,literal=literal,emitted=p,before=before,after=[u%len(key) if periodic else u,*tokens[-2:]],consumed=u-start,local_weight=local,total=score,contributions=contrib))
 return out
def main():
 frozen=json.loads((D/'fresh-controls.json').read_text());ext={c['id']:c for c in json.loads((D/'continuation-inputs.json').read_text())['cases']};claim=json.loads((D/'dominance.json').read_text());tables=json.loads((D/'dominance-source-tables.json').read_text());results=[]
 # Reconstruct source rune/word coordinates directly from the frozen source body.
 coord={}
 for name in ['shelley','mill']:
  src=next(s for s in frozen['sources'] if s['id']==name);path=R/src['path'];assert hashlib.sha256(path.read_bytes()).hexdigest()==src['sha256'];raw=path.read_text();lo,hi=src['body_char_span'];body=raw[lo:hi];exclusions=[(m.start(),m.end()) for m in re.finditer(r'\{[^}]*\}',body)];flat=[];spans=[]
  for m in re.finditer(r"[A-Za-z]+(?:['’][A-Za-z]+)*",body):
   if any(a<=m.start()<b for a,b in exclusions):continue
   runes=keyword_to_indices(re.sub("['’]",'',m.group()));flat+=runes;spans.extend([[lo+m.start(),lo+m.end()]]*len(runes))
  coord[name]=(raw,flat,spans)
 for model,lm in [('p03',LM()),('complementary',OtherLM())]:
  for name in ['fresh-shelley-2','fresh-mill-1']:
   base=next(c for c in frozen['cases'] if c['id']==name);case=ext[name];prior=json.loads(gzip.decompress((D/('fresh' if model=='p03' else 'complementary-fresh')/(name+'.json.gz')).read_bytes()));wrong=prior['exact'][0];true=trace(base['cipher'],case['key'],base['sign'],base['periodic'],set(base['ends']),set(base['truth_literal_positions']),lm);bad=trace(base['cipher'],case['key'],base['sign'],base['periodic'],set(base['ends']),set(wrong['literal_positions']),lm)
   assert [r['emitted'] for r in true]==base['truth'];assert [r['emitted'] for r in bad]==wrong['plain'];saved=next(c for c in claim['cases'] if c['model']==model and c['id']==name);segments=[];start=None
   for i,(a,b) in enumerate(zip(true,bad)):
    if start is None and (a['literal']!=b['literal'] or a['after']!=b['after']):start=i
    if start is not None and a['after']==b['after']:
     existing=saved['segments'][len(segments)];assert existing['start']==start and existing['reconverged_after']==i and existing['state']==a['after'];assert true[start]['before']==bad[start]['before']
     for ours,theirs in [(true[start:i+1],existing['true_rows']),(bad[start:i+1],existing['wrong_rows'])]:
      assert ours==theirs
     gap=math.fsum(bad[j]['local_weight']-true[j]['local_weight'] for j in range(start,i+1));assert gap>0 and abs(gap-existing['wrong_minus_true'])<1e-12
     raw,flat,spans=coord[base['source']];offset=base['source_rune_span'][0];assert flat[offset:offset+len(base['truth'])]==base['truth'];ss=spans[offset+start:offset+i+1];assert ss==existing['source_spans']==case['source_char_spans'][start:i+1]
     tab=next(t for t in tables if t['model']==model and t['start']==start);unique=sorted(set(map(tuple,ss)));words=raw[unique[0][0]:unique[-1][1]];assert tab['source_words']==words and tab['source_spans']==[list(x) for x in unique]
     for row,ar,br in zip(tab['rows'],true[start:i+1],bad[start:i+1]):
      assert row['truth']==TOK[ar['emitted']] and row['wrong']==TOK[br['emitted']] and row['weight_difference']==br['local_weight']-ar['local_weight']
      for side,tr in [('truth',ar),('wrong',br)]:assert row[side+'_contributions']==[dict(context=[TOK[t] for t in x['context']],emitted=TOK[x['emitted']],weight=x['weight']) for x in tr['contributions']]
     # One fixed branch-rich suffix, all8masks: demonstrate a pathwise bijection,
     # rather than rerunning150selected/random best suffixes.
     suffix=[0,16,0,3,0];ee={1,4};u=a['consumed'];ctx=tuple(a['after'][1:]);suffix_rows=[]
     for bits in itertools.product([False,True],repeat=3):
      lit={p for p,b in zip([0,2,4],bits) if b};tail=trace(suffix,case['key'],base['sign'],base['periodic'],ee,lit,lm,start=u,ctx=ctx);ta=a['total'];tb=b['total']
      for item in tail:ta+=item['local_weight'];tb+=item['local_weight'];assert tb>=ta
      suffix_rows.append(dict(literals=sorted(lit),true_total=ta,wrong_total=tb))
     segments.append(dict(start=start,reconverged_after=i,state=a['after'],source_words=words,source_spans=ss,gap=gap,true_rows=true[start:i+1],wrong_rows=bad[start:i+1],exhaustive_suffix_paths=suffix_rows));start=None
   assert len(segments)==len(saved['segments'])
   if start is not None:
    assert start==saved['unreconverged']['start']==514;assert true[-1]['after']==saved['unreconverged']['true_final_state']==[5,1,29];assert bad[-1]['after']==saved['unreconverged']['wrong_final_state']==[4,0,29]
   else:assert saved['unreconverged'] is None
   results.append(dict(model=model,id=name,segments=segments,unreconverged=saved['unreconverged']));print(model,name,[(x['start'],x['reconverged_after'],x['gap']) for x in segments],flush=True)
 dump('dominance-checks.json',dict(passed=True,cases=results,suffix_path_checks=24,scope='Independent cipher/state/token-weight/source-coordinate reconstruction;3segments×8fixedsuffixmasks. General dominance follows identical-state transition bijection and monotone float addition, not these samples.'))
if __name__=='__main__':main()
