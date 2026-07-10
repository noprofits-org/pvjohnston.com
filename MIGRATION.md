# Migration from noprofits.org

This repository is phase one of the July 2026 person/project split.

## Boundary

- `pvjohnston.com`: Peter Johnston’s résumé, portfolio, and personal writing—science, mathematics, art, software, automation, and systems.
- `noprofits.org`: nonprofit-watchdog tools, public information, mission, and project identity.
- `blog.noprofits.org`: articles specifically about nonprofits, Form 990 data, grants, and the infrastructure behind noprofits.org.

## Initial content move

The source blog contained 67 posts. This repository copies 51 personal/general posts. Sixteen nonprofit-specific posts remain canonical at `blog.noprofits.org`: thirteen already categorized as nonprofit content plus three engineering posts specifically about noprofits infrastructure.

This phase is copy-first. The source blog is not pruned until the new domain deploys successfully and redirect pages are ready for every moved URL.

## Follow-up sequence

1. Deploy and verify `pvjohnston.com`.
2. Generate one redirect page at `blog.noprofits.org/posts/...` for each migrated post, pointing to the same path on `pvjohnston.com`.
3. Remove migrated post sources and unreferenced assets from `noprofits-org/blog`.
4. Refocus `noprofits-org.github.io` on the nonprofit project and replace the full résumé with a credit link to `pvjohnston.com`.
