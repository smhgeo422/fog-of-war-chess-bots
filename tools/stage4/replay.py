"""Screen P1, P2 and P5 on the deterministic Stage 2 referee corpus.

Predecision forecasts use only one player's own view/history, or hypothetical
referee boards inferred from that history. Full replay moves and boards join
forecasts as retrospective labels. The synthetic corpus has no clocks.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import json
import math
from pathlib import Path
import random
from statistics import mean
from time import monotonic, process_time

from bots.eBotI.eBotI.engine import EnginePool
from bots.eBotI.eBotI.opponent import OTHER, OpponentPolicy
from tools import stage2_corpus
from tools.stage3 import P1, P2, P5

import chess
import referee


EARLY_PLIES = 8
MAX_HISTORIES = 256
ROOTS = 64
DRAW_REPETITIONS = 8
STYLES = ("capture", "quiet", "pressure")
STYLE_PRIOR = dict.fromkeys(STYLES, 1 / len(STYLES))
EVAL_SPLITS = ("holdout", "opponent_shift")
CORPUS_NAME = "Stage 2 schema-2 synthetic starter-policy replays (seed 7106)"


@dataclass(frozen=True)
class World:
    board: referee.FowBoard
    weight: float


def initial_support() -> list[World]:
    return [World(referee.FowBoard(), 1.0)]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def load_games(corpus: Path) -> list[tuple[dict, dict, list[dict], list[dict]]]:
    manifest = json.loads((corpus / "corpus_manifest.json").read_text())
    if manifest["schema"] != 2 or manifest["seed"] != 7106:
        raise ValueError("Stage 4 requires the pinned, schema-2 reference corpus")
    stage2_corpus.audit(corpus)
    registry = json.loads((corpus / "game_registry.json").read_text())
    games = []
    for split in ("train", *EVAL_SPLITS):
        observations = defaultdict(list)
        labels = defaultdict(list)
        for row in read_jsonl(corpus / "observations" / f"{split}.jsonl"):
            observations[row["game_id"]].append(row)
        for row in read_jsonl(corpus / "retrospective_labels" / f"{split}.jsonl"):
            labels[row["game_id"]].append(row)
        for game in registry:
            if game["split"] != split:
                continue
            replay = json.loads((corpus / game["replay"]).read_text())
            rows = observations[game["game_id"]]
            outcomes = labels[game["game_id"]]
            frames = replay["frames"]
            truth = referee.FowBoard()
            if len(rows) != len(frames) - 1 or len(outcomes) != len(rows):
                raise ValueError("reference rows do not cover replay")
            for ply, (row, outcome) in enumerate(zip(rows, outcomes)):
                online = row["online_inputs"]
                side = "white" if ply % 2 == 0 else "black"
                if (row["ply"] != ply or online["side"] != side
                        or online["view"] != frames[ply][side]
                        or outcome["truth_board_fen"] != truth.fen()
                        or outcome["policy"] != replay["policies"][side]
                        or outcome["selected_action"] != frames[ply + 1]["move"]):
                    raise ValueError("observation/action row contradicts referee replay")
                truth.push(chess.Move.from_uci(frames[ply + 1]["move"]))
            games.append((game, replay, rows, outcomes))
    return games


def on_own_action(worlds: list[World], action: str, side: chess.Color,
                  observed_after: str) -> list[World]:
    move = chess.Move.from_uci(action)
    result = []
    for world in worlds:
        if move not in referee.fow_moves(world.board):
            continue
        successor = world.board.copy(stack=False)
        successor.push(move)
        if referee.observation(successor, side) == observed_after:
            result.append(World(successor, world.weight))
    return result


def action_features(view: str, side: chess.Color, move: chess.Move) -> dict:
    dest = move.to_square
    enemy = "pnbrqk" if side else "PNBRQK"
    visible_king = view.find("k" if side else "K")
    if visible_king < 0:
        pressure = 1 - abs(chess.square_file(dest) - 3.5) / 3.5
    else:
        pressure = 1 - chess.square_distance(dest, visible_king) / 7
    return {
        "capture": float(view[dest] in enemy),
        "promotion": float(bool(move.promotion)),
        "development": float(view[move.from_square].lower() in "nb"
                             and chess.square_rank(move.from_square) == (0 if side else 7)),
        "pressure": pressure,
    }


def continuing(board: referee.FowBoard) -> bool:
    # This screen stops before ply 8 can become a predecision position.
    # Repetition and the 50-move rule cannot end a game before that cutoff.
    king = board.king(not board.turn)
    return (king is not None and not board.is_attacked_by(board.turn, king)
            and any(board.generate_pseudo_legal_moves()))


def opponent_forecast(worlds: list[World], side: chess.Color, online: dict,
                      observed_after: str, stockfish: OpponentPolicy | None = None,
                      stockfish_coverage: Counter | None = None) -> tuple[dict, list[World], dict, bool]:
    """Score hypothetical action/event distributions, then use the observed view."""
    methods = {"uniform": None, "static": STYLE_PRIOR, "online": online}
    roots = [(world, referee.fow_moves(world.board)) for world in worlds if continuing(world.board)]
    if not roots:
        return {}, [], online, False
    odds = [None] * len(roots)
    if stockfish is not None:
        methods["stockfish"] = None
        odds = stockfish([world.board for world, _ in roots], [len(moves) for _, moves in roots])
        if stockfish_coverage is not None:
            stockfish_coverage["eligible_worlds"] += len(roots)
            stockfish_coverage["engine_scored_worlds"] += sum(table is not None for table in odds)
    action_mass = {k: defaultdict(float) for k in methods}
    event_mass = {k: defaultdict(float) for k in methods}
    tables, events, weights, next_worlds = [], [], [], []
    total = sum(world.weight for world, _ in roots)
    for (world, moves), engine_odds in zip(roots, odds, strict=True):
        board = world.board
        opponent_view = referee.observation(board, not side)
        features = [action_features(opponent_view, not side, move) for move in moves]
        world_events = []
        weight = world.weight / total
        for move in moves:
            successor = board.copy(stack=False)
            successor.push(move)
            event = referee.observation(successor, side)
            world_events.append(event)
            if event == observed_after and len(next_worlds) <= MAX_HISTORIES:
                next_worlds.append(World(successor, weight / len(moves)))
        tables.append(features)
        events.append(world_events)
        weights.append(weight)
        for method, rho in methods.items():
            if method == "stockfish" and engine_odds is not None:
                probabilities = [engine_odds.get(move.uci(), engine_odds[OTHER]) for move in moves]
            elif rho is not None:
                probabilities = P2.predict(rho, features)
            else:
                probabilities = [1 / len(moves)] * len(moves)
            for move, event, probability in zip(moves, world_events, probabilities):
                action_mass[method][move.uci()] += weight * probability
                event_mass[method][event] += weight * probability
    for masses in (*action_mass.values(), *event_mass.values()):
        if not math.isclose(sum(masses.values()), 1.0, abs_tol=1e-9):
            raise ValueError("opponent action/event probability mass is not normalized")
    posterior, _, updated = P2.marginal_event_likelihood(
        STYLES, tables, events, observed_after, weights, [online[name] for name in STYLES],
    )
    return {"action": action_mass, "event": event_mass}, next_worlds, (
        P2.adapt(STYLE_PRIOR, posterior)
    ), updated


def unseen_king_attack(board: referee.FowBoard, move: chess.Move, side: chess.Color) -> int:
    board.push(move)
    try:
        king = board.king(side)
        attackers = board.attackers(not side, king)
        if not attackers:
            return 0
        view = referee.observation(board, side)
        return int(any(view[square] == "?" for square in attackers))
    finally:
        board.pop()


def king_forecasts(worlds: list[World], attempts: list[str], side: chess.Color,
                   seed: int) -> tuple[dict, dict]:
    """Compute exact and equal-root forecasts before choosing a replay action."""
    worlds = [world for world in worlds if continuing(world.board)]
    if not worlds:
        return {}, {}
    moves = [chess.Move.from_uci(action) for action in attempts]
    event_table = [[] for _ in moves]
    for world in worlds:
        if not set(moves).issubset(referee.fow_moves(world.board)):
            raise ValueError("hypothetical support contradicts observed attempts")
        for move, events in zip(moves, event_table):
            events.append(unseen_king_attack(world.board, move, side))
    weights = P1.normalize([world.weight for world in worlds])
    danger = [mean(events) for events in zip(*event_table)]
    sampled = {
        method: [P1.sample(weights, danger, ROOTS, alpha, seed + i)
                 for i in range(DRAW_REPETITIONS)]
        for method, alpha in (("posterior_draw", 0.0), ("threat_proposal", 0.30))
    }
    predictions = {}
    for move, events in zip(moves, event_table):
        predictions[move.uci()] = {
            "exact": sum(prob * event for prob, event in zip(weights, events)),
            **{method: [P1.expected_event(events, draw) for draw in draws]
               for method, draws in sampled.items()},
        }
    ess = {method: mean(draw["ess"] for draw in draws) for method, draws in sampled.items()}
    return predictions, ess


def retrospective_p1(forecasts: dict, ess: dict, action: str, truth_fen: str,
                     side: chess.Color, game: dict, worlds: list[World]) -> dict:
    probabilities = forecasts[action]
    truth = referee.FowBoard(truth_fen)
    key = referee.position_key(truth)
    outcome = unseen_king_attack(truth, chess.Move.from_uci(action), side)
    return {
        **row_ids(game),
        "event": outcome,
        "truth_supported": any(referee.position_key(world.board) == key for world in worlds),
        "exact_probability": probabilities["exact"],
        "exact": (probabilities["exact"] - outcome) ** 2,
        **{method: mean((p - outcome) ** 2 for p in probabilities[method]) for method in ess},
        **{f"{method}_mse_to_exact": mean((p - probabilities["exact"]) ** 2
                                         for p in probabilities[method]) for method in ess},
        **{f"{method}_ess": value for method, value in ess.items()},
    }


def retrospective_p2(forecasts: dict, action: str, event: str, policy: str,
                     game: dict) -> dict:
    row = {**row_ids(game), "target_policy": policy}
    for target, observed in (("action", action), ("event", event)):
        for method, probabilities in forecasts[target].items():
            probability = probabilities.get(observed, 0.0)
            if probability <= 0:
                raise ValueError("early opponent support omits the observed target")
            row[f"{method}_{target}_nll"] = -math.log(probability)
    return row


def early_replay(game: dict, replay: dict, rows: list[dict], labels: list[dict],
                 stockfish: OpponentPolicy | None = None,
                 stockfish_coverage: Counter | None = None) -> tuple:
    p1, p2 = [], []
    coverage = Counter()
    frames = replay["frames"]
    for side in (chess.WHITE, chess.BLACK):
        name = "white" if side else "black"
        worlds = initial_support()
        rho = STYLE_PRIOR.copy()
        for ply in range(min(EARLY_PLIES, len(rows))):
            own_turn = side == (ply % 2 == 0)
            # Final move is scored, but the terminal observation is not available
            # to the player under the protocol and cannot update style.
            if not own_turn and ply + 1 == len(rows):
                break
            after = frames[ply + 1][name]
            if own_turn:
                attempts = rows[ply]["online_inputs"]["legal_attempts"]
                seed = int(stage2_corpus.digest([game["game_id"], ply])[:14], 16)
                forecasts, ess = king_forecasts(worlds, attempts, side, seed)
                if not forecasts:
                    coverage["empty_support"] += 1
                    break
                label = labels[ply]
                action = label["selected_action"]
                p1.append(retrospective_p1(
                    forecasts, ess, action, label["truth_board_fen"], side, game, worlds,
                ))
                p1[-1]["sample_id"] = rows[ply]["sample_id"]
                worlds = on_own_action(worlds, action, side, after)
            else:
                forecasts, worlds, rho, updated = opponent_forecast(
                    worlds, side, rho, after, stockfish, stockfish_coverage,
                )
                if not forecasts or not updated:
                    coverage["empty_support"] += 1
                    break
                label = labels[ply]
                p2.append(retrospective_p2(forecasts, label["selected_action"], after,
                                          label["policy"], game))
                p2[-1]["sample_id"] = rows[ply]["sample_id"]
            if len(worlds) > MAX_HISTORIES:
                coverage["support_cap"] += 1
                break
    return p1, p2, coverage


def move_category(view: str, side: chess.Color, move: chess.Move) -> str:
    """A fixed view-geometry proxy, derived for each candidate without labels."""
    piece = view[move.from_square].lower()
    dest = move.to_square
    enemy = "pnbrqk" if side else "PNBRQK"
    if view[dest] in enemy or (piece == "p" and chess.square_file(move.from_square)
                              != chess.square_file(dest)):
        return "capture"
    neighborhood = chess.SquareSet(chess.BB_KING_ATTACKS[dest])
    exposed = sum(view[square] == "?" for square in neighborhood) >= 2
    if exposed and piece == "k":
        return "king-exposed"
    return "quiet-exposed" if exposed else "quiet-sheltered"


def retrospective_material_loss(board: referee.FowBoard, reply: chess.Move,
                                own_view: str) -> bool:
    """Realized immediate reply capturing an undefended N/B/R/Q from the fog."""
    victim = board.piece_at(reply.to_square)
    return bool(victim and victim.color != board.turn
                and victim.piece_type in (chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN)
                and own_view[reply.from_square] == "?"
                and not board.attackers(victim.color, reply.to_square))


def row_ids(game: dict) -> dict:
    return {"game_id": game["game_id"], "pair_block": game["pair_block"],
            "split": game["split"]}


def material_rows(game: dict, replay: dict, rows: list[dict],
                  labels: list[dict]) -> tuple[list[dict], Counter]:
    records = []
    excluded = Counter()
    frames = replay["frames"]
    for ply, (row, label) in enumerate(zip(rows, labels)):
        features = row["online_inputs"]
        name = features["side"]
        side = name == "white"
        categories = {
            action: move_category(features["view"], side, chess.Move.from_uci(action))
            for action in features["legal_attempts"]
        }
        # The last action has no observed reply. Terminal outcomes and the
        # corpus's artificial cap are censored, never counted as negative labels.
        if ply + 2 == len(frames):
            excluded[replay["reason"]] += 1
            continue
        action = label["selected_action"]
        board = referee.FowBoard(labels[ply + 1]["truth_board_fen"])
        reply = chess.Move.from_uci(frames[ply + 2]["move"])
        lost = retrospective_material_loss(board, reply, frames[ply + 1][name])
        records.append({
            **row_ids(game), "sample_id": row["sample_id"],
            "category": categories[action], "event": int(lost),
            "moved_piece_lost": bool(lost and reply.to_square == chess.Move.from_uci(action).to_square),
        })
    return records, excluded


def cluster_summary(rows: list[dict], candidate: str, baseline: str) -> dict:
    games = defaultdict(list)
    for row in rows:
        games[row["game_id"]].append(row)
    if not games:
        return {"decisions": 0, "games": 0, "complete_pairs": 0}
    game_scores = []
    for values in games.values():
        game_scores.append((values[0]["pair_block"], mean(row[candidate] for row in values),
                            mean(row[baseline] for row in values)))
    block_differences = defaultdict(list)
    for block, test, control in game_scores:
        block_differences[block].append(test - control)
    blocks = [mean(block) for block in block_differences.values() if len(block) == 2]
    interval = None
    if len(blocks) >= 2:
        rng = random.Random(7106)
        deltas = sorted(mean(rng.choices(blocks, k=len(blocks))) for _ in range(2000))
        interval = [deltas[49], deltas[1949]]
    return {
        "decisions": len(rows),
        "games": len(games),
        "complete_pairs": len(blocks),
        candidate: mean(test for _, test, _ in game_scores),
        baseline: mean(control for _, _, control in game_scores),
        "delta_95_paired_block_bootstrap": interval,
    }


def screen_p5(games: list[tuple]) -> dict:
    rows = []
    excluded = Counter()
    for game, replay, features, labels in games:
        records, censored = material_rows(game, replay, features, labels)
        rows.extend(records)
        excluded.update(censored)
    training = [(row["category"], row["event"]) for row in rows if row["split"] == "train"]
    model = P5.calibrate(training)
    baseline = mean(event for _, event in training)
    scores = {}
    for split in EVAL_SPLITS:
        test = [row for row in rows if row["split"] == split]
        for row in test:
            row["probability"] = P5.predict(model, row["category"])
            row["p5"] = (row["probability"] - row["event"]) ** 2
            row["train_rate"] = (baseline - row["event"]) ** 2
        quiet = [row for row in test if row["category"] != "capture"]
        scores[split] = {
            "noncapture": cluster_summary(quiet, "p5", "train_rate"),
            "by_class": {
                category: cluster_summary([row for row in test if row["category"] == category],
                                          "p5", "train_rate")
                for category in P5.CATEGORIES
            },
            "events": sum(row["event"] for row in test),
            "noncapture_events": sum(row["event"] for row in quiet),
            "moved_piece_events": sum(row["moved_piece_lost"] for row in test),
            "standing_piece_events": sum(row["event"] - row["moved_piece_lost"] for row in test),
            "event_rates_by_class": {
                category: {"n": sum(row["category"] == category for row in test),
                           "events": sum(row["event"] for row in test if row["category"] == category)}
                for category in P5.CATEGORIES
            },
        }
    return {
        "status": "screened",
        "dataset": CORPUS_NAME,
        "metric": "Game-averaged Brier score of next-reply unseen capture of undefended N/B/R/Q after our action",
        "training_decisions": len(training),
        "training_events": sum(event for _, event in training),
        "train_baseline_probability": baseline,
        "trained_event_probabilities": model,
        "censored_no_reply": dict(excluded),
        "splits": scores,
        "decision_records": rows,
        "limits": "Synthetic on-policy actions and the immediate observed reply only. Feature is predecision view geometry, not a belief/engine-conditioned estimate. No counterfactual, net recapture value, engine double-counting test, or game-strength result.",
    }


def run(corpus: Path, stockfish: Path | None = None) -> dict:
    if stockfish is None:
        return run_with_policy(corpus, None, "Stockfish not available for this invocation.")
    stockfish = stockfish.resolve(strict=True)
    pool = EnginePool.start([str(stockfish)], 1, monotonic() + 5, cwd=str(stockfish.parent))
    try:
        if not pool.ready_count():
            return run_with_policy(corpus, None, f"Stockfish did not start: {pool.failure}")
        return run_with_policy(corpus, OpponentPolicy(pool), None)
    finally:
        pool.close()


def run_with_policy(corpus: Path, engine: OpponentPolicy | None,
                    stockfish_blocker: str | None) -> dict:
    games = load_games(corpus)
    p1, p2, coverage = [], [], Counter()
    stockfish_coverage = Counter()
    started = process_time()
    eligible_p1 = eligible_p2 = 0
    for game, replay, features, labels in games:
        if game["split"] not in EVAL_SPLITS:
            continue
        early = min(EARLY_PLIES, len(features))
        eligible_p1 += early
        eligible_p2 += min(EARLY_PLIES, len(features) - 1)
        belief_rows, style_rows, stopped = early_replay(
            game, replay, features, labels, engine, stockfish_coverage,
        )
        p1.extend(belief_rows)
        p2.extend(style_rows)
        coverage.update(stopped)
    early_cpu = process_time() - started
    belief_splits, style_splits = {}, {}
    for split in EVAL_SPLITS:
        belief = [row for row in p1 if row["split"] == split]
        style = [row for row in p2 if row["split"] == split]
        belief_splits[split] = {
            "brier": cluster_summary(belief, "threat_proposal", "posterior_draw"),
            "exact_posterior_brier": cluster_summary(belief, "exact", "posterior_draw"),
            "mse_to_exact": cluster_summary(belief, "threat_proposal_mse_to_exact",
                                            "posterior_draw_mse_to_exact"),
            "mean_ess": {method: mean(row[f"{method}_ess"] for row in belief)
                         for method in ("posterior_draw", "threat_proposal")} if belief else {},
            "positive_labels": sum(row["event"] for row in belief),
            "nonzero_posterior_risk": sum(row["exact_probability"] > 0 for row in belief),
            "truth_board_supported": sum(row["truth_supported"] for row in belief),
        }
        style_splits[split] = {
            target: {
                control: cluster_summary(style, f"online_{target}_nll", f"{control}_{target}_nll")
                for control in ("static", "uniform", "stockfish") if control != "stockfish" or engine
            }
            for target in ("action", "event")
        }
        if split == "opponent_shift":
            pressure = [row for row in style if row["target_policy"] == "king_pressure"]
            style_splits[split]["shift_actor_only"] = {
                target: {
                    control: cluster_summary(pressure, f"online_{target}_nll", f"{control}_{target}_nll")
                    for control in ("static", "uniform", "stockfish") if control != "stockfish" or engine
                }
                for target in ("action", "event")
            }
    bounds = {
        "early_plies": EARLY_PLIES, "history_cap": MAX_HISTORIES,
        "sampled_roots_per_draw": ROOTS, "replicated_draws_per_decision": DRAW_REPETITIONS,
        "truncated_player_histories": dict(coverage), "combined_cpu_seconds": early_cpu,
    }
    return {
        "P1": {
            "status": "blocked" if not any(row["event"] for row in p1) else "screened",
            "dataset": CORPUS_NAME,
            "metric": "Early replay, game-averaged unseen king-attack Brier at 64 roots",
            "eligible_early_decisions": eligible_p1,
            "scored_decisions": len(p1),
            "bounds": bounds,
            "splits": belief_splits,
            "decision_records": p1,
            "limits": "Bounded uniform legal-history support, rather than the weighted eBotI posterior. No paired Stockfish-call comparison, repaired states, held-out competitive histories or full-game result. A lack of positive or nonzero risk rows is insufficient to test calibration.",
        },
        "P2": {
            "status": "screened",
            "dataset": CORPUS_NAME,
            "metric": "Game-averaged action and observed transition NLL on early opponent moves",
            "eligible_early_decisions": eligible_p2,
            "scored_decisions": len(p2),
            "bounds": bounds,
            "splits": style_splits,
            "decision_records": p2,
            "stockfish_world_coverage": dict(stockfish_coverage),
            "stockfish_blocker": stockfish_blocker,
            "limits": "Uniform observation-consistent history support fixed across policies. Stockfish, when configured, uses the existing depth-one opponent policy with uniform fallback for unanswered worlds. Competitive opponent validation remains unrun. Observed-view equivalence sets update style, with hidden actions and policy identity used only for retrospective scoring.",
        },
        "P5": screen_p5(games),
    }
