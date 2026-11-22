# P5 · Findings and closure

**Hypothesis.** Does a selective hazard model improve held-out calibration for unseen material losses? [Specification](proposal.md)

**Prior work and intervention.** eBotI already had HANG, SAFE_FIRST and related risk heuristics. The prototype tested class-conditioned event probability with shrinkage.

**V1 evidence.** Archived metric `heldout_selective_hidden_material_brier` = 0.14792809, recorded sample count 200. The catalog pins source `7b5ec24` and preserves the toy or restricted scope.

**Referee or replay outcome.** Stage 4 noncapture Brier was 0.01760 for the class model versus 0.01762 for the constant control on ordinary holdout with six events. The paired interval crossed zero. The shifted split worsened to 0.00575 from 0.00572 with four events.

**Verdict.** Inconclusive ordinary holdout and adverse opponent shift. The class model stays experimental.

**Full-clock decision.** No confirmation entry for this revision. Event-bearing observation data and an engine-conditioned control are needed before interpreting live material-loss effects.

[Stage 3 v1 catalog](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/f77141a20fd6209385a5ba99251e64a0ca823176/research/runs/research-offline-evidence-45076173654-1.json) · [Stage 4 findings](../../STAGE4_FINDINGS.md) · [Versions](variants.jsonl) · [Confirmation decision](../../STAGE6_FINDINGS.md)
