"""Build the independent, audited Stage 5 P8 corpora and execute the ablation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.stage2_corpus import audit, build, write_json
from tools.stage2_parity import verified_source_hashes
from tools.stage4_screen import sha256


def run_job(folder: Path, seed: int) -> None:
    from tools.stage5 import compute

    manifest = json.loads((folder / "manifest.json").read_text())
    if (manifest["project_id"], manifest["variant"], manifest["seed"]) != ("P8", "v2", seed):
        raise ValueError("P8 v2 manifest/config mismatch")

    stockfish = ROOT / "bots/obscuro_v4/stockfish/src/stockfish"
    network = stockfish.with_name("nn-1a298aa575a0.nnue")
    frozen = verified_source_hashes()
    if sha256(network) != frozen["stockfish_network_sha256"]:
        raise ValueError("Stockfish network differs from the frozen reference")

    corpora = {}
    sources = []
    started = perf_counter()
    for corpus_seed in range(seed, seed + 4):
        path = folder / "corpora" / str(corpus_seed)
        corpus, _, _ = build(path, corpus_seed)
        sources.append({
            "seed": corpus_seed,
            "manifest_sha256": sha256(path / "corpus_manifest.json"),
            "audit": audit(path),
            "split_game_ids": corpus["split_groups"],
        })
        corpora[corpus_seed] = path
    write_json(folder / "data_split.json", {
        "schema": 1,
        "provenance": "Four independent schema-2 synthetic referee corpora, using the Stage 2 generator and fresh seeds.",
        "analysis_splits": ["holdout", "opponent_shift"],
        "sources": sources,
    })
    report = compute.run(corpora, stockfish)
    json.dumps(report, allow_nan=False)
    write_json(folder / "ablation.json", report)
    primary = report["primary_metric"]
    write_json(folder / "metrics.json", {
        "schema": 1,
        "status": "complete" if primary else "incomplete",
        "claim_strength": False,
        "primary_metric": primary,
        "stockfish_sha256": sha256(stockfish),
        "network_sha256": sha256(network),
        "frozen_v4_source": frozen,
        "elapsed_seconds": perf_counter() - started,
    })
    (folder / "notes.md").write_text(
        "P8 v2 is an offline extra-breadth allocation ablation. Every included arm uses a common "
        "initial shortlist and slot quota. The reference worlds are disjoint from both candidate "
        "evaluation arms. The synthetic replays supply observation histories and no game clock.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--seed", required=True, type=int)
    args = parser.parse_args()
    run_job(args.run, args.seed)
