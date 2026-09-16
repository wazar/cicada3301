"""Materialise a source-only T1 register; never imports or executes research code."""
import datetime, hashlib, json, re, subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[2]
OUT=R/'audit'
BASE='396001a9ce55e0e85ddef19e405afc6a13954588'
HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True,timeout=30).strip()
LP='liber-primus/'
A=LP+'analysis/'
T0='audit/runs/T0/20260916T165851.125236Z/'
ledger=json.loads((R/LP/'LEDGER.json').read_text())
entries={e['id']:e for e in ledger['entries']}
read=set()
claims=[]
def source(path,anchor,span=4):
    lines=(R/path).read_text().splitlines(); read.add(path)
    hits=[i for i,l in enumerate(lines) if anchor in l]
    if not hits: raise ValueError((path,anchor))
    i=hits[0]; j=min(len(lines),i+span)
    return dict(commit=HEAD if path.startswith('audit/') else BASE,path=path,lines=f'{i+1}-{j}',excerpt='\n'.join(lines[i:j]))
def c(n,claim,kind,path,anchor,deps,assumptions,scope,limits,impact,next_check,ids=(),evidence=(),also=(),status='SOURCE_CHECKED'):
    sources=[source(path,anchor)]+[source(*s) for s in also]
    es=[entries[i] for i in ids]
    ev=list(dict.fromkeys([path]+list(evidence)+[s['path'] for s in sources[1:]]))
    for e in es:
        v=e.get('evidence') or []
        if isinstance(v,str):v=[v]
        ev.extend(v)
    record=dict(id=f'C-{n:03}',claim=claim,kind=kind,source=sources[0],additional_sources=sources[1:],
        depends_on=[f'C-{i:03}' for i in deps],assumptions=assumptions.split('|'),
        tested_scope={'T1':'Source and existing-record inspection only; no research rerun.',
                      'reported_or_source_scope':scope,
                      'inherited_ledger_bounds':[{'id':e['id'],'status':e.get('status'),'coverage':e.get('coverage'),'not_covered':e.get('not_covered'),'positive_control':e.get('positive_control')} for e in es]},
        not_tested=limits.split('|'),reproduce_command=None,expected_result=claim,
        observed_result='Source states or implements the cited claim. Historical measurements are not independently reproduced in T1.',
        evidence_paths=list(dict.fromkeys(ev)),status=status,
        impact_if_wrong=impact,next_check=next_check,inherited_ledger_ids=list(ids),
        provenance_note='Generated summaries, ledger rows and results prose are derived records, not independent replications.')
    claims.append(record)

c(1,'The pinned unsolved stream contains 12,956 rune indices with SHA-256 023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585.','data',LP+'PROBLEM.json','"ciphertext_identity"',[],
  '29-symbol mapping is appropriate|Non-rune removal and final-two-segment exclusion select the intended object',
  'Raw input hashes recorded in T0; normalised stream identity not executed there.',
  'Independent parser|Original-image page scope', 'All comparisons and coverage denominators depend on this object.',
  'T2: independently parse a preserved input copy, compare index hash and retain page boundaries.',evidence=[T0+'inputs.json',A+'run_stats.py',LP+'src/lp/gematria.py'])
c(2,'The apparent 55/56 unsolved-page mismatch is explained in R19 by runeless image p50: image p51–55 maps to segments 50–54; p56/57 to 55/56.','data',A+'round19/T2/RESULTS.md','`linemap.py` maps',[1],
  'R19 image labels and source assets are correctly identified|Discarding empty segments does not discard another useful channel',
  'R19 reports 57 textual segments / 58 images and 604 canon lines; dossier names image pages 0–55.',
  'Independent image-to-segment map|Direct inspection of p50|All header/ornament content', 'Off-by-one mapping can misassign crops, solved status and per-page evidence.',
  'T2: verify this existing explanation from filenames, original images and parser output before alleging a missing page.',
  also=[(LP+'SOLVERS-DOSSIER.md','**unsolved Liber'),(A+'run_stats.py','def load_pages'),(A+'round19/T1/RESULTS.md','no entry for image p50')], evidence=[A+'round19/T2/linemap.py',A+'round19/T2/out_linemap.json'])
c(3,'Community transcriptions agree rune-for-rune, but the dossier also says they share a 2017 ancestor.','data',LP+'SOLVERS-DOSSIER.md','- **Transcription is correct.**',[1,2],
  'Compared lineages cover the same regions|Shared-source copying can preserve shared errors',
  'Dossier reports 13,136/13,136 agreement and spot checks; explicitly not a fresh independent reread.',
  'True image transcription accuracy|Independent ancestry of copies', 'Agreement alone cannot certify the data used in every statistical rejection.',
  'T2: source ancestry map and targeted image checks; separate agreement from correctness.',evidence=[A+'transcription/crossdiff.py'])
c(4,'R19 per-rune controls report 180/180 solved LP2 glyphs correct and 450/450 O/A/AE disputed sites upheld.','measurement',A+'round19/T1/RESULTS.md','## 0.',[2,3],
  'Solved-page glyph identities are externally correct|Labels transferred from other canon occurrences do not perpetuate class-wide mistakes',
  'Leave-one-page-out bitmap bank; labelled consensus from other corpus positions; reports 99.6346% corpus agreement, not blind independent ground truth.',
  'T1 rerun of vision controls|Unknown glyph classes and correlated mistakes|LP1 typeface transfer',
  'Newer evidence narrows older vision limitations but cannot be accepted solely from the headline.',
  'T2: inspect bank-label ancestry, held-out controls and unresolved glyphs; distinguish corpus agreement from accuracy.',
  ids=['T1-01','T1-03','T1-04','T1-05'],also=[(A+'round19/T1/RESULTS.md','### 2.4 Classification')])
