# PERSISTENT-02 publication evidence

C01 actual full-score/factor arrays and every actual/null metadata record are published. The798 null NPZ files (1,714,385,767bytes) remain unchanged locally; they contain redundant factor/baseline arrays reconstructable from the published ciphertext, explicit boundaries, fixed model and code. They are excluded from Git to avoid a roughly2GB publication pack. No original local file was deleted or overwritten.

`C01-null-array-manifest.json` records each local archive hash and every raw array shape/dtype/SHA256, plus hashes of the original full score arrays and all source/model inputs. `reconstruct_q12_null.py` rebuilds those arrays without reading the local NPZ files, using the existing pure Q12 functions and refuses mismatched hashes or output overwrites. Archive-container bytes/timestamps may differ; raw numeric array bytes must match. This is a lossless reconstruction recipe on the recorded environment, not a claim of cross-platform floating-point identity.

Recorded sample reconstruction verified all9 arrays for actual1-null00, including all732,511 score entries. Review02 independently verified all9 raw arrays and original full-score bytes for a representative reconstruction. This does not repeat the full scientific search or inflate coverage.

Example (choose an unused output path):

```sh
.venv/bin/python exploration/persistent-02/coordinator/reconstruct_q12_null.py reconstruct --name actual1-null00 --out /tmp/p02-actual1-null00.npz
```

The session logger may be used while its fixed research window is active. It deliberately refuses new jobs after the deadline; future research needs a separately authorised window. Pure reconstruction does not modify old evidence.
