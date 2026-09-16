import ast,pathlib,json,zlib,bz2,lzma,gzip,hashlib
R=pathlib.Path(__file__).resolve().parents[3];O=pathlib.Path(__file__).parent
source=R/'exploration/persistent-01/worker-c/ob_c6.py';tree=ast.parse(source.read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='inspect');env=dict(zlib=zlib,bz2=bz2,lzma=lzma);exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'),env);inspect=env['inspect']
raw=bytes(range(29))*20; encoders={'zlib':zlib.compress,'gzip':lambda b:gzip.compress(b,mtime=0),'bz2':bz2.compress,'xz':lambda b:lzma.compress(b,format=lzma.FORMAT_XZ,check=lzma.CHECK_CRC64)};rows=[]
for name,encode in encoders.items():
 b=encode(raw);hits=inspect(b);assert any(h['format']==name and bytes.fromhex(h['decoded_hex'])==raw for h in hits)
 corrupt=bytearray(b)
 if name=='bz2':
  assert b[4:10]==bytes.fromhex('314159265359');corrupt[10]^=1
 else:corrupt[-1]^=1
 for mode,value in [('truncated',b[:-1]),('trailing',b+b'X'),('corrupt',bytes(corrupt)),('overcap',encode(b'X'*65537))]:
  h=inspect(value);assert not h,(name,mode,h)
 rows.append(dict(format=name,valid_recovers=True,invalid_modes_reject=True,encoded_hex=b.hex()))
alone=lzma.compress(raw,format=lzma.FORMAT_ALONE);nocheck=lzma.compress(raw,format=lzma.FORMAT_XZ,check=lzma.CHECK_NONE)
over=dict(lzma_alone_mislabeled_xz=any(h['format']=='xz' for h in inspect(alone)),xz_without_checksum_accepted=any(h['format']=='xz' for h in inspect(nocheck)))
records=0;admissible=0
with gzip.open(R/'exploration/persistent-01/worker-c/ob-c6/real-cells.jsonl.gz','rt') as f:
 for line in f:
  x=json.loads(line);records+=1
  if 'bytes_hex' in x:
   b=bytes.fromhex(x['bytes_hex']);assert hashlib.sha256(b).hexdigest()==x['sha256'];assert not inspect(b);admissible+=1
out=dict(review='C6 declared parser scope',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),controls=rows,overacceptance=over,real_records=records,real_admissible=admissible,all_real_hits_empty=True,conclusion='All four declared complete parser families recover the fixtures and reject four malformed/cap cases each. XZ acceptance is broader than card: auto-format admits legacy LZMA and no-check XZ. Original real accepted set is empty, so checksummed-XZ subset also empty. Future method must enforce FORMAT_XZ and check not CHECK_NONE; original output not silently revised.',scope='One fixture per family; control parser checks only, no new candidate coverage. Retained real bytes revalidated, not puzzle search. First review incorrectly expected a final bz2 padding-bit flip to fail; corrected corruption targets the explicit block CRC at byte10. Original failed run retained.')
(O/'C6-parser-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='controls'}))
