# PERSISTENT-02 publication evidence

C01 actual full-score/factor arrays and every actual/null metadata record are published. The798 null NPZ files (1,714,385,767bytes) remain unchanged locally; they contain redundant factor/baseline arrays reconstructable from the published ciphertext, explicit boundaries, fixed model and code. They are excluded from Git to avoid a roughly2GB publication pack. No original local file was deleted or overwritten.

`C01-null-array-manifest.json` records each local archive hash and every raw array shape/dtype/SHA256, plus hashes of the original full score arrays and all source/model inputs. `reconstruct_q12_null.py` rebuilds those arrays without reading the local NPZ files, using the existing pure Q12 functions and refuses mismatched hashes or output overwrites. Archive-container bytes/timestamps may differ; raw numeric array bytes must match. This is a lossless reconstruction recipe on the recorded environment, not a claim of cross-platform floating-point identity.

Recorded sample reconstruction verified all9 arrays for actual1-null00, including all732,511 score entries. Review02 independently verified all9 raw arrays and original full-score bytes for a representative reconstruction. This does not repeat the full scientific search or inflate coverage.

Example (choose an unused output path):

```sh
.venv/bin/python exploration/persistent-02/coordinator/reconstruct_q12_null.py reconstruct --name actual1-null00 --out /tmp/p02-actual1-null00.npz
```

The session logger may be used while its fixed research window is active. It deliberately refuses new jobs after the deadline; future research needs a separately authorised window. Pure reconstruction does not modify old evidence.

## R02 factor archives

The1,584 new histogram-sensitivity factor archives total2,153,015,659bytes. They remain unchanged locally and are excluded only fromGit through.git/info/exclude. Published cellJSON includes all fitted solutions, alternatives, bounds and scores. The pureW/B/q arrays are losslessly reconstructed by decoder/reset-feedback/histogram/publication/reconstruct.py, with per-array dtype/shape/raw-byte hashes and complete source/model/input pins in array-manifest.json.

Author checked case3/07-complementary-prefix-k7. Coordinator independently selected case0/19-p03-full-k5, reproduced all rawbytes and compared directly against the untouched local archive; evidence R02-publication-check.json. No optimizer or new scientific search was run. New ZIPcontainer bytes need not be identical in another environment. This avoids a>2GBGitHubpack while preserving exact reproducibility of these redundant factors.
