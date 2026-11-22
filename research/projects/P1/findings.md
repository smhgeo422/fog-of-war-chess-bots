# P1 · Findings and closure

**Hypothesis.** Does threat-stratified sampling improve hidden-attack posterior estimates at a matched root count? [Specification](proposal.md)

**Prior work and intervention.** The team already maintained weighted consistent boards with a native helper and capped Python fallback. The v1 kernel tested an importance-corrected proposal over existing states.

**V1 evidence.** Archived metric `rare_event_importance_sampling_mse` = 1.1847024e-05, recorded sample count 250. The catalog pins source `730a81c` and preserves the toy or restricted scope.

**Referee or replay outcome.** Stage 4 retained the true board in 108 scored decisions. Zero positive unseen king-attack labels and zero nonzero exact risks made the calibration comparison uninformative. Forty player histories reached the cap.

**Verdict.** Calibration blocked on the tested sample.

**Full-clock decision.** No confirmation entry for this revision. Use a prespecified threat-bearing dataset and wider legal-history support before a game-strength trial can answer the hypothesis.

[Stage 3 v1 catalog](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/a02fdca481ce746dfc782d362891d7993dca84ac/research/runs/research-offline-evidence-45076155100-1.json) · [Stage 4 findings](../../STAGE4_FINDINGS.md) · [Versions](variants.jsonl) · [Confirmation decision](../../STAGE6_FINDINGS.md)
