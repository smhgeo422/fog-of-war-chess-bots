#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
scratch=$(mktemp -d)
trap 'rm -rf -- "$scratch"' EXIT
mkdir -p "$scratch/cache" "$scratch/mpl"
export SOURCE_DATE_EPOCH=1795478400
export MPLCONFIGDIR="$scratch/mpl" XDG_CACHE_HOME="$scratch/cache"
python ../plot_ablations.py --pdf "$scratch/p8_paired_contrasts.pdf"
sed 's#../figures/p8_paired_contrasts.svg#p8_paired_contrasts.pdf#' REPORT.md > "$scratch/report.md"
pandoc "$scratch/report.md" --from=markdown+tex_math_dollars --resource-path="$scratch" \
  --pdf-engine=xelatex --output REPORT.pdf
