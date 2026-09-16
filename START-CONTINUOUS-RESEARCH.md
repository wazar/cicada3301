# Start continuous Cicada research

This is the setup entry point for the owner's local agent. It is not another research checklist.

**Goal:** start one external controller that requests successive Codex research turns for eight hours. A completed search batch must not end the work window.

## Read these files

- [Research contract](CICADA-CONTINUOUS-RESEARCH.md)
- [Controller instructions and limits](tools/continuous-research/README.md)
- [Controller](tools/continuous-research/keep_codex_working.py)
- [Mac startup helper](tools/continuous-research/start_in_terminal.py)

No ZIP download, file copying, package installation, or new framework is needed. All required files are in this repository.

## Setup assignment

When the owner tells you to use this guide, perform the following steps. Do not stop after summarising the files or suggesting the commands.

1. **Update safely.** Confirm this checkout's remote is the owner's `wazar/cicada3301` fork. Fetch and fast-forward from `origin/master` when safe. Preserve local setup work, newer commits, and unrelated changes. Do not reset, force-pull, auto-stash, or discard work. If integration conflicts, stop setup with the exact conflict instead of guessing.

2. **Check for an existing controller or research coordinator.** Use the status command below and inspect recorded worker PIDs. Do not create a second controller or researcher group. An already active controller should be reported and left running. A stale record is not proof of an active process. The owner STOP file must not be removed automatically.

3. **Inspect and test.** Read the two Python launch files. Choose an existing Python 3.10+ interpreter; the project's Python 3.12 environment is suitable when present. Run the local test suite once. These tests call a fake Codex program, not a model. Check the installed `codex --version` and `codex exec --help`. Keep the existing model, authentication, rules, and permission settings. Do not install software or enable unrestricted access.

4. **Start the external controller in its own macOS Terminal window.** Use `start_in_terminal.py`, not a short-lived background child of this chat. The helper creates a private `.command` file, opens Terminal, and checks for a live controller lock and PID. It uses process-scoped `caffeinate -i` when available; it does not change system power settings. This handoff is authorised when the owner assigns this guide. It does not authorise unrelated GUI actions or permission bypasses.

5. **Verify the actual handoff.** Read the controller status and the first turn's private log. Confirm the deadline, live PID/lock, successful Codex startup, and an initial research action or checkpoint. Opening a Terminal window alone is not proof. Do not read authentication secrets or publish raw private logs. Once the controller is active, this setup session must not launch competing research workers.

6. **Report the result, not an estimate.** State whether startup was verified, the actual deadline in the owner's timezone, the status/stop commands, and any observed block. If macOS automation, the terminal, authentication, or sandbox permissions prevent startup, report the exact error. Give the single manual foreground command from the README. Do not claim unattended execution from an unverified child process.

An unexpired interrupted controller window should use `--resume` so its deadline does not reset. A new eight-hour window requires a new owner start instruction. Do not keep extending a deadline on your own.

## Commands from the repository root

Use the selected existing Python interpreter in place of `python3` when needed.

```bash
# Local tests; no model calls.
python3 -m unittest discover -s tools/continuous-research -p 'test_*.py' -v

# Inspect status without starting model work.
python3 tools/continuous-research/start_in_terminal.py --repo . --status

# Start one new authorised eight-hour window in a separate Mac Terminal.
python3 tools/continuous-research/start_in_terminal.py --repo . --hours 8

# Resume an interrupted, unexpired window without extending the deadline.
python3 tools/continuous-research/start_in_terminal.py --repo . --resume
```

The controller stores private logs and process metadata below the Git common directory, under `cicada-keep-working/`. Its status output gives the exact path. A first-turn `thread.started` event confirms a Codex session started, not that research succeeded. Check actual tool activity or a substantive disk checkpoint separately.

## Stop

The owner can press Ctrl+C in the controller's Terminal or create:

```bash
touch exploration/persistent-01/STOP
```

The controller honours the deadline, stop request, and bounded execution-error safeguards. The research agent must not remove the STOP file, alter controller metadata, spawn another controller, or change launcher code during supervised research.

## Why this arrangement

The research contract defines the work. The external controller starts the next turn after Codex ends the current turn. Old report-completion instructions do not control this new research mission. An empty queue requires new justified experiments, not a completion report.

Permission, quota, service, and machine availability limits still apply. Eight hours is a wall-time limit, not a spending limit. Normal configured Codex usage applies. No process has been started merely by adding these files to GitHub.

**Setup completion means a verified external handoff, not completion of the research mission.**
