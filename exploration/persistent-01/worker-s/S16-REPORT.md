# S16 — canonical circular words under an unknown alphabet order

Originals 0 and 1 each contradict the hypothesis that every explicit word is emitted as its lexicographically least cyclic rotation under a fixed, unknown alphabet order. Each page has a two-word proof requiring both a < b and b < a. Separate orders were allowed for the two pages, so a shared-order assumption is unnecessary.

## Mechanism and scope

The verified p57 instruction containing “circumferences” motivated testing one precise circular-object representation. This is an interpretation chosen for falsifiability, not an established meaning of the clue. An encoder takes a circular rune word and prints its least rotation under one total alphabet order. Repeated runes, periodic words, tied identical rotations and one-rune words are permitted. Choosing greatest rotation is equivalent to reversing the unknown order.

A word must be lexicographically no greater than each rotation. For each unequal comparison, the first unequal rune pair imposes one strict order relation. Their directed graph is acyclic exactly when some total order satisfies every comparison: a topological order supplies a constructive witness. A directed cycle is an impossibility certificate. This tests all orders exactly, without arithmetic labels, English scoring, a statistical threshold or a finite search approximation.

The initially proposed cross-page equality-pattern test was abandoned before implementation because N03 already covers it. The narrow prior check found no earlier unknown-order canonical-necklace test; the coordinator confirmed scope. An alternative hidden reversible-opcode model was not executed because arbitrary hidden states/permutations make it poorly identifiable. `S16-CARD.md` froze the replacement before controls and actual measurements.

## Controls

Forty positive panels use the actual page word-length schedules: twenty independently seeded hidden orders per page, with random circular words canonicalized under their hidden order. All forty graphs were feasible; every recovered topological order directly satisfies every full rotation comparison. The circles, hidden orders, selected rotations and output words are saved.

An independent all-order enumeration agreed on all 7,260 unordered word pairs with replacement from the 120 length-1–4 words over three labels, and on all 84 length-1–3 single words over four labels. The respective feasible counts were 2,967 and 72. Explicit two-edge and three-edge contradictory plants were rejected. These tests validate the compatibility algorithm, not language recovery or the plausibility of the chosen representation.

## Exact discovery certificates

Each page generated 203 nontrivial rotation inequalities. Word numbers, rune labels and positions below are zero-based F06 values.

| Page | Word | Word runes | Rotation | Forced inequality | Original source positions compared |
|---|---:|---|---:|---|---|
| 0 | 55 | 0,3,18,7,28,22,20,0,25 | 2 | 0 < 18 | 322,324 |
| 0 | 12 | 18,27,0,14,6,0 | 2 | 18 < 0 | 72,74 |
| 1 | 36 | 0,4,23,21,18,1 | 1 | 0 < 4 | 551,552 |
| 1 | 4 | 4,17,3,23,2,0 | 5 | 4 < 0 | 377,382 |

All four comparisons differ immediately at their first rune. The cycles 0→18→0 and 0→4→0 are shortest possible nontrivial strict-order cycles. `s16_verify.py` independently reloads the original mapped words, forms the rotations and checks each inequality and source position, without importing the graph algorithm. It verifies both contradictions. Full original word maps, including raw positions and source lines, remain in `S16-result.json`; F06 source-character coordinates retain their original combined-source convention.

This is a deterministic incompatibility result for **minimal-rotation emission at every explicit word under one order per page**. Cyclic objects need not choose a lexicographically minimal orientation. Different units, word-specific orders, unmodeled exceptions, encrypted canonical forms or another normalization rule remain outside this test. There is no general rejection of “circumferences” or circular mechanisms and no decoded plaintext claim.

## Artifacts and reproduction

- `s16.py`: constraints, controls, exact graph procedure and source certificates.
- `S16-controls.json.gz`: all forty hidden-order panels, exhaustive enumeration counts and contradiction plants; seed 1709202616.
- `S16-result.json`: all words, all 406 inequalities and both shortest source certificates.
- `s16_verify.py`, `S16-proof-check.json`: independent direct certificate verification.

Input `worker-f/F06-maps.json` SHA-256: `74bdf46e10ce11080762e82350004bd95ea1952a866a9778b3e746c20012973b`. Logged runs: `20260917T020551.190257Z-S16-controls`, `20260917T020601.767618Z-S16-actual`, `20260917T020632.028367Z-S16-proof`. All passed with zero exit and no timeout; total logged execution was under one second. Commands and snapshots are preserved in those run directories. Resume modes are `s16.py controls`, then `s16.py actual`, then `s16_verify.py`, through the standard logger. STOP and the original 2026-09-17 03:30:37 UTC deadline remain binding. No prior artifacts, shared state, Git or additional source images were modified/accessed.
