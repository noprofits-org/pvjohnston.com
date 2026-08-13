#!/usr/bin/env bash
# Canonical run for the DCDHF-Me2 excited-state manifold.
#
# Stages run in SERIES on purpose: def2-TZVP TD-DFT on 39 atoms is ~900 basis
# functions, and two of these at once will not fit in 15 GB. Each stage is a
# separate process, so a failure in one leg leaves the others' output intact.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

PY="${PSI4_PYTHON:-/home/peter/miniconda3/envs/psi4_19/bin/python}"
THREADS="${THREADS:-6}"
MEMORY="${MEMORY:-6 GB}"
TD_BASIS="${TD_BASIS:-def2-tzvp}"
OPT_XYZ="geometry/dcdhf-me2-def2-svp-opt.xyz"

echo "== stage 1/3: geometry optimization (B3LYP/def2-SVP) =="
if [ -f "$OPT_XYZ" ]; then
  echo "   $OPT_XYZ exists; skipping (delete it or pass --force to redo)"
else
  "$PY" run_tddft.py optimize --basis def2-svp --functional b3lyp \
      --threads "$THREADS" --memory "$MEMORY"
fi

for func in cam-b3lyp b3lyp; do
  echo "== stage 2/3: TD-DFT ${func}/${TD_BASIS} =="
  "$PY" run_tddft.py excite --geometry "$OPT_XYZ" --basis "$TD_BASIS" \
      --functional "$func" --threads "$THREADS" --memory "$MEMORY"
done

echo "== stage 3/3: postprocess =="
"$PY" postprocess.py

echo
echo "Done. Canonical artifacts:"
echo "  results/states_*.json   per-state energies, oscillator strengths, character"
echo "  results/summary.json    manifold + band occupancy + geometry comparison"
echo "  results/tables.md       rendered per-functional tables"
echo "  results/spectra_*.csv   stick spectra and (cosmetic) broadened curves"
