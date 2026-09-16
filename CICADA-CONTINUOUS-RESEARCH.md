# CICADA CONTINUOUS RESEARCH — PERSISTENT-01

## Mission, not checklist

Work on solving the remaining Liber Primus puzzle in `wazar/cicada3301`.
Use OVERNIGHT-01, published through `ababcf31b477f3aaeb02fbe531d66a18561348d4`, as previous work. Preserve newer commits and unrelated local changes. Do not reset the checkout.

The owner wants sustained research, not completion of another finite task list. Continue proposing, implementing, running, comparing, and improving experiments throughout the authorised work window. Completing a batch, obtaining a negative result, writing a report, or pushing a commit does not complete this mission.

For a direct interactive/goal session, set an eight-hour deadline from the actual local start time. Record its absolute time and timezone once. It is the end of the work window, not permission to finish when a small checklist ends. On continuation, reuse that deadline. When a launcher supplies a deadline, use its deadline instead. Do not extend it or create a new eight-hour window on each restart.

This instruction supersedes older assignment-level commands to stop after a named report, a fixed queue, or one failed search control. Preserve those historical instructions and results as evidence. It does not override tool permissions, account limits, the owner's stop request, or unrelated safety rules.

Success means a reproducible, defensible advance on the puzzle. Work must remain honest when nothing useful is found. Do not invent a discovery to satisfy the mission.

## Two execution modes

DIRECT MODE: continue working within the active session until the deadline, an explicit owner stop, or a genuine global execution block. Use native goal/continuation controls only when actually available. A final summary is not a mechanism for keeping a turn active.

SUPERVISED MODE: an external launcher submits successive `codex exec` turns. Each turn should execute a useful research batch, persist its results and the next actions, then return a checkpoint. That is a turn boundary, not the end of the mission. The launcher starts the next turn automatically. Do not spawn another coordinator or modify the launcher's deadline, controls, or logs. Do not use `/goal` inside a non-interactive prompt as though it were a tool call.

In either mode, context loss or a turn boundary requires checkpoint recovery, not restarting the whole audit.

## Start from the actual current state

Read these first, then read only the lane code and evidence needed for your next action:
- `audit/reports/OVERNIGHT-01.md`
- `exploration/overnight-01/REPORT.md`
- `exploration/overnight-01/RESUME.md`
- `exploration/overnight-01/config.json`
- `exploration/persistent-01/STATE.md`, `QUEUE.json`, and recent experiment records, when present.

OVERNIGHT-01 ran real searches, but all eight queues were finite. None produced credible plaintext. Do not call their saved resume commands new work when their cursors are already complete. Do not review all 584 retained outputs again.

The existing rune input, 86-repeat measurement, complete reference groups, corrected literal-F arithmetic, and limited detector results are available starting evidence. Full transcription accuracy, scoring coverage, and broad cipher exclusions remain limited. Carry those limits forward instead of repeating their complete audits.

Initial genuine gaps identified by the last report:
1. R02 searched literal-F choices on a small subset of keys, partly selected through ordinary decoding. Correct F-model candidates can score poorly under the ordinary model. Search the F model independently of that filter.
2. R07's finite-offset literal-F search concentrated on original pages 49 and 51. Other discovery pages have limited coverage.
3. R04's short-period fitting used limited deterministic starts and a declared scoring surrogate. It did not establish recovery under all interrupted or multilingual models.
4. R06 tested a few layout routes with limited control coverage and did not cross them with the full clue-key/F set.

These are starting questions, not a terminal list or claims that they contain the solution.

## Organisation

Use one coordinator and up to three simultaneous native workers, within the actual runtime limit. Do not pretend sub-agents exist. No nested agent trees and no second coordinator. Keep one researcher testing concrete possibilities, one improving or challenging a useful method, and one investigating distinct structure or clues. Reassign idle workers immediately.

Give workers separate directories under `exploration/persistent-01/`. Only the coordinator edits shared state and performs Git writes. Reuse a freed worker slot for fresh review of a serious candidate. Reviews run alongside other research; they are not mandatory global barriers after every batch.

