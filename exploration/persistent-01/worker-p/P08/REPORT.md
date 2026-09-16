# P08 — source-backed Latin model under fixed skip-by-two arithmetic

The Latin model recovered all 719 runes, all four planted keys and all four complete rejection paths on the four held controls. The frozen English rune/boundary model did so too. This demonstrates Latin recovery for this finite mechanism; it does **not** demonstrate that the newer English model was blind to these controls. The actual page 0 and 17 searches produced no candidate.

| Packet | Runes | Latin score | Latin tail | English score | English tail | Latin−English contrast tail |
|---|---:|---:|---:|---:|---:|---:|
| Newton prefatory verse | 210 | −2.577149 | .05 | −3.330778 | .05 | .05 |
| Newton definition prose | 124 | −2.208056 | .05 | −3.396631 | .05 | .05 |
| Virgil first paragraph | 245 | −2.173719 | .05 | −3.387125 | .05 | .05 |
| Virgil second paragraph | 140 | −2.491043 | .05 | −3.263998 | .05 | .05 |
| Original 0 | 262 | −6.822697 | .15 | −4.674233 | .25 | .15 |
| Original 17 | 273 | −7.018393 | .95 | −4.642189 | .60 | .95 |

Scores are maximized joint log likelihood per rune plus boundary token, including the fixed .83 rejection process. Each tail is `(1 + null maxima at least observed)/20`; .05 is the finite 19-null resolution, not a precise rare-event probability. Latin-minus-English contrasts were declared in advance and are calibrated against the same null packets; raw scores across differently concentrated language models alone are not evidence of a language.

## Frozen sources and representation

Training uses only cached Caesar, `liber-primus/analysis/latin/latin_218.txt`, SHA256 `84ac8411841a4d8f5f4a49b6a2cd1f466917c6a5af72916d5e0b2b1ecb2f659c`. Its universal-newline character body span [1066,148293) contains 230 paragraphs and 120,990 mapped runes. Start is `GALLIA est omnis`; end precedes the Gutenberg footer. Context resets per complete paragraph.

Held sources are separate files/authors, never training inputs:

- Newton Principia, `latin_28233.txt`, SHA256 `cc3f9845acd902a26bb58e268499472da99c7c39d7825aa1a86ad8959450b2e8`, body [2400,806481). First two complete blank-line paragraphs with 80–400 runes occur at [9652,9924), 210 runes, and [10920,11072), 124 runes. The first is Latin prefatory verse in the Newton volume, not Newton's mathematical prose; this source-selection consequence is retained.
- Virgil Aeneid, `liber-primus/data/keys/armada19/virgil_aeneid_latin.txt`, SHA256 `adcda89e39c7429cbee028dbe3c246c3eab99b416c8a7a8ade71876446a141ca`, body [782,456098). First qualifying paragraphs are [782,1102), 245 runes, and [1105,1284), 140 runes.

All positions are decoded Unicode character offsets after Python universal-newline conversion, not byte offsets. Original file hashes preserve bytes. Selection inventories retain preceding excluded paragraph lengths. No control was selected using a score. The source maps preserve selected text, each normalized character, each emitted rune and its original positions, removed characters and word ends.

The frozen transform uses Unicode letter runs, uppercase, Æ/Œ expansion, accent removal, J→I, V→U, K/Q→C and Z→S, then longest canonical GP digraphs within a word. Punctuation, digits, underscores and whitespace separate words without emitting runes. This lossy classical spelling convention is one explicit hypothesis, not the unique Latin encoding. Existing boundaries are assumed to be plaintext word boundaries. For real pages the exact M25/F06 `raw_joined` rune-run parsing is retained, including its physical-line/boundary convention; it is not a new verified delimiter interpretation.

The first preparation run failed because a broad regex classified fraction ¾ as word material while scanning later Newton text. Before any score, this was corrected to Unicode category L and held scanning ended after the first two qualifying paragraphs. The failed log remains. No scored input or answer was edited.

## Mechanism, controls and null

Both models use the same trigram backoff (.5 unigram pseudocount, concentrations 8 and 5, boundary token 29). The English comparator is the inspected frozen five-reference-group model, not the historical English quadgram scorer. Decoder definitions were extracted by AST from inspected M25 functions without executing its old corpus/search code.

Search is exactly the four saved M25 cells: prime-minus-one and integer-phi, signs ±, finite 1024 draws, start 0, no wrap. An attempted repeated ciphertext rune is rejected with probability .83; rejection advances two key indices, burning the intervening draw. Dynamic programming retains the best path per sufficient state. The four controls plant those four cells respectively, seeds 330108–330111. Rejections are 3, 3, 10 and 5; consumed indices are 216, 130, 265 and 150. Both models recover those exact paths and all plaintext rune indices. Every best output and every cell's result is retained.

For each of four controls and two real pages, 19 independently generated null packets preserve the complete adjacent-repeat mask and the supplied boundaries: first symbol uniform over 29, then copy the generated predecessor at a prescribed repeat, otherwise draw uniformly from the other 28. This is uniform over streams satisfying that repeat mask, but does not preserve rune frequencies or establish that this null is the cipher's distribution. The full four-cell search runs on every null under both models. Packet streams have seeds 330208–330213. No MCMC or fitted real-output adaptation occurs.

## Scope relative to earlier work

R18/L7 measured language sensitivity with supplied keys; P03/P05 changed English to a consonantal register; M25 evaluated the same arithmetic under English references. P08 fits a separate Latin corpus and searches complete held and real inputs under that detector.

The targeted prior read also found `analysis/latin/latin_redteam.py` globbed `latin_*.txt`, including `latin_12472.txt`, whose own metadata identifies English/French *Bataille de dames*. P08 explicitly excludes it. R18/L7's particular Latin controls used 218/28233 instead. This is a scoped inherited corpus limitation, not a rewrite of all prior Latin results or proof that their conclusions reverse.

The actual result is bounded by four finite keys, start 0, the skip-two transition, boundary assumption, and this Caesar-trained GP Latin register. It does not exclude Latin, other arithmetic, other key starts, other corpora or other orthographies. No new text, key or parameter was added after the real miss. A justified next test would need a different independently motivated mechanism or input relationship, rather than expanding keys because these maxima were unremarkable.

## Verification and artifacts

Independent acceptance-index enumeration agrees with the DP's top scores on 80 finite short cases, 40 per model. A separate direct replay validates 960 searched cell outputs and all 114 null RNG streams. Source checking reconstructs 123,923 normalized source-character mappings and 121,709 rune mappings (train plus held). All checks passed.

`p08.py`, `p08_batch.py`, `p08_check.py`, `CARD.md`, `source-summary.json`, `sources.json.gz`, `held.json.gz`, four complete control artifacts, six full batch artifacts, `batch-summary.json` and `check.json` retain raw inputs, outputs, mappings, scores, nulls and path evidence. Standard logger records snapshots, exact input hashes, exit status and durations. Preparation fix 1.70 s, pilot .39 s, remaining controls .44 s, full batch 4.15 s, independent replay .79 s; all exit 0 except the preserved initial preparation failure. No live processes, new images, reserves, Git changes, installs or external source fetches.
