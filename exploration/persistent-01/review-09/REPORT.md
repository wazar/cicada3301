# Review09 — P03 representation and P04 shared codebook

**NO-ERROR-FOUND in P03/P04's stated finite model.** Independent source reconstruction validates P03's pagewise compatibility result. P04's shared-codebook infeasibility additionally has a small exact integer contradiction, so this particular bound need not rely only on the optimizer's status. Neither result recovers plaintext order or excludes homophonic ciphers generally.

## P03 direct-source reconstruction and certificates

Used the canonical29-entry GP table from KNOWLEDGE.json and the four original solved rune files; no J03 expansion or worker solver/checker was imported. Removed exactly AEIOU and retained Y. Reconstructed every expanded character, source-rune identity/index, within-expansion offset, retained/deleted index and rune-level map. All2505 expanded-letter maps agree. Consonantal lengths are490,481,324,195 for koan, loss_of_divinity, welcome, jpg107-167. The frozen fourth source remains admitted but contributes zero windows because195 is below every target page length; no replacement was introduced.

Independently checked all2812 source windows and full family coverage, including unsorted26-letter counts, original-rune spans and expansion boundaries. Per-page window totals512/500/647/674/479 and feasible totals47/113/213/517/141 agree. All1031 feasible certificates assign every observed positive rune exactly once and sum to its **named source letter's** count. The1781 infeasible windows share checked exact obstructions/certificates; no UNKNOWN was silently converted.

The new proof verifier uses integer generating-function coefficients to count every possible smallest-bin submultiset. Each DAG node's distinct, valid listed children have exactly that coefficient count, proving branch completeness without reusing the solver's recursion or earlier checker's subset-enumeration algorithm. Necessary total/support/minimum/subset-sum/capacity inequalities are separately checked. All210 saved control certificates pass;200 tiny cases additionally pass fresh labeled-assignment brute force.494 relevant rejected-proof nodes including controls were checked; feasible certificates do not require their abandoned search branches to be proofs.

Sorting counts is legitimate only for pagewise unlabeled partition feasibility. Every feasible witness was restored to actual rune IDs and actual letter IDs before validation. Count compatibility does not preserve order, specify homophone scheduling, yield a shared codebook, or establish linguistic probability. The overlapping-window weighting remains an imposed descriptive sampling scheme over this reused finite corpus.

## P04 independent model reconstruction

Rebuilt unsorted source-window count vectors from the four original files, retaining only P03-certified feasible windows and the common **letter support**, not a sorted count pattern. Because every output rune occurs on each of the five pages, a fixed disjoint rune-to-letter assignment requires identical source-letter support on every page. The only common support is BCDFGHLMNPRSTWY. Counts/aliases agree:43/103/155/376/129 distinct vectors,47/113/169/415/141 window aliases.

The independently built model uses one shared binary assignment for each rune/letter, one binary window-vector choice on each page, and exact count equalities for each named letter/page. Its1241 variables and109 equations match the saved matrix exactly after explicit row/column permutation. All bounds are[0,1] and integral for the actual test; there is no page-specific relabelling, letter sorting, fractional solution promoted, or unrecorded symmetry constraint. Deduplicating identical unsorted vectors is safe for this count-only test because all original window aliases remain attached.

Independent solver replay reproduces feasible positive and infeasible negative controls and INFEASIBLE for the real integer model. The LP relaxation is **feasible**: integrality is essential, and a fractional count mixture cannot be reported as a codebook. A reproduced HiGHS status alone would still not be a portable formal proof; the following integer certificate removes that limitation for this finite case.

## Elementary shared-assignment contradiction

Consider each letter's admissible count values across the five pages. Any output rune assigned to that letter contributes its entire five-dimensional observed count profile. A rune exceeding the letter's maximum available count on any page cannot belong to its group.

For B, only runes3,7,24 survive these simple upper bounds. Exhaustively checking their eight subsets against the five pages' allowed B counts leaves exactly **{7}**. For P, only runes3,7 survive; their four subsets leave exactly **{7} or {3}**. The shared disjoint assignment has already given rune7 to B, so P must receive **{3}**.

On original page1 these forced groups require **B=9 and P=9 simultaneously**. Among every surviving source-window vector, the only pair with B=9 is **(B,P)=(9,7)**. Thus no page1 source window can meet both forced counts. Pages3,7,17 also fail the same joint restriction, but one page suffices.

`elementary-certificate.json` records every eligible/excluded rune profile, upper-bound exclusion, all8/4 small subsets, actual allowed letter-count sets and all source B/P pairs. `elementary.py` reproduces the argument using integers only, without consulting a MILP result. Its premises include the fully checked P03 pagewise exclusions and the support join; it is not a statement about source windows outside the frozen corpus.

## Scope and integrity

The finite bound is: these five discovery histograms cannot share one disjoint rune-to-letter codebook while each corresponds to one admitted contiguous consonantal source window. Page-specific codebooks remain pagewise count-compatible as P03 reports. Other passages, registers, source corpora, overlapping/homophonic definitions, context-dependent maps or output mechanisms are not excluded; no source-order test was done. Do not turn this into a general homophonic or vowel-deletion verdict.

Review snapshots/hash records preserve P03 evidence and P04 support/model/matrix/result as read; no ongoing worker output was modified or interrupted. All source hashes/maps, independent matrix and LP/integer/control outputs are saved. Main logged checks.146s/.844s/.049s, one numerical thread. No reserved-page read, new register, Git mutation, nested worker or active process. Release this review slot.
