# Fog of War Chess · Report evidence package

The eight-stage research workflow is closed at the evidence handoff. This package is for writing the course report. The nine project verdicts range from restricted mechanism checks to negative or blocked empirical outcomes. The eligibility audit yielded zero 180+2 confirmation games and no integrated research candidate. Frozen `obscuro_v4` remains the comparison baseline. [Confirmation decision](../STAGE6_FINDINGS.md)

| Material | Where to find it |
| --- | --- |
| Nine project conclusions, including failures and data gaps | [Closure sheet](CLOSURE.md) |
| Machine-readable run ledger with exact metric definitions, source pins, checksums and available intervals | [JSON](../combined_results.json) · [CSV](../combined_results.csv) |
| P8 paired contrasts and underlying estimates | [Figure](figures/p8_paired_contrasts.svg) · [Figure data](figures/p8_paired_contrasts.csv) |
| Rules, experimental controls, split provenance and reproducibility | [Methods](METHODS.md) |
| Example observation and clock traces with archive member pointers | [Replay examples](REPLAY_EXAMPLES.md) |
| Primary references, earlier team code and contributor attribution | [Bibliography](BIBLIOGRAPHY.md) · [Contribution record](../contributions.md) |
| Manuscript planning and disclosure checklist | [Report outline](../report_outline.md) |

## Evidence audit

The combined table inventories 18 canonical run catalogs, including the Stage 1 pipeline pair, Stage 2 baseline and corpus records, all nine v1 studies, the Stage 4 offline and capped smoke bundles, and both Stage 5 v2 ablations. Early attempts and historical team experiments remain indexed in the prior stage findings; they are outside this canonical table. The P1 v0 smoke published two catalogs under the same hosted run ID, one for the game and one for offline evidence.

The four Git-tracked bundles passed direct SHA-256, inventory and catalog verification. For the 14 earlier records, the published Git catalogs, their pinned source ancestry and the Stage 3 ledger ties were checked. The draft Release pages returned HTTP 404 in this environment. Their hosted verification records are retained, and direct access to those older archive bytes remains unresolved. The Phase 2 source and starter ZIPs are tracked separately in [archives](../archives/).

Null game-score intervals and blank CSV cells represent unavailable statistics. A null field supplies no zero estimate. Stage 4's primary count is an inventory of nine project records. It does not count successful hypotheses. For P8, the paired bootstrap contrasts live in the verified archive payload and the figure CSV. The catalog contains the ordinary primary estimate and sample count. Stage 5 P3 reports four fixed fixture families with no sampling interval.

## Rebuild the package tables

From this repository, with the published branch heads available in a separate Git object store:

```sh
catalog_repo=$(mktemp -d)
git init --bare "$catalog_repo"
git -C "$catalog_repo" fetch --no-tags https://github.com/smhgeo422/fog-of-war-chess-bots.git '+refs/heads/*:refs/heads/*'
.venv/bin/python research/report_package/build_results.py --catalog-repo "$catalog_repo"
MPLCONFIGDIR=/tmp/fow-mpl XDG_CACHE_HOME=/tmp/fow-mpl-cache python research/report_package/plot_ablations.py
```

The plotting command uses Python with Matplotlib 3.10.8. Table and figure builders read archived evidence; they launch no games and alter no locked project dependencies.
