import pathlib,json,hashlib,importlib.util
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2]
spec=importlib.util.spec_from_file_location('gp',R/'liber-primus/src/lp/gematria.py');gp=importlib.util.module_from_spec(spec);spec.loader.exec_module(gp)
def trans(p,ends):return ''.join(gp.IDX_TO_TRANS[x]+(' ' if i in ends else '') for i,x in enumerate(p))
def main():
 rows=[];texts=[];topall=[]
 for path in sorted((O/'C01').glob('actual*-summary.json'),key=lambda p:int(p.name.split('-')[0][6:])):
  row=json.loads(path.read_text());page=row['page'];d=json.loads((O/'C01'/f'actual{page}.json').read_text());top=d['global16'][0];row.update(seed=top['seed'],k=top['k']);rows.append(row)
  texts.append(f"Original {page}; score {row['maximum']:.12f}; upper-tail {row['tail']}; k={top['k']}; seed={top['seed']}\n"+trans(top['plain'],set(d['ends']))+'\n')
  topall.append(dict(page=page,ends=d['ends'],alternatives=d['global16']))
 (O/'C01'/'coverage.json').write_text(json.dumps(rows,indent=2)+'\n');(O/'C01'/'page-leaders.txt').write_text('\n'.join(texts));(O/'C01'/'all-top16.json').write_text(json.dumps(topall,separators=(',',':'))+'\n')
 lines=['| Original | Runes | Maximum P03 | k | Seed | Null upper tail |','|---:|---:|---:|---:|---|---:|']
 for row in rows:lines.append(f"| {row['page']} | {row['length']} | {row['maximum']:.9f} | {row['k']} | {row['seed']} | {row['tail']:.2f} |")
 (O/'C01'/'coverage.md').write_text('\n'.join(lines)+'\n');print(json.dumps(dict(pages=len(rows),actual_seeds=len(rows)*732511,total_seeds=len(rows)*20*732511,search_seconds=sum(r['search_seconds'] for r in rows),tail05=[r['page'] for r in rows if r['tail']==.05])))
if __name__=='__main__':main()
