# Instructions for research coding agents

This fork is the **experimental** Fog of War Chess repository. Before working on a research task, read `research/idea_backlog.md`, `research/experiment_registry.jsonl`, `research/report_outline.md`, `experiments/AUTOMATION.md`, `APPROACHES.md`, and the relevant `docs/research/` notes. Preserve the distinction between earlier team work and new contributions.

## Scope and safety

- Work on an isolated branch based on the latest validated experimental branch; never modify `bots/obscuro_v2`, `bots/obscuro_v3`, or `bots/obscuro_v4`, or the official team upstream.
- Never submit/activate bots in the official MIT arena without explicit authorization. Never expose or commit team tokens, credentials, or logs containing secrets.
- Do not merge into `main` on your own. Use draft PRs and preserve old bot behavior.
- When implementing a method, inspect the existing implementation before claiming novelty. Existing `FOW_HANG` and `FOW_INFOSET` should be ablated/extended, not represented as original-from-scratch ideas.
- Keep a clean reproducible Git commit for every tested candidate. Prefer direct comparisons against frozen v4 and the current eBotI profile, with a documented control that isolates the new change.
- Never infer experimental strength from capped smoke games, a single short match, or an unresolved confidence interval. Record failed and negative experiments.

## One research item at a time

1. Select the next appropriate uncompleted idea, respecting the priority and dependency groups in `research/idea_backlog.md`. Verify its current status in `research/experiment_registry.jsonl` and existing source files.
2. Write a falsifiable hypothesis, scope of implementation, baseline, planned ablations, compute budget, and measurable success/failure diagnostics.
3. Implement and write meaningful correctness and regression tests; do not alter the frozen bots or trust unverified external full-board information during play.
4. Add a committed `experiments/configs/<ID>.json` file. On `experiment/<ID>-...` branches, a commit message containing `[run experiment]` triggers the hosted CI and experiment runner.
5. Review the completed job, complete replay evidence, confidence intervals, failure codes, and runtime limits. Locate its draft release and `research/runs/<release-tag>.json` record before declaring that the run was stored.
6. Continue with additional seeds/opponents and larger 180+2 matches only for plausible candidates. Do not promote variants on noisy short-clock evidence.
7. Update the registry, `research/contributions.md`, `research/results_index.md`, and `research/report_outline.md` with source- and run-linked evidence. AI assistance must be disclosed as such; do not assign work to a person without evidence.
8. Preserve the branch and draft PR even for unsuccessful ideas. Write a short scientific conclusion: what changed, what was measured, why the hypothesis survived or failed, and what should be tried next.

## Long-term continuity

A session is not the source of truth. Recover the next task from the registry and the published branches, and recover previous results from `research/runs/` plus the draft GitHub Releases. If an agent cannot read a particular archive or continue a Codex task, make the blocked state explicit and leave a precise resumable checkpoint in Git; never claim work was performed asynchronously without actually running it.

**Project goal:** produce a reproducible, evidence-rich final bot and report, including the negative experiments, before the course deadlines. Do not run all 46 heavyweight tournaments indiscriminately; screen cheaply and reserve full 180+2 trials for candidates with genuine supporting evidence.
