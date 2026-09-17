# Q05-latin-clean — corrected source boundary

Removed only the16wordfragments/59runes/75tokens belonging to the legacyGutenbergfooter at sourcecharacter150887. All20,484preceding mapped words remain identical; all heldVirgil controls remain identical. Training now contains120,854runes and141,338tokens including boundaries. The sourcebytes, three internal heading exclusions, normalization, interpolation and held selection are unchanged.

Root independent checker and review42 reproduce every map/count and all27,000 log-probabilities exactly. The correction affects all probability normalizations: median absolute log-probability change .00053045, maximum18.608995nats. The largest change is context(Y,boundary)→J: the footer phrase 'by Julius' had created that transition. OriginalJcount2 came from 'Project' and 'Julius'; cleanJcount0. A small source contamination fraction was therefore not grounds to presume negligible ranking impact.

OriginalQ05model/source-map mistake and originalP25results remain retained and labelled. P25-clean repeats identical140panels/162keycells, inputciphertexts/nullseeds/boundaries, without choosing between models or expanding the search. Its report supplies measured candidate/rank effects. This is a corpus-boundary repair, not proof the puzzle is Latin or a universalLatin detector. Classicaltext normalization/genre/register limitations remain.
