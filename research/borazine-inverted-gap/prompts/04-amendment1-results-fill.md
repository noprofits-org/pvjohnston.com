Fill the Amendment 1 placeholders in the already-published borazine follow-up note. Work only from the local checkout; never open live pvjohnston.com URLs. Verify against _site/ after a local rebuild.

CONTEXT
- Repo: pvjohnston/pvjohnston.com. Per AGENTS.md, never author in the primary tree: branch `post/borazine-a1-results` from main in a new worktree under ~/noprofits/pvjohnston-worktrees/.
- Published follow-up: posts/2026-09-30-borazine-inverted-gap-followup.md (merged via PR #119; A1 rows say Pending).
- First post: posts/2026-09-28-borazine-inverted-gap.md.
- Research pack: research/borazine-inverted-gap/
- Result files on this Mac (read the values from them; do not retype):
  - ~/Molecules/ist-borazine/package/tier1/results/1_eomccsd_def2-tzvp.json   (dEST_meV ≈ -47.5)
  - ~/Molecules/ist-borazine/package/tier1/results/11_eomccsd_def2-tzvp.json  (dEST_meV ≈ +520.8)
  - ~/Molecules/ist-borazine/package/tier1/results/2b_eomccsd_def2-svp.json   (dEST_meV ≈ +186.4)
- Frozen A1 rule (commit 8c0a21e): if ΔEST(11) <= 0, inconclusive; else ΔEST(1) > +50 meV method-driven; ΔEST(1) < -50 meV basis-driven; otherwise non-decisive. Applied verdict: NON-DECISIVE (11 = +520.8 > 0; 1 = -47.5 lies inside ±50).

DO
1. Copy the three result JSONs (plus their .log/.time.log/.stdout.log companions, following the existing archive naming) into research/borazine-inverted-gap/results/ and add them to PUBLIC_FILES.txt. Wire the numbers through the existing metrics mechanism so the post reads them from retained files.
2. Update the follow-up post:
   - Table: fill 2b EOM-CCSD/def2-SVP (+186.4 meV) and both A1 rows (1: -47.5, 11: +520.8), marked completed.
   - Abstract, Discussion, Conclusion: state the preregistered verdict as non-decisive, and report plainly what the numbers show: borazine's EOM-CCSD ΔEST changes sign between def2-SVP (+117.6 meV) and def2-TZVP (-47.5 meV), a 165 meV basis shift, while boroxine stays positive. So the first post's observation that EOM-CCSD never inverts holds only at def2-SVP. Do not upgrade the verdict beyond what the frozen rule says; do not claim convergence to the basis-set limit.
   - Keep the 2b ADC(2)/def2-TZVP "prepared for a team with more compute" section and the open invitation for feedback unchanged.
3. In the first post, add a short dated "Update (2026-09-30)" note near the EOM-CCSD statement saying the def2-TZVP rerun inverts borazine (-47.5 meV) and linking the follow-up. Do not otherwise rewrite the first post.
4. House style: ACS-style Research note, table and code captions above, figure captions below; plain prose, avoid repeated "this is X, not Y" contrasts. No X posting.
5. Save this prompt verbatim as research/borazine-inverted-gap/prompts/04-amendment1-results-fill.md, add a prompts/README.md row (recipient: Codex CLI; date 2026-09-30; what it did), and list it in PUBLIC_FILES.txt.
6. Rebuild and run the repo's usual build, test, bibliography, metrics, link, and allowlist checks locally.
7. Open a draft PR against main stating the three ΔEST values and the non-decisive verdict. Do not merge.

Report the PR URL, the values used, and anything you could not verify.
