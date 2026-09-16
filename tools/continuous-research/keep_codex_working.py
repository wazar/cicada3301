#!/usr/bin/env python3
"""Run successive local Codex research turns until a fixed deadline or an explicit stop.

macOS/Linux; Python 3.10+; standard library only. Does not bypass Codex permissions.
Raw Codex logs stay in Git's private metadata directory and are not staged or pushed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
from typing import Any

STOP_REQUESTED = False


def utc(timestamp: float | None = None) -> str:
    return datetime.fromtimestamp(time.time() if timestamp is None else timestamp,
                                  timezone.utc).isoformat()


def save_json(path: Path, value: Any) -> None:
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True,
                            text=True, timeout=20, check=True)
    return result.stdout.strip()


def checkpoint_digest(repo: Path) -> str:
    """A continuity check, NOT a measure of scientific progress."""
    digest = hashlib.sha256()
    for name in ('STATE.md', 'QUEUE.json', 'experiments.jsonl'):
        path = repo / 'exploration/persistent-01' / name
        digest.update(name.encode())
        if path.is_file():
            digest.update(path.read_bytes())
    return digest.hexdigest()


def inspect_events(path: Path) -> tuple[bool, bool]:
    completed, failed = False, False
    with path.open(encoding='utf-8', errors='replace') as source:
        for line in source:
            try:
                event = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                continue
            if not isinstance(event, dict):
                continue
            if event.get('type') == 'turn.completed':
                completed = True
            if event.get('type') == 'turn.failed':
                failed = True
    return completed, failed


def stop_group(process: subprocess.Popen[Any], grace: float = 15.0) -> None:
    """Interrupt this launch's process group, then escalate. No global process kill."""
    for sig, seconds in ((signal.SIGINT, grace), (signal.SIGTERM, 3.0),
                         (signal.SIGKILL, 1.0)):
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            return
        try:
            process.wait(timeout=seconds)
        except subprocess.TimeoutExpired:
            continue
        # A group child can survive after the parent exits. Signal that group too.
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        time.sleep(0.2)
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        return


def request_stop(_signum: int, _frame: Any) -> None:
    global STOP_REQUESTED
    STOP_REQUESTED = True


def run_turn(command: list[str], prompt: str, repo: Path, directory: Path,
             deadline: float, cycle_seconds: float, stop_file: Path) -> dict[str, Any]:
    started = time.time()
    limit = min(deadline, started + cycle_seconds)
    (directory / 'prompt.md').write_text(prompt, encoding='utf-8')
    record: dict[str, Any] = {'command': command, 'started_at': utc(started),
                              'deadline_utc': utc(deadline)}
    save_json(directory / 'run.json', record)
    reason = 'exited'
    process = None
    try:
        with (directory / 'prompt.md').open('rb') as stdin, \
             (directory / 'events.jsonl').open('wb') as stdout, \
             (directory / 'stderr.log').open('wb') as stderr:
            process = subprocess.Popen(command, cwd=repo, stdin=stdin, stdout=stdout,
                                       stderr=stderr, start_new_session=True)
            record['pid'] = process.pid
            save_json(directory / 'run.json', record)
            while process.poll() is None:
                if STOP_REQUESTED or stop_file.exists():
                    reason = 'owner_stop'
                    break
                if time.time() >= limit:
                    reason = 'deadline' if limit == deadline else 'cycle_timeout'
                    break
                time.sleep(0.5)
            if reason != 'exited':
                stop_group(process)
            record['exit_code'] = process.wait()
    except Exception:
        if process is not None and process.poll() is None:
            stop_group(process)
        raise
    finally:
        record.update(reason=reason, finished_at=utc(), elapsed_seconds=time.time()-started)
        save_json(directory / 'run.json', record)
    return record


