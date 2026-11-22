"""Stage 2 corpus, referee/oracle split, baseline profile and archival gates."""
from __future__ import annotations

import json
from pathlib import Path
import sys

import chess
import pytest

from tools.stage2_corpus import (COUNTS, MAX_PLIES, audit, build, choose, digest,
                                 play, score, validate_replay)
from tools.stage2_parity import B1_ENV
from tools.stage2_pipeline import rule_regression
from tools.experiment import load_settings


def make_config(tmp_path, **options):
    data = {"id": "ctrl", "hypothesis": "Stage 2 baseline control",
            "candidate": "eBotI", "baseline": "obscuro_v4",
            "games": 2, "seed": 17, "purpose": "smoke"}
    data.update(options)
    path = tmp_path / "control.json"
    path.write_text(json.dumps(data))
    return path


def test_control_profile_explicitly_disables_known_nonv4_features():
    assert B1_ENV["FOW_SAFE_FIRST"] == "0"
    assert B1_ENV["FOW_EXACT_RISK"] == "0"
    assert B1_ENV["FOW_HANG"] == "0"
    assert B1_ENV["FOW_ATTACKED"] == "6"
    assert B1_ENV["FOW_CLOCK"] == "v4"
    assert B1_ENV["FOW_BOOK"] == "none"


def test_candidate_environment_isolated_from_frozen_baseline(tmp_path):
    config = load_settings(make_config(tmp_path, candidate_env=B1_ENV), None)
    assert config["candidate_env"] == B1_ENV
    assert config["baseline_env"] == {}
    assert config["baseline"] == "obscuro_v4"


@pytest.mark.parametrize("override", [
    {"FOW_STOCKFISH": "fake"},
    {"FOW_POSITIONS": "fake"},
    {"FOW_ENGINES": "99"},
    {"HOME": "/tmp"},
    {"FOW_BOOK": "$(rm-a)"},
    {"FOW_HANG": 2},
])
def test_invalid_or_unsafe_environment_override_rejected(tmp_path, override):
    with pytest.raises(ValueError):
        load_settings(make_config(tmp_path, candidate_env=override), None)


@pytest.mark.parametrize("field", ["candidate_env", "baseline_env"])
def test_environment_overrides_must_be_objects(tmp_path, field):
    with pytest.raises(ValueError, match="object"):
        load_settings(make_config(tmp_path, **{field: ["FOW_HANG=1"]}), None)


def test_special_referee_castle_ep_repetition_king_capture_and_draw():
    outcomes = rule_regression()
    assert len(outcomes) >= 6
    assert all(outcomes.values())


@pytest.mark.parametrize("a,b,side", [
    ("uniform", "uniform", True),
    ("visible_capture", "king_pressure", False),
    ("king_pressure", "uniform", True),
])
def test_policy_scores_depend_on_view_only(a, b, side):
    view = "?" * 64
    moves = [chess.Move.from_uci("a2a3"), chess.Move.from_uci("b2b3")]
    rng = __import__("random").Random(3)
    assert score(moves[0], view, side, a) > 0
    assert choose(moves, view, side, b, rng) in moves


def test_generated_pair_rebuilds_every_referee_state_and_view():
    a, xs, labels = play("test-a", 16, 1, 0, "train", "uniform", "visible_capture")
    b, ys, labels_b = play("test-b", 16, 1, 1, "train", "visible_capture", "uniform")
    assert len(xs) > 5 and len(ys) > 5
    assert validate_replay(a) == len(xs)
    assert validate_replay(b) == len(ys)
    assert all(x["selected_action"] in x["legal_attempts"] for x in xs)
    assert all(l["retrospective_only"] for l in labels + labels_b)
    assert "truth_board_fen" not in xs[0] and "truth_board_fen" in labels[0]


def test_replay_validation_catches_forged_full_board_or_future_view():
    data, _, _ = play("mutate", 7, 2, 0, "train", "uniform", "visible_capture")
    data["frames"][1]["board"] = "-" * 64
    with pytest.raises(ValueError, match="full board"):
        validate_replay(data)


def test_reference_corpus_has_disjoint_game_and_color_block_splits(tmp_path):
    root = tmp_path / "dataset"
    manifest, game_records, features = build(root, 7106)
    metrics = audit(root)
    assert manifest["games"] == sum(COUNTS.values()) * 2 == 72
    assert metrics["pairs_checked"] == sum(COUNTS.values()) == 36
    assert metrics["games_checked"] == 72
    assert metrics["decisions_checked"] > 200
    assert set(x["split"] for x in features) == set(COUNTS)
    assert all(x["opponent_policy"] != "king_pressure" for x in features
               if x["split"] != "opponent_shift")
    assert len({x["game_id"] for x in game_records}) == 72
    by_block = {}
    for game in game_records:
        by_block.setdefault(game["pair_block"], set()).add(game["split"])
    assert all(len(s) == 1 for s in by_block.values())
    assert not any("truth_board" in x or "future" in x for x in features)
    assert all("?" in x["view"] for x in features[:15])
    # Replay files in the official referee format remain retrospective labels.
    assert all((root / item["replay"]).is_file() for item in game_records)


def test_corrupted_replay_checksums_fail_reaudit(tmp_path):
    root = tmp_path / "dataset"
    _, games, _ = build(root, 319)
    path = root / games[0]["replay"]
    path.write_text(path.read_text() + "\n")
    with pytest.raises(ValueError, match="SHA mismatch"):
        audit(root)
