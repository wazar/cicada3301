# Review03 — state dominance and actual invariant result

Completed around2026-09-17 09:02 UTC. Fixed assignment deadline remains16:15:06 UTC. Read current STATE, focused assignment, B HANDOFF/REPORT, C04 preregistration and actual metadata, C05 report, C06 preregistration, and A06 preregistration/section source-check record. Reviewer is independent of B08's author, but not blinded. Only review03 files were authored; no original evidence, producer code, Git or reserved input changed. Both logged executions passed.

**Finding: B08's state-reconvergence dominance claim is supported for the stated fixed key, literal-F transition relation and additive trigram objective. C04 actual rank.89 exactly follows the previously reviewed preregistered200-panel procedure. Neither finding supports further same-model beam widening or uninterrupted seed-length expansion.**

## B08 independent reconstruction

`check_dominance.py` did not call the author's trace/dominance functions. It independently reconstructed key consumption, ciphertext-to-rune transitions, the complete scoring-token history, state before/after every rune and individual token contributions. It calculated each token's log weight directly from the frozen model's counters and smoothing formula rather than calling `lm.step`. Full scalar rows matched the stored B08 rows exactly.

The independently located divergent/reconvergent spans are zero-based rune indices:

| Model | Divergent segment | Shared state after segment | Wrong−true local total |
|---|---|---|---:|
| P03 |498–504|finite position496, context(A,TH)|+1.4855086616007913nats|
| Complementary |498–504|finite position496, context(A,TH)|+1.8817335387013403nats|
| P03 |584–588|finite position579, context(S,boundary)|+.21838056005531414nats|

Source hashes and the greedy source-rune/word-span mapping were reconstructed. The first segment crosses parts of **“month her father”**, character spans[36011,36016),[36017,36020),[36021,36027). The second lies within **“Beaufort’s”**, span[36130,36140). Exact per-rune source positions, ordinary/literal flags, emitted runes, trigram/boundary contributions and table text all matched. Source spans are Python text character coordinates, not assumed byte offsets.

At a fixed input index, the common state contains the same finite-key position and the same last two score tokens. Thus each legal future ordinary/literal sequence from the true history is also legal from the wrong history, consumes the same key positions, emits the same suffix runes and receives the same suffix increments. Mapping a suffix to itself is a bijection between completions. A strictly larger wrong-prefix real total remains strictly larger after any common suffix sum. In the actual float implementation, adding the same finite increment is monotone: accumulated values can round to equality, but cannot reverse the weak ordering. Hence future ciphertext alone cannot make that true history uniquely optimal under this unchanged objective. This does not claim that every higher-ranked future path must have the same wrong segment, nor that richer scoring states share this limitation.

As a finite corroboration, the reviewer enumerated all8literal masks on one fixed five-rune branch-rich suffix for each of the three merges,24complete path checks total. Each paired completion preserved weak dominance. This is not the general proof and does not replay the author's150random suffix checks. The proof is the identical-state transition/weight bijection above.

Mill1 is different: after its515-rune prefix, truth ends at periodic phase5/context(U,boundary), whereas its wrong leader ends at phase4/context(F,boundary), under both models. The histories have not merged and future increments need not agree. Their observed continuation reversal is therefore consistent with the model. It cannot be generalized to Shelley's already-merged histories.

Evidence: `dominance-checks.json`, plus full command/source snapshots/stdout in `runs/20260917T090001.002134Z-B08-independent/`.

## C04 actual statistic and provenance

`check_c04_actual.py` confirmed `invariant.py` and `C04-PREREG.md` are byte-identical to the sources reviewed in review02. Actual input equals the frozen716-rune section body. It independently regenerated all199comparator ciphers from seed2026200000+replicate, preserving the declared first rune/equality mask, then reconstructed all200×33phase histograms using the separate difference-form baseline.

All numerators, denominators and saved histograms matched. Independent pooled mean/population-SD calculations,33-period maxima and upper-tail count reproduced:

- selected k4;
- actual standardized family maximum1.5705476157936 (last-bit rounding differs by<1e−12);
-177of199comparator maxima at least as large;
-plus-one family rank(1+177)/200=.89.

The checked actual-body SHA256 over rune-index bytes is `3e6191f2f5ab96359d9dbc27b223bd17d565f0e2978254e4b63041b61b2ed689`. No control panel was repeated. This is the predeclared conditional family rank, not an unadjusted selected-period significance or a programme-wide discovery probability. The result follows C04's stated branch decision to deprioritize merely widening uninterrupted seed lengths.

Evidence: `c04-actual-checks.json`, `runs/20260917T090059.225632Z-C04-actual-statistic/`.

## Concrete next research decision

**Finish the already-frozen A06/C06 comparisons, then prioritize the remaining physical delimiter/row-join check in the selected section rather than another key/model/horizon sweep.** This stays within the original three workstreams and addresses a still-unverified input assumption that directly controls the local objective.

1. A06 is the justified calibration correction for A's two minimum coarse ranks: it fixes literal-F sites/equality mask using the already-frozen B comparators. Honor its existing stopping rule if the effect disappears; do not add more null draws, histogram variants or scorer choices afterward merely to recover a tail. Its loss of first-rune conditioning and shared/adaptive comparator status must remain explicit.
2. C06 already tests the measured C05 ranking limitation using the one permitted frozen complementary model. Complete all32paired plants and20actual/comparator packets, including newly introduced errors and interruption gains. This changes scoring coverage, not seed/transition coverage. C04's.89 does not license an arbitrary longer uninterrupted-seed sweep; C05's ordinary P03 rank similarly gives no basis for automatic k4+ enlargement.
3. A's existing visual record verifies two of30within-page row joins (12/12/9text rows across the three pages), leaving28internal joins for a bounded native-resolution delimiter pass. Check punctuation presence/absence and row order without consulting candidate plaintext; do not claim a new729-glyph transcription. Freeze any source-justified correction or competing boundary vector first. Only a changed input warrants rerunning affected existing cells/continuations; if all joins agree, retain that stronger input verification and avoid redundant decoder reruns.
4. Keep B's already-verified exact decoder available to evaluate such changed source assumptions. B08 shows why spending that time on a longer unchanged suffix or larger beam cannot repair the Shelley-type failure. A third scorer or arbitrary new key family would exceed the current frozen-model/source rationale.

This is a decision recommendation from the current evidence, not an instruction to stop the eight-hour assignment early. Further work should be selected from new physical/source evidence or a demonstrated construction gap, with the same finite scopes and conditional claims.

## Reproduction

```sh
.venv/bin/python exploration/persistent-02/run_logged.py --owner exploration/persistent-02/review-03 --label B08-independent --seconds 900 --input exploration/persistent-02/decoder/dominance.py --input exploration/persistent-02/decoder/dominance_source_table.py --input exploration/persistent-02/decoder/dominance.json --input exploration/persistent-02/decoder/dominance-source-tables.json -- .venv/bin/python exploration/persistent-02/review-03/check_dominance.py
.venv/bin/python exploration/persistent-02/run_logged.py --owner exploration/persistent-02/review-03 --label C04-actual-statistic --seconds 900 --input exploration/persistent-02/feedback/invariant.py --input exploration/persistent-02/feedback/C04-PREREG.md --input exploration/persistent-02/feedback/C04/actual.json --input exploration/persistent-02/section/section-packet.json -- .venv/bin/python exploration/persistent-02/review-03/check_c04_actual.py
```

Logger supplies numerical thread limits1, captures sources and refuses work beyond the fixed deadline. Both checks are targeted reproductions, not new scientific search coverage.
