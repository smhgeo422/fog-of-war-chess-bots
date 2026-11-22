"""Stage 4 replay screens for P7 continuation value and P8 computation allocation.

Both are restricted early-game diagnostics on the Stage 2 synthetic replay split.
Replays provide observation histories and retrospective labels through separate paths.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from hashlib import file_digest
import json
import math
from pathlib import Path
import random
from statistics import mean

import chess
import chess.engine
import fow  # noqa: F401 (puts starter on sys.path)
import referee
from bots.eBotI.eBotI.belief import Belief
from bots.eBotI.eBotI.engine import cp_value, mate_value
from bots.eBotI.eBotI.evaluation import evaluate
from tools.stage2_corpus import score
from tools.stage3 import P7, P8


P7_PLIES = (2, 3, 4, 5)
P8_PLIES = (3, 4, 5)
HORIZON = 6
BELIEF_CAP = 128
P7_ROOTS = 4
P8_INITIAL = 4
P8_REFERENCE = 12
P8_CANDIDATES = 4
NODES = 256
RIDGES = (0.02, 0.2, 2.0, 20.0)
SEED = 74078
SHADOW_PRICE = 0.001
SPLITS = ("train", "development", "holdout", "opponent_shift")
MATERIAL = {"p": 1, "n": 3, "b": 3, "r": 5, "q": 9}


def _jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def _exact_histories(frames, side, key, last_ply):
    """Update the existing belief from this side's views and previously own moves."""
    belief = Belief(side, max_states=BELIEF_CAP, rng=random.Random(key))
    belief.observe(frames[0]["white" if side else "black"])
    for ply in range(1, min(last_ply, len(frames) - 1) + 1):
        last_mover = chess.WHITE if ply % 2 else chess.BLACK
        own_move = chess.Move.from_uci(frames[ply]["move"]) if last_mover == side else None
        belief.observe(frames[ply]["white" if side else "black"], own_move=own_move)
        if not belief.exact:
            return
        if side == (chess.WHITE if ply % 2 == 0 else chess.BLACK):
            yield ply, tuple(belief.states)


def _target(replay, ply, side):
    """Logged-policy six-ply material/terminal utility from this side's perspective."""
    last = len(replay["frames"]) - 1
    end = min(last, ply + HORIZON)
    if end == last:
        if replay["reason"] == "Synthetic ply cap":
            if ply + HORIZON > last:
                return None
        else:
            result = replay["result"]
            if result == "1/2-1/2":
                return 0.0
            return 1.0 if result == ("1-0" if side else "0-1") else -1.0
    board = replay["frames"][end]["board"]
    advantage = sum(MATERIAL.get(c.lower(), 0) * (1 if c.isupper() == side else -1) for c in board)
    return math.tanh(advantage / 5)


@contextmanager
def _scorer(stockfish):
    if stockfish is None:
        yield _material_value
        return
    binary = stockfish.resolve()
    with chess.engine.SimpleEngine.popen_uci(str(binary), timeout=15, cwd=binary.parent) as engine:
        engine.configure({"Threads": 1, "Hash": 16})

        def value(board, move):
            child = board.copy(stack=False)
            child.push(move)
            terminal = _terminal_value(child, board.turn)
            if terminal is not None:
                return terminal, 0
            orthodox = chess.Board(child.fen(en_passant="fen"))
            if not orthodox.is_valid():
                raise ValueError(f"invalid orthodox engine child: {orthodox.fen()}")
            info = engine.analyse(orthodox, chess.engine.Limit(nodes=NODES), game=object())
            pov = info["score"].pov(board.turn)
            result = mate_value(pov.mate()) if pov.is_mate() else cp_value(pov.score())
            return result, info["nodes"]

        yield value


def _terminal_value(child, side):
    terminal = referee.outcome(child, Counter({referee.position_key(child): 1}))
    if terminal is None:
        return None
    if terminal[0] == "1/2-1/2":
        return 0.0
    return 1.0 if terminal[0] == ("1-0" if side else "0-1") else -1.0


def _material_value(board, move):
    child = board.copy(stack=False)
    child.push(move)
    terminal = _terminal_value(child, board.turn)
    return (evaluate(child, board.turn) if terminal is None else terminal), 0


