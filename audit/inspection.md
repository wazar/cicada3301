# T0 pre-execution inspection

Scope: the four baseline commands and benchmark collection only. Inspection began
before the user interruption and resumed after the macOS setup handoff. No baseline
research commands were launched before that interruption.

## Instructions, environment and collection

- Read `AGENTS.md`, `CLAUDE.md`, the linked audit plan, `MACOS-SETUP.md`,
  `liber-primus/pyproject.toml`, and `scripts/activate-macos.sh`.
- The root `AUDIT-PLAN.md` was absent locally. Retrieved the user-linked raw file
  with `curl --max-time 60 -fsSL` into `audit/reference/AUDIT-PLAN.md` before execution.
  Its SHA-256 is in the environment record. This is a source snapshot, not a Git
  update. Earlier read-only retrievals used `curl -fsSL` to display the plan.
- Inspected `.venv/pyvenv.cfg`: isolated Python 3.12.14, system site packages disabled.
  The editable-install `.pth` contains only the local `liber-primus/src` path.
  Used `.venv/bin/python` directly; did not source the broader activation helper.
- Searched for pytest configuration and conftest files. The relevant project config
  is `liber-primus/pyproject.toml`; no project conftest was found. Read
  `benchmark/test_gates.py` and its imports before collection. Third-party plugin
  autoload is disabled, no xdist workers are requested, and pytest cache writes
  and bytecode writes are disabled. No tests are deselected by these settings.
- No packages installed, binaries executed, private accounts accessed, or input
  data fetched by T0. Only the small audit-plan source download used the network.
  Tests have no network calls on the inspected paths; no OS network sandbox was used.

## Import and input paths inspected

| Entry point | Local import path / reads | Side effects on the exercised path |
| --- | --- | --- |
| `tests/validate.py` | `lp.corpus`, `ciphers`, `solve`, `gematria`, `score`; `data/scream314_lp.md`, `data/english_quadgrams.txt` | Reads and stdout; selected keyword checks on five entries. |
| `verify_solution.py --selftest` | `lib_numchannel` → `run_stats` and `lp` modules; `skipdecode` → `gematria`, `score` | Quadgram read at import; deterministic synthetic data and stdout. `--selftest` returns before the real ciphertext hash check and `trust_anchor()` call. |
| `benchmark/test_gates.py` | `gates` → `plant`, `skipdecode`; `plant` → `feedback` → `lib_numchannel` → `run_stats`; `lp` modules | Reads quadgrams and `data/keys/self_reliance.txt`; builds a small prime table during feedback import. Seven gate functions plus one aggregate test. No skip markers. |
| `analysis/handoff/validate_ledger.py --strict` | stdlib `glob`, `json`, `os`, `sys`; `LEDGER.json`, filesystem path checks | Reads and stdout. Does not rerun experiments. Strict mode fails on recorded errors, not warnings. |

Read all six imported `lp` modules: corpus, ciphers, solve, gematria, score and stats.
Read `skipdecode.py`, `lib_numchannel.py`, `run_stats.py`, `feedback.py`, the benchmark
test and gate modules, and the plant implementation (including its rewrite mechanism).
Also reviewed `benchmark/null.py`; it is not imported by these benchmark tests.

`run_stats.py` has a report-writing main function, and `verify_solution.py` has a
subprocess trust anchor, candidate-module execution and optional JSON output. None
of those paths is reached by the assigned self-test/benchmark invocations. Module
imports adjust `sys.path`, instantiate the scorer, and reconfigure stdout encoding;
they do not launch campaigns. The wrapper does not import research modules.

## Unchanged deterministic controls

- Known-page validation uses the fixed keywords `DIVINITY`, `FIRFUMFERENFE` and a
  small fixed transform enumeration; no random seed.
- Oracle self-test: random keystream seed 3301, encipher seed 3301 reset per page,
  wrong-key seed 4242 recreated per symbol, shuffle seeds 3301 through 3360.
  Embedded `SELFTEST_PLAIN` and all parameters are preserved in the hashed source.
  The repeated construction of the wrong-key RNG is source-checked here, not repaired.
- Benchmark: plant/PRNG/shuffle seeds 3301; SHA-256 counter seed `CICADA3301`;
  running key `self_reliance.txt`; default embedded plaintext `primes`; deterministic
  wrong key `(i * 7 + 13) % 29`. Hashes of code capture the full parameters.
- Ledger validation and test collection do not use stochastic controls.

## Inspection-command caveats

Read-only inspection used `pwd`, `git status/rev-parse/diff`, `rg`, `ls`, `cat`,
`sed`, and `curl`; these were not research test runs. Two exploratory shell reads
returned exit 1: `ls audit` before that directory existed (so its following `&& cat`
did not execute), and `cat liber-primus/src/lp/__init__.py` because `lp` is a
namespace package without that file. The needed core files were subsequently read.
These are inspection-path errors, not baseline test failures or missing test inputs.

The baseline wrapper records raw stdout/stderr and actual exit codes independently
for all five child commands, including collection. It kills the process group at
300 seconds if necessary and records TIMEOUT separately; no timeout occurred.
