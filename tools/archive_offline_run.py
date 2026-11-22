#!/usr/bin/env python3
"""Archive calibrated/offline/model FoW research results, with complete checksums.

Offline evidence is NOT a chess game. Unlike archive_research_run.py this schema
requires metrics, data lineage and a report, not any referee replays.
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

try:
    from .research_ids import research_id, research_variant, SAFE_NAME
except ImportError:  # executed directly as tools/archive_offline_run.py
    from research_ids import research_id, research_variant, SAFE_NAME

HEX40 = re.compile(r"[a-f0-9]{40}")


def stable_json(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def inventory(run):
    files = {}
    total = 0
    for path in sorted(run.rglob("*")):
        if path.is_symlink():
            raise ValueError("symlink forbidden in offline evidence")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError("unsupported offline evidence entry")
        relative = path.relative_to(run).as_posix()
        if path.name.endswith(".tmp") or ".." in path.parts:
            raise ValueError("unsafe or partial offline evidence entry")
        data = path.read_bytes()
        if len(data) > 2_000_000_000:
            raise ValueError("single offline asset exceeds release limit")
        total += len(data)
        if total > 1_900_000_000:
            raise ValueError("offline research run too large; split evidence explicitly")
        files[relative] = {"sha256": sha256(data), "bytes": len(data)}
    return files


def evidence(run, project_id):
    research_id(project_id)
    if not run.is_dir() or not SAFE_NAME.fullmatch(run.name):
        raise ValueError("unsafe or missing offline run directory")
    for name in ("manifest.json", "metrics.json", "data_split.json", "notes.md"):
        if not (run / name).is_file():
            raise ValueError("missing offline evidence: " + name)
    m = read_json(run / "manifest.json")
    metric = read_json(run / "metrics.json")
    split = read_json(run / "data_split.json")
    if m.get("project_id") != project_id or m.get("run_id") != run.name:
        raise ValueError("offline project/run identity mismatch")
    if not HEX40.fullmatch(str(m.get("source_commit", ""))):
        raise ValueError("invalid offline git revision")
    if m.get("evidence_type") != "offline":
        raise ValueError("invalid offline evidence type")
    if m.get("purpose") not in ("smoke", "research"):
        raise ValueError("invalid offline purpose")
    variant = research_variant(m.get("variant"), project=project_id)
    if metric.get("status") not in ("complete", "failed", "incomplete"):
        raise ValueError("invalid offline completion status")
    if metric.get("schema") != 1 or split.get("schema") != 1:
        raise ValueError("invalid offline metric/data schema")
    primary = metric.get("primary_metric")
    if metric["status"] == "complete":
        if not isinstance(primary, dict) or not isinstance(primary.get("name"), str):
            raise ValueError("complete offline results need a named primary metric")
        if not isinstance(primary.get("n"), int) or primary["n"] <= 0:
            raise ValueError("complete offline results need a positive sample count")
        if not isinstance(split.get("provenance"), str) or not split["provenance"]:
            raise ValueError("complete offline results require data provenance")
    if m.get("purpose") == "smoke" and metric.get("claim_strength"):
        raise ValueError("smoke cannot claim strength")
    files = inventory(run)
    return {
        "schema": 1,
        "evidence_type": "offline",
        "research_id": project_id,
        "variant": variant,
        "run_id": run.name,
        "source_commit": m["source_commit"],
        "source_ref": m.get("source_ref"),
        "hypothesis": m.get("hypothesis"),
        "script": m.get("script"),
        "purpose": m["purpose"],
        "status": metric["status"],
        "valid_complete_run": metric["status"] == "complete",
        "primary_metric": primary,
        "data_provenance": split.get("provenance"),
        "conclusion": (
            "Synthetic offline integration smoke; not evidence of research or playing strength."
            if m["purpose"] == "smoke"
            else ("Offline metric recorded; playing-strength claims require independent matches."
                  if metric["status"] == "complete"
                  else "Failed or incomplete offline study; no performance inference.")
        ),
        "files": files,
    }


def verify(path):
    with tarfile.open(path, "r:gz") as tar:
        members = tar.getmembers()
        names = [member.name for member in members]
        if len(names) != len(set(names)) or not all(member.isfile() for member in members):
            raise ValueError("unsafe/duplicate offline archive member")
        if "run/EVIDENCE.json" not in names:
            raise ValueError("missing offline evidence index")
        index = json.load(tar.extractfile("run/EVIDENCE.json"))
        expected = {"run/EVIDENCE.json"} | {"run/" + p for p in index["files"]}
        if set(names) != expected:
            raise ValueError("offline inventory mismatch")
        for name, record in index["files"].items():
            data = tar.extractfile("run/" + name).read()
            if len(data) != record["bytes"] or sha256(data) != record["sha256"]:
                raise ValueError("offline archive checksum mismatch: " + name)
        return index


def archive(run, output, project_id):
    meta = evidence(run, project_id)
    output.mkdir(parents=True, exist_ok=True)
    stem = "research-offline-" + project_id + "-" + run.name
    dest = output / (stem + ".tar.gz")
    entries = [("EVIDENCE.json", stable_json(meta))]
    entries += [(name, (run / name).read_bytes()) for name in meta["files"]]
    with dest.open("wb") as stream:
        with gzip.GzipFile(filename="", fileobj=stream, mode="wb", mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode="w") as tar:
                for name, data in entries:
                    info = tarfile.TarInfo("run/" + name)
                    info.mode = 0o644
                    info.size = len(data)
                    info.mtime = 0
                    tar.addfile(info, io.BytesIO(data))
    digest = sha256(dest.read_bytes())
    (output / (stem + ".sha256")).write_text(digest + "  " + dest.name + "\n", encoding="utf-8")
    catalog = {k: v for k, v in meta.items() if k != "files"}
    catalog.update({"archive": dest.name, "sha256": digest, "file_count": len(meta["files"])})
    (output / (stem + ".json")).write_bytes(stable_json(catalog))
    (output / (stem + ".md")).write_text(
        "# Offline research evidence: " + project_id + " / " + run.name + "\n\n"
        + "Source revision: " + meta["source_commit"] + "\n"
        + "Variant: " + str(meta["variant"]) + "\n"
        + "Status: " + meta["status"] + "\n"
        + "Primary metric: " + str(meta["primary_metric"]) + "\n\n"
        + "**Interpretation:** " + meta["conclusion"] + "\n",
        encoding="utf-8",
    )
    verify(dest)
    return dest, digest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--research-id", required=True)
    args = p.parse_args()
    path, checksum = archive(args.run.resolve(), args.output.resolve(), args.research_id)
    print(path)
    print("sha256:", checksum)


if __name__ == "__main__":
    main()
