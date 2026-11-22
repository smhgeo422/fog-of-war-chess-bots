#!/usr/bin/env python3
"""Archive one FoW experiment with verifiable, self-contained evidence.

Uses only the Python standard library. No credentials, team tokens or private files
are ever read outside the explicitly supplied run directory.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile

ID = re.compile(r"(?:P[1-9]|[A-F][0-9]{2}|Infra)")
RUN = re.compile(r"[A-Za-z0-9_-]{1,100}")
HEX = re.compile(r"[a-f0-9]{40}")


def canonical(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def evidence(run, research_id):
    if not ID.fullmatch(research_id):
        raise ValueError("research ID must be P1..P9, A01..F99 or Infra")
    if not RUN.fullmatch(run.name) or not run.is_dir():
        raise ValueError("invalid run directory or ID")
    required = ("manifest.json", "report.json", "registry.json", "report.md")
    for name in required:
        if not (run / name).is_file():
            raise ValueError("missing run evidence: " + name)
    manifest, report, registry = [read_json(run / name) for name in required[:3]]
    settings = manifest.get("settings", {})
    if registry.get("id") != run.name or settings.get("id") != run.name:
        raise ValueError("run ID differs across registry, manifest and directory")
    if not isinstance(manifest.get("commit"), str) or not HEX.fullmatch(manifest["commit"]):
        raise ValueError("invalid source commit SHA")
    if registry.get("commit") != manifest["commit"]:
        raise ValueError("registry revision differs from manifest")
    if report.get("scheduled") != settings.get("games"):
        raise ValueError("scheduled game counts disagree")
    replay_files = sorted((run / "replays").glob("*.json"))
    if not replay_files or report.get("recorded") != len(replay_files):
        raise ValueError("recorded/replay game count mismatch")
    expected_games = []
    for path in replay_files:
        game = read_json(path).get("experimentGame", {})
        if (not path.stem.isdigit() or game.get("game") != int(path.stem)
                or game.get("replay") != "replays/" + path.name):
            raise ValueError("replay and embedded game record disagree: " + path.name)
        expected_games.append(game["game"])
    if len(set(expected_games)) != len(expected_games):
        raise ValueError("duplicate game numbers")
    files = {}
    total = 0
    for path in sorted(run.rglob("*")):
        if path.is_symlink():
            raise ValueError("symlinks are not allowed in research evidence")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError("unsupported entry in evidence")
        relative = path.relative_to(run).as_posix()
        if path.name.endswith(".tmp"):
            raise ValueError("unfinished temporary file in research evidence")
        data = path.read_bytes()
        if len(data) > 2_000_000_000:
            raise ValueError("individual evidence file exceeds GitHub release limit")
        total += len(data)
        if total > 1_900_000_000:
            raise ValueError("run too large for one archive; split archival explicitly")
        files[relative] = {"sha256": sha(data), "bytes": len(data)}
    purpose = settings.get("purpose", "strength")
    if purpose not in ("smoke", "strength"):
        raise ValueError("unknown experiment purpose")
    valid = (report.get("recorded") == report.get("scheduled")
             and not report.get("invalid")
             and not report.get("failure_codes")
             and all(x == 0 for x in report.get("worker_exit_codes", [])))
    if re.fullmatch(r"P[1-9]", research_id):
        if settings.get("project_id") != research_id or not re.fullmatch(r"v(?:0|[1-9][0-9]*)", settings.get("variant") or ""):
            raise ValueError("P1..P9 run lacks matching project_id and variant")
    metadata = {
        "schema": 1,
        "research_id": research_id,
        "variant": settings.get("variant"),
        "hypothesis": settings.get("hypothesis"),
        "run_id": run.name,
        "source_commit": manifest["commit"],
        "source_ref": manifest.get("ref"),
        "purpose": purpose,
        "candidate": settings.get("candidate"),
        "baseline": settings.get("baseline"),
        "base_seconds": settings.get("base"),
        "increment_seconds": settings.get("increment"),
        "max_plies": settings.get("max_plies"),
        "scheduled_games": report["scheduled"],
        "recorded_games": report["recorded"],
        "valid_complete_run": bool(valid),
        "score_rate": report.get("overall", {}).get("score_rate"),
        "paired_score_interval_95": report.get("complete_pair_score_interval_95"),
        "conclusion": (
            "Integration smoke only; not evidence of playing strength."
            if purpose == "smoke"
            else ("Awaiting substantive interpretation; score alone is not sufficient."
                  if valid else "Incomplete or invalid experiment; do not infer strength.")
        ),
        "files": files,
    }
    return metadata


def archive(run, output, research_id):
    metadata = evidence(run, research_id)
    output.mkdir(parents=True, exist_ok=True)
    slug = "research-" + research_id + "-" + run.name
    tgz = output / (slug + ".tar.gz")
    marker = canonical(metadata)
    # Deterministic tar members and gzip header. Same bytes => same archive.
    with tgz.open("wb") as destination:
        with gzip.GzipFile(filename="", fileobj=destination, mode="wb", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as tar:
                entries = [("EVIDENCE.json", marker)]
                entries.extend((name, (run / name).read_bytes()) for name in metadata["files"])
                for name, data in entries:
                    member = tarfile.TarInfo("run/" + name)
                    member.size = len(data)
                    member.mtime = 0
                    member.mode = 0o644
                    tar.addfile(member, io.BytesIO(data))
    fingerprint = sha(tgz.read_bytes())
    (output / (slug + ".sha256")).write_text(
        fingerprint + "  " + tgz.name + "\n", encoding="utf-8")
    catalog = {k: v for k, v in metadata.items() if k != "files"}
    catalog.update({"archive": tgz.name, "sha256": fingerprint,
                    "file_count": len(metadata["files"])})
    (output / (slug + ".json")).write_bytes(canonical(catalog))
    interval = metadata["paired_score_interval_95"]
    lines = [
        "# Experiment " + research_id + " / " + run.name,
        "",
        "Source commit: " + metadata["source_commit"],
        "Candidate: " + str(metadata["candidate"]),
        "Baseline: " + str(metadata["baseline"]),
        "Games: " + str(metadata["recorded_games"]) + " / " + str(metadata["scheduled_games"]),
        "Time control: " + str(metadata["base_seconds"]) + "+"
        + str(metadata["increment_seconds"]),
        "Purpose: " + metadata["purpose"],
        "Valid, complete run: " + str(metadata["valid_complete_run"]),
        "Score rate: " + str(metadata["score_rate"]),
        "Paired 95% interval: " + str(interval),
        "",
        "**Interpretation:** " + metadata["conclusion"],
        "",
        "The tar.gz contains the original manifest, reports, registry, per-game "
        "replays, and a SHA-256 evidence manifest. Inspect any failure codes and "
        "replay context before promoting an experimental method.",
    ]
    (output / (slug + ".md")).write_text("\n".join(lines) + "\n", encoding="utf-8")
    verify(tgz)
    return tgz, fingerprint


def verify(tgz):
    with tarfile.open(tgz, "r:gz") as tar:
        members = tar.getmembers()
        names = [m.name for m in members]
        if len(names) != len(set(names)) or not all(m.isfile() for m in members):
            raise ValueError("unsafe or duplicate archive member")
        if "run/EVIDENCE.json" not in names:
            raise ValueError("missing archive evidence index")
        metadata = json.load(tar.extractfile("run/EVIDENCE.json"))
        expected = {"run/EVIDENCE.json"} | {"run/" + f for f in metadata["files"]}
        if set(names) != expected:
            raise ValueError("archive inventory differs")
        for name, record in metadata["files"].items():
            data = tar.extractfile("run/" + name).read()
            if len(data) != record["bytes"] or sha(data) != record["sha256"]:
                raise ValueError("evidence checksum mismatch: " + name)
        return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--research-id", required=True)
    args = parser.parse_args()
    path, checksum = archive(args.run.resolve(), args.output.resolve(),
                             args.research_id)
    print(path)
    print("sha256:", checksum)


if __name__ == "__main__":
    main()
