# Worker F — separator models and a typography confound

No cipher candidate or plaintext. **Source-line starts have a reproducible rune bias, but a simple glyph-width wrapping process reproduces its magnitude.** This is a concrete omitted-layout explanation, not evidence for line-reset encryption. All ten reserved originals remain excluded. Discovery0,1,17 images were viewed; no independent full transcription is claimed.

## F01: exact-stream-preserving boundary test

45pages,10,466runes,2,662regex-per-line words,480nonempty source lines. Independent uniform circular shifts of each page's complete word/line label schedule preserve the stream, exact histogram and every genuine transition/doublet; actual page-seam transitions are never scored. There is no Markov sampler or mixing issue. Eight frozen endpoints and999null rotations, repeated as a predeclared edge-trim sensitivity. Raw offsets/statistics retained.

Word starts, ends, nonself transition pair distributions and doublet placement give rawtails .162,.279,.118,.787. Source-line-start identity gives G79.4447,0/999exceedances, Bonferroni8=.008; trimmedG65.8090 also0/999. Other line endpoints ordinary. Treating the two sensitivity analyses jointly gives16*.001=.016, still descriptive after the wider adaptive programme. Baseline0/8 and all three planted word-boundary mechanisms8/8 detected at the fixed family threshold;32full-size controls each had199nulls. These are explicit strong fixtures, not universal power.

## F02: different output-role explanation

Lengths and length-by-terminal-symbol page profiles compared across33observed contiguous original-page pairs. Whole-page permutation preserves all within-page structure. Clustering tails .1525 and.2695 (two-test .305/.539). All24strong grouped-role controls detected;2/8baseline controls rejected, too few to estimate calibration accurately. Page sample sizes/position exchangeability remain limitations.1,999real permutations plus32controls*499permutations retained.

## F03: word-conditioned diagnostic

F01selected this adaptive follow-up. Excluding45page starts leaves435line starts. Conditional permutations preserve page, within-word-offset(capped4), word-length(capped8) and number of starts per stratum;427starts are movable. G65.9294 and threefold predictive statistic13.5379 both beat1,999nulls. Folds by page modulo3 contribute[-.7888,3.3156,11.0111], so prediction is uneven and not untouched validation. No single page dominates: largest omission delta6.5052 from original17. Width-dependent wrapping remains unconditioned by this null.

## F04: image-grounded alternative explains the bias

Viewed originals0/1/17:12physical text rows on each; raw-row counts/left-edge sequences align. Original0 has a dropcap spanning first3rows; original1 is plain black type. For original1, full-resolution column components were measured inside12fixed text strips. Eight strips have exactly as many tall components as source runes; only these were aligned. All29runes have samples. No merged component was manually split; rejected rows and every component coordinate retained.

Median ink widths+fixed5px nominal gap range14px(rune10,I) to92px(rune28,EA). Enrichment correlates .7312 with width. Actual435noninitial starts have mean width52.9793px versus49.1842px overall. A greedy renderer with constant1180px line budget, actual rune stream and14px separator cost reproduces a comparable start bias:1,000simulations give independenceG median59.3671 and95%interval[38.1363,87.4561], versus observed62.4586 (tail.3956). Correcting expected frequencies by width leavesG31.0424 (simulationtail.3107). Equal-width200controls instead give median25.7306 and95%[16.3734,39.8043]. Thus this plausible plain-layout construction is enough to explain the observed statistic; reset-cipher inference is unwarranted.

This is approximate physical layout, not exact font/renderer recovery: unknown bearings/kerning, margins, headings and separator types matter. Simulated466–484starts exceed actual435. This prevents claims of exact reproduction but does not undo the demonstrated confound. F01/G79and F04/G62 are different likelihood statistics:2x29start/nonstart association versus multinomial start frequency against global frequencies, plus F04excludes page starts.

## Evidence and continuation

