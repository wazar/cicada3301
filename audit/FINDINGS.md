# Audit findings and open concerns

## F-001 — T0 wrapper does not propagate child failure at normal completion

**Claim:** C-037. **Status:** SOURCE_CHECKED implementation defect.
Source at `0e187df`: `audit/tools/run_t0.py:119–136`.

The wrapper records nonzero exits, caught launch errors and timeouts in per-command
JSON and continues. It has no final `sys.exit(...)` or raised aggregate error;
after normal completion it ends with a print. An unrelated uncaught exception can
still make the parent fail, so this is not a claim that the wrapper always exits 0.

**Existing-run evidence:** all five child commands in the preserved T0 manifest
exited 0, and their stdout was inspected. The defect therefore does not reveal a
hidden failed child in that run. Its presence makes the *parent exit alone* an
unsafe signal of overall success. Raw child outcomes remain intact.

**Deferred, as instructed:** runtime impact measurement, fault injection, regression
test and repair. A later repair task should stub the child commands (without
launching research checks) for all-success, exit 1, exit 2, timeout/signal and launch
error cases; measure current parent exit and artifact preservation; add a test that
fails on the current wrapper; then make and review a separate patch. Do not silently
reinterpret TIMEOUT or ERROR as a scientific FAIL. No such test was written or run
in T1, and the wrapper source is unchanged.

## F-002 — All 18 ledger warnings accounted for, none silently resolved

**Claims:** C-035–036, C-038–043, C-005–006.
The original T0 output has 11 missing-path warning occurrences covering nine
distinct paths, three missing threshold strings and four preregistration flags
that are not true. The path-existence checks in T1 confirm all nine paths remain
absent. See `LEDGER-WARNINGS.md` and the one-record-per-warning JSONL.

The latter four flags are null in the parsed entries; local PREREG documents exist.
That supports “metadata does not record true,” not the stronger historical claim
“the threshold was demonstrably chosen after results.” In particular, the archive
rescore's operative standardised contrast warrants comparison with its preregistered
raw-z flag. No chronology was verified in T1.

The same four L7 entries lack `evidence` lists. Source inspection shows the ledger
checker turns a missing list into an empty iterable, generating no missing-evidence
warning for it. Related PREREG, RESULTS and output files were located separately
and linked in the audit. This additional source-level concern is not a nineteenth
warning from the T0 command and is not experimental proof against those results.

## F-003 — Narrow test support is presented as broad trust

**Claims:** C-008–019, C-036. T0 reproduces selected-word checks and inherited
synthetic controls. The extra seven-page suite is useful additional coverage, but
it is generated from one template and still checks words/lengths rather than a
complete independently sourced plaintext fixture. Likewise, legacy oracle null
selection is narrower than candidate selection. Those are verified source limits;
their false-positive/false-negative impact is unmeasured here.

## F-004 — Descriptive statistics and mechanism conclusions are conflated

**Claims:** C-020–027. Reported counts and finite simulations are upstream of much
stronger full-length-key, unique-filter and continuity conclusions. Source documents
disagree on those conclusions and contain later narrowing evidence. No independent
statistics or mechanism experiment was run in T1. The register marks all of them
as requiring checks with stated assumptions, rather than accepting or rejecting the
headline based on the language of an inherited report.

## F-005 — Latest coverage needs arithmetic reconciliation

**Claims:** C-033–034. R26's semantic-seed table equates 4,274 rows with complete
323 × 7 × 2 coverage; the nominal product is 4,522 (248 more). Effective exclusions
or deduplication have not been examined, so this is an unresolved accounting concern.
R26 A explicitly identifies its larger count as planned with unfinished work; that
disclosure must remain attached whenever its coverage is cited.

## F-006 — Older broad closures coexist with explicit open or partial bounds

**Claims:** C-025, C-028–035, C-044–047. Examples include full-length necessity versus
a finite IoC detection floor; homophonic closure versus open surjective mappings;
~200 keytexts versus a later partially run 33-text slice; and PRNG family closure
versus a 0.5015% stated fraction of one generator/reducer space. These are reasons to
audit scope, not reasons to rerun campaigns during T1.
