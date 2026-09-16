import pathlib,json,hashlib,base64,zlib,re,subprocess,random,datetime
R=pathlib.Path(__file__).parent
assert not (R.parent.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
P=97513779050322159297664671238670850085661086043266591739338007321;Q=77506098606928780021829964781695212837195959082370473820509360759;N=P*Q;E=65537;d=pow(E,-1,(P-1)*(Q-1));k=(N.bit_length()+7)//8
src=pathlib.Path('corpus/A-primary-artifacts/pgp/messages/2014-01-rsa-oaep-challenge.asc');text=src.read_text();body=text.split('-----BEGIN PGP SIGNATURE-----')[0];body='\n'.join(x[2:] if x.startswith('- ') else x for x in body.splitlines());published=int(re.search(r'n = ([\d\\\s]+)',body).group(1).replace('\\','').replace(' ','').replace('\n',''));assert published==N;assert re.search(r'e = 65537\b',body)
armour=re.search(r'-----BEGIN COMPRESSED RSA ENCRYPTED MESSAGE-----.*?-----END COMPRESSED RSA ENCRYPTED MESSAGE-----',body,re.S).group(0)+'\n';segment=armour.split('\n\n',1)[1].split('-----END')[0];encoded,checksum=segment.rsplit('\n=',1);compressed=base64.b64decode(encoded);assert hashlib.md5(compressed).digest()==base64.b64decode(checksum.strip());raw=zlib.decompress(compressed);head=re.match(rb'(\d+)\x00(\d+)\x00',raw);nl,vl=map(int,head.groups());pos=head.end();assert len(raw)==pos+nl+vl;assert raw[pos:pos+nl]==b'Cyphertext';cipher=raw[pos+nl:];assert len(cipher)==162 and k==54

def mgf(seed,length,step):return b''.join(hashlib.sha1(seed+i.to_bytes(4,'big')).digest() for i in range(0,((length+19)//20)*step,step))[:length]
def xor(a,b):assert len(a)==len(b);return bytes(x^y for x,y in zip(a,b))
def decode(em,step):
 seed=xor(em[:20],mgf(em[20:],20,step));db=xor(em[20:],mgf(seed,len(em)-20,step));tail=db[20:];m=re.fullmatch(rb'\x00*\x01(.*)',tail,re.S);ok=db[:20]==hashlib.sha1(b'').digest() and m is not None
 return dict(seed=seed.hex(),db=db.hex(),lhash_ok=db[:20]==hashlib.sha1(b'').digest(),strict_ok=ok,message_hex=m.group(1).hex() if ok else None)
def encode(msg,emlen):
 seed=bytes(range(20));db=hashlib.sha1(b'').digest()+bytes(emlen-41-len(msg))+b'\1'+msg;md=xor(db,mgf(seed,emlen-20,20));return xor(seed,mgf(md,20,20))+md
blocks=[]
for i in range(3):
 c=int.from_bytes(cipher[i*k:(i+1)*k],'big');assert c<N;em=pow(c,d,N).to_bytes(k-1,'big');assert pow(int.from_bytes(em,'big'),E,N)==c;old=decode(em,1);new=decode(em,20);assert new['strict_ok'];a=bytes.fromhex(old['db']);b=bytes.fromhex(new['db']);blocks.append(dict(index=i,cipher_hex=cipher[i*k:(i+1)*k].hex(),em_hex=em.hex(),old=old,new=new,first_db_divergence=next((j for j,(x,y) in enumerate(zip(a,b)) if x!=y),None),reencryption_exact=True))
vectors=[dict(message_hex=x.hex(),emlen=n) for n,x in [(53,b'A'),(53,b'Hello world!'),(255,b'Known synthetic message\x00\xff'*8),(511,bytes(range(256)))]]
request=dict(vectors=vectors,historical_em_hex=[x['em_hex'] for x in blocks],armour=armour);(R/'harness-request.json').write_text(json.dumps(request,indent=2));cmd=['perl',str(R/'source_harness.pl'),str(R/'harness-request.json')];p=subprocess.run(cmd,capture_output=True);(R/'perl-stdout.json').write_bytes(p.stdout);(R/'perl-stderr.txt').write_bytes(p.stderr);(R/'perl-command.json').write_text(json.dumps(dict(command=cmd,exit_code=p.returncode),indent=2));assert p.returncode==0,p.stderr;perl=json.loads(p.stdout)
assert perl['container_cipher_hex']==cipher.hex() and perl['container_roundtrip']
for py,pe in zip(vectors,perl['vectors']):
 em=encode(bytes.fromhex(py['message_hex']),py['emlen']);assert em.hex()==pe['em_hex'];assert decode(em,20)['message_hex']==py['message_hex'];assert pe['message_hex']==py['message_hex']
for b,pe in zip(blocks,perl['historical']):assert pe['ok'] and b['new']['message_hex']==pe['message_hex']
# Header predicate equality is algebraic for every em: seedmask length20 usescounter0,
# and first20 of dbmask also usescounter0. Othercounter values never enter predicate.
rng=random.Random(2026091752);panel=[]
for n in [53,255,256,511]:
 eq=0
 for j in range(1000):
  em=bytes(rng.randrange(256) for _ in range(n));a=decode(em,1);b=decode(em,20);assert a['seed']==b['seed'] and a['db'][:40]==b['db'][:40] and a['lhash_ok']==b['lhash_ok'];eq+=1
 panel.append(dict(emlen=n,trials=eq))
message=b''.join(bytes.fromhex(x['new']['message_hex']) for x in blocks);(R/'historical-plaintext.bin').write_bytes(message)
out=dict(source_path=str(src),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),n=N,e=E,k=k,n_bits=N.bit_length(),factors_product_matches_published=True,cipher_length=len(cipher),cipher_sha256=hashlib.sha256(cipher).hexdigest(),container_raw_hex=raw.hex(),container_md5_valid=True,blocks=blocks,plaintext_hex=message.hex(),plaintext_utf8=message.decode('utf8'),synthetic_source_interoperability=len(vectors),header_equivalence_panel=panel,header_equivalence_proof='For any EM with hLen20, seedmask output length20 and first20 DBmask use only counter0 under either convention. Both reconstructed seed and DB[0:20] are identical. Subsequent counter0x14 versus0x01 only changes DB[20:].',lp2_payload_read=False,lp2_retest_reason='No change to old first20-only predicate; no new payload/key/offset search justified.',actual_source_dependencies=perl['dependency_limits'])
(R/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ['blocks','container_raw_hex']},indent=2))