def make_prompt(mission: str, state: dict[str, Any], limit_seconds: float,
                missing_checkpoint: int) -> str:
    warning = ''
    if missing_checkpoint:
        warning = (f'\nThe previous {missing_checkpoint} turn(s) did not update the required '
                   'research checkpoint. Execute a concrete experiment and record its outcome. '
                   'Do not merely restate a plan or write a completion message.\n')
    return f'''# Supervisor instruction — turn {state['next_turn']}

SUPERVISED MODE. The overall mission is still ACTIVE.
Original start: {state['started_at']}
Fixed overall deadline: {state['deadline_utc']}
Current UTC time: {utc()}
Maximum time for this turn: {limit_seconds:.0f} seconds.

Execute a useful batch now. Native workers must finish or be safely stopped before
this turn returns. Do not leave detached processes. Save STATE.md, QUEUE.json,
and experiments.jsonl under exploration/persistent-01, then return a checkpoint.
The external controller will start another turn. Finishing your queue or returning
this checkpoint does not end the mission. There is no need to ask the owner to continue.

Read current disk state, including the previous substantive result. Do not replay
completed OVERNIGHT-01 searches. If the ready queue is empty, generate and implement
the next justified experiment. Leave concrete follow-on work in the checkpoint.

Do not edit controller files under Git metadata, set the STOP file, extend the
deadline, bypass permissions, or start another Codex coordinator. Leave only owned,
tracked-in-state worker processes. The owner's STOP file is exploration/persistent-01/STOP.
{warning}
--- RESEARCH CONTRACT ---
{mission}
'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, type=Path)
    parser.add_argument('--hours', type=float, default=8.0)
    parser.add_argument('--cycle-minutes', type=float, default=40.0,
                        help='Maximum for one Codex turn, not a target runtime (default 40).')
    parser.add_argument('--prompt', type=Path,
                        default=Path(__file__).resolve().parents[2] / 'CICADA-CONTINUOUS-RESEARCH.md')
    parser.add_argument('--codex-bin', default='codex')
    parser.add_argument('--model', help='Optional; otherwise keep the configured model.')
    parser.add_argument('--resume', action='store_true',
                        help='Reuse the last controller deadline instead of starting a new window.')
    args = parser.parse_args()
    if any(not math.isfinite(v) or v <= 0 for v in (args.hours, args.cycle_minutes)):
        parser.error('Hours and cycle minutes must be finite and greater than zero.')
    if not args.prompt.is_file():
        parser.error(f'Missing research prompt: {args.prompt}')
    executable = shutil.which(args.codex_bin)
    if not executable:
        parser.error('Codex CLI not found. Use an existing authenticated CLI; do not paste API keys.')
    repo = args.repo.expanduser().resolve()
    repo = Path(git(repo, 'rev-parse', '--show-toplevel')).resolve()
    metadata = Path(git(repo, 'rev-parse', '--git-common-dir'))
    if not metadata.is_absolute():
        metadata = repo / metadata
    control = metadata.resolve() / 'cicada-keep-working'
    control.mkdir(parents=True, exist_ok=True)
    lock = (control / 'controller.lock').open('a+')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print('A controller is already running for this repository.', file=sys.stderr)
        return 2
    mission = args.prompt.read_text(encoding='utf-8')
    checkpoint = repo / 'exploration/persistent-01'
    checkpoint.mkdir(parents=True, exist_ok=True)
    stop_file = checkpoint / 'STOP'
    if stop_file.exists():
        print(f'STOP file exists. Remove it yourself to authorise a new run: {stop_file}')
        return 0
    state_path = control / 'controller.json'
    if args.resume:
        if not state_path.is_file():
            parser.error('No controller record exists to resume.')
        state = json.loads(state_path.read_text(encoding='utf-8'))
        if state['repo'] != str(repo):
            parser.error('Saved controller is for a different working directory.')
        if time.time() >= state['deadline_epoch']:
            print('The saved deadline has passed. A new run requires a new explicit launch.')
            return 0
    else:
        now = time.time()
        state = {'repo': str(repo), 'started_at': utc(now),
                 'deadline_epoch': now + args.hours*3600,
                 'deadline_utc': utc(now + args.hours*3600), 'next_turn': 1,
                 'run_id': datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')}
    state['status'] = 'active'
    state['controller_pid'] = os.getpid()
    save_json(state_path, state)
    logs = control / state['run_id']
    logs.mkdir(exist_ok=True)
    mission_file = logs / ('mission-' + hashlib.sha256(mission.encode()).hexdigest()[:16] + '.md')
    if not mission_file.exists():
        mission_file.write_text(mission, encoding='utf-8')
    version = subprocess.run([executable, '--version'], capture_output=True,
                             text=True, timeout=20)
    (logs / 'codex-version.txt').write_text(version.stdout + version.stderr, encoding='utf-8')
    print(f'Work deadline: {state["deadline_utc"]}', flush=True)
    print(f'Private logs: {logs}', flush=True)
    print(f'Stop with Ctrl+C or create: {stop_file}', flush=True)
    print('Do not run another coordinator on this checkout. Normal account usage applies.', flush=True)
    failures = unchanged = 0
    exit_code = 0
    while time.time() < state['deadline_epoch']:
        if STOP_REQUESTED or stop_file.exists():
            state['status'] = 'owner_stop'
            break
        number = state['next_turn']
        state['next_turn'] += 1
        save_json(state_path, state)
        directory = logs / f'turn-{number:04d}'
        directory.mkdir(exist_ok=False)
        seconds = min(args.cycle_minutes*60, state['deadline_epoch']-time.time())
        if seconds < 2:
            break
        before = checkpoint_digest(repo)
        prompt = make_prompt(mission, dict(state, next_turn=number), seconds, unchanged)
        command = [executable, '--ask-for-approval', 'never', 'exec',
                   '--sandbox', 'workspace-write', '--json',
                   '--output-last-message', str(directory / 'last-message.txt')]
        if args.model:
            command += ['--model', args.model]
        command += ['-']
        print(f'Launching research turn {number}.', flush=True)
        record = run_turn(command, prompt, repo, directory,
                          state['deadline_epoch'], seconds, stop_file)
        if record['reason'] in ('owner_stop', 'deadline'):
            state['status'] = record['reason']
            break
        completed, event_failed = inspect_events(directory / 'events.jsonl')
        good = record['exit_code'] == 0 and completed and not event_failed
        after = checkpoint_digest(repo)
        checkpointed_timeout = record['reason'] == 'cycle_timeout' and after != before
        if good or checkpointed_timeout:
            failures = 0
            unchanged = unchanged + 1 if after == before else 0
            label = 'reached its turn limit with a checkpoint' if checkpointed_timeout else 'ended'
            print(f'Turn {number} {label}. Mission still active; continuing from disk state.', flush=True)
            if unchanged >= 5:
                state['status'] = 'blocked_no_checkpoint'
                print('Five turns produced no required checkpoint. Pausing to prevent an empty usage loop.',
                      file=sys.stderr)
                exit_code = 2
                break
        else:
            failures += 1
            print(f'Turn {number} failed or timed out; see {directory}.', file=sys.stderr)
            if failures >= 3:
                state['status'] = 'blocked_cli_errors'
                print('Three consecutive execution failures. No permission or quota bypass attempted.',
                      file=sys.stderr)
                exit_code = 2
                break
            # Bounded backoff for a real execution error, not fake research activity.
            retry_at = min(time.time()+15*(2**(failures-1)), state['deadline_epoch'])
            while time.time() < retry_at and not STOP_REQUESTED and not stop_file.exists():
                time.sleep(0.5)
        save_json(state_path, state)
    if state['status'] == 'active':
        state['status'] = 'deadline'
    state['finished_at'] = utc()
    save_json(state_path, state)
    print(f'Controller stopped: {state["status"]}. State: {state_path}', flush=True)
    return exit_code


if __name__ == '__main__':
    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    try:
        raise SystemExit(main())
    except (OSError, subprocess.SubprocessError, ValueError, KeyError) as error:
        print(f'Controller error: {error}', file=sys.stderr)
        raise SystemExit(2)
