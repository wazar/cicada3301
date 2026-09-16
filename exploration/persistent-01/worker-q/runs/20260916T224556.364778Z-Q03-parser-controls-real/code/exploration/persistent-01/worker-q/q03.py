import pathlib,json,gzip,hashlib,datetime
R=pathlib.Path(__file__).parent;src=pathlib.Path('exploration/persistent-01/worker-f/F06-maps.json');maps=json.loads(src.read_text());reserved={4,9,14,19,24,29,34,39,44,54};assert len(maps)==45 and not reserved.intersection(m['page'] for m in maps)
def digits(v):
 if v==0:return [0]
 out=[]
 while v:out.append(v%29);v//=29
 return out[::-1]
def parse(records):
 D=[()];seen={()};out=[];trace=[]
 for i,w in enumerate(records,1):
  reason=None;ref=None
  if len(w)<2:reason='missing_reference_digit'
  elif len(w)>2 and w[0]==0:reason='noncanonical_leading_zero'
  else:
   ref=0
   for x in w[:-1]:ref=29*ref+x
   if ref>=len(D):reason='reference_out_of_range'
   elif D[ref]+(w[-1],) in seen:reason='duplicate_dictionary_phrase'
  if reason:return {'accepted':False,'valid_records':i-1,'decoded':out,'trace':trace,'failure':{'record_onebased':i,'unit':w,'reason':reason,'reference':ref,'dictionary_entries_including_empty':len(D),'max_reference':len(D)-1}}
  phrase=D[ref]+(w[-1],);D.append(phrase);seen.add(phrase);out.extend(phrase);trace.append({'record':i,'reference':ref,'phrase':list(phrase)})
 return {'accepted':True,'valid_records':len(records),'decoded':out,'trace':trace}
def encode(seq):
 D={():0};records=[];p=()
 for x in seq:
  p2=p+(x,)
  if p2 in D:p=p2
  else:records.append(digits(D[p])+[x]);D[p2]=len(D);p=()
 return records,p
fixtures=[([[1]],'missing_reference_digit'),([[0,0,1]],'noncanonical_leading_zero'),([[1,3]],'reference_out_of_range'),([[0,1],[0,1]],'duplicate_dictionary_phrase')]
for records,reason in fixtures:assert parse(records)['failure']['reason']==reason
controls=[];real=[]
for m in maps:
 assert not (R.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
 records=[m['indices'][w['start']:w['end']] for w in m['words']];assert sum(records,[])==m['indices'];n=len(records)
 control=[digits(i-1)+[(i+3)%29] for i in range(1,n+1)];c=parse(control);assert c['accepted'];enc,tail=encode(c['decoded']);assert enc==control and not tail
 controls.append({'page':m['page'],'records':control,'parse':c,'roundtrip':True,'real_lengths_matched':[len(w) for w in records]==[len(w) for w in control]})
 violations=[{'record_onebased':i,'actual_length':len(w),'minimum':2,'maximum':1+len(digits(i-1))} for i,w in enumerate(records,1) if not 2<=len(w)<=1+len(digits(i-1))]
 z=parse(records)
 if z['accepted']:
  enc,tail=encode(z['decoded']);assert enc==records and not tail
 else:
  k=z['failure']['record_onebased']-1;span=m['words'][k];z['failure']['rune_span']=[span['start'],span['end']];z['failure']['source_char_positions']=m['source_char_positions'][span['start']:span['end']]
 real.append({'page':m['page'],'records':records,'parse':z,'length_violations':violations,'actual_runes':sum(map(len,records)),'maximum_runes_at_record_count':sum(1+len(digits(i-1)) for i in range(1,n+1))})
e={'source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'maps':maps,'controls':controls,'real':real,'rejection_fixtures':fixtures}
with gzip.open(R/'Q03-evidence.json.gz','wt') as f:json.dump(e,f)
summary={'pages':len(real),'accepted':sum(x['parse']['accepted'] for x in real),'records':sum(len(x['records']) for x in real),'length_violations':sum(len(x['length_violations']) for x in real),'pages_with_impossible_shape':sum(bool(x['length_violations']) for x in real),'actual_count_roundtrip_controls':len(controls),'exact_shape_matched_controls':sum(x['real_lengths_matched'] for x in controls),'results':[{'page':x['page'],'valid_records':x['parse']['valid_records'],'failure':x['parse'].get('failure'),'length_violations':len(x['length_violations']),'actual_runes':x['actual_runes'],'maximum_runes':x['maximum_runes_at_record_count']} for x in real]};(R/'Q03-result.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))
