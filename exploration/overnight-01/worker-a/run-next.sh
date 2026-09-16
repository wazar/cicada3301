#!/bin/zsh
set -e
run() {
 .venv/bin/python -B exploration/overnight-01/run_logged.py --owner exploration/overnight-01/worker-a --label "$1" --input exploration/overnight-01/config.json --input audit/parallel-01/inputs/dataset.json --input audit/parallel-01/inputs/page-map.json --input audit/experiment-01/keys.json --input liber-primus/data/english_quadgrams.txt --input audit/f-interruption-01/check.py --input audit/parallel-01/reference/sources/solved_0_warning.txt --input audit/parallel-01/reference/sources/solved_0_wisdom.txt --input audit/parallel-01/reference/sources/solved_0_welcome.txt --input audit/parallel-01/reference/sources/solved_0_loss_of_divinity.txt --input audit/parallel-01/reference/sources/solved_0_koan_1.txt --input audit/parallel-01/reference/sources/solved_jpg107-167.txt --input audit/parallel-01/reference/sources/solved_p56_an_end.txt --input audit/parallel-01/reference/sources/solved_p57_parable.txt --input liber-primus/analysis/campaign18_skip/skipdecode.py --input audit/experiment-01/control.py --seconds 900 -- .venv/bin/python -B "exploration/overnight-01/worker-a/$2" "${@:3}"
}
run wordview-update wordview_patch.py
run r01-controls search.py controls
run r01-p55-zero search.py r01zero --page55
run r01-p55-rigid search.py r01rigid --page55
run r01-p55-f search.py r01f --page55
run r02-ordinary clues.py ordinary
run r02-f clues.py literal_f
run r02-controls r02_controls.py
run r01-rejection rejection.py
