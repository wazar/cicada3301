from pathlib import Path
import re,json,hashlib,datetime,sys
D=Path(__file__).parent;source=Path('audit/reports/PERSISTENT-01.md');name=sys.argv[1] if len(sys.argv)>1 else 'draft-snapshot';text=(D/(name+'.md')).read_text();rows=[]
for label,target in re.findall(r'\[([^\]]+)\]\(([^)]+)\)',text):
 if '://' in target:rows.append({'label':label,'target':target,'external':True});continue
 p=(source.parent/target.split('#')[0]).resolve();row={'label':label,'target':target,'exists':p.is_file()}
 if p.is_file():row.update(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 rows.append(row)
config=json.loads(Path('exploration/persistent-01/config.json').read_text());start=datetime.datetime.fromisoformat(config['start_local']);end=datetime.datetime.fromisoformat(config['hard_deadline_local']);assert (end-start).total_seconds()==8*3600;assert end.astimezone(datetime.timezone.utc).isoformat()=='2026-09-17T03:30:37+00:00'
out={'snapshot_sha256':hashlib.sha256((D/(name+'.md')).read_bytes()).hexdigest(),'links':rows,'all_local_links_exist':all(x.get('exists',True) for x in rows),'deadline_utc':config['deadline_utc'],'duration_hours':8};(D/(name+'-links.json')).write_text(json.dumps(out,indent=2));print('links',len(rows),'all_exist',out['all_local_links_exist'],'snapshot',out['snapshot_sha256'])
