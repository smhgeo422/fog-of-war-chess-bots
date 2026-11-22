# Stage 4 · Independent referee and replay screening

Stage 4 starts from the standalone v1 kernels and preregistered P1–P9 endpoints. Treat synthetic starter-policy games and restricted referee tables as feasibility evidence. Competitive replay replication, integration into a playing bot, and matched games each require their own evidence.

## Data and controls

- Regenerate the audited Stage 2 schema-2 corpus with seed 7106. Preserve the original whole-game and color-pair split, including the opponent-shift set. This is a local reconstruction from the pinned generator. The hosted draft-release tarball is a separate artifact.
- Reconstruct features from the side's visible observations and legal attempts. Use replay truth only for labels or an explicitly retrospective oracle. Record dropped rows, terminal positions, exact-support coverage and other selection limits where applicable.
- Use frozen obscuro_v4 (B0) for any future playing-strength comparison. Compare standalone screening methods to a task-appropriate disabled or simple control using the same inputs. B1 remains a separate v4-like profile.
- Use Stockfish 19 where a screen calls for it. Record the executable digest, node and thread settings, and differences between nominal and realized work. Treat offline node budgets and live game clocks as different measurements.

## Screening order

| Project | Screening question | Stronger evidence still needed |
| --- | --- | --- |
| P1 | At equal samples from observation-consistent support, does threat-stratified weighting change hidden-threat estimation error or calibration? | Wider legal-history support, competitive calibration, root-search integration |
| P2 | Does an event-conditioned style mixture improve action or event likelihood on held-out observation histories? | Real opponent behavior, wider belief histories and the preregistered engine control |
| P3 | Can one policy per future observation attain low regret on a restricted FoW tactical continuation? | Matched-CPU comparison with the team's existing infoset search |
| P4 | Does revealing decision-relevant information improve a continuation at matched direct payoff? | Real root-action and opponent-information effects |
| P5 | Does a calibrated predictor improve unseen next-reply material event prediction over its fixed control? | Competitive calibration and utility effects against current HANG/safe-first |
| P6 | Can a mixed restricted-game policy improve security over a greedy control on referee-derived payoffs? | Extensive-form FoW re-solving with matched engine leaf budgets |
| P7 | Does an observation-only residual reduce held-out continuation forecast error against the fixed evaluator? | Counterfactual action ranking and representative opponent data |
| P8 | Does the value-of-computation gate reduce action regret at a matched offline engine-work budget? | Integrated equal-CPU/clock behavior and forfeit accounting |
| P9 | What fraction of the declared restricted endgame domain can be certified, with every legal defender reply checked? | Larger horizon and domain, conversion rate and occurrence in complete games |

Preserve negative outcomes and scope restrictions. Each project has a different loss, payoff or coverage definition. The dashboard records each independently.

## Game gate

Only stage a short playing match when an integrated variant can isolate the mechanism, disabling it restores the control on fixed observations, both engines are verified, and the same compute and clock are applied to the matched color blocks. An offline candidate that changes no live bot behavior cannot pass this gate. Leave integrations and matches pending when the gate lacks evidence.
