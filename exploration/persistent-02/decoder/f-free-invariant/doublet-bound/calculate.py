import pathlib,json,hashlib,sys,importlib.util
from bound import forced
O=pathlib.Path(__file__).resolve().parent;R=O.parents[4];P=R/'exploration/persistent-02';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();sys.path.insert(0,str(R/'liber-primus/src'));from lp.gematria import runes_to_indices

def main():
 assert not (O/'results.json').exists();a=P/'feedback/C05/plants.json';b=P/'feedback/C11/plants.json';old=json.loads(a.read_text())['cases'];new=json.loads(b.read_text())['cases'];assert len(old)==len(new)==32;pins=[a,b,O/'bound.py',O/'PROOF.md',R/'liber-primus/src/lp/gematria.py'];controls=[]
 for idx,(x,y) in enumerate(zip(old,new)):
  assert all(x[f]==y[f] for f in ('id','truth','k','seed','literal_positions','source'));v=forced(x['truth'],x['k']);counts={label:sum(c==d for c,d in zip(z['cipher'],z['cipher'][1:])) for label,z in [('excluded',x),('emitted',y)]};assert all(n>=v['lower_bound'] for n in counts.values());assert all(z['cipher'][i]==z['cipher'][i-1] for z in (x,y) for i in v['forced_doublet_positions']);controls.append(dict(index=idx,id=x['id'],source=x['source'],observed_plant_doublets=counts,can_match_actual_four_doublets_under_bound=(v['lower_bound']<=4) if len(x['truth'])==716 else None,**v))
 src=R/'audit/parallel-01/reference/fixtures.py';pins.append(src);sp=importlib.util.spec_from_file_location('bound_reference_fixtures',src);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);refs=[]
 for name,*_ in mod.CASES:
  path=src.parent/'sources'/f'solved_{name}.txt';pins.append(path);p=runes_to_indices(path.read_text());assert p;refs.append(dict(id=name,source=str(path.relative_to(R)),sha256=H(path),plaintext=p,bounds=[forced(p,k) for k in (2,3)]))
 section=P/'section/section-packet.json';pins.append(section);c=json.loads(section.read_text())['body']['runes'];count=sum(x==y for x,y in zip(c,c[1:]));assert len(c)==716 and count==4
 result=dict(controls=controls,complete_known_references=refs,actual_geometry=dict(length=len(c),adjacent_opportunities=len(c)-1,doublets=count,doublet_positions=[i for i in range(1,len(c)) if c[i]==c[i-1]]),source_pins={str(p.relative_to(R)):H(p) for p in pins},scope='Lowerbound forfixedplaintext everyseed/legalplainFmask underbothno-reset constructors. Comparisontoactual4onlysame716length; not universalEnglishclaim; no optimization or actualdecode.');(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(same_length_controls=[dict(id=v['id'],k=v['k'],lower_bound=v['lower_bound'],observed=v['observed_plant_doublets']) for v in controls if v['length']==716],known_refs=[dict(id=v['id'],length=len(v['plaintext']),bounds=[b['lower_bound'] for b in v['bounds']]) for v in refs])))
if __name__=='__main__':main()
