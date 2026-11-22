# Stage 3 completed — nine independent v1 mechanisms, nine archived toy experiments

**Status:** first-version algorithmic-kernel and toy/offline validation milestone completed on 2026-11-22. This is **NOT** a claim of stronger Fog of War Chess play or confirmation of the nine Stage 0 scientific endpoints.

**Research code:** [draft PR #7](https://github.com/smhgeo422/fog-of-war-chess-bots/pull/7), branch `infra/stage3-independent-kernels`, based on Stage 2. The frozen baseline B0, current playing bot B2, upstream arena and `main` were not changed.

**All 334 repo tests passed** on the final shared algorithm source in [Actions 45076702957](https://github.com/smhgeo422/fog-of-war-chess-bots/actions/runs/45076702957). Initial Stage 3 failed CI attempts (333 pass/1 fail, due to an overly literal scope-wording assertion) and corrected reruns remain in GitHub. P6/P9 strengthened tests passed in subsequent hosted validation. Each of the nine individual offline workflows finished successfully, published a draft GitHub Release, downloaded its evidence files back and verified every archive/inventory hash; the assistant independently checked all nine downloaded ZIPs and compressed archive SHA-256 sidecars.

## Independent project-specific toy metrics

| Project / individual findings | Measured v1 toy outcome | Toy control or falsification | Permanent verified archive |
| --- | --- | --- | --- |
| [P1](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/experiment/P1-v1-toy-kernel/research/projects/P1/findings.md) | 1.18470e-5 rare-event MSE | 2.12430e-4 baseline MSE | [45076155100](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/experiment/P1-v1-toy-kernel/research/runs/research-offline-evidence-45076155100-1.json) |
| [P2](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/experiment/P2-v1-toy-kernel/research/projects/P2/findings.md) | 0.668536 retrospective action NLL | 1.098612 uniform NLL | [45076160806](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/experiment/P2-v1-toy-kernel/research/runs/research-offline-evidence-45076160806-1.json) |
| [P3](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/experiment/P3-v1-toy-kernel/research/projects/P3/findings.md) | 0.5 strategy fusion gap | 1.0 clairvoyant vs 0.5 feasible | [45076165589](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/experiment/P3-v1-toy-kernel/research/runs/research-offline-evidence-45076165589-1.json) |
| [P4](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/experiment/P4-v1-toy-kernel/research/projects/P4/findings.md) | 0.5 instrumental VOI | 0.0 irrelevant/equally visible VOI | [45076169979](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/experiment/P4-v1-toy-kernel/research/runs/research-offline-evidence-45076169979-1.json) |
| [P5](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/experiment/P5-v1-toy-kernel/research/projects/P5/findings.md) | 0.147928 heldout Brier | 0.241875 constant-class Brier | [45076173654](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/experiment/P5-v1-toy-kernel/research/runs/research-offline-evidence-45076173654-1.json) |
| [P6](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/experiment/P6-v1-toy-kernel/research/projects/P6/findings.md) | 0.005993 asymmetric restricted-game gap | 0.385617 gap after 10 vs 6000 iters | [45076458586](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/experiment/P6-v1-toy-kernel/research/runs/research-offline-evidence-45076458586-1.json) |
| [P7](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/experiment/P7-v1-toy-kernel/research/projects/P7/findings.md) | 0.000198908 synthetic holdout MSE | 0.001706911 uncorrected and 0.000695034 shuffled-target MSE | [45076181707](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/experiment/P7-v1-toy-kernel/research/runs/research-offline-evidence-45076181707-1.json) |
| [P8](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/experiment/P8-v1-toy-kernel/research/projects/P8/findings.md) | 0.15 near-tie computation gain | 0.0 gain on decisive action | [45076186587](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/experiment/P8-v1-toy-kernel/research/runs/research-offline-evidence-45076186587-1.json) |
| [P9](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/experiment/P9-v1-toy-kernel/research/projects/P9/findings.md) | Zero false certificates on toy graph | Depth-1 fails; depth-2 succeeds; adversary loss branch rejected | [45076510415](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/experiment/P9-v1-toy-kernel/research/runs/research-offline-evidence-45076510415-1.json) |

The metrics in this table are **not commensurate**. An NLL, Brier, exploitability gap, computation gain and endgame certificate are different units, with different experimental sample definitions. There is no meaningful common "percent good" score and no nine-project performance ranking based on this table.

## Mechanism-level conclusions, attribution and falsification

### P1

**What was actually verified:** Valid p/q sampling and positive support; ESS drops 64→46.39.

**What was not established:** No real hidden-state Brier or posterior support repair.

Tested source commit: `730a81cc7596ee61fe91b6011eda80a92149e3dd`. Project-specific science questions, formulas, preregistered endpoints and full algorithm pseudocode are in `research/projects/P1/proposal.md`; new v1 source is `tools/stage3/P1.py`; independent branch records include `research/projects/P1/variants.jsonl` and `findings.md`. 

### P2

**What was actually verified:** Online posterior updates use event equivalence classes and uniform floor.

**What was not established:** Opponent view/action uncertainty and unseen-opponent holdout not tested.

Tested source commit: `d90ee982e78630bde657a8473d1c15832396a516`. Project-specific science questions, formulas, preregistered endpoints and full algorithm pseudocode are in `research/projects/P2/proposal.md`; new v1 source is `tools/stage3/P2.py`; independent branch records include `research/projects/P2/variants.jsonl` and `findings.md`. 

### P3

**What was actually verified:** One action per same future observation/history; changed root; zero-cost fallback.

**What was not established:** Existing team infoset code not yet integrated/equal-CPU-tested.

Tested source commit: `037f595cc6adee37132ed3e9aa03ab96d113707d`. Project-specific science questions, formulas, preregistered endpoints and full algorithm pseudocode are in `research/projects/P3/proposal.md`; new v1 source is `tools/stage3/P3.py`; independent branch records include `research/projects/P3/variants.jsonl` and `findings.md`. 

### P4

**What was actually verified:** Only decision-consequential information has value at equal direct payoff.

**What was not established:** No opponent information denial or actual FoW root action effects.

Tested source commit: `5b7c84dced5c8fbd1d17b641a188954ebd85ab84`. Project-specific science questions, formulas, preregistered endpoints and full algorithm pseudocode are in `research/projects/P4/proposal.md`; new v1 source is `tools/stage3/P4.py`; independent branch records include `research/projects/P4/variants.jsonl` and `findings.md`. 

### P5

**What was actually verified:** Beta-shrunk distinct quiet-exposed, sheltered, capture and king-risk classes.

**What was not established:** Synthetic outcome process favors class model; real unseen losses unmeasured.

Tested source commit: `7b5ec24071da00f1d388051aee5d9044cb4f0872`. Project-specific science questions, formulas, preregistered endpoints and full algorithm pseudocode are in `research/projects/P5/proposal.md`; new v1 source is `tools/stage3/P5.py`; independent branch records include `research/projects/P5/variants.jsonl` and `findings.md`. 

### P6

**What was actually verified:** Nash mix near [0.25,0.75], plus symmetric matching-pennies zero gap.

**What was not established:** Matrix-only solver; no FoW infoset CFR, blueprint preservation or deep leaf CPU.

Tested source commit: `a23eca130e252dadb2b8d8e1c2590093b7cf7a0b`. Project-specific science questions, formulas, preregistered endpoints and full algorithm pseudocode are in `research/projects/P6/proposal.md`; new v1 source is `tools/stage3/P6.py`; independent branch records include `research/projects/P6/variants.jsonl` and `findings.md`. 

### P7

**What was actually verified:** Strict observation-only features; ridge chosen on development; model coefficients stored.

**What was not established:** Synthetic continuation teacher, no actual Stockfish causal counterfactual value.

Tested source commit: `03580db53f09c5d03a42a77bbcb5df3179b5e754`. Project-specific science questions, formulas, preregistered endpoints and full algorithm pseudocode are in `research/projects/P7/proposal.md`; new v1 source is `tools/stage3/P7.py`; independent branch records include `research/projects/P7/variants.jsonl` and `findings.md`. 

### P8

**What was actually verified:** Positive expected VOC vs no more search, reserve guard, martingale rejection.

**What was not established:** No measured Stockfish node timings, equal game CPU or time forfeit rates.

Tested source commit: `0a530594f0ea4858b629ed9c4de84bf10a4d3ba6`. Project-specific science questions, formulas, preregistered endpoints and full algorithm pseudocode are in `research/projects/P8/proposal.md`; new v1 source is `tools/stage3/P8.py`; independent branch records include `research/projects/P8/variants.jsonl` and `findings.md`. 

### P9

**What was actually verified:** Real local FoW referee: 23 common actions and 35 defender replies checked; **0** guaranteed one-turn captures.

**What was not established:** No general 8×8 KQ-v-K guarantee or new endgame theorem.

Tested source commit: `70e1d73eea061159ef500c61a0d7e4db6791ba4d`. Project-specific science questions, formulas, preregistered endpoints and full algorithm pseudocode are in `research/projects/P9/proposal.md`; new v1 source is `tools/stage3/P9.py`; independent branch records include `research/projects/P9/variants.jsonl` and `findings.md`. 


### Critical distinction from the earlier team's work and literature

The previously existing eBotI belief, search, risk, infoset, GT-CFR and frozen v4 engine code are **not** presented as new Stage 3 research. Stage 3's new software consists of assistant-generated *separate* minimal algorithm kernels, toy generators/certifiers, tests, branch-specific metrics and archives, created under user-directed hypotheses from Stage 0. Original team contributions and relevant published papers remain credited by the Stage 0 proposals and literature review. The new code is unreviewed assistant implementation; its scientific claims cannot exceed its actual tests.

P9 does **not** reproduce Gehnen & Stannat's endgame theorems. On the restricted real-referee test two hidden kings generated the same own observation, with 23 common moves. The one-turn certificate enumerated 35 defender responses and **certified zero universal wins**. A fabricated positive KQ-v-K guarantee would have been incorrect.

P6's 0 primary gap is a trivial symmetric matching-pennies equilibrium; the stronger result is the **nonuniform asymmetric restricted-game gap of 0.005993**, with near-correct 25%/75% strategies. It does not certify a full imperfect-information game solver.

P1's importance-sampling variance gain comes with **lower effective sample size**, so we cannot assume all threat distributions improve. P2/P5/P7 used artificial behavior or reward generators for the first correctness probe, so their predictive gains were expected by design and must not be extrapolated to real opponents.

## Validation and evidence accounting

- **Nine** separate `experiment/Pn-v1-toy-kernel` branches, one tracked `experiments/offline/Pn.json` each with fixed hypothesis, seed, version, purpose=research and immutable source revision.
- **Nine** distinct `tools/stage3/Pn.py` algorithm implementations; one shared `tools/offline_jobs/stage3.py` runner; Stage 3 deterministic/negative-control regression suite. Each project has an explicit enabled-v1/disabled toy comparator in `research/stage3_ablation_manifest.json`.
- **Nine** independent completed `research/runs/research-offline-evidence-<run>-1.json` records on the matching experiment branches; **nine** verified GitHub draft Release archives, each with SHA256 sidecar, JSON catalogue, split/fixture provenance, exact implementation module hash, toy results and explicit limitations.
- All early failed gate attempts retained; only the final correct source SHA counted for each project.
- **Zero** new real chess playing-bot integrations, **zero** genuine full-clock matched strength experiments, and no official arena submissions. Do not label synthetic target prediction "held-out competitive performance."

## Handoff to Stage 4 — necessary next scientific work

The Stage 3 v1 kernels are **diagnostic prototypes**. Stage 4, only when explicitly requested, must connect each relevant mechanism to real FoW observation histories or a legitimately validated restricted FoW solver and quantify the project-specific preregistered offline outcome. To compare playing strength, integrate through an explicit feature flag with a verified off-path, hold baseline B0 fixed, match both engines, decision compute, game clock and paired color/seed blocks, and report failures and uncertainty.

Several scientific directions (notably P1 posterior truth support, P2 actual opponent hidden-information likelihood, P7 causal alternative action value, P8 calibrated VOC, P9 multi-turn restricted endgame wins) may need further model development before a truthful real-world evaluation is feasible. If so Stage 4 should record that feasibility limit rather than fabricate results or prematurely call the mechanism successful.

No changes to scientific project taxonomy, no merge, and no scheduled research are authorized. The next user-directed stage is Stage 4: offline and short-game scientific screening, **not** manuscript writing or a promise that all variants are stronger.
