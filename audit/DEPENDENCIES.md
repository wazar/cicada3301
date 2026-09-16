# T1 claim dependencies

The register contains 47 scoped claims. `SOURCE_CHECKED` means the statement or
implementation was inspected, **not that its scientific conclusion is accepted**.
Only C-008 and C-010 carry `REPRODUCED`, specifically for the narrow T0 checks whose
raw logs already exist. No claim is newly experimentally reproduced by T1.

Each JSONL row includes source commit, line range and verbatim excerpt, assumptions,
dependencies, inherited ledger IDs, reported coverage and omissions, evidence paths,
impact if wrong and the smallest proposed check. `reproduce_command: null` means
no reproduction was undertaken or approved in T1; `next_check` is a proposal.
Reported coverage is kept distinct from the audit's own tested scope. Ledger text
is copied as evidence of what was claimed, not adopted as an audited bound.

## The dependency chain that matters

| Layer | Claims | Depends on | What becomes unsafe if unsupported |
| --- | --- | --- | --- |
| Object and page identity | C-001–003, C-007 | Source bytes, rune mapping, source ancestry | Comparing any result with the claimed LP2 object |
| Transcription and separators | C-004–006 | Correct image/page joins and independent controls | Exact counts, per-page experiments and alignment-sensitive decodes |
| Known-solution correctness | C-008–009 | Correct inputs and separately justified expected outputs | Reusing arithmetic, interrupter or parser operations as trusted primitives |
| Legacy detector | C-010–016 | Plant construction, decoder transitions, language/register and selection model | Interpreting a miss as a negative or a high score as a meaningful candidate |
| Later detector generations | C-017–019 | Mode-specific controls and appropriate panel/null calibration | Crediting later capabilities to earlier runs; automatic solution certification |
| Descriptive statistics | C-020–021 | C-001–005 and explicit boundary conventions | Repeated-rune anomaly and marginal distribution statements |
| Statistical/model inference | C-022–027 | Descriptive statistics, plaintext law and model assumptions | Full-length-key necessity, filter uniqueness, reset policy and OTP-class interpretation |
| Search/exclusion bounds | C-028–035, C-043, C-046–047 | Data identity plus the **actual** generator, search selection, transition and register | Family-wide exclusions from finite or underpowered searches |
| Evidence/accounting infrastructure | C-036–039, C-044 | Raw child results, ledger fields, historical chronology | Mistaking metadata success or current summaries for complete research support |
| Artifact and clue provenance | C-040–042, C-045 | Authentic bytes, controls and retained primary evidence | Software/generator priors and broad claims of payload absence |

The dependency edges in `CLAIMS.jsonl` express prerequisites for interpreting claims.
An edge does not endorse either endpoint. Later models must be linked to the exact
campaigns that used them; they do not retroactively repair an old null.

## Five highest-impact claims to check next

1. **C-002 — the page map and input scope** (with C-001/C-003).
   R19 already offers an explanation: p50 is an illustration without transcribed
   runes, and later image numbers shift relative to parsed segments. Verify that
   explanation directly and retain illustration/header content rather than calling
   the discrepancy a missing-page defect. Output: versioned image → transcription
   → segment map and independently computed normalised hash. This is T2 work.

2. **C-008 — the advertised known-solution trust anchor** (with C-009).
   T0's five keyword checks pass. A separate seven-page suite exists and includes
   AN END, so the gap is not simply “only five pages have ever been checked.” Both
   inspected suites lack full independently sourced expected-rune assertions.
   Output: solved-material inventory and complete reference fixtures. T3 work.

3. **C-015 — whether candidate selection is properly calibrated**
   (with C-010–019). Start by mapping the actual tool versions and modes used by
   each relevant campaign. Then test the full selection pipeline, not a smaller
   null procedure or a known-key decoder alone. Output: per-mode/register/reset
   coverage and error measurements, with unsupported cases explicit. T4 work.

4. **C-020 — the repeated-rune count and its sensitivity.**
   Independently recompute the reported 86 pairs under explicit image, segment,
   line and flattening conventions after input verification. Use uncertain readings
   as alternatives. Output: raw counts, denominators and sensitivity table. T5 work.

5. **C-026 — what supports the OTP-class headline** (with C-022–025/C-027).
   Separate finite-battery non-separation from formal indistinguishability and
   unique cipher identification. The doublet floor additionally needs its
   independence, plaintext-law and finite-sample assumptions. Output: an explicit
   supported model bound, or a documented inability to infer one. T5/T6 work.

These are a dependency-ordered shortlist, not permission to begin all five tasks.
The next smallest assignment is T2. A separate repair task can address C-037
before any future automation depends on the T0 runner's parent exit code.

## Current contradictions and scope mismatches

- **Page labels:** dossier image pages 0–55 versus PROBLEM's segments 0–54.
  R19 gives a specific reconciliation; T1 has not independently verified it.
- **Transcription:** the dossier calls consensus “correct” while admitting shared
  ancestry. R19 adds controls, but its bitmap labels use other canon occurrences
  and its forced alignment uses canon context. These are useful conditional audits,
  not a wholly independent blind transcription.
- **Known solves:** README/dossier say the validation reproduces every solved page;
  source checks five selected-word entries. Seven separate generated scripts also
  use word checks and shared data. The full-page trust claim exceeds these checks.
- **Key length:** dossier says flat IoC requires full-length keys; B4's later
  period ladder and D2 discussion explicitly limit that inference.
- **Mechanism/secrecy:** FINAL-SYNTHESIS retracts unconditional unsolvability near
  its beginning but retains an external-pad pinned construction and strong closure
  language later. README and R26 still promote bounded nulls into a broad headline.
- **Reset rule:** dossier asserts one continuous key; the legacy oracle restarts
  it per segment. Filter state and key state are different variables.
- **Detector era:** R18 documents legacy transition/register failures; R19 builds
  extensions. The legacy oracle still imports `skipdecode`. R21 then withholds
  no-oracle HIT certification. None of these statements can stand in for the others.
- **Metadata:** four L7 preregistration flags are unset although PREREG prose exists.
  Their ledger `evidence` lists are also absent; the validator does not warn on an
  empty list. Chronology and the operative archive statistic require later checking.
- **Coverage:** R26 C reports 4,274 rows as 323 × 7 × 2 (nominally 4,522).
  This is an accounting question, not proof that a scientific result is false:
  deduplication or excluded combinations may explain it. R26 A separately admits
  its quoted larger baseline count is planned, not completely executed.

All are retained in the audit; no inherited document or conclusion was rewritten.
