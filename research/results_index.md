# Experiments and durable evidence index

The source of truth for numerical results is each run's `manifest.json`, `report.json`, and replay files, not hand-copied percentages. This file links each archived run to its research claim.

| Research ID | Run ID | Commit | Type | Games / caps | Verified result | Evidence / archive URL | SHA-256 | Notes |
|---|---|---|---|---|---|---|---|---|
| Infra | phase2-ci | `01f4051` | integration smoke | 2 games, capped | Successful pipeline smoke; **not strength evidence** | [Phase 2 archive](https://drive.google.com/file/d/1oXz7_EgZVWmZGDG1O9nmC96RSrsAHgCl/view) | `e3f769f4bc13c016772091d68a8aff0a9fed65beb9bed6f1a3832770580256ca` | Artifacts verified from Codex archive |
| Infra | phase2-arena-clock | `01f4051` | 180+2 integration smoke | 4 games, 12-ply cap | 4 capped draws; **not strength evidence** | [Phase 2 archive](https://drive.google.com/file/d/1oXz7_EgZVWmZGDG1O9nmC96RSrsAHgCl/view) | `e3f769f4bc13c016772091d68a8aff0a9fed65beb9bed6f1a3832770580256ca` | Time control checked, not competition performance |
| Infra | phase2-parallel | `01f4051` | process-management integration | 4 games | Greedy 4–0 vs Random; **not candidate strength evidence** | [Phase 2 archive](https://drive.google.com/file/d/1oXz7_EgZVWmZGDG1O9nmC96RSrsAHgCl/view) | `e3f769f4bc13c016772091d68a8aff0a9fed65beb9bed6f1a3832770580256ca` | Multiworker cleanup validated |
| Infra | hosted-phase2-45059968560 | `2be8921` | GitHub Actions hosted CI | 235 tests + capped smoke | **235 passed** in 182.55s, integration test passed; **not playing-strength evidence** | [Hosted run and downloadable artifact](https://github.com/smhgeo422/fog-of-war-chess-bots/actions/runs/45059968560) | `bd35c2bedd5d6dd0d0f6c72a7f53315ccd1e1f35cf4edbd9ef92304480c5add8` | Artifact expires 2026-12-22; external long-term archive still needed |
