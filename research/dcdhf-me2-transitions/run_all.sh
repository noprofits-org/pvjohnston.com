#!/usr/bin/env bash
# Canonical run for the excited-state manifolds.
#
# Two molecules, asking the same question and getting opposite answers:
#   dcdhf-me2 - an engineered single-molecule fluorophore, whose visible band
#               is ONE transition carrying most of the oscillator strength
#   benzene   - whose strongly allowed band is a symmetry-degenerate PAIR
#
# Stages run in SERIES on purpose: def2-TZVP TD-DFT on 39 atoms is ~800 basis
# functions, and two of these at once will not fit in 15 GB. Each stage is a
# separate process, so a failure in one leg leaves the others' output intact.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

PY="${PSI4_PYTHON:-/home/peter/miniconda3/envs/psi4_19/bin/python}"
THREADS="${THREADS:-6}"
MEMORY="${MEMORY:-6 GB}"
TD_BASIS="${TD_BASIS:-def2-tzvp}"
MOLECULES="${MOLECULES:-dcdhf-me2 benzene}"

for mol in $MOLECULES; do
  OPT_XYZ="geometry/${mol}-def2-svp-opt.xyz"

  echo "== ${mol} 1/3: geometry optimization (B3LYP/def2-SVP) =="
  if [ -f "$OPT_XYZ" ]; then
    echo "   $OPT_XYZ exists; skipping (delete it or pass --force to redo)"
  else
    "$PY" run_tddft.py optimize --molecule "$mol" --basis def2-svp \
        --functional b3lyp --threads "$THREADS" --memory "$MEMORY"
  fi

  for func in cam-b3lyp b3lyp; do
    echo "== ${mol} 2/3: TD-DFT ${func}/${TD_BASIS} =="
    STATES="results/states_${mol}_${func}_${TD_BASIS}.json"
    # Skip rather than abort: this pipeline is resumable by design, so adding
    # a molecule must not force a recompute of results that already exist.
    if [ -f "$STATES" ]; then
      echo "   $STATES exists; skipping (delete it to recompute)"
    else
      "$PY" run_tddft.py excite --molecule "$mol" --geometry "$OPT_XYZ" \
          --basis "$TD_BASIS" --functional "$func" \
          --threads "$THREADS" --memory "$MEMORY"
    fi
  done
done

echo "== 3/5: stationary-point check (DCDHF-Me2) =="
# Part of the canonical run, not an optional extra: the post cites these
# energies as evidence that the planar geometry is a minimum along the tested
# coordinates, so a command that claims to reproduce the results has to
# produce them too.
if [ -f results/stationary_check.json ]; then
  echo "   results/stationary_check.json exists; skipping (delete it to recompute)"
else
  "$PY" check_stationary.py --threads "$THREADS" --memory "$MEMORY"
fi

echo "== 4/5: postprocess (all molecules) =="
"$PY" postprocess.py

echo "== 5/5: publication metrics =="
# Closes the chain: every number cited in the post resolves from metrics.json,
# so regenerating it is part of reproducing the work rather than a separate
# editorial step. --check then proves the committed projection matches.
# The generator resolves the repository root from its own path, so it does not
# care what the working directory is.
if command -v node >/dev/null 2>&1; then
  node ./generate-metrics.mjs
  node ./generate-metrics.mjs --check
else
  echo "   node not found: metrics.json NOT regenerated." >&2
  echo "   The committed projection may be stale relative to results/." >&2
  exit 1
fi

echo
echo "Done. Canonical artifacts:"
echo "  results/stationary_check.json  planar-minimum evidence + symmetry self-test"
echo "  metrics.json            the projection every cited number resolves from"
echo "  results/states_<molecule>_<functional>_<basis>.json  per-state data"
echo "  results/summary.json    manifold + band occupancy + geometry comparison"
echo "  results/tables.md       rendered per-molecule, per-functional tables"
echo "  results/spectra_*.csv   stick spectra and (cosmetic) broadened curves"
