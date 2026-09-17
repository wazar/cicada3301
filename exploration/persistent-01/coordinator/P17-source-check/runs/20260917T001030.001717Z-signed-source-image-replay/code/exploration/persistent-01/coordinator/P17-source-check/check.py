from pathlib import Path
import tempfile, subprocess, json, hashlib, math
from PIL import Image
B=Path('exploration/persistent-01/worker-p/P17'); O=Path('exploration/persistent-01/coordinator/P17-source-check')
msg=Path('corpus/A-primary-artifacts/pgp/messages/2012-01-second-chance.asc'); key=Path('corpus/A-primary-artifacts/pgp/keys/cicada-3301-pubkey.keyserver.ubuntu.com.asc')
commands=[]
with tempfile.TemporaryDirectory(prefix='cicada-source-verification-') as home:
 for args in [['--import',str(key)],['--status-fd','1','--verify',str(msg)]]:
  cmd=['/opt/homebrew/bin/gpg','--no-options','--no-autostart','--homedir',home,'--batch']+args
  p=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
  commands.append(dict(command=[x.replace(home,'<ISOLATED_TEMP_HOME>') for x in cmd],exit_code=p.returncode,stdout=p.stdout.replace(home,'<ISOLATED_TEMP_HOME>'),stderr=p.stderr.replace(home,'<ISOLATED_TEMP_HOME>')))
assert commands[1]['exit_code']==0
assert 'VALIDSIG 6D854CD7933322A601C3286D181F01E57A35090F ' in commands[1]['stdout']
text=msg.read_text(); assert 'http://i.imgur.com/hkdgl.png' in text
hint=Image.open(B/'hkdgl.png').convert('RGB'); plate=Image.open(B/'mhh4.jpg').convert('RGB'); crop=plate.crop((5,360,368,496))
assert hint.size==crop.size==(363,136)
a=list(hint.getdata());b=list(crop.getdata());diff=[abs(x-y) for p,q in zip(a,b) for x,y in zip(p,q)]
ag=list(hint.convert('L').getdata());bg=list(crop.convert('L').getdata());n=len(ag)
sx=sum(ag);sy=sum(bg);cov=n*sum(x*y for x,y in zip(ag,bg))-sx*sy
corr=cov/math.sqrt((n*sum(x*x for x in ag)-sx*sx)*(n*sum(y*y for y in bg)-sy*sy))
result=dict(commands=commands,files=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [msg,key,B/'hkdgl.png',B/'mhh4.jpg',B/'pg45315.txt']],crop=[5,360,368,496],pixel_exact_fraction=sum(p==q for p,q in zip(a,b))/n,mean_abs_channel_difference=sum(diff)/len(diff),max_channel_difference=max(diff),grayscale_correlation=corr,signed_url_only=True)
(O/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['commands','files']}))
