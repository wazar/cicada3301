# Audit status

**T0 reviewed by owner. T1 complete; stopped for owner review.**

All four assigned baseline commands exited 0. Benchmark: 8 collected, 8 passed,
0 skipped. Ledger: 0 errors, 18 warnings, 27 notes. No timeouts or missing execution
inputs. Missing ledger evidence remains recorded and unresolved.

Baseline/working commit: `396001a9ce55e0e85ddef19e405afc6a13954588`.
Run: `runs/T0/20260916T165851.125236Z/`.

See [T0 report](reports/T0.md), [baseline](BASELINE.md),
[environment](environment.json), and [inspection](inspection.md).

No research code, input data or inherited conclusions changed by T0. No campaign or repair was performed during T0. Existing setup changes remain.
The repository's scientific conclusions are still unaudited claims.

T1 adds 47 scoped claims, a dependency summary and individual accounting for all
18 ledger warnings. See [T1 report](reports/T1.md), [claim index](CLAIM-INDEX.md),
[dependencies](DEPENDENCIES.md), [warnings](LEDGER-WARNINGS.md) and
[findings](FINDINGS.md). No T0 rerun or research experiment was performed.

C-037 records the T0 runner's missing aggregate failure exit. Its runtime impact
measurement, regression test and fix are deferred to a later repair task. The
existing T0 child results all exited zero; no hidden failed child was observed.

No blocker to reviewing T1. Next decision: assign T2 input/page verification and/or
a separate runner repair task. Neither has begun. T1 working commit on entry:
`0e187df`; inherited scientific baseline remains the commit above.

## Publication authorization

After T0, the owner explicitly requested a GitHub push and asked that completed
work be pushed by default going forward. This authorizes publication of completed
work; T1 and later audit tasks still require assignment. T0 reports describe the
state at their original stop point. Private checkout prefixes in JSON metadata
were redacted before publication; raw command output and scientific evidence
were preserved.
