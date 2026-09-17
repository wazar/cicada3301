from pathlib import Path
import json,gzip
R=Path(__file__).parent;P=R.parent/'worker-p/P20';MC={'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..','0':'-----','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....','7':'--...','8':'---..','9':'----.'};n=0
for path in [P/f'control-{i}.json.gz' for i in range(4)]+[P/'alphabet-control.json.gz']:
 z=json.load(gzip.open(path,'rt'));expected=[]
 for wi,word in enumerate(z['words']):
  for li,ch in enumerate(word):
   if li==0 and wi:
    expected.extend(dict(word=wi,letter=li,boundary='word',gap=g,trit='g') for g in range(2))
   elif li:expected.append(dict(word=wi,letter=li,boundary='letter',trit='g'))
   expected.extend(dict(word=wi,letter=li,morse_index=i,char=ch,trit=t) for i,t in enumerate(MC[ch]))
 assert expected==[{k:v for k,v in m.items() if k!='rune'} for m in z['maps']];n+=len(expected)
(R/'emission.json').write_text(json.dumps({'status':'PASS','complete_emission_maps':5,'entries':n,'morse_lengths':sorted(set(map(len,MC.values())))}));print(n)
