# Experiment 01 — BLOCKED_BY_POSITIVE_CONTROL

**The real puzzle experiment did not run.** The frozen gate stopped on a fresh
DIVINITY / sign +1 / legacy rejection-beam positive control: the detector ranked
the planted recipe/sign first but recovered only 119 of 120 runes on its first
page. This is a failure of this instrument's required exact-recovery gate, not a
failed puzzle-key hypothesis. No calibration, held-out negatives, real-derived
shuffle panel, or real candidate decode was executed.

## Frozen scope and chronology

The proposal was copied verbatim into `preregistration.json`, together with the
execution details, before importing the decoder or scoring any candidate.
`FREEZE.json` records preregistration SHA-256
`ed0fdd288c12a705f3688924a813960d489b20c504116002ef6a811adfced9ea`.
The logged freeze completed at 2026-09-16 18:03:27 UTC. The first positive pilot
began at 18:04:24 UTC; the main batch began at 18:05:21 UTC. The inputs and frozen
hashes were checked at the beginning of both runs.

The fixed key arrays in `keys.json` each contain 2,048 rune indices: repeating
DIVINITY, literal FIRFUMFERENFE, ascending primes beginning at 2 modulo 29, and
prime-minus-one modulo 29. Both decode signs use `p=(c+sign*k) mod 29`; encryption
uses its inverse. Array equivalence was checked after applying each sign: all
eight signed candidates are distinct, with source labels retained. Array hashes
and the complete groups are in `ACCOUNTING.json` and each output directory's
`candidate-dedup.json`.

The intended real slices are the first 120 indices of original images `0.jpg`
and `1.jpg`, located by their original filenames in
`audit/parallel-01/inputs/dataset.json` (`parallel-01-inputs-v1`). Their complete
arrays, segment identities and byte-index SHA-256s were frozen in `slices.json`.
Freezing these slices is input preparation, not decoding them. Every proposed
choice resets key and filter state for each page, uses offset zero, and uses rigid
or unmodified legacy beam400/max_skip3. No offset, spelling, recipe, page, or
parameter was added.

The frozen selection rule takes each recipe/sign's better decoder score per
page, then the lower of the two page scores, then maximises over the eight shared
recipe/sign hypotheses. Exact-score ties are retained. The prospective flag rule
requires both page scores at least −5.5 and the joint statistic strictly greater
than calibration maximum +0.5. It has not been calibrated in this execution.

## Positive controls and execution counts

Sixteen required recipe/sign/model cells each planned 20 two-page cases, for
320 pairs. The required rigid cell uses unfiltered encryption; the required beam
cell uses the one-key-draw rejection loop at suppression probability .83. Seeds
and every accepted/rejected encryption attempt are saved. Each executed pair was
evaluated under all 32 page/recipe/sign/decoder choices; every complete output,
score and selected key-consumption alignment was retained.

The messages in `fixtures.json` are 20 fresh authored variations on two prose
passages, cut to 120 runes per page. They were written and frozen before scoring,
without rejecting or selecting any text by detector performance. They are not 20
independent language corpora. The actual structured key arrays were used to plant
the controls; random-key success was not substituted.

| Recipe | Sign | Required model | Executed | Passed | Failed | Skipped |
|---|---:|---|---:|---:|---:|---:|
| DIVINITY | −1 | Unfiltered rigid | 20 | 20 | 0 | 0 |
| DIVINITY | −1 | Rejection beam | 20 | 20 | 0 | 0 |
| DIVINITY | +1 | Unfiltered rigid | 20 | 20 | 0 | 0 |
| DIVINITY | +1 | Rejection beam | 7 | 6 | 1 | 13 |
| FIRFUMFERENFE | −1 | Unfiltered rigid | 0 | 0 | 0 | 20 |
| FIRFUMFERENFE | −1 | Rejection beam | 0 | 0 | 0 | 20 |
| FIRFUMFERENFE | +1 | Unfiltered rigid | 0 | 0 | 0 | 20 |
| FIRFUMFERENFE | +1 | Rejection beam | 0 | 0 | 0 | 20 |
| PRIMES | −1 | Unfiltered rigid | 0 | 0 | 0 | 20 |
| PRIMES | −1 | Rejection beam | 0 | 0 | 0 | 20 |
| PRIMES | +1 | Unfiltered rigid | 0 | 0 | 0 | 20 |
| PRIMES | +1 | Rejection beam | 0 | 0 | 0 | 20 |
| TOTIENTS | −1 | Unfiltered rigid | 0 | 0 | 0 | 20 |
| TOTIENTS | −1 | Rejection beam | 0 | 0 | 0 | 20 |
| TOTIENTS | +1 | Unfiltered rigid | 0 | 0 | 0 | 20 |
| TOTIENTS | +1 | Rejection beam | 0 | 0 | 0 | 20 |

