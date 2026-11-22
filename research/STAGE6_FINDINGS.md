# Stage 6 · Confirmation decision

**Decision: zero eligible research candidates.** Stage 6 reviewed the P1–P9 evidence from the Stage 4 and Stage 5 checkpoints. The 180+2 schedule has zero pairs, and there is no combined research bot. The archived evidence supports closing the confirmation gate for this campaign. Playing-strength effects remain unmeasured for the nine research projects.

## Candidate review

| Project | Strongest relevant evidence | Confirmation disposition |
| --- | --- | --- |
| P1 · Belief reconstruction | All 108 scored early decisions retained the true board. Zero positive hidden king-threat labels. | Calibration endpoint blocked by the available sample. |
| P2 · Opponent policy | Online adaptation beat the engine-only control on synthetic opponents. It was slightly worse than the static mixture in-family, with a small inconclusive shifted action-likelihood contrast. | Adaptation lacks a consistent isolated predictive gain. |
| P3 · Contingent tactics | v2 covered different replies in 18 of 32 root/world cases. Across eight mirrored scenarios it changed zero root decisions and oracle regret remained 0.03389067 in both arms. | Retain the legacy default. The opt-in branch has exact feature-off parity on scripted controls and no measured decision gain. |
| P4 · Information value | Matched-payoff referee fixtures identified useful information in one motif. | Live action-conditioned observation forecast and isolated decision improvement are unmeasured. |
| P5 · Catastrophic risk | Held-out calibration was inconclusive and shifted Brier worsened from 0.00572 to 0.00575. | Keep the current categorical model out of confirmation. |
| P6 · Restricted strategic solving | Mixed policy improved security in the scripted hidden-world matrix. | Evidence is local to that matrix. Full FoW opponent policy, blueprint safety and matched engine cost are unresolved. |
| P7 · Continuation value | Residual increased forecast MSE on both held-out splits. | The tested residual has adverse offline evidence. |
| P8 · Adaptive computation | v2 versus v1 ordinary regret difference +0.00021017 over 24 paired blocks, exploratory interval [0, +0.00063052]. Shift difference −0.00001124 with interval [−0.00003371, 0]. Both arms had equal aggregate root counts and nearly equal aggregate nodes. Per-block node counts varied. | No ordinary improvement, negligible shifted contrast, and live clock/reserve behavior unmeasured. |
| P9 · Certified endgames | Exhaustive one-turn check on 222 active positions and 39,034 defender replies found zero sound hidden-world winning actions and zero oracle disagreements. | The declared domain has zero hidden-world conversion coverage. |

[Stage 4 evidence](STAGE4_FINDINGS.md) · [Stage 5 evidence](STAGE5_FINDINGS.md) · [Criteria](stage0_preregistration.md)

## Baseline and evidence audit

- Frozen `obscuro_v4` (B0) remains the authoritative control. Default eBotI (B2) remains the existing comparison profile. B1's Stage 2 action agreement was 6/9, with B0 self-agreement 10/11, so equivalent behavior was never established. No B3 is designated.
- The recorded Stage 2 B2-versus-B0 result of 1–0–3 at 36+0.4 and the Stage 4 two capped draws at 24+0.1 are integration smokes. The 180+2 infrastructure smoke documented in the evidence index had a 12-ply cap. These runs establish pipeline operation within their scope. The earlier team full-clock and arena histories involve other variants and remain historical evidence.
- The frozen source inventory, local native component digests and both B0/B2 helper self-tests passed. The Stage 4 screen and smoke bundles and both Stage 5 v2 bundles passed checksum and member-inventory verification. Earlier draft-release evidence is cited through its catalogs and reported hosted results.
- The audited branch tip is Stage 5 `ef08541`. Its playing-bot and referee trees match Stage 3 `96ac91d`. The published research branches expose the same two v2 experiments recorded in Stage 5.

[Stage 2 baseline evidence](STAGE2_FINDINGS.md) · [Evidence index](results_index.md)

## Stage 7 input

Preserve the nine project dispositions, code and controls, run catalogs, checksums, diagnostic effects and remaining limitations. The eventual report can make scoped claims about the measured mechanisms and negative results. The confirmation tournament and final research candidate have empty result sets.
