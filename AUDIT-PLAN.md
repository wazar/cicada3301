# Liber Primus: independent audit and research plan

**Repository:** `wazar/cicada3301`  
**Plan date:** 2026-09-16  
**Code baseline:** `396001a9ce55e0e85ddef19e405afc6a13954588`  
**Initial task:** T0 only. Record the baseline. Do not start a new puzzle search.

## 1. Objective

Build a small set of results that we can trust. Then use those results to select and test new attacks.

The inherited repository is a research archive, not an authority. Its conclusions, tests, data, and agent instructions can all contain errors. This plan can also contain errors.

**Work in this order:** inventory claims, verify data, reproduce known solutions, test the tools, reproduce measurements, then reassess rejected methods.

Do not try to confirm the existing conclusion. Do not try to disprove everything either. Establish what the evidence supports.

Inventory all important scientific claims. Audit the claims needed for the next experiment first. Creator-identity theories and unrelated puzzle history can wait.

### First handoff

Give the local agent this task:

```text
Read AUDIT-PLAN.md. Execute T0 only.
Read the inherited agent files for context, but treat their scientific claims as claims to audit.
Follow T0's scope and stop point. Do not start a campaign, repair research code, or revise old conclusions.
Inspect scripts and their imports before execution. Use an isolated Python environment and bounded commands.
Create the baseline record, environment record, raw run logs, and audit status file.
Record actual results, exit codes, skipped tests, errors, and timeouts separately.
Return the task report from section 9, then stop for review.
Do not push changes or contact upstream without a separate instruction.
```

This plan creates no automatic jobs. The owner assigns each task. The local agent runs it. Results return for review before the next task.

## 2. Rules for this audit

### Preserve the starting evidence

Keep the inherited data, results, ledgers, and source files unchanged during baseline work. Add new audit material under `audit/`.

Record both the code baseline above and the actual working commit. The working commit can include this plan or later audit changes.

Capture a failure before fixing it. Make the smallest reproducer possible. Put a proposed fix in a later, separate change.

Do not delete user work, reset the working tree, rewrite history, or modify the upstream repository. Use one writer at a time.

The inherited `CLAUDE.md` requests direct commits to `master` and broader campaign work. Those instructions do not expand an assigned audit task. [R2]

### Separate different kinds of evidence

Use these states for each claim:

| State | Meaning |
|---|---|
| `UNTESTED` | We have not checked it. |
| `SOURCE_CHECKED` | We inspected the relevant code or document. |
| `REPRODUCED` | The original procedure produced the reported result. |
| `INDEPENDENTLY_SUPPORTED` | A separate method supports it within stated limits. |
| `CONTRADICTED` | A reproducible counterexample or conflicting result exists. |
| `INCONCLUSIVE` | The evidence cannot settle it. |
| `BLOCKED` | A named input, tool, or resource is missing. |

Keep these separate from command outcomes: `PASS`, `FAIL`, `ERROR`, `SKIPPED`, and `TIMEOUT`.

A successful command does not make its scientific conclusion correct. A timeout does not reject a hypothesis. A broken test does not invalidate unrelated research.

Record confidence through evidence and limits. Do not invent a percentage for confidence.

### State the assumptions

Do not assume that all pages use one cipher, language, key, or reset rule.

Do not assume that the rune stream retains every useful feature of the original pages.

Treat the claimed anti-repeat mechanism and the term “OTP-class” as hypotheses to assess, not starting facts. [R1] [R3]

A random-looking result does not identify its generating mechanism. A model that produces one observed pattern does not establish that it produced the puzzle.

A failed finite search only addresses its tested keys, transforms, input versions, and detection rules.

### Keep the local work bounded

Use a separate Python environment. Inspect code, imports, package metadata, and tests before running them. A virtual environment isolates packages; it is not a security sandbox.

For the first pass, use at most two CPU workers and a 300-second limit per command. These are starting limits, not runtime estimates.

Record a timeout and defer that run. Do not silently increase limits, start all-core searches, or launch background workers.

Do not run downloaded puzzle binaries. Do not access unrelated local files, credentials, or private accounts.

Do not use paid APIs, upload local material, or fetch large archives without a separate instruction. Keep permitted source downloads separate from offline tests.

