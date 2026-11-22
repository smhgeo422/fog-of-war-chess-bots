"""P8 v2 slot allocation from independent, referee-derived engine traces."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from hashlib import file_digest, sha256
import json
import math
from pathlib import Path
import random
from statistics import mean
from time import perf_counter_ns, process_time_ns

import chess
import fow  # noqa: F401 (puts starter on sys.path)
import referee
from tools.stage2_corpus import score
from tools.stage3 import P8
from tools.stage4.compute import (
    BELIEF_CAP, NODES, P8_CANDIDATES, P8_INITIAL, SHADOW_PRICE,
    _action, _block_means, _exact_histories, _jsonl, _means, _scorer,
)


CORPUS_SEEDS = (75101, 75102, 75103, 75104)
PLIES = (2, 3, 4, 5, 6, 7)
SPLITS = ("holdout", "opponent_shift")
MIN_REFERENCE = 6
MAX_REFERENCE = 16
SEED = 87211
RANDOM_CONTROLS = 16
BOOTSTRAPS = 2000


def _forecast_voc(samples, initial_count):
    means = dict(enumerate(_means(samples)))
    outcomes = [
        (1 / len(samples),
         {i: (initial_count * value + sample[i]) / (initial_count + 1)
          for i, value in means.items()})
        for sample in samples
    ]
    return P8.value_of_computation(means, outcomes, duration=1,
                                   price=SHADOW_PRICE)["expected_decision_gain"]


def _scores(initial):
    """v2 discounts the plug-in VOC when it depends heavily on any one root."""
    count = len(initial)
    raw = _forecast_voc(initial, count)
    omission = [_forecast_voc(initial[:i] + initial[i + 1:], count) for i in range(count)]
    omission_mean = mean(omission)
    se = math.sqrt((count - 1) / count * sum((value - omission_mean) ** 2 for value in omission))
    top, second = sorted(_means(initial), reverse=True)[:2]
    return {"voc_raw": raw, "voc_jackknife_se": se, "voc_v2": max(0.0, raw - se),
            "v2_clipped": raw < se, "initial_margin": top - second,
            "v1_eligible": raw > SHADOW_PRICE}


@dataclass(frozen=True)
class RootScore:
    root_sha256: str
    values: tuple[float, ...]
    nodes: tuple[int, ...]
    elapsed_ns: int


def _engine_row(board, moves, value):
    started = perf_counter_ns()
    values, nodes = zip(*(value(board, move) for move in moves), strict=True)
    elapsed = perf_counter_ns() - started
    root = sha256(board.fen(en_passant="fen").encode()).hexdigest()
    return RootScore(root, values, nodes, elapsed)


def _trace(row, states, seed, pair, value):
    """Use a common candidate set and keep the evaluator and reference roots disjoint."""
    evaluated = P8_INITIAL + 1
    if len(states) < evaluated + MIN_REFERENCE:
        return None, "insufficient_disjoint_support"
    rng = random.Random(f"{SEED}:{seed}:{row['sample_id']}:roots")
    legal = set(referee.fow_moves(states[0]))
    for state in states[1:]:
        legal.intersection_update(referee.fow_moves(state))
    online = row["online_inputs"]
    picks = [chess.Move.from_uci(uci) for uci in online["legal_attempts"]]
    candidates = [move for move in picks if move in legal]
    if len(candidates) < P8_CANDIDATES:
        return None, "insufficient_common_actions"
    rng.shuffle(candidates)
    side = online["side"] == "white"
    candidates.sort(key=lambda move: -score(move, online["view"], side, "visible_capture"))
    moves = candidates[:P8_CANDIDATES]
    count = min(len(states), evaluated + MAX_REFERENCE)
    roots = [_engine_row(board, moves, value) for board in rng.sample(states, count)]
    initial = roots[:P8_INITIAL]
    extra = roots[P8_INITIAL]
    reference = roots[evaluated:]
    if {root.root_sha256 for root in roots[:evaluated]} & {root.root_sha256 for root in reference}:
        raise ValueError("engine evaluation and reference roots overlap")
    start = process_time_ns()
    decisions = _scores([root.values for root in initial])
    overhead = process_time_ns() - start
    immediate = _action(_means([root.values for root in initial]))
    after_extra = _action(_means([root.values for root in roots[:evaluated]]))
    reference_values = _means([root.values for root in reference])
    best = max(reference_values)
    return {
        "sample_id": row["sample_id"], "corpus_seed": seed, "pair": pair,
        "history_sha256": online["own_history_sha256"],
        "ply": row["ply"], "support_size": len(states), "candidates": [m.uci() for m in moves],
        **decisions, "controller_cpu_ns": overhead,
        "initial_choice": moves[immediate].uci(), "extra_choice": moves[after_extra].uci(),
        "initial_regret": best - reference_values[immediate],
        "extra_regret": best - reference_values[after_extra],
        "initial_nodes": sum(sum(root.nodes) for root in initial),
        "extra_nodes": sum(extra.nodes),
        "initial_elapsed_ns": sum(root.elapsed_ns for root in initial),
        "extra_elapsed_ns": extra.elapsed_ns,
        "initial_roots": [asdict(root) for root in initial],
        "extra_root": asdict(extra), "reference_roots": [asdict(root) for root in reference],
        "reference_values": reference_values,
    }, None


def _gather(corpus, seed, split, value):
    by_game = defaultdict(dict)
    for row in _jsonl(corpus / "observations" / (split + ".jsonl")):
        if row["ply"] in PLIES:
            by_game[row["game_id"]][row["ply"]] = row
    registry = json.loads((corpus / "game_registry.json").read_text())
    rows, coverage = [], Counter()
    for game in registry:
        if game["split"] != split:
            continue
        coverage["games"] += 1
        game_id = game["game_id"]
        replay = json.loads((corpus / game["replay"]).read_text())
        histories = {ply: states for side in chess.COLORS for ply, states in
                     _exact_histories(replay["frames"], side, game_id, max(PLIES))}
        for ply, row in by_game[game_id].items():
            coverage["offered"] += 1
            if ply not in histories:
                coverage["nonexact_prefix"] += 1
                continue
            result, reason = _trace(row, histories[ply], seed, game["pair_block"], value)
            if reason is not None:
                coverage[reason] += 1
            else:
                rows.append(result)
                coverage["scored"] += 1
    return rows, dict(coverage)


def _allocate(rows, seed, split):
    if not rows:
        return {}
    count = max(1, len(rows) // 4)
    rng = random.Random(f"{SEED}:{seed}:{split}:slot-ties")
    stable_order = rng.sample(range(len(rows)), len(rows))

    def slots(key):
        return set(sorted(stable_order, key=key, reverse=True)[:count])

    return {
        "v2_shrunk_voc": slots(lambda i: rows[i]["voc_v2"]),
        "v1_threshold_matched": slots(lambda i: rows[i]["v1_eligible"]),
        "raw_voc_rank": slots(lambda i: rows[i]["voc_raw"]),
        "margin_rank": slots(lambda i: -rows[i]["initial_margin"]),
        **{f"fixed_random_{rep}": set(random.Random(
            f"{SEED}:{seed}:{split}:fixed:{rep}").sample(range(len(rows)), count))
           for rep in range(RANDOM_CONTROLS)},
    }


def _interval(rows, differences):
    by_seed = defaultdict(list)
    for row, change in zip(rows, differences, strict=True):
        by_seed[row["corpus_seed"]].append((row["pair"], change))
    groups = [_block_means((x[0] for x in items), (x[1] for x in items))
              for _, items in sorted(by_seed.items())]
    blocks = [value for group in groups for value in group]
    rng = random.Random(SEED)
    draws = sorted(mean(value for group in groups for value in rng.choices(group, k=len(group)))
                   for _ in range(BOOTSTRAPS))
    return {
        "pairs": len(blocks), "delta": mean(blocks),
        "better_pairs": sum(value < -1e-12 for value in blocks),
        "worse_pairs": sum(value > 1e-12 for value in blocks),
        "tied_pairs": sum(abs(value) <= 1e-12 for value in blocks),
        "exploratory_95pct_bootstrap": [draws[50], draws[1949]] if len(blocks) >= 2 else None,
    }


def _summary(by_seed, split):
    rows = []
    quotas = {}
    for seed, records in sorted(by_seed.items()):
        allocation = _allocate(records, seed, split)
        quotas[seed] = len(allocation.get("v2_shrunk_voc", ()))
        rows.extend(row | {"extra_policies": [name for name, ids in allocation.items() if i in ids]}
                    for i, row in enumerate(records))
    if not rows:
        return {"status": "blocked", "reason": "No eligible exact histories with disjoint reference roots."}
    arms = tuple(_allocate([rows[0]], int(rows[0]["corpus_seed"]), split))
    pairs = [(row["corpus_seed"], row["pair"]) for row in rows]

    def losses(name):
        return [row["extra_regret" if name in row["extra_policies"] else "initial_regret"] for row in rows]

    costs = {}
    base_nodes = sum(row["initial_nodes"] for row in rows)
    base_wall = sum(row["initial_elapsed_ns"] for row in rows)
    for name in arms:
        extra = [row for row in rows if name in row["extra_policies"]]
        costs[name] = {
            "block_mean_regret": mean(_block_means(pairs, losses(name))),
            "engine_nodes": base_nodes + sum(row["extra_nodes"] for row in extra),
            "trace_engine_wall_ms": (base_wall + sum(row["extra_elapsed_ns"] for row in extra)) / 1e6,
        }
    reference_sizes = [len(row["reference_roots"]) for row in rows]
    v2 = losses("v2_shrunk_voc")
    contrasts = {name: _interval(rows, [a - b for a, b in zip(v2, losses(name), strict=True)])
                 for name in arms if name != "v2_shrunk_voc"
                 and not name.startswith("fixed_random_")}
    random_arms = [name for name in arms if name.startswith("fixed_random_")]
    mean_random = _means([losses(name) for name in random_arms])
    contrasts["fixed_random_mean"] = _interval(
        rows, [a - b for a, b in zip(v2, mean_random, strict=True)])
    return {
        "status": "screened", "n": len(rows), "quotas": quotas,
        "distinct_observed_histories": len({row["history_sha256"] for row in rows}),
        "evaluated_roots_per_policy": P8_INITIAL * len(rows) + sum(quotas.values()),
        "reference_roots": {"min": min(reference_sizes), "mean": mean(reference_sizes),
                            "max": max(reference_sizes), "overlap": 0},
        "controller_cpu_us_mean": mean(row["controller_cpu_ns"] for row in rows) / 1000,
        "v1_natural_extra_slots": sum(row["v1_eligible"] for row in rows),
        "v2_clipped": sum(row["v2_clipped"] for row in rows),
        "v2_extra_overlap": {name: sum("v2_shrunk_voc" in row["extra_policies"]
                                       and name in row["extra_policies"] for row in rows)
                             for name in ("v1_threshold_matched", "raw_voc_rank", "margin_rank")},
        "policies": costs, "v2_minus_comparators": contrasts, "decisions": rows,
    }


def run(corpora: dict[int, Path], stockfish: Path) -> dict:
    if tuple(sorted(corpora)) != CORPUS_SEEDS:
        raise ValueError("P8 Stage 5 requires all four predeclared independent seeds")
    for seed, corpus in corpora.items():
        manifest = json.loads((corpus / "corpus_manifest.json").read_text())
        if manifest["schema"] != 2 or manifest["seed"] != seed:
            raise ValueError(f"P8 unexpected schema or seed for corpus {seed}")
    results = {}
    with _scorer(stockfish) as value:
        for split in SPLITS:
            by_seed, coverage = {}, {}
            for seed, corpus in sorted(corpora.items()):
                by_seed[seed], coverage[seed] = _gather(corpus, seed, split, value)
            results[split] = _summary(by_seed, split) | {"coverage": coverage}
    histories = {split: {row["history_sha256"] for row in results[split].get("decisions", [])}
                 for split in SPLITS}
    primary = None
    if results["holdout"]["status"] == "screened":
        contrast = results["holdout"]["v2_minus_comparators"]["v1_threshold_matched"]
        primary = {"name": "holdout_v2_minus_v1_matched_quota_regret",
                   "value": contrast["delta"], "n": contrast["pairs"],
                   "unit": "color-pair blocks"}
    with stockfish.open("rb") as binary:
        executable_hash = file_digest(binary, "sha256").hexdigest()
    return {
        "project": "P8", "variant": "v2-jackknife-voc-ranking",
        "status": "restricted_diagnostic" if results["holdout"]["status"] == "screened" else "blocked",
        "hypothesis": "Down-weighting one-root-sensitive VOC improves held-out slot allocation at the same quota.",
        "primary_metric": primary,
        "parameters": {
            "corpus_seeds": CORPUS_SEEDS, "random_seed": SEED, "plies": PLIES,
            "belief_cap": BELIEF_CAP, "initial_roots": P8_INITIAL, "optional_roots": 1,
            "reference_roots_min": MIN_REFERENCE, "reference_roots_max": MAX_REFERENCE,
            "candidate_moves": P8_CANDIDATES, "nodes_per_action": NODES,
            "shadow_price": SHADOW_PRICE, "slots": "max(1, floor(n/4)) separately per seed/split",
            "stockfish_sha256": executable_hash, "threads": 1,
            "fixed_random_controls": RANDOM_CONTROLS,
        },
        "split_results": results,
        "common_observed_histories_across_splits": len(histories["holdout"] & histories["opponent_shift"]),
        "limitations": [
            "Synthetic starter-policy openings and exact-support subset, with a common four-action shortlist.",
            "Offline quota can compare slots across decisions. Live allocation, protocol reserve and clock forfeits remain open.",
            "Reference worlds are disjoint but share one engine, candidate set and position support with the intervention.",
            "Root evaluation counts are matched. Actual engine nodes and traced wall time are reported by arm.",
            "Controller CPU timings and engine wall timings are measurements of trace generation, not isolated live phase budgets.",
        ],
    }