Use at most three CPU-heavy local jobs initially, with one numerical-library thread each. Increase a particular job's CPU allocation only after measuring benefit and respecting the host's available memory and responsiveness. Do not rent compute or switch to paid providers.

## The mandatory research loop

Repeat until the real stop condition:

1. CHECK: read the clock, current experiment state, active worker/process state, and new evidence.
2. SELECT: choose work expected to change a research decision, not merely increase a counter.
3. SPECIFY: write a short experiment card before execution.
4. IMPLEMENT: reuse checked arithmetic; write only missing method-specific code.
5. TEST: run appropriate small controls to catch implementation errors. Measure imperfect ranking rather than pretending it is exact.
6. SEARCH: execute on the authorised real discovery input.
7. COMPARE: inspect full outputs, alternatives, matched controls, continuation behaviour, and sensitivity to parameters.
8. LEARN: explain what changed, what did not, and the next useful discriminating test.
9. REPLENISH: add follow-on work before the ready queue becomes empty. Then execute it.

Keep at least twice as many concrete ready jobs as available worker slots whenever practical. Queue entries need input, method, exact change from prior work, first command or implementation step, expected cost, and a result that would change the next decision.

An empty queue triggers hypothesis generation and implementation. It is not a stopping condition. A fresh reviewer, when requested, evaluates evidence; it does not veto all further work just because one method has limits.

## First work, then evolve from evidence

Start independent F-only clue-key coverage and the uncovered finite block-key/F offsets. Pilot their actual costs before selecting the first tranche. A rigid-score shortlist must not control admission to an F-only search. Preserve the complete current discovery/holdout split.

Have the remaining researcher build a different useful capability. Priorities include a delimiter-aware rune language model checked on held-out solved/reference material; efficient search of exact F transitions; or periodic-key fitting that handles interruption choices. Pick based on the code and current bottleneck, not on a fixed preference in this document.

After each initial tranche, choose among:
- Extend a method's actually uncovered parameters when controls support it.
- Improve a method that fails planted recovery and then test its repaired scope on real text.
- Combine two individually tested methods when the composition has a concrete rationale.
- Test section/reset structure using documented physical boundaries, not arbitrary grouping selected for a good score.
- Use a source-grounded clue to construct a genuinely new key or transform.
- Build a small counterexample or matched synthetic test that distinguishes competing explanations.
- Independently inspect source regions implicated by a promising result, without choosing glyphs to improve its score.

Do not expand only by multiplying arbitrary constants. Explain why an expansion can resolve uncertainty. After two unrewarding expansions in one family, change a material assumption or shift resources to another family. Revisit it later only with new evidence or capability.

Maintain diversity. At least one active lane should avoid depending on the existing English quadgram ranking. Alternative views are not automatically independent evidence; record shared training sources. Non-language structure can matter, but binary-looking output is not a discovery without a justified validity check.

## Discovery standards, not a universal perfection gate

Separate:
- Exact arithmetic with a specified key/path.
- Whether search retains that path.
- Whether a language score ranks it first.
- Whether the method finds a key without being supplied the answer.
- Whether a real result is convincing.

An arithmetic defect blocks results from that implementation until isolated or repaired. It does not stop other lanes.

A 119/120 output or competing compatible path is a measured limitation. It does not prohibit exploratory decoding. Retain top alternatives, key consumption, full outputs, and uncertainty. Never relabel the original Experiment01 failure as passing.

For representative controls, compare truth survival, rank, recovery, and actual searched-key recovery. Use matched full-procedure negative searches where feasible. Rank a fitted model on text not used to fit its parameters. A high training score is not validation.

Adaptive experiments are allowed. Label them exploratory, record the additional selection, and do not claim their final selected score has an untouched-test p-value. Count actual evaluated candidates, restarts, paths, and data examined. Counts are not proof of significance or progress.

