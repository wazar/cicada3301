# S10 — unknown-label exposed-state recurrence
Tested one precise generative representation: a fixed arbitrary bijection maps runes toGF29states; each word obeys x_i=x_(i−1)+x_(i−2), with freefirsttwo states and separateper-pagebijections. No additivekeystream/plaintext decoding, Englishscoring orcoefficient/ordersearch. This addressesG09/G10's explicitunknown-relabeling exclusion while changingframing towordresets.

Original0 has147within-wordtriple equations;original1 has141. Both29variable coefficientmatrices have rank29, forcingallhiddenlabelvalues0. Hence neitherpage admits abijection for this specified generator. Saved29originalsource-row certificates independently yield integerBareiss determinants−321 and−48, residues27and10mod29. These nonzero residues certifyfullrank independentlyofmodularelimerowoutput. Exactrune/sourcecharpositions andwordindices retained for allrows andcertificates.

Controls:30randomhiddenbijections generated60actual-word-length pages fromword-resetFibonacci states; alltruehiddenmaps satisfytheequations, acceptedranks26–28, and reconstructexactlyfromreturnednullspacebasis.100tinyGF5systems in3variables were checkedagainst all125assignments each, includingentirenullspace solution sets andfullrankdeterminants whereapplicable. No claimthatconstraints recoverauniquemap inthese controls.

Disclosure: firstloggedrun had a disabledplaceholder for an extra GF29hiddenmap reconstructionassertion, althoughknownmaps already satisfiedequations andGF5solution spaces wereexhaustivelychecked. Thatassertion wasimplementedexplicitly and the samefrozenexperiment replayed successfully. Initialresult preservedasS10-initial-result.json andscopeexplainedinS10-CONTROL-CHECK.md. No realparameters/inputswerechanged; replayisnotcountednewcoverage. Runs20260917T010752.672735Z-S10 and20260917T010824.932475Z-S10-control-check bothPASS≈.145s.

Limits: exactexposedstate recurrence, fixedFibonacci coefficients, GF29bijection, explicitwordresets, no skip/rejection/errors. Hiddenstates, alteredcoefficients/order, interruptedgenerators andotheroutputrepresentations remainoutside scope. Rankdeficiencywouldnotbyitselfhavebeenapass. Alternativesliteral/copyinstructiondecoderwasnotimplementedbecauseopcodeconventionswereunmotivated. No solutionclaim.

Evidence: S10-result.json finalfullcontrols/tinyproofs/realcertificates;S10-CARD.md frozen;loggercode/inputhashes andcommands under runs/. ExistingS01–09outputs remainunchanged.

Resume exact controlledreplay ifneeded:
`.venv/bin/python exploration/persistent-01/run_logged.py --owner exploration/persistent-01/worker-s --label S10-control-check --seconds 900 --input exploration/persistent-01/worker-f/F06-maps.json --input exploration/persistent-01/worker-s/S10-CARD.md --input exploration/persistent-01/worker-s/S10-CONTROL-CHECK.md --input exploration/persistent-01/worker-s/S10-initial-result.json -- .venv/bin/python exploration/persistent-01/worker-s/s10.py`
