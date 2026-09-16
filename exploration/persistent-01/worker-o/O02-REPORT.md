# O02 — exact count partitions eliminate the five-page J03 conjunction

The collision-compatible Latin-source windows cannot jointly explain the five observed rune histograms under disjoint homophone assignment, even allowing a different optimal assignment on each page. Pages0,3,17 have **no feasible windows**. This is an exact finite count obstruction, not a claim about every source register, arbitrary token encoding, or the probability of any cipher.

| Page | J03 compatible windows | Distinct sorted count vectors | Exact feasible | Exact infeasible | Unknown |
|---|---:|---:|---:|---:|---:|
|0|285|253|0|285|0|
|1|424|362|24|400|0|
|3|129|114|0|129|0|
|7|1468|1318|212|1256|0|
|17|30|27|0|30|0|

All2,336 eligible windows were checked, with2,074 distinct page/count cases after deduplication. Full group/start provenance and unsorted letter counts remain attached to every case. Noneligible windows already fail J03's necessary collision bound, independently reviewed in review04. Thus replacing that relaxation with the exact necessary partition test makes the same five-page finite-window conjunction zero. It does not undo the lesson that source representation materially affects bounds.

The exact condition is simple: assign each of29 observed output-symbol counts to exactly one present source letter; the sum assigned to each letter must equal its source count. A rare source letter cannot be represented when every output symbol occurs more often than it does. More generally, source bins of size<=t can use only output counts<=t, so their cumulative demand cannot exceed the total of those available counts. These necessary conditions reject2,046 windows:497 by minimum count and1,549 by cumulative small-bin capacity. Complete partition search rejects a further54 (20 on page1,34 on page7), while236 survive count feasibility. No timeouts occurred.

The bounded exact solver partitions the smallest remaining source count, enumerating all possible submultisets of remaining output counts, and memoizes exhausted states. Feasible results contain every group plus explicit source-letter-to-original-rune assignments for each original window. Infeasible searches contain full rejection DAGs: each node either has an exact necessary-condition witness, or lists every possible selected group and its rejected child. Every timeout would be marked UNKNOWN; none was inferred from an uncompleted search.

Controls:200 independent tiny exhaustive labeled-assignment comparisons agree exactly with solver feasibility; five planted attainable partitions using the actual output histograms succeed, and five same-total impossible controls fail. A separate checker, importing no solver functions, validates every real rejection reason, reconstructs every feasible letter/rune assignment, and checks exhaustive rejected-branch coverage using an alternate item-by-item subset construction. It also validates all210 control certificates. This is independent arithmetic code within the same worker, not a fresh external review.

Scope remains J03's fixed Latin transliterations, frozen solved-source window register, preserved counts, and disjoint homophone groups. Zero-count source letters receive no reserved used outputs, optimistically as before. Symbol order, plaintext semantics, homophone scheduling and a common cross-page codebook remain untested. Feasibility alone proves none of those. Because three pages have no survivors, no five-page candidate tuple exists and a shared-assignment search would be vacuous; no combinatorial tuple expansion was performed.

Input source vectors were reconstructed from J03's stored source sequences. The five actual histograms were checked against F06 discovery rune streams; no reserved page or image was accessed. Frozen source maps and prior review04 provide provenance and transliteration verification, not independent new image transcription. Exact source hashes are in O02-evidence.json.gz and logger manifests.

Evidence: O02-card.md; o02.py; O02-result.json; O02-evidence.json.gz; check_o02.py; O02-check.json. Initial execution0.317s; replay adding explicit rune assignment certificates0.372s; independent certificate check approximately0.05s, all logged exit0. Raw commands, code snapshots and output remain under runs/. No Git mutations, new dependencies, external services or running processes.

Decision: close this exact finite count-partition follow-up. Next useful tests require a changed premise: either an independently justified source register whose count vectors pass the partition conditions, or a specified variable-length/context-dependent encoder with an observable prediction that escapes fixed per-letter count conservation. More random codebooks cannot defeat these exact rejected count vectors. Overall mission continues under the existing coordinator/deadline.