c(5,'R19 forced-alignment analysis reports at most one insertion and one deletion at 95% confidence.','measurement',A+'round19/T2/RESULTS.md','**the indel bound**',[2,3,4],
  'Injected single errors model actual transcription failures|Detection/localisation power supports the confidence bound|Canon-conditioned templates do not hide correlated errors',
  '13,121 slots, 13,725 gaps, 604 lines; 26 flags adjudicated as segmentation; 15 illuminated slots outside slot coverage.',
  'Multi-indels|Whole-line omissions|Correlated segmentation errors|Independent statistical derivation of upper bound',
  'An overstated error ceiling can falsely certify doublet and decode robustness.',
  'T2: reconstruct bound from retained rows and controls; T4/T5: propagate permitted error classes.',
  ids=['T2-INDEL'],evidence=[A+'round19/T2/PREREG.md'])
c(6,'The 19 shortlisted separator disagreements are reported resolved in favour of canon; whole-book boundary-position disagreements remain.','measurement',A+'round19/T2/RESULTS.md','**A-05 / B-23',[2],
  'Dot extraction and line-to-image assignment are valid|Boundary attribution is distinguished from missing marks',
  '19 shortlisted lines; 604-line audit, 580/604 position-exact; 24 boundary-attribution disagreements not re-attributed.',
  'Independent image review|Boundary re-attribution|Ledger threshold completion',
  'Separator-sensitive algorithms need preserved uncertainty even when rune-only tests pass.',
  'T2: map those 19 cases and 24 residual lines; later metadata task traces thresholds without inventing them.',ids=['A-05','B-23'],evidence=[A+'round19/T2/PREREG.md'])
c(7,'The images are reported byte-identical to archived onion7 originals: 56/56 SHA-1 matches.','data',LP+'SOLVERS-DOSSIER.md','original onion7 release',[2],
  'Archive manifest represents intended release|Byte identity is not proof of absence of a payload',
  '56 original image comparisons claimed; ordinary test_provenance.py checks manifest and only local pages 0,1,2.',
  'T1 byte verification|Independent archive provenance|Solved-image source chain',
  'Incorrect image identity undermines visual audits and forensic comparisons.',
  'T2: separate raw-byte checks, acquisition provenance and image-to-transcription mapping.',evidence=[A+'stego/provenance.json',LP+'tests/test_provenance.py'])
c(8,'The inherited validation script passes five selected-word page checks, not complete expected plaintext comparisons.','implementation',LP+'tests/validate.py','SOLVED =',[1],
  'Keyword presence is useful partial evidence but cannot guarantee complete decoding',
  'T0: 5/5 checks passed; five LP1 entries, substring label selection and scorer-driven transforms/interrupters.',
  'Full expected rune arrays|Every solved page|Independent expected plaintext',
  'The advertised trust anchor does not by itself establish all-solved-page correctness.',
  'T3: inventory every known solved page, then full-rune fixtures from separately checked sources.',evidence=[T0+'01-validate.stdout.txt'],also=[('README.md','solved page**')],status='REPRODUCED')
c(9,'The standalone reproduction suite covers seven named pages but also asserts selected words and lengths, using shared generated code and source data.','implementation','analysis/reproduce/README.md','Last run:',[8],
  'Copied cipher specification and shared data may share errors|No imports from lp is only one dimension of independence',
  'Five LP1 plus LP2 56/57; generated from one template; extra totient/interrupter coverage exists outside validate.py.',
  'T1 execution|Complete independent expected outputs|Exhaustive solved-page inventory',
  'Avoid both overclaiming all-page coverage and wrongly claiming the repository has only five-page coverage.',
  'T3: map assertions and fixtures in both suites; retain AN END tail/interrupter distinction.',evidence=['analysis/reproduce/build_reproduce_scripts.py','analysis/reproduce/reproduce_page_56_an_end.py',LP+'tests/test_rig.py'])
c(10,'T0 oracle self-test accepts its correct synthetic key and rejects its constructed wrong key.','measurement',LP+'verify_solution.py','def selftest',[8],
  'Same generator/decoder assumptions may conceal shared defects',
  'T0: 3 planted 130-rune pages; same seed/key resets each page; selftest bypasses actual ciphertext hash and trust-anchor call.',
  'Real candidate correctness|General false-positive/false-negative rate|Independent plants',
  'A passing smoke test is narrower than a reliable candidate adjudicator.',
  'T4: independent plants through the full submission path, positive and negative controls.',evidence=[T0+'02-oracle-selftest.stdout.txt'],status='REPRODUCED')
c(11,'The oracle self-test constructs a constant wrong key by reinitialising Random(4242) at each symbol.','implementation',LP+'verify_solution.py','K_wrong =',[10],
  'Identical initial RNG state returns the same first value',
  '4096 calls each use a newly seeded generator; T0 observed rejection of this control.',
  'Impact on real false acceptance|Varied wrong keys', 'One easy negative may give misleading reassurance.',
  'T4 repair task: measure constant versus varied controls before a separate patch; preserve constant case.')
c(12,'judge_keystream starts every supplied segment at offset zero under one shared key.','implementation',LP+'verify_solution.py','def judge_keystream',[2,10],
  'Per-segment reset is only one candidate model',
  'Rigid/beam and both signs; o=0 each segment; default submission tests first six segments.',
  'Continuous-key offsets|Section resets|Per-page keys', 'Correct candidates outside this interface could be missed.',
  'T4: test reset, continuous and per-page cases independently; unsupported models stay unsupported.')
