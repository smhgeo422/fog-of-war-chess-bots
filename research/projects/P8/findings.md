# P8 · Findings and closure

**Hypothesis.** Does an uncertainty-adjusted value-of-computation forecast improve action choice at a matched root quota? [Specification](proposal.md)

**Prior work and intervention.** The team already used a reserve clock and root/depth settings. V1 tested threshold-based extra-root allocation; v2 adjusted the allocation forecast for leave-one-root sensitivity.

**V1 evidence.** Archived metric `near_tie_exact_computation_value` = 0.15, recorded sample count 2. The catalog pins source `0a53059` and preserves the toy or restricted scope.

**Referee or replay outcome.** Stage 4 showed an exploratory effect over eight holdout decisions with a shared reference. In Stage 5, v2 minus v1 regret was +0.00021017 [0, +0.00063052] over 24 ordinary blocks, and −0.00001124 [−0.00003371, 0] over 24 shift blocks. Quotas and aggregate engine nodes were closely matched and reference worlds were disjoint within each decision.

**Verdict.** V2 produced no ordinary gain and a negligible shifted contrast. Neither version has a validated live clock effect.

**Full-clock decision.** No confirmation entry for this revision. A full-clock study would need an integrated controller, independent traces with more decisions where extra search changes the action, and matched live CPU and reserve checks.

[Stage 3 v1 catalog](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/96747e85b3d5d87bc5278b2e2f0089217df718dd/research/runs/research-offline-evidence-45076186587-1.json) · [Stage 4 findings](../../STAGE4_FINDINGS.md) · [Stage 5 v2 catalog](../../runs/stage5-P8-v2.json) · [Stage 5 findings](../../STAGE5_FINDINGS.md) · [Versions](variants.jsonl) · [Confirmation decision](../../STAGE6_FINDINGS.md)
