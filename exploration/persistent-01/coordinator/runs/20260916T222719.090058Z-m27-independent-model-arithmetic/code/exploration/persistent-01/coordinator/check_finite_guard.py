"""Independent existence/forward check of new finite-F prefix guard, both signs."""
import importlib.util,itertools,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=pathlib.Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('new_finite',ROOT/'exploration/persistent-01/worker-b/feasible.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
class Hostile:
    def add(self,t,s,n,r):return '',s+float(r!=0)*100,n+1

def main():
    tested=0;feasible=0
    for n in range(1,6):
        for c in itertools.product((0,1,2),repeat=n):
            for length in range(n+1):
                key=[(i*7+4)%29 for i in range(length)]
                for sign in (-1,1):
                    rows=m.decode(c,key,sign,False,Hostile(),width=1)
                    expected=length>=sum(v!=0 for v in c)
                    assert bool(rows)==expected,(c,key,sign)
                    if rows:
                        r=rows[0];literal=set(r['path']);j=0;rebuilt=[]
                        for i,p in enumerate(r['plain']):
                            if i in literal:assert p==0;rebuilt.append(0)
                            else:rebuilt.append((p-sign*key[j])%29);j+=1
                        assert tuple(rebuilt)==c and j==r['used'] and j<=length
                        feasible+=1
                    tested+=1
    result=dict(cases=tested,compatible_cases=feasible,width=1,signs=[-1,1],finding='Prefix feasibility guard retained an arithmetic completion iff key length >= nonzero ciphertext count, even under hostile ranking. Every retained path independently reconstructs ciphertext.',limit='Existence and arithmetic only; not optimal language ranking, planted recovery or plaintext evidence.')
    (OUT/'finite-guard-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
