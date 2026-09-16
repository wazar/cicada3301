"""Count a specific prior finite-running-key F admission gap; does not decode."""
import hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[3]
OUT=pathlib.Path(__file__).resolve().parent

def main():
    defs=json.loads((ROOT/'exploration/overnight-01/worker-a/r02/keys.json').read_text())
    hold=set(json.loads((ROOT/'exploration/persistent-01/config.json').read_text())['reserved_original_pages'])
    pages=[p for p in json.loads((ROOT/'audit/parallel-01/inputs/dataset.json').read_text())['pages'] if p['original_page']<=55 and p['original_page'] not in hold]
    assert len(pages)==45 and not {p['original_page'] for p in pages}&hold
    eligible=[];omitted=[]
    for p in pages:
        n=len(p['indices']);f=p['indices'].count(0)
        for t in defs['texts']:
            for off in t['offsets']:
                rem=len(t['key'])-off
                if rem<=0 or rem<n-f:continue
                for sign in (-1,1):
                    r=dict(page=p['original_page'],key_id=t['id'],offset=off,sign=sign,remaining=rem,runes=n,cipher_Fs=f,minimum_consumption=n-f)
                    eligible.append(r)
                    if rem<n:omitted.append(r)
    summary=dict(eligible_cells=len(eligible),old_ordinary_length_eligible=len(eligible)-len(omitted),new_length_gap_cells=len(omitted),affected_pages=sorted({r['page'] for r in omitted}),interpretation='Necessary key-length eligibility only; no plaintext tested or recovered.',input_hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['audit/parallel-01/inputs/dataset.json','exploration/overnight-01/worker-a/r02/keys.json']})
    (OUT/'P10-scope.json').write_text(json.dumps(dict(summary=summary,omitted_cells=omitted),indent=2)+'\n')
    print(json.dumps(summary))
if __name__=='__main__':main()
