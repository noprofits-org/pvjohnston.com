# Preregistration: experiment title

Freeze this document before canonical execution. Before result exposure, review
may require a new version. After any result exposure, do not silently edit this
file or redefine an existing run: create a new protocol version plus a small
`workflow/AMENDMENT.example.md`-based receipt and pass
protocol amendment, amendment review, amended setup, and amended setup review
before execution.

## Intellectual contract

- Post type: research / understanding
- Shelf entry (Research only):
- Primary source and relationship to it:
- Contribution sentence and type (Research only):
- Question:
- Hypothesis and falsifier (Research only):
- Explanatory route and stopping boundary (Understanding only):
- Why the other outcome is still publishable (Research only):
- What this experiment can establish:
- What it cannot establish:

## Pilot boundary

- Permitted smoke or feasibility checks:
- Pilot-only inputs/seeds:
- Evidence that pilots cannot enter the canonical result:
- Conditions that park the experiment before production:

## Frozen protocol

- Exact inputs, versions, and acquisition:
- Parameters, cases, seeds, repeats, and ordering:
- Controls and ablations:
- Primary and secondary metrics:
- Decision rule for supported / falsified / inconclusive (Research only):
- Demonstration reconstruction and failure conditions (Understanding only):
- Exclusions and missing-data handling:
- Stopping and expansion rules:
- Same-run resume conditions and exact restart semantics:
- Fresh-run infrastructure retry conditions authorized before execution:
- Analysis-plan rerun conditions authorized before result exposure:
- Exact restartable production command:
- Expected raw and derived artifact paths:

## Execution and analysis boundary

- Environment lock and hardware assumptions:
- Maximum compute, wall time, memory, and paid-resource budget:
- Run/shard identity and append-only output rule:
- Integrity checks before analysis:
- Prespecified analysis and uncertainty calculation:
- Planned figures and metric projection:
- Exploratory diagnostics allowed only after the primary analysis:

## Publication boundary

- Rights, privacy, secrets, and public-file review:
- Reproducibility level this design can earn:
- Archived-evidence or future-rerun constraints:

## Amendments

None at freeze. After exposure, keep this frozen version and record each
proposed successor separately. The amendment receipt names the exposed results,
invalid or incomplete lineage, quarantined artifacts, old and new protocol
digests, changed and unchanged decisions, confirmation-bias risk, and why the
revision still answers the same question. A new hypothesis or explanatory
question starts a new workflow rather than becoming an amendment.
