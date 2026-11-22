# P1–P9 experimental infrastructure (Stage 1)

**Scope:** This document explains the tested mechanics and the remaining gates. It does **not** schedule research, authorize autonomous work, merge into main, or submit to the MIT arena. Algorithms and full-clock tournaments happen only after the user asks for those stages. Existing A01..F99 and Infra archives remain valid.

## Identity conventions

- Nine scientific project IDs: P1 through P9, frozen by the Stage 0 work.
- Branch: experiment/P1-v1-candidate-short-description; version is the first segment after project ID. For further changes, create experiment/P1-v2-... instead of rewriting a scientific outcome. v0 is reserved for integration smoke / no research claim.
- Each branch tracks its own game config at experiments/configs/P1.json, with project_id:"P1", variant:"v1" (match branch), plus ID, hypothesis, candidate, baseline, seeded paired games, clocks and purpose. GitHub workflow launches this when a push commit has the exact marker [run experiment].
- For offline evidence, each branch instead/as well tracks experiments/offline/P1.json, whose project_id and variant match the branch. It names a **committed** Python script under tools/offline_jobs/ that accepts --run and --seed. Commit with marker [run offline]. Research scripts are implemented only in later stages; the sole Stage 1 job is tools/offline_jobs/smoke.py, with purpose: smoke and synthetic data.
- A commit can contain both markers to launch an independent paired game smoke and synthetic offline evidence in parallel; expensive real tournaments must be expressly authorized by the user. Creating the branch or editing code without the exact marker runs only checks.
- The CI runner checks config and branch identity, source commit, binary version/network digest, worker/core limits and caught failures. Experiment release and index are pushed only after re-downloading release assets and verifying archive, SHA-256 and catalog.

## What is stored in GitHub

1. Each run directory is immutable by unique ID actions-<run-number>-<attempt>. The current action source commit SHA is recorded.
2. Game runs: manifest.json, registry.json, report.json/report.md, complete referee replays, failures, full source+runtime configuration, and binary hashes. 'tools/archive_research_run.py' verifies report count, replay identities and checksums.
3. Offline runs: manifest.json, metrics.json (including status, primary_metric and sample n), data_split.json (mandatory provenance and train/test references), notes.md, plus any other files the research script creates in its run directory, including model and predictions. 'tools/archive_offline_run.py' validates and checksums *all* files; no replays are required.
4. Archive tar.gz includes an embedded run/EVIDENCE.json inventory of each file and its SHA-256, plus separate .sha256 and .json catalog. Never store credentials, unauthorized replays or private team tokens in the experiment directory.
5. The publisher first tries a **draft GitHub Release**: research-evidence-<run>-<attempt> for games; research-offline-evidence-<run>-<attempt> for offline, each with tar.gz, SHA256 and catalog. If GitHub denies release creation, the publisher instead attempts a content-addressed copy of all three files in `research/archives/<tag>/` on the experiment branch. Both are intended as durable stores; ordinary Actions artifacts expire. The branch-backed fallback has passed simulated unit tests but has **not** yet passed an independent hosted storage smoke.
6. On success, the workflow **downloads its own draft release assets back from GitHub** (or reads fallback archive files back from the branch), checks the sidecar, catalog, every contained file and metadata with tools/verify_research_archive.py, and only then commits research/runs/<release-tag>.json on the experiment branch. Entries identify `storage`, `verified_remote`, and either a `release_url` or the fallback `archive_urls`. If neither durable route verifies, the job fails instead of declaring archival complete. A failed or incomplete experiment retains a non-success scientific conclusion if its evidence is complete; no run is silently called a win.
7. The same verification command can be run locally after downloading assets, using --archive --sha256-file --catalog. Source SHA and branch link to a precise historical revision.

## Example project smoke-only config

~~~json
{
  "id": "P1-infra-smoke",
  "project_id": "P1",
  "variant": "v0",
  "hypothesis": "Verify the new project and version identity in the durable game evidence pipeline",
  "purpose": "smoke",
  "candidate": "eBotI",
  "baseline": "obscuro_v4",
  "games": 2,
  "seed": 7106,
  "base": 24,
  "increment": 0.1,
  "max_plies": 20,
  "parallel": 1
}
~~~

Place as experiments/configs/P1.json on experiment/P1-v0-pipeline-smoke and commit with [run experiment]. These two capped games **are not playing-strength data**.

The already tracked experiments/offline/P1.json invokes a deterministic synthetic integration script; its model coefficients and predictions are fake placeholders to exercise data retention. Do not use its output for P1 posterior claims.

## Later research use and safety notes

- Stage 2 defines a true game corpus, train/dev/held-out split and baseline action parity. Do not use labels from future hidden states as runtime model inputs.
- Stage 3 implements an algorithm and new script in tools/offline_jobs/, changing branch/version config from smoke to research. No generated outcome may be used to train and then validate on the same game or seed block.
- Stage 4 launches scientific experiments with precommitted seeds, source SHA and controlled CPU. More than 20 games or full-clock 180+2 evaluations require deliberate authorization. CI max runtime ~350 minutes per game job; use separately archived shards for long trials.
- Stage 7 consolidates verified catalogs across project branches; the root research/projects.json is a planning/status snapshot and **not** a magic reflection of all branches. Results must be actively retrieved and reconciled.
- The legacy 46-item backlog remains intact for provenance, but the fixed research questions are the nine P projects. Supporting engineering and integration are not tenth contributions.
- No existing v4 or team frozen bot source is modified by this Stage 1 work. No work is initiated by any schedule.
