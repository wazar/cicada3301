# Fresh algorithm review — PERSISTENT-02

Review completed 2026-09-17 around 08:36 UTC, within the fixed 16:15:06 UTC deadline. Reviewed the focused brief, config and STATE. Reviewer authored only this directory. No reserved-page experiment, input edits, Git mutation, nested agent or full ordinary-negative replay. Fresh relative to algorithm authors; not blinded because their code/results and inherited work were accessible.

**Decision: no arithmetic blocker found for the stated exact literal-F optimizer or the structured sum-feedback optimizer. Proceed with preregistered longer-seed section work using its explicit numerical tolerance and capped-search bounds.** This is a targeted code/instrument review, not evidence for intended plaintext.

## Literal-F optimizer

At each fixed ciphertext index, key phase (periodic) or absolute key position (finite), plus the last two scoring tokens, determine every future transition and local score. Retaining the best `retain` paths per state is sufficient for the global n-best score multiset. Distinct path identities remain distinct, even if their plaintexts coincide. Normal F consumes key; literal F does not. At finite exhaustion literal F remains legal while a non-F makes a path impossible. Backpointers and used-key counts reconstruct complete paths consistently.

The float-rounding qualification is necessary: unequal prefix totals can become equal after adding the same suffix. Thus the retained tie representatives need not match a globally mask-sorted exhaustive list, and propagated prefix-optimum counts are only lower bounds on final optimum ties. Current code/docstrings correctly qualify this; the coordinator's prior counterexample remains relevant. This review does not assert uniqueness or a complete tie census.

`independent_checks.py` independently enumerated 900 varied packets: 633 legal, 267 exhausted, 13,563 complete paths. It covered both signs, finite/periodic modes, arbitrary starts, initial score contexts, fixed boundaries, consecutive F, empty input, zero-score ties, integer and fractional weights, and retain counts 1/2/7/16/35. Every returned score list matched exhaustive top-n scores exactly under the same incremental summation. Every path's plaintext, literal positions and consumed-key count matched its independent reconstruction. Reported tie lower bounds never exceeded the exhaustive tie count. Raw records: `decoder-checks.json`.

Integration replay checked all three complete keyed/totient reference groups (`0_welcome`, `jpg107-167`, `p56_an_end`). Source/truth hashes and inputs matched frozen outputs; independent known-rule reconstruction used F occurrence ordinals, then the optimizer searched without supplied interruptions. Full exact outputs, truth metrics and paired width64/256/1024 gaps reproduced. Each truth remained rank1 with zero rune errors.

One deliberately selected existing maximum width1024 pruning miss was replayed: `section-whole-KOAN-CIRCUMFERENCE-11-1`. Exact-minus-beam normalized gaps reproduced as 0.024065338873830555 / 0.02195236616192897 / 0.019278916474001484 for widths64/256/1024. This is a representative claim check selected from existing results, not new discovery coverage. Full records: `reference-and-pair-checks.json`.

## Structured sum-feedback optimizer

For fixed first offsets a,b, the suffix terminal value includes both closing factors W0(u,v,a) and W1(v,a,b). Backward maximization includes each remaining factor exactly once. The suffix bound relaxes the modular sum but preserves cyclic scoring dependencies. Prefix score plus suffix value therefore bounds every feasible completion in exact arithmetic. The final one/two-variable cases enforce zero sum. Incumbent construction yields feasible lower bounds only.

Cap bookkeeping is sound: unresolved heap maximum, the popped prefix interrupted by frontier cap, and every tolerance-discarded upper bound remain eligible for the reported upper bound. Initial suffix construction and 841 incumbent constructions are uninterruptible within `solve`; wall-time enforcement is at branch boundaries and separately at the external logger. Alternatives are encountered feasible outputs, not certified global n-best. These qualifications are explicit in implementation and derivation.

Independent exhaustive checks used 12 new factor arrays: periods m=3/4/5, each with integer, normal-float, tiny (~1e-12), and constant weights. Each was tested under five cap settings (60 solves total): full budget, node0, node1, node3, and time0. Exhaustive enumeration spans every zero-sum assignment, up to 29^4=707,281 assignments per m5 array. Every lower/upper pair contained the exhaustive optimum within 1e-10; every full-budget result matched within 1e-10. Encountered terminations: 44 exhausted, 10 node_limit, 4 time_limit, 2 frontier_limit. Every returned alternative was zero-sum and direct-score consistent. Factors and results are retained in `factors-m*-*.npz` and `structured-checks.json`.

