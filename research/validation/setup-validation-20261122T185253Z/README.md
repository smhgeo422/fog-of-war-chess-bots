# Local infrastructure validation

Two full Obscuro versus Greedy games exercised the existing referee and paused
process isolation. Colors were swapped at 45 seconds plus 0.5 seconds per move.
The referee used no ply cap. Both games ended with a capturable king. This
sample checks the workflow and does not estimate bot strength.

`config.json` records the run settings and code commit. `report.json` summarizes
the games. Replay JSON includes protocol events and local bot diagnostics.
`match.log` is the runner output. Check file integrity with
`sha256sum -c SHA256SUMS` from this directory.

To rerun from the repository root at the recorded source commit, use a separate
output directory with a copy of `source-commit.txt` and execute
`FOW_STOCKFISH=off PYTHONPATH="$PWD" uv run --locked python /absolute/path/to/run.py /absolute/path/to/output`.
