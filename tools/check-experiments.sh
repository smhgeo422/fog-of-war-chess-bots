#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
logs=data/research/checks
mkdir -p "$logs"
tools/setup-experiments.sh 2>&1 | tee "$logs/setup.log"
FOW_STOCKFISH="$PWD/bots/obscuro/stockfish/src/stockfish" \
    .venv/bin/python -m pytest -ra 2>&1 | tee "$logs/pytest.log"
.venv/bin/python tools/experiment.py experiments/configs/ci-smoke.json "$@" |
    tee "$logs/smoke.log"
