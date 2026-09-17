import pathlib,sys,json,gzip,hashlib,re,math
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];D=R/'exploration/persistent-02/decoder';sys.path.insert(0,str(D))
import posterior_run as PR
import complementary as C
def dump(name,x):(O/name).write_text(json.dumps(x,indent=2)+'\n')
def striptime(x):
 if isinstance(x,list):return [striptime(v) for v in x]
 if isinstance(x,dict):return {k:striptime(v) for k,v in x.items() if k!='seconds'}
 return x
def main():
 src=json.loads((D/'complementary-model.json').read_text());fresh=json.loads((D/'fresh-controls.json').read_text());sourcechecks=[]
 assert not {s['path'] for s in src['sources']}&{s['path'] for s in fresh['sources']}
 for rec,(name,needle) in zip(src['sources'],C.SPEC):
  path=R/rec['path'];raw=path.read_text();assert hashlib.sha256(path.read_bytes()).hexdigest()==rec['sha256'];lo,hi=rec['span'];assert raw[lo:hi]==rec['raw_excerpt'];assert raw.index(needle)==lo
  matches=list(re.finditer(r"[A-Za-z]+(?:['’][A-Za-z]+)*",raw[lo:]))[:1000];assert len(matches)==1000;spans=[[lo+m.start(),lo+m.end()] for m in matches];assert spans==rec['word_spans'] and spans[-1][1]==hi
  p=[];ends=[]
  for m in matches:p.extend(C.keyword_to_indices(re.sub("['’]",'',m.group())));ends.append(len(p)-1)
  assert p==rec['runes'] and ends==rec['ends'];assert 'Gutenberg' not in raw[lo:hi] and '{Picture:' not in raw[lo:hi]
  sourcechecks.append(dict(path=rec['path'],sha256=rec['sha256'],span=rec['span'],words=1000,runes=len(p),begin=raw[lo:lo+180],end=raw[hi-180:hi]))
 cases=json.loads((D/'continuation-inputs.json').read_text())['cases'];rows=[]
 for model,lm in [('p03',PR.LM()),('complementary',PR.OtherLM())]:
  for name in ['fresh-mill-1','fresh-shelley-2']:
   c0=next(x for x in cases if x['id']==name);c=dict(c0,ends=c0['ends_primary']);prior=PR.read('continuation',model+'-'+name)['joint'];got=PR.run(c,[c['prefix_length']],prior,lm);old=PR.read('posterior-fresh',model+'-'+name);assert striptime(got)==striptime(old)
   pos=514 if 'mill' in name else 498;pre=next(x for x in got['prefix_only'][0]['posterior']['branch_marginals'] if x['position']==pos);post=next(x for x in got['full']['branch_marginals'] if x['position']==pos)
   score=lm.score(c['truth'],set(c['ends']))*(len(c['truth'])+len(c['ends']));weight=math.exp(score-got['full']['log_partition'])
   rows.append(dict(id=name,model=model,position=pos,prefix_literal=pre['literal'],full_literal=post['literal'],truth_path_weight=weight,joins_prefix=got['prefix_only'][0]['posterior']['joins'][-1]['key_positions'],joins_full=next(x['key_positions'] for x in got['full']['joins'] if x['cut_after_rune_count']==c['prefix_length']),pool_mass={w:v['pool_mass'] for w,v in got['beams'].items()}))
   print('posterior replay',model,name,pre['literal']['probability'],post['literal']['probability'],flush=True)
 dump('posterior-source-checks.json',dict(passed=True,sourcechecks=sourcechecks,representative_replays=rows,scope='All4model source spans remapped; targeted previously selected Mill/Shelley consequence, no new population estimate. P03 versus complementary differs in corpus and lexical preprocessing.'))
if __name__=='__main__':main()
