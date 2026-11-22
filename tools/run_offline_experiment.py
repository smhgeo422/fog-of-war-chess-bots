#!/usr/bin/env python3
"""Execute a reviewed tracked offline research script and retain all evidence.

Scripts live under tools/offline_jobs/, are committed before execution and must
write metrics.json, data_split.json and notes.md inside --run. The runner writes
a provenance manifest before executing; a failure is retained as failure.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

from research_ids import research_id, research_variant, SAFE_NAME

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, timeout=15).strip()


def validate(config, branch):
    if not isinstance(config, dict):
        raise ValueError("offline config must be an object")
    keys = {"project_id", "variant", "purpose", "hypothesis", "script", "seed"}
    if set(config) != keys:
        raise ValueError("offline config must specify only " + ", ".join(sorted(keys)))
    project = research_id(config["project_id"])
    version = research_variant(config["variant"], project=project)
    if config["purpose"] not in ("smoke", "research"):
        raise ValueError("unknown offline purpose")
    if not isinstance(config["hypothesis"], str) or not config["hypothesis"].strip():
        raise ValueError("empty offline hypothesis")
    if type(config["seed"]) is not int or config["seed"] < 0:
        raise ValueError("invalid offline seed")
    script = config["script"]
    if not isinstance(script, str) or not script.startswith("tools/offline_jobs/"):
        raise ValueError("script must live under tools/offline_jobs/")
    path = ROOT / script
    if path.suffix != ".py" or not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT / "tools/offline_jobs"):
        raise ValueError("invalid offline script")
    git("ls-files", "--error-unmatch", "--", script)
    if not branch.startswith("experiment/" + project + "-" + version + "-"):
        raise ValueError("offline config must match branch project/version")
    return config


def execute(config_path, run):
    if git("status", "--porcelain"):
        raise ValueError("commit all source changes before offline experiment")
    if run.exists():
        raise ValueError("offline run directory already exists; never overwrite evidence")
    if not SAFE_NAME.fullmatch(run.name):
        raise ValueError("invalid offline run ID")
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    config = validate(json.loads(config_path.read_text(encoding="utf-8")), branch)
    run.mkdir(parents=True)
    manifest = {
        "schema": 1, "evidence_type": "offline",
        "source_commit": git("rev-parse", "HEAD"), "source_ref": branch,
        "run_id": run.name, "project_id": config["project_id"],
        "variant": config["variant"], "hypothesis": config["hypothesis"],
        "purpose": config["purpose"], "seed": config["seed"],
        "script": config["script"],
        "utc_started": datetime.now(timezone.utc).isoformat(),
        "environment": {"platform": platform.platform(), "python": platform.python_version()},
    }
    (run / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    argv = [sys.executable, str(ROOT / config["script"]), "--run", str(run),
            "--seed", str(config["seed"])]
    try:
        subprocess.run(argv, cwd=ROOT, check=True, timeout=300, env={**os.environ, "PYTHONHASHSEED": "0"})
    except Exception as exc:
        (run / "metrics.json").write_text(json.dumps({
            "schema": 1, "status": "failed", "primary_metric": None,
            "failure": type(exc).__name__ + ": " + str(exc),
        }, indent=2) + "\n")
        if not (run / "data_split.json").exists():
            (run / "data_split.json").write_text(json.dumps({
                "schema": 1, "provenance": "no completed data due to offline job failure"
            }, indent=2) + "\n")
        if not (run / "notes.md").exists():
            (run / "notes.md").write_text("# Failed offline job\n\n" + repr(exc) + "\n")
        raise
    for name in ("metrics.json", "data_split.json", "notes.md"):
        if not (run / name).is_file():
            raise ValueError("offline script failed to produce " + name)
    return run


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("config", type=Path)
    p.add_argument("--run", type=Path, required=True)
    args = p.parse_args()
    execute(args.config.resolve(), args.run.resolve())


if __name__ == "__main__":
    main()
