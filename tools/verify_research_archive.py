#!/usr/bin/env python3
"""Verify a downloaded GitHub release research-evidence bundle end to end.

Accepts a tar.gz, matching SHA-256 sidecar and JSON catalog. Re-checks every
tar member against the embedded SHA-256 evidence manifest, and cross-checks
metadata and the release-side catalog. Offline bundles and game runs supported.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from .archive_research_run import verify as verify_game
    from .archive_offline_run import verify as verify_offline
except ImportError:
    from archive_research_run import verify as verify_game
    from archive_offline_run import verify as verify_offline


def verify_bundle(archive, checksum, catalog):
    path = Path(archive)
    if not path.is_file() or not checksum.is_file() or not catalog.is_file():
        raise ValueError("missing release artifact")
    sha_line = checksum.read_text(encoding="utf-8").strip()
    parts = sha_line.split()
    if len(parts) != 2 or parts[1] != path.name or len(parts[0]) != 64:
        raise ValueError("invalid SHA-256 sidecar")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != parts[0]:
        raise ValueError("archive SHA-256 mismatch")
    record = json.loads(catalog.read_text(encoding="utf-8"))
    if record.get("archive") != path.name or record.get("sha256") != actual:
        raise ValueError("catalog and release archive differ")
    # Identify archive type from existing catalog: original game bundles predate
    # offline evidence_type; maintain compatibility without modifying old data.
    meta = (verify_offline(path) if record.get("evidence_type") == "offline"
            else verify_game(path))
    for key in ("research_id", "run_id", "source_commit", "valid_complete_run",
                "purpose", "variant"):
        if key in meta and record.get(key) != meta[key]:
            raise ValueError("archive/catalog identity mismatch: " + key)
    if record.get("file_count") != len(meta["files"]):
        raise ValueError("catalog evidence-file count mismatch")
    return meta


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--sha256-file", type=Path, required=True)
    p.add_argument("--catalog", type=Path, required=True)
    args = p.parse_args()
    data = verify_bundle(args.archive, args.sha256_file, args.catalog)
    print(json.dumps({
        "verified": True, "research_id": data["research_id"],
        "run_id": data["run_id"], "valid_complete_run": data["valid_complete_run"],
        "evidence_type": data.get("evidence_type", "game"),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
