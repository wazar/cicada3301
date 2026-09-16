import checks as c

def final_legacy(result,cs,key):
    if not result['english_accept']: return {'accept':False,'reason':'two-page English prerequisite failed; remaining gate cannot reverse rejection'}
    mean,mx=c.oracle.null_band(cs[0],key,n=200)
    bar=max(-5.5,mx+.5)
    return {'accept':result['second']>=bar and result['best']>mx+.5,'null_n':200,'null_mean':mean,'null_max':mx,'bar':bar}

def main():
    c.handchecks();t=c.time.monotonic();out={'handchecks':True,'matrix_sha256':c.hashlib.sha256((c.OUT/'MATRIX.md').read_bytes()).hexdigest(),'cells':[],'challenges':[]}
    for L in [60,120]:
        cell={'L':L,'positive':[],'negative':[],'structured_controls':[],'shuffle_selection':[]}
        for seed in range(51000,51020):
            ps,key,cs,used=c.plant(L,seed);r=c.select(cs,key,ps);r.update(seed=seed,used=used,final=final_legacy(r,cs,key));cell['positive'].append(r)
        ps,key,cs,used=c.plant(L,51000)
        for seed in range(61000,61100):
            rng=c.random.Random(seed);wk=[rng.randrange(29) for _ in range(2048)];r=c.select(cs,wk,ps);r.update(seed=seed,final=final_legacy(r,cs,wk));cell['negative'].append(r)
        for name,wk in [('constant',[13]*2048),('periodic',[i%29 for i in range(2048)]),('shifted',key[1:]+key[:1])]:
            r=c.select(cs,wk,ps);r.update(control=name,final=final_legacy(r,cs,wk));cell['structured_controls'].append(r)
        for seed in range(71000,71100):
            rng=c.random.Random(seed);sh=[x.copy() for x in cs]
            for x in sh:rng.shuffle(x)
            r=c.select(sh,key);narrow=r['rows'][0]['choices'][2]['score']
            cell['shuffle_selection'].append({'seed':seed,'narrow':narrow,'selected_best':r['best'],'selected_second':r['second'],'english_accept':r['english_accept']})
        out['cells'].append(cell);print('cell',L,'done',flush=True)
    spec=c.importlib.util.spec_from_file_location('audit_drift',c.ROOT/'liber-primus/analysis/round19/I1/driftbeam.py');drift=c.importlib.util.module_from_spec(spec);spec.loader.exec_module(drift)
    for construction,register in [('continuous','english'),('skip2','english'),('reset','novowel')]:
        cell={'construction':construction,'register':register,'L':120,'positive':[]}
        for seed in range(51000,51020):
            ps,key,cs,used=c.plant(120,seed,construction,register);r=c.select(cs,key,ps);r.update(seed=seed,used=used,final=final_legacy(r,cs,key))
            if construction=='skip2':
                r['R19_pair']=[]
                for p,ct in zip(ps,cs):
                    d=drift.beam_decode(ct,key,sign=-1,beam_w=400,**drift.PRESETS['pair']);r['R19_pair'].append({'score':d['score'],'recovery':sum(a==b for a,b in zip(p,d['plain_idx']))/len(p),'exact':p==d['plain_idx']})
            if construction=='continuous':
                r['known_offset_beam']=[]
                for p,ct,u in zip(ps,cs,used):
                    d=c.sk.beam_decode(ct,key,sign=-1,o=u[0],beam_w=400,max_skip=3);r['known_offset_beam'].append({'offset':u[0],'recovery':sum(a==b for a,b in zip(p,d['plain_idx']))/len(p),'score':d['score']})
            if register=='novowel':r['truth_scores']=[c.sk.Q.score_norm(''.join(c.TOKENS[i] for i in p)) for p in ps]
            cell['positive'].append(r)
        out['challenges'].append(cell);print('challenge',construction,register,'done',flush=True)
    out['elapsed_seconds']=c.time.monotonic()-t
    (c.OUT/'raw-results.json').write_text(c.json.dumps(out,indent=2));print('finished',out['elapsed_seconds'])
if __name__=='__main__': main()
