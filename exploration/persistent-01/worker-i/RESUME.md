# Resume worker I
Read PREREG.md and REPORT.md; current source input is original images0/1 only. Reserved originals untouched. Fixed global deadline2026-09-17T03:30:37Z; obey exploration/persistent-01/STOP. All work one process, one numerical thread via logger.

Exact deterministic reproducibility commands (reruns do not count as new coverage):
```
.venv/bin/python exploration/persistent-01/run_logged.py --owner exploration/persistent-01/worker-i --label replay-geometry --seconds 900 --input liber-primus/data/relikd/p0.jpg --input liber-primus/data/relikd/p1.jpg -- .venv/bin/python exploration/persistent-01/worker-i/glyph_test.py
.venv/bin/python exploration/persistent-01/run_logged.py --owner exploration/persistent-01/worker-i --label replay-width --seconds 900 --input exploration/persistent-01/worker-i/coordinates.json --input liber-primus/data/relikd/p0.jpg --input liber-primus/data/relikd/p1.jpg -- .venv/bin/python exploration/persistent-01/worker-i/width_test.py
```
Next substantive alternatives: internal stroke landmarks or fractional typography model, as detailed REPORT.md. No further parameter tuning of failed coarse two-state geometry models is justified by current data.

I05/I06 continuation complete: actual pixel-column adjacency graph had8/138 repeats, p_lower=.9624 versus10k row-profile permutations; control power18%. See appended REPORT.md. Replay:
```
.venv/bin/python exploration/persistent-01/run_logged.py --owner exploration/persistent-01/worker-i --label replay-pixel-columns --seconds 900 --input exploration/persistent-01/worker-i/coordinates.json --input exploration/persistent-01/worker-i/width-arrays.npz --input audit/parallel-01/inputs/dataset.json -- .venv/bin/python exploration/persistent-01/worker-i/column_test.py
```
No active processes. Next substantive work needs new card: continuous nearest-x graph with explicit ambiguity/gap breaks or internal stroke landmarks, not more threshold tuning of x bands.

P11 existing-method rotation COMPLETE:11,520real+11,520matched-null cells, two independently selected scorers each, no further sweeps. See P11-REPORT.md and p11/publication/. Root review pending; all rawshards remain local unchanged. Reproduction without furthersearch:
```
.venv/bin/python exploration/persistent-01/worker-i/summarize_p11.py
.venv/bin/python exploration/persistent-01/worker-i/publish_p11.py
```
These rebuild summaries/publication only and are not new scientific coverage. Exact replay cell metadata identifies phi offset/sign, ciphertext, literal sites and consumed-key traces; everycandidate reencrypted duringgeneration. No active processes. Further work requires root's new bounded assignment, not a phi-space extension.
