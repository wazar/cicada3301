# Review57 — S17 scoped PASS

Independent replay verifies all 1,536 retained bijective maps across 64 searches, every decoded output and inverse re-encryption, and all complete scores reconstructed from the frozen clean Latin count dictionaries (maximum error zero). All 27,000 reconstructed log probabilities and the exported native table agree. Corpus provenance/source cleaning remains the separately audited Q05 premise; this review does not repeat that source audit.

All four held-source encodings, source objects, seeded permutations, word boundaries, frequency initializations and truth scores/ranks were rebuilt. Selected rune errors are 0/1/2/0 and ranks 1/13/18/1. Six or seven labels per control are unused, so full-map disagreement is not equivalent to plaintext error. Controls do not establish short-page recovery at original55 length.

All 57 null RNG streams were replayed through every rejected proposal and their first accepted permutation. They preserve the exact histogram and equality COUNT, not equality positions. Attempts range 1–38,004, below the fixed cap. Conditional uniformity follows from uniform multiset permutations followed by this fixed rejection event; it is a declared comparison model, not evidence of the ciphertext generator. Retained-max selection independently yields tails .15/.75/.75 on originals0/17/55.

The inspected C++ kernel correctly touches trigram terms at each swapped occurrence and its two successors, retaining boundary29. A compiled tiny harness calls this frozen kernel and compares against separately written full scalar scoring for every swap across 164 small streams: 66,584 checks, maximum error 2.16e-12. Cases include empty streams, all boundaries, repeated symbols, random symbols and unused labels. All 2,048 saved full-input swap probes also pass; selected reported local optima were checked directly across all swaps.

The fixed 24-restart annealing/hill-climb budget and selection code were inspected. Recorded evaluation and acceptance totals reconcile (46,729,194 and 857,745), but full optimization trajectories/RNG proposals were not rerun. Nothing here proves global optimality, posterior coverage or recovery of every possible substitution. These are best retained finite-restart scores. Unlike earlier beam lanes, S17 is simulated annealing, not a beam search.

All 72 complete actual restart transliterations were read without editorial repair. No coherent complete Latin candidate was apparent; isolated word-like fragments are not elevated. This subjective reading is separate from the verified scores/null accounting.

Logged run `20260917T022256.689737Z-review57-all-outputs` exited zero in 4.154 seconds; compilation and tiny kernel exited zero. All snapshotted scientific inputs remained unchanged. No failed audit attempt, no scientific search rerun, no parameter change and no blocking defect. The local compiled review kernel is reproducible from source and need not be published as a binary.
