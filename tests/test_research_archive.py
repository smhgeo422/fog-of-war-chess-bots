"""Evidence archival is deterministic, complete, and refuses inconsistent results."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tarfile

import pytest

from tools.archive_research_run import archive, evidence, verify


def make_run(tmp_path: Path, *, purpose="strength") -> Path:
    run = tmp_path / "run-C01-0001"
    (run / "replays").mkdir(parents=True)
    settings = {
        "id": run.name, "candidate": "eBotI", "baseline": "obscuro_v4",
        "games": 2, "base": 36, "increment": 0.4,
        "max_plies": 1000, "purpose": purpose,
    }
    revision = "a" * 40
    (run / "manifest.json").write_text(json.dumps({
        "commit": revision, "ref": "experiment/C01", "settings": settings}))
    (run / "registry.json").write_text(json.dumps({
        "id": run.name, "commit": revision, "conclusion": "pending"}))
    (run / "report.json").write_text(json.dumps({
        "scheduled": 2, "recorded": 2, "invalid": 0,
        "worker_exit_codes": [0], "failure_codes": {},
        "overall": {"score_rate": 0.75},
        "complete_pair_score_interval_95": None,
    }))
    (run / "report.md").write_text("# Test report\n")
    for i in (1, 2):
        file = run / "replays" / f"{i:04d}.json"
        file.write_text(json.dumps({"experimentGame": {
            "game": i, "replay": f"replays/{i:04d}.json", "score": 1 if i == 1 else 0.5
        }}))
    return run


def test_archive_contains_all_original_evidence_and_hashes(tmp_path):
    run = make_run(tmp_path)
    first = tmp_path / "first"
    archive_file, checksum = archive(run, first, "C01")
    assert hashlib.sha256(archive_file.read_bytes()).hexdigest() == checksum
    metadata = verify(archive_file)
    assert metadata["research_id"] == "C01"
    assert metadata["source_commit"] == "a" * 40
    assert metadata["valid_complete_run"] is True
    assert metadata["score_rate"] == 0.75
    with tarfile.open(archive_file, "r:gz") as tar:
        assert tar.extractfile("run/report.md").read() == b"# Test report\n"
        assert "run/replays/0001.json" in tar.getnames()
        assert "run/replays/0002.json" in tar.getnames()
    assert (first / (archive_file.stem.replace(".tar", "") + ".json")).exists()


def test_repeat_produces_identical_bytes(tmp_path):
    run = make_run(tmp_path)
    a, sha_a = archive(run, tmp_path / "a", "C01")
    b, sha_b = archive(run, tmp_path / "b", "C01")
    assert sha_a == sha_b
    assert a.read_bytes() == b.read_bytes()


def test_smoke_cannot_be_reported_as_strength(tmp_path):
    run = make_run(tmp_path, purpose="smoke")
    result, _ = archive(run, tmp_path / "output", "Infra")
    metadata = verify(result)
    assert metadata["purpose"] == "smoke"
    assert "not evidence of playing strength" in metadata["conclusion"]


def test_missing_run_data_is_rejected(tmp_path):
    run = make_run(tmp_path)
    (run / "report.md").unlink()
    with pytest.raises(ValueError, match="missing run evidence"):
        evidence(run, "C01")


def test_replay_count_disagreement_is_rejected(tmp_path):
    run = make_run(tmp_path)
    (run / "replays/0002.json").unlink()
    with pytest.raises(ValueError, match="recorded/replay"):
        evidence(run, "C01")


def test_replay_embedded_id_mismatch_is_rejected(tmp_path):
    run = make_run(tmp_path)
    (run / "replays/0001.json").write_text(json.dumps({
        "experimentGame": {"game": 8, "replay": "replays/0001.json"}}))
    with pytest.raises(ValueError, match="embedded game record"):
        evidence(run, "C01")


def test_unsupported_research_id_is_rejected(tmp_path):
    run = make_run(tmp_path)
    with pytest.raises(ValueError, match="research ID"):
        evidence(run, "../C01")


def test_symlink_evidence_is_rejected(tmp_path):
    run = make_run(tmp_path)
    (run / "replays/extra.json").symlink_to(run / "replays/0001.json")
    # A symlink cannot be included in an evidence archive.
    with pytest.raises(ValueError):
        evidence(run, "C01")


def test_failed_run_is_preserved_but_not_validated(tmp_path):
    run = make_run(tmp_path)
    report = json.loads((run / "report.json").read_text())
    report["failure_codes"] = {"component_failure": 1}
    (run / "report.json").write_text(json.dumps(report))
    result, _ = archive(run, tmp_path / "output", "C01")
    metadata = verify(result)
    assert not metadata["valid_complete_run"]
    assert "do not infer strength" in metadata["conclusion"]