c(13,'The legacy beam permits a skipped key symbol only when it would reproduce the preceding ciphertext rune.','implementation',A+'campaign18_skip/skipdecode.py','validity: each skipped',[10],
  'One-draw rejection model|max_skip and beam pruning are sufficient for tested key structure',
  'T0 benchmark passes inherited skip/rewrite plants; R18 reports skip_by_two failures at ~25.8% recovery.',
  'Arbitrary drift|All key families/lengths|General rewrite recovery', 'Legacy negatives must retain a transition-model conditional.',
  'T4: separately identify legacy and newer decoder call sites, then independent transition plants.',ids=['L7-B-BEAM-ENVELOPE'],evidence=[A+'round18/L7-redteam/out_b1.json',A+'round18/L7-redteam/RESULTS.md'])
c(14,'The English scorer can reject correctly recovered non-English or abbreviated plaintext.','measurement',A+'round18/L7-redteam/RESULTS.md','### A.1 The scorer-language',[10,13],
  'Plant text/register and key family represent the stated panel|RNG replicates are not independent language corpora',
  'R18: 10 registers x 4 lengths x 12 replicates, SHA counter family; Latin power .33 and Welsh/vowel-dropped .00 at L120 reported.',
  'Other registers|Other generators|T1 reproduction of power', 'A no-hit result can be an adjudicator blind spot.',
  'T4: verify correct-key rune recovery and score separately for each claimed register.',ids=['L7-A-SCORER-ENGLISH-ONLY'],evidence=[A+'round18/L7-redteam/out_a1.json',LP+'src/lp/score.py'])
c(15,'The oracle selects across signs and decoders but calibrates its shuffle null using only beam/sign -1 on the first segment.','implementation',LP+'verify_solution.py','def null_band',[10,12,13,14],
  'The selected statistic requires a null that matches its entire selection process|Shuffling may erase relevant anti-repeat structure',
  'NULL_N=200 (selftest 60); best-per-page over four choices; >=2 passing pages and English threshold.',
  'Full-procedure false acceptance|Page/candidate dependence|Matched-structure nulls',
  'Reported margins are not yet a measured error guarantee for the full selection procedure.',
  'T4: replay all selection choices on negative controls; distinguish two-page policy from statistical independence.',also=[(LP+'verify_solution.py','def judge_keystream'),(LP+'verify_solution.py','c3 = best')])
c(16,'threshold_for accepts segment_len but does not use it; its default extreme-value constants are tied to a particular historical calibration.','implementation',LP+'benchmark/null.py','def threshold_for',[14,15],
  'Tail model transfers only with justified score/length/selection conditions|Trial count must match the selected statistic',
  'Defaults mu=-7.2517 beta=.0725; two historical maxima described; function ignores length.',
  'New calibration|Effective trial counts|Other decoders/registers', 'Wrong thresholds can miss valid candidates or flag noise.',
  'T4: measure full selection null by length/mode and track offsets versus scored survivors.',ids=['L7-C-THRESHOLD-CALIBRATION'],evidence=[A+'round18/L7-redteam/out_c1.json',A+'round18/L7-redteam/out_c4.json'])
c(17,'R19 driftbeam reports recovery of legacy failure cases, with a materially raised wrong-key null and configuration limits.','measurement',A+'round19/I1/RESULTS.md','**G-FIX**',[13,16],
  'Planted cases represent named transitions|Reported scores and calibration correspond to the exact mode/penalties',
  '20/20 gate cells reported; lam>=8 0/2000 wrong keys reach -5.5, lower penalties fail; keyskip2 is not universal.',
  'T1 rerun|Combinations beyond tested cells|Integration into legacy oracle',
  'An old decoder limitation cannot be attributed wholesale to later repaired sweeps.',
  'T4: per-campaign instrument/version map and independent mode-specific controls.',ids=['I1-02','I1-03','I1-07'],evidence=[A+'round19/I1/driftbeam.py',A+'round19/I1/out_fix.json'])
c(18,'R19 nine-register adjudicator reports power >=.90 in 27 cells, but its speed gate failed and panel calibration is separate from legacy English scoring.','measurement',A+'round19/I2/RESULTS.md','**G-POWER**',[14,16,17],
  'Held-out text is disjoint from training|Panel-max calibration includes correlated model selection',
  '9 registers x L120/240/400, minimum reported .92; speed 4.79x against 3x gate.',
  'All languages|Raw end-to-end key search survival|T1 power reproduction',
  'New detector capability is finite and must not be silently credited to old runs.',
  'T4: check training/test separation, mode/register null and actual sweep adoption.',ids=['I2-MULTI-REGISTER-ADJUDICATOR','R19-I3-NULLS'],evidence=[A+'round19/I2/adjudicate.py',A+'round19/I3/RESULTS.md'])
c(19,'R21 withheld automatic HIT certification after its held-out proxy failed the frozen catch-rate requirement.','measurement',A+'round21/SYNTHESIS.md','The seal **failed',[17,18],
  'Planted hallucinations and genuine controls approximate future failure modes',
  'R20 real-mode caught 15/45; R21 best genuine-safe catch .80 below .90, fresh surrogate false-reject .167 above .10.',
  'Universal solution certification|T1 re-evaluation of retained controls',
  'A bar-clearing score cannot be treated as a confirmed solve, even under newer tools.',
  'T4: audit real-mode acceptance separately from known-plaintext recovery; retain flag-only policy.',ids=['R21-L1-SEAL','R20-HITFN-RECOVERY-GATE'])
