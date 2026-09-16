# Independent statistics and inference review

The **86 repeated-rune pairs are reproducible**, conditional on the pinned rune-only transcription. The full-length-key, unique-filter and continuous-key conclusions do **not** follow from these measurements. This audit provides explicit counterexamples; it does not propose a replacement cipher theory or conduct a key search.

## Input and implementation independence

`check_statistics.py` scans raw Unicode characters in `liber-primus/data/krisyotam_runes.txt`, counting `%` regions and `/` lines with a literal alphabet. It imports neither inherited implementations nor A's parser. Every index and raw character position in all57 nonempty segments agrees with A's frozen `parallel-01-inputs-v1` export. All55 selected segment starts/ends agree with A's page map. The page labels come from A, so this is an independent parsing check, **not an independent image-to-page-map adjudication**. Parser and data SHA256s, Python version and commit identifiers appear in `results.json`.

The selected stream has12,956 runes and SHA256 `023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585`. Original image coverage is p0–49 and p51–55; p50 contributes no rune segment. A reports that p50 contains13 alphanumeric rows and that p49/51 contain mixed alphanumeric/rune material. Thus these are **not measurements of every symbol on every puzzle page**. They do not validate the image transcription. Slash lines reflect the source transcription, not certified typographic lines.

## Recomputed measurements

| Adjacency convention | Equal pairs | Pair denominator | Rate |
|---|---:|---:|---:|
| All flattened selected runes |86|12,955|0.663837%|
| Within selected pages |86|12,901|0.666615%|
| Literally adjacent source rune characters |60|9,640|0.622407%|
| Within-line pairs across removed characters/separators |22|2,722|0.808229%|
| Across slash-line breaks within pages |4|539|0.742115%|
| Across page joins |0|54|0%|

The last four rows partition the flattened pairs. Raw gaps and both endpoint positions are in `pairs.csv` for all86 equal pairs; positions and lines are zero-based. Removing separators creates rune-stream adjacency but does not make those positions contiguous in the original text. The repeated-rune deficit persists among literal adjacent runes. `pages.csv` and `lines.csv` provide counts, denominators, frequencies, entropy and IoC by original page/source line. A section-level aggregation is **not supplied**: this bounded worker did not independently verify a section-to-original-page membership map; page and line tables preserve data for a later documented grouping.

Overall empirical symbol entropy is **4.85650361370827 bits**; IoC is **0.03447839786450569**, or **0.999873538070665 × (1/29)**. `frequencies.csv` lists all29 marginal counts (range399–492). Here IoC means `sum n_a(n_a−1)/(N(N−1))`; the normalizing multiplier is alphabet size29, **not stream length**. Entropy is `−sum p_a log2 p_a`, a marginal empirical statistic, not a bound on cryptographic security or sequence entropy rate.

Against an IID uniform29-symbol comparison, expected repeats are446.724 and the empirical reduction is80.7487%. This comparison is a specified reference model, not a universal plaintext baseline. It is also not the rejection probability of a filter. In the particular uniform-proposal repeated-rejection model, accepting an equal proposal with probability `a` gives output-repeat probability `r=a/(28+a)`. Fitting86/12,955 gives `a=0.1871163` (81.2884% rejection of equal proposals). Other proposal laws/constructions have other parameter mappings; “83%” is not a directly observed constant.

## Sensitivity and limits

All **362,768** single-rune substitutions were enumerated, with exact local repeat updates and recomputed marginal formulas: the flattened count ranges85–88; entropy4.8564800–4.8565267; IoC0.03447730–0.03447952. This is exhaustive one-symbol sensitivity, not a measured transcription error model. Each arbitrary substitution changes at most two neighboring pair indicators; correlated omission/duplication errors need separate treatment. This worker did not adjudicate uncertain glyphs; an isolated disputed glyph cannot account for the deficit, while systematic transcription effects remain unbounded here.

Excluding rune regions of mixed p49/51 leaves12,798 runes with85/12,797 repeats; including the two solved pages gives13,136 with89/13,135. These are descriptive flattened alternatives with changed joins, not equivalent ciphertext populations. No numeric sensitivity claim is made for omitted alphanumeric fields: there is no justified mapping from those fields into this rune alphabet. The data inventory gap matters for cipher inference even though it cannot change the count within the defined stream.

## Claim-by-claim inference review

**C-020 — independently supported, scoped to transcription and conventions.** Counts and denominators reproduce. Positions, separator effects and original-page labels are explicit. Image correctness and omitted regions remain outside this result.

**C-021 — independently supported marginal measurements; mechanism inference unsupported.** Entropy and IoC reproduce. A uniformly balanced deterministic periodic sequence has high marginal entropy and flat IoC without random symbols or cryptographic secrecy. These statistics alone do not measure independence.

