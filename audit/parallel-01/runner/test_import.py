"""Importing the repaired wrapper must not execute checks or create output files."""
import pathlib, runpy, unittest.mock
with unittest.mock.patch('subprocess.Popen',side_effect=AssertionError('unexpected subprocess')), unittest.mock.patch('os.chdir',side_effect=AssertionError('unexpected chdir')), unittest.mock.patch.object(pathlib.Path,'mkdir',side_effect=AssertionError('unexpected mkdir')):
 namespace=runpy.run_path('audit/tools/run_t0.py',run_name='audit_import_test')
 assert callable(namespace['main'])
print('PASS: import creates no run, changes no cwd, launches no subprocess')