c(20,'The unsolved stream is reported to contain 86 equal adjacent pairs: 86/12,955 flattened or 86/12,901 within pages.','measurement',A+'round12/D2/RESULTS.md','0.664% over 12,955',[1,2,3,5],
  'Rune classification and ordering correct|Boundary/normalisation convention explicit',
  'R12 D2 and R18 L7-C report same count; D2 reimplements counting but shares rune mapping and input.',
  'T1 independent recomputation|Disputed glyph sensitivity|Boundary-map validation',
  'The main mechanism argument rests on this statistic.',
  'T5 after T2: independently compute counts per image/segment/line and perturb uncertain glyphs.',ids=['R12-D2','L7-C-HEADLINE-STATS'],evidence=[A+'round12/D2/recompute.py',LP+'src/lp/stats.py'])
c(21,'IoC x 29 is reported as .999874 and monogram Shannon entropy as 4.856504 bits.','measurement',A+'round18/L7-redteam/RESULTS.md','**0.999874**',[1,2,3],
  'Marginal summaries are not tests of all higher-order structure|Denominators use the same data version',
  'Aggregate monogram counts in inherited results; per-page variation also described.',
  'T1 independent calculation|All higher-order structure|Unique generating mechanism',
  'Near-uniform marginals alone cannot establish ciphertext randomness or cipher identity.',
  'T5: independent formulas and per-page/section tables with explicit scope.',ids=['L7-C-HEADLINE-STATS'],evidence=[A+'round12/D2/recompute.py'])
c(22,'For independent plaintext/key increments in an additive model, the expected doublet probability is a weighted sum bounded by the minimum plaintext increment probability.','interpretation',A+'round10b/B4-otp-steelman/b4_identifiability.py','P(c_i = c_{i-1})',[20],
  'Additive mod-29 construction|Independence of increments at the relevant positions|Population model, not a deterministic lower bound on every finite sample|Mixtures/position dependence handled explicitly',
  'Code states convolution inequality and compares large-corpus empirical floors to observed finite stream.',
  'Finite-sample tail bound|Unknown plaintext law|Correlated/nonstationary key and text',
  'Misusing an expectation bound as an impossibility proof rejects too many models.',
  'T5: write formal assumptions and a hand-checkable derivation; separately assess sample uncertainty and alternative models.',evidence=[A+'round12/D2/g3_floor_probe.py'])
c(23,'Empirical minimum-increment floors are reported as 1.38–1.83% on four English corpora, later 0.972% for the tested German register.','measurement',A+'round18/L7-redteam/RESULTS.md','**German**',[22],
  'Test corpora/normalisation represent candidate plaintext registers|Data versions match historical inputs',
  'Four English books plus nine register samples across five languages; not every natural-language text.',
  'Universal natural-language bound|Other preprocessing and lengths|T1 recomputation',
  'The minimum over selected books cannot justify a universal plaintext exclusion.',
  'T5: pin corpus hashes, window selection and uncertainty; separate empirical minimum from theorem.',ids=['L7-C-G3-FLOOR-EXTENDED'],evidence=[A+'round12/D2/g3_floor_probe.py','macos-data-checks.json'])
c(24,'The README asserts a pinned ~83% soft anti-repeat filter over a memoryless base.','mechanism','README.md','project pinned what produces it',[20,21,22,23],
  'Candidate mechanism family includes the real process|Parameter fit is identifiable|Suppression ratio is not automatically rejection-loop probability',
  'Inherited controls show selected filters can produce a deficit; R18 reports empirical lag-1 suppression 80.746%.',
  'Unique mechanism identification|Alternative encodings/orderings|Uniform mechanism across pages',
  'Treating the mechanism as established preselects decoder transitions and can foreclose valid alternatives.',
  'T5: distinguish observed deficit, fitted parameter and mechanism; compare prespecified alternatives.',ids=['VERDICT-OTP-CLASS','R18-L2-A-LOCUS'],evidence=[A+'round18/L7-redteam/RESULTS.md'])
c(25,'The dossier says flat IoC is reachable only by a full-length keystream; later B4 reports finite detection limits around period 400.','interpretation',LP+'SOLVERS-DOSSIER.md','Perfect IoC flatness',[21],
  'Detection floor depends on plaintext/window/key distribution and chosen statistic',
  'B4 tests a discrete period ladder with 60 trials per period and one uniform-null threshold; p*=400 is a tested-grid result.',
  'All periodic keys|Exact universal period cutoff|Information-theoretic proof',
  'A stale full-length necessity claim artificially narrows the problem.',
  'T5/T6: trace B4 G2 simulation assumptions and report a sensitivity bound, not full-length necessity.',evidence=[A+'round10b/B4-otp-steelman/b4_identifiability.py',A+'round10b/B4-otp-steelman/b4_results.json'])
c(26,'The headline OTP-class verdict is inferred from a limited statistical battery failing to separate an external-pad model from a derived-key model.','interpretation',LP+'PROBLEM.json','"statement": "OTP-class',[20,21,24,25],
  'Failure to distinguish named models does not exhaust cipher families|Finite-battery similarity is not information-theoretic equality|Filtered external-pad secrecy needs its own model',
  'B4/G5 six statistics reported max |z|=1.60; D3 reports recovery of a planted derived key.',
  'Universal indistinguishability|Actual LP2 key origin|Exhaustive alternatives',
  'This is the repository headline and controls whether further work is considered possible.',
  'T5/T6: separate formal secrecy statements, model non-identifiability and empirical test power.',ids=['VERDICT-OTP-CLASS','VERDICT-UNSOLVABLE-BY-DESIGN'],evidence=[A+'round12/D3/RESULTS.md',A+'round10b/B4-otp-steelman/b4_results.json'])
