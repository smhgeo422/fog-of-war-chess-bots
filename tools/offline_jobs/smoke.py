#!/usr/bin/env python3
"""Deterministic synthetic fixture for Stage 1 archiving; NOT a research study."""
import argparse
import json
from pathlib import Path


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--seed", type=int, required=True)
    args = p.parse_args()
    run = args.run
    write(run / "metrics.json", {
        "schema": 1, "status": "complete",
        "primary_metric": {"name": "synthetic_integrity_only", "value": 1.0, "n": 2},
        "claim_strength": False,
        "interpretation": "Synthetic fixture, deliberately not scientific evidence",
    })
    write(run / "data_split.json", {
        "schema": 1, "provenance": "deterministic generated synthetic fixture",
        "train_ids": ["synthetic-train"], "test_ids": ["synthetic-test"],
        "seed": args.seed, "contains_real_game_data": False,
    })
    (run / "notes.md").write_text(
        "# Synthetic offline archiving smoke\n\nNo algorithm, model training,"
        " chess outcome, statistical inference, or playing-strength claim.\n")
    write(run / "model/weights.json", {
        "type": "synthetic_placeholder", "coefficients": [0.0, 0.0],
        "research_claim": False,
    })
    (run / "predictions/rows.jsonl").parent.mkdir(parents=True, exist_ok=True)
    (run / "predictions/rows.jsonl").write_text(
        '{"id":"synthetic-train","prediction":0.0}\n'
        '{"id":"synthetic-test","prediction":0.0}\n'
    )


if __name__ == "__main__":
    main()
