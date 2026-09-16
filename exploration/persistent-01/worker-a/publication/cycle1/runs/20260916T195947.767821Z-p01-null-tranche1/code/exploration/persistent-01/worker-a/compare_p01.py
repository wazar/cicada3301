"""Descriptive full-procedure real/null comparison and fixed per-page leader replay."""
import gzip,json,collections,random
import p01
s=p01.s;O=p01.O

def main():
 data,pages,queue,excluded=p01.setup();defs={x['id']:x for x in data['keys']};lookup={p['original_page']:p for p in pages};q=s.Score();summary={};bestby={};leaders=[]
 for mode in ['real','null']:
  cp=json.loads((O/mode/'checkpoint.json').read_text());assert cp['cursor']==len(queue)
  ids=set();best={};counts=collections.Counter()
  for f in sorted((O/mode).glob('scores-*.jsonl.gz')):
   for line in gzip.open(f,'rt'):
    row=json.loads(line);i=int(row['id'].split(':')[-1]);assert i not in ids;ids.add(i);pid=row['original_page'];counts[pid]+=1
    if pid not in best or row['score']>best[pid]['score']:best[pid]=row
  assert ids==set(range(len(queue)));bestby[mode]=best;summary[mode]=dict(count=len(ids),per_page_counts=dict(counts),max=max(x['score'] for x in best.values()))
  for pid,row in best.items():
   c=lookup[pid]['indices'].copy()
   if mode=='null':random.Random(330104+pid).shuffle(c)
   key=p01.clues.key_for(row,defs,len(c));alts,diag=s.fbeam(c,key,row['sign'],q);assert abs(alts[0]['score']-row['score'])<1e-10;leaders.append(dict(row,alternatives=alts,transliteration=s.render(alts[0]['plain'],lookup[pid]),replay_only=True))
 paired=[dict(page=pid,n=len(lookup[pid]['indices']),real=bestby['real'][pid]['score'],null=bestby['null'][pid]['score'],gap=bestby['real'][pid]['score']-bestby['null'][pid]['score']) for pid in sorted(lookup)];summary.update(paired_page_maxima=paired,real_above_single_null=sum(x['gap']>0 for x in paired),interpretation='One matchedshuffle, descriptive comparison only.45 maxima compared; no pvalue. Replay90 leaders is diagnostic, not new searchcoverage.');s.dump(O/'p01-comparison.json',summary);s.dump(O/'p01-page-leaders.json',leaders);print(json.dumps(summary))
if __name__=='__main__':main()
