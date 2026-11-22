# Replay examples and provenance

Both examples below come from Stage 4 bundles that passed the checksum and member-inventory verifier. The excerpt comes from frame 1, after one move. A `?` represents a hidden square and the view strings run a1 through h8.

| Use | Archived member and observation | Scope |
| --- | --- | --- |
| Show how an opponent move can stay hidden | `run/corpus/replays/holdout/s2-025-ab.json`, frame 1. The referee records White's `b2b3`. Black sees `????????????????????????????????----------------pppppppprnbqkbnr`. The game ended 0–1, king capturable, after 25 plies. | Seed-7106 synthetic holdout replay. The move and true board serve as retrospective labels. [Screen bundle](../archives/stage4-screen-20261122/) |
| Show the two-bot protocol and clock trace | `run/replays/0001.json`, frame 1. eBotI plays `d2d4` as White. The saved clocks are 24.096353 and 24.0 seconds. This game ended in a capped draw after 20 plies. | eBotI versus frozen v4 at 24+0.1. Use for integration and replay examples only. [Smoke bundle](../archives/stage4-b0-b2-smoke-20261122/) |

To read either record, use `tar -xOzf <bundle.tar.gz> <member>`. Verify the sibling SHA-256 sidecar and JSON catalog first with `tools/verify_research_archive.py`. The full member paths and parent bundles identify the examples without duplicating the replay data.