@dataclass(frozen=True)
class Continuation:
    sample_id: str
    pair: int
    features: tuple[float, ...]
    baseline: float
    target: float
    roots: int
    nodes: int

    @property
    def design(self):
        return self.features, self.baseline, self.target


def _continuation(replay, row, label, states, pair, value):
    ply = row["ply"]
    side = row["online_inputs"]["side"] == "white"
    target = _target(replay, ply, side)
    if target is None:
        return None
    if label["selected_action"] not in row["online_inputs"]["legal_attempts"]:
        raise ValueError("logged action absent from own candidate set")
    features = P7.featurize(row["online_inputs"])
    move = chess.Move.from_uci(label["selected_action"])
    sample = random.Random(f"{SEED}:{row['sample_id']}:P7").sample(
        states, min(P7_ROOTS, len(states)))
    if not all(move in referee.fow_moves(board) for board in sample):
        return None
    values, nodes = zip(*(value(board, move) for board in sample), strict=True)
    return Continuation(row["sample_id"], pair, features, mean(values), target,
                        len(sample), sum(nodes))


def _means(rows):
    return tuple(mean(column) for column in zip(*rows, strict=True))


def _action(values):
    return max(range(len(values)), key=values.__getitem__)


def _marginal_voc(initial):
    """Empirical martingale forecast from initial sampled results only."""
    current = dict(enumerate(_means(initial)))
    count = len(initial)
    outcomes = [
        (1 / count, {i: (count * old + outcome[i]) / (count + 1)
                     for i, old in current.items()})
        for outcome in initial
    ]
    decision = P8.select(current, {"root": {"outcomes": outcomes, "duration": 1}},
                         remaining_seconds=2, reserve_seconds=1, price=SHADOW_PRICE)
    voc = P8.value_of_computation(current, outcomes, duration=1, price=SHADOW_PRICE)
    return decision["decision"] == "compute", voc["expected_decision_gain"]


def _trace(row, states, pair, value):
    # Skip exact supports too small to both add an unseen root and form a reference.
    if len(states) <= P8_INITIAL + 1:
        return None
    rng = random.Random(f"{SEED}:{row['sample_id']}:P8")
    roots = rng.sample(states, min(P8_REFERENCE, len(states)))
    legal = set(referee.fow_moves(states[0]))
    for board in states[1:]:
        legal.intersection_update(referee.fow_moves(board))
    online = row["online_inputs"]
    candidates = [chess.Move.from_uci(uci) for uci in online["legal_attempts"]]
    candidates = [move for move in candidates if move in legal]
    if len(candidates) < P8_CANDIDATES:
        return None
    rng.shuffle(candidates)
    candidates.sort(key=lambda move: -score(move, online["view"], states[0].turn,
                                           "visible_capture"))
    candidates = candidates[:P8_CANDIDATES]
    scores = [[value(board, move) for move in candidates] for board in roots]
    rows = [tuple(score for score, _ in root) for root in scores]
    initial = rows[:P8_INITIAL]
    adapt, gain = _marginal_voc(initial)
    fixed_action = _action(_means(initial))
    extra_action = _action(_means(rows[:P8_INITIAL + 1]))
    reference = _means(rows)
    best = max(reference)
    return {
        "sample_id": row["sample_id"], "pair": pair,
        "candidate_actions": [move.uci() for move in candidates],
        "initial_action": candidates[fixed_action].uci(),
        "extra_action": candidates[extra_action].uci(),
        "predicted_gain": gain, "adapt": adapt, "reference_roots": len(roots),
        "regret_initial": best - reference[fixed_action],
        "regret_extra": best - reference[extra_action],
        "initial_nodes": sum(nodes for root in scores[:P8_INITIAL] for _, nodes in root),
        "extra_nodes": sum(nodes for _, nodes in scores[P8_INITIAL]),
    }


def _block_means(pairs, values):
    grouped = defaultdict(list)
    for pair, value in zip(pairs, values, strict=True):
        grouped[pair].append(value)
    return [mean(values) for _, values in sorted(grouped.items())]


