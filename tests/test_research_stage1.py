"""Stage 1: project IDs, offline scientific assets, checksum and no-strength guards."""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import tarfile

import pytest

from tools.research_ids import research_id, research_variant, branch_identity
from tools.archive_offline_run import archive, evidence, verify
from tools.archive_research_run import archive as game_archive, verify as game_verify
from tools.run_offline_experiment import validate as validate_offline_config
from tools.research_ids import SAFE_NAME


def dump(path, record):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2) + "\n")


def sample_offline(tmp_path, *, project="P1", variant="v1", purpose="research", status="complete"):
    run = tmp_path / "offline-P1-v1"
    run.mkdir()
    dump(run / "manifest.json", {
        "project_id": project, "run_id": run.name, "variant": variant,
        "source_commit": "c" * 40, "source_ref": "experiment/P1-v1-test",
        "hypothesis": "A calibration study", "purpose": purpose,
        "evidence_type": "offline", "script": "tools/offline_jobs/smoke.py",
    })
    dump(run / "metrics.json", {
        "schema": 1, "status": status,
        "primary_metric": {"name": "heldout_brier", "value": 0.25, "n": 2}
        if status == "complete" else None,
        "claim_strength": False,
    })
    dump(run / "data_split.json", {
        "schema": 1, "provenance": "synthetic offline fixture", "test_game_ids": ["a", "b"]
    })
    (run / "notes.md").write_text("No game strength claims.\n")
    dump(run / "model/weights.json", {"type": "tiny", "coefficients": [1.0, 2.0]})
    (run / "predictions").mkdir()
    (run / "predictions/rows.jsonl").write_text('{"id":"a","p":0.4}\n')
    return run


@pytest.mark.parametrize("id", ["P1", "P5", "P9", "A01", "C08", "F99", "Infra"])
def test_valid_project_and_legacy_id(id):
    assert research_id(id) == id


@pytest.mark.parametrize("id", ["P0", "P10", "P99", "F100", "Z01", "../P1", "P1/x"])
def test_reject_noncanonical_research_id(id):
    with pytest.raises(ValueError):
        research_id(id)


@pytest.mark.parametrize("branch,identity", [
    ("experiment/P1-v0-pipeline-smoke", ("P1", "v0")),
    ("experiment/P9-v12-endgame", ("P9", "v12")),
    ("experiment/C01-old", ("C01", None)),
    ("experiment/Infra-archive-smoke", ("Infra", None)),
])
def test_branch_identity_backwards_compatible(branch, identity):
    assert branch_identity(branch) == identity


@pytest.mark.parametrize("branch", [
    "main", "infra/P1-v1-test", "experiment/P10-v1-test",
    "experiment/P1-test", "experiment/P1-v-foo", "experiment/P1-v1",
    "experiment/P1-v1-../",
])
def test_reject_bad_branches(branch):
    with pytest.raises(ValueError):
        branch_identity(branch)


def test_offline_archive_contains_complete_model_and_prediction_evidence(tmp_path):
    run = sample_offline(tmp_path)
    path, checksum = archive(run, tmp_path / "out", "P1")
    assert hashlib.sha256(path.read_bytes()).hexdigest() == checksum
    data = verify(path)
    assert data["research_id"] == "P1"
    assert data["variant"] == "v1"
    assert data["evidence_type"] == "offline"
    assert data["primary_metric"]["name"] == "heldout_brier"
    assert data["valid_complete_run"] is True
    with tarfile.open(path, "r:gz") as tar:
        assert "run/model/weights.json" in tar.getnames()
        assert "run/predictions/rows.jsonl" in tar.getnames()
    other, other_sha = archive(run, tmp_path / "other", "P1")
    assert other_sha == checksum
    assert other.read_bytes() == path.read_bytes()


def test_offline_synthetic_smoke_has_explicit_no_scientific_claim(tmp_path):
    run = sample_offline(tmp_path, purpose="smoke")
    output, _ = archive(run, tmp_path / "out", "P1")
    assert "not evidence of research or playing strength" in verify(output)["conclusion"]


