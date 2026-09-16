#!/usr/bin/env python3
"""Start the controller in a separate macOS Terminal window, or inspect its status.

Python 3.10+, standard library only. No model calls from this setup process.
The separate Terminal owns the controller after the setup agent's turn ends.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import math
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import time
import uuid

HERE = Path(__file__).resolve().parent


def locations(path: Path) -> tuple[Path, Path]:
    def git(*args: str) -> str:
        return subprocess.run(['git', '-C', str(path), *args], check=True,
                              capture_output=True, text=True, timeout=20).stdout.strip()
    repo = Path(git('rev-parse', '--show-toplevel')).resolve()
    common = Path(git('rev-parse', '--git-common-dir'))
    if not common.is_absolute():
        common = path / common
    return repo, common.resolve() / 'cicada-keep-working'


def lock_held(control: Path) -> bool:
    control.mkdir(parents=True, exist_ok=True)
    with (control / 'controller.lock').open('a+') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        fcntl.flock(lock, fcntl.LOCK_UN)
        return False


def status(control: Path) -> dict:
    state_file = control / 'controller.json'
    state = json.loads(state_file.read_text()) if state_file.is_file() else {}
    alive = False
    pid = state.get('controller_pid')
    if isinstance(pid, int) and pid > 0:
        try:
            os.kill(pid, 0)
            alive = True
        except ProcessLookupError:
            pass
        except PermissionError:
            alive = True  # Exists; not a reason to change permissions.
    return {'lock_held': lock_held(control), 'pid_exists': alive,
            'state_path': str(state_file), 'state': state}


def shell_text(repo: Path, python: str, codex: str, hours: float,
               resume: bool, path_value: str, caffeinate: str | None) -> str:
    command = [python, str(HERE / 'keep_codex_working.py'), '--repo', str(repo),
               '--codex-bin', codex, '--hours', str(hours)]
    if resume:
        command.append('--resume')
    if caffeinate:
        command = [caffeinate, '-i', *command]
    return ('#!/bin/sh\nset -eu\n' + 'export PATH=' + shlex.quote(path_value) + '\n'
            + 'cd ' + shlex.quote(str(repo)) + '\nexec ' + shlex.join(command) + '\n')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    parser.add_argument('--hours', type=float, default=8.0)
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--status', action='store_true')
    args = parser.parse_args()
    if not math.isfinite(args.hours) or args.hours <= 0:
        parser.error('Hours must be finite and greater than zero.')
    repo, control = locations(args.repo.expanduser().resolve())
    current = status(control)
    if args.status:
        print(json.dumps(current, indent=2))
        return 0
    if current['lock_held']:
        print('An existing controller holds the lock. Not starting another.')
        print(json.dumps(current, indent=2))
        return 0
    if sys.platform != 'darwin':
        parser.error('Automatic Terminal launch requires macOS. Use keep_codex_working.py in a persistent terminal.')
    if (repo / 'exploration/persistent-01/STOP').exists():
        parser.error('Owner STOP file exists. It will not be removed automatically.')
    codex = shutil.which('codex')
    if not codex:
        parser.error('Codex CLI is missing from PATH. Do not install or change authentication automatically.')
    if args.resume:
        state = current['state']
        if not state or state.get('deadline_epoch', 0) <= time.time():
            parser.error('No unexpired controller window to resume.')
        if state.get('repo') != str(repo):
            parser.error('Existing controller record belongs to a different checkout.')
    script = control / ('start-' + uuid.uuid4().hex + '.command')
    caffeinate = '/usr/bin/caffeinate' if Path('/usr/bin/caffeinate').is_file() else None
    script.write_text(shell_text(repo, sys.executable, codex, args.hours, args.resume,
                                 os.environ.get('PATH', ''), caffeinate), encoding='utf-8')
    script.chmod(0o700)
    before_pid = current['state'].get('controller_pid')
    subprocess.run(['/usr/bin/open', '-a', 'Terminal', str(script)], check=True, timeout=20)
    # A successful 'open' alone is not proof that the controller started.
    until = time.monotonic() + 30
    while time.monotonic() < until:
        now = status(control)
        if (now['lock_held'] and now['pid_exists']
                and now['state'].get('controller_pid') != before_pid
                and now['state'].get('status') == 'active'):
            print('Controller startup observed in a separate Terminal.')
            print(json.dumps(now, indent=2))
            print('Now inspect the first turn log. Active controller status alone is not proof of research progress.')
            return 0
        time.sleep(1)
    print('Terminal open was requested, but controller startup was not confirmed.', file=sys.stderr)
    print('Inspect that window and the status before attempting another launch.', file=sys.stderr)
    print(json.dumps(status(control), indent=2))
    return 2


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, subprocess.SubprocessError, ValueError, KeyError) as error:
        print(f'Startup error: {error}', file=sys.stderr)
        raise SystemExit(2)
