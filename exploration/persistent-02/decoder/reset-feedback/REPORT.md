# R01 — same-seed feedback restarted at fixed major marks

Completed2026-09-17; no solved candidate. The actual full-body score ranks first among the actual+19 fixed comparator panels under both frozen scorers, but only by small margins. Complete leading outputs are incoherent. This is a modest conditional ranking departure requiring that qualification, not a global probability or a blanket negative.

| Frozen scorer | Fullbody fit | Best comparator fullfit | Fullfit rank | Prefixfit rank | Frozen continuation score | Continuation rank |
|---|---:|---:|---:|---:|---:|---:|
| P03 |−4.5826721647|−4.5914899139|1/20|7/20|−4.8770685796|1/20|
| Complementary |−5.2900318537|−5.2969230388|1/20|5/20|−6.0180337281|9/20|

All four actual selections choose k8 but distinct seeds. Fullfit P03 seed[9,15,21,5,25,8,21,26]; complementary[9,15,8,7,25,22,15,27]. Prefix-selected P03[21,20,21,7,25,8,13,15]; complementary[9,28,21,21,10,23,3,15]. Fullfit and continuation are separate statistics, not selected against one another. Prefix249 determines the seed andk; remaining467runes receive that unchanged seed, with the prescribed resets and continuous scorecontext. Every complete selected output is retained in leaders.json and was read. English-like fragments occur inside otherwise incoherent strings; no oracle submission is warranted as a solution claim.

## Implementation and validation

model.py assembles cyclic triple factors plus reset-crossing pairs; solver.py adapts reviewed C02 conditional suffix Viterbi bounds. DERIVATION.md states the recurrence and admissibility argument. Same seed is restarted at body indices141,262,284,337,381,421,518. A reset must follow an explicit separator; other reset types are rejected. No literal-F branch exists. Only k5–8 is fitted on actuals; no new model, seed band, punctuation rule or training data.

Own checks.json:140 independent scalar recurrence/factor trials,732511 exhaustive assignments at k2/3/4 with direct vector recurrence scores,9 capped/uncapped maximum containment checks. All pass. Frozen44plants from eight existing A07 sources are recovered exactly under both models:88/88, each optimum certified within1e-10. These sources were used in earlier research and are not an untouched population sample. Plant records include fullplaintexts, seeds, scores, factors and source coordinates via frozen inputsource links.

Fresh reviewer /root/p02_section independently checked1440 recurrence/factor cases, dense arbitrary factor exhaustive k2/3 cases and cap containment; reconstructed44plant ciphers,20 actual/comparator panels and54000 model cells; independently replayed representative16paths and adapter semantics. Clearance was recorded BEFORE actual optimization. Evidence lives in section/review-feedback; REVIEW-CLEARANCE.md links the records. This worker authored R01 and did not count their own checks as fresh review.

All320 actual/comparator/model/horizon/k cells completed and certified maxima within1e-10, with saved lower/upper bounds. No resource-capped unresolved cell remains. This is float64/tolerance certification, not interval arithmetic; alternatives are encountered feasible paths, not globally ranked n-best paths or a tie census. Source/checksum pins, numeric modeltables and input freeze are in inputs.json. Complete factors/baselines and outputs are in actual/*.npz and *.json. Selection and rank calculations are in summary.py and summary.json; leaders.json gives all four complete actual selections.

## Coverage and consequence

The tested construction is uninterrupted sum-plaintext/sign-minus feedback modulo29, one shared k5–8seed reset at the seven frozen body major marks, with two fixed English-register local scorers. Comparators reuse B05 wholepacket panels sliced13, conditioned on F-sites/equalitymask; no histogram or first-rune conditioning is claimed. Twenty panels support only coarse conditional comparison, especially after preceding related experiments. Cross-model continuation is inconsistent; tiny fullfit departures do not identify a plaintext or establish intended construction.

Do not infer that all feedback, all resets, all seeds or other languages are excluded. Within this exact objective and construction, increasing beam width cannot improve the certified optimum. C's separate literal-F-reset pilot covers a different transition relation. No new sweep/model/key expansion is proposed from these outputs alone.

## Reproduction and logs

Run scripts with .venv/bin/python through exploration/persistent-02/run_logged.py using owner exploration/persistent-02/decoder/reset-feedback, single numerical threads and <=900second chunks. Saved run manifests give full commands, source snapshots, hashes, stdout/stderr and outcomes. Executed labels: freeze-inputs; core-checks; plants-all; plant-summary; actual-panel00; comparator-panels01-10; comparator-panels11-19; actual-summary; read-leaders. The actual driver refuses execution without a recorded fresh-review clearance; all producer scripts refuse overwriting existing result paths. Summary scripts aggregate existing records without rerunning searches.

Post-run independent aggregation review also passed: section/review-feedback/reset-summary-review.json reconstructs80 panel selections from320cells, every bound/tied rank count, all certification flags, and prefix-only selection. No search or result values changed.
