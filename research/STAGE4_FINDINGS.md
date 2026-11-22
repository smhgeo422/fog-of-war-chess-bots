# Stage 4 · Referee and replay screening findings

The offline screening milestone is complete. The run contains nine project records, including one blocked calibration endpoint and multiple negative results. Competitive validation remains open. No prototype passed the gate for a short playing-bot comparison.

## Source and evidence

- Source commit `effafc631d198de8e2e4101ac50ea787bc147f17` on `infra/stage4-scientific-screening`. All 19 frozen v4 inventory entries were checked against their recorded hashes.
- Run `stage4-screen-20261122`. The existing Stage 2 generator reconstructed 72 synthetic games from seed 7106 with 2,190 observations and 36 paired color blocks. The archived run contains the regenerated replays, observations, retrospective labels, split provenance, tactical fixtures, and per-project decision records. These are local starter-policy replays. The historical hosted tarball and competitive arena replays were unavailable from this environment.
- B0 Stockfish 19 was rebuilt from the pinned source. The exact pinned model was recovered by verifying the official Linux release archive, exporting its embedded network, and verifying the full model digest before building. The archive manifest records the engine executable and network hashes.
- [Checksummed evidence and catalog](archives/stage4-screen-20261122/) and [run index](runs/stage4-screen-20261122.json). The bundle uses the offline archiver and verifier. Its umbrella metric counts project records, including blocked endpoints.

## Project results and dispositions

| Project | What Stage 4 measured | Evidence-based disposition |
| --- | --- | --- |
| **P1 · Belief reconstruction** | The exact early-prefix screen retained the true board in all 108 scored decisions. Forty player histories exceeded the support cap. No scored decision had a positive unseen king-attack label or nonzero exact predicted risk. | **Calibration blocked.** Zero Brier from this sample carries no evidence of useful threat calibration. Prespecify a larger legal-history support and a threat-bearing set before retesting. |
| **P2 · Opponent policy** | Over 129 early decisions, online action NLL was 3.480 versus Stockfish 3.937 in-family and 3.440 versus 3.967 on shift. Stockfish scored all 2,344 hypothetical worlds. Online adaptation was slightly worse than the static mixture in-family. The shifted action-NLL difference from static was about −0.0023 and its paired interval crossed zero. | **Mixed.** The online model predicts these synthetic opponents better than the fixed engine control. The static and uniform controls prevent attributing that advantage to adaptation itself. Retain all controls for a wider replay study. |
| **P3 · Contingent tactics** | On eight restricted roots with one legal fixed reply per case, observation-contingent regret was 0 versus 0.125 for the fixed blind continuation. The incompatible-escape fixture exposed a 0.5 clairvoyance gap. | **Fixture mechanism supported.** Compare against the team's existing infoset planner at matched compute before claiming a distinct playing benefit. Color mirrors are paired checks. |
| **P4 · Information value** | With identical per-world escape utilities and matched immediate payoff, the informative root was worth 0.5 versus 0. The informative root exposed 8.5 squares on average versus 10 for the irrelevant option. Both earned zero on the shared-escape control. | **Fixture mechanism supported.** An action-conditioned forecast and a matched utility control are still needed for live evaluation. |
| **P5 · Catastrophic risk** | Noncapture Brier was 0.01760 versus 0.01762 for the constant training-rate control on holdout, with only six positive events and a paired interval spanning zero. On shift it worsened to 0.00575 versus 0.00572 with four events. | **Inconclusive in-family and adverse on shift.** The current screen gives no basis to promote the class model or claim lower live losses. |
| **P6 · Restricted strategic solving** | On the incompatible-escape referee payoff matrix, mixed security was −0.5043 versus greedy −1.0. The duality gap was about 0.0113. When both worlds shared a safe action, the gain was zero. | **Restricted-game mechanism supported.** The adversary chooses the hidden world in this table. Extensive-form resolution, blueprint safety, and matched engine leaves are open. |
| **P7 · Learned continuation value** | The residual raised six-ply logged-action MSE from 0.05147 to 0.05232 in-family and from 0.03548 to 0.04127 on shift. Each split has six paired blocks and both paired intervals cross zero. The intercept-only and shuffled controls also beat the fitted residual on these splits. | **Do not promote this residual.** A fixed-policy counterfactual teacher and alternative-action rankings are still needed for the original endpoint. |
| **P8 · Adaptive computation** | For eight held-out decisions and 36 root evaluations per arm, adaptive regret was 0.00039 versus 0.02371 for the fixed allocation (37,046 versus 37,050 reported engine nodes). The paired difference interval is [−0.06995, 0]. Four shift decisions triggered no extra computation in either arm. | **Exploratory signal.** The shared larger-root reference includes evaluated roots. Replicate on an independent, larger trace with live cost and reserve checks before changing the clock policy. |
| **P9 · Certified endgames** | The oracle enumerated 222 active KQvK boards across six fixed layouts, 6,146 root actions, and 39,034 defender replies. It found 24 known-world positive positions and zero one-turn certificates in the six hidden-world sets. No false or missing certificate was observed in the declared domain. | **Sound within the declared check, zero hidden-world conversion coverage.** A larger horizon and a provably complete information set are necessary to test general conversion. |

The replay experiments use the available observations for input and keep hidden truth for retrospective scoring. P2, P5 and P7 compare predictive losses, P3/P4/P6/P9 check restricted referee questions, and P8 uses a shared offline node-limited reference. Their effect sizes are in different units.

## Match gate and handoff

The first four stages left the proposed mechanisms as standalone kernels. Their offline controls establish limited behavior. The tested branches contain no live candidate with verified feature-off action parity and isolated equal-compute behavior. The Stage 4 research screen therefore contains zero variant-vs-baseline games. The separate baseline integration smoke completed both color-swapped games at 24+0.1, capped at 20 plies. Both reached the cap. Its archive is recorded under purpose smoke.

Stage 5 can use the project dispositions above for targeted revisions. Priority should come from evidence and feasibility within each existing hypothesis. Broader permissioned, full-clock replay data would resolve several coverage gaps. The public arena API was blocked by this environment. No strength claim, promotion, official arena submission, or final report follows from these screens.

## Validation and reproduction

The local regression suite passed all 346 tests with real Stockfish enabled. It reported one python-chess asyncio deprecation warning. The offline evidence and [separate baseline smoke](archives/stage4-b0-b2-smoke-20261122/) both passed the repository's archive verifier.

From the repository root with the locked environment available, reproduce the screen from a clean checkout of the source revision:

```sh
bash tools/setup-experiments.sh
.venv/bin/python -m tools.stage4_screen \
  --run data/research/stage4/rerun \
  --stockfish bots/obscuro_v4/stockfish/src/stockfish
```
