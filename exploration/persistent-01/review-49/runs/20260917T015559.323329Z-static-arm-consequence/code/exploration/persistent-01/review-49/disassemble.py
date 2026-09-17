from pathlib import Path
import subprocess,json
R=Path(__file__).parent;binary=R.parent/'worker-p/private-P28/resurrecting-open-source-projects-outguess-24810e1/src/outguess';p=subprocess.run(['/usr/bin/otool','-tvV',str(binary)],capture_output=True,text=True);(R/'otool.stderr').write_text(p.stderr);assert p.returncode==0
lines=p.stdout.splitlines();keep=[];active=False
for line in lines:
 if line.endswith(':') and not line.startswith(' '):active=line in ['_iterator_next:','_iterator_adapt:','_steg_retrbyte:']
 if active:keep.append(line)
(R/'iterator-disassembly.txt').write_text('\n'.join(keep)+'\n');(R/'disassembly-command.json').write_text(json.dumps(dict(command=p.args,exit_code=p.returncode,scope='Static inspection only; no extractor rerun'),indent=2));print('\n'.join(keep))