Four reviewer-seeded plants used the frozen Guest0, Mill1, Shelley2, Blake2 excerpts with k5/6/7/8 respectively. Source hashes checked; excerpts were reused, not newly independently sampled prose. All four recovered every rune with zero errors and gaps at most 2.28e-13. For each plant, 100 independent zero-sum offsets checked factor assembly against whole-string direct scoring; maximum discrepancy was 9.10e-12 on total scores. `fresh-plant-checks.json` preserves seeds, inputs, outputs and diagnostics. Blake heading and forced final-word-boundary limitations remain those recorded by B; this review does not remove them.

Float64 bounds are not interval arithmetic. The mathematical admissibility proof does not imply bit-level certified real-number bounds; containment tests allow the stated numerical tolerance. No broader exactness claim is supported for arbitrary magnitude/non-finite factors, arbitrary score order, or altered recurrence.

## Composite-panel statistic

Reviewed `coordinator/aggregate_q12.py` and independently rebuilt the 42x20 matrix from all 840 stored search metadata files. Confirmed exactly the eligible F06 page set, exclusion of prior0/17/55 and reserved pages, 732,511 seeds per cell, the row maxima, all source hashes, and 798 unique prescribed null seeds. Independently recomputed pooled per-page mean/population-SD standardization, per-label maxima and upper-tail rank; rank1.0 reproduced. Two whole-column permutations preserved equivariance. `aggregate-checks.json` stores this check.

This supports an exploratory rank under the specified composite comparator. It does not establish a global discovery probability, exchangeability with arbitrary cipher models, or an independent replay of the 615 million search cells.

## Preserved reviewer failures and reproduction

Two harness failures were corrected without editing authors' code or deleting evidence:

1. `runs/20260917T083204.920537Z-independent-algorithms`: reviewer required exact equality between Python3.12 built-in `sum` over Python floats and the solver's sequential NumPy-scalar addition. Normal-float last-bit rounding broke that overly strict check. Changed only that direct-reconstruction assertion to 1e-12; exhaustive containment remains 1e-10. Successful rerun: `runs/20260917T083226.563312Z-independent-algorithms-tolerance`.
2. `runs/20260917T083413.761528Z-integration-checks`: reviewer initially misread fixture interruption lists as rune indices. They are 1-based F occurrence ordinals, as confirmed in reference.py. Corrected independent reconstruction; successful rerun: `runs/20260917T083434.683573Z-integration-correct-fordinal`.

Additional eligible-page-set check: `runs/20260917T083503.751095Z-aggregate-coverage`. Every run retains exact command, environment, stdout/stderr, source copies/hashes and failure status. Reproduce the principal checks from repository root:

```sh
.venv/bin/python exploration/persistent-02/run_logged.py --owner exploration/persistent-02/review-01 --label independent-algorithms --seconds 900 --input exploration/persistent-02/decoder/exact.py --input exploration/persistent-02/feedback/structured.py -- .venv/bin/python exploration/persistent-02/review-01/independent_checks.py
.venv/bin/python exploration/persistent-02/run_logged.py --owner exploration/persistent-02/review-01 --label integration-checks --seconds 900 --input exploration/persistent-02/decoder/exact.py --input exploration/persistent-02/decoder/compare.py --input exploration/persistent-02/feedback/structured.py --input exploration/persistent-01/coordinator/Q12-sum-autokey/test.py --input exploration/persistent-02/coordinator/aggregate_q12.py --input exploration/persistent-02/decoder/fresh-controls.json -- .venv/bin/python exploration/persistent-02/review-01/integration_checks.py
```

The logger supplies numerical thread limits1 and refuses execution after the fixed deadline. Its saved source copies identify precisely what was reviewed if worker implementations later change.

## Narrow B06 addendum

At B's request, `continuation_check.py` additionally reviewed the already-selected Mill1 horizon example, both fixed models. Independently rebuilt source rune/character spans and genuine boundaries, verified the original prefix ciphertext, and re-encrypted the full planted continuation. Replayed all retained-prefix continuations and joint/genuine searches; outputs and direct scores matched. Committing prefix rank1 gives 1 prefix + 89 suffix errors; retained prefix rank2 and joint horizon both recover zero errors, joint truth rank1. This confirms the stated horizon consequence, not a blind power estimate. Evidence: `continuation-check.json` and the `B06-Mill1-targeted` logged run. Forest adapter received preliminary source inspection only, not completed independent review; defer it to review02.
