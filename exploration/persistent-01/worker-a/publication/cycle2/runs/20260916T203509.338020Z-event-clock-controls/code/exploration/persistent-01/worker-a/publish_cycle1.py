"""Freeze completed A cycle-one evidence; preserve working originals verbatim."""
import pathlib,json,gzip,hashlib,datetime
O=pathlib.Path(__file__).resolve().parent;ROOT=O.parents[2]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 dest=O/'publication'/'cycle1';assert not dest.exists();dest.mkdir(parents=True)
 names=['REPORT.md','P01-RESULTS.md','P04-RESULTS.md','P10-RESULTS.md','CARD-P01.md','CARD-P04.md','CARD-P10.md','p01.py','p04.py','p10.py','replay.py','compare_p01.py','periodic-aliases.json','p01-comparison.json','p01-structure-comparison.json','p01-page-leaders.json','p04-results.json','replay-results.json','strategy-ack.json','supplemental-input-manifest.json']
 files=[O/x for x in names]
 for name in ['real','null','plant','p10']:files+=sorted((O/name).glob('*'))
 for run in sorted((O/'runs').iterdir()):
  rec=run/'command.json'
  if not rec.exists():continue
  d=json.loads(rec.read_text())
  if d.get('outcome')!='PASS':continue
  if any(token in run.name for token in ['p01-','p04-','p10-']):files+=sorted(x for x in run.rglob('*') if x.is_file())
 rows=[]
 for src in sorted(set(files)):
  if not src.is_file():continue
  b=src.read_bytes();rel=src.relative_to(O);compress=src.suffix in ['.json','.txt'] and len(b)>50000;target=dest/str(rel)
  if compress:target=target.with_name(target.name+'.gz')
  target.parent.mkdir(parents=True,exist_ok=True);out=gzip.compress(b,compresslevel=9,mtime=0) if compress else b;target.write_bytes(out);assert (gzip.decompress(out) if compress else out)==b
  rows.append(dict(source=str(src.relative_to(ROOT)),source_sha256=sha(b),source_bytes=len(b),publication=str(target.relative_to(ROOT)),publication_sha256=sha(out),publication_bytes=len(out),encoding='gzip-of-source' if compress else 'verbatim-copy'))
 manifest=dict(frozen_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),strategy='outside-box-v1',experiments=['P01','P04','P10'],note='Immutable publication copies; source files preserved. Existing gzip score files copied verbatim, not recompressed. Planned P07/P12 are not executed evidence.',files=rows)
 (dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(dict(files=len(rows),source_bytes=sum(x['source_bytes'] for x in rows),publication_bytes=sum(x['publication_bytes'] for x in rows),manifest=str((dest/'manifest.json').relative_to(ROOT)))))
if __name__=='__main__':main()
