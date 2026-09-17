# Proposed next C-lane discriminating test: seed-invariant phase collisions

Written before longer-seed actual decoding results. This is a proposed experiment, not an executed finding. It stays within Q12's exact uninterrupted sign-minus recurrence and does not expand a brute-force key search.

If p[i] = q[i] + e[i mod(k+1)] mod29, equality between two plaintext runes in the same phase is exactly equality between their baseline q values. Therefore the number of equal pairs within phase classes is independent of every seed and of the zero-sum constraint. This can test whether the longer-seed family retains ordinary nonuniform symbol frequencies without relying on an English language scorer. It cannot identify this recurrence uniquely or detect a deliberately frequency-flattened plaintext.

Primary object: the frozen716-rune section body, with no heading-policy search. A finite band k=2 through floor(N/20)-1 gives at least20 observations per phase. This sample-size rule is fixed before actual collision scores; it is a diagnostic period band, not a claim that these lengths are clue-supported. No key enumeration. Retain counts and denominators separately, phase histograms, all periods and input hashes.

Controls should independently encode fresh source excerpts with predeclared seeds/lengths spanning the band and check the equality invariant exactly, then measure detection against matched first-rune/adjacent-equality-mask controls. Also include uniform plaintext as a competing construction; nonuniformity alone is not semantic language recognition. No universal perfect-language gate, but arithmetic identity must pass.

Suggested calibration: one fixed family statistic max across periods after pooled symmetric within-period standardization over actual plus199 fixed-seed comparator panels. Every comparator runs all periods. Store raw collision fractions and the entire panel matrix. Rank is conditional on this comparator, not a global programme-wide p-value. Full histogram-preserving permutation is a distinct possible sensitivity test only if a substantive result warrants it, not an automatic second null sweep.

Decision: if controls are detectable and actual is ordinary, deprioritize extending seed lengths merely to improve English scores. If a period is exceptional, freeze it and test source-supported section continuation before any candidate claim; a high collision count is not plaintext. This challenges the assumption that an English score is needed to decide whether more seed fitting is useful.

Owner lane should turn this into a final preregistration with deterministic seeds and precise test population before execution. Review the tiny invariance implementation independently. No reserved page access or new scorer is required.
