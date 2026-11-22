"""Summarize referee replays from one two-bot experiment."""
from collections import Counter
import random
import statistics

import chess


def distribution(values):
    return {
        "n": len(values),
        "min": min(values, default=None),
        "median": statistics.median(values) if values else None,
        "p90": sorted(values)[int(0.9 * (len(values) - 1))] if values else None,
        "max": max(values, default=None),
    }


def score_summary(games):
    wins = sum(game["score"] == 1 for game in games)
    draws = sum(game["score"] == 0.5 for game in games)
    losses = sum(game["score"] == 0 for game in games)
    return {
        "n": len(games), "wins": wins, "draws": draws, "losses": losses,
        "score_rate": (wins + draws / 2) / len(games) if games else None,
    }


def replay_metrics(replay):
    frames = replay["frames"]
    spent = [0.0, 0.0]
    hidden = [Counter(), Counter()]
    king_attacked = [0, 0]
    increment = replay["timeControl"]["incrementSeconds"]
    board = chess.Board()
    for before, after in zip(frames, frames[1:]):
        move = chess.Move.from_uci(after["move"])
        side = 0 if board.turn else 1
        victim = 1 - side
        spent[side] += before["clocks"][side] - after["clocks"][side] + increment
        capture_square = move.to_square
        if board.is_en_passant(move):
            capture_square += -8 if board.turn else 8
        piece = board.piece_at(capture_square)
        victim_view = before["black" if victim else "white"]
        if piece and piece.color != board.turn and victim_view[move.from_square] == "?":
            hidden[victim][piece.symbol().lower()] += 1
        board.push(move)
        for index, color in enumerate((chess.WHITE, chess.BLACK)):
            king = board.king(color)
            if king is not None and board.is_attacked_by(not color, king):
                king_attacked[index] += 1
    for failure in replay.get("studentReports", []):
        if failure["code"] == "time_limit":
            side = 0 if failure["side"] == "white" else 1
            spent[side] += frames[-1]["clocks"][side]
    return [
        {
            "clock_charged_seconds": round(spent[side], 6),
            "hidden_captures_suffered_by_piece": dict(hidden[side]),
            "king_attacked_post_move_frames": king_attacked[side],
        }
        for side in range(2)
    ]


def summarize(games, settings):
    valid = [game for game in games if game["score"] is not None]
    pairs = {}
    for game in valid:
        pairs.setdefault(game["pair"], []).append(game["score"])
    means = [statistics.mean(pair) for pair in pairs.values() if len(pair) == 2]
    interval = None
    if len(means) >= 5 and settings["purpose"] == "strength":
        rng = random.Random(20261122)
        resampled = sorted(statistics.mean(rng.choices(means, k=len(means))) for _ in range(5000))
        interval = [resampled[125], resampled[4874]]
    complete_games = [game for game in valid if len(pairs[game["pair"]]) == 2]
    return {
        "scheduled": settings["games"],
        "recorded": len(games),
        "invalid": len(games) - len(valid),
        "overall": score_summary(valid),
        "complete_pairs": len(means),
        "complete_pair_score": score_summary(complete_games),
        "complete_pair_score_interval_95": interval,
        "interval_method": "5000 percentile bootstrap resamples of complete color pairs, seed 20261122; suppressed for smoke or fewer than five pairs",
        "by_candidate_color": {
            color: score_summary([game for game in valid if game["candidate_color"] == color])
            for color in ("white", "black")
        },
        "plies": distribution([game["plies"] for game in valid]),
        "clock_charged_seconds": {
            role: distribution([game["metrics"][role]["clock_charged_seconds"] for game in valid])
            for role in ("candidate", "baseline")
        },
        "diagnostics": {
            role: {
                "king_attacked_post_move_frames": sum(
                    game["metrics"][role]["king_attacked_post_move_frames"] for game in valid
                ),
                "hidden_captures_suffered_by_piece": dict(sum(
                    (Counter(game["metrics"][role]["hidden_captures_suffered_by_piece"]) for game in valid),
                    Counter(),
                )),
            }
            for role in ("candidate", "baseline")
        },
        "termination_reasons": dict(Counter(game["reason"] for game in games)),
        "failure_codes": dict(Counter(code for game in games for code in game["failure_codes"])),
        "games": games,
    }


def markdown(report, settings):
    lines = ["# " + settings["id"], "", settings["hypothesis"], "",
             f"Candidate **{settings['candidate']}** vs baseline **{settings['baseline']}**. "
             f"{settings['base']}+{settings['increment']}, cap {settings['max_plies']} plies, "
             f"{report['recorded']}/{report['scheduled']} recorded, {report['invalid']} invalid. "
             f"Root seed {settings['seed']}, {settings['parallel']} worker(s).", ""]
    if settings["purpose"] == "smoke":
        lines.extend(["This smoke run checks integration and provides no playing-strength evidence.", ""])
    lines.extend(["| Candidate games | N | W | D | L | Score |",
                  "|---|---:|---:|---:|---:|---:|"])
    for name, row in [("All valid", report["overall"]), *report["by_candidate_color"].items()]:
        rate = "—" if row["score_rate"] is None else f"{row['score_rate']:.1%}"
        lines.append(f"| {name} | {row['n']} | {row['wins']} | {row['draws']} | {row['losses']} | {rate} |")
    interval = report["complete_pair_score_interval_95"]
    lines.extend(["", f"Complete color pairs · {report['complete_pairs']}.",
                  f"95% paired score interval · {interval if interval else 'unavailable'}.", ""])
    for label, key in (("Game lengths in plies", "plies"), ("Clock usage in seconds", "clock_charged_seconds"),
                       ("Termination reasons", "termination_reasons"), ("Failure codes", "failure_codes"),
                       ("King safety and hidden captures", "diagnostics")):
        lines.extend([f"## {label}", "", f"`{report[key]}`", ""])
    lines.append("See `manifest.json` for revision, binaries and environment, and `report.json` for per-game data.")
    return "\n".join(lines) + "\n"
