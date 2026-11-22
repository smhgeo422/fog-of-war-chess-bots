# Research decisions and rationale

## 2026-11-22 — Storage design
Decision: keep readable ideas, experiment conclusions, contribution evidence and the report outline in Git under `research/`. Use the existing `experiments/` runner and manifest outputs for reproducibility. Save bulky replay archives privately in durable storage, with indexed links and SHA-256 hashes.

Reason: code+explanations should be versioned together, while large artifacts would bloat Git; GitHub Actions artifacts expire.

Resolved blocker (historical note): Codex originally used `Shad0wSeven` with read-only access. The `smhgeo422` GitHub account was subsequently connected and verified with write permissions. Phase 2 source was recovered byte-for-byte and published in draft PR #2; hosted CI [45059968560](https://github.com/smhgeo422/fog-of-war-chess-bots/actions/runs/45059968560) passed 235 tests and an integration smoke. This restored source is a new Git commit, while the original commit history remains safely archived in its private Git bundle.

Remaining operational follow-ups: keep long-running experiment artifacts in durable storage (GitHub Actions retention is finite); independently validate full-length statistical tournaments; get explicit authorization before any official arena submission. The temporary `research-validation` CI had two environment-specific build-script test failures (6 logged compiler invocations where 5 were expected); it was superseded by the full 235-test Phase 2 validation workflow, not silently interpreted as a pass.
