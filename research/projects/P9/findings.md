# P9 · Findings and closure

**Hypothesis.** Can an exhaustive bounded policy certify hidden-information endgame conversion soundly? [Specification](proposal.md)

**Prior work and intervention.** Prior work established endgame theorems under specified rules. This implementation checks a declared one-own-turn referee domain.

**V1 evidence.** Archived metric `finite_endgame_reachability_certifier_soundness` = 1, recorded sample count 2. The catalog pins source `70e1d73` and preserves the toy or restricted scope.

**Referee or replay outcome.** The Stage 4 oracle covered 222 active KQvK boards, 6,146 root actions and 39,034 defender replies. It found 24 known-world positives, zero hidden-world certificates, and zero false or missing certificates in the declared domain.

**Verdict.** Sound on the declared domain with zero hidden-world coverage.

**Full-clock decision.** No confirmation entry for this revision. Expanding coverage requires a new declared exhaustive domain or longer horizon. Full games cannot substitute for that proof obligation.

[Stage 3 v1 catalog](https://github.com/smhgeo422/fog-of-war-chess-bots/blob/902dec1bc5088b7167a7c04c2c041e98128abd13/research/runs/research-offline-evidence-45076510415-1.json) · [Stage 4 findings](../../STAGE4_FINDINGS.md) · [Versions](variants.jsonl) · [Confirmation decision](../../STAGE6_FINDINGS.md)
