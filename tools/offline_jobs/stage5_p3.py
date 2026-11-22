"""Run the P3 v2 bounded tactical ablation on independent referee fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.stage2_corpus import write_json
from tools.stage2_parity import verified_source_hashes


def run_job(folder: Path, seed: int) -> None:
    from tools.stage5 import tactics

    manifest = json.loads((folder / "manifest.json").read_text())
    if (manifest["project_id"], manifest["variant"], manifest["seed"]) != ("P3", "v2", seed):
        raise ValueError("P3 v2 manifest/config mismatch")
    write_json(folder / "data_split.json", {
        "schema": 1,
        "provenance": "Declared bounded local FoW referee tactical fixtures and their color mirrors. No training or competitive replays.",
    })
    report = tactics.run()
    json.dumps(report, allow_nan=False)
    write_json(folder / "ablation.json", report)
    primary = report["primary_metric"]
    write_json(folder / "metrics.json", {
        "schema": 1,
        "status": "complete" if primary else "incomplete",
        "claim_strength": False,
        "primary_metric": primary,
        "frozen_v4_source": verified_source_hashes(),
    })
    (folder / "notes.md").write_text(
        "P3 v2 ablates one reply slot against the legacy infoset ranking on bounded "
        "referee fixtures. The ablation isolates reply selection. Live engine-depth, clock, "
        "and playing-strength effects require separate tests.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--seed", required=True, type=int)
    args = parser.parse_args()
    run_job(args.run, args.seed)
