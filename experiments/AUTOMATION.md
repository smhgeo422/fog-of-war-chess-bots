# Low-touch FoW research workflow

This setup builds on the Phase 2 runner rather than replacing it.

## What is automatic

1. Every new implementation is developed in an isolated `experiment/<ID>-<description>` Git branch. The 46 proposals and ownership/evidence fields live in `research/experiment_registry.jsonl`; existing team code is never reattributed.
2. When a commit message includes the exact token `[run experiment]`, the branch's tracked `experiments/configs/<ID>.json` is selected. GitHub Actions runs full tests, then the seeded, paired, color-balanced experiment against its declared baseline.
3. The runner preserves manifest, configuration, source SHA, binary hashes, reports, process-failure diagnostics, and the complete referee replays. The archiver verifies consistency and builds a checksummed tar.gz. Even failures are recorded as failures, not as strength evidence.
4. GitHub Actions creates a **draft GitHub Release** named `research-evidence-<run_number>-<attempt>` containing the full archive, SHA-256 file, and machine-readable catalog. These release assets are the durable replay store; ordinary Actions artifacts (30/90 days) remain convenient temporary copies.
5. The workflow creates one small `research/runs/<release_tag>.json` machine-readable index entry on the branch. This entry includes the revision, number of games, score, confidence interval, run status, and release URL. GitHub's `GITHUB_TOKEN` commits do not automatically trigger more workflows.

A config must exist and be committed before an experiment is dispatched. A branch without `[run experiment]` runs validation but not an expensive tournament. The workflow uses a single worker to avoid unrealistic CPU oversubscription.

## How to launch without manual commands

The coding agent may create or update `experiment/C01-hidden-material`, put an independently verified candidate implementation in the branch, commit `experiments/configs/C01.json`, and push a commit with the exact token `[run experiment]`. The CI workflow then starts, tests, archives the outcome, and adds its index entry automatically. For `A01` and other IDs, use the matching file name. Example:

```json
{
  "id": "C01-screen-v1",
  "hypothesis": "A controlled hidden-material penalty reduces quiet-move material loss",
  "candidate": "eBotI",
  "baseline": "obscuro_v4",
  "purpose": "strength",
  "games": 20,
  "seed": 21931,
  "base": 36,
  "increment": 0.4,
  "max_plies": 1000,
  "parallel": 1
}
```

This 20-game phase is *screening*, not decisive evidence. A positive screening result should be replicated with independent seeds and then 180+2 full matches, ideally with multiple opponents. At 20 games, even a large numerical difference may be sampling noise. We require color balance, full games, working Stockfish, comparable clock/CPU budgets, and absence of timeouts or component losses.

An experimental variant must be separately identifiable from the frozen baseline and actually change the behavior being tested. Check control-v4 parity before scoring a claim.

## Evidence standards

- Score = (wins + 0.5 * draws) / games; record both score and 95% paired bootstrap interval.
- Never conclude an improvement merely because a short tournament scored above 50%.
- Examine hidden-material losses, king captures, decision examples, clocks and invalid/rejected games.
- Preserve *negative* experiments, failed code, timeouts, and hypotheses with their source revision.
- Update `research/contributions.md` only with traceable work and correct human / AI attribution.
- Periodically update `research/report_outline.md` with strong results and informative failures; never add unverified success claims.
- No unofficial access to the MIT arena, no upload/activation without explicit authorization.
- No changes to frozen bots, upstream team repository, or main in a research branch.

## What this does NOT automate

This workflow runs *implemented* experiments. GitHub Actions cannot invent, implement and debug new algorithms on its own; an authorized coding agent still needs to perform those coding tasks. The 46 idea descriptions are an ordered research backlog, not executable programs. It is not truthful to mark them “implemented” or “tested” until corresponding branches and results exist.

Draft Releases and index entries must also be verified with an actual GitHub-hosted archive smoke test. A successful local archive alone is insufficient. The official arena remains a separately authenticated service.

## Security and cost controls

- Candidate code runs only after a tracked source commit; archive code never reads outside the configured run directory.
- Workflows use read-only tokens for tests, and contents-write only for the experiment archival job.
- Released evidence stays in *draft* state (visible to users with release access; not advertised as public releases).
- Archives have explicit size limits and SHA-256 hashes.
- Only `experiment/**` branches with the exact commit-message token start expensive experiments.
- Large-scale runs consume GitHub-hosted compute and should use staged, pre-specified game budgets.

## Unattended acceptance criteria

After a full test on an `experiment/Infra-...` branch, verify:

1. tests complete and a genuine 2-game integration match terminates cleanly;
2. a draft GitHub Release holds a tar.gz, JSON catalog and sha256 file;
3. unpacking the archive reproduces all replay files and passes `tools/archive_research_run.py` integrity checks;
4. `research/runs/<tag>.json` is committed and points to the correct release, source SHA, clock and outcomes;
5. a *new* task can independently read the branch, result index, and release evidence;
6. there is no user action required for experiments beyond choosing/assigning research tasks to a coding agent.

Full ongoing independent coding across 46 hypotheses is still a separate capability and should never be implied by passing this infrastructure check.
