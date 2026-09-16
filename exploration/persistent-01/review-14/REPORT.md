# Review14: coordinator/Q01

The scalar state convention, training/held separation, conditional probabilities and saved result accounting check out. One implementation deviation from the preregistered card was found: real nulls use seed331321, not330901. The original card/code/results were preserved, and root acknowledged the discrepancy without rerunning or selecting another seed. This review concerns coordinator/Q01 only, not worker-q/Q01.

State before predicting position i is parity of marker occurrences strictly before i, with page-start state0. The previous rune therefore toggles state before the current prediction; a forced repeated marker toggles again on the next position. Counts and generation use exactly that convention. A marker can itself be emitted from the current state's distribution and then acts on subsequent symbols; the implemented model is not an escape that removes a marker from the observed stream. No generator/predictor mismatch was found.

Training uses even sorted discovery ordinals0,2,...44 (23 pages), held uses odd ordinals (22). The count update never reads held targets. All29 marker choices are selected by training gain only; each packet's held statistic uses the selected marker and the same held nonrepeat denominator. Saved held scores for other markers do not enter selection. First runes are omitted from prediction scoring/count targets but determine subsequent state; generators sample those first runes from state0. Repeats are imposed by the fixed mask and contribute no score, while still affecting state.

At a nonrepeat position, excluding the preceding rune and renormalizing w[y]/(1−w[x]) gives a valid distribution. Forty-eight exact rational five-symbol sequence enumerations (three marker choices ×16 repeat masks in a three-symbol toy) independently sum to one, including repeated-marker toggles. These are the explicitly imposed-mask generative laws. They do not establish equivalence to conditioning an arbitrary unrestricted hidden-state process on its entire future repeat mask.

Fresh verification, without importing q01.py:

- Rebuilt scalar counts, weights, all29 per-page gains, training selection and held scores for8 saved panels: real, controls0/6/11, real nulls0/198, control0 null0 and control6 null18.
- Checked all440 saved panel inventories and training-only choices,12,760 marker fits, all saved score denominators and all13 reported tails. This does not repeat all440 fits.
- Recreated all12 control Dirichlet vectors/permutations/markers and random arrays from seeds, then independently regenerated every control ciphertext using scalar inverse-CDF arithmetic.
- Reconstructed four first-null panels and independently replayed the complete first-null RNG arrays for all13 calibration streams. All masks and observed outputs in this bounded generation subset agree.

Real scalar score is−.0031225107383871563 nats per held nonrepeat, marker13; tail is41/200=.205. All12 controls recover their planted marker and have positive held gains; each beats all19 saved nulls, giving1/20=.05. The controls therefore demonstrate the claimed planted effects, but their19-null resolution cannot meet the distinct .01 real review trigger. They do not establish universal power for low marker occupancy, almost equal state weights or other state conventions.

The actual null seeds are331763 through331772 for control0 through control9,331812 for control10,331813 for control11, and331321 for real. These match saved draws. There are no seed collisions among these13 null streams or the12 control-generation seeds330902 through330913. The byte-sum seed scheme can collide for other names, but no such collision occurs here. Exact seed evidence is in seeds-and-estimator.json; original source/card/result/input snapshots are retained locally.

The counts+.5 estimator is the frozen procedure, not the likelihood maximizer for exclusion-normalized transitions. More strongly, in the homogeneous all-nonrepeat chain the stationary destination frequencies are proportional to w[x](1−w[x]), generally not w[x]. An exact three-symbol example with w=(1/2,1/3,1/6) gives stationary counts(9/22,4/11,5/22), verified by rational arithmetic. Thus even abundant destination counts need not recover the transition weights used by the generator. Parametric nulls generated from those fitted weights and refitted by the same rule remain descriptive plug-in comparisons, not an exact calibrated composite-null test. Root's scope restriction is warranted; the negative real held gain supplies no broad exclusion of control-symbol ciphers.

Both review batches passed (2.477s and.091s). No failed checks were discarded, no null or optimizer run was expanded, and no shared or historical file was changed. Review complete.