## 3. Evidence layout

Create these files as their tasks require them. Do not fill them with invented results.

```text
audit/
  STATUS.md                 Current task, evidence summary, blockers, next decision
  BASELINE.md               Original test results and baseline limits
  environment.json          Python, macOS, architecture, packages, source revisions
  CLAIMS.jsonl              One claim per line, with dependencies and evidence
  FINDINGS.md               Confirmed defects and unresolved concerns
  DECISIONS.md              Reasons to retain, narrow, or reopen conclusions
  data/                     Input manifests, page map, transcription differences
  reference/                Independently sourced known-solution fixtures
  tools/                    Small audit helpers and independent implementations
  tests/                    Audit tests, including defect regression tests
  runs/T0/<run-id>/          Commands, stdout, stderr, exit codes, result manifest
  reports/T0.md             Completed task report
```

Use a new run directory for every run. Never overwrite the only copy of an earlier result.

For each run, record the command, working directory, timestamp, source commit, local code changes, input hashes, seeds, limits, duration, and exit status.

Record only the environment values needed for reproduction. Do not dump the complete process environment. Remove tokens and private paths before committing logs.

Keep large downloaded inputs outside Git. Record their source, retrieval date, checksum, and retrieval method. Retain small raw results needed to inspect a finding.

### Claim record

Split compound statements into separate claims. Use stable IDs such as `C-001`.

```json
{
  "id": "C-001",
  "claim": "Exact claim, with its scope preserved",
  "kind": "measurement",
  "source": {"commit": "...", "path": "...", "lines": "..."},
  "depends_on": [],
  "assumptions": [],
  "tested_scope": {},
  "not_tested": [],
  "reproduce_command": null,
  "expected_result": null,
  "observed_result": null,
  "evidence_paths": [],
  "status": "UNTESTED",
  "impact_if_wrong": "Which research decisions would change",
  "next_check": "Smallest useful check"
}
```

Use `kind` values such as `data`, `implementation`, `measurement`, `mechanism`, `search_bound`, and `interpretation`.

Keep an inherited ledger ID beside the new claim ID where applicable. Do not silently relabel the inherited ledger.

## 4. Starting observations and questions

These are starting leads, not a completed audit. They refer to the pinned code baseline. A later revision can change them.

### O1. Known-solution coverage

`tests/validate.py` contains five page entries. It checks selected words in decoded text rather than comparing complete expected outputs. [R4]

**Established by source inspection:** this script alone does not establish complete coverage of all solved material.

**Still to check:** whether other tests provide that coverage. Build a coverage map before describing this as a repository-wide gap.

### O2. Constant wrong-key control

The solution checker's self-test constructs its wrong key with:

```python
[random.Random(4242).randrange(N) for _ in range(4096)]
```

It recreates the generator on each iteration. With `N = 29`, an isolated Python check produced 4,096 copies of `27`. [R5]

**Established:** this control is constant, not a varied pseudorandom sequence.

**Not established:** that this defect caused a false acceptance or invalidated any particular campaign.

Test that impact before making a broader claim. Keep the constant control as a distinct test case when adding varied wrong keys.

### O3. Ledger validation is not experiment validation

`validate_ledger.py` inspects recorded fields and evidence paths. It does not rerun every experiment behind those fields. [R6]

**Audit question:** which conclusions have direct raw evidence and independently checked controls?

Also test malformed entries, missing evidence, summary counts, and exit codes. Do not treat a successful ledger check as proof of scientific validity.

### O4. The solution checker has a limited model

`judge_keystream()` starts each segment with the same key sequence at offset zero. Its self-test also resets the key for each synthetic page. [R5]

**Audit question:** what happens with a continuous key sequence, section resets, per-page keys, or a different skip rule?

English scoring and a two-page requirement are detector policies. They are not requirements that every genuine partial solution must satisfy.

### O5. Data scope needs a page map

The repo describes 12,956 runes, pages 0–54, and 57 segments. Its loader separates the final two segments as solved material. [R3] [R7]

CicadaSolvers describes 58 LP2 pages, with 56 unsolved pages and solved pages `56.jpg` and `57.jpg`. [R8]

**Audit question:** how do original filenames, displayed pages, parsed segments, and excluded material map to each other?

