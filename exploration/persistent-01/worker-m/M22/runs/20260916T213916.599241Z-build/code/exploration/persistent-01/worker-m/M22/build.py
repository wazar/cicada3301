import pathlib,subprocess,json,hashlib
R=pathlib.Path(__file__).parent;cmd=['cc','-O3','-std=c99','-dynamiclib',str(R/'exact.c'),'-o',str(R/'exact.dylib')];p=subprocess.run(cmd,capture_output=True);(R/'compiler.json').write_text(json.dumps(dict(command=cmd,exit_code=p.returncode,stdout=p.stdout.decode(),stderr=p.stderr.decode()),indent=2));assert p.returncode==0
