# Supplemental whole-page-family controls, no new real search.
import pathlib,json
R=pathlib.Path(__file__).parent
code=(R/'h10.py').read_text().split('gate();before=counts.copy()')[0]
exec(compile(code,str(R/'h10.py'),'exec'),globals())
full=[]
for c in controls:
 gate();pi=next(i for i,m in enumerate(M) if m['page']==c['original_page']);planted=[x[:] for x in L];planted[pi]=c['lengths'];hits,u=scan(planted);truth=[h for h in hits if h['page_index']==pi and h['record_hex']==c['record_hex']];assert truth
 null=[];nullhits=[]
 for rep in range(99):
  hh,_=scan([rng.sample(x,len(x)) for x in planted]);null.append(len(hh))
  if hh:nullhits.append(dict(rep=rep,hits=hh))
 full.append(dict(page=c['original_page'],base=c['base'],origin=c['origin'],reverse=c['reverse'],record_hex=c['record_hex'],truth=truth,hits=len(hits),null=null,nullhits=nullhits,tail=(1+sum(n>=len(hits) for n in null))/100))
r=dict(controls=full,seed=2026091730,full_control_searches=len(full),full_control_null_searches=99*len(full),counts=counts,byte_stream_sha256=digest.hexdigest());(R/'H10-full-controls.json').write_text(json.dumps(r,indent=2));print(json.dumps(dict(controls=len(full),null_searches=99*len(full),tails=[c['tail'] for c in full],counts=counts),indent=2))
