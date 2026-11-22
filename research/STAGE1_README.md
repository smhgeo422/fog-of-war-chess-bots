# Stage 1 COMPLETE — versioned P1–P9 research evidence pipeline

**Completed 2026-11-22.** Planning and infrastructure only. No research algorithm, strength tournament, official arena submission, modification to frozen bots or merge into main. The implementation is on branch 'infra/p1-p9-research-pipeline' in [draft PR #5](https://github.com/smhgeo422/fog-of-war-chess-bots/pull/5), based on the Stage 0 research-planning branch.

## Implemented

- 'tools/research_ids.py' validates canonical project IDs P1..P9 and version IDs v0/v1/v2... while preserving older A01..F99 and Infra identifiers.
- '.github/workflows/experiments.yml' derives the project ID/version from experiment/P1-vN-description and checks it against tracked experiment config. Commit marker '[run experiment]' launches games; '[run offline]' launches a separate offline study. No marker triggers any expensive study.
- 'tools/experiment.py' and 'tools/archive_research_run.py' record the matching project/variant, source revision, hypothesis, binary/engine hashes, config, per-game referee replays, matched colors, outcome/error metrics, and complete checksummed archive.
- 'tools/run_offline_experiment.py' executes a committed script under tools/offline_jobs/ with exact project, version and seed identity. 'tools/archive_offline_run.py' preserves non-game data including manifest, held-out metric and sample count, split provenance, model files, predictions, failures and notes. It rejects missing or inconsistent evidence and symlinks.
- 'tools/verify_research_archive.py' independently validates tar.gz, SHA-256 sidecar, JSON catalog and embedded per-file hashes.
- 'tools/persist_research_evidence.py' prefers a draft GitHub Release, **downloads its assets back and verifies them**, then commits the permanent research/runs/*.json index. If release creation fails, it has a Git-branch storage fallback under research/archives/<tag>/; the fallback is verified by simulation/unit tests, but a successful hosted fallback has NOT been demonstrated.
- 'research/projects.json' records the nine independent hypotheses and their evidence pointers without falsely marking any idea implemented; 'research/STAGE_STATUS.json' records completed stages and next action. 'experiments/RESEARCH_PIPELINE.md' documents actual use.

## Hosted acceptance evidence

**Full infrastructure CI:** [run 45071250294](https://github.com/smhgeo422/fog-of-war-chess-bots/actions/runs/45071250294), successful, **282 tests passed**. This measures build/correctness infrastructure, not chess-playing strength.

**Hosted dual experiment smoke:** [run 45071213893](https://github.com/smhgeo422/fog-of-war-chess-bots/actions/runs/45071213893), **all three jobs successful** (checks, game experiment, offline experiment) on branch 'experiment/P1-v0-pipeline-smoke', exact source revision 'eae833fd78bab8f580f5ca9408b801d708ebe533'.

- Game: 2/2 valid capped color-swapped games, purpose smoke, no strength claim. Permanent [game index](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/experiment/P1-v0-pipeline-smoke/research/runs/research-evidence-45071213893-1.json). GitHub draft Release tag 'research-evidence-45071213893-1', with three assets (.tar.gz, .sha256 and .json). Archive SHA256 '33953ce41daaa324e9fd6575f5fb6e6c81f98b57bbc42081ea0274e80913af87'.
- Offline: synthetic fake observations, model weights and predictions, provenance manifest, primary-metric placeholder. Permanent [offline index](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/experiment/P1-v0-pipeline-smoke/research/runs/research-offline-evidence-45071213893-1.json). Draft Release tag 'research-offline-evidence-45071213893-1', three assets. Archive SHA256 '3614a7c521d9274e12f9f7b53a9866f0643454f880bc25c90c1f6ac140479ddf'.
- BOTH records say project=P1, version=v0, purpose=smoke, valid_complete_run=true, verified_remote=true and storage=draft-release. Both point to the exact same source revision. They are not evidence that P1's algorithm has been implemented.

## Failures detected and corrected

The first [integration attempt 45069998818](https://github.com/smhgeo422/fog-of-war-chess-bots/actions/runs/45069998818) failed to start the offline job because its fresh runner lacked .venv. This was corrected by installing the locked Python environment in the offline job. Initial attempts also encountered an intermittent GitHub HTTP 403 when creating Releases despite contents:write, although earlier and later jobs succeeded. The release-or-Git fallback was added so a denied Release does not quietly become a claimed permanent archive. **The fallback's permission-handling is covered by a simulated unit test; the hosted successful acceptance used the draft Release path.** Failed early runs remain visible; they are not omitted or misrepresented.

## Stage 2 handoff

Stage 2, when explicitly requested by the user, establishes reference B0 frozen v4, B1 parity-configured eBotI, B2 current eBotI, validates action-level controls and referee observation/replay reconstruction, and freezes a leakage-safe train/development/holdout corpus and first match configs. Only Stage 3 begins independent algorithm implementations. All later implementations use new v1+ branches; the v0 smoke config is not a research variant. No schedules or automatic stage advancement.
