#!/usr/bin/env bash
# Canonical run for the BMN frontier-orbital note.
#
# Four rungs on one scaffold:
#   bmn-h  bmn-f  bmn-nh2  bmn-nme2   benzylidenemalononitrile, X = H -> NMe2
#
# Stages run in SERIES on purpose: def2-TZVP TD-DFT on ~18-26 atoms is several
# hundred basis functions, and two at once will not fit in 15 GB. Each stage is
# a separate process, so a failure in one leg leaves the others' output intact.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

PY="${PSI4_PYTHON:-/home/peter/miniconda3/envs/psi4_19/bin/python}"
THREADS="${THREADS:-6}"
MEMORY="${MEMORY:-6 GB}"
TD_BASIS="${TD_BASIS:-def2-tzvp}"
STATES="${STATES:-12}"
MOLECULES="${MOLECULES:-bmn-h bmn-f bmn-nh2 bmn-nme2}"
FORCE="${FORCE:-0}"

# FORCE=1 recomputes every stage, even when committed artifacts already exist.
# Use it to verify end-to-end reproducibility from a clean starting geometry.
force_opt() { if [ "$FORCE" = "1" ]; then echo "--force"; fi; }

echo "== 1/5: starting geometries =="
# Idempotent: build_geometries.py skips anything already present, so this is
# safe to re-run and does not silently rebuild an input a result depends on.
"$PY" build_geometries.py

for mol in $MOLECULES; do
  OPT_XYZ="geometry/${mol}-def2-svp-opt.xyz"

  echo "== 2/5: ${mol} geometry optimization (B3LYP/def2-SVP) =="
  if [ -f "$OPT_XYZ" ] && [ "$FORCE" != "1" ]; then
    echo "   $OPT_XYZ exists; skipping (delete it or set FORCE=1 to redo)"
  else
    "$PY" run_tddft.py optimize --molecule "$mol" --basis def2-svp \
        --functional b3lyp --threads "$THREADS" --memory "$MEMORY" $(force_opt)
  fi

  for func in cam-b3lyp b3lyp; do
    echo "== 3/5: ${mol} TD-DFT ${func}/${TD_BASIS} =="
    OUT="results/states_${mol}_${func}_${TD_BASIS}.json"
    # Skip rather than abort: this pipeline is resumable by design, so adding a
    # molecule must not force a recompute of results that already exist.
    if [ -f "$OUT" ] && [ "$FORCE" != "1" ]; then
      echo "   $OUT exists; skipping (delete it or set FORCE=1 to recompute)"
    else
      "$PY" run_tddft.py excite --molecule "$mol" --geometry "$OPT_XYZ" \
          --basis "$TD_BASIS" --functional "$func" --states "$STATES" \
          --threads "$THREADS" --memory "$MEMORY" $(force_opt)
    fi
  done
done

echo "== 4/5: HOMO/HOMO-1 and full frontier gaps parsed from the run logs =="
if [ -f results/orbital_gaps.json ] && [ "$FORCE" != "1" ]; then
  echo "   results/orbital_gaps.json exists; skipping (delete to redo or set FORCE=1)"
else
  "$PY" orbital_gaps.py $(force_opt)
fi

LOGS_DIR="${LOGS_DIR:-logs}"
if [ -f results/frontier_orbitals.json ] && [ "$FORCE" != "1" ]; then
  echo "   results/frontier_orbitals.json exists; skipping (delete to redo or set FORCE=1)"
else
  "$PY" extract_frontier.py --logs-dir "$LOGS_DIR" $(force_opt)
fi

echo "== 5/5: figure and publication metrics =="
node ./make-figure.mjs
node ./make-figure.mjs --check
node ./generate-metrics.mjs
node ./generate-metrics.mjs --check

echo
echo "Done. Canonical artifacts:"
echo "  geometry/<molecule>-def2-svp-opt.xyz     optimized geometries"
echo "  results/states_<molecule>_<functional>_<basis>.json  per-state manifold"
echo "  results/orbital_gaps.json                occupied frontier energies"
echo "  results/frontier_orbitals.json           HOMO-1, HOMO, LUMO, LUMO+1"
echo "  results/figure_frontier_levels.html      inline-SVG figure"
echo "  metrics.json                             the projection every cited number resolves from"
