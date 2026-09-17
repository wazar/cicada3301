# P25 — original Latin-dominant model, frozen F/clue-key search
No coherent plaintext emerged from the fixed search on originals0/17/55. Full-procedure per-page tails are0.30,0.85 and0.95 against19 matched nulls. All four separate Virgil controls recover every rune and the exact planted literal-F path, with the planted key/phase/sign ranked first.

**Source-boundary defect:** after this run, review42 found16 English footer word fragments (59runes+16boundaries=75tokens, about0.053% of training tokens) inside the frozen Caesar training slice. This original model and every result remain unchanged. It must be described as classical Latin plus small English-footer contamination, not pure Latin. A separately named corrected-boundary replay is planned using identical packets/seeds/keys; this report does not silently substitute that model or choose between their scores.

## Fixed source, cipher and search
Coordinator Q05-latin supplied Caesar PG218 training (20,500words/120,913runes/141,413tokens including that footer) and four disjoint first60-word windows from Virgil PG227 booksI/IV/VII/X. Canonical GP conversion and original character/rune maps are retained by the coordinator. Headings/abbreviations and body limits were fixed before puzzle scores. The model uses P03's rune/boundary trigram interpolation(.5,8,5), with boundary29. Original model NPZ SHA256 is16f491d53007cc4492d1bb94b42fed16aca136bca0f62ba7ebe1b8ba769c3b93.

This is the existing optional-literal-F additive construction: ciphertextF may yield plaintextF without consuming key, or use ordinary p=(c+sign*K[u])mod29 consuming one key rune. Other symbols use only the ordinary branch. Keys repeat cyclically; no rejection wrapper, seed search or finite-EOF variant is included. Both word boundaries and the Latin register are conditional assumptions.

The first16 frozen clue keys contribute81 natural phases×2signs=162 cells. Every cell uses the unchanged p03_frozen.beam width64, retaining up to16 complete paths. No English score selects candidates before the Latin search. Prior P08 used a different skip-by-two transition and four numeric keys; P25 is an additive-method/register extension, not a new cipher family.

## Held unknown-key controls
| Virgil source | Runes | Planted key index/phase/sign | Rune errors | Key rank | True path rank | Tail |
|---|---:|---|---:|---:|---:|---:|
|BookI|303|0 /0 /−1|0|1|1|0.05|
|BookIV|339|5 /1 /+1|0|1|1|0.05|
|BookVII|331|10 /2 /−1|0|1|1|0.05|
|BookX|383|15 /3 /+1|0|1|1|0.05|

No control truth path was pruned. The encoder emits sourceF literally when position%3!=1, otherwise ordinarily, as in the existing P03 control construction. Full source text, literal decisions, consumed indices, true keys and all alternative outputs remain available. These four passages are from one held author, not four independent corpora. Exact arithmetic recovery and ranking are separate measurements; re-encryption alone would not establish a real solution.

One hundred small cases with at most six F branch sites match exhaustive path enumeration for every returned top16 score. That finite test does not make beam64 globally exact on full pages.

## Actual results
| Page | Runes/boundaries | Best key/phase/sign | Full score | Matched tail |
|---|---|---|---:|---:|
|0|262 /59|clue008 /3 /+1|−6.59722100|0.30|
|17|273 /69|clue006 /0 /+1|−6.71571979|0.85|
|55|76 /17|clue012 /3 /−1|−6.43410896|0.95|

All48 leading actual alternatives were retained and inspected in full. They do not give coherent complete Latin plaintext. The files packet-4/5/6-full-top16.txt contain every displayed transliteration; no isolated word-like fragment is used as evidence. No legacy score threshold or cross-model numerical comparison is imported.

## Null and selection accounting
Each packet has19 full searches generated under the exact ciphertext-F mask, exact adjacent-equality mask and fixed boundary schedule. F slots force0; nonF repeats copy the previous rune; other nonF slots draw uniformly from1..28 excluding the previous nonF symbol. The first nonF symbol is uniform1..28.

The number of choices at each draw depends only on the fixed masks. Hence the sampler is uniform over this precisely conditioned finite class, not merely an approximately matched Markov generator. It fixes F branching opportunities but does not preserve nonF histograms, longer dependence or an established true cipher distribution.

Every null repeats all162 cells and the same global-alternative selection. Four controls plus three real pages, each with19 nulls, give140 searches and22,680 cells. The per-packet empirical tail has resolution0.05; no cross-page discovery probability or significance from control-floor tails is claimed.

Global16 alternatives are distinct in (plaintext,literal positions), drawn from each cell's beam-retained16. Their encountered key aliases are recorded; this is not exhaustive recovery of all tied aliases or paths pruned by the beam. Scores, every retained cell path and all null ciphertexts are saved.

## Verification, cost and disposition
Production re-encrypts every retained path. A separate checker imports neither beam nor scorer: it verifies the key/phase grid, source controls, all mask-null draws, every retained plaintext/consumption path, independently vectorized LM scores, global16 selection/encountered aliases and every tail. All140 searches/22,680 cells/336,960 retained alternatives pass; maximum score discrepancy1.87e−14. Root separately checked original corpus arithmetic, and review42 subsequently identified the footer boundary defect.

The seven main search batches plus reused pilot contain71.55s of search computation; independent full replay took6.60s. All logged production exits are0, one thread, no batch near900s. The140 compressed search artifacts total12,453,350bytes; largest113,954bytes. The pilot control is reused, not additional search coverage.

No corpus fitting to puzzle outputs, key expansion, wider beam, reserved page, original50, image read, install or Git mutation occurred. The original contaminated model remains a complete, reproducible result. Any corrected-boundary replay is a disclosed source repair under exactly the same search, not a newly selected hypothesis or replacement of this record.

## Completed correction replay

The separate P25-clean replay is complete on identical inputs and the same 22,680 cells. Its report and complete paired comparisons retain this original record. Corrected actual tails are .20, 1.00 and .95; controls remain exact. The repair materially changes some rankings, so the small footer fraction is not treated as negligible.

Independent review43 passes the original and corrected complete outputs; see ../../review-43/REPORT.md. The original source defect remains disclosed.
