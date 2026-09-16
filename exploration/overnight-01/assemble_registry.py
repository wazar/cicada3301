"""Assemble retained evidence; does not decode, rank anew, or consume holdouts."""
import hashlib,json,pathlib,collections
ROOT=pathlib.Path(__file__).resolve().parents[2]
BASE=ROOT/'exploration/overnight-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
    checks=[]
    for name in ['checked.json','binary_checked.json']:
        p=BASE/'review'/name
        if p.exists():
            d=read(p);checks.extend(d if isinstance(d,list) else d.get('checked',[]))
    checked={(str(r.get('source_file',r.get('file'))),str(r.get('id')),r.get('page') if '/r06/' in str(r.get('source_file',r.get('file'))) else None) for r in checks if r.get('independently_reproduced')}
    entries=[]
    for lane,rel in [('R01','worker-a/R01/top_candidates.json'),('R02','worker-a/r02/top_candidates.json'),('R03','worker-b/r03/top_candidates.json'),('R03','worker-b/r03-f/top_candidates.json'),('R04','worker-b/r04/top_candidates.json'),('R04','worker-b/r04/top_continuation_candidates.json'),('R04','worker-b/r04-wide/top_candidates.json'),('R04','worker-b/r04-wide/top_continuation_candidates.json'),('R05','worker-b/r05/top_candidates.json'),('R05','worker-b/r05/top_crib_implications.json'),('R06','worker-b/r06/top_candidates.json')]:
        p=BASE/rel
        if not p.exists():
            if 'crib' in rel:continue
            raise FileNotFoundError(p)
        entries.extend((lane,p,r) for r in read(p))
    p=BASE/'worker-c/top_candidates.json'
    for lane in ['R07','R08']:entries.extend((lane,p,r) for r in read(p)[lane])
    grouped={};counts=collections.Counter()
    for lane,p,r in entries:
        counts[lane]+=1
        page=r.get('original_page',r.get('page'))
        plain=r.get('plain_idx',r.get('plain',r.get('rune_indices')))
        if plain is None and r.get('choices'):plain=r['choices'][0].get('rune_indices')
        if plain is not None:identity=['runes',page,plain]
        elif 'output_hex' in r:identity=['bytes',r['output_hex']]
        else:identity=['relationship',r.get('pages'),r.get('positions_a'),r.get('positions_b'),r.get('difference_indices'),r.get('predicted_indices'),r.get('crib_side'),r.get('best_crib_implication')]
        key=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
        source=str(p.relative_to(ROOT));worker=p.relative_to(BASE).parts[0]
        reproduced=(source,str(r.get('id')),page if '/r06/' in source else None) in checked
        origin={'lane':lane,'source_file':source,'source_sha256':sha(p),'local_id':r.get('id'),'independently_reproduced':reproduced,'payload':r,'execution_manifests':f'exploration/overnight-01/{worker}/runs/*/command.json','current_code_sha256':{str(x.relative_to(ROOT)):sha(x) for x in (BASE/worker).glob('*.py')}}
        if key not in grouped:grouped[key]={'registry_id':'candidate-'+key[:20],'output_identity_sha256':key,'lanes':[],'status':'UNREVIEWED','origins':[],'input_config_sha256':sha(BASE/'config.json'),'review':'Arithmetic reproduction alone is not validation or evidence of meaning.'}
        item=grouped[key];item['origins'].append(origin)
        if lane not in item['lanes']:item['lanes'].append(lane)
        if reproduced:item['status']='REPRODUCIBLE_CANDIDATE'
    assert all(counts[f'R{i:02}']>=20 for i in range(1,9)),counts
    with (BASE/'candidate-registry.jsonl').open('w') as f:
        for item in grouped.values():f.write(json.dumps(item,separators=(',',':'))+'\n')
    summary={'retained_source_rows_by_lane':dict(counts),'unique_outputs_or_relationships':len(grouped),'status_counts':dict(collections.Counter(x['status'] for x in grouped.values())),'no_validation_or_solution_promotions':True,'checked_evidence':'review/checked.json and binary_checked.json; exact source-file/local-id matches only','note':'Unchanged complete worker payloads preserve keys, rune/byte outputs, alternatives, scores and transformation parameters. Code at actual execution is pinned in origin execution_manifests snapshots; current hashes are additional references. Duplicate outputs retain all origins; lane counts are not independent trials.'}
    (BASE/'registry-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
if __name__=='__main__':main()