def _clustered(pairs, differences):
    means = _block_means(pairs, differences)
    if not means:
        return {"pairs": 0, "difference": None, "exploratory_95pct_bootstrap": None}
    rng = random.Random(SEED)
    draws = sorted(mean(rng.choices(means, k=len(means))) for _ in range(2000))
    return {"pairs": len(means), "difference": mean(means),
            "exploratory_95pct_bootstrap": [draws[50], draws[1949]] if len(means) >= 2 else None}


def _cluster_mean(rows, values):
    return mean(_block_means((row.pair for row in rows), values))


def _p7(splits):
    if not all(splits[split] for split in SPLITS):
        return {"status": "blocked", "reason": "No eligible exact-prefix rows in at least one split."}
    train = [row.design for row in splits["train"]]
    dev = splits["development"]
    models = {alpha: P7.fit(train, alpha) for alpha in RIDGES}
    chosen = min(RIDGES, key=lambda alpha: _cluster_mean(dev, [
        (P7.predict(row.features, row.baseline, models[alpha]) - row.target) ** 2
        for row in dev]))
    model = models[chosen]
    intercept = P7.fit([((1.0,), baseline, target) for _, baseline, target in train], chosen)
    residuals = [target - baseline for _, baseline, target in train]
    random.Random(SEED).shuffle(residuals)
    shuffled = P7.fit([
        (x, baseline, max(-1.0, min(1.0, baseline + residual)))
        for (x, baseline, _), residual in zip(train, residuals, strict=True)
    ], chosen)
    out = {
        "status": "restricted_diagnostic", "ridge": chosen,
        "coefficients": dict(zip(P7.FEATURES, model, strict=True)),
        "split_rows": {name: len(rows) for name, rows in splits.items()},
        "metric": "Equal color-pair-block weight MSE of six-ply logged-policy utility",
        "split_results": {},
    }
    for name in ("holdout", "opponent_shift"):
        rows = splits[name]
        evaluated = [
            {"sample_id": row.sample_id, "pair": row.pair,
             "target": row.target, "baseline": row.baseline,
             "residual": P7.predict(row.features, row.baseline, model),
             "intercept": P7.predict((1.0,), row.baseline, intercept),
             "shuffled": P7.predict(row.features, row.baseline, shuffled),
             "roots": row.roots, "nodes": row.nodes}
            for row in rows
        ]
        losses = {
            method: [(entry[method] - entry["target"]) ** 2 for entry in evaluated]
            for method in ("baseline", "residual", "intercept", "shuffled")
        }
        out["split_results"][name] = {
            "block_mean_mse": {method: _cluster_mean(rows, errors)
                               for method, errors in losses.items()},
            "residual_minus_baseline": _clustered(
                [row.pair for row in rows],
                [a - b for a, b in zip(losses["residual"], losses["baseline"], strict=True)]),
            "decisions": evaluated,
        }
    return out


def _p8(splits):
    out = {"status": "restricted_diagnostic", "split_results": {},
           "metric": "Equal color-pair-block weight action regret against the shared larger root sample",
           "initial_roots": P8_INITIAL, "maximum_reference_roots": P8_REFERENCE,
           "actions_per_decision": P8_CANDIDATES, "shadow_price_per_root": SHADOW_PRICE}
    for name, rows in splits.items():
        if not rows:
            out["split_results"][name] = {"status": "blocked", "reason": "No eligible root traces."}
            continue
        extra_count = sum(row["adapt"] for row in rows)
        random_slots = set(random.Random(f"{SEED}:{name}:fixed").sample(range(len(rows)), extra_count))
        compared = [
            row | {"fixed_extra": i in random_slots,
                   "adaptive_regret": row["regret_extra" if row["adapt"] else "regret_initial"],
                   "fixed_regret": row["regret_extra" if i in random_slots else "regret_initial"]}
            for i, row in enumerate(rows)
        ]
        differences = [row["adaptive_regret"] - row["fixed_regret"] for row in compared]
        pairs = [row["pair"] for row in compared]
        always = sum(row["initial_nodes"] for row in rows)
        nodes = {
            "adaptive": always + sum(row["extra_nodes"] for row in compared if row["adapt"]),
            "fixed": always + sum(row["extra_nodes"] for row in compared if row["fixed_extra"]),
        }
        out["split_results"][name] = {
            "n": len(compared), "extra_slots_each": extra_count,
            "root_evaluations_each": len(rows) * P8_INITIAL + extra_count,
            "actual_reported_engine_nodes": nodes,
            "adaptive_mean_regret": mean(_block_means(pairs, (row["adaptive_regret"] for row in compared))),
            "fixed_mean_regret": mean(_block_means(pairs, (row["fixed_regret"] for row in compared))),
            "adaptive_minus_fixed": _clustered(pairs, differences),
            "decisions": compared,
        }
    return out


