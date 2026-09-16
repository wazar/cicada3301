import pathlib,gzip,json
R=pathlib.Path(__file__).parent;d=json.load(gzip.open(R/'Q03-evidence.json.gz','rt'));checked=0
for x in d['controls']:
 phrases=[[]];decoded=[]
 for w,t in zip(x['records'],x['parse']['trace']):
  ref=sum(v*29**i for i,v in enumerate(w[-2::-1]));phrase=phrases[ref]+[w[-1]];assert phrase==t['phrase'];phrases.append(phrase);decoded.extend(phrase);checked+=1
 assert decoded==x['parse']['decoded']
for x in d['real']:
 bad=[]
 for i,w in enumerate(x['records'],1):
  maxdigits=1
  while 29**maxdigits<=i-1:maxdigits+=1
  if not 2<=len(w)<=1+maxdigits:bad.append(i)
 assert bad==[z['record_onebased'] for z in x['length_violations']]
 w=x['records'][0];f=x['parse']['failure'];assert f['record_onebased']==1
 if len(w)==1:assert f['reason']=='missing_reference_digit'
 elif len(w)>2 and w[0]==0:assert f['reason']=='noncanonical_leading_zero'
 else:
  ref=sum(v*29**i for i,v in enumerate(w[-2::-1]));assert ref>0 and ref==f['reference'];assert f['reason']=='reference_out_of_range'
out={'control_records_decoded_independently':checked,'real_pages_first_failures_verified':len(d['real']),'all_length_bounds_verified':True};(R/'Q03-check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
