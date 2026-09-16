import pathlib,sys,json,random,gzip,time
R=pathlib.Path(__file__).parent;ROOT=R.parents[3];sys.path.insert(0,str(R.parent/'M25'));import m25
# Deliberate output-directory override; scientific functions/keys/objective unchanged.
m25.R=R
assert (R/'execution-clearance.json').is_file(), 'Awaiting root independent-kernel clearance'
clearance=json.load(open(R/'execution-clearance.json'));assert clearance['cleared'] is True
assert m25.CELLS==json.load(open(R.parent/'M25/keys.json'))
(R/'evidence').mkdir(exist_ok=True);(R/'keys.json').write_bytes((R.parent/'M25/keys.json').read_bytes())
base_transition=m25.transitions;diag={}
def monitored(c,prev,j,key,sign,stride):
 diag['transition_queries']+=1;diag['max_consumed_before']=max(diag['max_consumed_before'],j)
 if j>=len(key):diag['exhausted_consumed_state_queries']+=1
 out=base_transition(c,prev,j,key,sign,stride)
 for p,u,t in out:diag['max_accepted_key_index']=max(diag['max_accepted_key_index'],u-1)
 return out
m25.transitions=monitored

def generate(c,rng):
 v=[rng.randrange(29)]
 for a,b in zip(c,c[1:]):
  if a==b:v.append(v[-1])
  else:q=rng.randrange(28);v.append(q+(q>=v[-1]))
 assert [a==b for a,b in zip(v,v[1:])]==[a==b for a,b in zip(c,c[1:])];return v

def execute(name,c,ends):
 p=R/'evidence'/(name+'.json.gz');dpath=R/'diagnostics'/(name+'.json')
 if p.exists():
  with gzip.open(p,'rt') as f:r=json.load(f)
  if not dpath.exists():dpath.write_text(json.dumps(dict(diagnostic_status='unavailable interrupted between evidence and diagnostic write',input_runes=len(c),minimum_buffer_slack=1024-len(c),finite_buffer=1024),indent=2))
  return r
 diag.update(transition_queries=0,max_consumed_before=0,max_accepted_key_index=-1,exhausted_consumed_state_queries=0)
 r=m25.search(name,c,ends);dpath.write_text(json.dumps(dict(**diag,input_runes=len(c),minimum_buffer_slack=1024-len(c),finite_buffer=1024,selected_terminal_used=max(row['decode']['alternatives'][0]['used'] for row in r['rows']),max_complete_terminal_used=max(s['used'] for row in r['rows'] for s in row['decode']['terminal_states'])),indent=2));return r

def main():
 m25.gate();(R/'diagnostics').mkdir(exist_ok=True);maps=json.load(open(ROOT/'exploration/persistent-01/worker-f/F06-maps.json'));pages=[m for m in maps if m['page'] not in [0,17]];assert len(pages)==43;rng=random.Random(330828);results=[];omitted=[];start=time.monotonic()
 for m in pages:
  pid=m['page'];c,ends=m25.parse(m['raw_joined']);assert c==m['indices']
  if len(c)>1024:omitted.append(dict(page=pid,reason='input exceeds finite1024drawbuffer'));continue
  real=execute('real-'+str(pid),c,ends);null=[]
  for rep in range(19):
   v=generate(c,rng);r=execute('null-'+str(pid)+'-'+str(rep),v,ends);null.append(dict(name=r['name'],score=r['score']))
  row=dict(page=pid,map=m,score=real['score'],best_id=real['rows'][0]['id'],null=null,tail=(1+sum(x['score']>=real['score'] for x in null))/20,seed=330828);results.append(row);m25.dump('results',results);m25.dump('resume',dict(completed_pages=[x['page'] for x in results],omitted=omitted,rng_state=repr(rng.getstate())));print(pid,row['score'],row['tail'],'elapsed',time.monotonic()-start,flush=True)
 m25.dump('summary',dict(pages=len(results),omitted=omitted,searches=len(results)*20,top1_calls=len(results)*80,top16_calls=len(results)*20,descriptive_min_tail_pages=[r['page'] for r in results if r['tail']==.05],seconds=time.monotonic()-start,best=max((dict(page=r['page'],score=r['score'],tail=r['tail'],key_id=r['best_id']) for r in results),key=lambda x:x['score'])))
if __name__=='__main__':main()
