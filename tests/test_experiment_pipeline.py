"""Checks for experiment reproducibility and failure accounting."""
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from experiment import ComponentCapture, load_settings, validate_components
from experiment_report import summarize


def config(tmp_path, **changes):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({
        "id": "sample", "candidate": "eBotI", "games": 2,
        "seed": 7, "hypothesis": "Smoke", **changes,
    }))
    return path


@pytest.mark.parametrize("changes", [
    {"games": 3}, {"candidate_args": ["--stockf=off"]}, {"baseline_args": ["--seed=2"]},
    {"id": "../outside"}, {"parallel": 0},
])
def test_configuration_rejects_imbalanced_or_unmanaged_runs(tmp_path, changes):
    with pytest.raises(ValueError):
        load_settings(config(tmp_path, **changes), None)


def test_configuration_defaults_to_frozen_baseline_and_arena_clock(tmp_path):
    settings = load_settings(config(tmp_path), "override")
    assert (settings["id"], settings["baseline"], settings["base"], settings["increment"]) == (
        "override", "obscuro_v4", 180, 2,
    )


def test_required_engine_uses_matching_readiness_and_detects_late_failure(monkeypatch):
    monkeypatch.setattr(ComponentCapture, "instances", [], raising=False)
    capture = ComponentCapture()
    bot = {"name": "test", "components": {"stockfish": {"engines": 2, "path": "/test/stockfish"}}}
    capture.feed(b"obscuro: stockfish ready: 2 of 2 ")
    capture.feed(b"engines in 0.1s, binary /test/stockfish\n")
    assert validate_components(bot, capture) == []
    capture.feed(b"other log\n" * 2000)
    assert validate_components(bot, capture) == []
    capture.feed(b"obscuro: stockfish engine lost (exited)\n")
    assert "engine lost" in validate_components(bot, capture)[0]


def test_invalid_games_and_incomplete_pairs_are_visible():
    metrics = {role: {"clock_charged_seconds": 0.5, "king_attacked_post_move_frames": 0,
                      "hidden_captures_suffered_by_piece": {}} for role in ("candidate", "baseline")}
    scores = [(1, "white", 1), (1, "black", 0.5), (2, "white", 0), (2, "black", None)]
    games = [
        {"pair": pair, "score": score, "candidate_color": color, "plies": 12, "metrics": metrics,
         "reason": "component unavailable" if score is None else "complete",
         "failure_codes": ["component_failure"] if score is None else []}
        for pair, color, score in scores
    ]
    report = summarize(games, {"games": 4, "purpose": "smoke"})
    assert report["overall"]["score_rate"] == 0.5
    assert report["complete_pair_score"]["score_rate"] == 0.75
    assert report["complete_pair_score_interval_95"] is None
    assert report["by_candidate_color"]["white"]["n"] == 2
    assert report["invalid"] == 1
    assert report["failure_codes"] == {"component_failure": 1}
