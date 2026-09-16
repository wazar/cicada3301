"""Independent retained-evidence consistency checks; standard library only."""
import json
import pathlib
import sys

def main():
    checked = 0
    summaries = []
    for name in sys.argv[1:]:
        data = json.loads(pathlib.Path(name).read_text())
        for ref in data['reference']:
            literals = [t for t in ref['trace'] if t['action']=='literal_F']
            assert all(t['cipher']==t['plain']==0 and t['key_before']==t['key_after'] for t in literals)
            assert ref['plain']==ref['expected']
            print(json.dumps(dict(reference=ref['name'],interruption_trace=literals)))
        for result in data['cases']:
            c = result['fixture']
            truth_trace=[]
            used=0
            for i,p in enumerate(c['plain']):
                literal=i in c['interrupt']
                before=used
                enc=0 if literal else (p+c['key'][used])%29
                used+=not literal
                assert enc==c['cipher'][i]
                truth_trace.append(dict(position=i,plain=p,cipher=enc,action='literal_F' if literal else 'normal',key_before=before,key_after=used))
            signatures=set()
            for candidate in result['exhaustive']:
                j=0; rebuilt=[]
                for i,p in enumerate(candidate['plain']):
                    if i in candidate['path']:
                        assert p==0
                        rebuilt.append(0)
                    else:
                        rebuilt.append((p+c['key'][j])%29);j+=1
                assert rebuilt==c['cipher'] and j==candidate['used']
                signatures.add((tuple(candidate['path']),tuple(candidate['plain']),candidate['used']))
                checked+=1
            assert len(signatures)==result['compatible_paths']
            for beam in result['beams']:
                assert all((tuple(s['path']),tuple(s['plain']),s['used']) in signatures for s in beam['final_states'])
            summaries.append(dict(name=c['name'],runes=len(c['cipher']),observed_F=c['cipher'].count(0),
                                  literal_F=len(c['interrupt']),ordinary_cipher_F=c['cipher'].count(0)-len(c['interrupt']),
                                  truth_trace=truth_trace))
    print(json.dumps(dict(reencrypted_compatible_paths=checked,cases=summaries),indent=2))

if __name__=='__main__':main()
