# Stage 0 complete: nine profound research directions, before implementation

**Completed 2026-11-22 — planning/evidence-design only.** The research project will be executed only when the user explicitly requests the next stage. No timetable, unattended agent recurrence, experimental bot code, match launches, main merge, or official arena submission is authorized by this document.

## Where to start

1. [Nine original directions, literature anchors and cross-project novelty boundaries](consolidated_contributions.md)
2. [Fresh annotated primary-source literature review and prior team evidence](stage0_literature_review.md)
3. [Original 46 ideas mapped losslessly into 9 directions plus 3 supporting items](consolidated_crosswalk.json)
4. [Preregistered metrics, controls, splits, statistical and evidence standards](stage0_preregistration.md)
5. [Scientific dependency map and exact per-project readiness gates](stage0_dependency_map.md)
6. [Machine-readable scientific experiment cards](stage0_experiment_cards.json)
7. [Eight-stage execution plan, excluding final report](execution_plan_nine_projects.md)
8. [Persistent stage-completion and next-stage tracker](STAGE_STATUS.json)

## Project specifications and research-version evidence ledgers

| Project | Deep proposal | Evidence ledger | Scientific object |
|---|---|---|---|
| P1 | [Belief reconstruction](projects/P1/proposal.md) | [Versions](projects/P1/variants.jsonl) | Hidden-state posterior |
| P2 | [Opponent policy](projects/P2/proposal.md) | [Versions](projects/P2/variants.jsonl) | Hidden opponent action distribution |
| P3 | [Contingent tactical planning](projects/P3/proposal.md) | [Versions](projects/P3/variants.jsonl) | Observation-consistent future action policy |
| P4 | [Instrumental information value](projects/P4/proposal.md) | [Versions](projects/P4/variants.jsonl) | Game information flow and future decision utility |
| P5 | [Catastrophic tactical risk](projects/P5/proposal.md) | [Versions](projects/P5/variants.jsonl) | Terminal king/material-event probability and action value |
| P6 | [Bounded game-theoretic solver](projects/P6/proposal.md) | [Versions](projects/P6/variants.jsonl) | Mixed-strategy security/exploitability in a local game |
| P7 | [Learned continuation value](projects/P7/proposal.md) | [Versions](projects/P7/variants.jsonl) | Learned long-horizon residual to Stockfish evaluation |
| P8 | [Metareasoning with hard clock](projects/P8/proposal.md) | [Versions](projects/P8/variants.jsonl) | Value and allocation of computations |
| P9 | [Certified FoW endgames](projects/P9/proposal.md) | [Versions](projects/P9/variants.jsonl) | Restricted belief-state reachability/capture certificate |

All nine proposal files contain mathematically defined objectives and algorithm mechanisms, repository touchpoints, version roadmaps, test counterexamples, evaluation metrics, and explicit conditions for rejection. They are distinct scientific hypotheses, not feature collections; later combinations count as **integration**, not a new research direction.

### What Stage 0 checked

- The 46 legacy IDs map **exactly once** in the crosswalk; there are nine independent research projects and F01/F07/F08 explicitly designated supporting engineering.
- All nine proposal files exist, each with >850 words and formalism, experiments, versions, and negative-result criteria.
- The library and source-tree literature audit explicitly identifies the existing team implementations and historically rejected variants so prior authors' work is not reattributed.
- The preregistration distinguishes primary offline/scientific outcomes from tournament playing strength, sets the baseline/control requirements, and keeps scientific verdicts honest.
- The Stage 0 files add no bot implementation or research run. The planning work is in **draft PR #4** targeting the infrastructure branch.

### What Stage 0 intentionally did not do

- Do not assert any of P1–P9 is a successful implementation or performance improvement.
- Do not assert current eBotI is v4-equivalent until the actual Stage 2 action-parity test.
- Do not generate features using retrospective full-board truth that cannot be observed during play.
- Do not promise all nine variants can be proven and tested at full clock in one day.
- Do not merge unreviewed changes into the team's branch or submit to the arena.

## Next user-controlled stage

**Stage 1: upgrade the experimental infrastructure to recognize P1–P9 project/version branches, archive offline evidence and model artifacts in addition to games, preserve existing A01..F08/Infra compatibility, and validate the full checksummed pipeline with a minimal non-strength smoke.** No need to schedule work; the user can say **"next stage"** whenever ready. The 'STAGE_STATUS.json' file is the persistent record to consult when resuming in a new chat.
