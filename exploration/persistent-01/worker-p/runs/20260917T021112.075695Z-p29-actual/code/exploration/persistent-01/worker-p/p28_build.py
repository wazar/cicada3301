from pathlib import Path
import subprocess,json,hashlib,shutil
R=Path(__file__).resolve().parents[3];W=R/'exploration/persistent-01/worker-p';S=W/'private-P28/resurrecting-open-source-projects-outguess-24810e1';O=W/'P28';rows=[]
def run(label,cmd,cwd):
 p=subprocess.run(cmd,cwd=cwd,capture_output=True,timeout=240);(O/(label+'.stdout')).write_bytes(p.stdout);(O/(label+'.stderr')).write_bytes(p.stderr);rows.append(dict(label=label,command=cmd,cwd=str(cwd.relative_to(R)),exit=p.returncode));(O/'build-commands.json').write_text(json.dumps(rows,indent=2)+'\n');assert p.returncode==0,label
# No autoconf/automake installed. Explicit platform config replaces generation only.
(S/'src/config.h').write_text('#define HAVE_MMAP 1\n#define HAVE_SNPRINTF 1\n')
j=S/'src/jpeg-6b-steg';c=(j/'jconfig.cfg').read_text()
for name in ['HAVE_PROTOTYPES','HAVE_UNSIGNED_CHAR','HAVE_UNSIGNED_SHORT','HAVE_STDDEF_H','HAVE_STDLIB_H']:c=c.replace('#undef '+name,'#define '+name+' 1')
(j/'jconfig.h').write_text(c)
run('build-jpeg',['make','-j1','-f','makefile.ansi','CC=cc','CFLAGS=-O2 -DHAVE_STDC_HEADERS','libjpeg.a'],j)
run('build-outguess',['cc','-O2','-std=gnu99','-I.','outguess.c','golay.c','arc.c','pnm.c','jpg.c','iterator.c','md5.c','jpeg-6b-steg/libjpeg.a','-lm','-o','outguess'],S/'src')
run('version',[str(S/'src/outguess'),'-h'],S/'src')
files=[S/'src/outguess',S/'src/config.h',j/'jconfig.h',W/'private-P28/source.tar.gz'];(O/'build-hashes.json').write_text(json.dumps([dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in files],indent=2)+'\n');print('BUILD PASS')
