"""Independent bounded review; no worker algorithm imports and no LP2 reads."""
import ast, base64, datetime, hashlib, io, json, math, pathlib, re, subprocess, tarfile, urllib.request, zlib
R=pathlib.Path(__file__).resolve().parent
W=R.parent/'worker-m/M21'
assert not (R.parent/'STOP').exists()
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
H=lambda x:hashlib.sha1(x).digest()
X=lambda a,b:bytes(x^y for x,y in zip(a,b))
def mask(s,n,step=20):
    out=bytearray()
    for offset in range(0,n,20):out.extend(H(s+(offset if step==20 else offset//20).to_bytes(4,'big')))
    return bytes(out[:n])
def unmask(em,step=20):
    seed=X(em[:20],H(em[20:]+bytes(4)))
    return X(em[20:],mask(seed,len(em)-20,step))
def strict(em,step=20):
    if len(em)<41:return None
    db=unmask(em,step)
    if db[:20]!=H(b''):return None
    tail=db[20:];i=0
    while i<len(tail) and tail[i]==0:i+=1
    return tail[i+1:] if i<len(tail) and tail[i]==1 else None
def wrap(db,seed=bytes(range(20))):
    mdb=X(db,mask(seed,len(db)))
    return X(seed,H(mdb+bytes(4)))+mdb
sources=[]
for mf in ['manifest.json','armour-manifest.json']:
    meta=json.loads((W/'sources'/mf).read_text());local=W/'sources'/meta['url'].split('/')[-1]
    remote=urllib.request.urlopen(meta['url'],timeout=30).read(1000000)
    assert remote==local.read_bytes()
    assert hashlib.sha256(remote).hexdigest()==meta['sha256']
    archive=tarfile.open(fileobj=io.BytesIO(remote),mode='r:gz');n=0
    for entry in meta['files']:
        b=archive.extractfile(entry['path']).read()
        assert b==(W/'sources'/entry['path']).read_bytes()
        assert hashlib.sha256(b).hexdigest()==entry['sha256'];n+=1
    sources.append({'url':meta['url'],'sha256':meta['sha256'],'unpatched_files_verified':n})
src=pathlib.Path('corpus/A-primary-artifacts/pgp/messages/2014-01-rsa-oaep-challenge.asc')
t=src.read_text();body=t[:t.index('-----BEGIN PGP SIGNATURE-----')]
body='\n'.join(line.removeprefix('- ') for line in body.splitlines())
arm=body[body.index('-----BEGIN COMPRESSED RSA'):body.index('-----END COMPRESSED RSA ENCRYPTED MESSAGE-----')+len('-----END COMPRESSED RSA ENCRYPTED MESSAGE-----')]+'\n'
lines=arm.splitlines();start=lines.index('')+1;cs=next(i for i in range(start,len(lines)) if lines[i].startswith('='))
packed=base64.b64decode(''.join(lines[start:cs]),validate=True)
assert hashlib.md5(packed).digest()==base64.b64decode(lines[cs][1:],validate=True)
raw=zlib.decompress(packed);a,b,tail=raw.split(b'\0',2);a,b=int(a),int(b)
assert tail[:a]==b'Cyphertext' and len(tail)==a+b
cipher=tail[a:];assert len(cipher)==162
p=97513779050322159297664671238670850085661086043266591739338007321
q=77506098606928780021829964781695212837195959082370473820509360759
n=int(''.join(re.search(r'n = ([\d\\\s]+)',body)[1].replace('\\','').split()))
assert p*q==n and re.search(r'e = 65537\b',body)
d=pow(65537,-1,math.lcm(p-1,q-1));ems=[];plain=[];rsa=[]
for pos in range(0,len(cipher),54):
    block=cipher[pos:pos+54];c=int.from_bytes(block,'big');assert c<n
    m=pow(c,d,n);em=m.to_bytes(53,'big');assert pow(m,65537,n).to_bytes(54,'big')==block
    # Separate CRT calculation checks ordinary modular exponentiation result.
    mp=pow(c,d%(p-1),p);mq=pow(c,d%(q-1),q)
    assert (mq+q*((mp-mq)*pow(q,-1,p)%p))==m
    assert strict(em) is not None and strict(em,1) is None
    assert unmask(em)[:20]==unmask(em,1)[:20]==H(b'')
    ems.append(em);plain.append(strict(em));rsa.append({'em_hex':em.hex(),'message_hex':plain[-1].hex(),'reencryption':True,'crt_agrees':True})
assert b''.join(plain)==bytes.fromhex('0a63753334336c33336e7161656b726e772e6f6e696f6e0a0a')
# Controls include empty and capacity messages, binary bytes, long zero padding,
# plus malformed DB cases with an otherwise valid empty-label hash.
vectors=[{'emlen':size,'message_hex':m.hex()} for size,m in [(41,b''),(42,b'x'),(53,b'A'),(53,b'Hello world!'),(255,bytes(range(214))),(511,bytes(range(256)))]]
bad_dbs=[H(b'')+b'\0'*13,H(b'')+b'\0\2\1BAD',H(b'')+b'\2\1BAD',b'X'*20+b'\1OK']
bad_ems=[wrap(db) for db in bad_dbs]+[b'X'*40,ems[0][::-1],b'\0'+ems[0]]
assert all(strict(em) is None for em in bad_ems)
request={'vectors':vectors,'historical_em_hex':[em.hex() for em in ems+bad_ems],'armour':arm}
(R/'request.json').write_text(json.dumps(request,indent=2))
cmd=['perl',str(W/'source_harness.pl'),str(R/'request.json')]
proc=subprocess.run(cmd,capture_output=True,timeout=30)
(R/'perl-stdout.json').write_bytes(proc.stdout);(R/'perl-stderr.txt').write_bytes(proc.stderr)
(R/'perl-command.json').write_text(json.dumps({'command':cmd,'exit_code':proc.returncode},indent=2));assert proc.returncode==0,proc.stderr
got=json.loads(proc.stdout);assert got['container_cipher_hex']==cipher.hex() and got['container_roundtrip']
for v,result in zip(vectors,got['vectors']):
    msg=bytes.fromhex(v['message_hex']);db=H(b'')+bytes(v['emlen']-41-len(msg))+b'\1'+msg
    assert result['em_hex']==wrap(db).hex() and result['message_hex']==msg.hex()
assert [x['ok'] for x in got['historical']]==[True]*3+[False]*len(bad_ems)
assert [x['message_hex'] for x in got['historical'][:3]]==[x.hex() for x in plain]
# Extract old matcher definitions without loading module imports or executing mains.
oldpath=pathlib.Path('liber-primus/analysis/round19/C1/e01_cryptrsa.py')
tree=ast.parse(oldpath.read_text());fns=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in {'mgf1','oaep_unmask','match_cryptrsa_oaep'}]
ns={'hashlib':hashlib,'HLEN':20,'LHASH':H(b'')};exec(compile(ast.Module(body=fns,type_ignores=[]),str(oldpath),'exec'),ns)
panels=[]
for size in [41,42,53,255,256,511]:
    for i in range(100):
        em=hashlib.shake_256(f'{size}/{i}'.encode()).digest(size)
        assert ns['oaep_unmask'](em)[:20]==unmask(em)[:20]
        assert bool(ns['match_cryptrsa_oaep'](em))==(unmask(em)[:20]==H(b''))
    panels.append({'em_length':size,'cases':100})
for em in ems+bad_ems:
    assert bool(ns['match_cryptrsa_oaep'](em))==(len(em)>=41 and unmask(em)[:20]==H(b''))
out={'verdict':'PASS_SCOPED','sources':sources,'carrier_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'blocks':rsa,'known_vectors':len(vectors),'malformed_controls_rejected':len(bad_ems),'old_predicate_panels':panels,'source_harness_sha256':hashlib.sha256((W/'source_harness.pl').read_bytes()).hexdigest(),'lp2_read':False,'signature_verified_here':False,'missing_legacy_factor_script':True}
(R/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