Do not call this a missing-page defect before checking the mapping. Do not force the input to match a target count by dropping data.

### O6. Candidate selection and null calibration may differ

The checker selects across decoder types and signs. Its shuffle comparison uses one decoder/sign setting on the first segment. [R5]

**Audit question:** does that comparison calibrate the actual selection procedure, across all tested pages and candidates?

This is a calibration concern from source inspection. It is not yet a measured false-positive rate.

## 5. Task queue

Each task ends with a report. Complete only the assigned task. Later tasks may start with unresolved findings, but must state which conclusions remain blocked.

### T0 — Capture the unchanged baseline

**Goal:** establish what runs, on which inputs, before repairs.

Inspect `AGENTS.md`, `CLAUDE.md`, package metadata, relevant test configuration, and the scripts below. Trace imports for downloads and other side effects. [R1] [R2] [R9]

Record Git state, platform, architecture, Python version, dependency versions, available inputs, and the planned run limits.

After inspection and environment setup, attempt these commands from the repository root:

```bash
python3 liber-primus/tests/validate.py
python3 liber-primus/verify_solution.py --selftest
python3 -m pytest liber-primus/benchmark/ -q
python3 liber-primus/analysis/handoff/validate_ledger.py --strict
```

Run each through a timeout/logging wrapper. Preserve the actual exit code. Do not let a logging pipeline hide a failure.

List the tests collected, tests skipped, and missing inputs. Check collection code before collecting tests. Do not run every historical campaign.

**Deliver:** `audit/BASELINE.md`, `audit/STATUS.md`, `audit/environment.json`, run logs, and `audit/reports/T0.md`.

**Done when:** each command has a recorded result, or a specific reason why it was not run. Include current limits.

**Stop:** report failures without fixing them. Do not claim the repository is validated, even when all commands pass.

### T1 — Build the claim and dependency register

**Goal:** identify the assertions that control research decisions.

Start with the README, agent files, `PROBLEM.json`, `LEDGER.json`, solver dossier, synthesis documents, and the corresponding implementation files.

Extract measurements, claimed mechanisms, excluded methods, and acceptance rules. Record exact locations and the evidence they cite.

Prioritise data identity, page coverage, detector limits, repeated-rune statistics, and claims that reject whole cipher families.

Mark contradictions between documents. Treat generated summaries as derived outputs, not independent sources.

**Deliver:** `audit/CLAIMS.jsonl`, a dependency summary, and `audit/reports/T1.md`.

**Done when:** every high-impact headline claim has a source, dependencies, assumptions, and a proposed check. List documents not yet reviewed.

### T2 — Verify inputs and page coverage

**Goal:** establish exactly what each script analyses.

Build a page map from original filename to source image, transcription, parsed segment, solved status, rune count, and stream offset.

Identify duplicates, omissions, merges, headers, numbers, and artwork-only material. Keep original page boundaries, lines, separators, and alternate readings.

Recompute raw-file hashes and the repo's normalised-stream hash. A matching hash proves agreement with that copy, not correctness of its transcription.

Compare with a separately obtained source. Record whether the sources share a transcription ancestor. Two copied websites are not independent evidence.

Read clear image regions directly. Record uncertain runes as alternatives. Do not use an English score to silently choose a transcription.

Start with solved controls, page boundaries, and claimed repeated-rune sites. This targeted check does not establish full transcription accuracy.

**Deliver:** page map, source manifest, transcription differences, excluded-material list, and `audit/reports/T2.md`.

**Done when:** the 55/56-page and 57/58-segment descriptions are explained, or the exact unresolved mapping is documented. Preserve separate dataset versions.

### T3 — Build complete known-solution tests

**Goal:** create an independent correctness reference.

Inventory all known solved material from separately checked sources. Distinguish pages without ciphertext from pages that require decryption. [R8]

For each applicable page, record input runes, complete expected rune output, readable text, transform, key, and special rules.

Compare rune indices before comparing expanded Latin text. Document spelling and transliteration alternatives explicitly.

Implement a small reference decoder without importing the research decoder. Do not derive expected outputs from the implementation under test.

Include hand-worked arithmetic cases, full-page comparisons, and appropriate re-encryption checks. Change one rune or key position and verify that the test detects it.

