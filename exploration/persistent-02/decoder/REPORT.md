# PERSISTENT-02 B01–B06 checkpoint

Exact search exposes beam pruning on the selected section, but produces no credible plaintext. Complete historical keyed references decode exactly under every compared width. Fresh controls separate two problems: a prematurely committed prefix can corrupt continuation, while some internally wrong plaintexts remain preferred by the frozen local score even after more text is supplied.

## Scope and overlap

| Item | Prior work | This assignment |
|---|---|---|
| Periodic fixed-key exact optimization | PERSISTENT-01 `worker-c/p09_viterbi.py` and `p10_kbest.py`/`frozen_kbest.py` already implement this | Reused for paired checks; **not** claimed newly invented |
| Old discovery P09/P10 | P09 first16 clue keys on0/17/49/55; P10 clue IDs16–31 on saved allpages data, separate-page objectives | New unit is complete section0–2, body716 or whole729 runes, explicit punctuation and uninterrupted page joins. These are existing discovery page bytes, not newly revealed pages |
| Key grid | Prior P03 clue list; neither exact solved periodic vector occurs in its complete stored list up to cyclic rotation | Two historical reference vectors, all phases/signs:42 cells per heading policy,84 total. A selected/source-justified this grid before decoding |
| Finite-key and ties | Publisher bootstrap had finite best-path only, prior frozen k-best periodic only | Finite n-best sparse backpointers, independent arithmetic checks, qualified tie lower bound |
| Scoring | Frozen P03 local rune/boundary trigram | Primary unchanged byte-for-byte; one complementary model frozen before its tests |

This targeted overlap check is not a claim that no other inherited code ever tested either key. Section continuity and boundaries make this a different objective from separate-page sweeps.

## B01: arithmetic and prototype review

`exact.py` merges `(key phase or finite position, previous two scoring tokens)` at each input position; retains n-best **decision paths**, not n-best distinct plaintexts; no state cap. The periodic and finite normal/literal-F branches match the assignment. Source `selftest.py` independently enumerates bit masks, reconstructs full token histories and scores them:4,836 cases,3,374 legal and1,462 exhausted;22,643 complete legal paths;3,374 bootstrap and2,378 prior-kbest comparisons passed. `float_selftest.py` adds1,000 random real-valued-score cases and the rounding fixture. Exactness means the stated float-evaluated additive objective, never intended plaintext.

Root found a real **tie-count overclaim**, not a maximum-score failure: unequal prefixes can merge, then later round to the same float. The original failing fixture and source snapshot remain logged. The revised diagnostic `optimal_path_ties_lower_bound` combines best-prefix propagation with retained equal-best paths, and is only a lower bound. A value1 does **not** certify uniqueness. Representatives at tied cutoffs are arbitrary; no complete tie enumeration or globally lexicographic tie order is claimed. The revised fixture explicitly checks retain16 gives bound2 while retain1 gives only bound1. Integer-valued-score exhaustive tests can count all exact ties in their tested cases.

Bootstrap initial invocation accidentally omitted `--selftest` and exited2; corrected invocation passed. Neither bootstrap file was edited. Fresh review01 completed900 independent arithmetic cases, all three reference replays, a selected width1024 pruning miss, and the consequential Mill1 continuation. No algorithm blocker found; see `../review-01/REPORT.md`.

## B02: complete keyed references

Reference inputs are complete WELCOME515 runes, circumference KOAN319, and finite prime-minus-one AN END85. Interruption positions establish the expected truth independently but are never passed into search. Explicit punctuation positions come from original ciphertext; physical newlines are removed. Those boundaries agree exactly with independently stored solved text:124/88/25 endpoints.

All three have truth competition rank1 and zero rune errors under exact search and beams64/256/1024, for both models. Primary objective scores are−2.2641914903,−2.0614024147,−2.4754844669. This is fixed known-key path recovery, not unknown-key identification. Rank counts decision paths, with1e−12 comparison tolerance and a stated bound when retained lists are insufficient.

Frozen P03 training parsing remains untouched and can treat physical line breaks as ends. Corrected evaluation boundaries therefore create a disclosed train/test preprocessing mismatch; changing that training would invalidate the primary same-score comparison.

## B03–B04: same-objective section comparison and one complementary model

Every complete output is stored in compressed per-cell records. `section-full-alternatives.txt` and `complementary-section-full-alternatives.txt` retain16 distinct leaders per heading policy among retained per-cell paths; that is **not** certified global top16 distinct plaintext enumeration.

| Objective | Cells where beam64 misses | Beam256 | Beam1024 | Largest per-token gaps,64/256/1024 |
|---|---:|---:|---:|---|
| Frozen P03 |61/84|47/84|31/84|.0470131/.0230819/.0192789|
| Complementary |21/84|5/84|4/84|.0872549/.0691794/.0334941|