Each F01–F04 has a pre-execution card, source, logged immutable source snapshot, scalar result and full compressed raw null/control evidence. F01-maps.json pins rune/word/source-character coordinates. Main job elapsed seconds:9.3943,1.8761,8.8875,1.8500; these are child wall times, not CPU usage. Exact counts are in result files. The earlier human-message denominator478was a mental sum error; arrays always contain480and F03explicitly435after45page-first exclusions.

Next executable jobs:
1. F05: distinguish explicit hyphen versus period separator role using label permutations among actual delimiter locations, conditioned on page and physical-row-start status. This avoids the now-demonstrated width confound; retain stream/rare doublets exactly.
2. Independent F04 review: recount image component alignment and implement greedy-layout simulation separately; test a source-supported width-aware null before any line-reset cipher attempt. No reserved reveal.

Strategy outside-box-v1; coordinator/root; deadline2026-09-17T03:30:37Z unchanged. STOP honored. No Git operations or nested agents.

## F05/F05b/F06: explicit punctuation and corrected units

F05uses only actual period/hyphen events, retaining2,310interior events:134periods,2,176hyphens. Page-and-line-start-conditioned label permutation preserves ciphertext and actual separator placement. Rune-before/rune-after tails .117/.3315; no role signal. F05's provisional fragment-length endpoints are superseded by the separately saved F05b, whose explicit-unit length tails are .050/.916 (family min.20). Both retain1,999realnulls and24controls*199nulls;baseline1/8and bothstrongroleencoders8/8detected. Periods at terminal page edges are outside the two-sided event test.

F06produces a separate explicit-delimiter-unit parser: **2,662per-line fragments become2,355units,307spanningphysicalrows,maximum14runes**. Join only empty/whitespace-only gaps; never join acrosspages. All hyphens/periods/mixednumeric/&/$gaps remain preserved exactly. Four synthetic parser controls pass. Original0indices83–89spanrows3/4: row3's terminalIand row4's sixinitial runes form oneunit without an interposed marker. Original1indices21–24spanrows0/1: three row-final runes followed by row1's initialEA, again before the visible nextseparator. This is a bounded visual check of missingnewlinepunctuation, not a full reread. `F06-maps.json.words` contains new units; its inherited `labels` field is explicitly the originalF01fragment/line schedule, so downstream unit boundaries must come from `words`.

## F07/F07b: whole-unit output and rotation capability limit

Indexsum and primesum mod29of2,355explicitunits give rawtails .346,.635,.867,.677 under999exact-stream circular-boundary rotations. However F07's four strong constantlength4fixtures fail most detection checks: the boundaryschedule has onlyfourdistinctphases, so aboutonequarterofrotationsretainplantedword sums. Exactdecoding stillpasses. **F07alone is detector-limited, not a sound negative.** At mostone pseudo-unit crosses the circularpage seam; the null remains phase-exchangeability conditional.

F07baddresses that specific ambiguity without rescoring realinput: all45actualunit schedules have trivialstabilizer, hence asmanydistinctphasesasrunes. Four matched-varied-length fixtures now recover and detect the designated bias/dependency exactly, each tail1/200and fourtest.02. Prime one-rune support is explicitly handled:7biased and13Markov targets require declared resets to attainable residues; none in indexfixtures. Every rejection loop is capped1,000; all targets/streams saved. These are fourstrongcontrols, not populationpower. They establish a narrow capability on actualschedules; absence of these strongsumstructures does not exclude arbitraryword-levelmechanisms.

## F08: complete contiguous signatures against frozen in-book sources

Nine frozen solved publicgroups (733explicitunits) form the complete sourcefamily. Search all contiguous unitlength signatures, extending exact8unitseeds; count3,137,572dictionaryprobes over real/matchednull/control scans. Real maximum is7units, no>=8unitcandidate.999wholeunit-orderpermutations yield tail.936. Therefore no realspan was admitted to affine/substitution/periodicconsistency checks; zero realtransformchecks is deliberate, not missing work. Each of9affine2x+3planted complete-source controls is recovered exactly, with expected affinekey and tail1/100against99matchedpermutations. These are controls for knownreferencepassages, not independent plaintext discoveries. Non-length-preserving encoders, literal-F mismatches and othertexts are outside scope.