Reserve originals 4, 9, 14, 19, 24, 29, 34, 39, 44, and 54 unless the existing config documents a different already-authorised split. Do not open them merely because there is spare time. Freeze a candidate rule before validation and reveal only the required material. Each reveal is recorded and is not later reused as untouched confirmation. A local page-specific solution can be investigated without claiming cross-page uniformity.

## Productive persistence

Do not spend the session waiting for the deadline. Do not add sleeps, repeat completed cells, inflate the queue with duplicate jobs, or create empty reports to appear active. Waiting for a real computation or respecting rate-limit backoff is different; use blocking tools rather than rapid status polling.

Do not count planning documents, commits, reviews of known noise, or larger execution counts as scientific advances. Each completed batch needs new measured evidence, a tested method improvement, a source-backed observation, or a resolved ambiguity.

If two batches produce no material new evidence, the coordinator must diagnose the research loop. Assign a fresh worker to design a different discriminating experiment while another implements a concrete uncovered case. This is a change of approach, not permission to idle or terminate.

Use cached inputs and intermediate results. Keep routine audit/report work small. Do not create a new generic agent platform, dashboard, or large testing framework. Tools must have a concrete experiment that will use them during this window.

## Candidate follow-up

Inspect complete rune or byte outputs without editorial fixes. Retain non-leading alternatives from materially different models. Use cheap deterministic replay before expensive review.

For a serious candidate, freeze the construction and inputs. Have another worker implement the transform independently. Check re-encryption as consistency, key provenance, unused text predictions, and image evidence where relevant. Distinguish an exact reproducer from evidence of genuine plaintext. An arbitrary plaintext with a reverse-engineered pad is not a solution.

A promising candidate starts a verification task; it does not end the mission. A partial solution should be recorded as partial. Do not submit public claims or contact upstream without separate owner approval.

## State and checkpoints

Use these lightweight files:
- `exploration/persistent-01/STATE.md`: last substantive result, current tasks, blockers, exact next steps, worker/PID state, and clock/deadline.
- `exploration/persistent-01/QUEUE.json`: ready/running/completed/deferred jobs, with completion not equivalent to mission completion.
- `exploration/persistent-01/experiments.jsonl`: append-only experiment cards and result references.
- Per-run directories for commands, versions, seeds, candidate outputs, and measured scope.

Each experiment card contains: hypothesis; rationale; novelty versus prior work; input hashes; model/scorer; parameter bounds; controls; actual counts; outcome; limits; next decision. A brief card is enough.

Checkpoint after meaningful batches and before a context/turn boundary. Leave at least two executable next actions. Record active processes and ensure they are supervised. Do not orphan calculations or spawn detached Codex sessions. A new coordinator must check for existing workers before starting replacements.

In direct mode, give short progress updates at substantive milestones and continue. In supervised mode, end a turn with `CHECKPOINT — CONTINUE`, plus the new evidence and next exact action. The launcher, not this text, controls continuation. Do not claim execution continues after your turn unless an actual supervisor is running.

Push reviewed, focused changes to the owner's fork under the standing instruction when existing permissions allow. A blocked push does not block local research. Preserve historical results, unrelated work, secrets, and large local data. Do not bypass sandbox rules, approval rules, or quota limits. Avoid force pushes and unapproved upstream writes.

## Actual stopping conditions

End the overall session only when:
- The recorded work deadline arrives.
- The owner stops it, including the configured STOP file.
- Authentication, quota, permissions, or infrastructure prevents every useful remaining activity after bounded recovery.
- A safety or data-integrity issue requires an owner decision.
- A genuinely reproduced solution has been verified strongly enough to require owner review rather than further autonomous changes.

A failed experiment, one blocked lane, exhausted finite queue, lack of a promising candidate, completed report, or completed commit is not such a condition.

When the overall session ends, save a factual summary and exact continuation instructions. Do not claim time, CPU work, model calls, new coverage, independence, or discoveries that were not measured.

START THE NEXT REAL EXPERIMENT. Do not answer only with this plan restated.
