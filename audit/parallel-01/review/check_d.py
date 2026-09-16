import pathlib,json,collections,math,importlib.util
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=pathlib.Path(__file__).parent
p=ROOT/'audit/parallel-01/statistics/check_statistics.py';spec=importlib.util.spec_from_file_location('review_statistics',p);d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d);d.tests()
raw=(ROOT/'liber-primus/data/krisyotam_runes.txt').read_text();alpha='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';sites=[(i,c) for i,c in enumerate(raw) if c in alpha][:12956];bins=collections.defaultdict(lambda:[0,0]);pairs=[]
for j,((a,x),(b,y)) in enumerate(zip(sites,sites[1:])):
 gap=raw[a+1:b];tag='page_join' if '%' in gap else 'slash_line_join' if '/' in gap else 'within_line_separator' if gap else 'literal_adjacent_runes';bins[tag][0]+=1;bins[tag][1]+=x==y
 if x==y:pairs.append(j)
n=len(sites);counts=collections.Counter(c for i,c in sites);entropy=sum(-v/n*math.log2(v/n) for v in counts.values());ioc=sum(v*(v-1) for v in counts.values())/(n*(n-1));actual=json.loads((ROOT/'audit/parallel-01/statistics/results.json').read_text())
assert abs(entropy-actual['overall']['entropy_bits'])<1e-12 and abs(ioc-actual['overall']['ioc'])<1e-12
assert {k:{'pairs':v[0],'equal':v[1]} for k,v in bins.items()}==actual['categories']
import csv
recorded=[int(x['left_global']) for x in csv.DictReader((ROOT/'audit/parallel-01/statistics/pairs.csv').open())];assert pairs==recorded
r={'categories':dict(bins),'entropy':entropy,'ioc':ioc,'all_86_pair_positions_equal':pairs==recorded,'formula_handtests_pass':True};(OUT/'statistics-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
