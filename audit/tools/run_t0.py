"""Capture the four unchanged T0 checks, sequentially, with bounded raw logs.

Run from the repository root with .venv/bin/python audit/tools/run_t0.py.
No research modules are imported by this wrapper. Each invocation creates a new run.
"""
import datetime
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT)
RUN = ROOT / 'audit/runs/T0' / datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
RUN.mkdir(parents=True, exist_ok=False)
ENV = os.environ.copy()
OVERRIDES = {
    'PYTHONUTF8': '1', 'PYTHONUNBUFFERED': '1', 'PYTHONDONTWRITEBYTECODE': '1',
    'PYTHONNOUSERSITE': '1', 'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1',
    'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1',
    'VECLIB_MAXIMUM_THREADS': '1', 'NUMEXPR_NUM_THREADS': '1',
    'PYTEST_ADDOPTS': '-p no:cacheprovider',
}
ENV.update(OVERRIDES)
for k in ('PYTHONPATH', 'PYTHONHOME', 'PYTEST_PLUGINS'):
    ENV.pop(k, None)
ENV['PATH'] = str(ROOT / '.venv/bin') + os.pathsep + ENV.get('PATH', '')

def save(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')

def git(*args):
    return subprocess.check_output(['git', *args], text=True, timeout=30).strip()

def fingerprint(path):
    p = ROOT / path
    if not p.is_file():
        return {'path': path, 'exists': False}
    return {'path': path, 'exists': True, 'bytes': p.stat().st_size,
            'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}

inputs = ['liber-primus/data/english_quadgrams.txt',
          'liber-primus/data/scream314_lp.md', 'liber-primus/data/keys/self_reliance.txt',
          'liber-primus/data/krisyotam_runes.txt', 'liber-primus/LEDGER.json',
          'liber-primus/PROBLEM.json']
source_paths = [str(p.relative_to(ROOT)) for p in (ROOT / 'liber-primus/src/lp').glob('*.py')]
source_paths += ['AGENTS.md', 'CLAUDE.md', 'MACOS-SETUP.md', '.gitignore',
    'liber-primus/pyproject.toml', 'liber-primus/tests/validate.py',
    'liber-primus/verify_solution.py', 'liber-primus/analysis/handoff/validate_ledger.py',
    'liber-primus/analysis/run_stats.py', 'liber-primus/analysis/round11/lib_numchannel.py',
    'liber-primus/analysis/campaign18_skip/skipdecode.py',
    'liber-primus/analysis/round12/C1/feedback.py', 'audit/reference/AUDIT-PLAN.md',
    'audit/tools/run_t0.py']
source_paths += [str(p.relative_to(ROOT)) for p in (ROOT / 'liber-primus/benchmark').glob('*.py')]
tracked = git('ls-files', '-z').split('\0')
before_tracked = [fingerprint(p) for p in tracked if p]
save(RUN / 'tracked-before.json', before_tracked)
save(RUN / 'inputs.json', [fingerprint(p) for p in inputs])
save(RUN / 'sources.json', [fingerprint(p) for p in sorted(set(source_paths))])
revision = git('rev-parse', 'HEAD')
initial_status = git('status', '--short', '--untracked-files=all')
(RUN / 'git-status-before.txt').write_text(initial_status + '\n')
(RUN / 'git-diff-before.patch').write_text(git('diff', '--binary') + '\n')
environment = {
    'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'code_baseline': '396001a9ce55e0e85ddef19e405afc6a13954588',
    'working_commit': revision, 'cwd': str(ROOT), 'python_executable': sys.executable,
    'python_version': sys.version, 'python_prefix': sys.prefix,
    'python_base_prefix': sys.base_prefix, 'platform': platform.platform(),
    'mac_version': platform.mac_ver(), 'architecture': platform.machine(),
    'packages': sorted([{'name': d.metadata['Name'], 'version': d.version}
                        for d in importlib.metadata.distributions()], key=lambda d: d['name'].lower()),
    'environment_overrides': OVERRIDES,
    'removed_environment_keys': ['PYTHONPATH', 'PYTHONHOME', 'PYTEST_PLUGINS'],
    'limits': {'wall_seconds_per_command': 300, 'concurrent_commands': 1,
               'worker_processes_per_command': 1, 'numeric_library_threads': 1,
               'note': 'Inspected T0 paths are serial stdlib Python; no CPU affinity or memory limit imposed.'},
    'plan_source': 'https://raw.githubusercontent.com/wazar/cicada3301/master/AUDIT-PLAN.md',
    'plan_snapshot': fingerprint('audit/reference/AUDIT-PLAN.md'),
    'setup_note': 'Existing isolated .venv reused after MACOS-SETUP.md handoff; no packages installed by T0.',
    'run_directory': str(RUN.relative_to(ROOT)),
}
save(RUN / 'environment.json', environment)
save(ROOT / 'audit/environment.json', environment)
commands = [
    ('01-validate', ['python3', 'liber-primus/tests/validate.py']),
    ('02-oracle-selftest', ['python3', 'liber-primus/verify_solution.py', '--selftest']),
    ('03-collect', ['python3', '-m', 'pytest', 'liber-primus/benchmark/', '--collect-only', '-q']),
    ('04-benchmark', ['python3', '-m', 'pytest', 'liber-primus/benchmark/', '-q']),
    ('05-ledger-strict', ['python3', 'liber-primus/analysis/handoff/validate_ledger.py', '--strict']),
]
results = []
for name, cmd in commands:
    start = time.monotonic()
    record = {'id': name, 'command': cmd, 'cwd': str(ROOT), 'source_commit': revision,
              'started_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'timeout_seconds': 300, 'timed_out': False,
              'environment': 'environment.json', 'input_manifest': 'inputs.json',
              'source_manifest': 'sources.json', 'local_changes': 'git-status-before.txt',
              'stdout': name + '.stdout.txt', 'stderr': name + '.stderr.txt',
              'seeds': 'Inherited unchanged; see inspection.md in audit/ and hashed sources.'}
    save(RUN / (name + '.json'), record)
    print('START', name, flush=True)
    with (RUN / record['stdout']).open('wb') as out, (RUN / record['stderr']).open('wb') as err:
        try:
            p = subprocess.Popen(cmd, cwd=ROOT, env=ENV, stdout=out, stderr=err, start_new_session=True)
            try:
                code = p.wait(timeout=300)
            except subprocess.TimeoutExpired:
                record['timed_out'] = True
                os.killpg(p.pid, signal.SIGKILL)
                code = p.wait()
            record['exit_code'] = code
            record['outcome'] = 'TIMEOUT' if record['timed_out'] else ('PASS' if code == 0 else 'NONZERO_REQUIRES_REVIEW')
        except OSError as exc:
            record.update(exit_code=None, outcome='ERROR', launch_error=str(exc))
    record['duration_seconds'] = round(time.monotonic() - start, 3)
    record['finished_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save(RUN / (name + '.json'), record)
    results.append(record)
    save(RUN / 'manifest.json', results)
    print('END', name, record['outcome'], record['exit_code'], record['duration_seconds'], flush=True)

after_tracked = [fingerprint(p) for p in tracked if p]
save(RUN / 'tracked-after.json', after_tracked)
changes = [{'before': a, 'after': b} for a, b in zip(before_tracked, after_tracked) if a != b]
save(RUN / 'tracked-content-changes.json', changes)
save(RUN / 'inputs-after.json', [fingerprint(p) for p in inputs])
(RUN / 'git-status-after.txt').write_text(git('status', '--short', '--untracked-files=all') + '\n')
print('RUN', RUN.relative_to(ROOT), 'TRACKED CONTENT CHANGES', len(changes), flush=True)
