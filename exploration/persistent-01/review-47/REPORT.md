# Review47 — P27 reverse-half stability

PASS for all600 reverse panels and7,034 candidates. This is a separate follow-up on the same P26 data, not an independent replication. Review45's independent audit routines were adapted to the reversed split without importing production code or rerunning optimization.

Direct sequence counting confirms last22 pages train and first23 predict, with no page rotation accidentally giving23 training pages. Every parent JSON/NPZ hash matches its P27 reference; all1,200 P26 scientific files also remain byte-identical to the earlier review45 hashes. There are no new draws. Source/RNG validation therefore rests on review45's complete replay of these exact same inputs.

All reverse baseline probability rows, direct conditional likelihoods and analytic gradients agree (maximum discrepancy6.67e-15). All fits qualify; largest normalized gradient6.27e-7<2e-6. Recomputed each spectral acceptance threshold, phase ordering, gauge, alias grouping, candidate probabilities and training-only selection. Right-eigenpair residuals are at most1.00e-15. All reverse held terms and full45-page decoded increment arrays agree, including page255 sentinels and stutter zeros. This checks the saved eigensystem and optimizer result, not independently reproducing eigensolver/optimizer internals or exhaustively searching orders.

All primary sums use the separately trained baseline in each direction and exactly add the two held gains. Full affine alignment was independently recomputed via residue histograms for all28 multipliers and29 translations; selected-order alignments and every control candidate's truth alignment match. No canonical plaintext interpretation follows from affine order agreement.

Actual forward gain−7.58679985 plus reverse−27.86087867 gives **−35.44767852**. Five of199 null sums exceed or equal it, giving nominal primary tail .030. Selected orders match only5/29 symbols; maximizing affine maps are (7,14) and(17,1), with193/199 null alignments at least as large and descriptive secondary tail .970. Thus the actual result has neither positive aggregate prediction nor unusual order stability. The small primary upper rank cannot turn a negative gain into predictive improvement.

All four planted controls have positive sums, primary tails .01 and secondary tails .01. Cross-direction order matches10/18/12/9 are partial; reverse truth matches16/23/17/14 are also partial. They demonstrate sensitivity to these categorical source-marginal plants, not natural-language recovery or exact latent-order identification.

The same panels support both directions and were reused after P26 inspection. Nulls remain generated from the original-direction fitted baseline; the reverse procedure is fully replayed on every null, but this does not make the plug-in law exact or provide fresh holdouts. Multiple prior adaptive experiments, finite spectral candidate coverage and repeated discovery use preclude a campaign-level significance claim. Primary and secondary results were both retained rather than selecting the more favorable tail. No subsequent order/scorer/generator variant is included here.

One logged independent replay passed in12.45seconds, with no failed audit attempt. Inputs, production code/card snapshot, result tables and unchanged-parent check are retained. No shared scientific changes, reserves or Git operations occurred.
