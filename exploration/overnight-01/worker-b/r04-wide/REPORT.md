# R04 wide extension

No readable new candidate. Executed1,307 page/period cells, each with an equally searched shuffled control, for2,614 fits; periods33–64 on45 discovery originals, excluding133 cells with fewer than two training observations per phase. `definition.json` explicitly lists every skip. Budget:115.383s logged actual runtime,68,231,664 variant evaluations,2,352,816 baseline evaluations and10,456 final restart evaluations =70,594,936 training objective evaluations. This is a separate authorised adaptive extension after the cheap initial pilot.

The same four-restart/five-coordinate-sweep procedure as R04 was used. First75% fitted, last25% checked once unchanged-phase; no refit to continuation. All keys, seeds, outputs and scores are in compressed per-cell files. Top20 by training are `top_candidates.json`; top20 by continuation are separately marked exploratory in `top_continuation_candidates.json`. Mean continuation:real−7.486463 versus shuffled−7.512053; max:real−6.384716 versus shuffled−6.184524. No interpretation of these descriptive maxima as significance or proof.

Initial R04 controls demonstrate exact recovery through period32 on a long493-rune synthetic English source; dedicated planted33–64 recovery controls were not run, so this extension has a specific unmeasured search-power limit. No literalF, feedback, Beaufort coefficient−1 on ciphertext, non-English or decoder skipping is covered. Exact additive signs are equivalent through unrestricted key negation. Long keys have33–64 adjustable rune symbols, explicitly compared with matched fitted shuffled controls.

Resume command (checkpoint complete):
```
.venv/bin/python -B exploration/overnight-01/run_logged.py --owner exploration/overnight-01/worker-b --label r04-wide-resume --input exploration/overnight-01/config.json --input audit/parallel-01/inputs/dataset.json --input audit/parallel-01/inputs/page-map.json --seconds 900 -- .venv/bin/python -B exploration/overnight-01/worker-b/search.py r04 --wide --pages 1440 --seconds 820
```
Scalar replay uses stored key and original ciphertext: `p[i]=(c[i]-key[i%period])%29`. The surrogate/exact scoring distinction and source-hash provenance are described in `../r04/REPORT.md`. No reserved page was decoded.
