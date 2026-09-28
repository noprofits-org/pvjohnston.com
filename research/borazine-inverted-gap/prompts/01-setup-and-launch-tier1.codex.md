You are setting up and launching a computational-chemistry experiment for Peter V. Johnston's notebook (repo pvjohnston/pvjohnston.com) on this Mac (Apple M1 Pro, 32 GB, 8P+2E cores). Read AGENTS.md, notes/blog-authoring.md (§0, §1, §2, §7, §9) and research/_TEMPLATE/ first and follow them.

GOAL
Reproduce the ADC(2)/def2-TZVP singlet-triplet gaps (ΔEST = E(S1) − E(T1)) that Shizu, Ishihara, Uratani, Kaji, "Inorganic benzenes with inverted singlet-triplet gaps", Commun. Chem. 2026, doi:10.1038/s42004-026-02141-0, report for borazine (1), the boroxine control (11), and molecules 9, 10, 12, then 2a, using open-source PySCF DF-ADC(2) on the paper's own PBE0/6-31G(d) geometries. Plus an EOM-CCSD/def2-SVP cross-check. The preregistration (falsifier) is already written and must be frozen by a commit BEFORE any production calculation starts.

HARD RULES
- Do not edit PREREGISTRATION.md, the tier1 scripts, the xyz files or expected/ after the freeze commit. If a script crashes, stop that job, record the error, and report; do not patch and rerun silently.
- Do not interpret results beyond what PREREGISTRATION.md says. Do not write numbers from our runs into the post.
- Do not touch: css/, templates/, lib/, app/, scripts/, .github/, index.html, standalone *.markdown pages, images/, fonts/, js/, downloads/, stack.yaml*, *.cabal, any other post, any other research/* directory, research/_TEMPLATE/, research/metrics.schema.json. bib/bibliography.bib and notes/questions.md are append-only.
- Exactly one local commit (the freeze). No push, no PR, no branch deletion, no stash. Do not touch the parked MECP LaunchAgent com.pvjohnston.hillel-m4-mecp-ci or anything under ~/Molecules/hillel-m4-sft/.
- The only install allowed is a fresh venv with pyscf==2.14.* (numpy/scipy/h5py come with it). No Homebrew, no conda changes, no system Python changes.
- Do not start 2b or 2c. They are not queued.

STEP 1. Verify and unpack the inputs
shasum -a 256 ~/Molecules/ist-borazine/package.tar.gz must equal 71c2d85d5dcc1cded1d88a2b5351455b9993999cf9383da7a35ec096862c8327. If missing or different, STOP and report. Extract it into ~/Molecules/ist-borazine/ (gives ~/Molecules/ist-borazine/package/). This directory is the run directory; calculations run here, not in the repo.

STEP 2. Worktree and scaffold
- Check git worktree list and git branch -vv. Then, per AGENTS.md: git -C "$primary" fetch origin, and git -C "$primary" worktree add -b post/borazine-inverted-gap "$trees/borazine-inverted-gap" origin/main. If the branch already exists, STOP and report.
- In the worktree create research/borazine-inverted-gap/ from research/_TEMPLATE/, filled from package/:
  * PREREGISTRATION.md: copy package/PREREGISTRATION.md verbatim. Remove PREREGISTRATION.example.md.
  * README.md: template README filled from package/README.md. Status "running", traceability "not yet established", reproduction level "none".
  * sources.json from package/sources.json (remove the example file).
  * Copy byte-for-byte: xyz/ (57 .xyz + index.json + basis_counts.json), expected/published_SI_tables_1-3.csv, tier1/ (run_adc2_pyscf.py, run_eomccsd_pyscf.py, orca/*.inp), tier2/, bench/, parse_xyz.py, parse_tables.py, count_bf.py, estimate.py.
  * environment.md: an "M1" section filled from real probes (sw_vers, sysctl -n machdep.cpu.brand_string hw.memsize hw.perflevel0.physicalcpu, the venv's python --version, and pyscf/numpy/scipy versions after Step 3).
  * PUBLIC_FILES.txt listing only README.md and PREREGISTRATION.md for now (match the template's path format; delete the example).
  * No metrics.json or generate-metrics.mjs yet; delete their .example copies.
  * .gitignore in the experiment dir: tier1/results/, *.log, .venv/, __pycache__/.
- Draft post posts/2026-09-28-borazine-inverted-gap.md with front matter: title "Does borazine keep its inverted singlet-triplet gap? (draft)", date 2026-09-28, author Peter Johnston, tags "quantum chemistry, excited states", description (≤155 chars, no numbers of ours), post-type research, contribution "An independent open-source ADC(2)/def2-TZVP singlet-triplet gap for borazine and boroxine on the published geometries, which is not in Shizu et al. 2026.", contribution-type "untested regime", draft: true. Do NOT add experiment: (the build fails without metrics.json); leave the YAML comment "# experiment: borazine-inverted-gap  (add when metrics.json exists)". Body: the IMRaD headers from blog-authoring §2 with one-line TODOs, except Introduction (one plain sentence naming the source by sentence two, citing [@Shizu2026]), Computational Methods (short paragraph pointing to PREREGISTRATION.md; says SCS-CC2 is not run by us and the numbers in expected/ are the authors'), and Results ("Calculations running; no results yet."). End with a bare "## References".
- Append to bib/bibliography.bib only if no existing entry matches "shizu" or the DOI (if one exists under another key, cite that key instead):
  @article{Shizu2026, author = {Shizu, Katsuyuki and Ishihara, Kuraudo and Uratani, Hiroki and Kaji, Hironori}, title = {Inorganic benzenes with inverted singlet-triplet gaps}, journal = {Communications Chemistry}, year = {2026}, doi = {10.1038/s42004-026-02141-0}}
  Do not invent a volume or article number.
- Append a notes/questions.md shelf entry in the file's documented format: "## Does borazine keep its inverted S1/T1 gap under an independent ADC(2)? (Shizu et al. 2026)", with Observed (paper: ADC(2)/def2-TZVP ΔEST −193 meV borazine, +279 meV boroxine; SCS-CC2 and ADC(2) disagree in sign for 2a, 2b, 9 per SI Tables 1/3), Source, Type (untested regime), Contribution (candidate), Falsifier (research/borazine-inverted-gap/PREREGISTRATION.md P1/P2/S1), Status: running.
- Cheap checks in the worktree: node scripts/verify-bib.mjs, node scripts/verify-metrics.mjs, the bib brace-balance awk one-liner from AGENTS.md, grep for [@Shizu2026] in the post, post ends with "## References". No stack/site build.

STEP 3. Environment (run directory, not the repo)
python3 -m venv ~/Molecules/ist-borazine/.venv, then ~/Molecules/ist-borazine/.venv/bin/pip install "pyscf==2.14.*". Smoke test with the venv python on WATER only (not any paper molecule): RHF/def2-SVP, then RADC(2)-ee density-fit with def2-svp-ri, 2 roots, and a UADC(2) run with 4 roots confirming that the <S^2> path used by tier1/run_adc2_pyscf.py (ua._adc_es.get_spin_square() after kernel) returns values. Report whether it worked or the script would fall back to RADC matching. If pip or the smoke test fails, STOP and report.

STEP 4. Freeze the preregistration (the one commit)
In the worktree: git add the new experiment dir, the post, and the bib/questions appends; commit with message "borazine-inverted-gap: scaffold + frozen preregistration (no results)". Record the commit hash, its ISO timestamp, and shasum -a 256 of PREREGISTRATION.md into ~/Molecules/ist-borazine/FREEZE.txt (outside the repo). Also confirm that shasum of package/PREREGISTRATION.md equals the worktree copy.

STEP 5. Queue runner under launchd (not nohup: a departing shell kills the process group)
Write ~/Molecules/ist-borazine/run_queue.sh (bash, set -u) that runs jobs strictly one at a time from ~/Molecules/ist-borazine/package/tier1 with the venv python, OMP_NUM_THREADS=8, and wraps the whole queue in caffeinate -ims. Queue in this order:
  1. run_adc2_pyscf.py 1 --basis def2-tzvp --aux def2-tzvp-ri --mem-mb 24000
  2. run_adc2_pyscf.py 11 (same flags)
  3. run_eomccsd_pyscf.py 1 --basis def2-svp --mem-mb 24000
  4. run_eomccsd_pyscf.py 11 --basis def2-svp --mem-mb 24000
  5-7. run_adc2_pyscf.py 9, then 10, then 12 (same flags as job 1)
  8-10. run_eomccsd_pyscf.py 9, 10, 12 --basis def2-svp --mem-mb 24000
  11. run_adc2_pyscf.py 2a (same flags as job 1)
  12. run_eomccsd_pyscf.py 2a --basis def2-svp --mem-mb 24000
Idempotent: skip a job whose results/<id>_<method>_<basis>.json already exists. A failed job is logged and the queue moves on (a failed control is data, not a reason to stop). For each job, record start/end time, exit code, peak RSS (/usr/bin/time -l) and wall-clock. Maintain ~/Molecules/ist-borazine/status.json (current job, done, failed, queued, last update) and append one line per job to ~/Molecules/ist-borazine/JOURNAL.md. Write a LaunchAgent ~/Library/LaunchAgents/com.pvjohnston.ist-borazine-tier1.plist (RunAtLoad true, KeepAlive false, stdout/stderr to ~/Molecules/ist-borazine/launchd.{out,err}), load it with launchctl bootstrap gui/$(id -u), and confirm job 1 has started (PySCF log growing under package/tier1/results/, python process visible).

STEP 6. Report back, then stop
Worktree path and branch, the freeze commit hash and FREEZE.txt contents, git status --short (should be clean after the commit), cheap-check output, installed versions, smoke-test outcome (including the <S^2> path), the LaunchAgent label and how to stop it (launchctl bootout gui/$(id -u)/com.pvjohnston.ist-borazine-tier1), current status.json, and anything skipped with the reason. Do not wait for the queue to finish. Keep the Mac plugged in with the lid open; expected wall-clock is roughly 14–21 hours.
