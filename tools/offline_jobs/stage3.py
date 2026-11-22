#!/usr/bin/env python3
"""Execute precisely one P1-P9 Stage 3 v1 scientific toy algorithm.

The tracked offline runner supplies the project ID and seed in manifest.json.
Each project has its own module, hypothesis, falsification test and metric
definition. Synthetic toy evidence is NOT a full FoW strength experiment.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


METRICS = {
    "P1": ("rare_event_importance_sampling_mse", lambda r: r["proposal_results"]["0.3"]["mse"], 250,
           "Compare corrected threat sampling against exact 4-state hidden-event prior."),
    "P2": ("observable_event_style_model_retrospective_action_nll", lambda r: r["online_mean_nll"], 180,
           "Infer online style from event equivalence classes and retrospectively score actions."),
    "P3": ("bounded_contingent_strategy_fusion_gap", lambda r: r["ambiguous_fusion_gap"], 2,
           "Choose a single future action per observation/history set, not per hidden board."),
    "P4": ("instrumental_information_value_matched_action", lambda r: r["relevant_voi"], 2,
           "Compare new information only when direct tactical value is matched."),
    "P5": ("heldout_selective_hidden_material_brier", lambda r: r["calibrated_brier"]["overall"], 200,
           "Calibrate quiet exposed and hidden capture losses by action class."),
    "P6": ("restricted_game_exploitability_gap", lambda r: r["matching_pennies"]["certificate"]["exploitability_gap"], 6000,
           "Compute average mixed security strategy with exact restricted best response."),
    "P7": ("heldout_synthetic_counterfactual_residual_mse", lambda r: r["holdout_mse"], 160,
           "Fit a regularized bounded value residual using only predecision feature vectors."),
    "P8": ("near_tie_exact_computation_value", lambda r: r["near_tie_gain"], 2,
           "Allocate another computation if expected better decision exceeds shadow clock cost."),
    "P9": ("finite_endgame_reachability_certifier_soundness", lambda r: float(r["adversary_counterexample_rejected"]), 2,
           "Certify one information-state action across hidden worlds and all defender replies."),
}

LIMITATIONS = {
    "P1": "No legal-history reconstruction algorithm; operates only on provided valid state support.",
    "P2": "Artificial action-feature scores and toy observed events; actual live opponent view is uncertain.",
    "P3": "Leaf utilities are controlled synthetic tables, not depth/CPU-matched Stockfish.",
    "P4": "Artificial matched action values; not calibrated opponent information-denial benefit.",
    "P5": "Artificial Bernoulli event labels; proper scoring trial only, no empirical risk change.",
    "P6": "Normal-form zero-sum restricted game, not a FoW extensive-form CFR/blueprint solve.",
    "P7": "Synthetic counterfactual value teacher; not actual Stockfish residual or causal outcome.",
    "P8": "Synthetic computation-outcome distribution; no measured engine node/clock benefit.",
    "P9": "Finite toy graph and limited local referee sanity; not a global queen-v-king theorem.",
}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
                    encoding="utf-8")


def run_job(folder, seed):
    folder = Path(folder)
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    project = manifest["project_id"]
    if project not in METRICS or manifest["variant"] != "v1":
        raise ValueError("Stage3 offline run requires P1-P9 v1")
    if manifest["seed"] != seed or manifest["purpose"] != "research":
        raise ValueError("seed/purpose mismatch")
    module = importlib.import_module("tools.stage3." + project)
    source = Path(module.__file__)
    if not source.resolve().is_relative_to(ROOT / "tools/stage3"):
        raise ValueError("algorithm source outside tracked Stage3 project directory")
    started = time.perf_counter()
    result = module.trial(seed)
    elapsed = time.perf_counter() - started
    if not isinstance(result, dict):
        raise ValueError("project trial must return evidence dictionary")
    name, measure, n, definition = METRICS[project]
    primary = float(measure(result))
    if not -1e10 < primary < 1e10:
        raise ValueError("nonfinite primary test result")
    write_json(folder / "results" / "toy_evidence.json", result)
    write_json(folder / "results" / "algorithm_metadata.json", {
        "schema": 1, "project_id": project, "variant": "v1",
        "module": str(source.relative_to(ROOT)),
        "module_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "specification": "research/projects/" + project + "/proposal.md",
        "scientific_question": definition, "toy_primary": name,
        "toy_n": n, "predeclared_limitations": LIMITATIONS[project],
        "not_integrated_into_arena": True,
        "no_offline_train_holdout_strength_claim": True,
        "no_auto_merge": True,
    })
    write_json(folder / "metrics.json", {
        "schema": 1, "status": "complete", "claim_strength": False,
        "primary_metric": {"name": name, "value": primary, "n": n},
        "seconds_elapsed": elapsed, "independent_kernel": project,
        "interpretation": "Executable algorithmic toy correctness / predictive feasibility only, not verified FoW playing strength.",
        "known_limitations": LIMITATIONS[project],
    })
    write_json(folder / "data_split.json", {
        "schema": 1,
        "provenance": "tracked Stage 3 synthetic fixtures generated from toy models; "
                      "no use of private arena replays, official match data, or Stage 2 holdout labels",
        "seed": seed, "algorithm": project, "version": "v1",
        "train_test_definition": "Module-specific deterministic synthetic fixture, "
                                 "not a competitive opponent/seed-heldout corpus",
        "not_a_game_strength_dataset": True,
        "stage2_holdout_accessed": False,
    })
    (folder / "notes.md").write_text(
        "# " + project + " v1 scientific toy algorithm\n\n"
        "## Distinct question\n" + definition + "\n\n"
        "## Measured toy primary\n" + name + " = " + str(primary) + "\n\n"
        "## Scope\n"
        "The tracked kernel is tools/stage3/" + project + ".py.\n"
        "The original proposal is research/projects/" + project + "/proposal.md.\n"
        "This run is not a FoW chess strength claim and is **not** a replacement "
        "for the Stage 4 offline/replay-screening or later controlled tournaments.\n\n"
        "## Unresolved\n" + LIMITATIONS[project] + "\n\n"
        "## Scientific integrity\n"
        "The result is recorded even if it is unfavorable to the hypothesis. "
        "Do not infer improvement over an unchanged frozen v4 bot from toy utility, "
        "event NLL, MSE, or an equilibrium gap alone.\n",
        encoding="utf-8",
    )
    print(json.dumps({"project": project, "variant": "v1",
                      "primary_metric": name, "measured_value": primary,
                      "n": n, "elapsed_seconds": round(elapsed, 4),
                      "claim_strength": False}, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    run_job(args.run.resolve(), args.seed)
