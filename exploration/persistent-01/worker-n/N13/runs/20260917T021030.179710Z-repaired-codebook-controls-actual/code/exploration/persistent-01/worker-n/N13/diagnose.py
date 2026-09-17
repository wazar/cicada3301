from pathlib import Path
R=Path(__file__).parent
s=(R/'test.py').read_text().replace("assert len(proposals)<10000", "\n   if len(proposals)>=10000:\n    (R/'failed-control.json').write_text(json.dumps(dict(n=n,L=L,rep=rep,proposals=proposals,completed_controls=controls),indent=2));raise RuntimeError(f'preserved failed n={n} L={L}')")
exec(compile(s,str(R/'test.py'),'exec'))