Primary exact maxima:body−4.7526582669 (DIVINITY phase3 sign+), whole−4.7433264376 (circumference phase3 sign−). Complementary maxima:body−5.5097339862, whole−5.5069149787. Scales from different models must not be compared directly. All four complete leaders were read and are incoherent. This is joint complete-section optimization, **not** A's prefix-selected continuation evidence. All periodic exact n-best objective scores also agree with the inherited frozen k-best implementation.

The complementary model uses the first1,000 body words each of Emerson Self-Reliance, Poe Tell-Tale Heart, Plato Republic/Jowett and Melville Moby Dick. Full selected raw spans, word coordinates, rune vectors, source hashes and formula are frozen in `complementary-model.json`. The four fresh-control authors are absent from training. Smoothing/order remains .5/8/5 trigram interpolation. Corpus and greedy GP/lexical-boundary preprocessing change jointly; results cannot be attributed solely to source diversity. No further scorer variant or parameter tuning was performed.

## Fresh controls and B06 continuation

Twelve fixed source excerpts from Guest, Mill, Shelley and Blake (249/515/716 runes per author) use new independent periodic or finite keys. Source-level separation from both models is explicit. These are deterministic four-author capability checks, not a population estimate of English detection power. GP aliases and greedy digraph conversion bound natural-LP representativeness. Frozen metadata erroneously said no headings occur in excerpts:Blake1/2 include authorial headings. `FRESH-SOURCE-QUALIFICATION.md` corrects this without changing inputs.

Under P03,10/12 exact leaders equal truth; Mill1 has1 error/truthrank2, Shelley2 has8 errors/truthrank4. Complementary also10/12:Mill1 unchanged, Shelley2 has5 errors/truthrank2. Every compared beam width attains the exact same maxima on these controls. These misses are ranking failures, not path pruning.

Inspection shows Mill1 was cut after the U of USE at rune514 and assigned an artificial final boundary; both models prefer literal F. B06 freezes the next200 source runes for each control. Original ciphertext and existing key bytes remain exact; finite keys receive200 independently seeded extra values. Primary continuation preserves the original prefix endpoint; a separately labeled diagnostic uses genuine source boundaries. No artificial boundary is inserted at a new partial-word endpoint.

- Mill1:committing best prefix yields1 wrong prefix rune plus89 wrong suffix runes under both models. Keeping its original second-ranked prefix yields zero errors. Joint full-text search also recovers truth at rank1, with either endpoint convention. Continuation-selected alternative is **not** called heldout prediction.
- Shelley2:the8/5 internal errors persist after200 new runes. Full-joint truth ranks6/2, and truth remains retained. More horizon does not repair the local scoring preference.
- Other ten controls stay exact under both models.

`continuation-inputs.json`, all24 full records and `continuation-summary.json` preserve these comparisons, including complete alternatives. Search receives no truth interruption oracle.

## B05: conditional full-grid comparison

Nineteen fixed null section streams preserve every ciphertext-F position and the complete adjacent equality mask, including page joins, while sampling other labels uniformly from1..28 excluding the prior symbol where unequal. They do not preserve rune inventory. The same84-cell grid is optimized under each frozen objective:3,192 null exact cell optimizations, each paired with beam64.

P03 actual complete-grid maximum is below every null maximum:19/19 exceed, conditional plus-one upper-tail rank1.00. Complementary has13/19 exceed, rank.70; body/whole separately.70/.65. This is exploratory calibration conditional on the two-key grid, supplied boundaries, fixed F-site/equality comparator and model; it is not a global puzzle discovery probability. There is no candidate to verify.

## Resources, records and continuation decision

All scientific commands use the selected `.venv/bin/python`, numerical thread limits1 and logger deadlines≤900s. Commands, exit codes, source snapshots, raw stdout/stderr and durations are under `runs/`. No timeout occurred. The initial missing-flag failure and tie-count counterexample are preserved. The whole B06 run took107.56s; the38 B05 model/null packets took73.18s.

For the84 P03 actual cells, measured decoder-only exact top16 time totals3.82s versus beam64/256/1024 totals1.28/4.85/18.79s. References/fresh retain256, so their timing is not like-for-like with beam outputs limited to16. `measure-*.json` provides isolated one-method processes:716-rune section exact top16 process peak30.21MB, finite716-rune plant56.71MB; these include Python/model overhead. Per-case `maxrss_bytes` in ordinary comparisons is **cumulative whole-process high-water**, not exact-method peak. Timed decode regions exclude imports/model construction but may include first score-cache fills. Backpointer memory remains a practical limit as finite keys, retain counts and horizons grow.

Decision:use checked exact path optimization for these local fixed-key objectives, retain alternatives across uncertain endpoints, and stop treating beam width alone as the principal recovery bottleneck on controls. Neither scoring model turns the finite grounded section grid into a candidate. Do not widen the key grid or retune the model after this miss. Coordinate the next source-supported section rule or independent workstream finding; this checkpoint is not the end of the eight-hour mission.