c(27,'The dossier infers a continuous keystream and no resets from suppressed boundary repeats.','mechanism',LP+'SOLVERS-DOSSIER.md','## 6b.',[2,20,24],
  'Filter state continuity implies key-state continuity (not established)|Boundary sample has discriminatory power',
  'R12 reports zero repeated pairs at 54 page joins; STRUCTURE-FINDINGS asserts no resets.',
  'Key reset inference|Boundary-specific uncertainty|Separate filter/key state models',
  'Could wrongly exclude page-reset or section-reset attacks and conflicts with oracle reset convention.',
  'T5: distinguish filter state from key phase, calculate boundary power before choosing a reset model.',also=[(A+'STRUCTURE-FINDINGS.md','## 2.'),(LP+'verify_solution.py','def judge_keystream')])
c(28,'Broad autokey exclusion is asserted, although inherited supplements make it conditional on plaintext statistics and finite feedback families.','search_bound','README.md','refuted**, not merely',[13,14,20,21],
  'The tested diagonal signature applies to the specific recurrence and plaintext|A finite feedback basis covers only itself',
  'R12-C1 finite k-history basis; B4 supplement explicitly notes ct-autokey differences equal plaintext only for its recurrence.',
  'All autokey/feedback recurrences|Non-English/nonlinguistic payloads|Other transitions and resets',
  'An overbroad closure can suppress a whole class without adequate coverage.',
  'T6: trace each recurrence, key/history space, transition and adjudicator register through controls.',ids=['R12-C1','D-04'],evidence=[A+'round10b/B4-otp-steelman/b4_autokey_audit.py',A+'round12/C1/feedback.py'])
c(29,'The dossier groups substitution and homophonic ciphers as excluded by IoC preservation.','interpretation',LP+'SOLVERS-DOSSIER.md','Substitution / homophonic',[21],
  'Bijective substitution and many-to-one/homophonic mappings must not be conflated',
  'D-03 explicitly leaves surjective 29-to-k search open; simple substitution invariants have narrower scope.',
  'All homophonic maps|Full search with language/model controls',
  'A bijection invariant does not alone close broader symbol mappings.',
  'T6: formalise separate transform families and match each to the cited evidence.',ids=['D-03'])
c(30,'The dossier rejects transposition-only as doublet-transparent.','interpretation',LP+'SOLVERS-DOSSIER.md','**Transposition-only**',[20,21],
  'Permutation preserves monogram counts but its effect on adjacency depends on order|English plaintext marginal assumptions remain explicit',
  'No new permutation counterexample run; source-level rationale flagged for mathematical review.',
  'All orderings|Other plaintext distributions|Mixed substitution/transposition',
  'An invalid invariant can close a family for the wrong reason even if another bound applies.',
  'T6: separate monogram invariance from adjacency; inspect tested ordering families before any new search.',evidence=[A+'crypto_rigor.py'])
c(31,'The README treats running keytexts as closed by exhaustion over ~200 texts; later R26 records a distinct 33-text slice only partially run.','search_bound','README.md','closed **by exhaustion',[12,13,14,15],
  'Enumerated texts, offsets and truncation are the tested keyspace|Skip/rewrite control does not cover all transition variants',
  'R26 B: 33 texts, keyskip1/keyskip2, four offsets/text, 3/9 pages complete; reported 1,562 decodes.',
  'All texts|All offsets/pages|Other registers/constructions',
  'Finite corpus negatives cannot certify an entire keytext family.',
  'T6: versioned coverage map across original sweeps and R26, using actual completed rows.',ids=['B-16','R12-C2','R26-B-KEYTEXT-RUNNINGKEY-SKIPAWARE'],evidence=[A+'round12/D1_redteam/RESULTS.md',A+'round26/SYNTHESIS.md'])
c(32,'Seeded PRNG exclusions cover specific generators and seed fractions; R25 reports only 0.5015% of one Py2.7 random29 space.','search_bound',A+'round25/SYNTHESIS.md','cumulative 2³² coverage',[13,14,16,17,18,19],
  'Generator emulation matches historical runtime|Disjoint completed seeds counted correctly|End-to-end control survives selection',
  'R25 reports 21,539,647 words, offset 0, pair decoder; old B-21 partial coverage and different detector remain distinct.',
  'Remaining >99.49% of named space|Other PRNGs/reducers/offsets|T1 checkpoint recount',
  'Huge decode totals are not equivalent to complete keyspace coverage.',
  'T6: verify checkpoint arithmetic and generator/transition/register tuple before deciding on any rerun.',ids=['B-21','B-01','R25-COMPUTE-TAIL-CHUNK1'])
c(33,'R26 semantic-seed lane reports 4,274 rows as 100% of 323 seeds x 7 generators x 2 decoders.','search_bound',A+'round26/SYNTHESIS.md','**C** | **Semantic-seed**',[17,18,19],
  'Effective enumeration may exclude unsupported combinations|Screen statistic and threshold must share a scale',
  'Source table reports 4,274 rows; nominal product is 4,522. No raw-row recount in T1.',
  'Explanation for missing nominal combinations|Completed coverage|Screen-versus-pmax comparability',
  'Latest high-level coverage can overstate completion if exceptions are not explicit.',
  'T6: reconcile nominal cross-product, deduplication/exclusions and actual records; do not infer a failed cipher from a count discrepancy.',ids=['R26-C-SEMANTIC-SEED-ZOO','R26-D-REDTEAM'])
