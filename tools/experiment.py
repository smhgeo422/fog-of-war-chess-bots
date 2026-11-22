#!/usr/bin/env python3
"""Run a seeded, color-balanced two-bot experiment from a clean commit."""
import argparse
import ctypes
from datetime import UTC, datetime
import hashlib
import json
import math
import multiprocessing
import os
from pathlib import Path
import platform
import random
import re
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import fow.local as local
import referee
from experiment_report import markdown, replay_metrics, summarize

NAME = re.compile(r"[a-zA-Z0-9_-]+")
STOCKFISH_NET = "nn-1a298aa575a0.nnue"
NETWORK_HASH = "1a298aa575a085434d29027978dc36867fe9c5bcea9376654b7a8eba1e52dfc2"
COMPONENT_LOG = (
    b"stockfish ready:", b"position-set helper ready", b"stockfish engine lost",
    b"position-set helper lost", b"no stockfish result", b"no Stockfish",
    b"stockfish did not start", b"starting stockfish failed", b"no position-set helper",
)
ORIGINAL_CAPTURE = referee.StderrCapture


class ComponentCapture(ORIGINAL_CAPTURE):
    """Track component messages throughout a game, beyond the referee's rolling tail."""

    def __init__(self):
        super().__init__()
        self.partial = b""
        self.messages = []
        self.overflow = False
        self.fallback_moves = 0
        self.__class__.instances.append(self)

    def feed(self, chunk):
        lines = (self.partial + chunk).split(b"\n")
        self.partial = lines.pop()[-4096:]
        for line in lines:
            if b"fallback move" in line:
                self.fallback_moves += 1
            if any(marker in line for marker in COMPONENT_LOG):
                if len(self.messages) >= 4096:
                    self.overflow = True
                else:
                    self.messages.append(line[:4096].decode("utf-8", "replace"))
        return super().feed(chunk)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def command_version(argv, cwd=ROOT):
    return subprocess.check_output(argv, cwd=cwd, text=True, timeout=15).splitlines()[0]


