# Lossless publication recipe for R02 factor arrays

The1,584 local histogram/cells/case*/*.npz archives remain untouched. Their exact compressed file sizes total2,153,015,659bytes; filesystem allocation may differ. All JSON fit results, alternatives and selected outputs remain published unchanged. Instead of adding the redundant factor archives to Git, publish array-manifest.json and reconstruct.py with their pinned dependencies.

Each manifest record identifies the original archive path/SHA256/bytecount, its resultJSON/hash, case/panel/model/horizon/k, and every W/B/q array's dtype, dtype-string, shape and SHA256 of C-order raw bytes. Sourcepins include the script, exact arithmetic model.py, both numeric modeltables, frozen panels and original inputs/pins. NumPy/Python versions are recorded. The script checks all sourcepins and cellJSON hash before rebuilding; every reconstructed array must match its original metadata and raw hash exactly. No optimizer is imported or run.

From repository root, reconstruct any named cell to a NEW output path:

```sh
.venv/bin/python exploration/persistent-02/decoder/reset-feedback/histogram/publication/reconstruct.py reconstruct --name case3/07-complementary-prefix-k7 --out /tmp/r02-case3-panel07-complementary-prefix-k7.npz
```

It refuses overwriting an existing path and requires explicit.npz suffix. The archive container is not promised byte-identical across NumPy/ZIP environments; the raw arrays are. Original archive hashes identify original local artifacts. Reused sixteen actualpanel0cells never had separate histogram factor archives and are excluded from the1,584 records.

Author sample case3/07-complementary-prefix-k7 passed all three rawarray checks; its newly generated NPZ also happened to match the original container SHA256. Logged command and output: publication/runs/20260917T095640.646294Z-author-reconstruct. Manifest construction logged separately and preserved all original files. The independent coordinator selected case0/19-p03-full-k5 and verified every rawarray byte against the untouched local archive; see ../../../../coordinator/R02-publication-check.json.

No scientific result, score, seed, rank or local archive changed. Git staging/exclusion is handled separately by the coordinator.