def run(corpus: Path, stockfish: Path | None = None) -> dict:
    games = json.loads((corpus / "game_registry.json").read_text())
    p7 = {name: [] for name in SPLITS}
    p8 = {name: [] for name in ("holdout", "opponent_shift")}
    attempted = {name: Counter() for name in SPLITS}
    with _scorer(stockfish) as value:
        for split in SPLITS:
            observations = defaultdict(dict)
            labels = {}
            feature_rows = _jsonl(corpus / "observations" / (split + ".jsonl"))
            label_rows = _jsonl(corpus / "retrospective_labels" / (split + ".jsonl"))
            for row, label in zip(feature_rows, label_rows, strict=True):
                if row["sample_id"] != label["sample_id"] or label["retrospective_only"] is not True:
                    raise ValueError("Stage 2 observation/retrospective label misalignment")
                observations[row["game_id"]][row["ply"]] = row
                labels[row["sample_id"]] = label
            for game in games:
                if game["split"] != split:
                    continue
                replay = json.loads((corpus / game["replay"]).read_text())
                frames = replay["frames"]
                rows = observations[game["game_id"]]
                prefix = {ply: states for side in chess.COLORS for ply, states in
                          _exact_histories(frames, side, game["game_id"], max(P7_PLIES))}
                pair = game["pair_block"]
                for ply in P7_PLIES:
                    if ply not in rows:
                        continue
                    attempted[split]["p7_rows"] += 1
                    if ply not in prefix:
                        attempted[split]["p7_nonexact"] += 1
                        continue
                    row = rows[ply]
                    entry = _continuation(replay, row, labels[row["sample_id"]], prefix[ply], pair, value)
                    if entry is not None:
                        p7[split].append(entry)
                    else:
                        attempted[split]["p7_unavailable_action_or_target"] += 1
                if split in p8:
                    for ply in P8_PLIES:
                        if ply not in rows:
                            continue
                        attempted[split]["p8_rows"] += 1
                        if ply not in prefix:
                            attempted[split]["p8_nonexact"] += 1
                            continue
                        row = rows[ply]
                        entry = _trace(row, prefix[ply], pair, value)
                        if entry is not None:
                            p8[split].append(entry)
                        else:
                            attempted[split]["p8_insufficient_roots_or_candidates"] += 1
    digest = None
    if stockfish is not None:
        with stockfish.open("rb") as binary:
            digest = file_digest(binary, "sha256").hexdigest()
    engine = {
        "evaluator": "Stockfish on candidate child positions" if stockfish else "eBotI fallback evaluator",
        "binary_sha256": digest,
        "analysis_node_limit": NODES if stockfish else None,
        "threads": 1 if stockfish else None,
    }
    return {
        "P7": _p7(p7) | {
            "engine": engine, "attempted": attempted, "plies": P7_PLIES,
            "primary_endpoint_status": "partial",
            "target": "Bounded material utility after six plies from logged action, with terminal outcomes",
            "limitations": [
                "Synthetic starter policies, opening positions, exact unweighted early belief prefixes only.",
                "Stockfish diagnostic, when present, is a restricted sampled-belief reference with capped nodes, rather than the full pinned playing-bot search.",
                "Only the logged action has an observed continuation. The shared view-level correction does not yield validated alternative-action values.",
            ],
        },
        "P8": _p8(p8) | {
            "engine": engine, "attempted": attempted, "plies": P8_PLIES,
            "primary_endpoint_status": "partial",
            "limitations": [
                "No wall-clock pacing or forfeit accounting in the synthetic corpus.",
                "Equal root-evaluation counts and nominal node caps, with actual engine-node counts reported separately.",
                "Empirical forecast and overlapping larger-sample reference on early beliefs and four candidate actions.",
                "Offline random extra-slot allocation is a matched-count control, rather than a live reserve-clock policy.",
            ],
        },
    }
