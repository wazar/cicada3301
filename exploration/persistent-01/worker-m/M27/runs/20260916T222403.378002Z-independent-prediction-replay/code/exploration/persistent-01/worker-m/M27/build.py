import pathlib,subprocess,json
R=pathlib.Path(__file__).parent;cmd=['c++','-O3','-std=c++17','-dynamiclib',str(R/'fit.cpp'),'-o',str(R/'fit.dylib')];p=subprocess.run(cmd,capture_output=True);(R/'compiler.json').write_text(json.dumps(dict(command=cmd,exit_code=p.returncode,stdout=p.stdout.decode(),stderr=p.stderr.decode()),indent=2));assert p.returncode==0