c(34,'R26 generator lane describes planned ~747-seed coverage while explicitly recording unfinished baseline execution.','search_bound',A+'round26/SYNTHESIS.md','Lane A interim null',[17,18,19],
  'Plan counts are distinct from completed counts|Interim artifacts are not final results',
  'Prior-dense 347 seeds said complete; dense-from-zero partial; ledger partially-run.',
  'Latest raw finalisation state|All 2^32/2^64 tails',
  'Treating plans as results inflates tested coverage.',
  'T6: inspect retained checkpoints/control finalisation and count only completed cells.',ids=['R26-A-GEN-SWEEP-FIRST-FIRE'])
c(35,'The public-pad branch remains partial and detector-dependent; Marsaglia records 77/756 units and limited prefilter survival.','search_bound',LP+'LEDGER.json','"id": "B-13-MARSAGLIA"',[12,13,14,16],
  'Byte provenance and builder order match|Prefilter survival is part of search power',
  'Recorded ~1.54e9 offsets; 77/756 units; survival .5625 in 16 controls; missing manifest/checksum references.',
  'Unfinished builders/units|Original 1995 pressing provenance|Models outside English legacy beam',
  'Zero hits over a partially sensitive pipeline cannot eliminate every public pad.',
  'T6: restore exact input manifest evidence if available, then inspect survival/selection and completed scope.',ids=['B-13-MARSAGLIA','R19-C2-MARSAGLIA-GATE','R17-PUBLIC-PAD'])
c(36,'Ledger validation checks declarations and paths; zero unsound-negative flags does not validate the experiments.','implementation',A+'handoff/validate_ledger.py','bad = len(errors)',[],
  'Recorded positive_control strings reflect real runs (not checked by validator)',
  'T0 strict: 0 errors, 18 warnings, 27 notes. Missing thresholds and evidence paths are warnings; absent evidence list yields no missing-path warning.',
  'Scientific adequacy of controls|Preregistration chronology|All schema/error handling',
  'A green metadata check can coexist with unavailable evidence or overbroad claims.',
  'T1 account for each warning; later validation task tests malformed/missing evidence without editing historical entries.',evidence=[T0+'05-ledger-strict.stdout.txt'])
c(37,'run_t0.py records child failures but has no aggregate failure exit at normal completion.','implementation','audit/tools/run_t0.py',"record['exit_code'] = code",[36],
  'Wrapper reaches normal end without another uncaught exception|Caller uses wrapper exit rather than per-command JSON',
  'Source lines 119–136 record statuses then end after print; T0 manifest has five actual zero exits, so no failed child was hidden in the recorded baseline.',
  'Runtime fault injection|Timeout/launch-error aggregation|Impact measurement and regression test (deferred by instruction)',
  'Automation could report success despite a failed child; original raw child results remain available.',
  'Later repair task: inject success/nonzero/timeout/launch-error stubs, measure parent exits and preserved logs, add regression test before a separate fix.',evidence=[T0+'manifest.json'])
c(38,'The four L7 warnings about thresholds not fixed in advance arise from missing/null metadata despite local PREREG claims.','data',LP+'LEDGER.json','"id": "L7-A-SCORER-ENGLISH-ONLY"',[36],
  'Present prereg prose alone cannot prove historical ordering|Operative archive statistic may differ from prereg flag',
  'Four threshold_fixed_in_advance values are null; PREREG A/B/C rules exist. Four entries also have no evidence list.',
  'Commit/time chronology|Whether all operative thresholds were prespecified',
  'Neither auto-filling true nor labelling the experiments post-hoc is justified yet.',
  'Later provenance/metadata task: compare PREREG, implementation, outputs and history, especially archive contrast selection.',
  ids=['L7-A-SCORER-ENGLISH-ONLY','L7-A-ARCHIVE-RESCORE','L7-B-BEAM-ENVELOPE','L7-C-THRESHOLD-CALIBRATION'],evidence=[A+'round18/L7-redteam/PREREG.md',A+'round18/L7-redteam/RESULTS.md'])
c(39,'A-05, B-23 and T2-INDEL are negative ledger entries without recorded threshold strings, although T2 has prereg/control rules.','data',LP+'LEDGER.json','"id": "T2-INDEL"',[5,6,36],
  'A control gate and an outcome decision rule are distinct|Metadata omission does not itself disprove result',
  'Three missing-threshold warnings; T2-INDEL has threshold_fixed_in_advance=true but no threshold text.',
  'Historical preregistration order|Exact mapping from each decision to its rule',
  'Cannot reconstruct the declared negative solely from the ledger.',
  'Later metadata task: link exact operating rules and control evidence without inventing a threshold.',ids=['A-05','B-23','T2-INDEL'],evidence=[A+'round19/T2/PREREG.md'])
c(40,'R18 attributes image production to a two-stage Ghostscript/ImageMagick pipeline and compares 11 fonts, but three cited inspection artifacts are missing.','interpretation',A+'round18/L1-toolchain/RESULTS.md','ImageMagick, re-encoding',[7],
  'Tested encoder features uniquely identify a pipeline rather than merely match it|Candidate font bank is bounded',
  '58 file vectors, 18 pipeline and 20 chain controls reported; 11-font comparison; 493-PDF local scan.',
  'Other encoders/pipelines|Untested fonts|Source PDF identity|Missing glyph/contact sheet and per-PDF log',
  'Artifact-based generator priors should retain uncertainty rather than dictate a historical runtime.',
  'Later evidence task: inspect surviving feature/control JSON and distinguish encoder consistency from unique attribution.',ids=['G-01','B-11'])
