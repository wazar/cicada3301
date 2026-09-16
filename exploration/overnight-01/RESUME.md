# Replay and continuation

All scheduled cursors are complete. Nothing is running. These commands are for deterministic replay or recovery of a genuinely interrupted copy; they are not additional work executed in this session. Some scripts write fixed lane checkpoints/check outputs. Run on a disposable checkout/copy when preserving this published evidence. Use the committed virtual-environment requirements; no installation was performed here.

From the repository root, independently reproduce retained outputs (the reviewer code is separate from the search implementations):

```sh
.venv/bin/python -B exploration/overnight-01/run_logged.py --owner exploration/overnight-01/review --label retained-replay --input exploration/overnight-01/config.json --input audit/parallel-01/inputs/dataset.json --seconds 900 -- .venv/bin/python -B exploration/overnight-01/review/check.py
```

R01/R02 fixed-rule replay, including stored F alternatives:

```sh
.venv/bin/python -B exploration/overnight-01/run_logged.py --owner exploration/overnight-01/worker-a --label retained-replay --input exploration/overnight-01/config.json --input audit/parallel-01/inputs/dataset.json --input audit/experiment-01/keys.json --input exploration/overnight-01/worker-a/r02/keys.json --seconds 900 -- .venv/bin/python -B exploration/overnight-01/worker-a/replay.py
```

Checkpoint resume for numeric, initial periodic, cross-page and layout queues (already complete):

```sh
.venv/bin/python -B exploration/overnight-01/run_logged.py --owner exploration/overnight-01/worker-b --label r03-resume --input exploration/overnight-01/config.json --input audit/parallel-01/inputs/dataset.json --seconds 900 -- .venv/bin/python -B exploration/overnight-01/worker-b/search.py r03 --seconds 820
.venv/bin/python -B exploration/overnight-01/run_logged.py --owner exploration/overnight-01/worker-b --label r04-resume --input exploration/overnight-01/config.json --input audit/parallel-01/inputs/dataset.json --seconds 900 -- .venv/bin/python -B exploration/overnight-01/worker-b/search.py r04 --pages 1440 --seconds 820
.venv/bin/python -B exploration/overnight-01/run_logged.py --owner exploration/overnight-01/worker-b --label r05-resume --input exploration/overnight-01/config.json --input audit/parallel-01/inputs/dataset.json --input audit/parallel-01/inputs/page-map.json --seconds 900 -- .venv/bin/python -B exploration/overnight-01/worker-b/structural.py r05 --seconds 820
.venv/bin/python -B exploration/overnight-01/run_logged.py --owner exploration/overnight-01/worker-b --label r06-resume --input exploration/overnight-01/config.json --input audit/parallel-01/inputs/dataset.json --input audit/parallel-01/inputs/page-map.json --seconds 900 -- .venv/bin/python -B exploration/overnight-01/worker-b/structural.py r06 --seconds 820
```

Every executed command, including R04-wide, numeric F, original55 catchups, width1024 follow-ups and binary tests, is preserved verbatim as an argument array in `execution-summary.json` and the corresponding `runs/*/command.json`. These manifests also locate the immutable execution-time source snapshot and exact input hashes. Prefer that snapshot for reproducing an older batch over assuming the final script is identical.

R07 supports deterministic individual replay using `worker-c/search.py MODE --start ID --stop ID+1` (substitute recorded integers; add `--page55` for its separate catchup). `f-jobs.json` fixes F enumeration. Supply the logger and the exact source/input list from that candidate's batch manifest. R08 is the finite `worker-c/binary.py` matrix, likewise recorded in its command manifest. The full keys, bytes, consumption paths and rune outputs in the registry permit independent arithmetic without rerunning the search.

Potential next work is a **new finite tranche**, not an unfinished checkpoint: broaden R02 F keys independently of rigid scores or R07 finite F offsets beyond49/51. Freeze the new job list, representative controls and count before execution. No wider search or holdout reveal is already running or claimed here.