**C-022 — conditional theorem valid; universal finite-sample exclusion invalid.** In additive arithmetic modulo29 let `D_P=P_i−P_(i−1)` and `D_K=K_i−K_(i−1)`. Under independence at this position, `Pr(C_i=C_(i−1))=sum_d Pr(D_P=d)Pr(D_K=−d) ≥ min_d Pr(D_P=d)`. The weights are nonnegative and sum to1. For varying positions, apply the per-position result and average the per-position minima. Independence conditional on position does not justify multiplying pooled increment histograms: mixing positions can induce dependence.

The formula bounds an expectation, not every realized repeat count. A finite-sample exclusion additionally needs a null distribution or dependence-aware tail bound and a justified plaintext law. Counterexample when independence fails: modulo3 choose `D_P` uniformly and set `D_K=1−D_P`; both marginals are uniform, but no sum is0. This refutes dropping the independence condition, not the conditional inequality. The executable handtest also checks an independent convolution with probabilities(.2,.3,.5) and(.6,.1,.3), yielding.26≥.2.

**C-023 — historical numbers not independently remeasured here; universal extension unsupported.** The four English corpora and German0.972% figure remain source-reported finite-corpus measurements. Corpus hashes/window choices were not reacquired in this bounded worker. There is no theorem that every natural-language rune text has a positive minimum across all29 increments: any text/window with fewer than29 transitions necessarily has an unobserved increment, and text/register/preprocessing choices alter the histogram. This refutes a universal empirical floor, not the measured historical corpus values or the usefulness of a calibrated representative-language model.

**C-024 — low-repeat observation supported; unique mechanism not identified.** Two constructions have exactly the same output transition row: (1) uniform proposals, rejecting repeat proposals unless accepted with probability `a`; (2) a direct Markov generator emitting the prior symbol with probability `a/(28+a)` and each other symbol with probability `1/(28+a)`. The second needs no rejection loop. Their entire output laws agree when initialized equally, yet their internal transitions and decoding requirements need not agree. A handtest checks the row sums. This refutes mechanism uniqueness from repeats (even from output law alone in this example); it does not explain the complete puzzle.

**C-025 — full-length necessity false as stated.** The handtest uses plaintext `P_i=i mod29` and a one-symbol repeating additive key4 over2,900 symbols. The ciphertext is balanced, entropy `log2(29)`, normalized IoC near1, with key period1. A language-like plaintext constraint would exclude this specific construction, but that extra assumption is absent from a claim of necessity based on flat IoC. This example refutes that necessity only; it is not a proposed LP plaintext. The historical period400 detection floor was not rerun and cannot be promoted from a tested grid under one simulation law into a universal cutoff.

**C-026 — finite battery does not establish OTP-class membership or information-theoretic indistinguishability.** Failure to reject two tested generators does not prove either generated the observed ciphertext, exhaust alternatives, or show equality under every possible test. True additive OTP secrecy requires a uniform independent pad, used once, at least the message length, plus the specified observation model. A deterministic generator with a short seed has a restricted keyspace; any security claim is computational or model-specific, not Shannon perfect secrecy. A filter may require additional pad symbols and synchronization state; perfect secrecy must be proved for its actual whole observation law. A failed finite derived-key dictionary search cannot identify an external pad because untested seeds, derivations, plaintexts and mechanisms remain. No preferred alternative is inferred here.

**C-027 — continuity inference invalid; weak boundary evidence.** Key reset state and output-filter state are separate. Executable example: reset key `[0,1]` for each page, encrypt plaintext pages `[0,0]`, `[1,1]`, and retain the previous output for a rule incrementing a repeat proposal. Outputs `[0,1]`, `[2,3]` have no boundary repeat despite key reset. This refutes the claimed implication, not the possibility of continuous keys. Moreover, under54 independent uniform29-symbol joins, observing0 repeats has probability `(28/29)^54=0.150329`; it is ordinary even with no suppression. A one-sided exact95% binomial upper bound on the repeat probability is5.3966%, above1/29. These calculations assume independent identically distributed joins and are illustrative, not a fitted page-boundary model. Zero boundary repeats cannot establish universal cross-page suppression.

## Execution and handoff

Run from repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python audit/parallel-01/statistics/check_statistics.py
```

Both executed runs exited0, each within300 seconds (single process, numerical libraries unused). The second added explicit filter-equivalence and reset handtests without changing measurement logic. No random sampling, seeds, external downloads, inherited imports, inherited file edits or Git writes were used. `run-output.txt` retains the final complete stdout; `execution.json` records both run outcomes. The code reruns lightweight formula controls before dataset comparisons and sensitivity enumeration. Files in this directory are the complete owned deliverable. This is a partial T5/T6 verification: section aggregation, empirical corpus-floor reproduction and systematic transcription-error modelling remain uncompleted rather than silently certified.
