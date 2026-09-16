import pathlib,json,collections,hashlib
import numpy as np
O=pathlib.Path(__file__).resolve().parent

def main():
 d=O/'l1-conditional';maps=json.loads((d/'maps-full-phases.json').read_text());manifest=json.loads((d/'input-manifest.json').read_text());summary=json.loads((d/'summary.json').read_text());ROOT=O.parents[2];config=json.loads((ROOT/'exploration/persistent-01/config.json').read_text());dataset=ROOT/'audit/parallel-01/inputs/dataset.json';assert hashlib.sha256(dataset.read_bytes()).hexdigest()==config['dataset_sha256'];originals={p['original_page']:p['indices'] for p in json.loads(dataset.read_text())['pages'] if p['original_page']<=55 and p['original_page']!=50 and p['original_page'] not in config['reserved_original_pages']};checked=0;certs=[];elig={m:{'train':[],'held':[],'omitted':[],'inspected_train':0,'inspected_held':0} for m in [1,2,4]}
 for page,pid in zip(maps,manifest['pages']):
  x=page['compressed'];idx=page['source_indices'];orig=originals[pid];expected_idx=[i for i in range(len(orig)) if i==0 or orig[i]!=orig[i-1]];assert idx==expected_idx;assert x==[orig[i] for i in expected_idx];part='held' if page['page_index']%2 else 'train'
  for mod in page['models']:
   m=mod['m'];B=29*m
   if not mod['phases']:
    assert len(x)<2*B-1;elig[m]['omitted'].append(pid);continue
   elig[m][part].append(pid);elig[m]['inspected_'+part]+=mod['best'][2]
   for phase,expected,inspected in mod['phases']:
    excess=0;witness=None
    for start in range(phase,len(x)-B+1,B):
     cc=collections.Counter(x[start:start+B]);excess+=sum(max(0,n-m) for n in cc.values())
     if witness is None:
      for symbol,n in cc.items():
       if n>m:
        positions=[idx[i] for i in range(start,start+B) if x[i]==symbol];witness={'original_page':pid,'m':m,'phase':phase,'compressed_block_start':start,'block_source_start':idx[start],'block_source_end_inclusive':idx[start+B-1],'rune_index':symbol,'count':n,'source_occurrences':positions};break
    assert expected==excess;assert inspected==B*((len(x)-phase)//B);checked+=1
    if witness:certs.append(witness)
   assert mod['best']==min(mod['phases'],key=lambda a:(a[1]/a[2],a[0]))
 null=json.loads((d/'null-arrays.json').read_text());cal=json.loads((d/'calibration.json').read_text());crit=float(np.quantile(null['statistics'],.99));mu=np.array(cal['mean']);sd=np.array(cal['sd']);controls=json.loads((d/'controls.json').read_text());power={}
 for k,c in controls.items():
  z=(np.array(c['scores'])-mu)/sd;choices=np.argmin(z[:,0,:],axis=1);stat=-z[np.arange(len(z)),1,choices];power[k]={'n':len(z),'detections_above_null99percentile':int(np.sum(stat>crit)),'held_statistic_range':[float(stat.min()),float(stat.max())]}
 result={'checked_phase_scores':checked,'excess_witnesses':len(certs),'every_eligible_real_phase_has_witness':len(certs)==checked,'eligibility':elig,'null_99percentile':crit,'power':power,'input_manifest_sha256':hashlib.sha256((d/'input-manifest.json').read_bytes()).hexdigest()};(d/'independent-verification.json').write_text(json.dumps(result,indent=2)+'\n');(d/'phase-witnesses.json').write_text(json.dumps(certs,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
