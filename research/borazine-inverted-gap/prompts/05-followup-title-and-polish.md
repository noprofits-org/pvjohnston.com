Polish draft PR #120 (branch post/borazine-a1-results) in pvjohnston/pvjohnston.com before merge. Work in the existing worktree for that branch under ~/noprofits/pvjohnston-worktrees/ (never the primary tree, per AGENTS.md). Read only local files; never open live pvjohnston.com URLs. Verify against _site/ after a local rebuild.

File: posts/2026-09-30-borazine-inverted-gap-followup.md

1. Title. The borazine EOM-CCSD sign flip at def2-TZVP is now the lead finding alongside the 2b compute limit. Retitle so both are visible, in plain words, e.g. "Borazine's EOM-CCSD gap turns negative at def2-TZVP; 2b needs more memory" (pick the clearest short version; no colon-heavy headline). Do NOT rename the file or change the URL slug.
2. Description front matter: lead with the borazine result (+117.6 to −47.5 meV, Amendment 1 non-decisive), then the 2b handoff. Use the metric values, not new hand-typed numbers where the template supports metrics; if front matter cannot render metrics, the rounded values above are acceptable.
3. contribution / contribution-type front matter: add the measured basis sensitivity of borazine's EOM-CCSD gap (sign change between def2-SVP and def2-TZVP) next to the existing 2b resource-limit/handoff contribution. Keep status: inconclusive (2b ADC(2) has no gap; A1 is non-decisive).
4. Abstract and Introduction: make sure the first two sentences a reader sees state the borazine flip and the non-decisive verdict, then the 2b limit. Keep the "prepared for a team with access to higher levels of compute to run" wording and the open invitation for feedback, comments and results exactly as they are.
5. Attribution: the sentence "Peter observed a roughly 37 GB footprint and 28.4 of 29.7 GB swap..." should read as an observation made during monitoring ("We observed..."), keeping the caveat that no monitor capture was retained and that the timing log counters are the machine record.
6. In the first post (posts/2026-09-28-borazine-inverted-gap.md), make sure the dated Update paragraph is separated by blank lines from the paragraphs around it, and that its link text still fits the new follow-up title. Change nothing else there.
7. Check the site's post index, home page, and any tag or feed listing pick up the new title correctly.
8. Style: ACS-style Research note, plain prose, avoid repeated "this is X, not Y" contrasts. No X posting.
9. Save this prompt verbatim as research/borazine-inverted-gap/prompts/05-followup-title-and-polish.md, add a prompts/README.md row (recipient: Codex CLI; date 2026-09-30; what it did), and list it in PUBLIC_FILES.txt. Add one sentence in the follow-up's Prompts and data section linking prompt 05.
10. Rebuild and run the repo's usual build, test, bibliography, metrics, link, allowlist and whitespace checks. Push to the same branch so PR #120 updates; update the PR title/body to match. Leave it as a draft. Do not merge.

Report the new title, the final description line, and check results.
