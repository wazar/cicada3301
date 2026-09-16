"""Fixed-rule replay from retained candidates, independently spelled arithmetic; no ranking."""
import argparse,json,pathlib
R=pathlib.Path(__file__).resolve().parents[3];O=pathlib.Path(__file__).parent

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--id');a=ap.parse_args();data=json.loads((R/'audit/parallel-01/inputs/dataset.json').read_text());pages={p['original_page']:p['indices'] for p in data['pages']};keys=json.loads((R/'audit/experiment-01/keys.json').read_text());clues=json.loads((O/'r02/keys.json').read_text());defs={x['id']:x['key'] for x in clues['keys']+clues['texts']};out=[]
 for lane in ['R01','R02']:
  for c in json.loads((O/('r02' if lane=='R02' else lane)/'top_candidates.json').read_text()):
   if a.id and c['id']!=a.id:continue
   m=c['method'];ct=pages[c['original_page']];sign=m['sign'];off=m['offset'];mode=m['mode'];k=None
   if mode!='affine':
    if 'recipe' in m:k=keys[m['recipe']][off:]
    else:
     src=defs[m['key_id']];k=[src[(i+off)%len(src)] for i in range(len(ct))] if m['periodic'] else src[off:]
   def decode(literals):
    result=[];j=0
    for i,v in enumerate(ct):
     if mode=='affine':p=(int(m['recipe'])*v+sign)%29
     elif mode=='literal_f' and i in literals:assert v==0;p=0
     elif mode=='rejection':p=(v+sign*k[m['key_use'][i]])%29
     else:p=(v+sign*k[j])%29;j+=1
     result.append(p)
    return result
   got=decode(set(c['literal_positions']));assert got==c['plain_idx'],c['id']
   for alt in c['alternatives']:assert decode(set(alt['literal_positions']))==alt['plain'],c['id']
   out.append(dict(id=c['id'],original_page=c['original_page'],exact=True,alternatives=len(c['alternatives']),n=len(got)))
 assert out,'no candidate matched';(O/'replay-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(verified=len(out),runes=sum(x['n'] for x in out))))
if __name__=='__main__':main()
