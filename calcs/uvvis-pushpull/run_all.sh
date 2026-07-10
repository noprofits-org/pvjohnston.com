#!/bin/zsh
cd /Users/pvjohnst/noprofits/blog/calcs/uvvis-pushpull
export PSI_SCRATCH=/Users/pvjohnst/noprofits/blog/calcs/uvvis-pushpull/scratch
PY=/opt/homebrew/Caskroom/miniforge/base/envs/qchem/bin/python
for m in benzene aniline nitrobenzene pNA; do
  echo "=== START $m $(date +%H:%M:%S) ==="
  $PY run_one.py $m && echo "=== OK $m $(date +%H:%M:%S) ===" || echo "=== FAIL $m $(date +%H:%M:%S) ==="
done
echo "=== ALL DONE $(date +%H:%M:%S) ==="
