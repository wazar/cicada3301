import json,pathlib,importlib.util,hashlib
R=pathlib.Path(__file__).parent;P=R.parent/'worker-p';s=importlib.util.spec_from_file_location('p10final',P/'p10.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
x=m.parse((R/'fixtures/RGB-2.jpg').read_bytes())[0];assert x['blocks']==24 and x['dummy_blocks']==7
out={'dummy_edge':{'coded_blocks':24,'stored_blocks':17,'dummy_blocks':7},'parser_sha256':hashlib.sha256((P/'p10.py').read_bytes()).hexdigest(),'actual_evidence':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((P/'P10').glob('actual-*.json'))},'status':'PASS','scope':'baseline one-scan no-restart JPEG originals0/1 plus synthetic fixtures'};(R/'FINAL-CHECK.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
