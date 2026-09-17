from pathlib import Path
import re,json,hashlib
p=Path('audit/reports/PERSISTENT-01.md');s=p.read_text();o=Path('exploration/persistent-01/review-73');links=[]
for label,target in re.findall(r'\[([^\]]+)\]\(([^)]+)\)',s):
 if '://' not in target:
  q=(p.parent/target.split('#')[0]).resolve();assert q.exists(),str(q);links.append({'label':label,'path':str(q.relative_to(Path.cwd())),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()})
assert '68 eligible' in s and '119/2,355' in s and '32,640' in s and 'ranks8/1/1/1' in s
assert 'Draft under final review' in s and 'will be recorded at the fixed deadline' in s
(o/'report-snapshot.md').write_text(s)
(o/'result.json').write_text(json.dumps({'pass':True,'report_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'links_checked':len(links),'links':links,'scope':'N18/S20/S21/N19 additions and corrected future glyph pool; deadline closure claims remain pending, not audited as completed'},indent=2))
print('PASS',len(links),'local links')