Totals: 67 pairs executed, 66 passed, one failed, 253 skipped. This produced
2,144 complete page choices (1,072 rigid and 1,072 beam). Later recipes appeared
as competing decode candidates, but their own planted positive cells were not
executed and are not credited as passed. All planned cells and per-case skips
remain in the preregistration and `ACCOUNTING.json`. Individual run summaries
list cases absent from that run; the accounting file combines pilot and main.

## The first failure

The retained failure is
`outputs/20260916T180521.719679Z/case-066.json`: cell index 3, case 6,
DIVINITY / sign +1 / rejection beam, encryption seeds 913012 and 913013.

| Page | Exact runes | Decoded score | True plaintext score |
|---|---:|---:|---:|
| 0 | 119/120 | −4.0951382033607935 | −4.096305974563245 |
| 1 | 120/120 | −4.125387407138635 | −4.125387407138635 |

At page 0's final position (rune index 119), the true rune is A (index 24) using
key index 123; the decoder instead emits S (index 15) using key index 122. The
wrong complete output receives a slightly higher normalised English score. The
planted recipe/sign is still the top joint hypothesis, with statistic
−4.125387407138635 and beam selected on both pages. It fails the separately
required exact-recovery condition. Neither page's encryption exceeded one
consecutive rejected draw, so exceeding the max_skip3 bound is not this
failure's explanation. No stronger causal claim about beam pruning is made.

A trace-only copy follows the inherited beam's enumeration, scoring, stable sort
and winner rule while recording key indices and retained widths. **For every
beam choice, its full output dictionary was asserted equal to the unmodified
production `beam_decode` output before the result could be accepted as evidence.**
The records retain tied cumulative-score beam winners, tied page decoders and
tied joint hypotheses. The plaintext arrays, original prose, ciphertext arrays,
full 2,048-symbol planted key, encryption state traces, all outputs and scores,
and decoding key-use traces for the failure are in that one case file. There was
no instrument comparison failure or decoder modification.

## Resources, logs and code defects

`runs/*/command.json` records contemporaneous command, commit, input/source
hashes, timestamps, actual exit status and environment; adjacent files preserve
stdout/stderr and code snapshots. Initial imports were inspected: the legacy
module loads the alphabet and English quadgram scorer, with no experiment at
import. The logger pins numerical library thread counts to one.

The pilot measured 0.0812 seconds internally (0.1249 logged wall seconds). After
that measurement, the coordinator authorised one named `experiment-01-main`
with a 300-second limit in `audit/next-01/EXPERIMENT-BUDGET.md`, hashed as a main
input. The main ran for 5.7976 logged seconds and stopped immediately at the
required failure. Freeze and continuation wiring were also logged. All six
logged commands, including accounting below, used approximately 8.91 seconds in
total, well below the assigned 1,800-second execution cap. No scientific retry
or additional main batch occurred.

A separate **post-stop accounting code defect** is preserved: the first
`summarize.py` run raised `KeyError: duration_seconds` when reading its own
still-running logger record. That run's traceback, exit 1 and original source
snapshot remain in `runs/20260916T180556.208277Z-post-stop-accounting/`.
Changing only the duration aggregation to treat a not-yet-completed record as
zero fixed accounting; the corrected accounting run is separately logged.
It re-read retained data and never imported or called the detector. This defect
did not cause or change the scientific control failure. The accounting elapsed
field is explicitly the sum available before its own completion; the final
approximately 8.91-second total above includes that completion.

`continuation.py` contains the prewritten gated calibration/held-out/shuffle/real
continuation. That branch was never entered and has no execution validation from
this task. Its existence must not be presented as completed calibration.

## Interpretation and smallest next action

Calibration: 0/100 planned pairs executed. Held-out checking: 0/100.
Separate histogram sensitivity: 0/100. Real input: 0/32 page choices.
All were skipped because the first required positive failed. No empirical
false-flag rate or calibrated real-input verdict can be reported. Had the
held-out gate run with zero flags in 100, its one-sided 95% bound would still be
about 2.95% conditional on that negative distribution, not a universal guarantee.
Shuffling was planned only as a separate panel and would destroy adjacency and
repeat patterns.

The smallest justified next action is an independently reviewed synthetic
instrument task on this retained final-rune mismatch: determine whether exact
terminal recovery is identifiable and how scoring chooses among compatible
paths. Keep exact recovery, path ambiguity and candidate flagging separate.
Any revised gate or decoder would require a new preregistration and fresh
controls, not retroactive removal of this failed cell. This record supports no
negative conclusion about the four recipes on LP2, other offsets or reset rules,
other languages, continuous keys, different page methods, or the separate
literal-F interruption model.

Worker A stops here for fresh review. Only `audit/experiment-01/` was written.
