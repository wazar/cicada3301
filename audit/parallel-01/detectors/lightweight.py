import checks as c
out={'handchecks':c.handchecks()}
wrong=[c.random.Random(4242).randrange(29) for _ in range(4096)]
rng=c.random.Random(4242);varied=[rng.randrange(29) for _ in range(4096)]
out['C011']={'legacy_distinct':len(set(wrong)),'legacy_symbol':wrong[0],'varied_distinct':len(set(varied))}
# Execute public functions with instrumented, deterministic decoder wrappers to record
# actual selection dispatch. This is an interface probe, not a statistical test.
orig_b,orig_r=c.sk.beam_decode,c.sk.rigid_decode;calls=[]
def spy(mode):
    def f(seg,key,**kw):
        calls.append({'mode':mode,'page_length':len(seg),**kw});return {'score':-7.,'translit':'TEST'}
    return f
try:
    c.sk.beam_decode=spy('beam');c.sk.rigid_decode=spy('rigid')
    c.oracle.judge_keystream([1]*100,[[1,2,3],[4,5,6,7]],'probe');out['judge_dispatch']=calls.copy();calls.clear()
    c.oracle.null_band([1,2,3],[1]*100,n=3);out['null_dispatch']=calls.copy()
finally:c.sk.beam_decode,c.sk.rigid_decode=orig_b,orig_r
spec=c.importlib.util.spec_from_file_location('audit_null',c.ROOT/'liber-primus/benchmark/null.py');mod=c.importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
out['C016']={str(L):mod.threshold_for(10**9,segment_len=L) for L in [1,31,60,120,400,12956,None]}
# Actual model-loading attempt; no builder or downloads.
spec=c.importlib.util.spec_from_file_location('audit_panel',c.ROOT/'liber-primus/analysis/round19/I2/adjudicate.py');ad=c.importlib.util.module_from_spec(spec);spec.loader.exec_module(ad)
try:ad.Panel();out['C018_model']='loaded'
except FileNotFoundError as e:out['C018_model']={'blocked':type(e).__name__,'expected_relative_path':'liber-primus/analysis/round19/I2/models/panel.npz'}
surface=c.json.loads((c.ROOT/'liber-primus/analysis/round21/L1-seal-realmode-proxy/catch_surface.json').read_text())
valid=[]
for row in surface['catch_surface']:
    assert row['catch_rate']==row['catch']/row['catch_n']
    assert row['genuine_false_reject_rate']==row['genuine_false_reject']/row['genuine_n']
    if row['genuine_false_reject_rate']<=.1:valid.append(row)
best=max(valid,key=lambda r:r['catch_rate']);held=surface['heldout_surrogate_audit']
out['C019_record_arithmetic']={'tested_surface_cells':len(surface['catch_surface']),'best_genuine_safe_catch':best['catch_rate'],'heldout_catch':held['kfold_catch']/held['kfold_catch_n'],'heldout_false_reject':held['surrogate_genuine_false_reject']/held['surrogate_genuine_n'],'fresh_population_rerun':False}
answer=c.json.loads((c.ROOT/'audit/parallel-01/coordination/blind-answer.json').read_text());challenge=c.json.loads((c.ROOT/'audit/parallel-01/coordination/blind-challenge.json').read_text());ranking=c.json.loads((c.OUT/'blind-ranking.json').read_text());top=ranking['ranking'][0]['candidate_id'];key=challenge['keys'][challenge['candidate_ids'].index(top)]
out['blind_reveal']={'top':top,'correct':answer['correct_candidate'],'match':top==answer['correct_candidate'],'decoded':c.select(challenge['ciphertext_pages'],key,answer['plaintext_indices'])}
# Selftest run, capture exact output without invoking CLI main / puzzle inputs.
import io,contextlib
buf=io.StringIO()
with contextlib.redirect_stdout(buf):code=c.oracle.selftest()
(c.OUT/'oracle-selftest.stdout.txt').write_text(buf.getvalue());out['C010_selftest_returncode']=code
(c.OUT/'lightweight.json').write_text(c.json.dumps(out,indent=2));print(c.json.dumps(out,indent=2))
