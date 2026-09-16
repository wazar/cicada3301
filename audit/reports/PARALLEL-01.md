# PARALLEL-01 — checked research base and bounded next experiment

**We now have a usable, limited research base. The rune-stream identity and main
counts check out; several inherited tests and strong conclusions need narrowing.**
No new key search was run. The audit runner was repaired. Independent workers and
a fresh reviewer tested code, fixtures and outputs before integration.

For the owner: the repository contains real, reproducible measurements, but those
measurements do not establish that the puzzle requires a full-length key, uses a
unique anti-repeat filter, or cannot reset keys between pages. Some “known solution”
tests also pass while dropping real letters. We have complete reference comparisons
and measured detector limits now, so the next experiment can begin with specific
controls instead of assuming that the old passes validate everything.

## What we can use, within limits

| Checked result | Scope we trust |
|---|---|
|12,956 runes and exact pinned SHA256 | Identity of the specified rune-only transcription, independently parsed by A/D and checked by reviewer |
|58 images /57 nonempty segments | Complete filename inventory; targeted p49–51,55–57 transition confirmed; other spatial joins remain provisional |
|58/58 image SHA1 matches | Byte agreement with freshly retrieved archive metadata, not image authorship or absence of hidden content |
| Nine complete reference groups,2,979 runes | Independent rules match source-backed expected arrays;8 hand checks and11 mutation checks pass; image ancestry and LP1 page cuts remain limited |
|86 repeats, entropy4.85650361370827, IoC×29=.999873538070665 | Independent measurements with explicit boundary treatment, not cipher identification |
| Bounded legacy reset-English detector |40/40 synthetic instances accepted;79/80 pages exact;0/100 varied wrong keys per length; one blinded8-key search recovers240/240 runes |
| Audit-runner repair | All-success parent0; five distinct failure stimuli parent1 with child outcomes/logs preserved; import runs no checks |

The frozen dataset is `parallel-01-inputs-v1`, [dataset](../parallel-01/inputs/dataset.json)
and [page map](../parallel-01/inputs/page-map.json). The normalized unsolved hash is
`023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585`.
A publishes it before downstream work; D independently parses raw input before
comparing every array and source position. Three local transcription arrays agree,
but shared ancestry prevents treating them as independent image witnesses.

## What failed or changed

**The input is narrower than the puzzle.** p50 is omitted by the rune parser but
contains13 alphanumeric rows. p49 andp51 contain mixed rune/alphanumeric fields.
A rune hash match does not justify discarding that content from research reasoning.
Targeted image checks and coordinates are in the [input report](../parallel-01/inputs/REPORT.md).

**Keyword passes hide real errors.** The inherited seven scripts all PASS, yet
three keyed outputs delete plaintext F; WELCOME also selects the wrong interruption
path. Only three outputs equal complete corresponding reference groups. Koan's
742-rune subsection is correct but omits a38-rune instruction. Two local transcription
discrepancies were found; p57 E/Y was visually checked as Y, while a missing O in the
LP1 loss-of-divinity group remains unresolved. No inherited code or data was changed.
See [complete comparisons](../parallel-01/reference/REPORT.md).

**Detector acceptance is not exact recovery.**20/20 continuous-key instances are
rejected at the legacy reset interface.20/20 vowel-removed instances are rejected.
Two unsupported skip-by-two cases PASS despite selected page recoveries as low as
65%. R19's pair preset does much better on that transition:39/40 pages exact, but
its wrong-key calibration was not rerun. Full selection gives larger shuffled maxima
than the narrower production null.0/100 varied-key acceptances still permits a
2.95% one-sided95% upper bound under each tested fixed-ciphertext distribution.
These results cannot certify a billion-trial search or a new candidate-set maximum.
See [detector results](../parallel-01/detectors/REPORT.md).

**The repeat deficit is real; its interpretation was overstated.** Of86 repeated
pairs,60 are literal source neighbors,22 span separators, and4 span slash-line breaks.
None crosses the54 page joins. Denominators are12,955 flattened and12,901 within
pages. All362,768 single-rune substitutions leave85–88 repeats, a bounded sensitivity
check rather than a transcription-error model. Zero repeats in54 independent uniform
joins has probability0.150329; it does not establish a continuous key. Explicit
counterexamples also refute full-length-key necessity from flat IoC and unique
filter identification from output statistics. They do not identify a replacement
cipher. [Measurements and derivations](../parallel-01/statistics/REPORT.md).

**The runner defect is fixed.** Temporary stub commands reproduced the original
parent-zero behavior for exit1, exit2, signal, timeout and launch error. The small
repair adds an inert import guard and aggregate failure exit. No live inputs were
corrupted and no real T0 failure was induced. Original T0 evidence is unchanged.
[Before/after logs and tests](../parallel-01/runner/REPORT.md).

## What remains uncertain or blocked

