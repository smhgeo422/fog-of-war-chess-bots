# P7 · Findings and closure

**Hypothesis.** Does a learned observation-only residual improve a fixed continuation forecast? [Specification](proposal.md)

**Prior work and intervention.** The team already evaluated sampled worlds with Stockfish. The prototype adds a small regularized residual to the fixed evaluator.

**V1 evidence.** Archived metric `heldout_synthetic_counterfactual_residual_mse` = 0.00019890761, recorded sample count 160. The catalog pins source `03580db` and preserves the toy or restricted scope.

**Referee or replay outcome.** The residual increased six-ply logged-action MSE from 0.05147 to 0.05232 in-family and from 0.03548 to 0.04127 on opponent shift. The paired intervals crossed zero. Simpler intercept and shuffled controls beat the residual in both splits.

**Verdict.** The tested residual stays out of the candidate. The observed MSE changes were adverse.

**Full-clock decision.** No confirmation entry for this revision. A sound alternative-action teacher with held-out targeted labels is needed before running a strength match.

[Stage 3 v1 catalog](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/653af06d4bfb3a1387ec699ebf2f8cce87707e49/research/runs/research-offline-evidence-45076181707-1.json) · [Stage 4 findings](../../STAGE4_FINDINGS.md) · [Versions](variants.jsonl) · [Confirmation decision](../../STAGE6_FINDINGS.md)
