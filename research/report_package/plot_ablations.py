"""Render P8's archived paired contrasts without rerunning the experiment."""

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams.update({"svg.hashsalt": "fow-stage7-p8", "font.family": "DejaVu Sans"})
import matplotlib.pyplot as plt

from build_results import RESEARCH, checked_bundle, read_member

OUT = Path(__file__).resolve().parent / "figures"
CONTRASTS = {
    "v1_threshold_matched": "V1 threshold",
    "raw_voc_rank": "Raw VOC ranking",
    "margin_rank": "Action margin",
    "fixed_random_mean": "Mean of 16 random policies",
}


def main(pdf=None):
    [bundle] = (RESEARCH / "archives" / "stage5-P8-v2").glob("*.tar.gz")
    _, catalog = checked_bundle(bundle)
    report = read_member(bundle, "run/ablation.json")
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.6), sharex=True, sharey=True, layout="constrained")
    records = []
    for (name, title), ax in zip(
        (("holdout", "Ordinary holdout"), ("opponent_shift", "Opponent shift")), axes, strict=True
    ):
        outcomes = report["split_results"][name]
        ax.axvline(0, linewidth=1, color="#687382", linestyle="--")
        for i, (key, label) in enumerate(CONTRASTS.items()):
            contrast = outcomes["v2_minus_comparators"][key]
            low, high = contrast["exploratory_95pct_bootstrap"]
            estimate = contrast["delta"]
            y = len(CONTRASTS) - i
            ax.hlines(y, low, high, color="#00667c", linewidth=2)
            ax.scatter(estimate, y, color="#00667c", s=32, zorder=2)
            records.append((name, label, estimate, low, high, contrast["pairs"], outcomes["n"]))
        ax.set_title(f"{title} · {outcomes['n']} decisions")
        ax.set_yticks(range(len(CONTRASTS), 0, -1), CONTRASTS.values())
        ax.ticklabel_format(axis="x", style="sci", scilimits=(-3, -3))
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0)
    fig.suptitle("P8 v2 · Equal root quota, disjoint reference worlds", fontweight="bold")
    fig.supxlabel("V2 minus control regret · lower favors v2 · exploratory 95% paired intervals")
    if pdf is not None:
        with matplotlib.rc_context({"pdf.fonttype": 42}):
            fig.savefig(pdf, format="pdf", metadata={"CreationDate": None,
                        "Subject": f"Stage 5 P8, source {catalog['source_commit']}, 24 paired blocks per split."})
        return
    OUT.mkdir(exist_ok=True)
    svg = OUT / "p8_paired_contrasts.svg"
    fig.savefig(svg, metadata={"Date": None,
        "Description": f"Stage 5 P8, source {catalog['source_commit']}, 24 paired blocks per split."})
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    with (OUT / "p8_paired_contrasts.csv").open("w", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("split", "control", "v2_minus_control", "lower_95", "upper_95", "blocks", "decisions"))
        writer.writerows(records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, help="Write a vector PDF for the manuscript")
    main(parser.parse_args().pdf)
