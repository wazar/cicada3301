# Review21 — Q03 Chaocipher29: scoped PASS

No blocking implementation or accounting defect was found. An independently authored codec reproduced the complete published26-letter fixture, all28 published pre-step alphabet pairs, both one-step alphabets, and every one of the22,500 simulated discovery-length page ciphertexts (5,233,000 runes). The two saved count comparisons reproduce exactly.

| Observable | Actual45 discovery pages | Simulation500 panels | Two-sided rank tail | Bonferroni2 |
|---|---:|---:|---:|---:|
| Adjacent equality |57|308–422; mean362.342|0.003992015968063872|0.007984031936127744|
| Distance2 equality |357|296–404; mean349.648|0.6626746506986028|1|

These values compare the actual packet with the **specified random-start alphabets, circular four-source English sampler, nadir14 adaptation and per-page resets**. The existing adjacent-repeat deficit is not a new discovery. These ranks are not probabilities against every Chaocipher key, adversarially chosen alphabets, unknown plaintext, other registers or other permutation schemes. No unknown-key search occurred, and a simulation miss is not a general family exclusion.

## Independent construction

I read the complete primary description [Moshe Rubin, Chaocipher Revealed: The Algorithm](https://www.chaocipher.com/ActualChaocipher/Chaocipher-Revealed-Algorithm.pdf), then the coordinator card/code. This is independent implementation, not strong code blinding. The PDF hash is6f86f102658725916541352ee983794c9639d70cf7adef7c522da79010158d01; PDF and extracted text stay in the private local directory and are not copied into this review.

My codec uses explicit output-position maps derived from the prose's hole-and-shift operations, rather than the coordinator's slice/pop or deque routines. In zero-based terms, left positions after rotation are0,2..m,1,m+1..n−1. Right positions after the extra rotation are0,1,3..m,2,m+1..n−1. For n26, m13 matches the publication; for n29, m14 is the coordinator's explicitly chosen adaptation. The primary source does not specify a29-rune algorithm.

Two hundred fresh random26/29 cases pass forward/inverse roundtrip, left-label equality invariance and right-label inverse equivariance. Every symbol doublet in those states passes the exact restriction (5,500 cases); all200 coordinator control records also match. The full published intermediate trace is a stronger source anchor than roundtrip alone.

The doublet restriction has a direct positional explanation. After an emitted pair, its plaintext symbol occupies right index n−1, while its ciphertext symbol remains at left index0. Repeating that plaintext selects left index n−1, a different symbol. This does **not** prohibit all ciphertext doublets: a different plaintext may select right index0 and emit the preceding ciphertext again.

Fixed relabeling of the initial left alphabet commutes with encryption: lookup positions come from the right alphabet, and all left updates depend only on positions. Thus the ciphertext is merely relabeled, preserving both equality statistics. Likewise fixed relabeling of the initial right alphabet commutes with decoding. Sampling both initial alphabets is compatible with the declared distribution, but left labels do not supply additional equality-pattern coverage. The simulation does not explore29! distinct count behaviors through those redundant left relabelings.

## Source and simulation replay

The checker reconstructs all four canonical rune sources directly from raw characters, verifies hashes/start offsets/lengths, regenerates every seeded circular slice and both starting permutations, and compares complete ciphertexts and both counts. All22,500 outputs, their saved offsets/wrap counts, all500 panel aggregates and both rank calculations pass. Additional source-seam and wrap counts are retained in `simulation.json`, making the artificial corpus seams explicit. The corpus is four fixed held groups concatenated into1014 runes, not an independent language population.

Actual counts were recomputed separately from the F06 discovery-filtered45-page maps, with a checked exclusion of the ten reserve IDs and original50. Page joins are excluded from both statistics. No reserved plaintext or image was accessed. The review does not certify the inherited rune transcription itself.

The standard logger recorded control exit0 in0.311s and complete simulation replay exit0 in6.571s, one numeric thread. `review.py`, `CARD.md`, `controls.json`, `simulation.json`, fresh control records and immutable command snapshots preserve the procedure. No coordinator files were changed. This review supports the narrow construction/source comparison, not a cipher solve or an unknown-key coverage claim.