- Full image transcription, source genealogy, complete region inventory and LP1
  physical-page cuts remain unverified. The complete solution comparisons are
  group-level references, not a new blind image transcription.
- The historical indel bound, separator adjudications and English/German corpus
  increment floors were not reproduced. Statistics by verified section are absent.
- I2 execution is blocked by missing `models/panel.npz`. R21 work checks retained
  table arithmetic, not regenerated populations or end-to-end certification.
- All18 ledger warnings remain accounted for and unresolved. Missing historical
  artifacts and R26 coverage arithmetic were not replaced with new assumptions.
- Actual cipher family, language, key length, reset policy and treatment of
  alphanumeric material remain unknown.

T2 input identity and targeted mapping are delivered; complete visual coverage is
partial. T3 has complete group fixtures but partial physical-page certification.
T4 is a bounded capability study with a blocked later model. T5 core measurements
are delivered, with sections/corpus/error-model work incomplete. T6 reasoning is
partially checked; historical campaign validation remains incomplete. **This is
not completion of every task in T2–T6.**

## Review, execution and evidence limits

Entry commit: `95e11e918ace77a51de4b612a48e74c298e67e58`.
Inherited baseline: `396001a9ce55e0e85ddef19e405afc6a13954588`.
Actual agents: `/root/inputs`, `/root/reference`, `/root/detectors`,
`/root/statistics`, followed by fresh `/root/review`. Runtime permits four total
agents including coordinator; A/B/C ran concurrently, D started when A finished,
and reviewer started when B finished. No nested agents. See
[assignment record](../parallel-01/ASSIGNMENTS.md).

Fresh review independently confirmed the stream hash, all86 repeat positions and
denominators, nine complete fixture comparisons including a separately implemented
85-rune totient decode, detector counterexamples, all six runner cases, and the
p50 image. It accepted scoped results and narrowed the next-experiment statistic
and tie rule. [Review report](../parallel-01/review/REPORT.md).

The existing Python3.12.14 environment was reused; numeric libraries had one thread,
at most two heavy jobs, routine300-second limits. No limit increase, installs,
paid services, large archive downloads or puzzle binaries. Small public source
retrievals have URLs/dates/hashes. No full T0 rerun; C repeated the oracle selftest
once to compare its legacy control with fresh independent plants. A/B source and
comparison checks, C pilot/main/blind/lightweight tests, D formula/count/sensitivity
runs, coordinator fixtures and reviewer reruns are recorded in each directory.

Final check commands passed; discrepancies are data, not silently swallowed test
failures. Expected timeout/signal/launch-error stimuli belong only to runner tests.
Three attempted source URLs returned404; unrelated work continued. Audit-helper
errors were corrected before final comparisons or the frozen detector batch.
Evidence-history limits remain explicit: D overwrote its first stdout and lacks
per-run timing metadata; C did not preserve its initial failing mapper source/raw
traceback. Final evidence and independent review remain available; missing history
was not fabricated. B's private path prefixes were redacted in metadata/raw fetch
output, with hashes and disclosure in
[publication-redactions.json](../parallel-01/coordination/publication-redactions.json).
Reproduce scripts in a temporary copy to avoid overwriting preserved fixed-name logs.

## Which rejections to retain, narrow or reopen

Retain measured finite negatives only with their actual inputs, keyspace, offsets,
transitions, register, controls and stopping bounds. Reopen unconditional full-key
and no-reset implications and full known-solution-fidelity claims. Narrow legacy
and later detector claims separately. Treat OTP-class and unique-filter conclusions
as unresolved. Other running-key, PRNG, numeric and fractionation closures remain
historical finite bounds pending campaign-specific checks; this work does not
establish that every past negative was wrong. [Decision table](../DECISIONS.md).

## One proposed first puzzle experiment — not run

A small **solved-recipe reuse recheck**: freeze four2,048-symbol key arrays from
DIVINITY, literal FIRFUMFERENFE, primes, and prime totients. Test both arithmetic
signs and rigid/legacy beam400/max_skip3, offset0 and per-page resets, on only the
first120 runes of original LP2 pages0 and1. This uses known solved clues and is not
claimed to be previously untried.

Before touching those slices, require fresh plants using these actual structured
keys, exact recovery and correct tied-ranking behavior; then calibrate the maximum
over the entire frozen hypothesis set and check held-out negatives. The same recipe
and sign must apply to both pages. Any failed control stops the experiment without
a puzzle result. Stop at the fixed scope or finite budget; no adaptive expansion.
Any flag needs independent complete-output follow-up, and a miss rejects only this
small setup. [Exact controls, threshold and stop rule](../parallel-01/coordination/PROPOSED-EXPERIMENT.md).

Only assignment changes are to be committed and pushed to the owner's fork.
Unrelated macOS setup work remains separate. **Stop after publication; no proposed
puzzle experiment is authorised to run by this report itself.**
