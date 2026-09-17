# Live worker C resume state (09:12 UTC)

Fixed deadline2026-09-17T16:15:06Z. Never extend or alter PERSISTENT-01STOP.

C01–C06 complete; do not repeat. Reports: feedback/REPORT.md plus C04/REPORT.md, C05/REPORT.md, C06/REPORT.md. C01 all42newpages exactk2–4 no candidate; C02 exactstructuredk5–8body/prefix no candidate; C03unchangedbodycontinuation no candidate; C04seed-invariantbodyk2..34ordinary; C05/C06literal-Funknownseed k2/3samebodyordinary undertwofrozenmodels. C05algorithm reviewed byB, C02review01, C04review02.

C07 is active, `page_invariant.py`. Frozeninputs25controls/45pages/411features. Controls0–14 complete; controls15–24currentloggedjob. Eachcontrol logs localperiodfamily and full45-unit syntheticcomposite. Controls are not universally sensitive: e.g Shelley66control10fullbookrank.995 and Shelley121k5control12rank.13. Reportallranks, not only successes. NoactualC07score yet. Review04independently clearedarithmetic and two representative syntheticbooks; finishfullcapabilitypanelbeforeactual.

Resumable control command (skips completedlocal/book files):
```sh
.venv/bin/python exploration/persistent-02/run_logged.py --owner exploration/persistent-02/feedback --label C07-controls-resume --seconds 900 --input exploration/persistent-02/feedback/C07/inputs.json -- /usr/bin/time -l .venv/bin/python exploration/persistent-02/feedback/page_invariant.py controls 15 16 17 18 19 20 21 22 23 24
```
Then write fullcontrol summary, confirmreview04clearance and run actual ONCE if absent:
```sh
.venv/bin/python exploration/persistent-02/run_logged.py --owner exploration/persistent-02/feedback --label C07-actual --seconds 900 --input exploration/persistent-02/feedback/C07/inputs.json -- /usr/bin/time -l .venv/bin/python exploration/persistent-02/feedback/page_invariant.py actual
```
Actual code currently overwrites rather than skips an existingactual file; inspectbeforeuse. It must not be rerun as newcoverage. Save controlqualifications and actualdecision, then select the next justified workstreamstep withroot. C07 independently initializedpagebaselines do not assertphysicalresets; effective initialseeds cover arbitrary contiguousslices (15newchecks in slice-identity.json). No newscorer or keyenumeration.

Root owns Git/shared state/publication. C01nullNPZsremainlocal; rootpublishes per-arraymanifest/reconstructor to avoidoversizedGitpacks, leavingoriginal localrawdataunchanged.
