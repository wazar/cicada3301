# Parallel verification assignment

Working input commit: `95e11e918ace77a51de4b612a48e74c298e67e58`.
Inherited research baseline: `396001a9ce55e0e85ddef19e405afc6a13954588`.
Runtime agent identifiers below are the canonical IDs returned by native spawn.

| Agent | Exclusive output directory | Scope | Dependencies |
|---|---|---|---|
| `/root/inputs` (A) | `inputs/` | C-001–007, independently parse and inspect images | Local raw transcription/images; separate alphabet source |
| `/root/reference` (B) | `reference/` | C-008–009, complete known solutions | Original page IDs initially; A map for final joins |
| `/root/detectors` (C) | `detectors/` | C-010–019, fresh synthetic detector tests | Coordinator blinded challenge; independent of A |

A, B and C launched concurrently. This runtime has four total slots including
coordinator, so D and the fresh reviewer are launched as slots free, rather than
claiming four simultaneous sub-agents. No nested agent trees. Only coordinator
writes shared register/status files or uses Git mutations.

Limits: existing `.venv` Python 3.12.14; routine command wall limit 300 seconds;
numeric libraries one thread; at most two heavy jobs. C has heavy slot 1 and B
slot 2 initially; A's parsing/image reads are lightweight. No limit increases yet.
No research searches, inherited code/data/threshold/ledger changes, system installs,
large archive downloads, or T0 reruns. Only existing executable repair permitted:
`audit/tools/run_t0.py`. Separate worker `assigned-claims.json` files pin exactly
the relevant T1 rows and source excerpts. Workers read their relevant assignment
sections, not the full research archive.

Entry local changes preserved and excluded from publication: `.gitignore`,
`Brewfile`, `MACOS-SETUP.md`, `homebrew-macos-versions.txt`,
`macos-data-checks.json`, `requirements-macos-resolved.txt`, `scripts/`.
Existing images and reference texts checked through worker source inventories;
no assumption that an existing file is an independent witness.

A published frozen v1 `dataset.json` and `page-map.json` before completing visual
checks. B was notified immediately. Map status at publication is explicitly
provisional; later visual evidence supplements rather than silently replaces it.

After A completed and stopped writing, `/root/statistics` (D) launched with exclusive
`statistics/`, C-020–027, an independent raw parser and frozen A v1 for comparison.
D received heavy slot2; no heavy job overlap beyond the two-job limit occurred.
After B completed, fresh `/root/review` launched with exclusive `review/`, no prior
worker transcript, and instructions to inspect code/raw evidence and independently
rerun selected checks. Reviewer began A/B/runner checks while D worked. The reviewer
will inspect D outputs once available. C's main job finished in about10seconds;
no routine command ceiling was raised.

Actual bounded blinded-search handoff: C received only challenge and commitment;
its saved ranking SHA256 was checked before coordinator revealed the answer and
generator. Candidate6 ranked first and was the committed answer. See
`coordination/blind-protocol.md` for procedural separation limits.
