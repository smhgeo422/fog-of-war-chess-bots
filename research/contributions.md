# Individual contributions — evidence log

**Status:** Unassigned future work; historical team contributions must be credited to original authors. Fill only with verified evidence.

| Date | Person/role | Experiment ID | Specific contribution | Evidence (commit/PR/run/file) | AI assistance used | Verified by |
|---|---|---|---|---|---|---|
| 2026-11-22 | Research planning (provisional; not a tested implementation) | All | Developed research agenda and working report outline in ChatGPT | `research/idea_backlog.md`, `research/report_outline.md` | ChatGPT assisted substantially with research planning and drafting | Documentation only |
| 2026-11-22 | Infrastructure agent (not yet attributed to individual author) | Infra | Codex implemented experiment tooling, then the source was restored to the fork from its verified archive | Original Git bundle commit `01f4051`; restored blobs in [draft PR #2](https://github.com/smhgeo422/fog-of-war-chess-bots/pull/2); [hosted 235-test CI](https://github.com/smhgeo422/fog-of-war-chess-bots/actions/runs/45059968560) | Codex, ChatGPT assisted with restoration and setup | Hosted 235 tests and capped integration smoke passed |

*Add one row per substantive contribution. Do not turn ideas, prompts, or already-written teammate code into claims of new implementation.*


## Stage 3 AI-assisted algorithmic prototype attribution (2026-11-22)

The project owner requested nine independent, profound scientific research directions; Stage 0 documented their motivations from the team's existing code, proposals and literature. Stage 3 committed **new assistant-generated Python toy algorithm kernels** and tests under tools/stage3/P1.py through P9.py, with independent evidence on experiment/Pn-v1-toy-kernel branches. These are new implementations of established mathematical ideas, **not** new mathematical theorems or independently validated chess-strength improvements. The user-directed selection/motivation and the assistant's implementation must be distinguished from contributions made by prior human teammates.

| Date | Person/role | Project(s) | Actual work | Evidence | AI assistance | Verification status |
|---|---|---|---|---|---|---|
| 2026-11-22 | User-directed project, ChatGPT implementation (human review pending) | P1–P9 | Nine distinct first-version algorithms and their deterministic toy/negative-control tests, no playing-bot integration | [Stage 3 draft PR #7](https://github.com/smhgeo422/fog-of-war-chess-bots/pull/7), tools/stage3, research/STAGE3_FINDINGS.md | **Substantial**: code, tests, experimental scripts and recordkeeping authored using ChatGPT | 334 passing CI tests; source-linked independent study evidence for each P; no real FoW strength endpoint |
| 2026-11-22 | User-directed project, ChatGPT implementation (human review pending) | P1–P9 | Nine branch-scoped tracked offline studies; complete metrics, toy fixtures, hashes, negative controls and limitations; individual variant ledgers/findings | research/results_index.md and research/projects/Pn/findings.md on each project branch | **Substantial**: ChatGPT executed GitHub workflows and generated finding drafts | Nine remotely verified archives and independent ZIP/checksum cross-checks; human verification not yet recorded |

Original teammate source and published antecedents, including the existing eBotI FOW_INFOSET and GT-CFR implementations and earlier material-risk heuristics, are **prior work**; Stage 3 did not rewrite or claim authorship of them. The frozen v4 bot remains unmodified. All future paper contribution statements require human review and should cite the specific new code, independent experiment and proper literature precedent. No automated test constitutes human scientific endorsement.

## Stage 4 screening attribution (2026-11-22)

User-directed continuation. Codex implemented the FoW screening harness, fixtures, statistical controls, and verified Stockfish model recovery, then executed and archived the local screens. Code, tests, run execution, and draft findings involved substantial AI assistance and await human review. Existing team playing-bot and referee source provided the unchanged comparison context. Evidence is traced through [the Stage 4 findings](STAGE4_FINDINGS.md) and [run index](runs/stage4-screen-20261122.json).

## Stage 5 guided-ablation attribution (2026-11-22)

At the user's direction, Codex developed and tested the P8 uncertainty adjustment and the experimental P3 reply-slot selector, built the controlled ablations, ran regression tests, and archived the results. The prior team authored the underlying eBotI infoset planner, native components, and frozen comparisons. Code, tests, experimental execution, and draft findings involved substantial AI assistance. [Stage 5 findings and source records](STAGE5_FINDINGS.md)

## Stage 6 confirmation audit attribution (2026-11-22)

At the user's direction, Codex reviewed eligibility for each project, checked archived evidence and native component integrity, and recorded the confirmation decision. This work used substantial AI assistance for the audit and documentation. It adds no playing-strength observations. [Stage 6 confirmation decision](STAGE6_FINDINGS.md)

## Stage 7 evidence package attribution (2026-11-22)

The user directed completion of the eight-stage research plan. Codex assembled the report inputs, checked the accessible archives and Git provenance, generated the ledger and figure, and wrote scoped project dispositions. This documentation, tooling, and evidence audit involved substantial AI assistance. Original teammate code and historical match work remain attributed separately. Human review and formal course disclosure remain report-writing tasks. [Evidence package](report_package/README.md)
