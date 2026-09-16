# P05: actual unknown homophonic decoding exposes a scoring limitation

A fixed29-to-17consonant homophonic attack was implemented and searched on16held-source controls plus discovery pages0and17and38matched null packets. It does not recover the controls reliably: median suffix plaintext accuracy5.56%, range0–40%, and the true mapping ranks last among itself and eight searched mappings on every control under the initial LM-only objective. Real results therefore provide no general negative evidence about homophonic consonantal encoding.

This materially changes the model being searched rather than extending additive keys. The targeted prior check found LEDGER D-03 explicitly marking the proposed homophonic annealing search never coded/open; R18L7 measured correct-key scorer blindness, not search recovery. Persistent C5/J01/count-bound lanes implement different mechanisms. The check was scoped, not a proof that no related code exists anywhere.

## Frozen procedure

Canonical GP expansion minusAEIOU, retainingY. The fixed alphabetBCDFGHJLMNPRSTWXY has17letters, including rareJ/X. Every fitted29-rune mapping is surjective onto all17; that is a strong real-input assumption. The first five named solved-reference groups train a trigram/backoff model; four whole remaining groups are held out, with consonantal lengths324,195,54,62. Source hashes and every kept/deleted letter's original rune coordinate are in model.json. No delimiter/word-boundary data enter the model. Shared source/transcription ancestry remains.

LM unigrams have.5pseudocounts; bigram/trigram backoff concentration4. Scalar C++ annealing runs eight restarts times5,000proposals per packet, temperature3to.05, with swaps and surjectivity-preserving reassignments. It fits only firstfloor(2n/3) symbols. Best prefix score selects one mapping; suffix is then evaluated without fitting. Every restart's complete mapping/output and scores are retained. Python independently reproduces every C++ prefix score and checks surjectivity. No restart budget or source variant was changed after control failures.

Controls use four codebooks per held group. Each codebook has one rune per letter plus12frequency-allocated extra homophones. Encoding uniformly selects a matching rune and, when that equals the previous rune and alternatives exist, redraws once among alternatives with probability.83. Unary bins cannot suppress repeats. The true mapping round-trip is exact. Recovery is measured on plaintext letters and separately on mappings of actually emitted runes; unused-rune assignments are unidentifiable and reported separately.

## Measured controls and first-order fit

Across16controls, overall plaintext accuracy median12.90%, range0–35.90%; suffix accuracy median5.56%, range0–40%; observable emitted-rune mapping accuracy median11.32%, range0–31.03%. One to four rune symbols are unused in many controls. Correct plaintext legacy English quadgram scores range−8.164to−7.651, median−7.841; this is only the inherited detector diagnostic.

Correct mapping ranks9of9under the original prefix objective on every control. All eight fitted alternatives score above truth, so the failure is not merely insufficient optimization of an otherwise correctly ranked answer. Controls retain all wrong positions and alternative outputs.

Actual encoder ciphertext doublet rates range0–.04334, median.01887. The324letter held group always contains13unavoidable unary-bin doublets and emits13or14total repeats; the195letter group emits2–4repeats,54letter group0–1,62letter group1–2. Thus the stated rejection probability does not by itself reproduce LP's first-order repeat rate. Measured real pages0and17have2/261and0/272adjacent repeats respectively. The encoder's unary limitation is a substantive mismatch, not hidden by the word"anti-repeat".

## Real packets and matched comparison

Page0prefix174/suffix88: selected suffix conditional-minus-unigram gain−.866560nats/symbol; raw conditional score−3.963930; descriptive upper tail.40against19nulls. Page17prefix182/suffix91: gain−1.090081; rawconditional−4.210646; descriptive tail1.00. There is no attractive continuation candidate. Control failure prevents using these numbers as a broad cipher-family exclusion.

Each null preserves exactly the page's rune histogram and adjacent-equality count through nontrivial accepted swaps. All38chains reached100*naccepted swaps, final changed positions246–267, acceptance rates.810–.841. Every accepted swap and final output is retained in samplers.json.gz and per-packet files. These diagnostics do not prove uniform conditional sampling, irreducibility or adequate mixing. The tails are explicitly exploratory comparisons, not calibrated p values. The suffix is unused by this fitting procedure, not globally untouched puzzle material.

## P05D: exact emission likelihood diagnosis on saved mappings

The initial objective uses only plaintext LM probability and omits ciphertext emission probability. Surjectivity alone permits codebooks that gain by moving many output runes onto frequently predicted letters. The follow-up freezes all saved candidates and adds the exact emission likelihood from the actual one-shot redraw encoder, with coefficient1and no optimization:

- First symbol or previous rune outside current bin: probability1/k.
- Previous rune inside bin,k>1: repeat probability.17/k; each other output probability1/k+.83/[k(k−1)].
- Unary bin: probability1.

Ten exact-rational finite branch enumerations (binsizes1through5,previousinside/outside) verify the formula and normalization. All56saved packets are rescored, without overwriting original selection or claiming a new null calibration.

True-map joint prefix ranks change to[5,3,5,5]forwelcome,[1,3,1,2]forjpg107-167,and[9,9,9,9]for each short held group. Only2/16truth maps rankfirst; all eight short controls remain last. The missing emission term explains part of the bias, but the corrected conditional objective still has serious source-model/short-text limitations. No weights were tuned to make truth win and no additional real optimization occurred. P05D preserves the failed original controls and saved-map alternatives in emission-evidence.json.gz/emission-results.json.

## Execution, evidence and next decision

Pilot20260916T220431.737924Z: exit0,0.903731s including compiler invocation and four controls. Full frozen procedure20260916T220551.690169Z: exit0,6.644549s for remaining12controls and40real/null packets. Emissiondiagnosis20260916T220721.889347Z: exit0,0.203395s. Total56packets,448restarts,2,240,000nominal proposal iterations; invalid proposals are counted separately in every restart. Installed Appleclang21compiled scalar C++; no installs/paralleljobs/Git/reserves/newimages. Raw commands/code/hash/exit logs remain under worker-p/runs. No process remains.

The finite-register count bounds P03/P04and actual search P05 answer different questions. P04's common-codebook obstruction for four frozen sources does not exclude unknown plaintext; P05's failed ranking does not validate a better cipher hypothesis. The useful next experiment is scorer/encoder identifiability on held controls, with a properly specified generative objective and independently justified training coverage, before another real optimizer. Parent requested this limitation be frozen if exact emission correction still fails; it has been frozen. No automatic wider restart, vowel variant or real search is queued here.

## Independent review12 update

Review12 independently reconstructs sources and448candidate scores, replays16control RNG traces, checks90exact-rational emission cases and1,016,500accepted-swap invariants. It identifies a stronger null-sampling limitation: stopping after a fixed number of accepted swaps follows an embedded jump chain whose stationary law is generally proportional to accepted-move degree, not uniform over constrained streams. An exact small(2,2,2)histogram/zero-repeat example has degrees2,4,6. Therefore the original null ranks remain descriptive even if mixing were excellent; they must not be promoted to exact-uniform conditional p values. Frozen sampler/results remain unchanged. See review-12/REPORT.md.
