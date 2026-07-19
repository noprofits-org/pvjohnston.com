# Operator-only provenance

Files in this directory document real identities, corpus roles, score sources,
candidate-return locations, extraction decisions, and manual corrections. They
are part of the reproducible repository but are never embedded in a model
prompt and never listed in the `cases` array of `../manifest.json`.

Complete `pilot-corpus.csv` before assigning arbitrary model-facing opaque case
IDs. The assignment is not claimed to be randomized; the IDs must encode no
identity or corpus role.
The identity map should be revealed for scoring the identification probe only
after every scheduled model response has been collected.

`EXPERT_REVIEW.md` is the pre-collection audit packet for a later
music-theory reviewer. It joins the opaque dossiers to exact operator-only
source coordinates, documents known representation limits and open findings,
and points to `EXPERT_REVIEW_TEMPLATE.json` for structured criticism. Its
existence does not imply expert verification.

`audits/2026-07-19-fable5-read-only-reconciliation.md` records which findings
from a model-produced repository survey remained current after the sixth
dossier and schema-3.1 work. It is a dated protocol audit, not independent
musicological review.

`IDENTIFICATION_ADJUDICATION_EXECUTION.md` is an outcome-blind pre-collection
clarification of how the frozen L0/L1/L2 rule will handle text normalization,
contradictory structured fields, and hedged multiple candidates. It changes no
threshold or identity value and must not use response confidence or prose as
scoring evidence.