Account for every page in the solved inventory. Do not require a cipher test for a page with no encrypted text.

**Deliver:** fixtures, independent reference code, coverage map, tests, and `audit/reports/T3.md`.

**Done when:** each applicable known solution matches in full, or has a documented discrepancy. Selected keyword matches are not sufficient.

### T4 — Test the candidate detector and its limits

**Goal:** measure what the tool can recover and what it can falsely accept.

First write small tests for O2, O3, O4, and O6. Reproduce defects before preparing patches.

Use many declared seeds for correct and wrong keys. Keep constant, random, periodic, shifted, and near-correct keys as separate cases.

Use an independent data generator. Test reset-per-page and continuous keys, alternative skip rules, different lengths, language variants, and modest transcription errors.

These are test cases, not claims about the real puzzle. An unsupported model must be labelled unsupported, not rejected as impossible.

Keep test text separate from score training or tuning text where possible. Use hidden planted cases generated before the recovery agent sees them.

Measure rune recovery, alignment, false acceptance, and missed correct keys. Report counts and uncertainty. Zero failures in a finite sample does not prove zero risk.

Replay the full selection process on negative controls. Include all signs, decoder choices, pages, offsets, and parameter choices used to select the reported candidate.

Check whether shuffled data are a suitable comparison for the question. Document which structure the shuffle preserves or destroys.

**Deliver:** defect reproducers, regression tests, a detector coverage matrix, calibration results, proposed separate patches, and `audit/reports/T4.md`.

**Done when:** every claimed detector capability has a test and a stated limit. Unchecked capabilities remain untrusted.

### T5 — Recompute the main statistics independently

**Goal:** separate measurements from explanations.

Do not reuse the original statistics functions for the independent calculation. Use the verified input version, or clearly label a provisional version.

Recompute symbol counts, repeated neighbours, entropy, and index of coincidence. The last measure describes how often two sampled symbols match.

Report results by page and section, then for the combined stream. Specify the denominator and treatment of every boundary and separator.

For repeated neighbours, compare boundary-preserving and flattened counts. Test sensitivity to disputed runes and page exclusions.

Use small hand-checkable inputs to test the formulas. State each simulated comparison model and its limits before examining its results.

Compare explanations for any confirmed pattern. Failure to distinguish two models does not prove that either generated the puzzle.

**Deliver:** independent calculation code, raw result tables, sensitivity checks, claim updates, and `audit/reports/T5.md`.

**Done when:** the high-impact measurements are reproduced, contradicted, or explicitly unresolved. Keep mechanism claims separate.

### T6 — Reassess rejected approaches

**Goal:** convert broad rejection claims into tested bounds.

Prioritise conclusions affected by T2–T5. Trace each through its script, raw output, controls, thresholds, and actual search coverage.

Record keys, generator versions, parameter ranges, offsets, reset rules, skip models, languages, and pages tested. Record omissions and early termination.

A control must run through the actual search procedure. Giving the decoder the correct key does not prove that the search would find it.

Challenge a broad rejection with a planted example inside its claimed coverage. Success outside that coverage only identifies an untested region.

Propose the smallest rerun needed to measure impact. Do not automatically rerun a large campaign after finding one defect.

Where possible, replace broad wording with: “No candidate was found within X, using Y, with detection tested under Z.”

**Deliver:** bounded conclusions, a reopen list, proposed reruns, and `audit/reports/T6.md`.

**Done when:** the important conclusions have explicit supported limits. Leave unaudited claims labelled unaudited.

### T7 — Select one new experiment

**Goal:** resume puzzle work without waiting for a perfect archive-wide audit.

Choose one experiment whose required data and tools have passed the relevant checks. Compare a few options by evidence, cost, and ability to distinguish hypotheses.

Before running, write the hypothesis, alternatives, exact input version, search bounds, controls, selection rule, compute limit, and stop conditions.

Reserve material not used to choose the method for later validation where practical. Do not require every page to use the same mechanism.

Accept a reproducible single-page advance as a possible partial result. Do not call it a full solution.

Require a justified key or transform, not just readable text. In an additive cipher, arbitrary text can be made to fit by defining a matching key.