def test_offline_failure_preserved_but_not_interpreted_as_success(tmp_path):
    run = sample_offline(tmp_path, status="failed")
    out, _ = archive(run, tmp_path / "out", "P1")
    data = verify(out)
    assert data["valid_complete_run"] is False
    assert data["status"] == "failed"


def test_offline_mismatched_identity_rejected(tmp_path):
    run = sample_offline(tmp_path)
    with pytest.raises(ValueError, match="identity mismatch"):
        evidence(run, "P2")


def test_offline_symlink_refused(tmp_path):
    run = sample_offline(tmp_path)
    (run / "model/alias").symlink_to(run / "notes.md")
    with pytest.raises(ValueError, match="symlink"):
        evidence(run, "P1")


def test_offline_archive_checksum_fails_on_modified_member(tmp_path):
    run = sample_offline(tmp_path)
    out, _ = archive(run, tmp_path / "out", "P1")
    # Verification checks each archive member, not just the tarball SHA.
    import io
    with tarfile.open(out, "r:gz") as src:
        items = [(entry.name, src.extractfile(entry).read()) for entry in src]
    corrupted = tmp_path / "corrupted.tar.gz"
    with tarfile.open(corrupted, "w:gz") as tar:
        for name, contents in items:
            if name == "run/notes.md":
                contents = b"tampered but same length"
            member = tarfile.TarInfo(name)
            member.size = len(contents)
            tar.addfile(member, io.BytesIO(contents))
    with pytest.raises(ValueError, match="checksum"):
        verify(corrupted)


def test_project_game_archive_with_tracked_variant(tmp_path):
    run = tmp_path / "game-P1"
    (run / "replays").mkdir(parents=True)
    settings = {"id": run.name, "project_id": "P1", "variant": "v1",
                "candidate": "eBotI", "baseline": "obscuro_v4",
                "hypothesis": "A project archive smoke", "games": 2,
                "base": 24, "increment": 0.1, "purpose": "smoke"}
    dump(run / "manifest.json", {"commit": "a" * 40, "ref": "experiment/P1-v1-test",
                                "settings": settings})
    dump(run / "registry.json", {"id": run.name, "commit": "a" * 40})
    dump(run / "report.json", {"scheduled": 2, "recorded": 2, "invalid": 0,
                             "failure_codes": {}, "worker_exit_codes": [0],
                             "overall": {"score_rate": 0.5},
                             "complete_pair_score_interval_95": None})
    (run / "report.md").write_text("Smoke\n")
    for i in [1, 2]:
        dump(run / "replays" / f"{i:04d}.json",
             {"experimentGame": {"game": i, "replay": f"replays/{i:04d}.json"}})
    out, _ = game_archive(run, tmp_path / "out", "P1")
    meta = game_verify(out)
    assert meta["variant"] == "v1"
    assert meta["purpose"] == "smoke"
    assert "not evidence" in meta["conclusion"]


def test_project_archive_rejects_missing_version(tmp_path):
    run = sample_offline(tmp_path, variant=None)
    with pytest.raises(ValueError, match="variants"):
        evidence(run, "P1")


def test_offline_script_config_validation_rejects_untracked_or_wrong_branch(monkeypatch, tmp_path):
    from tools import run_offline_experiment as runner
    monkeypatch.setattr(runner, "git", lambda *args: "tracked")
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    (tmp_path / "tools/offline_jobs").mkdir(parents=True)
    (tmp_path / "tools/offline_jobs/smoke.py").write_text("# executable fixture\n")
    good = {"project_id": "P1", "variant": "v0", "purpose": "smoke",
            "hypothesis": "synthetic test", "script": "tools/offline_jobs/smoke.py", "seed": 3}
    assert validate_offline_config(good, "experiment/P1-v0-archive") == good
    with pytest.raises(ValueError, match="branch"):
        validate_offline_config(good, "experiment/P2-v0-archive")
    with pytest.raises(ValueError, match="under tools"):
        validate_offline_config({**good, "script": "../../unsafe.py"}, "experiment/P1-v0-archive")


