# PERSISTENT-02 — focused recovery, not another format survey

## Repository entry points

Everything needed to start this assignment is in this repository:

- Brief: `PERSISTENT-02-FOCUSED-RESEARCH.md` (this file).
- Prototype: [literal_f_exact_dp.py](exploration/persistent-02/bootstrap/literal_f_exact_dp.py).
- Executed synthetic check: [literal_f_exact_dp_selftest.json](exploration/persistent-02/bootstrap/literal_f_exact_dp_selftest.json).
- Previous result: [PERSISTENT-01.md](audit/reports/PERSISTENT-01.md).

No chat attachment or manual download is required. Safely fetch and fast-forward
from `origin/master` before starting. Preserve local work and any newer commits;
do not reset, discard changes, force push, or clear an earlier session's STOP file.

For this project, publish research assignments, helper code, and test records in
the owner's fork. Give the owner a repository link and a copy-and-paste prompt.
Do not make manual downloads from chat attachments part of the handoff.

The prototype's test record is from the publisher's isolated environment, not the
owner's Mac. It records its source hash and a repository-root reproduction command.
Keep this bootstrap evidence unchanged. Put adaptations and new test results in
`exploration/persistent-02/decoder/`.

## Mission

Continue `wazar/cicada3301` from the reviewed PERSISTENT-01 result:
`25bf6f95b31600f3011481999f39d05262216958`.

Use the persistent execution arrangement that actually worked in PERSISTENT-01.
Do not build another supervisor or replace it merely to start this assignment.

When the owner starts this assignment, use an eight-hour research window unless
the owner gives another duration. Read the real clock, record one fixed deadline,
and preserve it across agent turns. End earlier only for an owner stop, a real
resource/platform limit, or a confirmed result that requires a decision.

A completed batch is not the end of the assignment. Continue with the next
justified step within the three workstreams below. Do not fill remaining time
with repeated completed work, arbitrary variants, or reports alone.

**Goal:** obtain a stronger decoding capability, use the confirmed seed-search
gap on real untested material, and pursue a small number of rules tied to one
verified section of the book.

This brief defines a new assignment; execution starts on the owner's instruction.
Keep the old session's STOP marker, failures, and evidence unchanged. Create new
state under `exploration/persistent-02/`.

## What the last run established

Treat these as scoped findings, not general cipher conclusions:

- Q12 corrects a specific inherited sum-feedback seed argument. Wrong seeds do
  not disappear in that recurrence. Its exhaustive seed-length 2–4 search covered
  actual originals 0, 17, and 55, not all unsolved pages.
- P03's frozen fixed-key literal-F search uses a width-limited beam and a local
  rune/boundary trigram score. Retained maxima need not be global maxima.
- Q11's uniform-nonrepeat comparison removed support for the earlier reciprocal
  model's apparent advantage.
- N18's omitted-sentinel BWT admits original 0, but also 3/19 matched inventory
  permutations. No readable result or source-based reason currently makes it a
  preferred puzzle route.
- A specific OutGuess shared prefix was explained by image background.
- The 14-label Latin-window results reject their exact source/encoding setup,
  not Latin in general.
- Source boundaries and glyph readings are partly verified. In particular, a
  printed line break is not automatically a word boundary.

Do not rerun the full audit or automatically choose the two easiest proposals
at the end of PERSISTENT-01.

## Coordinator and workers

Use one coordinator and up to three native workers, with separate directories.
A fresh reviewer can use a freed slot. Do not pretend concurrent capacity exceeds
the actual runtime limit.

Worker A: `section/` — one section and clue-based rules.
Worker B: `decoder/` — exact fixed-key literal-F path optimisation.
Worker C: `feedback/` — exploit and extend Q12's demonstrated coverage gap.

These worker directories are under `exploration/persistent-02/`.
Only the coordinator changes shared state, claim records, or Git. Workers may
read one another's frozen outputs but cannot edit them.

Reuse checked inputs, models, and tools. Record exact source versions. Before
building anything, perform a short targeted check for an already suitable exact
implementation. A failed repository search is not proof that none exists.

Keep meaningful real-puzzle work running while a particular control or source
question is unresolved elsewhere. Do not restore the old universal 100%-exact
control gate. Arithmetic defects block the affected implementation; incomplete
language recovery narrows conclusions.

## Worker A — make a section, not a three-page sample, the research unit

1. Select one small, contiguous, already-discovery section using original images,
   explicit end marks, headings, and marginalia. Start by inspecting the region
   around originals 0–2, but do not declare those exact pages a section without
   checking the boundary.
2. Reuse prior image and source work. Verify just the selected section's rune
   order, explicit delimiters, uninterrupted line joins, and uncertain symbols.
   Do not create a new whole-book transcription or font-classification project.