## Latest checkpoint

F01–F08and the two suffixedfollowups are complete; no localprocess remains. F05/F05b/F06/F07/F07b/F08childwalltimes2.9108/3.0775/.0453/2.3105/.7870/4.6168seconds. No installations/network/Gitwrites. Originaldata unchanged.

Concrete next options for coordinator allocation:
1. Test whether preserved numeric/mixedgap fields imply a finite index or order relation using **only F06gaps** and explicit coordinate outputs; define validity before transformation. This changes outputtarget away from prose and sums.
2. Select a source-backed visual annotation rule from alreadyviewedoriginal0redheading, verifying its exact13runeextent and contrasting image-confirmedblackbody; coordinate with existing OB-LAYOUTlane rather than duplicating it. No reservedimages.
3. A fixed delimiter-unit substitution model could be constrained by complete repeated-unit patterns; first measure repeatedunit classes and matchedcontrols before selecting a plaintext lexicon. This is a new encodingunit, not an arbitrarypad.

## F09: deterministic whole-unit repetition constraint

Completed before the coordinator prioritized numberedfields. Among units length>=2, real ciphertext has92equal-unit occurrencepairs and maximumclass3;999exact-streamrotations give upper tails.512/1.0. Twenty injective no-internal-doublet codebooks driven by the nine solved-source token distributions and actualunitlength schedules produce25,031–27,847pairs and maximumclasses80–113. Allobservedlengths are covered by those sourcepools. First4controls eachbeat100rotations at bothendpoints, two-test.0198. This weighs against the tested deterministicwholeunit codeword model in that observed register, not homophonic/stateful coding or another source distribution. No dictionaryplaintext was fitted to realcipherunits.

## F10: source-grounded numbered regions

Actually viewed originals10,36,37,38; exactimagehashes and redpixelboundingboxes saved. Original10's blackinline7is inside a sentence and is notpartofredlist1..5. Original36has introtext thenred1;37hasred2,3,4;38continues4thenred5, ending5at a redsectionbreak. Exactsegmentation follows those labels and source & marker. Item4is concatenated acrossobservedpages37→38, with whitespace-onlyunit joining; no other pagejoins introduced into previousexperiments.

Fiveitems have rune/unitcounts139/30,91/20,98/25,96/19,129/28. Thus they are not length-preserving successive encodings of onefixedobject, nor identicalfullunitlengthtemplates. The frozen alternative predicts a commonfirst4orlast4unitlengthtemplate: pairwiseL1distances74/82, selectedmaxcalibrated against999withinitempermutations, tail.194. A common-prefixfixturegives.005;1/8baselinefixturesat.05. This rejects neither normalnumbering nor genericmulti-stepinstructions; it simply supplies no measurablecommonobject/template relationship for the twoexplicitfamilies. No arbitrary5characterextract was treatedasplaintext.

Final workercheckpoint: F09/F10childwalltimes3.2225/.9701seconds; no jobsrunning. The substantiveadvance is identifying and testing a typographyconfound, plus independently correcting the unitrepresentation(307linewrapjoins). Otherboundedfamiliesyield no crediblecandidate. Reviewer02is independently checkingF01/F03/F04undercoordinatorcontrol.

Ready followups with explicitdecision:
- Refine physicalwrapping prediction using per-glyphadvances from only original1acceptedrows, then predict12observedlinebreaks on alreadyviewedoriginal17without refitting; test whether advance/margin uncertainty explains remaining rendercount discrepancy. This is a renderer explanation test, not decodersearch.
- For numbereditems, test a fixed shared-parameter instruction grammar only if a complete source-backed grammar or repeatedcipherunit structure can constrain it. Currentcounts/template do not warrant arbitraryn-th-symbol extraction. If no suchconstraint exists, reallocate to a differentmodel ratherthan generating tiny freeformoutputs.