## B07: quantify hidden path uncertainty using the same weights

`posterior.py` performs log-domain sum-product forward/backward on the same fixed-key local-score DAG. It produces the partition function, complete legal decision-path count, per-ciphertext-F ordinary/literal marginals and key-phase/finite-position distributions at supplied joins. Prefix-only runs contain no future weights; full-context runs include the complete available text. This adds no new scorer, key, branch prior or training. Every probability is a **normalized model-induced decision-path weight conditional on the fixed key and supplied boundaries**, not calibrated confidence in plaintext. Different paths yielding identical plaintext remain distinct.

Independent mask enumeration checks800cases (620legal/180exhausted),25,761 complete paths, both signs, starts/contexts, boundaries, finite exhaustion, zero/tied scores and empty input. Maximum absolute partition/marginal discrepancy is4.43e−14. Three hundred separate pool comparisons match unchanged P03 or finite-beam returned top16. The extended beam audit additionally retains and hashes the entire terminal64/256/1024 path pools, since the inherited function only returns16. Fresh review02 independently checked650packets/6,275complete paths and both selected full-control examples, with no arithmetic blocker; see `../review-02/REPORT.md`.

All3complete references,12existing controls with the B06 fixed200-rune suffix, and84same section cells were evaluated under both existing models. Full records are in `posterior-references/`, `posterior-fresh/`, `posterior-section/`; `posterior-summary.json` includes per-case and join metrics. No null reruns or extra key cells were added.

For actual section cells, P03 exact top16 paths contain .644652–.998961 of their conditional path weight, while the complete width64 terminal pool retains only1.337e−18–.995587 (mean.291108 across the84cells). Complementary top16 mass is .906544–.999999; width64 pool mass1.452e−33–.999948 (mean.724994). These are per-fixed-key measurements, not probabilities averaged over keys. Severe pruning under a wrong/nonproductive key can discard almost all model weight without implying useful plaintext was missed. Both exact-scored section maxima already failed B05's conditional null comparison.

Mill1 illustrates why premature commitment is unsafe:at its original515-rune cut, the erroneous last literal-F branch has model weight .955607(P03)/.915245(complementary), and the wrong outgoing key phase4 is most weighted. After the fixed200-rune continuation, that branch falls to9.80e−125/3.65e−190 and phase5 dominates. This is full-context revision, not successful top1-prefix prediction. For Shelley2, the internal erroneous branch at498 keeps weight .815403/.867810 after continuation; truth-path weight is only .057769/.130623. Thus more precise search/uncertainty accounting does not remove the scorer's wrong preference.

Reference top16 path mass is numerically near1; extended-control P03 top16 minimum .999873, complementary minimum .999999998. This does **not** establish correctness:the Shelley wrong leader remains inside a highly concentrated distribution. Log-domain floating arithmetic sometimes records probabilities above1 by a few10⁻¹² or rounded exactly1; raw values are preserved and cannot imply mathematical certainty. Beam lost-mass output clamps a tiny negative roundoff to0; normalized log weights remain available.

## B08: reconvergence explains the persistent wrong preference

`dominance.py` traces the frozen Shelley2 truth and wrong leader. Their first differing segment starts498 and reconverges after504 at finite key position496 and score context(A,TH). The wrong segment gains1.485508662nats under P03 and1.881733539 under the complementary model. P03 has a second segment584–588, reconverging at position579/context(S,boundary), gaining .218380560nats. `dominance-source-tables.json` preserves the exact source words/rune spans and each competing trigram/boundary contribution; nothing was retuned.

At the same state, the two histories have identical future legal transitions and score increments. Every completion of the true history therefore has a no-lower-scoring wrong counterpart. With real sums the gap is invariant; repeated float additions can coalesce to ties but cannot reverse weak dominance. Unchanged extra suffix text cannot make that true history uniquely optimal. One hundred fifty independently seeded arbitrary-suffix checks corroborate the algebra, but are not the proof.

Mill1 ends in different states:true phase5/context(U,boundary), wrong phase4/context(F,boundary). It has not reconverged, so later text can distinguish it; B06/B07 measure exactly that. This diagnosis applies only to the current local objective and transition state. It is no conclusion against richer language scores or the puzzle's intended construction.

Path-mass caution:low retained decision-path mass is not automatically missed plaintext or even a missed maximum. `posterior_alias_fixture.py` gives8equal paths producing one plaintext under periodic key0; the finite zero-key fixture gives7paths, also one plaintext. Corresponding branch marginals are1/2 and4/7. Mode-score gaps, decision-path mass and semantic ambiguity must remain separate. No full-plaintext marginal aggregated over aliases has been claimed.
