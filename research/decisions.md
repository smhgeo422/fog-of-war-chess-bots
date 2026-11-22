# Research decisions and rationale

## 2026-11-22 — Storage design
Decision: keep readable ideas, experiment conclusions, contribution evidence and the report outline in Git under `research/`. Use the existing `experiments/` runner and manifest outputs for reproducibility. Save bulky replay archives privately in durable storage, with indexed links and SHA-256 hashes.

Reason: code+explanations should be versioned together, while large artifacts would bloat Git; GitHub Actions artifacts expire.

Resolved blocker (historical note): Codex originally identified `Shad0wSeven`, with read-only access to `smhgeo422/fog-of-war-chess-bots`. Infrastructure is committed in a local bundle, not published. Do not claim hosted CI exists until verified.
