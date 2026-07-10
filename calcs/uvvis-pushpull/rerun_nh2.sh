#!/bin/zsh
cd /Users/pvjohnst/noprofits/blog/calcs/uvvis-pushpull
export PSI_SCRATCH=/Users/pvjohnst/noprofits/blog/calcs/uvvis-pushpull/scratch
PY=/opt/homebrew/Caskroom/miniforge/base/envs/qchem/bin/python
for m in aniline pNA; do
  echo "=== START $m $(date +%H:%M:%S) ==="
  $PY run_one.py $m && echo "=== OK $m ===" || echo "=== FAIL $m ==="
done
echo "=== NH2 RERUN DONE $(date +%H:%M:%S) ==="