c(41,'PGP verification is reported for 238 held files / 54 distinct messages; missing rerun log limits replay evidence but structured verification tables remain cited.','measurement',LP+'LEDGER.json','"id": "CORPUS-G-02"',[],
  'Key fingerprint and signature bytes are authenticated|Valid signature proves key control, not individual authorship',
  'Held repository messages only; all 238 reported verified; raw rerun log absent.',
  'T1 signature execution|Off-repository messages|Attribution',
  'Canonical clue/authenticity decisions need reproducible cryptographic checks.',
  'Later provenance task: inspect table status lines and scripts; reproduce only if needed for selected clues.',ids=['CORPUS-G-02'])
c(42,'The L1 GnuPG version/timestamp correction is supported by a surviving crosscheck JSON but its textual log is missing.','measurement',LP+'LEDGER.json','"id": "L1-F6-CORRECTION"',[41],
  'Duplicate files and distinct messages are not interchangeable|Armor labels do not uniquely identify software version',
  'Coverage says 192 passing files / 54 messages; correction refers to 56 version-labelled files with 54 timestamps.',
  'T1 verification of counts|Exact minor-version inference',
  'Runtime priors can inherit a wrong denominator or version conclusion.',
  'Later provenance task: reconcile structured records and denominator definitions before generator priors.',ids=['L1-F6-CORRECTION'])
c(43,'R19-G3 validates a historical Python generator but explicitly clears no keyspace; its pilot row file is missing.','search_bound',LP+'LEDGER.json','"id": "R19-G3"',[32],
  'Native reference binaries and version/wordsize vectors valid|A plumbing pilot is not a registered exhaustive search',
  '2,165 hash/8,660 stream vectors and other cases reported; 10,112-decode pilot exceeds stated 10,000 cap by 112, disclosed.',
  'Pilot raw-row replay|Untested reducers/runtimes/hash randomisation|Actual keyspace exclusion from this lane',
  'A validated emulator is an instrument, not a negative search result.',
  'T6: separate emulation vectors from later sweep coverage; resolve missing pilot only if needed.',ids=['R19-G3'],evidence=[A+'round19/G3/READY.md'])
c(44,'PROBLEM.json and other navigation documents retain old open/closed descriptions after later ledger work.','data',LP+'PROBLEM.json','"open_or_untested"',[4,5,17,18,31,32,36],
  'Generated summaries may lag source records|Newer records still need audit',
  'PROBLEM lists per-rune vision parked, KDF running and broad eliminated families; ledger includes R19/R24–R26 work.',
  'Full document-by-document reconciliation|Scientific validity of newer records',
  'Stale navigation can cause duplicate work or suppress untested work.',
  'T1 dependency summary names discrepancies; defer navigation edits until evidence checks justify them.',evidence=[LP+'LEDGER.json','AGENTS.md',LP+'FINAL-SYNTHESIS.md'])
c(45,'Image byte authenticity and render provenance are used alongside a broad no-steganography claim.','interpretation','AGENTS.md','no recoverable steganography',[7,40],
  'Authentic rendering does not by itself exclude deliberate hidden content|Finite decoder/password tests cover only their tested spaces',
  'Dossier lists appended/EXIF/LSB/carve/color/OutGuess tests; B-10 retains an open Linux OutGuess control.',
  'Every steganographic method/key|Full positive-control adequacy|T1 artifact forensics',
  'A provenance fact could wrongly close an independent information channel.',
  'T6 if relevant: enumerate forensic tests, carrier bytes and positive controls; keep provenance separate from payload absence.',ids=['B-10'],evidence=[A+'stego/STEGO-VERDICT.md'])
c(46,'PROBLEM.json lists number-theoretic keystreams and the whole number channel as eliminated while later semantic-seed compositions remain finite searches.','search_bound',LP+'PROBLEM.json','number-theoretic keystreams',[13,14,16,33],
  'Enumerated arithmetic recipes do not exhaust every use of numerical values|Direct keys, feedback and seeds are distinct',
  'Round11 synthesis and implementation offer specific transforms; R26 separately composes 323 semantic seeds with generators.',
  'All arithmetic functions/compositions|Other reset/offset/language models',
  'A phrase such as whole channel hides a finite hypothesis list.',
  'T6: trace recipe enumeration and actual detector tuple before interpreting each exclusion.',evidence=[A+'round11/SYNTHESIS.md',A+'round11/lib_numchannel.py'])
c(47,'The dossier declares fractionation excluded because it cannot produce flat IoC or the doublet deficit.','interpretation',LP+'SOLVERS-DOSSIER.md','**Fractionation**',[20,21],
  'Named Bifid/Polybius constructions and parameter ranges define tested family|Single-symbol invariants need proof for fractionating transforms',
  'Dossier cites OPEN-AVENUES; only the headline/reference is inventoried here.',
  'Formal family-wide invariant|Original lane controls and complete implementation review',
  'Generic cipher-family labels may exceed the evidence.',
  'T6: inspect cited construction-specific arguments and controls; do not accept universal exclusion from the heading.',evidence=[A+'OPEN-AVENUES.md'])

# T0 results are carried forward explicitly, not recomputed.
for n in (8,10):
    claims[n-1]['observed_result']='T0 raw logs reproduce the bounded check stated in tested_scope; T1 performed no rerun.'
# Statements retain source locations and full inherited bounds; null command means no T1 reproduction.
(OUT/'CLAIMS.jsonl').write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in claims))

