"""Tests of the setup helper. Does not open Terminal or call a real model."""
import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('starter', HERE / 'start_in_terminal.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class StartTests(unittest.TestCase):
    def test_shell_quoting(self):
        repo = Path("/tmp/a b/'quote';echo bad")
        text = m.shell_text(repo, '/a b/python', '/c d/codex', 8, False,
                            "/bin:/x y/'z", '/usr/bin/caffeinate')
        lines = text.splitlines()
        self.assertEqual(shlex.split(lines[3]), ['cd', str(repo)])
        self.assertEqual(shlex.split(lines[4]), ['exec', '/usr/bin/caffeinate', '-i',
            '/a b/python', str(HERE/'keep_codex_working.py'), '--repo', str(repo),
            '--codex-bin', '/c d/codex', '--hours', '8'])

    def test_resume_flag(self):
        text = m.shell_text(Path('/tmp/repo'), 'python3', 'codex', 8, True, '/bin', None)
        self.assertEqual(shlex.split(text.splitlines()[-1])[-1], '--resume')

    def test_repo_location_and_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(['git', 'init', '-q', str(repo)], check=True)
            root, control = m.locations(repo)
            self.assertEqual(root, repo.resolve())
            self.assertEqual(control, repo.resolve()/'.git/cicada-keep-working')
            state = m.status(control)
            self.assertFalse(state['lock_held'])
            self.assertFalse(state['pid_exists'])
            (control/'controller.json').write_text(json.dumps({'controller_pid': os.getpid()}))
            self.assertTrue(m.status(control)['pid_exists'])

    def test_lock_detection(self):
        import fcntl
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            with (folder/'controller.lock').open('w') as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.assertTrue(m.lock_held(folder))
            self.assertFalse(m.lock_held(folder))


if __name__ == '__main__':
    unittest.main(verbosity=2)
