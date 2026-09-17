import argparse,time,resource,json
from compare import LM,section,O,beam,kbest,finite_beam
from exact import decode
ap=argparse.ArgumentParser();ap.add_argument('case',choices=['section','finite']);ap.add_argument('method',choices=['exact','oldexact','beam64','beam256','beam1024']);a=ap.parse_args()
case=section()[0] if a.case=='section' else json.loads((O/'fresh-controls.json').read_text())['cases'][2];c=case['cipher'];ends=set(case['ends']);key=case['key'];sign=case.get('sign',-1);periodic=case.get('periodic',True);lm=LM();before=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;t=time.monotonic()
if a.method=='exact':rows,d=decode(c,key,lm.extend,sign=sign,periodic=periodic,ends=ends,retain=16)
elif a.method=='oldexact':
 assert periodic;rows,d=kbest(c,ends,key,sign,lm)
else:
 width=int(a.method[4:]);rows,d=beam(c,ends,key,sign,lm,width) if periodic else finite_beam(c,ends,key,sign,lm,width)
result=dict(case=case['id'],method=a.method,runes=len(c),score=rows[0]['score'],seconds=time.monotonic()-t,maxrss_before_bytes=before,isolated_process_maxrss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,diagnostics=d,scope='One process, one decoder; includes Python imports/model in process high-water; timed region excludes imports/model construction, includes first scorer cache fill; macOS ru_maxrss bytes.')
(O/('measure-'+a.case+'-'+a.method+'.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