3. Freeze a section packet. Give original page/region/rune coordinates, competing
   readings where justified, and separate physical layout from textual boundaries.
   Never select a glyph because a proposed decryption reads better.
4. Extract at most three explicit procedural hypotheses from this section and
   linked solved instructions. For each, cite the actual source, state the rule,
   and name a prediction that was not chosen by its decryption score.
5. Test those rules on real discovery data. Possible distinctions include key
   continuity across a section versus page reset, a source-supported numerical
   direction, or a specifically indicated reading route. Do not turn every
   decorative feature into an unrestricted parameter.
6. When fitting a rule on one region, freeze it before applying it to the next.
   Because discovery pages have been viewed before, call this model-specific
   continuation, not globally untouched validation.

Success is either a reproducible continuation or a clear comparison that changes
which section rule should be tried next. Do not stop at producing a section map.

Retain reserved pages until a concrete candidate and prediction justify a staged
reveal. Preserve the existing page-54 exposure qualification. Do not call a reused
validation page pristine.

## Worker B — remove avoidable path pruning

`exploration/persistent-02/bootstrap/literal_f_exact_dp.py` is an independent
prototype. It passed small synthetic exhaustive comparisons, not a puzzle
benchmark. Review it rather than taking it on trust. Run its self-test from the
repository root:

```bash
python3 -S exploration/persistent-02/bootstrap/literal_f_exact_dp.py --selftest
```

### Exact scope

For a fixed periodic or finite key, and fixed input boundaries:

- Normal branch: emit `(cipher + sign * key[position]) mod 29`; consume one key.
- Literal-F branch, allowed only at ciphertext F: emit F; consume no key.
- Score each emitted token using the previous two tokens, including supplied
  boundary tokens.

At a fixed input position, future behaviour depends on:
`(key phase or finite-key position, previous two score tokens)`.

Merge paths with the same state. Keep the highest cumulative score and suitable
backpointers. This gives an exact maximum for this stated local objective.

It does NOT establish intended plaintext. The prototype retains one best path,
not every tie or all n-best outputs. Add carefully tested n-best/tie handling for
research use. Do not generalise this state to plaintext-feedback keys or
whole-text neural scores without deriving the additional required state.

### Required execution

1. Recheck the prototype against independent exhaustive enumeration on short
   inputs. Include both signs, key phases, periodic and finite keys, ordinary F,
   literal F, consecutive F, boundaries, ties, and finite-key exhaustion.
2. Use the repository's current frozen P03 score unchanged for the first paired
   comparison. Compare exact search with beam widths 64/256/1024 on identical
   inputs, keys, and boundaries. Save objective differences and actual runtimes.
3. Test the complete keyed reference groups without supplying interruption
   positions to the search. Measure truth rank, rune recovery, and ambiguity
   separately. A model can prefer the wrong valid plaintext even when its search
   is exact.
4. Use fresh source excerpts and independent planted keys for capability checks.
   Keep source-level train/test separation. Four repeatedly reused references
   alone are not a new broad estimate of detection power.
5. Apply the checked exact method to the chosen real section and a finite,
   source-justified key set. Do not admit keys only because ordinary decoding
   scored well. Compare complete outputs with the corresponding old beam results.
6. After the same-score comparison, test at most one additional independently
   prepared English/rune model with more source diversity. Use the same key grid.
   Clean page furniture, match runic and delimiter preprocessing, and freeze
   training before examining new test results. Prefer complementary ranking to
   repeatedly tuning one scorer on this puzzle.

Use sparse states/backpointers; measure peak memory and throughput. If exact
search is not practical for a particular key/scorer, report that boundary and
use a bounded method with a measured search gap. Do not claim exactness after
introducing state caps.

A useful outcome is a verified best-scoring path, a measured beam miss, or proof
that ranking rather than path pruning remains the immediate issue. It need not
be a solution to make this capability worth retaining.

## Worker C — use the actual Q12 finding

Start from Q12's exact recurrence, not an unrelated generic autokey construction.

1. Independently check the seed-error identity and its original source claim on
   small examples. Preserve the original code and report.
2. Build a per-page coverage table. Complete the same justified seed-length 2–4
   test on the remaining eligible discovery pages, including the selected section.
   Avoid repeating 0/17/55 as new coverage.
3. Reuse the same objective and bounds for that extension. Preserve matched
   full-search comparisons and explicit candidate outputs. Calibrate according
   to the compared statistic; do not turn a coarse rank into a global discovery
   probability.
4. For candidates, fit on a prefix and test the unchanged seed/recurrence on a
   continuation. Do not select or repair the seed using that continuation and
   still call it held out.
5. Only then consider a longer-seed extension. Derive a structured optimiser
   before increasing brute-force length.

