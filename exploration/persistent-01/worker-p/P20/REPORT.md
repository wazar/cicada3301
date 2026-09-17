# P20 — fixed homophonic Morse separator constraint
Originals0/1 cannot share a fixed rune-to-gap partition under the frozen one/two-gap, at-most-five-dot/dash format. An exact33-node Boolean refutation proves the necessary binary relaxation UNSAT. Each page separately is SAT, so the demonstrated contradiction is specifically the shared partition across the two pages.

No dot/dash assignment search or language scoring was performed. This is not an exclusion of all Morse encodings.

## Format and exact constraints
The speculative Pollux-style mechanism assigns each of29 runes one permanent role: dot, dash or gap. Letters are A–Z/digits, with one gap between letters and two between words. The control character table follows [ITU-R M.1677-1 Annex1](https://www.itu.int/dms_pubrec/itu-r/rec/m/R-REC-M.1677-1-200910-I!!PDF-E.pdf). The one/two-gap serialization is an engineering convention, not a claim about standard physical Morse timing. Punctuation, prosigns, nulls, changing assignments and extra padding are outside the frozen format.

Let g_r be1 exactly when rune r is a gap. Every three-symbol window requires at least one nongap; every six-symbol window requires at least one gap. These constraints allow every valid A–Z/digit code but also many invalid dot/dash patterns. Therefore their contradiction is sufficient to reject the stronger grammar; satisfying them would not recover plaintext.

Original0 contributes517 clauses from262 runes; original1 contributes525 from266 runes, for1,042 jointly. Visible word delimiters play no role. Cross-page windows are omitted, and edges may cut codes. All clauses retain page, zero-based start, original rune indices and original source-character positions. Repeated rune IDs within a window are logically deduplicated into one literal.

## Exact result and certificate
No SAT/SMT package was installed. A small independently authored exact DPLL implementation uses deterministic unit propagation and Boolean branching, capped at120s or1,000,000 nodes per instance; exceeding a cap would mean UNKNOWN. No cap was reached, and no numerical MILP infeasibility status is used.

| Input | Result | Solver nodes | Seconds |
|---|---|---:|---:|
|Originals0/1, shared partition|UNSAT|33|0.00633|
|Original0 alone|SAT|59|0.00538|
|Original1 alone|SAT|41|0.00441|

The joint refutation has16 branch nodes and17 conflict leaves. It uses215 of the original1,042 clauses. The complete refutation is in actual-joint.json.gz; refutation-used-core.json maps every clause used by that proof back to its original window. This is a proof-used subset, not a minimal unsatisfiable core. Individual-page satisfying partitions are retained unchanged as witnesses to the weaker per-page condition.

The separate no-import p20_check.py independently reconstructs every original clause, checks each unit implication, confirms both assignments at every UNSAT branch, and verifies each conflict using Boolean integer logic. It checks all SAT witnesses against every source window. The certificate, not a solver status string alone, supports the joint impossibility.

## Controls and comparator behavior
Four complete solved-source rune texts are canonically expanded through the KNOWLEDGE GP table, preserving every rune-run as a word. Complete Latin, trit and original rune/character position maps are saved. Fixed random seeds partition29 output runes into10 dot,10 dash and9 gap homophones. Selection excludes the immediately previous rune; because each class has at least two choices, repeat avoidance never alters the trit sequence. Each entire encoded source is split halfway into two page-like chunks, including possible cuts inside codes.

| Source | Complete trit/rune length | Unknown separator search | Gap-role errors vs planted assignment |
|---|---:|---|---:|
|welcome|2,068|SAT|0|
|jpg107-167|1,232|SAT|0|
|p56_an_end|330|SAT|0|
|p57_parable|362|SAT|0|

These four found gap partitions happen to equal the planted ones; uniqueness was not tested or required. Full plaintext recovery under the planted dot/dash/gap roles is exact. An additional complete A–Z/0–9 fixture is SAT but its found gap partition differs on four rune IDs, correctly illustrating that a binary relaxation witness need not identify the true roles or plaintext.

Two hundred random eight-variable CNFs match exhaustive enumeration and pass proof verification. The control batch took0.20s including startup. The actual/comparator batch took0.26s; certificate replay took0.21s. All logged exits are0.

All19 frozen comparator pairs also fail the shared binary partition test. They retain actual page lengths, first symbols and exact repeat masks, with uniform selection among28 different symbols at each nonrepeat. Thus the observed contradiction is compatible with generic symbol streams; it is not a distinctive positive feature or a discovery p-value. The comparators do not preserve symbol histograms.

## Scope and retention
All27 full actual/control/comparator instances, every clause/source map, every solver proof/witness and the200 exhaustive small cases are retained, approximately0.56MB before this report/manifest. Input/source hashes and code snapshots accompany the logged commands. No reserves, original50, fresh image, extra source, new solver install or Git mutation was used.

A narrow search of persistent cards/reports found no equivalent test. A2013 artifact has a Morse-related filename, but that title was not treated as evidence for this2014 construction, and its whitespace payload was not used as a key or grammar specification.

The bound is exact for a shared fixed rune-role partition, one/two-gap serialization and maximum five signal elements per character across originals0/1. It does not cover changing page codebooks, six-element punctuation, timing-unit representations, omitted separators, multi-rune symbols or damaged/transposed input. No such variant was added after the result.

Review32 independently passed all27 full certificates,200 exhaustive small cases,1,077 tree nodes/546 leaves, all source windows, random streams, GP expansion and4,160 control emission maps. Its stricter verifier confirms the joint-only contradiction and215 used clauses. See exploration/persistent-01/review-32/REPORT.md. Its separate ITU retrieval timed out; the primary character-table inspection recorded here belongs to the experiment, not that review.
