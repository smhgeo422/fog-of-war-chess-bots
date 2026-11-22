"""Run the Stage 4 limited FoW replay and referee screens from a clean commit."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import traceback

from tools.stage2_corpus import audit, build, write_json
from tools.stage2_parity import verified_source_hashes


REPO = Path(__file__).resolve().parents[1]
PROJECTS = {f"P{i}" for i in range(1, 10)}


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(output: Path, stockfish: Path | None) -> None:
    from tools.stage4 import compute, replay, tactics

    if git("status", "--porcelain"):
        raise ValueError("run Stage 4 from a clean, committed source revision")
    if stockfish is not None:
        stockfish = stockfish.resolve(strict=True)
    network = stockfish.with_name("nn-1a298aa575a0.nnue") if stockfish else None
    output.mkdir(parents=True, exist_ok=False)
    seed = 7106  # Stage 2 schema-2 reference fixture
    write_json(output / "manifest.json", {
        "schema": 1,
        "project_id": "Infra",
        "variant": None,
        "run_id": output.name,
        "source_commit": git("rev-parse", "HEAD"),
        "source_ref": git("branch", "--show-current"),
        "evidence_type": "offline",
        "purpose": "research",
        "script": "tools/stage4_screen.py",
        "hypothesis": "The nine v1 mechanisms can be screened independently on restricted referee fixtures and held-out synthetic referee histories.",
        "frozen_v4_source": verified_source_hashes(),
        "seed": seed,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "available_logical_cpus": os.process_cpu_count(),
            "stockfish_sha256": sha256(stockfish) if stockfish else None,
            "stockfish_network_sha256": sha256(network) if network and network.is_file() else None,
        },
    })
    (output / "notes.md").write_text(
        "Restricted referee fixtures and locally regenerated Stage 2 synthetic games. "
        "The project-specific outcomes and limitations are in projects.json. "
        "This run contains zero playing-strength matches.\n",
        encoding="utf-8",
    )
    try:
        corpus = output / "corpus"
        manifest, _, observations = build(corpus, seed)
        checks = audit(corpus)
        write_json(output / "data_split.json", {
            "schema": 1,
            "provenance": manifest["provenance"],
            "mode": "locally regenerated schema 2",
            "split_game_ids": manifest["split_groups"],
            "observations": len(observations),
            "corpus_manifest_sha256": sha256(corpus / "corpus_manifest.json"),
            "games_registry_sha256": sha256(corpus / "game_registry.json"),
            "audit": checks,
        })
        projects = {
            **replay.run(corpus, stockfish),
            **tactics.run(),
            **compute.run(corpus, stockfish),
        }
        if projects.keys() != PROJECTS:
            raise ValueError("expected one screening record per Stage 0 proposal")
        # Fail closed if an unmeasurable metric produced a NaN or infinity.
        json.dumps(projects, allow_nan=False)
        write_json(output / "projects.json", projects)
        write_json(output / "metrics.json", {
            "schema": 1,
            "status": "complete",
            "claim_strength": False,
            "primary_metric": {
                "name": "stage4_project_screen_records",
                "value": len(projects),
                "n": len(PROJECTS),
                "unit": "projects",
            },
            "scope": "Completion count includes restricted and blocked endpoint records.",
            "playing_matches": 0,
        })
    except Exception:
        (output / "failure.log").write_text(traceback.format_exc(), encoding="utf-8")
        write_json(output / "metrics.json", {"schema": 1, "status": "failed"})
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--stockfish", type=Path)
    args = parser.parse_args()
    run(args.run, args.stockfish)


if __name__ == "__main__":
    main()
