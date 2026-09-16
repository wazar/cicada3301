# Continuous research controller

The root [start guide](../../START-CONTINUOUS-RESEARCH.md) is the entry point for the local agent.
The root [research contract](../../CICADA-CONTINUOUS-RESEARCH.md) tells each Codex turn what to do.

`keep_codex_working.py` starts another local `codex exec` turn whenever a normal turn ends. A finite queue, negative result, report, or commit is not its stopping rule. The controller uses one fixed deadline and disk checkpoints. It does not guarantee a discovery or useful model behaviour.

## Requirements

macOS or Linux, Python 3.10+, Git, and an installed, authenticated Codex CLI. The Mac Terminal helper requires macOS and permission to open Terminal. No Python packages are required. Use the existing project environment where suitable.

Keep one controller/coordinator per checkout. The controller locks the Git common directory, including across worktrees. The lock cannot detect every separately launched interactive agent, so inspect known worker state before launch.

## Start from the repository

Preferred local-agent handoff on macOS:

```bash
python3 tools/continuous-research/start_in_terminal.py --repo . --hours 8
```

The helper starts a separate Terminal, which owns the controller independently of the setup chat. It checks lock, PID, and active state. It does not claim that those checks alone establish scientific progress. Inspect the first turn log and checkpoint too.

The helper passes the already located Codex executable and selected Python interpreter. It shell-quotes paths, so spaces in the checkout path are supported. A process-scoped `caffeinate -i` is used when available. Closing the laptop, shutting down the machine, or terminating Terminal can still interrupt work.

If automatic Terminal opening is denied or unavailable, run this in a normal persistent terminal from the repository root:

```bash
python3 tools/continuous-research/keep_codex_working.py --repo . --hours 8
```

Do not substitute a short-lived background tool child and assume it will survive the parent agent. Do not bypass a denied permission. The helper never installs Codex, changes model providers, or sets credentials.

## Continuation and stopping

A Codex turn has a default maximum of 40 minutes. Completed shorter turns are immediately followed by another turn. The model must record useful results and next actions before returning. Fresh sessions read disk state; the controller does not resume an unrelated `--last` session.

Research state:

```text
exploration/persistent-01/STATE.md
exploration/persistent-01/QUEUE.json
exploration/persistent-01/experiments.jsonl
```

Inspect the controller:

```bash
python3 tools/continuous-research/start_in_terminal.py --repo . --status
```

Stop with Ctrl+C in its Terminal, or:

```bash
touch exploration/persistent-01/STOP
```

The STOP file is never removed automatically. For an interrupted window whose deadline has not passed:

```bash
python3 tools/continuous-research/start_in_terminal.py --repo . --resume
# Or, from a persistent terminal:
python3 tools/continuous-research/keep_codex_working.py --repo . --resume
```

Resume preserves the original deadline. A new start without `--resume` creates a new work window and requires owner authority. The helper will not start a second locked controller.

At a deadline or stop request, the controller interrupts its owned process group and escalates if necessary. Shutdown can extend slightly beyond the deadline; no new turn starts afterwards. Detached descendants in separate process groups cannot be guaranteed to stop. The contract forbids detached research jobs and requires PID records. After a hard interruption, inspect recorded processes before restarting. Never kill unrelated processes.

Three consecutive execution/protocol failures pause the controller. Five otherwise successful turns without a changed required checkpoint also pause it. This prevents an empty usage loop. A checkpoint change proves continuity, not scientific quality. These safeguards do not stop a normally completed research batch.

## Permissions and usage

The controller invokes the documented interface in this form:

```text
codex --ask-for-approval never exec --sandbox workspace-write --json --output-last-message FILE -
```

It keeps the configured model unless an owner supplies `--model` to the foreground controller. It does not disable sandboxing, ignore rules, use `--yolo`, switch accounts, or bypass a quota. Actions requiring unavailable approval remain blocked. Network access, protected Git writes, or pushes may be unavailable under the local configuration. Preserve results and continue permitted work rather than weaken the configuration.

Normal configured Codex allowance or API charges apply. Sub-agents also consume resources. Eight hours is a time limit, not a token or currency budget. Authentication, quota, service, permission, and machine failures can interrupt the session.

Raw prompts, JSON events, stderr, and final replies stay under:

```text
<git-common-directory>/cicada-keep-working/<run-id>/
```

The launcher does not stage, commit, or upload those private files. They may contain local paths or private repository content. Reviewed research outputs may be pushed under the owner's standing authority when current permissions permit.

## Tests and limits

Run from the repository root:

```bash
python3 -m unittest discover -s tools/continuous-research -p 'test_*.py' -v
```

All 12 local tests passed on 2026-09-16 in the preparation container. [Raw output](TEST-RESULTS.txt) is retained. Eight tests cover the controller with a fake Codex executable and temporary Git repositories. Four tests check helper path quoting, resume arguments, repository/status handling, and lock detection.

The controller suite checks continuation across turns, deadline preservation, stop requests, duplicate locks, no-checkpoint pausing, nonzero child exits, timeouts, event failure, and invalid budgets. The tests make no model calls and do not open macOS Terminal. They do not validate the installed Codex CLI, authentication, the owner's Mac, or cryptanalytic work. Local startup still requires observation.

The original downloadable package's first test run used a fixture deadline too short for startup. That fixture was corrected before its eight tests passed. This repository version changes the default mission path for repository-relative use and adds the Terminal helper and four tests. No original research result was changed.

## Interface and research references

Official Codex documentation checked on 2026-09-16:

- [Non-interactive mode](https://developers.openai.com/codex/noninteractive/)
- [CLI reference](https://developers.openai.com/codex/cli/reference/)

Starting research evidence:

- [OVERNIGHT-01 report](../../audit/reports/OVERNIGHT-01.md)
- [Full search report](../../exploration/overnight-01/REPORT.md)
- [Coverage gaps and resume notes](../../exploration/overnight-01/RESUME.md)

This controller is a local utility, not a hosted service. Uploading it does not start it.