Re-encryption is a consistency check, not proof by itself. Seek additional constraints, independent reproduction, and successful predictions on unused material.

**Deliver:** one experiment proposal and `audit/reports/T7.md`.

**Stop:** obtain approval for that experiment before starting its search.

## 6. Independence requirements

Using a different AI model does not make a check independent.

For each independent result, name what is separate: source transcription, parser, implementation, expected output, data generator, or review.

Where practical, let one agent implement from the written specification without seeing the original output. Have another compare the results afterwards.

Two implementations that share the same wrong parser are not independent checks of the input.

Do not use an AI's familiarity with known plaintext as evidence of successful decryption. The recorded transform must produce the result mechanically.

## 7. Gates for new puzzle searches

Do not start a large search until its specific dependencies meet these conditions:

- The input version and page scope are known. Relevant transcription uncertainty is represented.
- Complete known-solution tests cover the reused operations.
- The actual search recovers independent planted cases within its claimed model.
- Candidate selection has suitable negative controls and a recorded trial budget.
- Important inherited rejection claims are supported or set aside explicitly.

These gates apply to the proposed search, not to every possible future approach. A failure in one method must not block unrelated well-tested work.

Do not declare the puzzle impossible from failed searches, random-looking statistics, or the age of the problem.

## 8. Changes and reporting discipline

Keep each change small: baseline capture, test, fix, or interpretation. Avoid combining them in one change.

Before changing research code, show the failing case and name the affected claims. After the change, compare old and new behaviour on the same inputs.

Do not rewrite old results as though the corrected code produced them. Mark them for rerun or narrow their interpretation.

Track the current task and next decision in `audit/STATUS.md`. Keep untested concerns separate from confirmed findings.

The agent may prepare local changes for review. It must not push, open upstream issues, or make public solution claims without an explicit instruction.

## 9. Required task report

Use this structure in `audit/reports/T<number>.md` and in the agent's handoff:

```text
Task:
Code baseline and working commit:
Files changed:
Commands actually executed:
Inputs, hashes, seeds, and resource limits:
Observed results and raw evidence paths:
Claims supported, contradicted, or still untested:
Assumptions and limits:
Errors, skipped work, timeouts, and blockers:
Smallest useful next task:
Decision needed from the owner:
```

Lead with the result. Include enough detail to reproduce it. Distinguish “I inspected,” “I ran,” and “I inferred.”

Do not report a planned command as executed. Do not report a passing self-test as a puzzle solution.

## 10. Source references

Repository references are pinned to the code baseline. They document what this plan inspected, not independent proof that the research is correct.

[R1]: https://github.com/wazar/cicada3301/blob/396001a9ce55e0e85ddef19e405afc6a13954588/AGENTS.md
[R2]: https://github.com/wazar/cicada3301/blob/396001a9ce55e0e85ddef19e405afc6a13954588/CLAUDE.md
[R3]: https://github.com/wazar/cicada3301/blob/396001a9ce55e0e85ddef19e405afc6a13954588/liber-primus/PROBLEM.json
[R4]: https://github.com/wazar/cicada3301/blob/396001a9ce55e0e85ddef19e405afc6a13954588/liber-primus/tests/validate.py
[R5]: https://github.com/wazar/cicada3301/blob/396001a9ce55e0e85ddef19e405afc6a13954588/liber-primus/verify_solution.py
[R6]: https://github.com/wazar/cicada3301/blob/396001a9ce55e0e85ddef19e405afc6a13954588/liber-primus/analysis/handoff/validate_ledger.py
[R7]: https://github.com/wazar/cicada3301/blob/396001a9ce55e0e85ddef19e405afc6a13954588/liber-primus/analysis/round11/lib_numchannel.py
[R8]: https://www.cicadasolvers.com/quickstart/
[R9]: https://github.com/wazar/cicada3301/blob/396001a9ce55e0e85ddef19e405afc6a13954588/liber-primus/pyproject.toml

External page checked on 2026-09-16. Recheck its claims when assembling the independent source inventory.

---

**First milestone:** a recorded baseline, a verified input map, complete reference tests, and measured detector limits.

**Research goal:** a reproducible advance on the puzzle, not a more confident summary of inherited claims.
