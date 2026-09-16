"""Local tests with a fake Codex executable. No network or real model calls."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import time

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('controller', HERE / 'keep_codex_working.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

FAKE = '''#!/usr/bin/env python3
import json, os, pathlib, sys, time
if '--version' in sys.argv:
    print('fake-codex for local tests'); raise SystemExit(0)
prompt = sys.stdin.read()
root = pathlib.Path.cwd()
assert '--sandbox' in sys.argv and sys.argv[sys.argv.index('--sandbox')+1] == 'workspace-write'
assert '--ask-for-approval' in sys.argv and 'never' in sys.argv
assert 'SUPERVISED MODE' in prompt
control = root/'fake-call-count.txt'
n = int(control.read_text())+1 if control.exists() else 1
control.write_text(str(n))
if not os.environ.get('FAKE_NO_CHECKPOINT'):
    folder = root/'exploration/persistent-01'
    folder.mkdir(parents=True,exist_ok=True)
    (folder/'STATE.md').write_text('new measured batch '+str(n))
if os.environ.get('FAKE_STOP_AFTER_TWO') and n >= 2:
    (root/'exploration/persistent-01/STOP').touch()
print(json.dumps({'type':'thread.started','thread_id':'fake-'+str(n)}),flush=True)
print(json.dumps({'type':'turn.completed','usage':{'input_tokens':1,'output_tokens':1}}),flush=True)
if '--output-last-message' in sys.argv:
    pathlib.Path(sys.argv[sys.argv.index('--output-last-message')+1]).write_text('CHECKPOINT - CONTINUE')
'''


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        subprocess.run(['git','init','-q',str(self.root)],check=True)
        self.fake = self.root/'fake-codex'
        self.fake.write_text(FAKE)
        self.fake.chmod(0o755)
        module.STOP_REQUESTED = False

    def tearDown(self):
        self.temp.cleanup()

    def command(self, *extra):
        return [sys.executable, str(HERE/'keep_codex_working.py'),
                '--repo',str(self.root),'--codex-bin',str(self.fake),*extra]

    def state(self):
        return json.loads((self.root/'.git/cicada-keep-working/controller.json').read_text())

    def test_multiple_turns_until_deadline(self):
        result = subprocess.run(self.command('--hours','.002'),capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertGreaterEqual(int((self.root/'fake-call-count.txt').read_text()),2)
        state = self.state()
        self.assertEqual(state['status'],'deadline')
        deadline = state['deadline_epoch']
        resumed = subprocess.run(self.command('--resume'),capture_output=True,text=True,timeout=5)
        self.assertEqual(resumed.returncode,0)
        self.assertEqual(self.state()['deadline_epoch'],deadline)

    def test_five_no_checkpoint_turns_pause(self):
        env=dict(os.environ,FAKE_NO_CHECKPOINT='1')
        result=subprocess.run(self.command('--hours','.01'),env=env,capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,2,result.stderr)
        self.assertEqual(int((self.root/'fake-call-count.txt').read_text()),5)
        self.assertEqual(self.state()['status'],'blocked_no_checkpoint')

    def test_stop_file(self):
        env=dict(os.environ,FAKE_STOP_AFTER_TWO='1')
        result=subprocess.run(self.command('--hours','.01'),env=env,capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(int((self.root/'fake-call-count.txt').read_text()),2)
        self.assertEqual(self.state()['status'],'owner_stop')

    def test_exclusive_lock(self):
        folder=self.root/'.git/cicada-keep-working'
        folder.mkdir(parents=True)
        import fcntl
        with (folder/'controller.lock').open('w') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            result=subprocess.run(self.command(),capture_output=True,text=True,timeout=5)
            self.assertEqual(result.returncode,2)
            self.assertIn('already running',result.stderr)

    def test_child_nonzero_is_preserved(self):
        directory=self.root/'run'; directory.mkdir()
        record=module.run_turn([sys.executable,'-c','raise SystemExit(7)'],
            'test',self.root,directory,time.time()+10,5,self.root/'STOP')
        self.assertEqual(record['exit_code'],7)
        self.assertEqual(record['reason'],'exited')
        self.assertEqual(module.inspect_events(directory/'events.jsonl'),(False,False))

    def test_child_timeout_is_recorded(self):
        directory=self.root/'run'; directory.mkdir()
        record=module.run_turn([sys.executable,'-c','import time; time.sleep(30)'],
            'test',self.root,directory,time.time()+10,.15,self.root/'STOP')
        self.assertEqual(record['reason'],'cycle_timeout')
        self.assertNotEqual(record['exit_code'],0)

    def test_event_failure_is_not_success(self):
        path=self.root/'events'
        path.write_text('{"type":"turn.completed"}\n{"type":"turn.failed"}\n')
        self.assertEqual(module.inspect_events(path),(True,True))

    def test_bad_budget(self):
        result=subprocess.run(self.command('--hours','nan'),capture_output=True,text=True,timeout=5)
        self.assertEqual(result.returncode,2)
        self.assertIn('finite',result.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
