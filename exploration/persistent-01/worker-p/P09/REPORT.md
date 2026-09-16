# P09 — plaintext-word-boundary assumption

No recovery gap appeared on the four frozen controls. Both the boundary-free Latin rune trigram and the boundary-aware model given relocated separators recovered every one of 719 runes, all four planted keys, every rejection decision and final consumed key index. The declared gate therefore stops this path: **no new real-page search was run**.

| Held control | Runes | Separator count | Original/relocated overlap | Free errors | Relocated-aware errors |
|---|---:|---:|---:|---:|---:|
| Newton prefatory verse | 210 | 35 | 8 | 0 | 0 |
| Newton definition | 124 | 23 | 5 | 0 | 0 |
| Virgil 1 | 245 | 48 | 11 | 0 | 0 |
| Virgil 2 | 140 | 25 | 5 | 0 | 0 |

This is evidence of recovery robustness for these four finite-key controls, not evidence that the actual separators are plaintext word boundaries. It also does not exclude a power gap under other keys, texts, lengths or transformations. The boundary-aware truth language likelihood worsened from approximately −2.16…−2.57 to −3.26…−3.56, but likelihood loss alone did not satisfy the predeclared recovery-gap criterion.

The only changed assumption is segmentation. All P08 Caesar training paragraphs and all held source maps, ciphertexts, planted keys and encoder traces are retained unchanged. For n runes and m markers the relocated ends are `ceil(j*n/m)-1`, j=1…m: a fixed equal-spacing schedule using only length/count, independent of plaintext symbols and scores. It preserves m unique positions and the terminal marker. No alternative schedule was tried after seeing the result.

The free model removes every boundary token during training and inference, resets context at the same paragraph starts, and uses pseudocount .5 over 29 outcomes, bigram concentration 8 and trigram concentration 5. Scores normalize by runes; boundary-aware scores normalize by runes plus markers, so raw scores between models are not direct comparisons. Both retain the exact four M25 cells, 1024 finite draws, start 0, no wrap, skip-by-two rejection with probability .83. Full outputs for all four cells under both models remain saved.

The targeted overlap read found R18/L7 A.3 and the associated LEDGER entry already explain why the **legacy boundary-free English quadgram model** needs no word-boundary repair. That does not evaluate the newer explicit-boundary rune LM. Worker C's P03/P08 cards keep supplied boundaries fixed, and worker F's boundary identity/transition statistics test different predictions. P09 is a controlled segmentation assumption test for the newer model, not a relabeling of the legacy observation.

Independent acceptance-index enumeration agrees with the free-model DP top scores on 40 short finite cases. Direct arithmetic replays all 32 searched outputs; all four control fixtures exactly equal their unchanged P08 versions. Probability normalization passes for all 900 possible two-token contexts, including start sentinels. The free model gives identical truth likelihood regardless of supplied original or relocated ends. Checks passed; main run exit 0 in .563 s, independent replay exit 0 in .502 s.

Artifacts: `CARD.md`, `p09.py`, `p09_check.py`, four complete `control-*.json` files, `summary.json`, `check.json`, and `MANIFEST.json`, plus standard logger snapshots and input hashes. No new images, reserved pages, source texts, key starts, key families or external fetches. A different next experiment must supply another explicit prediction; this result does not justify simply extending the same search.
