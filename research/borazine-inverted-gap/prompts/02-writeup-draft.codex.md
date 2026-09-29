You are working in the pvjohnston.com Hakyll repo, worktree
/Users/pvjohnston/noprofits/pvjohnston-worktrees/borazine-inverted-gap, branch post/borazine-inverted-gap.
Follow AGENTS.md and notes/blog-authoring.md exactly (ACS style; table and Code captions ABOVE, figure captions below).
Do not push. Do not touch css/ or templates/. Commit locally when done.

GOAL
Write the draft post posts/2026-09-28-borazine-inverted-gap.md (keep draft: true) as an ACS-style Research note:
a preregistered rematch of Shizu, Ishihara, Uratani, Kaji, Commun. Chem. 2026, doi:10.1038/s42004-026-02141-0,
which reports an inverted singlet–triplet gap (ΔEST < 0) for borazine at ADC(2).

SOURCES OF TRUTH (read them; do not invent numbers)
- research/borazine-inverted-gap/PREREGISTRATION.md (frozen commit 59824fd; Amendment 1 appended in 8c0a21e)
- Results JSONs + JOURNAL.md: ~/Molecules/ist-borazine/package/tier1/results/*.json and ~/Molecules/ist-borazine/JOURNAL.md
  Copy the finished results JSONs and JOURNAL.md into research/borazine-inverted-gap/results/ and add them to PUBLIC_FILES.txt.
- research/borazine-inverted-gap/prompts/ (README.md + 01-setup-and-launch-tier1.codex.md)
- Published values: expected/published_SI_tables_1-3.csv inside the research pack, or the prereg S1 line.

WHAT TO REPORT (compute every number from the JSONs; these are the expected values for cross-checking)
Table 1 (ADC(2)/def2-TZVP, RI, frozen core, PySCF 2.14.0, M1 Pro): id, name, S1 (eV), T1 (eV), ΔEST ours, ΔEST published, |diff|, verdict.
  1 borazine −191.9 vs −193 (P1: supported, magnitude reproduced)
  11 boroxine +278.4 vs +279 (P2 control passes, reproduced)
  9 +29.3 vs +26; 10 −46.9 vs −47; 12 −158.5 vs −160 (sign test passes); 2a +35.0 vs +34.
  2a, 9, 10: sign non-decisive by preregistration.
Table 2 (exploratory, outside the falsifier): EOM-CCSD/def2-SVP ΔEST for 1, 11, 9, 10, 12, 2a
  (about +118, +473, +15, +45, +29, +151 meV). Every EOM-CCSD value is positive, including borazine.
  State plainly: this is a small-basis cross-check, not a verdict, and was not part of the frozen falsifier.

SECTIONS
Abstract; Introduction (why inverted gaps matter, what the paper claims, one paragraph);
Preregistration (what was frozen, when, hash, P1/P2/S1, ±50 meV tolerance and its reasoning, smoke-test disclosure);
Methods (short, with one Code listing, caption above, excerpted from run_adc2_pyscf.py; link the full file);
Results (Table 1, Table 2, runtimes and peak memory from JOURNAL.md);
Discussion (ADC(2) reproduces the paper closely; EOM-CCSD at def2-SVP disagrees on sign across the whole set;
  that could be method or basis, which is exactly what Amendment 1 tests);
Prompts (one short excerpt of the Codex prompt as a code block, then link the full file and prompts/README.md;
  mention the checksum deviation recorded there);
What comes next; Data and code availability; References (ACS format).

DISCLOSURES TO INCLUDE
- Runtimes are pessimistic: from 2026-09-21 to 2026-09-29 a parked, unrelated ORCA job kept relaunching on the same Mac
  and shared its cores. Energies are unaffected.
- The 2a ADC(2) run printed one non-converged Davidson root: the 4th singlet at 7.40 eV, far above S1/T1; no effect on ΔEST.
- The JSON "threads" field records 1, but the process used about 2 cores; report it as recorded, with that note.

WHAT COMES NEXT (brief, forward-looking, no claims)
- Running now: 2b ADC(2)/def2-TZVP (the second sign test; published +106 meV) and its EOM-CCSD/def2-SVP check.
- Amendment 1, preregistered before running: EOM-CCSD/def2-TZVP on borazine and boroxine, with the frozen decision rule
  (boroxine must stay positive; borazine > +50 meV means method-driven disagreement, < −50 meV means basis-driven, between is non-decisive).
- A nod to the series: more inverted-gap rematches in this vein, run on a laptop where feasible; anything needing weeks of compute
  is written up as "prepared for a team with access to higher levels of compute to run", with inputs committed and no claim we ran it.
- Say the post will be updated when 2b and Amendment 1 finish.

STYLE
Plain, precise prose; no hype; avoid repeated "this is X, not Y" constructions. Numbers to 0.1 meV in tables, whole meV in text.
Do not add an experiment: line or metrics.json yet.

DONE WHEN
The site builds cleanly (stack/cabal build + site build per AGENTS.md), the post renders with both tables and the code listing,
PUBLIC_FILES.txt includes results and prompts, and there is one local commit. Report the commit hash and any number that
did not match the expected values above.
