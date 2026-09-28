# Prompts

The AI prompts that set up and launched this experiment, saved verbatim so readers can see exactly what the
agents were told. The calculations were run by the scripts in `tier1/`, not by the language model; the
prompts only built the scaffold, installed PySCF, froze the preregistration and started the job queue.

| File | Given to | When (PT) | What it did |
|---|---|---|---|
| `01-setup-and-launch-tier1.codex.md` | Codex CLI on the M1 | 2026-09-28, about 12:30 | Checked the input package, created this directory and the draft post, installed PySCF 2.14 in a venv, smoke-tested on water, committed the frozen preregistration (59824fd, 12:51), and started the launchd queue for 1, 11, 9, 10, 12, 2a plus EOM-CCSD/def2-SVP checks. |

One disclosed deviation: the prompt's package checksum refers to an earlier build of the input tarball.
Before launch that tarball was rebuilt so the preregistration carried the smoke-test disclosure and the
approved 2b run; the committed PREREGISTRATION.md (sha256 2fe30830…2fb7) is the rebuilt version.