def available_cpus():
    cpus = len(os.sched_getaffinity(0))
    quota = Path("/sys/fs/cgroup/cpu.max")
    if quota.is_file():
        count, period = quota.read_text().split()
        if count != "max":
            cpus = min(cpus, max(1, int(count) // int(period)))
    return cpus


def load_settings(path, identifier):
    settings = {
        "baseline": "obscuro_v4", "base": 180, "increment": 2, "max_plies": 1000,
        "parallel": 1, "engines": 2, "purpose": "strength", "candidate_args": [],
        "baseline_args": [],
    }
    config = json.loads(path.read_text())
    unknown = config.keys() - (settings.keys() | {"id", "candidate", "games", "seed", "hypothesis", "project_id", "variant"})
    if unknown:
        raise ValueError(f"unknown settings {sorted(unknown)}")
    settings.update(config)
    if identifier:
        settings["id"] = identifier
    for key in ("id", "candidate", "baseline"):
        if not isinstance(settings[key], str) or not NAME.fullmatch(settings[key]):
            raise ValueError(f"invalid {key}")
    if "project_id" in settings:
        from research_ids import research_id, research_variant
        project = research_id(settings["project_id"])
        if re.fullmatch(r"P[1-9]", project):
            research_variant(settings.get("variant"), project=project)
        elif settings.get("variant") is not None:
            raise ValueError("legacy runs must not declare a P-project variant")
    elif "variant" in settings:
        raise ValueError("variant requires project_id")
    if settings["candidate"] == settings["baseline"]:
        raise ValueError("candidate and baseline must be distinct bot directories")
    for key in ("games", "seed", "parallel", "engines", "max_plies"):
        if type(settings[key]) is not int or settings[key] < (0 if key == "seed" else 1):
            raise ValueError(f"invalid {key}")
    if settings["games"] % 2:
        raise ValueError("games must be even for color balance")
    for key in ("base", "increment"):
        value = settings[key]
        if type(value) not in (float, int) or not math.isfinite(value) or value < 0 or (key == "base" and not value):
            raise ValueError(f"invalid {key}")
    if settings["purpose"] not in ("smoke", "strength") or not isinstance(settings["hypothesis"], str) or not settings["hypothesis"].strip():
        raise ValueError("purpose and hypothesis are required")
    for key in ("candidate_args", "baseline_args"):
        args = settings[key]
        reserved = ("--stockfish", "--positions", "--engines", "--seed")
        if (not isinstance(args, list) or any(not isinstance(arg, str) for arg in args)
                or any(arg == "--" or any(flag.startswith(arg.split("=")[0]) for flag in reserved)
                       for arg in args if arg.startswith("--"))):
            raise ValueError(f"{key} may not override managed component or seed arguments")
    return settings


def bot_spec(settings, role):
    name = settings[role]
    directory = ROOT / "bots" / name
    if not (directory / "run.sh").is_file():
        raise ValueError(f"unknown bot {name}")
    args = local.bot_argv(str(directory), *settings[role + "_args"])
    components = {}
    if (directory / "REQUIRE_STOCKFISH").is_file():
        binary = directory / "stockfish/src/stockfish"
        network = binary.with_name(STOCKFISH_NET)
        if digest(network) != NETWORK_HASH:
            raise ValueError(f"{name} has an unexpected Stockfish network")
        version = command_version([str(binary), "compiler"], binary.parent)
        if not re.match(r"^Stockfish 19(?:\s|$)", version):
            raise ValueError(f"{name} has an unexpected Stockfish version {version}")
        components["stockfish"] = {
            "path": str(binary), "sha256": digest(binary), "version": version,
            "network_sha256": NETWORK_HASH, "engines": settings["engines"],
        }
        args.extend(["--stockfish", str(binary), "--engines", str(settings["engines"])])
    if (directory / "REQUIRE_POSITIONS").is_file():
        binary = directory / "positions"
        check = command_version([str(binary), "selftest"], directory)
        if not check.startswith("selftest ok"):
            raise ValueError(f"{name} position-set self-test did not report success")
        components["positions"] = {"path": str(binary), "sha256": digest(binary)}
        args.extend(["--positions", str(binary)])
    return {"name": name, "argv": args, "components": components}


def write_json(path, value):
    scratch = path.with_suffix(".tmp")
    scratch.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    scratch.replace(path)


def stop(_signum, _frame):
    raise SystemExit("experiment interrupted")


def stop_worker(signum, frame):
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    # A partly initialized bot may have started but not entered the referee's
    # list of bots to close. The local recorder already has its process group.
    proc = local._recorder.latest
    if proc is not None and proc.poll() is None:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    stop(signum, frame)


def worker_init():
    # The referee kills each bot's process group. Adopt the engine/helper
    # grandchildren so minimal container init processes need not reap them.
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(36, 1, 0, 0, 0) != 0:  # Linux PR_SET_CHILD_SUBREAPER
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, stop_worker)
    local.use_project_python()
    local.install_pausing()
    referee.StderrCapture = ComponentCapture


def reap_children():
    deadline = time.monotonic() + 2
    while True:
        try:
            pid, _ = os.waitpid(-1, os.WNOHANG)
        except ChildProcessError:
            return True
        if pid == 0:
            if time.monotonic() >= deadline:
                return False
            time.sleep(0.01)


def validate_components(bot, capture):
    components = bot["components"]
    errors = []
    for key, marker in (("stockfish", "stockfish ready:"), ("positions", "position-set helper ready")):
        if key not in components:
            continue
        component = components[key]
        if not any(marker in line and line.endswith("binary " + component["path"])
                   and (key != "stockfish" or f"ready: {component['engines']} of {component['engines']} engines" in line)
                   for line in capture.messages):
            errors.append(f"{bot['name']}: required {key} readiness absent")
    for line in capture.messages:
        if ("engine lost" in line or "helper lost" in line or "0 engines running" in line):
            errors.append(f"{bot['name']}: {line}")
    if capture.overflow:
        errors.append(f"{bot['name']}: component log overflow")
    return errors


def play(out, settings, bots, number, seed):
    start = time.monotonic()
    roles = ("candidate", "baseline") if number % 2 else ("baseline", "candidate")
    candidate_side = roles.index("candidate")
    argv = [bots[role]["argv"] + ["--seed", str(seed[role])] for role in roles]
    names = [bots[role]["name"] for role in roles]
    ComponentCapture.instances = []
    local._recorder.latest = None
    issues = []
    try:
        try:
            replay = referee.run_match(
                *argv, settings["base"], settings["increment"],
                match_id=f"{settings['id']}-{number:04d}", white_name=names[0], black_name=names[1],
                max_plies=settings["max_plies"], turn_control_factory=local.pause_control_factory,
            )
        finally:
            if not reap_children():
                issues.append("Worker still had child processes after referee cleanup")
        captures = ComponentCapture.instances
        for index, role in enumerate(roles):
            if index < len(captures):
                issues.extend(validate_components(bots[role], captures[index]))
            elif bots[role]["components"]:
                issues.append(f"{bots[role]['name']}: no component diagnostics")
        metrics = dict(zip(roles, replay_metrics(replay)))
        replay["experimentDiagnostics"] = {
            role: {"component_messages": capture.messages, "fallback_log_lines": capture.fallback_moves}
            for role, capture in zip(roles, captures)
        }
    except Exception as error:
        replay = {"result": "*", "reason": f"Runner exception: {type(error).__name__}: {error}", "frames": []}
        metrics = {}
    replay["experimentSeeds"] = seed
    replay["experimentIssues"] = issues
    path = f"replays/{number:04d}.json"
    failure_codes = [report["code"] for report in replay.get("studentReports", [])]
    if issues:
        failure_codes.append("component_failure")
    if replay["result"] == "*":
        failure_codes.append("infrastructure_failure")
    score = {"1-0": 1 - candidate_side, "0-1": candidate_side, "1/2-1/2": 0.5}.get(replay["result"])
    game = {
        "game": number, "pair": (number + 1) // 2, "candidate_color": ("white", "black")[candidate_side],
        "result": replay["result"], "score": score if not issues else None, "reason": replay["reason"],
        "failure_codes": failure_codes, "issues": issues, "plies": max(0, len(replay["frames"]) - 1),
        "metrics": metrics, "seed": seed, "wall_seconds": round(time.monotonic() - start, 3), "replay": path,
    }
    replay["experimentGame"] = game
    write_json(out / path, replay)
    return game



def play_schedule(out, settings, bots, schedule):
    worker_init()
    for number, seed in schedule:
        game = play(out, settings, bots, number, seed)
        print(f"{game['game']:04d} {game['candidate_color']} {game['result']} {game['reason']}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("--id", help="override the experiment ID for a new run")
    parser.add_argument("--results", type=Path, default=ROOT / "data/research/runs")
    args = parser.parse_args()
    settings = load_settings(args.config, args.id)
    if git("status", "--porcelain"):
        raise ValueError("commit source changes before running an experiment")
    for key in ("FOW_STOCKFISH", "FOW_POSITIONS"):
        os.environ.pop(key, None)
    for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[key] = "1"
    os.environ["PYTHONHASHSEED"] = "0"
    bots = {role: bot_spec(settings, role) for role in ("candidate", "baseline")}
    binaries = [Path(bot["components"]["stockfish"]["path"])
                for bot in bots.values() if "stockfish" in bot["components"]]
    if len(binaries) == 2 and binaries[0].samefile(binaries[1]):
        raise ValueError("bots must use separate Stockfish binary files")
    cpu_budget = available_cpus()
    per_game = max((1 + bot["components"].get("stockfish", {}).get("engines", 0)
                    for bot in bots.values()), default=1)
    if settings["parallel"] > max(1, cpu_budget // per_game):
        raise ValueError(f"parallelism exceeds CPU budget ({cpu_budget} CPUs, estimated {per_game} per game)")
    if settings["parallel"] > settings["games"]:
        raise ValueError("parallel workers exceed game count")
    out = args.results.resolve() / settings["id"]
    out.mkdir(parents=True)
    (out / "replays").mkdir()
    manifest = {
        "schema": 1, "started_utc": datetime.now(UTC).isoformat(), "settings": settings, "bots": bots,
        "commit": git("rev-parse", "HEAD"), "ref": git("rev-parse", "--abbrev-ref", "HEAD"),
        "environment": {
            "platform": platform.platform(), "cpu_budget": cpu_budget,
            "affinity_cpus": len(os.sched_getaffinity(0)), "python": platform.python_version(),
            "compiler": command_version(["g++", "--version"]), "uv_lock_sha256": digest(ROOT / "uv.lock"),
            "python_hash_seed": 0, "numeric_threads": 1, "pause_opponent": True,
        },
    }
    write_json(out / "manifest.json", manifest)
    rng = random.Random(settings["seed"])
    schedule = []
    for number in range(1, settings["games"] + 1):
        if number % 2:
            seed = {role: rng.getrandbits(32) for role in bots}
        schedule.append((number, seed))
    context = multiprocessing.get_context("fork")
    workers = [
        context.Process(target=play_schedule, args=(out, settings, bots, schedule[slot::settings["parallel"]]))
        for slot in range(settings["parallel"])
    ]
    signal.signal(signal.SIGTERM, stop)
    try:
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join()
    finally:
        # Only the driver receives SIGINT. On interruption, signal and join
        # each worker so its referee and subreaper cleanup finish before exit.
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        for worker in workers:
            if worker.is_alive():
                worker.terminate()
        for worker in workers:
            if worker.pid is not None:
                worker.join()
        # Recover every completed game, even if an earlier worker was interrupted.
        games = [
            json.loads(path.read_text())["experimentGame"]
            for path in sorted((out / "replays").glob("*.json"), key=lambda path: int(path.stem))
        ]
        report = summarize(games, settings)
        complete = len(games) == settings["games"]
        report["worker_exit_codes"] = [worker.exitcode for worker in workers]
        healthy = (complete and not report["invalid"] and not report["failure_codes"]
                   and all(code == 0 for code in report["worker_exit_codes"]))
        write_json(out / "report.json", report)
        (out / "report.md").write_text(markdown(report, settings))
        conclusion = ("Smoke integration passed." if settings["purpose"] == "smoke" else
                      "Pending research interpretation.") if healthy else "Failures or incomplete execution; inspect report."
        write_json(out / "registry.json", {
            "id": settings["id"], "hypothesis": settings["hypothesis"], "commit": manifest["commit"],
            "ref": manifest["ref"], "candidate": settings["candidate"], "baseline": settings["baseline"],
            "settings": settings, "results": "report.json", "conclusion": conclusion,
        })
        print(out, flush=True)
    return 0 if healthy else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        sys.exit(f"Experiment failed: {error}")
