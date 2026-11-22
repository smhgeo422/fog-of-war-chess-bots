#!/usr/bin/env python3
"""Stage 2 offline evidence: frozen references, action probe and nonleaking corpus.

Executed only on a user-triggered Stage 2 branch with a tracked source SHA.
Writes complete machine-readable scientific-method evidence, not strength claims.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import fow  # noqa: F401,E402
import chess  # noqa: E402
import referee  # noqa: E402
try:
    from .stage2_corpus import build, audit, write_json
    from .stage2_parity import B0, B1, B2, B1_ENV, static_audit, black_box_probe, verified_source_hashes
except ImportError:  # standalone tools/stage2_pipeline.py CLI
    from stage2_corpus import build, audit, write_json
    from stage2_parity import B0, B1, B2, B1_ENV, static_audit, black_box_probe, verified_source_hashes


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rule_regression():
    """Probe the three FoW-specific rule categories with an independent fixture."""
    results = {}
    castle = referee.FowBoard("4k3/8/8/8/8/8/4r3/R3K2R w KQ - 0 1")
    castle_moves = {m.uci() for m in referee.fow_moves(castle)}
    results["castling_through_attacked_squares_allowed"] = (
        "e1g1" in castle_moves and "e1c1" in castle_moves)
    enp = referee.FowBoard()
    for uci in ("e2e4", "a7a6", "e4e5", "d7d5"):
        if chess.Move.from_uci(uci) not in referee.fow_moves(enp):
            raise ValueError("en-passant setup contains invalid move")
        enp.push_uci(uci)
    results["en_passant_visible_destination_legal"] = (
        chess.Move.from_uci("e5d6") in referee.fow_moves(enp))
    board = referee.FowBoard()
    reps = Counter({referee.position_key(board): 1})
    for uci in ("g1f3", "g8f6", "f3g1", "f6g8",
                "g1f3", "g8f6", "f3g1", "f6g8"):
        if chess.Move.from_uci(uci) not in referee.fow_moves(board):
            raise ValueError("repetition setup invalid")
        board.push_uci(uci)
        reps[referee.position_key(board)] += 1
    results["fow_threefold_repetition"] = (
        referee.outcome(board, reps) == ("1/2-1/2", "Threefold repetition"))
    fifty = referee.FowBoard("k7/8/8/8/8/8/8/7K w - - 100 51")
    results["fifty_move_terminal_draw"] = (
        referee.outcome(fifty, Counter({referee.position_key(fifty): 1}))
        == ("1/2-1/2", "50-move rule"))
    attack = referee.FowBoard("4k3/8/8/8/8/8/4Q3/4K3 w - - 0 1")
    results["capturable_opponent_king_terminal"] = (
        referee.outcome(attack, Counter({referee.position_key(attack): 1}))
        == ("1-0", "King capturable"))
    initial = referee.FowBoard()
    for color in (chess.WHITE, chess.BLACK):
        view = referee.observation(initial, color)
        own = {p.symbol() for p in initial.piece_map().values() if p.color == color}
        results["own_pieces_visible_" + ("white" if color else "black")] = (
            len(view) == 64 and
            all(view[square] == piece.symbol()
                for square, piece in initial.piece_map().items() if piece.color == color))
    if not all(results.values()):
        raise ValueError("referee rule regression failure: " + str(results))
    return results


def record_binaries():
    bots = {}
    for name in (B0, B1):
        directory = ROOT / "bots" / name
        assets = {"bot_entry": directory / "bot.py",
                  "positions": directory / "positions",
                  "stockfish": directory / "stockfish/src/stockfish",
                  "network": directory / "stockfish/src/nn-1a298aa575a0.nnue"}
        statuses = {}
        for key, path in assets.items():
            if not path.is_file():
                raise ValueError("missing bot artifact: " + str(path))
            statuses[key] = {"sha256": file_sha(path), "relative_path": str(path.relative_to(ROOT))}
        bots[name] = statuses
    if bots[B0]["stockfish"]["sha256"] == bots[B1]["stockfish"]["sha256"]:
        # Both engines built from identical Stockfish source; distinct per-bot
        # paths, not necessarily unequal content hashes, are the isolation check.
        pass
    if bots[B0]["network"]["sha256"] != bots[B1]["network"]["sha256"]:
        raise ValueError("different Stockfish networks in control bots")
    return bots


def make_manifest(output, seed):
    sha = git("rev-parse", "HEAD")
    if git("status", "--porcelain"):
        raise ValueError("Stage 2 must use a committed clean source revision")
    return {
        "schema": 1, "evidence_type": "offline", "project_id": "Infra",
        "run_id": output.name, "variant": None, "source_commit": sha,
        "source_ref": git("rev-parse", "--abbrev-ref", "HEAD"),
        "hypothesis": "Local referee rules, split provenance, and B0/B1/B2 controls are auditable before scientific algorithms.",
        "purpose": "research", "seed": seed, "script": "tools/stage2_pipeline.py",
        "utc_started": datetime.now(timezone.utc).isoformat(),
        "environment": {"platform": platform.platform(), "python": platform.python_version()},
        "not_strength_evidence": True,
    }


def run(output, seed):
    output = Path(output)
    if output.exists():
        raise ValueError("Stage 2 run directory already exists")
    manifest = make_manifest(output, seed)
    output.mkdir(parents=True)
    write_json(output / "manifest.json", manifest)
    try:
        laws = rule_regression()
        frozen = verified_source_hashes()
        bins = record_binaries()
        corpus, records, features = build(output / "corpus", seed)
        checks = audit(output / "corpus")
        stat = static_audit()
        live = black_box_probe(output / "parity_logs")
        write_json(output / "baseline_audit.json", {
            "schema": 1,
            "reference": {"id": "B0", "bot": B0, "frozen": True, "hashes": frozen},
            "parity_candidate": {"id": "B1", "bot": B1, "env": B1_ENV,
                                 "parity_profile_status": "proposed_not_assumed"},
            "working_bot": {"id": "B2", "bot": B2, "env": {},
                            "note": "B2 is current default; not assumed stronger than B0"},
            "bot_binary_hashes": bins,
            "static": stat, "behavioral_probe": live,
            "parity_conclusion": (
                "Limited shared-history action agreement observed; not a proof of complete bot equivalence."
                if live["action_parity_established"] and stat["all_shared_components_equal"]
                else "B1 NOT verified action-equivalent: freeze B0 as the baseline; do not equate B1 with B0."
            ),
        })
        game_ids = corpus["split_groups"]
        split_manifest = {
            "schema": 1, "provenance": corpus["provenance"],
            "dataset": "corpus/observations and separate corpus/retrospective_labels",
            "generator": corpus["generator"], "root_seed": seed,
            "train_game_ids": game_ids["train"],
            "development_game_ids": game_ids["development"],
            "holdout_game_ids": game_ids["holdout"],
            "opponent_shift_holdout_game_ids": game_ids["opponent_shift"],
            "train_test_unit": "whole game; paired opening/color block never crosses split",
            "train_data_policy": "only on observed legal actions, never use retrospective truth as live input",
            "synthetic_not_representative_of_competitive_opponents": True,
            "split_manifest_sha256": file_sha(output / "corpus/corpus_manifest.json"),
            "registry_sha256": file_sha(output / "corpus/game_registry.json"),
            "feature_rows": len(features),
        }
        write_json(output / "data_split.json", split_manifest)
        write_json(output / "referee_checks.json", laws)
        metrics = {
            "schema": 1, "status": "complete", "claim_strength": False,
            "primary_metric": {
                "name": "reference_replay_reconstruction_rate", "value": 1.0,
                "n": checks["games_checked"], "unit": "games",
            },
            "secondary_metrics": {
                "rule_regression_checks": len(laws),
                "games": checks["games_checked"], "color_swapped_pairs": checks["pairs_checked"],
                "observed_decisions": checks["decisions_checked"],
                "split_games": checks["split_counts"],
                "static_parity_components": stat["checks"],
                "live_action_parity_comparisons": live["action_comparisons"],
                "live_action_parity_equal": live["equal_actions"],
                "live_action_divergences": live["divergent_actions"],
                "live_runtime_errors": live["runtime_errors"],
                "B1_action_parity_established": live["action_parity_established"] and
                                                stat["all_shared_components_equal"],
            },
            "interpretation": "Reference rule/data integrity only; synthetic starter-policy corpus, no chess strength inference.",
        }
        write_json(output / "metrics.json", metrics)
        notes = [
            "# Stage 2: baseline controls, referee-rule audit and held-out reference corpus",
            "",
            "## Source revision", manifest["source_commit"], "",
            "All 72 games are generated locally from permitted open starter code.",
            "This corpus tests observation and replay validity and is not evidence of strong play.",
            "No outside arena games or unseen private team data were accessed.",
            "",
            "## Validation",
            f"- {checks['games_checked']} games, {checks['pairs_checked']} swapped-color pairs, {checks['decisions_checked']} decisions reconstructed",
            "- Every game replay, per-ply board and both side observations matched the referee.",
            f"- {len(laws)} special-rule regression checks passed",
            f"- {sum(stat['checks'].values())}/{len(stat['checks'])} shared-component baseline parity checks matched",
            f"- Black-box parity: {live['equal_actions']}/{live['action_comparisons']} identical choices, {live['divergent_actions']} divergences, {live['runtime_errors']} runtime errors.",
            "",
            "## Interpretation",
            ("B1 passed finite observed action-prefix probes but does not have an all-histories equivalence proof."
             if live["action_parity_established"] and stat["all_shared_components_equal"]
             else "B1 **has NOT been shown equivalent** to the frozen B0. Use actual B0 for control comparisons."),
            "",
            "## Split and leakage policy",
            "Train 36 games; development 12; in-family held-out 12; opponent-style shift held-out 12.",
            "Paired games remain together in one split. Observation files contain only each player's",
            "information-available view and legal actions. Private true board/FEN labels live in",
            "separate retrospective_labels/ files and are forbidden as online model inputs.",
            "The opponent-style holdout policy never appears in any development or training game.",
            "",
            "## Next stage",
            "Project v1 code is implemented only if user requests Stage 3.",
            "This is NOT a competitive learning dataset and should be augmented with approved",
            "real bot replays before claiming P2/P7 generalization or meaningful Elo.",
        ]
        (output / "notes.md").write_text("\n".join(notes) + "\n", encoding="utf-8")
        print(json.dumps({"status": "complete", "source": manifest["source_commit"],
                          "replayed_games": checks["games_checked"],
                          "synthetic_decisions": checks["decisions_checked"],
                          "parity": live["action_parity_established"],
                          "live_divergences": live["divergent_actions"]}, sort_keys=True))
        return metrics
    except Exception as exc:
        error = {"schema": 1, "status": "failed", "claim_strength": False,
                 "primary_metric": None, "failure": type(exc).__name__ + ": " + str(exc)}
        write_json(output / "metrics.json", error)
        if not (output / "data_split.json").is_file():
            write_json(output / "data_split.json", {
                "schema": 1, "provenance": "Stage 2 pipeline failed before verified corpus completion"
            })
        (output / "notes.md").write_text(
            "# Stage 2 failure, not a successful corpus\n\n" + repr(exc) + "\n\n"
            + traceback.format_exc()[-10000:], encoding="utf-8")
        raise


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--seed", type=int, default=7106)
    args = p.parse_args()
    run(args.run.resolve(), args.seed)
