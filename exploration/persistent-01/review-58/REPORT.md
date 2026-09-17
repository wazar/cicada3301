# Review58 — P29 bounded source-membership test

**Scoped PASS.** Independent reconstruction verifies every first-conflict certificate across all 600 panels and 10,993,800 complete source windows. Original0 admits no complete window from the pinned Blake conversion under the stated bijective digraph model. No scientific defect was found.

## Independent checks

The review imports neither production search nor P29's local checker. It reconstructs all 4,580 source words, 18,584 runes and individual original-character maps from the pinned raw Gutenberg bytes using the declared body endpoints, ASCII/apostrophe tokenization, greedy digraphs and aliases. These exactly match P29's frozen source maps and P17 source. The raw SHA-256 is `fc9a76619fcb76c58273d7fc9e034108b0d7fffed3780ad5b8226954a12b289a`. Original0's complete 262 runes, all source positions and ignored word boundaries agree with pinned F06.

Compatibility is independently computed by canonical first-occurrence labels, rather than production's bidirectional pair maps or the local checker's previous-occurrence distances. Equal canonical patterns are equivalent to the existence of an injective map between observed pair labels. Any such map extends to a full 841-symbol permutation by pairing unused labels; the unobserved part is a witness completion, not recovered information. Direct source/cipher prior-index checks separately reproduce the exact first-conflict reason and the most recent earlier witness index.

Every one of the 600 NPZ obstruction arrays agrees, including all compatible offsets. Their combined stored size is 9,654,874 bytes. Actual reason counts reproduce as 13,894 source-repeat/output-change and 4,429 output-repeat/source-change conflicts. The four maximum-prefix offsets are 2416, 3174, 14457 and 17300, each length 34 of 131 pairs. Full source/cipher coordinates for all four examples are independently reconstructed in `result.json`; the printed example at 2416 matches P29's report exactly.

All four seeded random 841-permutation encoders reproduce their ciphertext and unique complete true offsets 0/4096/8192/12288. Their 88/92/89/97 observed assignments and full deterministic bijection completions verify. All eight deliberately malformed controls reject with the recorded conflict. The review reproduces every null permutation from its seed, verifies complete pair-multiset preservation, and confirms all 595 null seeds are distinct.

## Results and inferential boundary

All four controls have prefix upper tail 0.01 against their 99 full-family nulls; none of the 396 control nulls admits a complete source window. Actual maximum prefix is 34, with 186 of 199 null maxima at least that large, giving (1+186)/200 = 0.935. Actual-null maxima range 17–59 and none admits a complete window. Every reported maximum, match set and tail is reproduced.

The primary result is exact finite membership failure for one pinned source conversion, the complete original0 stream, fixed ciphertext phase0 and one unknown bijective ordered-pair codebook. It does not require a language score or the null model. The secondary prefix comparison assumes exchangeability of complete cipher blocks conditional on their multiset; it preserves within-block equality but not cross-block adjacency or word structure. It is not a claim about the true cipher process, and a 34-pair consistent prefix is not partial plaintext evidence.

The source's documented artifact connection motivates this bounded hypothesis but does not establish these edition bytes as 2014 plaintext. This review verifies the pinned text conversion and computation, not fresh historical signatures/image provenance. Other editions, texts, phases, block lengths, homophonic/noninjective maps, variable state, omissions or altered boundaries remain outside scope. No further source or hypothesis was searched.

## Preservation

`check.py` is the independent reviewer implementation; `result.json` contains all panel summaries and maximal witness coordinates. `MANIFEST.json` hashes the source, code, cards/reports and all checked scientific data files. Original worker artifacts are unchanged.

Logged command in `runs/20260917T022543.271489Z-P29-independent-canonical-review` passed with exit0 in 1.44 seconds, one numerical thread, no timeout. It replayed source membership rather than invoking either original search implementation. No new network/image/reserve access, shared-state change, source repair, key expansion or Git action occurred.
