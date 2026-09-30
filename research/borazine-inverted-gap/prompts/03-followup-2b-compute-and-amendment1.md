You are working in Peter V. Johnston's Hakyll notebook repo pvjohnston/pvjohnston.com on his Mac. Follow AGENTS.md: never author in the primary checkout; create a feature branch `post/borazine-inverted-gap-followup` in a new worktree under ~/noprofits/pvjohnston-worktrees/. Open a DRAFT PR when done. Do not merge.

GOAL
Write a short follow-up Research note to the published post posts/2026-09-28-borazine-inverted-gap (Shizu et al., Commun. Chem. 2026, doi 10.1038/s42004-026-02141-0; our preregistered PySCF rematch of ADC(2)/def2-TZVP inverted singlet-triplet gaps). The follow-up covers (a) molecule 2b, which we could not finish on this machine, and (b) Amendment 1 (EOM-CCSD/def2-TZVP on 1 and 11), if its results exist.

SOURCES (read these; do not invent numbers or compound names)
- Research pack: research/borazine-inverted-gap/ (prereg frozen at commit 59824fd; Amendment 1 at 8c0a21e; prompts/ folder with README and PUBLIC_FILES.txt).
- Run package and results: ~/Molecules/ist-borazine/ (status.json, JOURNAL.md, run_queue.sh, run_adc2_pyscf.py, package/tier1/results/*.json and *.log).
- Use compound labels exactly as the existing post and the paper's SI use them.

PART A: 2b ADC(2)/def2-TZVP, prepared for a team with more compute
Facts from the run (verify against JOURNAL.md and 2b_adc2_def2-tzvp.log):
- Machine: MacBook Pro M1 Pro, 32 GB RAM. PySCF RADC with DF (def2-tzvp-ri), --mem-mb 24000, 14 frozen core orbitals.
- 2b active space: 33 occupied x 447 virtual. For comparison 2a: 24 x 324, which finished in 11.5 h with 25 GB peak RSS.
- The ADC(2) doubles space scales as (o*v)^2, so 2b's is about 3.6x larger than 2a's; we estimate roughly 90 GB of memory to run it in core.
- MP2 reference correlation energy printed: -2.03570034 Eh. The run then entered the RADCEE Davidson solve and wrote nothing further.
- After 19.6 h wall (70412 s) the process had used about 12.4 h CPU, memory footprint about 37 GB, swap 28.4 of 29.7 GB used. We stopped it (SIGTERM, exit -15) on 2026-09-30 at 08:06 PT.
- Published 2b ADC(2)/def2-TZVP value: +106 meV. Prereg sign test: fails if our ΔEST(2b) <= 0.
Peter's compute rule: nothing that would take weeks on this Mac. Write this part as "we prepared this experiment for a team with access to higher levels of compute to run". Make no claim that we ran it or have a result. Commit into research/borazine-inverted-gap/ everything needed to run it: 2b coordinates, exact command line and script version, basis/aux/frozen-core settings, the frozen falsifier, expected output format (results JSON schema), the published value to compare against, and our resource estimate with the reasoning above. Add these to PUBLIC_FILES.txt so readers can download them.

Invite readers openly: say plainly that we can't accomplish this calculation without more compute, that everything is prepared for anyone who can, and that we welcome feedback, comments, and results from anyone interested. Check what contact routes the site and repo actually offer (Contact page, GitHub issues or discussions) and link the real ones; do not invent a comment system.

PART B: 2b EOM-CCSD/def2-SVP and Amendment 1
Read package/tier1/results/ for 2b_eomccsd_def2-svp.json, 1_eomccsd_def2-tzvp.json, 11_eomccsd_def2-tzvp.json. For each that exists, report ΔEST in meV. Apply the Amendment 1 rule exactly as frozen in 8c0a21e: if ΔEST(11) <= 0, A1 is inconclusive; otherwise ΔEST(1) > +50 meV means method-driven disagreement, ΔEST(1) < -50 meV means the def2-SVP sign flip was basis-driven, anything between is non-decisive. Any result file that is missing: state it is still running and leave a clearly marked placeholder, with no numbers.

STYLE
Match the house style of the existing borazine post and notes/blog-authoring.md: ACS-style Research note, tables and code captions ABOVE the table/fence, figure captions below. Link back to the first post. Include a short code listing (the exact 2b command) as a captioned code block. Plain, direct prose; avoid repeated "this is X, not Y" contrasts. No X/Twitter posting.

PROMPT ARCHIVE (required)
Save this entire prompt verbatim as research/borazine-inverted-gap/prompts/03-followup-2b-compute-and-amendment1.md. Add a row to prompts/README.md (recipient: Codex CLI; date; what it did) and an entry in PUBLIC_FILES.txt. In the post, show a short excerpt as a code block and link the full file.

DONE WHEN
The site builds locally with no errors, the new post renders, all new public files resolve, and a draft PR is open. Report the PR URL, the ΔEST values you used, and anything you could not verify.