def test_downloaded_release_bundle_full_round_trip(tmp_path):
    from tools.verify_research_archive import verify_bundle
    run = sample_offline(tmp_path)
    archive_file, _ = archive(run, tmp_path / "released", "P1")
    stem = archive_file.name[:-len(".tar.gz")]
    folder = archive_file.parent
    index = verify_bundle(archive_file, folder / (stem + ".sha256"),
                          folder / (stem + ".json"))
    assert index["run_id"] == run.name
    assert index["variant"] == "v1"


def test_downloaded_release_bundle_detects_tampered_sidecar_and_catalog(tmp_path):
    from tools.verify_research_archive import verify_bundle
    run = sample_offline(tmp_path)
    archive_file, _ = archive(run, tmp_path / "released", "P1")
    stem = archive_file.name[:-len(".tar.gz")]
    folder = archive_file.parent
    sidecar = folder / (stem + ".sha256")
    catalog = folder / (stem + ".json")
    original = sidecar.read_text()
    sidecar.write_text("0" * 64 + "  " + archive_file.name + "\n")
    with pytest.raises(ValueError, match="SHA-256"):
        verify_bundle(archive_file, sidecar, catalog)
    sidecar.write_text(original)
    data = json.loads(catalog.read_text())
    data["source_commit"] = "f" * 40
    dump(catalog, data)
    with pytest.raises(ValueError, match="identity mismatch"):
        verify_bundle(archive_file, sidecar, catalog)


def test_release_permission_denial_falls_back_to_verified_git_branch(monkeypatch, tmp_path):
    from tools import persist_research_evidence as publisher
    run = sample_offline(tmp_path, project="P1", variant="v1", purpose="research")
    new = tmp_path / "actions-123-1"
    run.rename(new)
    manifest = json.loads((new / "manifest.json").read_text())
    manifest["run_id"] = new.name
    dump(new / "manifest.json", manifest)
    archive(new, tmp_path / "bundle", "P1")
    stored = {}

    def no_release(*args):
        raise RuntimeError("HTTP 403: Resource not accessible by integration")

    def fake_gh(*args, stdin=None):
        if args[0] == "--method" and args[1] == "PUT":
            dest = args[2].split("/contents/", 1)[1]
            assert dest not in stored
            stored[dest] = json.loads(stdin)["content"]
            return {"content": {"path": dest}}
        assert args[0].startswith("repos/") and "/contents/" in args[0]
        dest = args[0].split("/contents/", 1)[1].split("?ref=", 1)[0]
        if dest not in stored:
            raise RuntimeError("Missing fake remote file " + dest)
        return {"content": stored[dest], "encoding": "base64"}

    monkeypatch.setattr(publisher, "gh_cli", no_release)
    monkeypatch.setattr(publisher, "gh", fake_gh)
    storage, location = publisher.publish(
        tmp_path / "bundle", "offline", "owner/repository",
        "experiment/P1-v1-test", "c" * 40, "actions-123-1")
    assert storage["storage"] == "git-branch"
    assert storage["release_url"] is None
    assert "research/runs/research-offline-evidence-123-1.json" in location
    saved = [k for k in stored if k.startswith("research/archives/")]
    assert len(saved) == 3
    for k in saved:
        assert base64.b64decode(stored[k])


def test_archive_publisher_rejects_other_revision(monkeypatch, tmp_path):
    from tools import persist_research_evidence as publisher
    run = sample_offline(tmp_path)
    archive(run, tmp_path / "bundle", "P1")
    with pytest.raises(ValueError, match="workflow source"):
        publisher.publish(tmp_path / "bundle", "offline",
                          "owner/repository", "experiment/P1-v1-test",
                          "a" * 40, run.name)
