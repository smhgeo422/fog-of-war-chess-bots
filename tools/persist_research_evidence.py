#!/usr/bin/env python3
"""Publish *verified* run evidence, preferring draft Releases with Git fallback.

A GitHub-hosted Action's GITHUB_TOKEN can occasionally be prohibited from
creating Releases despite contents:write. A complete evidence bundle must not be
considered archived based on an ephemeral Actions artifact alone. If Release
publication fails, store the exact tar.gz, SHA256 and catalog as content-addressed
files on the *experiment branch* and read them back to verify checksums.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

try:
    from .verify_research_archive import verify_bundle
except ImportError:  # direct CLI execution
    from verify_research_archive import verify_bundle

MAX_GIT_FALLBACK_BYTES = 25_000_000


def gh(*args, stdin=None):
    p = subprocess.run(["gh", "api", *args], input=stdin, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        raise RuntimeError("GitHub API call failed: " + p.stderr[-1200:])
    return json.loads(p.stdout) if p.stdout.strip() else {}


def gh_cli(*args):
    p = subprocess.run(["gh", *args], text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    if p.returncode:
        raise RuntimeError("GitHub release action failed: " + p.stderr[-1200:])
    return p.stdout.strip()


def checked_files(folder):
    a = list(folder.glob("*.tar.gz"))
    h = list(folder.glob("*.sha256"))
    c = list(folder.glob("*.json"))
    n = list(folder.glob("*.md"))
    if any(len(x) != 1 for x in (a, h, c, n)):
        raise ValueError("exactly one archive, sidecar, catalog, and notes required")
    verify_bundle(a[0], h[0], c[0])
    return a[0], h[0], c[0], n[0]


def upload_branch(repo, branch, tag, files):
    if files[0].stat().st_size > MAX_GIT_FALLBACK_BYTES:
        raise ValueError("archive exceeds git-fallback budget; split experiment")
    mapping = {}
    for path in files:
        dest = "research/archives/" + tag + "/" + path.name
        body = {
            "message": "Preserve verified research evidence " + tag + " / " + path.name,
            "branch": branch,
            "content": base64.b64encode(path.read_bytes()).decode("ascii"),
        }
        gh("--method", "PUT", "repos/" + repo + "/contents/" + dest,
           "--input", "-", stdin=json.dumps(body))
        mapping[path.name] = dest
    with TemporaryDirectory() as temp:
        root = Path(temp)
        for source in files:
            meta = gh("repos/" + repo + "/contents/" + mapping[source.name] +
                      "?ref=" + branch)
            raw = meta.get("content")
            if meta.get("encoding") != "base64" or not isinstance(raw, str):
                # Contents API omits large blobs; retrieve by stored blob SHA.
                blob = gh("repos/" + repo + "/git/blobs/" + str(meta["sha"]))
                raw = blob.get("content")
                if blob.get("encoding") != "base64":
                    raise ValueError("GitHub did not return verifiable blob bytes")
            actual = base64.b64decode(raw)
            if actual != source.read_bytes():
                raise ValueError("remote GitHub blob bytes differ: " + source.name)
            (root / source.name).write_bytes(actual)
        verify_bundle(root / files[0].name, root / files[1].name,
                      root / files[2].name)
    return {
        "storage": "git-branch",
        "archive_urls": {
            name: "https://github.com/" + repo + "/blob/" + branch + "/" + dest
            for name, dest in mapping.items()
        },
        "release_url": None,
    }


def upload_release(repo, tag, sha, files, notes):
    gh_cli("release", "create", tag, "--repo", repo, "--target", sha, "--draft",
           "--title", "[research evidence] " + files[0].name,
           "--notes-file", str(notes), *(str(x) for x in files))
    with TemporaryDirectory() as temp:
        gh_cli("release", "download", tag, "--repo", repo, "--dir", temp)
        root = Path(temp)
        verify_bundle(root / files[0].name, root / files[1].name,
                      root / files[2].name)
    result = gh_cli("release", "view", tag, "--repo", repo, "--json", "url",
                    "--jq", ".url")
    return {"storage": "draft-release", "archive_urls": {}, "release_url": result}


def index(repo, branch, tag, catalog, storage):
    record = json.loads(catalog.read_text(encoding="utf-8"))
    record.update(storage)
    record["release_tag"] = tag
    record["verified_remote"] = True
    record["archive_sha256"] = record["sha256"]
    path = "research/runs/" + tag + ".json"
    body = {
        "message": "Record verified archived research evidence " + tag,
        "branch": branch,
        "content": base64.b64encode((json.dumps(record, indent=2, sort_keys=True)
                                     + "\n").encode()).decode(),
    }
    gh("--method", "PUT", "repos/" + repo + "/contents/" + path,
       "--input", "-", stdin=json.dumps(body))
    remote = gh("repos/" + repo + "/contents/" + path + "?ref=" + branch)
    data = json.loads(base64.b64decode(remote["content"]))
    if data.get("sha256") != record["sha256"] or not data.get("verified_remote"):
        raise ValueError("GitHub research index verification failed")
    return "https://github.com/" + repo + "/blob/" + branch + "/" + path


def publish(folder, evidence_type, repo, branch, source_sha, run_id):
    archive, sidecar, catalog, notes = checked_files(folder)
    manifest = json.loads(catalog.read_text(encoding="utf-8"))
    if manifest.get("source_commit") != source_sha or manifest.get("run_id") != run_id:
        raise ValueError("published evidence does not match workflow source/replay")
    if evidence_type == "offline":
        if manifest.get("evidence_type") != "offline":
            raise ValueError("offline job cannot publish game evidence")
    elif manifest.get("evidence_type") == "offline":
        raise ValueError("game job cannot publish offline evidence")
    tag = ("research-offline-evidence-" if evidence_type == "offline"
           else "research-evidence-") + run_id[len("actions-"):]
    files = (archive, sidecar, catalog)
    try:
        storage = upload_release(repo, tag, source_sha, files, notes)
    except RuntimeError as exc:
        print("WARNING: draft Release unavailable; trying permanent branch-backed "
              "archive instead: " + str(exc), file=sys.stderr)
        storage = upload_branch(repo, branch, tag, files)
    location = index(repo, branch, tag, catalog, storage)
    print(json.dumps({"release_tag": tag, "source_sha": source_sha,
                      "storage": storage["storage"], "index_url": location,
                      "remote_evidence_verified": True}, sort_keys=True))
    return storage, location


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive-dir", type=Path, required=True)
    p.add_argument("--type", choices=["game", "offline"], required=True)
    args = p.parse_args()
    repo = os.environ["GITHUB_REPOSITORY"]
    branch = os.environ["GITHUB_REF_NAME"]
    sha = os.environ["GITHUB_SHA"]
    rid = "actions-" + os.environ["GITHUB_RUN_ID"] + "-" + os.environ["GITHUB_RUN_ATTEMPT"]
    publish(args.archive_dir.resolve(), args.type, repo, branch, sha, rid)


if __name__ == "__main__":
    main()