# One warning record per exact T0 warning, including repeated artifact paths.
log=(R/T0/'05-ledger-strict.stdout.txt').read_text()
block=log.split('WARNINGS: 18\n')[1].split('\nNOTES:')[0]
warning_lines=[l.strip() for l in block.splitlines() if l.strip()]
assert len(warning_lines)==18
mapping={'A-05':[6,39],'B-23':[6,39],'T2-INDEL':[5,39],'G-01':[40], 'B-11':[40],
 'B-13-MARSAGLIA':[35],'R19-C2-MARSAGLIA-GATE':[35],'L7-A-SCORER-ENGLISH-ONLY':[14,38],
 'L7-A-ARCHIVE-RESCORE':[14,38],'L7-B-BEAM-ENVELOPE':[13,38],'L7-C-THRESHOLD-CALIBRATION':[16,38],
 'CORPUS-G-02':[41],'L1-F6-CORRECTION':[42],'R19-G3':[43]}
warning_records=[]
for i,line in enumerate(warning_lines,1):
    eid=re.match(r'\[([^]]+)\]',line).group(1); e=entries[eid]
    missing=line.split('evidence path does not exist: ')[1] if 'evidence path does not exist: ' in line else None
    kind='missing_artifact' if missing else ('missing_threshold' if 'no recorded threshold' in line else 'preregistration_flag_not_true')
    refs=e.get('evidence') or []
    if isinstance(refs,str):refs=[refs]
    existing=[v for v in refs if (R/v.split('#')[0]).is_file()]
    if eid.startswith('L7-'):
        existing += [A+'round18/L7-redteam/PREREG.md', A+'round18/L7-redteam/RESULTS.md']
        existing += [A+'round18/L7-redteam/'+{'L7-A-SCORER-ENGLISH-ONLY':'out_a1.json','L7-A-ARCHIVE-RESCORE':'out_a2.json','L7-B-BEAM-ENVELOPE':'out_b1.json','L7-C-THRESHOLD-CALIBRATION':'out_c1.json'}[eid]]
    if eid in ('A-05','B-23','T2-INDEL'):existing.append(A+'round19/T2/PREREG.md')
    action = ('Locate the exact retained artifact or reproducible source; do not replace it with a summary or manufacture a new historical log.' if missing else
              'Trace the exact decision rule, control and history in a later metadata/provenance task; do not fill missing fields from assumption.')
    if eid=='L7-A-ARCHIVE-RESCORE':action+=' Compare prereg raw-z flag with the operative archive-standardised contrast; its timing is not established.'
    warning_records.append(dict(id=f'W-{i:02}',original_warning=line,inherited_ledger_id=eid,claim_ids=[f'C-{n:03}' for n in mapping[eid]],category=kind,
       ledger_source=source(LP+'LEDGER.json',f'"id": "{eid}"'),threshold_present='threshold' in e,threshold=e.get('threshold'),
       threshold_fixed_in_advance=e.get('threshold_fixed_in_advance'),missing_path=missing,
       path_exists_now=(R/missing).exists() if missing else None,
       surviving_evidence=[dict(path=p,exists=(R/p.split('#')[0]).is_file()) for p in existing],
       impact='Direct replay/inspection of this artifact is unavailable; related summaries are not independent substitutes.' if missing else
       'Ledger metadata cannot alone establish a preregistered decision; absence is not proof that no rule existed.',
       disposition='ACCOUNTED_FOR_UNRESOLVED',next_action=action))
(OUT/'LEDGER-WARNINGS.jsonl').write_text(''.join(json.dumps(w,ensure_ascii=False)+'\n' for w in warning_records))
used_ids=set(i for c in claims for i in c['inherited_ledger_ids'])
(OUT/'runs/T1/ledger-extract.json').write_text(json.dumps([entries[i] for i in entries if i in used_ids],ensure_ascii=False,indent=2)+'\n')
# Snapshot file existence and checksums; hashes are identity metadata, not validation.
for c in claims:
    read.update(s['path'] for s in c['additional_sources']); read.add(c['source']['path'])
metadata=[]
for p in sorted(read|{LP+'LEDGER.json',T0+'manifest.json','audit/tools/run_t0.py'}):
    b=(R/p).read_bytes();metadata.append(dict(path=p,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b)))
(OUT/'runs/T1/source-manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
(OUT/'runs/T1/inventory.json').write_text(json.dumps(dict(recorded_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),baseline_commit=BASE,working_commit=HEAD,
 claim_count=len(claims),warning_count=len(warning_records),warning_categories={k:sum(w['category']==k for w in warning_records) for k in ['missing_artifact','missing_threshold','preregistration_flag_not_true']},
 distinct_missing_paths=len(set(w['missing_path'] for w in warning_records if w['missing_path'])),
 t0_repeated=False,research_executed=False,wrapper_failure_injection=False,source_excerpt_files=sorted(read)),indent=2)+'\n')
# Structural verification of audit artefacts, not scientific tests.
ids={c['id'] for c in claims}
assert len(ids)==len(claims)
assert all(set(c['depends_on'])<=ids for c in claims)
assert all(set(w['claim_ids'])<=ids for w in warning_records)
assert not any(w['path_exists_now'] for w in warning_records if w['missing_path'])
assert sum(w['category']=='missing_artifact' for w in warning_records)==11
print(f'Created {len(claims)} claims; accounted for all {len(warning_records)} warnings (11 artifact, 3 missing threshold, 4 preregistration flag).')
print('No research code imported/executed; no T0 rerun; no fault injection or regression test.')
