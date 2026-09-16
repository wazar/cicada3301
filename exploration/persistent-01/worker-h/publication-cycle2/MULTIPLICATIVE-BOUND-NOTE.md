# Narrow correction to a mechanistic exclusion rationale
The inspected historical table `liber-primus/analysis/campaign18_skip/armada2/COVERAGE-MATRIX.md:77` labels "Multiplicative / prime gematria" EXCLUDED-INDEP with rationale "Mechanistic (no closed multiplicative group mod 29)".

The nonzero residues modulo29 do form a multiplicative group, oforder28. All29residues includingzero do notform a group under multiplication, becausezero lacks an inverse. That narrower observation cannotexclude a bijectivegroup action on the complete29-symbolalphabet.

Constructiveexample: forprimitive rootg, `p_i = c_i * g^(c_(i-1)) mod29`, previouscipherinitial0. Everyfactor isnonzero; inverse `c_i = p_i * g^(-c_(i-1)) mod29` isdefined forallcipher/plain symbols. Zeroisfixed, withoutanexception branch. H17 checks all29previousstates×29symbols×12roots=10,092inversecases; fouractualsolvedsourceplants recoverexactly. This example is a possiblemathematicalconstruction, not a claim about Cicada'salgorithm or plaintext.

H17 foundno predictivefrequencygain ondiscoverytext (bestcontinuation gain-.001328nats/rune, model-specific199nulltail.88). H18 tests another totalaction, invertiblepower feedback; itfixeszero/one andpreserves multiplicative-orderclasses. Scope is these explicitlyboundedfamilies, not allnonadditivefeedback.

Inspected prior `round12/C1/feedback.py` and `campaign18_skip/ctfeedback_coeffs.py` use additive output shifts, evenwhentheirhistoryfunctions vary. This observation is limitedtothose codepaths and isnotanarchive-wide novelty claim. Historicalfiles were notmodified. No issueposted.
