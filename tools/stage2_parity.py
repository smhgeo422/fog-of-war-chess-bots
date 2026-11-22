"""Stage 2: fixed B0/B1/B2 profile, component equivalence and live action-parity probe.

Never modify the frozen bot. Functional equivalence is a test hypothesis, not
a consequence of matching environment flags.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import importlib
import json
import os
from pathlib import Path
import random
import select
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import fow  # noqa: F401,E402
import chess  # noqa: E402
import numpy as np  # noqa: E402
import referee  # noqa: E402
from uniform_random import ObservationTracker  # noqa: E402

B0 = "obscuro_v4"
B1 = "eBotI"
B2 = "eBotI"
B1_ENV = {
    "FOW_SAFE_FIRST": "0", "FOW_EXACT_RISK": "0", "FOW_ATTACKED": "6",
    "FOW_HANG": "0", "FOW_CLOCK": "v4", "FOW_BOOK": "none",
    "FOW_ROOTS": "64", "FOW_SCAN": "256", "FOW_DEPTH": "12",
    "FOW_SLICE": "1.0", "FOW_RISK_UNIFORM": "0", "FOW_TIME": "1.0",
    "FOW_FOG_TAX": "0", "FOW_HAZARD": "0", "FOW_CVAR": "0",
    "FOW_WORST": "0", "FOW_RISK_LAMBDA": "1.0",
    "FOW_THREAT": "1.0", "FOW_KING_PENALTY": "0",
    "FOW_RANDOM": "0", "FOW_INFOSET": "0",
}
# Baseline-affecting flags outside this whitelist are never inherited from
# the build runner, unless explicitly added to a new audited configuration.
FOW_CLEAN = {k for k in os.environ if k.startswith("FOW_")}


def stable(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"))


def checksum(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def verified_source_hashes():
    frozen_files = (ROOT / "tests/frozen_bots.sha256").read_text().splitlines()
    recorded = dict(reversed(line.split(maxsplit=1)) for line in frozen_files if line.strip())
    targets = [name for name in recorded if name.startswith("bots/obscuro_v4/")]
    mismatched = [name for name in targets if checksum(ROOT / name) != recorded[name]]
    if not targets or mismatched:
        raise ValueError("frozen v4 checksum mismatch: " + str(mismatched))
    return {"frozen_inventory_entries": len(targets),
            "frozen_inventory_sha256": checksum(ROOT / "tests/frozen_bots.sha256"),
            "stockfish_network_sha256": "1a298aa575a085434d29027978dc36867fe9c5bcea9376654b7a8eba1e52dfc2"}


def static_audit():
    """Compare shared algorithm components on explicitly constructed evidence."""
    for k in list(os.environ):
        if k.startswith("FOW_"):
            del os.environ[k]
    os.environ.update(B1_ENV)
    sys.path[:0] = [str(ROOT / "bots/eBotI"), str(ROOT / "bots/obscuro_v4")]
    sf1 = importlib.import_module("eBotI.stockfish_search")
    sf0 = importlib.import_module("obscuro_v4.stockfish_search")
    c1 = importlib.import_module("eBotI.search")
    c0 = importlib.import_module("obscuro_v4.search")
    checks = {}
    checks["constant_attacked_weight"] = (sf1.ATTACKED_WEIGHT == sf0.ATTACKED_WEIGHT == 6.0)
    checks["root_scan_depth_slice"] = (
        (sf1.MAX_ROOTS, sf1.SCAN_STATES, sf1.MAX_DEPTH, sf1.MAX_SLICE)
        == (sf0.MAX_ROOTS, sf0.SCAN_STATES, sf0.MAX_DEPTH, sf0.MAX_SLICE)
    )
    budgets = [(8, 0), (24, 0.1), (36, 0.4), (180, 2), (600, 0), (120, 1)]
    differences = [
        abs(c1.move_budget(t, inc, 1 + i) - c0.move_budget(t, inc))
        for i, (t, inc) in enumerate(budgets)
    ]
    checks["move_budget_function"] = max(differences) < 1e-12
    evidence_data = {
        "scan_attacked": np.array([True, False, True, False]),
        "scan_suicide": np.array([[False, True, False], [False, False, True],
                                  [True, True, False], [False, False, False]], dtype=bool),
        "root_attacked": np.array([True, False, False]),
        "root_suicide": np.array([[False, True, False], [True, False, False],
                                  [False, False, True]], dtype=bool),
        "root_values": np.array([[0.1, -1.0, 0.4], [-0.9, 0.2, 0.3],
                                  [0.5, 0.2, -1.0]]),
        "sampled": 3, "depths": (8, 10, 11),
        "scan_count": np.array([2, 1, 3, 1]),
        "root_count": np.array([2, 1, 1]),
    }
    a = sf0.Evidence(**evidence_data)
    b = sf1.Evidence(**evidence_data)
    x0 = sf0.weigh(a)
    x1 = sf1.weigh(b)
    errs = [float(np.max(np.abs(x - y))) for x, y in zip(x0, x1)]
    checks["risk_and_value_aggregation"] = max(errs) < 1e-10
    board = referee.FowBoard()
    states = [board.copy(stack=False)]
    for uci in ("e2e4", "d7d5", "g1f3", "c8g4", "f1b5"):
        board.push_uci(uci)
        states.append(board.copy(stack=False))
    for weights in (None, [1, 2, 3, 4, 5, 6]):
        y0 = [(s.fen(), k) for s, k in sf0.draw(states, weights, random.Random(619))]
        y1 = [(s.fen(), k) for s, k in sf1.draw(states, weights, random.Random(619))]
        if y0 != y1:
            checks["belief_root_draw"] = False
            break
    else:
        checks["belief_root_draw"] = True
    actions = referee.fow_moves(referee.FowBoard())
    a0 = sf0.classify(referee.FowBoard(), actions)
    a1 = sf1.classify(referee.FowBoard(), actions)
    checks["fow_move_classification"] = a0 == a1
    return {
        "profile": B1_ENV, "profile_sha256": hashlib.sha256(stable(B1_ENV).encode()).hexdigest(),
        "checks": checks, "max_move_budget_difference": max(differences),
        "max_evaluation_difference": max(errs), "all_shared_components_equal": all(checks.values()),
        "caveat": "These test shared components only; full action parity requires black-box probing.",
    }


def bot_command(name, move_time=0.18):
    folder = ROOT / "bots" / name
    stockfish = folder / "stockfish/src/stockfish"
    helper = folder / "positions"
    for path in (folder / "run.sh", stockfish, helper):
        if not path.is_file():
            raise ValueError("missing baseline bot component: " + str(path))
    return ["bash", str(folder / "run.sh"), "--seed", "23", "--engines", "1",
            "--move-time", str(move_time), "--stockfish", str(stockfish),
            "--positions", str(helper)]


class BotProbe:
    def __init__(self, name, side, seed, folder, profile):
        self.logfile = (Path(folder) / (name + "-" + ("w" if side else "b") + "-" + str(seed) + ".stderr"))
        self.log = self.logfile.open("w", encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if not k.startswith("FOW_")}
        env.update(profile)
        env.update({"PYTHON": sys.executable, "OMP_NUM_THREADS": "1",
                    "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"})
        argv = bot_command(name)
        argv[argv.index("--seed") + 1] = str(seed)
        self.process = subprocess.Popen(argv, cwd=ROOT, env=env,
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=self.log, text=True, bufsize=1,
                                        start_new_session=True)
        self.send("fow")
        self.send(("w" if side else "b") + " 36 0.4")
        if self.read(20) != "ready":
            raise RuntimeError("bot did not declare readiness")

    def send(self, line):
        self.process.stdin.write(str(line) + "\n")
        self.process.stdin.flush()

    def read(self, seconds=20):
        ready, _, _ = select.select([self.process.stdout], [], [], seconds)
        if not ready:
            raise RuntimeError("bot timeout, exit=" + str(self.process.poll()))
        line = self.process.stdout.readline()
        if not line:
            raise RuntimeError("bot exited without a move: " + str(self.process.poll()))
        return line.strip()

    def close(self):
        if hasattr(self, "process"):
            if self.process.poll() is None:
                try:
                    os.killpg(self.process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    self.process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(self.process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    self.process.wait(timeout=3)
            if self.process.stdin:
                self.process.stdin.close()
            if self.process.stdout:
                self.process.stdout.close()
        if hasattr(self, "log"):
            self.log.close()


def black_box_probe(directory, *, seeds=(17, 29), sides=(True, False),
                    max_own_decisions=3):
    """Compare decisions only while both bots share the exact same legal history.

    On first divergence stop the trajectory; subsequent decisions would no
    longer be conditioned on the same self-chosen history.
    """
    summary = {"trials": [], "action_comparisons": 0, "equal_actions": 0,
               "divergent_actions": 0, "runtime_errors": 0}
    for side in sides:
        for seed in seeds:
            trial = {"side": "white" if side else "black", "seed": seed,
                     "actions": [], "first_divergence_ply": None, "error": None}
            baseline = candidate = None
            try:
                baseline = BotProbe(B0, side, seed, directory, {})
                candidate = BotProbe(B1, side, seed, directory, B1_ENV)
                board = referee.FowBoard()
                reps = Counter({referee.position_key(board): 1})
                opponent = ObservationTracker(not side)
                rng = random.Random(1000 + seed + int(side))
                for ply in range(32):
                    if referee.outcome(board, reps) or len(trial["actions"]) >= max_own_decisions:
                        break
                    view = referee.observation(board, side)
                    baseline.send(view)
                    candidate.send(view)
                    opponent.observe(referee.observation(board, not side))
                    if board.turn == side:
                        baseline.send("30.0")
                        candidate.send("30.0")
                        aa = baseline.read(30)
                        ab = candidate.read(30)
                        if not aa.startswith("move ") or not ab.startswith("move "):
                            raise ValueError("non-protocol move in parity comparison")
                        move_a = chess.Move.from_uci(aa[5:])
                        move_b = chess.Move.from_uci(ab[5:])
                        if move_a not in referee.fow_moves(board) or move_b not in referee.fow_moves(board):
                            raise ValueError("bot parity move illegal under referee")
                        equal = move_a == move_b
                        trial["actions"].append({
                            "ply": ply, "view_sha256": hashlib.sha256(view.encode()).hexdigest(),
                            "baseline": move_a.uci(), "candidate": move_b.uci(),
                            "equal": equal,
                        })
                        summary["action_comparisons"] += 1
                        if equal:
                            summary["equal_actions"] += 1
                        else:
                            summary["divergent_actions"] += 1
                            trial["first_divergence_ply"] = ply
                            break
                        move = move_a
                    else:
                        moves = opponent.legal_moves()
                        if not moves:
                            break
                        move = rng.choice(moves)
                        opponent.record_move(move)
                        if move not in referee.fow_moves(board):
                            raise ValueError("opponent observation-only move not legal")
                    board.push(move)
                    reps[referee.position_key(board)] += 1
            except Exception as exc:
                summary["runtime_errors"] += 1
                trial["error"] = type(exc).__name__ + ": " + str(exc)
            finally:
                for bot in (candidate, baseline):
                    if bot:
                        bot.close()
            summary["trials"].append(trial)
    n = summary["action_comparisons"]
    summary["observed_action_agreement_rate"] = (
        summary["equal_actions"] / n if n else None)
    summary["action_parity_established"] = (
        n > 0 and summary["divergent_actions"] == 0 and summary["runtime_errors"] == 0
    )
    summary["interpretation"] = (
        "Finite, clock-sensitive black-box parity probe; agreement does not prove all-history identity."
        if summary["action_parity_established"] else
        "Baseline-equivalent settings did NOT establish action parity; use frozen B0 directly as control until resolved."
    )
    return summary


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--skip-live", action="store_true")
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    record = {
        "schema": 1, "reference": B0, "candidate_parity_profile": B1,
        "current_default_profile": B2,
        "reference_hashes": verified_source_hashes(),
        "static": static_audit(),
        "live": ({"status": "not_run"} if args.skip_live
                 else black_box_probe(args.output / "parity_logs")),
    }
    # stdout logs are diagnostic, never source code / full hidden board input.
    out = args.output / "baseline_audit.json"
    out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"shared_component_pass": record["static"]["all_shared_components_equal"],
                      "live_action_parity": record["live"].get("action_parity_established"),
                      "action_comparisons": record["live"].get("action_comparisons"),
                      "action_divergences": record["live"].get("divergent_actions"),
                      "runtime_errors": record["live"].get("runtime_errors")}, sort_keys=True))


if __name__ == "__main__":
    main()
