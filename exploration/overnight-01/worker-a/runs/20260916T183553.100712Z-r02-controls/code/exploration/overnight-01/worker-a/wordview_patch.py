from pathlib import Path
root=Path(__file__).parent
p=root/'search.py';s=p.read_text();anchor='def render(p,page):'
new='''_WORDS=None
_BOUNDARIES={}
def wordstats(p,page):
 global _WORDS
 if _WORDS is None:
  import re
  _WORDS=set()
  for fn in ['solved_0_warning.txt','solved_0_wisdom.txt','solved_0_welcome.txt','solved_0_loss_of_divinity.txt','solved_0_koan_1.txt','solved_jpg107-167.txt','solved_p56_an_end.txt']:
   raw=(ROOT/'audit/parallel-01/reference/sources'/fn).read_text()
   _WORDS.update(tuple(ABC.index(c) for c in w) for w in re.findall('['+ABC+']+',raw))
 pid=page['original_page']
 if pid not in _BOUNDARIES:
  import re
  words=re.findall('['+ABC+']+','/'.join(x['raw'] for x in page.get('lines',[])));j=0;bounds=[]
  for w in words:bounds.append((j,j+len(w)));j+=len(w)
  _BOUNDARIES[pid]=bounds
 bounds=_BOUNDARIES[pid]
 return {'known_word_rune_fraction':sum(b-a for a,b in bounds if tuple(p[a:b]) in _WORDS)/max(1,len(p)), 'matched_words':sum(tuple(p[a:b]) in _WORDS for a,b in bounds),'word_count':len(bounds),'independence':'same solved-text register; descriptive only'}
'''
s=s.replace(anchor,new+anchor).replace('statistics=stats(p))','statistics=stats(p),word_view=wordstats(p,page))');p.write_text(s)
for fn in ['clues.py','rejection.py']:
 p=root/fn;s=p.read_text().replace('statistics=s.stats(p))','statistics=s.stats(p),word_view=s.wordstats(p,page))');p.write_text(s)
