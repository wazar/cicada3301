import json,pathlib,re,hashlib
R=pathlib.Path(__file__).parent;D=json.load(open('audit/parallel-01/inputs/dataset.json'));old=json.load(open(R/'F01-maps.json'));allowed={m['page'] for m in old};maps=[]
def parse(raw,A):
 chars=[(i,A.index(c)) for i,c in enumerate(raw) if c in A];words=[];gaps=[];start=0
 for j,((i,r),(ii,s)) in enumerate(zip(chars,chars[1:])):
  gap=raw[i+1:ii]
  if gap and not gap.isspace():
   words.append({'start':start,'end':j+1});gaps.append({'previous':j,'next':j+1,'text':gap,'type':'period' if '.' in gap else 'hyphen' if '-' in gap else 'mixed'});start=j+1
 if chars:words.append({'start':start,'end':len(chars)})
 return chars,words,gaps
A=D['alphabet'];controls=[]
for raw,expected in [(A[:2]+'\n'+A[2:4],[4]),(A[:2]+'\n-'+A[2:4],[2,2]),(A[:2]+'.\n'+A[2:4],[2,2]),(A[:2]+'7'+A[2:4],[2,2])]:
 c,w,g=parse(raw,A);out=[u['end']-u['start'] for u in w];assert out==expected;controls.append({'raw':raw,'lengths':out})
for p in D['pages']:
 if p['original_page'] not in allowed:continue
 raw=''.join(l['raw'] for l in p['lines']);c,w,g=parse(raw,A);assert [r for i,r in c]==p['indices'];lineof={i:l['source_line'] for l in p['lines'] for i in range(l['rune_start'],l['rune_end'])}
 for u in w:
  u['source_lines']=sorted({lineof[i] for i in range(u['start'],u['end'])});u['raw_positions']=[c[i][0] for i in range(u['start'],u['end'])];u['source_char_positions']=p['source_char_positions'][u['start']:u['end']]
 assert sum(u['end']-u['start'] for u in w)==len(c)
 maps.append({'page':p['original_page'],'indices':p['indices'],'source_char_positions':p['source_char_positions'],'raw_joined':raw,'words':w,'gaps':g,'line_of_rune':[lineof[i] for i in range(len(c))],'labels':next(m['labels'] for m in old if m['page']==p['original_page'])})
summary={'old_fragment_count':sum(len(m['words']) for m in old),'new_unit_count':sum(len(m['words']) for m in maps),'multiline_units':sum(len(w['source_lines'])>1 for m in maps for w in m['words']),'max_length':max(w['end']-w['start'] for m in maps for w in m['words']),'controls':controls,'examples':[{'page':m['page'],'word':w,'indices':m['indices'][w['start']:w['end']]} for m in maps if m['page'] in [0,1] for w in m['words'] if len(w['source_lines'])>1][:8]}
(R/'F06-maps.json').write_text(json.dumps(maps));(R/'F06-result.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
