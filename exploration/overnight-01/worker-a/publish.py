import argparse,hashlib,json,pathlib
import search as s

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--interim',action='store_true');a=ap.parse_args();O=s.O;stages=[p for p in O.iterdir() if p.is_dir() and p.name.startswith('r01')]+list((O/'r02').glob('*')) if (O/'r02').exists() else [p for p in O.iterdir() if p.is_dir() and p.name.startswith('r01')];summary=[];bylane={'R01':[],'R02':[]}
 for stage in stages:
  cp=stage/'checkpoint.json'
  if not cp.exists():continue
  d=json.loads(cp.read_text());lane='R01' if stage.name.startswith('r01') else 'R02';summary.append(dict(lane=lane,stage=str(stage.relative_to(O)),cursor=d['cursor'],total=d['total'],best=d['top'][0]['score'] if d['top'] else None));bylane[lane].extend(dict(x,stage=str(stage.relative_to(O))) for x in d['top'])
 for lane,rows in bylane.items():
  seen={};unique=[]
  for r in sorted(rows,key=lambda x:x['score'],reverse=True):
   k=(r['original_page'],tuple(r['plain']))
   if k in seen:seen[k]['equivalent_origins'].append(dict(id=r['id'],stage=r['stage'],mode=r['mode']));continue
   out=dict(id=f'{lane}:{r["stage"]}:{r["id"]}',lane=lane,original_page=r['original_page'],positions={'start':0,'end':r['n'],'kind':'full frozen rune-bearing original-page transcription'},plain_idx=r['plain'],translit=r['transliteration'],scores={'english_quadgram':r['score'],'statistics':r['statistics'],'word_view':r.get('word_view')},method={k:r[k] for k in ['mode','recipe','key_id','periodic','sign','offset','diagnostics','key_use'] if k in r},reset='key index reset at page start; F does not consume; rejection separate',literal_positions=r.get('alternatives',[{}])[0].get('literal_positions',[]) if r.get('alternatives') else [],alternatives=r.get('alternatives',[]),status='UNREVIEWED',replay={'stage':r['stage'],'source_candidate_id':r['id'],'search_code':'exploration/overnight-01/worker-a/search.py','clue_code':'exploration/overnight-01/worker-a/clues.py','fixed_keys':'audit/experiment-01/keys.json','clue_keys':'exploration/overnight-01/worker-a/r02/keys.json','run_manifests':'exploration/overnight-01/worker-a/runs/*/command.json','config_sha256':hashlib.sha256((s.ROOT/'exploration/overnight-01/config.json').read_bytes()).hexdigest()},equivalent_origins=[])
   if r.get('key') is not None:out['key']=r['key']
   seen[k]=out;unique.append(out)
  # Retain every stage top and deduplicate, with at least top20 overall and model-leading structurally distinct rows.
  (O/('r02' if lane=='R02' else lane)).mkdir(exist_ok=True);s.dump(O/('r02' if lane=='R02' else lane)/'top_candidates.json',unique)
 s.dump(O/'summary.json',dict(interim=a.interim,stages=summary,candidates={k:len(v) for k,v in bylane.items()}));print(json.dumps(summary))
if __name__=='__main__':main()
