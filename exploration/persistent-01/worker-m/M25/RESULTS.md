# M25 — skip-by-two coverage defect repaired; small real pilot misses

The reported transition gap is real for the scoped source/controls. Correct skip-by-two decoding recovered **allfour actual searched keys, all1,014 plaintext runes, exact rejection traces and exact terminal consumption**. For three controls the true plaintext is unreachable under skip-by-one even without beam pruning; the fourth has no rejection and is reachable under both. This is a construction-coverage improvement, not an LP2 solve.

Real originals0/17 produced incoherent fulloutputs, conditional-stuttermask null tails **0.26/0.61** (99 nulls/page), scores −4.6742328/−4.6421890. No key/offset/family expansion followed.

## Source and exact transition

Inspected `liber-primus/analysis/round18/L7-redteam/b1_power_envelope.py:enc_skip_by_two` rather than importing its side-effectful module or trusting prose. The actual encoder rejects a candidate equal to previouscipher with probability0.83, advances its key index by2 afterrejection, and by1 afteracceptance. The intervening burned keydraw is never tested. Existing `campaign18_skip/skipdecode.py` tests every skipped draw against previouscipher; its transition cannot represent many skip-by-two traces. Targeted OVERNIGHT/PERSISTENT source/report search found no implementation/search of the corrected rule. The historical25.8% claim was not rerun or restated as this experiment's measured recovery.

M25 freezes finite1024draw keys with no wrap/padding: prime-minus-one and integerphi sequences at offset0/page-reset, both signs (four candidates), already source-justified by the printed PRIMES/TOTIENT clue and earlier R03/P11. Integerphi literalF coverage is not this rejection construction. All buffers retained in keys.json. No dictionary or period/offset search was added.

At consumedindexj and candidate rejectioncountt, accepted keyindex is j+2t and plaintextp=(ci+sign*K[j+2t])mod29. Every rejected positionj,j+2,…,j+2(t−1) must yield previouscipher; odd intervening positions are unconstrained burned draws. Terminalconsumption is j+2t+1. The firstsymbol cannot reject because no previouscipher exists. Key exhaustion is a real finitebuffer constraint; incompletepaths are not scored as completedoutputs.

Exact DP state is absoluteconsumedindex and lasttwo rune/boundary LM tokens. The fixed objective is frozenP03 LM logprobability plus t·ln(.83) perposition plus ln(.17) when emittedcipher equals previouscipher, normalized by runes+boundaries. Thus both the transition and suppression prior are explicit. It is a maximum joint path score, not a summed plaintext posterior. No beam pruning or skipbudget is used. Same-state dominatedpaths are safe to discard because future transitions/scores agree. Retain16 gives exact globaltop16 path scores, with arbitrary choice among exactties; top1 statescore tables/diagnostics and fullwinning alternatives are saved. This retains bounded leading ambiguity, not every possible plaintext.

## Arithmetic, reachability, search and ranking separately

The upstream encoder function was extracted by AST without moduleimports/main. Forty fixed random fixtures matched its completecipher and rejectioncount exactly. Fifty short finitekey cases matched an independent enumeration of every valid acceptanceindex path, including top16 jointscores. Sourcehashes/full fixtures are saved.

Four complete groups excluded from LMtraining were planted and searched against allfour keys:

| Source | Runes | Rejections | True/selected terminaluse | Newrune errors | Skip1rune errors | Trueplaintext reachable under skip1 |
|---|---:|---:|---:|---:|---:|---|
| welcome |515|13|541|0|452|No, fails atposition50|
| jpg107-167 |319|11|341|0|286|No, fails atposition15|
| p56_an_end |85|0|85|0|0|Yes: no rejection in this fixture|
| p57_parable |95|5|105|0|58|No, fails atposition32|

Positions are zero-based. Allfour planted keys rankfirst; trueplaintext and exacttrace appear in correctkey top16 and win. The skip1 comparison uses the same frozen LM/prior and exact-state search, isolating transitioncoverage rather than a different beam/scorer. Constrained-plaintext reachability separately enumerates possible consumptionstates, independently of winner scoring. The29 real rejection events supply29 burned draws that fail the old tested-every-position rule. The zero-event fixture measures basic arithmetic/keyranking but does not discriminate constructions.

Controls beat every one of19 conditionalnulls each (tail0.05, minimum available resolution). Four related English fixtures cannot establish universal power. Non-English/register failure remains a limitation of the shared solved-rune LM; no independent non-English scorer was used.

## Null-design correction and chronology

Original wholecipher-permutation nulls gave realtails0.16/0.31. Those complete outputs remain **descriptive only**: the observedrepeat·ln(.17) term is constant across allkeys/paths for onecipher, but permutations change it along with the repeatdeficit. Source reasoning identified this problem during execution; summaryscores were seen before the calibrationcard, but keys/plaintextleaders had not been inspected. This chronology is explicit; the followup is sensitivity calibration, not blinded corroboration.

The fixed replacement null draws firstsymbol uniformly, copies previousgeneratedsymbol at exactly each observedstutterposition, and otherwise draws uniformly among28other symbols. It preserves the entire repeatmask/length/boundaries and hence the repeat-likelihood term, while changing unigramhistograms/higher-order structure. Four-key selection and winningtop16 are fully replayed.19draws/control and99draws/realpage, seed330827. Existing real/control outputs were reused without any new modelselection. The resulting0.26/0.61 tails concern this stipulated memory1 null only.

## Counts and retained evidence

Original280 complete searches plus274 conditionalnull searches = **554 fullsearch artifacts**, **2,216 top1 candidate decodes**, **554 winningtop16 decodes**. Four additional correctkeytop16 control diagnostics and four stride1 control decodes are distinct; short arithmetic tests are also separate. Audited storedsearch transitions:3,946,989 top1 path expansions and11,786,628 winningtop16 expansions.10,863 retained outputpaths were replayed. All finitebuffers, perrune rejection/burn/accept walks, consumptionstates, plaintext indices, ciphertext/nulls, maps, statistics (IoC×N/min32distinct/zlib), seeds and objectivecomponents remain under evidence/ and top-levelJSONs.

Pilot logged0.322s; originalcontrols/discovery17.219s; conditionalcalibration16.613s; completeevidence replay4.598s. OneCPU thread/batch. `check.py` re-encrypts each retainedpath, recomputes combined LM/filter scores, checks consumedcount parity, exactconditionalrepeatmasks and nulltails. `check-result.json` records counts and traceidentity. Exact commands, source snapshots/hashes and exitcodes are in runs/. No inheritedfiles modified, reservedpages read, Git writes or nestedworkers.

Decision: checkpoint this four-key/two-page transition pilot. It repairs one demonstrated mechanism gap but supplies no realcandidate. Bounds are the specified finite1024draw keybuffers/offset0/signs, stochastic0.83 outputrepeat rejection consuming2draws, and frozenEnglishrune/boundary register. LiteralF, hard suppression, alternative probabilities, infinitebuffers, otherkey/offset spaces and arbitrary drift remain outside this result. No broad family exclusion or automatic expansion.
