# Audit runner failure propagation

C-037/F-001 reproduced and repaired. No real T0 command was rerun. The preserved
T0 child results were all successful; this defect does not change their results.

`test_runner.py` executes the real wrapper body in fresh temporary Git repositories.
An AST fixture substitutes only ROOT, the child command list, and 300-second values
with 0.2 seconds. The same substitutions apply before and after repair. Each case
runs a second successful child to check continuation and complete log retention.
The external parent limit is 30 seconds per case. All fixture repositories are
removed after raw child/parent logs and manifests are saved here.

| Child case | Original parent | Repaired parent | Preserved outcome |
|---|---:|---:|---|
| Success | 0 | 0 | PASS / 0 |
| Exit 1 | 0 | 1 | NONZERO_REQUIRES_REVIEW / 1 |
| Exit 2 | 0 | 1 | NONZERO_REQUIRES_REVIEW / 2 |
| SIGTERM | 0 | 1 | NONZERO_REQUIRES_REVIEW / -15 |
| Timeout, killed | 0 | 1 | TIMEOUT / -9 |
| Missing executable | 0 | 1 | ERROR / null |

The repair adds an import-safe `main()` guard and returns 1 if any required child
has an outcome other than PASS. It preserves the original per-child execution and
log semantics. Indentation accounts for most diff lines; `git diff -w` shows the
small functional change. Uncaught wrapper exceptions continue to fail normally.
A separate guarded import test confirms no subprocess, mkdir, or chdir happens.

Commands (all exited 0):

```
.venv/bin/python -B audit/parallel-01/runner/test_runner.py --source audit/tools/run_t0.py --label before
# minimal repair applied
.venv/bin/python -B audit/parallel-01/runner/test_runner.py --source audit/tools/run_t0.py --label after --expect-fixed
.venv/bin/python -B audit/parallel-01/runner/test_import.py
```

See `before/results.json`, `after/results.json`, their per-case manifests and raw
stdout/stderr, plus `import.stdout.txt` and `import.stderr.txt`. The before source
is recoverable exactly from T1 commit; its hash is recorded in results. Timeout
and launch error are deliberate test stimuli, not missing research inputs or
scientific rejections. No test skipped; no unexpected timeout or failure.
