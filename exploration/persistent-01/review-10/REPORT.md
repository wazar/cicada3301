# Review10 — M25 skip-by-two DP

**NO-ERROR-FOUND within the fixed four-key,1024-draw,soft-.83 transition scope.** The independent kernel checks found no defect blocking a separately authorized input extension under these unchanged assumptions. This review did not execute that extension or rerun554 searches.

## Transition and exactness

Inspected M25's AST extraction of the upstream `enc_skip_by_two` function: it extracts that function alone with explicit `random` andN=29 bindings, rather than running the source module. The upstream function advances by2 on a rejected repeated candidate and1 on acceptance; the odd intervening draw is not tested. Independently implemented scalar encoding reproduces all40 stored upstream fixtures, complete ciphertext, decisions, rejection/burn/accept events and terminal use. The source hash matches.

Direct acceptance-index enumeration independently agrees with16160 transition cases across both signs, strides1/2, repeated-key patterns, all small candidate/previous symbols, exhausted indices and first-symbol handling. Eighty finite brute-path fixtures enumerate106 complete paths and include8 infeasible cases; every reported top16 joint score agrees. A separate84-path constant-key fixture stresses same-state ties and top16 retention. Explicit boundary checks allow the final valid key draw and reject overlength output without wrapping.

For stride2, a candidate acceptance indexa=j+2t implies plaintextp=ci+sign*K[a]. Each tested indexj,j+2,...,a−2 must encode previouscipher; every intervening odd index is unconstrained. Accepted drawa consumes througha+1. A nonrepeat acceptance contributes probability1, a repeat acceptance.17, and each rejection.83. There is no rejection on the first symbol. These statements reproduce the implementation including soft acceptance of an otherwise rejectable repeat.

The sufficient state is absolute consumed index plus lasttwo LM tokens at a fixed ciphertext position. Future transitions, LM scores, boundary insertions and remaining buffer then coincide, so dominated prefix paths can be discarded. Retaining16 best paths per sufficient state preserves globaltop16 complete **path scores**, with arbitrary tied identities. It does not enumerate all plaintexts or give posterior probabilities. The published calls use retain1/16; no guarantee is inferred for a hypothetical request for16 outputs while retaining fewer than16 per state. Scores are maximum joint path totals normalized by a fixed rune+boundary denominator.

## Complete control and key audit

Independently regenerated all1024 prime-minus-one values by trial division and all1024 integerphi values by gcd counting, modulo29; both signed copies match keys.json. No wrap, extrapolation or offset change occurs.

All four complete fixtures replay exactly, totaling1014 plaintext runes. Their rejection counts13/11/0/5 and terminal uses541/341/85/105 agree. Selected correct-key paths reproduce plaintext, rejection counts and terminal draw consumption exactly. All29 burned positions fail the old tested-every-position condition in these fixtures.

Independent constrained-plaintext reachability reproduces the stride1 failures at zero-based positions50,15,32 for welcome,jpg107-167,p57; p56 has no rejection and remains reachable under both rules. Stride2 reaches all four complete plaintexts. This checks representability separately from LM ranking or beam width.184 saved retained paths were independently re-encoded and rescored with the independently constructed P03 table from review08; no M25 LM/decoder import was executed. The scoped decoder functions were AST-extracted for comparison against the independent enumeration, not trusted as the reference.

## Calibration and unchanged real inputs

All274 corrected null ciphertexts preserve their original **entire adjacent-repeat mask**, lengths and boundary locations. Saved null scores match calibration records; tails recount to.05 for each control and **.26/.61** for real0/17. Both null families reference the same saved real outputs and exact scores−4.674232774206064/−4.642189046369565, with output hashes recorded. No new real key/leader selection was introduced by calibration.

The observed-repeat likelihood term is constant across all paths and four keys for one fixedcipher. It cannot affect within-input ranking, but it does change cross-input null comparisons. Real0 has2 repeats, whereas its original shuffled nulls have3–16(mean8.838); real17 has0, versus3–16(mean9.515). Each added repeat shifts the unnormalized score byln(.17)=−1.77195684. Thus the initial.16/.31 permutation tails carry the disclosed systematic repeat-count change. The corrected masks remove this specific mismatch, while changing unigram counts and higher-order dependence. Neither null identifies the actual cipher mechanism; calibration is explicitly post-inspection sensitivity analysis, not independent corroboration.

Counted554 saved fullsearch artifacts without rerunning them; this review directly validates selected complete paths and all corrected masks/tails, not every stored DP expansion count. Controls have only19 nulls, so.05 is their minimum attainable empirical tail and is not p<.01 evidence. Four related English fixtures provide a narrow construction/register envelope.

## Disposition

Retain M25's transition-coverage improvement and corrected conditional-null miss with the existing qualifications. No numerical correction required. The bounds remain the four fixed finite1024-draw key buffers, offset0/page reset, both stated signs, stochastic repeat rejection consuming2 draws, and frozen English rune/boundary scoring. LiteralF, other suppression values, infinite streams, other clocks or non-English recovery are outside scope.

Code snapshots, exact hashes, brute cases and findings are in review-10. Logged kernel check.088s; complete trace/calibration check1.011s, one numerical thread. No reserved pages, Git changes, nested workers or active process. Release the review slot.
