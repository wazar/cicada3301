# Review17: Q04 joint-objective search is correct but does not recover controls

No substantive objective, generator, proposal-accounting or held-isolation error found. The eight fixed controls fail unknown-map recovery despite using the proper source-plus-emission objective. This supports Q's decision not to run real pages/nulls or increase the budget within this task. It does not exclude homophonic encoding.

Q04 keeps the same17 consonantal letters,29 output labels, surjectivity, fixed P05 source model and8×5000 search budget. The four held controls are unchanged P05 group0..3/rep0, with original optimizer seeds. The four model-generated controls use those same truth maps and lengths324/195/54/62, with source seeds470400+2g and emission seed+1; optimizer seeds470800+g. No control was chosen or replaced after its result. The optimizer receives only the model, full ciphertext/cut and seed, never truth; its score and initialization/proposal logic use no held suffix observations.

The exact one-shot emission probabilities are correct:1/k initially or outside the previous mapped bin; singleton1; eligible same-rune repeat .17/k; another member of the same bin1/k+.83/[k(k−1)]. Bin sizes include all29 mapping entries. Moving an UNUSED rune can change emission while leaving decoded text/LM identical; an independent witness gives−1.2262089458 nats. The code recomputes the full prefix score for every proposed map, so that effect is included. Under surjectivity the largest bin is13, within the kernel's lookup bounds. The objective is conditional generative likelihood, not a posterior or a likelihood with the control allocator's bin-size prior.

Fresh checks before interpreting results:

- Compiled an inspected immutable local kernel copy, SHA256 `cc5afe06c107921cad966730c38c1f7c7bafcf781a15356dc64be694649a8d5d`. Compiler/version/commands/errors are retained; binaries are local platform-specific artifacts.
-974 independent finite score fixtures cover every bin size1–13, singleton/repeat/different-member branches and64 complete random maps. Maximum discrepancy1.42e−14 across LM/emission/joint totals. Twelve suffix perturbations leave score-only output exactly unchanged.
-A separately instrumented local one-restart200-proposal harness records162 valid proposals:98 swaps/64 reassignments,55 accepted/107 rejected. Independent scalar objective, temperature, Metropolis decision, current map, surjectivity and best-map replay agree, and final cached counts equal a fresh recount. This is a bounded bookkeeping test, not another Q04 search sweep.
-All four new model controls'1,296 source/emission uniform draws are replayed independently from seeds and checked against inverse-CDF bins and one-shot logic. All original held cipher/plaintext/map/seed/cut data match P05 exactly.
-All64 saved restart maps and10,160 scored positions are independently rescored; prefix selection, truth ranks, plaintext recovery, observed-map accuracy and unused-rune accounting agree. Search totals are320,000 nominal proposals,265,198 valid and22,814 accepted.

Swaps preserve bin counts. Accepted reassignments decrement the old label/increment the new; rejected moves leave counts unchanged. Singleton removal is forbidden, keeping surjectivity. Best scores/maps update together on strict improvement. This annealing code is an optimizer; asymmetric proposal eligibility is not corrected by a Hastings ratio and should not be described as posterior sampling.

| Control | Truth rank among truth+8 found maps | Total plaintext accuracy | Suffix accuracy |
|---|---:|---:|---:|
| Held324 |9 |13.58% |19.44% |
| Model324 |1 |11.73% |11.11% |
| Held195 |8 |4.62% |3.08% |
| Model195 |1 |4.10% |4.62% |
| Held54 |9 |1.85% |0% |
| Model54 |7 |7.41% |5.56% |
| Held62 |9 |6.45% |9.52% |
| Model62 |9 |0% |0% |

No control recovers the full observed mapping. For the two longer model controls, the supplied true map scores above every found map, yet optimization misses it: good known-truth ranking does not imply search recovery. For the short model controls, newly optimized alternatives outrank truth even when plaintext was drawn from the exact assumed source distribution. That is a finite-sample/adaptive-selection limitation absent from N06's fixed-competitor experiment. It does not invalidate N06; it prevents extending its1600/1600 fixed-map result into a claim of unknown-map recovery or uniquely diagnosed language mismatch.

P05D's actual-source failures remain relevant and preserved. Q04 legitimately changes the maps found by optimizing the joint objective; those new maps are not the eight frozen P05D alternatives. Its held ranks9/8/9/9 therefore need not equal P05D's ranks5/1/9/9 for the four representative old sets. No claim that the corrected objective fixes source/register mismatch follows.

All review batches pass; original Q/P files remain unchanged. The independent fixture/kernel/proposal/full-control checks took.084/1.783/.781/.080s in logged runs. Local modified harness output still carries the product's hardcoded nominal5000 metadata; the review explicitly records its actual200-step cap and never counts that harness as a Q04 production search. Every compiler command, exact source copy, fixtures, transcripts, hashes and results is retained. No real page, expanded key/source class, new starts, reserve or Git operation was used. Review complete.
