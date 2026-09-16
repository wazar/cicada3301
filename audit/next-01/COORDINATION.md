# NEXT-01 coordination

Input working commit: `beee1b995e142ba920280736e9e45835abbf650a`.
Inherited baseline: `396001a9ce55e0e85ddef19e405afc6a13954588`.
The owner explicitly invoked the assignment; the document is its execution scope.
The original root prompt and macOS setup files stay outside assignment commits.

| Actual native agent ID | Ownership | Finite scope/budget |
|---|---|---|
| `/root/next_experiment` | `audit/experiment-01/` | Four recipes only; positive gates before calibration before two real slices; <=1800s total processing,300s routine; any named >300s main requires measured pilot and coordinator approval, maximum one1800s batch |
| `/root/next_alphanumeric` | `audit/alphanumeric-01/` | p49–51 transcription, structure and prior coverage; initial15min reasoning target; <=4 light processing batches300s each, <=6 small public retrievals30s each; no hypothesis search |
| `/root/next_f_model` | `audit/f-interruption-01/` | Known reference key-consumption and bounded synthetic unknown-F paths; <=1200s processing, <=4 main300s batches; no unsolved input |

Coordinator owns `audit/next-01/`, shared integration and Git writes. Three workers
launched concurrently; no nested agents. A has heavy slot1, C heavy slot2; B's
source reading/image work is lightweight. Existing isolated Python environment,
one numerical thread per job, no installs/new model training. Any failed scientific
control stops only that experiment. Audit-code defects may be corrected with before/
after evidence. No retries to tune away a valid failed control.

All actual processing commands use `run_logged.py`: unique run directories, actual
start/end UTC, elapsed time, current commit, selected input hashes, exact owned-code
snapshots, stdout/stderr and actual child exit/outcome. Seeds and experiment settings
are in each worker's frozen configuration/results, passed as hashed inputs. Read-only
source inspection commands and direct image viewing are separately described in
reports; they are not mislabeled experimental runs.

A fresh reviewer will start as a slot frees. Its scope includes freeze order,
failed-cell retention, one image ambiguity, an independently calculated F/key
consumption case, and bounded reruns without overwriting worker evidence.

Fresh native reviewer `/root/next_reviewer` launched after C stopped writing, with
exclusive `audit/next-review/`. It independently replayed selected controls and
checked an image ambiguity and literal-F key consumption. Two logged runs passed;
all workers and reviewer stopped before shared integration. No nested agents.
A's scientific gate failed at ordinal66; no negative calibration, shuffle or real
branch ran. B/C continued independently. No >300s command was authorised.
