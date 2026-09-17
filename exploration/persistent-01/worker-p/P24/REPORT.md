# P24 — shared relabeling cannot restore greedy-renderer compatibility
The pooled discovery text contains **all812 directed pairs of distinct runes within explicit words**. Consequently no fixed bijection of the29 rune labels can hide even one forbidden distinct pair from the P23 greedy renderer. The shared-bijection format is exactly incompatible with the whole45-page collection.

This is a graph obstruction, not a plaintext search or statistical significance claim.

## Why no permutation search is needed
P23's exact canonical-plus-alias renderer forbids14 directed pairs, each with distinct endpoints. A bijection preserves distinctness. Any mapped forbidden pair must therefore be one of the812 ordered pairs of distinct ciphertext symbols. Every such pair is observed somewhere within an admitted explicit word, so none can be an absent edge.

The graph has8,111 withinword edge occurrences from2,355 units on45 discovery pages, covering836 distinct ordered edges: all812 nonself pairs plus24 self pairs. The absent nonself graph is empty. All12 active pattern vertices have empty initial target domains. The solver returns UNSAT at its root, one node, without branching or enumerating alphabets.

This excludes one shared mapping across the whole collection. It does not establish that any individual page lacks its own mapping, and no per-page mapping search was added.

## Exact source certificate
independent-certificate.json provides a first observed source witness and count for every one of812 distinct pairs: page, explicit unit, within-unit positions, page rune indices and source-character positions. actual.json.gz retains all unit sequences/maps and all observed counts. No cross-word or cross-page adjacency was introduced.

P23's fourteen forbidden pairs, aliases and renderer are unchanged. The pattern has12 active vertices and three weak components (sizes8,2,2); the empty absent graph has29 isolated vertices. Degree/domain computation preceded the root test. Weak-component bookkeeping was completed during independent replay rather than the initial graph pass; it was not used to select or change a test.

## Controls and capability
One hundred tiny random directed graph instances, with2..6 vertices, match exhaustive injective enumeration. Four complete solved-source word panels are rendered greedily and relabeled by fixed random29-symbol permutations, then repeated across45 page labels without joining words. Every unknown-mapping control is SAT in13 nodes and its returned full bijection reparses every word successfully.

The returned mappings differ from the planted mapping on11–12 of12 active vertices. That ambiguity is expected: these sparse source graphs have670/726/765/750 absent directed pairs, and membership only asks for some compatible relabeling. Controls do not demonstrate recovery of the true alphabet or plaintext. Repeating the same source over45 page labels supplies no independent source diversity.

A separate no-import checker regenerates the relabelings, verifies all returned full bijections, reconstructs every actual edge/count/source witness directly from F06 and proves complete coverage of all distinct ordered pairs. The simple mathematical obstruction requires no trust in a SAT status or numerical optimizer.

Controls, actual and replay logged0.15s/0.09s/0.08s, all exit0 and one thread. No search cap was approached. Full artifacts, code snapshots and source hashes are retained.

## Rejected initial proposal and scope
The initial P24 many-time-pad collision idea was rejected before execution because structure/fingerprint2.py120–142 already measures head/tail-aligned interpage collision rates; armada/FOLLOWUP-TESTS #4 and selfref_skip.py also study aligned shared-pad differences. No new shared-pad collision scores or controls were computed.

The replacement changes P23's fixed-symbol-mapping assumption while retaining the exact greedy A–Z renderer, aliases and explicit-unit resets. It does not cover per-page alphabets, nonbijective homophony, hidden parser breaks, nongreedy/direct rune output, deletions, alternate spellings or all Latin-first formats. No English score, key list, reserved page, original50, new image, install or Git mutation was used.

Review40 independently reconstructed all2,355 units/8,111 transitions and all812 nonself source witnesses, and checked the shared-bijection contradiction separately from the embedding solver. See exploration/persistent-01/review-40/REPORT.md. No production defect or scientific change was required.
