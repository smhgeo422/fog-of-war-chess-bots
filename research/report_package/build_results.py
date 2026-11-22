"""Build the report tables from verified bundles and published run catalogs."""

import argparse
import csv
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.verify_research_archive import verify_bundle

AUDIT_REF = "91c060c"
WEB = "https://github.com/smhgeo422/fog-of-war-chess-bots/blob/"
RESEARCH = ROOT / "research"


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def checked_bundle(path):
    catalog = path.with_suffix("").with_suffix(".json")
    sidecar = catalog.with_suffix(".sha256")
    return verify_bundle(path, sidecar, catalog), json.loads(catalog.read_text())


def read_member(path, member):
    with tarfile.open(path, "r:gz") as archive:
        with archive.extractfile(member) as stream:
            return json.load(stream)


def stage3_ledgers():
    for i in range(1, 10):
        pid = f"P{i}"
        ledger = RESEARCH / "projects" / pid / "variants.jsonl"
        yield next(row for row in map(json.loads, ledger.read_text().splitlines())
                   if row["version"] == "v1")


def read_hosted(repo, branch, path):
    ref = f"refs/heads/{branch}"
    data = json.loads(git(repo, "show", f"{ref}:{path}"))
    if data["source_ref"] != branch:
        raise ValueError(f"Wrong source branch for {path}")
    git(repo, "merge-base", "--is-ancestor", data["source_commit"], ref)
    catalog_commit = git(repo, "log", "-1", "--format=%H", ref, "--", path)
    return data, WEB + catalog_commit + "/" + path


def row(stage, scope, catalog, source_url, verification, archive_path=None):
    if not re.fullmatch(r"[a-f0-9]{64}", catalog["sha256"]):
        raise ValueError("Malformed archive digest")
    return {
        "stage": stage, "scope": scope, "run_id": catalog["run_id"],
        "project": catalog["research_id"], "variant": catalog.get("variant"),
        "source_commit": catalog["source_commit"], "source_ref": catalog["source_ref"],
        "catalog_url": source_url, "bundle_verification": verification,
        "archive_path": archive_path, "archive_sha256": catalog["sha256"],
        "draft_release_url": catalog.get("release_url"), "purpose": catalog["purpose"],
        "valid_complete_run": catalog["valid_complete_run"],
        "primary_metric": catalog.get("primary_metric"), "score_rate": catalog.get("score_rate"),
        "paired_score_interval_95": catalog.get("paired_score_interval_95"),
        "games": catalog.get("recorded_games"), "base_seconds": catalog.get("base_seconds"),
        "increment_seconds": catalog.get("increment_seconds"), "max_plies": catalog.get("max_plies"),
        "conclusion": catalog.get("conclusion"),
    }


def collect(remote):
    specs = [
        (1, "offline pipeline smoke", "experiment/P1-v0-pipeline-smoke", "research-offline-evidence-45071213893-1"),
        (1, "game pipeline smoke", "experiment/P1-v0-pipeline-smoke", "research-evidence-45071213893-1"),
        (2, "B1 versus B0 smoke", "experiment/Infra-stage2-b1-parity-profile", "research-evidence-45073041219-1"),
        (2, "B2 versus B0 smoke", "experiment/Infra-stage2-b2-current-default", "research-evidence-45073046202-1"),
        (2, "canonical synthetic corpus and parity", "infra/stage2-baselines-corpus", "research-offline-evidence-45073998777-1"),
    ]
    expected = {}
    for entry in stage3_ledgers():
        run_number = entry["offline_runs"][0].split("-")[1]
        key = f"research-offline-evidence-{run_number}-1"
        specs.append((3, "v1 toy or restricted correctness", entry["branch"], key))
        expected[key] = entry
    results = []
    for stage, scope, branch, key in specs:
        catalog, url = read_hosted(remote, branch, f"research/runs/{key}.json")
        if key in expected:
            entry = expected[key]
            if (catalog["source_commit"], catalog["sha256"], catalog["research_id"]) != (
                    entry["source_commit"], entry["archive_sha256"], entry["project_id"]):
                raise ValueError(f"Stage 3 ledger mismatch for {key}")
        if not catalog["verified_remote"]:
            raise ValueError(f"Hosted verification missing for {key}")
        results.append(row(stage, scope, catalog, url,
                           "catalog and source verified; bundle verification reported by hosted run"))

    for folder, stage, scope in (
        ("stage4-b0-b2-smoke-20261122", 4, "B2 versus B0 capped smoke"),
        ("stage4-screen-20261122", 4, "nine-project restricted offline screen"),
        ("stage5-P3-v2", 5, "fixed-slot referee ablation"),
        ("stage5-P8-v2", 5, "matched-quota Stockfish ablation"),
    ):
        [path] = (RESEARCH / "archives" / folder).glob("*.tar.gz")
        manifest, catalog = checked_bundle(path)
        git(remote, "merge-base", "--is-ancestor", manifest["source_commit"],
            f'refs/heads/{catalog["source_ref"]}')
        archive_path = path.relative_to(ROOT).as_posix()
        catalog_path = archive_path.removesuffix(".tar.gz") + ".json"
        results.append(row(stage, scope, catalog, WEB + AUDIT_REF + "/" + catalog_path,
                           "bundle checksum and member inventory reverified", archive_path))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog-repo", type=Path, required=True)
    args = parser.parse_args()
    rows = collect(args.catalog_repo)
    if len(rows) != 18 or len({row["run_id"] + "/" + row["scope"] for row in rows}) != len(rows):
        raise ValueError("Unexpected catalog inventory")
    dataset = {"schema": 1, "audited_checkpoint": AUDIT_REF,
               "eligible_confirmatory_candidates": [], "confirmatory_games": 0, "runs": rows}
    (RESEARCH / "combined_results.json").write_text(json.dumps(dataset, indent=2, allow_nan=False) + "\n")
    with (RESEARCH / "combined_results.csv").open("w", newline="") as stream:
        fields = csv.DictWriter(stream, list(rows[0]), lineterminator="\n")
        fields.writeheader()
        for entry in rows:
            fields.writerow({key: json.dumps(value) if isinstance(value, (dict, list)) else value
                             for key, value in entry.items()})


if __name__ == "__main__":
    main()