For the uninterrupted sign-minus decoding relation, after the seed region:
`C_i = P_i + sum(P_(i-j), j=1..k) mod 29`.
Thus, for `i >= k+1`:
`C_i - C_(i-1) = P_i - P_(i-k-1) mod 29`.

Q12 already uses the equivalent periodic-error reduction for k=2–4. Longer
candidate plaintexts can be represented as phase-dependent offsets from one
baseline decode, with the zero-sum constraint on an offset period of k+1.
Use that structure for constraint search, bounds, or dynamic programming.
Do not promise a cheap exact solution for arbitrary k: score order, cyclic
dependencies, and the modular sum constraint affect cost.

Choose any extended lengths by a recorded structural reason or a modest frozen
coverage band, not because a training fragment looks like words. First benchmark
the solver on longer-seed plants and compare exhaustive small-k results.

The goal is to exploit a proved gap, not to declare autokey the likely answer.
Failure excludes only the tested recurrence, seeds, input, and detection scope.

## Research selection rules

Keep BWT metadata ranking, generic Morse/postfix formats, further OutGuess
background-prefix work, and arbitrary Latin source expansions parked unless a
new, independently stated puzzle clue makes them relevant.

For each new batch record:
- the question and why it matters to this section or demonstrated gap;
- the result expected if the hypothesis is useful;
- the simplest competing explanation;
- the finite changed scope relative to prior work;
- controls, selection rule, resource limit, and resulting decision.

A narrow proof against an invented representation is not automatically high-value
progress. Do not manufacture new representations just to keep workers occupied.

Use the repeat-suppressed reference where appropriate, alongside specified
boundary/histogram comparisons. No single null is automatically correct for every
question. A model must do more than beat a needlessly complicated fitted opponent.

Adapt within these workstreams without repeatedly requesting approval. End a weak
branch and pursue the next reasoned question. Failure of one branch does not stop
the other workers.

## Review, resources, and records

Keep the prior practical machine/thread safeguards. Allocate compute to measured
useful tasks, not all-core activity for its own sake. Checkpoint resumable batches.
Do not run large downloads, paid APIs, external machines, or unknown binaries
without separate authorisation.

Review new algorithms, consequential counterexamples, and candidates closely.
Do not automatically replay every numerical trial independently after each miss.
Retain deterministic inputs and targeted consistency checks so further review is
possible. A representative code check is not exhaustive independent replay.

Keep concise shared state and one record per meaningful batch. Store dense numeric
results in suitable compressed arrays rather than thousands of tiny metadata files
when possible. Preserve failures, versions, and outputs necessary for reproduction.
Do not change original scientific evidence or silently upgrade old conclusions.

If a search is producing only misleading fragments, change a material assumption
or move effort to another of these workstreams. Do not choose language-model
settings, glyph repairs, or source passages to force a preferred sentence.

## Final result

Publish `audit/reports/PERSISTENT-02.md` with:

1. Actual new puzzle coverage, without double-counting reruns.
2. The exact-search versus beam comparison under the same objective.
3. Section-specific rules tested and their continuation results.
4. The Q12 extension's supported bounds and strongest complete alternatives.
5. Candidates that merit verification, or an explicit statement that none do.
6. The one next research decision justified by these results.

Use the owner's standing publication instruction for reviewed assignment files.
Do not publish claims or contact third parties on the owner's behalf beyond that
scope. Confirm the final commit. Stop at the fixed new deadline, not when the
first three batches finish.

## Sources inspected for this brief

All repository links are pinned to the reviewed commit.

- [Final report](https://github.com/wazar/cicada3301/blob/25bf6f95b31600f3011481999f39d05262216958/audit/reports/PERSISTENT-01.md)
- [Q12 result](https://github.com/wazar/cicada3301/blob/25bf6f95b31600f3011481999f39d05262216958/exploration/persistent-01/coordinator/Q12-sum-autokey/REPORT.md)
- [Q12 implementation](https://github.com/wazar/cicada3301/blob/25bf6f95b31600f3011481999f39d05262216958/exploration/persistent-01/coordinator/Q12-sum-autokey/test.py)
- [P03 implementation](https://github.com/wazar/cicada3301/blob/25bf6f95b31600f3011481999f39d05262216958/exploration/persistent-01/worker-c/p03_frozen.py)
- [Q11 reference comparison](https://github.com/wazar/cicada3301/blob/25bf6f95b31600f3011481999f39d05262216958/exploration/persistent-01/coordinator/Q11-uniform-reference/REPORT.md)
- [N18 result](https://github.com/wazar/cicada3301/blob/25bf6f95b31600f3011481999f39d05262216958/exploration/persistent-01/worker-n/N18/REPORT.md)
- [Boundary work](https://github.com/wazar/cicada3301/blob/25bf6f95b31600f3011481999f39d05262216958/exploration/persistent-01/CHECKPOINT-02.md)
