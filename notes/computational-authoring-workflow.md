# Computational authoring as a reviewed graph

This workflow separates a computationally heavy note into bounded roles with
durable handoffs. It supplements, and does not replace,
`notes/blog-authoring.md`, `notes/worktrees.md`, and
`notes/research-journal.md`. Those documents remain authoritative for the form
of a post, branch ownership, verification, publication, and crash recovery.

The workflow coordinator records state. Role agents produce or review
artifacts; they do not advance themselves. Heavy calculations are still run by
the experiment's own commands, outside the workflow CLI and outside the normal
site build.

## Why this is a graph

The common case is a sequence, but the real process is not a checklist. A
review can return work to the immediately preceding role, expose a flaw several
stages upstream, quarantine a run, or turn a post-hoc question into a separate
experiment. Production can also fan out into independent registered shards and
join only after all of them pass an integrity review.

Two related graphs make those distinctions explicit.

### 1. The immutable provenance DAG

The scientific record is a directed acyclic graph of versioned artifacts:

```text
declared question (ready shelf entry for Research)
        |
        v
question packet -> frozen protocol + inputs + environment
                              |
                              v
                    reviewed implementation
                              |
                    +---------+---------+
                    |         |         |
                    v         v         v
                 run A      run B     run ...
                    |         |         |
                    +---------+---------+
                              |
                              v
                    sealed canonical outputs
                              |
                              v
                  analysis + metrics + figures
                              |
                              v
                         reviewed post
                              |
                              v
                     PR + CI receipt -> integration review
```

Every child names or is submitted against the exact parent artifacts it used.
An approval applies to those bytes, not merely to a filename or stage name. If
an accepted parent must change, a review back-edge returns the active state to
the appropriate producer. A new version then supersedes the prior lineage in
the work graph, the append-only event log preserves both, and every affected
downstream gate runs again. Raw production outputs are never overwritten to
make a retry look like the original run. Once any production result has been
exposed, a protocol-changing correction creates a separate amendment artifact,
passes `amendment_review`, and moves through `amended_setup` and
`amended_setup_review` to produce a new implementation/run lineage. It never
reaches backward and edits the original provenance.

### 2. The cyclic work-state graph

The coordinator moves work through activity nodes and independent review
nodes. The happy path is exactly:

```text
brainstorm
  -> question_review
  -> setup
  -> setup_review
  -> execute
  -> run_review
  -> analyze
  -> analysis_review
  -> write
  -> editorial_review
  -> ready_for_pr
  -> pr_review
  -> ready_to_merge
```

The useful back-edges and their workflow decision names are:

```text
question_review  -- revise --> brainstorm
question_review  -- park --> parked
setup_review     -- revise --> setup
setup_review     -- redesign --> brainstorm
run_review       -- resume --> execute
run_review       -- registered_retry --> execute
run_review       -- amend --> protocol_amendment
analysis_review  -- revise --> analyze
analysis_review  -- registered_rerun --> execute
analysis_review  -- amend --> protocol_amendment
editorial_review -- revise --> write
editorial_review -- reanalyze --> analyze
editorial_review -- amend --> protocol_amendment
ready_for_pr     -- submit --> pr_review
pr_review        -- revise --> write
pr_review        -- reanalyze --> analyze
pr_review        -- amend --> protocol_amendment
protocol_amendment -- submit --> amendment_review
amendment_review -- approve --> amended_setup
amendment_review -- revise --> protocol_amendment
amended_setup    -- submit --> amended_setup_review
amended_setup_review -- approve --> execute
amended_setup_review -- revise --> amended_setup
amended_setup_review -- amend --> protocol_amendment
every review     -- park --> parked
```

`park` does not mean that a hypothesis was falsified. It means the workflow
cannot justify continuing in its present lineage. A parked question remains on
the shelf; an inadmissible run is quarantined; a new scientific question
becomes a new workflow. A valid Research outcome of **supported**,
**falsified**, or **inconclusive** advances through analysis and writing on the
same terms.

## The programme loop and the post loop

There is one boundary outside the per-post graph. A Research question must
already have been on `notes/questions.md`; `brainstorm` selects and sharpens a
ready shelf question, but it does not invent a question and immediately promote
it into a post. New anomalies and next steps update the shared shelf in their
own `feature/` branch and PR. They never ride on a `post/<slug>` branch.

The Research post loop begins only after that shelf entry is ready. Its
Conclusion names the next experiment, which returns to the programme loop
through another question-shelf change. This is how one finished post can feed
another without allowing outcome-driven expansion of the current experiment.

An Understanding note uses the same handoff graph but a different intellectual
contract. Its brainstorm artifact declares the explanatory question, audience,
dependency-ordered route, computational demonstrations, and boundary instead
of novelty, a hypothesis, and a falsifier. Its analysis produces observations
and reproducible demonstrations, not a confirmatory verdict. Its writer follows
dependency order rather than IMRaD. Understanding questions do not need to
originate on the Research shelf.

## State and review decisions

Replay identifies one current activity, review, or terminal node and preserves
the earlier versions and transitions that led there. The only terminal states
are `parked` and `ready_to_merge`. Every review gate accepts `approve`, and each
gate exposes only the backward decisions that make sense there:

- `revise` returns to that gate's producer;
- `redesign` is a pre-result `setup_review` return to `brainstorm`;
- `resume` continues the same incomplete execution under its already approved
  restart contract;
- `registered_retry` starts a fresh run ID only for an infrastructure failure
  covered by a retry rule frozen before execution, without changing the
  scientific design;
- `registered_rerun` starts only a rerun already authorized by the frozen
  analysis plan before exposure, with no outcome-contingent change;
- `reanalyze` returns post or PR findings to the accepted analysis;
- `amend` sends any post-result protocol, implementation, input, case, seed,
  threshold, exclusion, or stopping-rule change through protocol amendment,
  amendment review, amended setup, and amended setup review; and
- `park` stops honestly without publication.

`resume`, `registered_retry`, and `registered_rerun` are deliberately distinct,
narrow safe execution edges: same incomplete run, fresh infrastructure attempt,
and fresh analysis-plan rerun, respectively. If the applicable frozen condition
does not exist, do not relabel an unregistered correction as a retry or rerun:
use `amend`. An amendment discloses which results were already exposed,
quarantines the affected lineage, states every changed and unchanged decision,
and explains why the revised protocol still answers the same question. A new
hypothesis or explanatory question starts a new workflow.

A review record must contain the gate name, decision, reviewed artifact paths
and digests, blocking findings, non-blocking observations, evidence for each
finding, and the node to which work should return. The reviewer reports those
fields to the coordinator. The coordinator, not the reviewer, records the
transition with the workflow CLI.

Workflow validity and scientific outcome are separate fields. Neither the CLI
nor a reviewer may treat a desired result as evidence that a gate passed.

## Role and mutation boundaries

The boundaries below are intellectual as well as filesystem boundaries. One
person may fill more than one role in different sessions, but nobody approves
their own submission. Use a fresh, independent reviewer session at every gate.
The CLI checks only that the submitted actor-ID strings differ; actor IDs are
self-asserted process labels, not authenticated identities. The coordinator is
responsible for honest, stable IDs and for ensuring that the reviewer is in
fact a different session or person. A different string alone does not establish
independence.

| Role | May mutate | Must not mutate or decide |
| --- | --- | --- |
| Coordinator | Workflow state, small handoff/review/PR receipts, worktree and PR lifecycle, and journal handoff metadata | Scientific artifacts, review findings, thresholds, results, or verdicts |
| Brainstormer | Initial question/protocol material, post-exposure amendment packets, and research-journal source/decision records | `notes/questions.md` on the post branch, production code or outputs, figures, post prose, or its own review |
| Experiment engineer | Prospective `setup` or post-exposure `amended_setup` source, tests, fixtures, input/source manifests, environment lock/record, exact run instructions, output schema, and restart contract under `research/<slug>/` | The frozen protocol or approved amendment, production runs, scientific interpretation, post prose, or its own review |
| Run operator | The same incomplete run for `resume`, or a new registered run directory for a normal run, `registered_retry`, or `registered_rerun`; raw outputs, stdout/stderr, run manifests, checksums, and execution journal checkpoints | Protocol, source, tests, environment definition, analysis, threshold tuning, post prose, or completed or quarantined run artifacts |
| Analyst | Analysis code, canonical derived results, diagnostics, figures, metric generator, and `metrics.json` | Frozen protocol, runner, raw outputs, unregistered stopping rules, narrative post claims, or its own review |
| Writer | `posts/<slug>.md` and append-only entries in `bib/bibliography.bib`; placement, alt text, and captions for reviewed figures | Protocol, code, raw or canonical results, metric values, figure data, or scientific decision rules |
| Independent reviewer | Nothing in the worktree; it may run genuinely read-only inspection commands and return findings for question, prospective/amended setup, run, analysis, editorial, amendment, and PR gates | Fixes, workflow transitions, new analyses, self-authored substitute artifacts, or approval of work it created |

The project-scoped Codex role definitions live in `.codex/agents/`. Their
instructions are deliberately narrow. The independent reviewer definition
requests a read-only sandbox, and returning a review message to the parent
coordinator does not require filesystem writes. A live parent permission
override can supersede that configured default, so the coordinator must not
grant a reviewer write access; a review conducted with writable permissions is
not independent under this workflow.

## Artifact and gate contracts

### `brainstorm` -> `question_review`

For Research, the brainstormer submits a question-and-protocol packet
containing:

- the exact ready entry from `notes/questions.md` and declared
  `post-type: research`;
- the recent primary source, source relationship, availability of its code and
  data, and the boundary imposed by anything unavailable;
- a one-sentence `contribution: X, which is not in [source]` and one of the
  allowed contribution types;
- a falsifiable hypothesis, its falsifier, and an explicit statement that the
  other outcome would still be published;
- what the proposed computation can and cannot establish;
- explicit separation and exclusion of every feasibility pilot; and
- a frozen, versioned preregistration with inputs, parameters, cases, seeds,
  grids, primary and secondary observables, thresholds, exclusions, fidelity
  gates, stopping rule, verdict rule, inconclusive conditions, analysis plan,
  expected artifacts, restart boundary, and public-data constraints.

For Understanding, the packet instead contains:

- `post-type: understanding` and one bounded explanatory question;
- the reader's assumed starting point and dependency-ordered explanatory route;
- the representations or mechanisms connected by each computational
  demonstration;
- what the calculations demonstrate, where the model stops, and which claims
  they cannot establish; and
- a frozen demonstration protocol with digital inputs, parameters,
  deterministic controls, generated quantities, environment, failure
  conditions, analysis route, expected artifacts, restart boundary, and
  public-data constraints, without a novelty claim, hypothesis, falsifier, or
  verdict.

Both forms include:

- the digital inputs, rough compute/storage budget, likely fidelity risks, and
  whether a feasibility pilot is needed; and
- explicit separation of exploratory work from the frozen production
  calculation or demonstration.

For Research, the question reviewer approves only when the contribution is
real, the source relationship is accurately bounded, both outcomes are
informative, and the frozen protocol closes the material researcher degrees of
freedom before production. A Research topic without a contribution sentence is
parked, not passed downstream for the writer to rescue. For Understanding, the
reviewer instead checks that the question is bounded, the route is genuinely
explanatory rather than a definition or plot collection, every demonstration
does necessary work, and the stopping boundary is explicit. For both, the work
must be executable without living subjects and its cost must be proportionate.

### `setup` -> `setup_review` and amended setup review

The experiment engineer turns the accepted frozen protocol into an
implementation packet:

- source and input provenance, licenses, checksums, acquisition instructions,
  and the intended public allowlist boundary;
- executable code, tests, tiny or synthetic fixtures, a native dependency lock
  or precise environment record, deterministic ordering, and one exact run
  command;
- restart and shard semantics, including which output paths are new and
  disjoint, what counts as complete, and how a failed shard is quarantined; and
- an analysis implementation that, for Research, machine-tests supported,
  falsified, and inconclusive decision branches before production data exists,
  or, for Understanding, reconstructs every generated quantity and tests
  declared failure and boundary cases without inventing a verdict.

The setup reviewer traces every scientific choice in the protocol into code,
tests seeds or deterministic controls and the form-appropriate analysis
branches, checks source-method fidelity, estimates the real compute budget, and
looks for ambiguous defaults, data leakage, silent overwrite, nondeterminism,
and unregistered researcher degrees of freedom. Review uses fixtures or pilots
only. No canonical production result may exist when setup is approved.

Before production exposure, an implementation bug returns to `setup` and a
scientific ambiguity can return to `brainstorm` through `redesign`. After
production exposure, amendment approval enters the separate `amended_setup`
node. Its independent `amended_setup_review` may `approve -> execute`,
`revise -> amended_setup`, `amend -> protocol_amendment`, or `park`; it cannot
use the prospective `redesign` edge. No ambiguity is ever resolved by an
undocumented choice in code.

### `execute` -> `run_review`

The run operator receives the approved protocol, implementation commit or
digest, input digests, environment, run identifier, registered command, and
expected shard manifest. The operator creates:

- one new output namespace per run and, when applicable, per registered shard;
- an execution manifest binding run, protocol, implementation, environment,
  inputs, parameters, seeds, timestamps, hardware, commands, and exit status;
- raw stdout/stderr and native outputs without interpretation or cleanup; and
- checksums and completeness records sufficient to seal admitted artifacts.

The operator may monitor resource health and registered fidelity gates. The
operator may not add cases, seeds, observables, thresholds, or stopping rules
after seeing emerging values. A transient failure may `resume` only as the same
incomplete run under the frozen restart contract. It may use
`registered_retry` only to start a fresh run ID under an infrastructure retry
rule frozen before execution. Otherwise the run returns for amendment or parks.

The run reviewer checks lineage, expected shard count, registered inputs and
seeds, exit status, checksums, convergence/fidelity gates, missingness, stopping
rules, and evidence of overwrite or cherry-picking. This is an admissibility
review, not an interpretation of whether the numbers are exciting. `approve`
seals the admitted raw artifacts for analysis. `resume` is allowed only for the
same incomplete run under the frozen restart contract. `registered_retry` is
allowed only for a fresh infrastructure attempt prospectively authorized
before execution; its report cites that exact rule and uses a new run ID. Any
discovered change to protocol, code, environment definition, inputs, cases,
seeds, gates, or stopping takes `amend`; a valid scientific stop still takes
`approve` and is analyzed.

### `analyze` -> `analysis_review`

The analyst consumes only admitted, sealed outputs and produces:

- deterministic analysis code and a canonical rich result artifact;
- for Research, the preregistered verdict derived mechanically from the frozen
  decision rule, or, for Understanding, the frozen generated demonstrations and
  observations without a verdict;
- uncertainty, sensitivity checks, registered diagnostics, and a separate
  namespace and label for any post-hoc diagnostic;
- reader-facing plots whose values, axes, clipping, uncertainty, and callouts
  are recoverable from the canonical result;
- a cheap generator for typed `metrics.json` values, with fingerprints of its
  canonical inputs; and
- the commands needed to regenerate analysis, figures, and metrics without
  repeating the expensive experiment.

For Research, the analyst does not repair an inconclusive outcome by changing a
threshold or adding a run; an interesting unregistered contrast is reported as
exploratory or becomes a new shelf question. For Understanding, an unplanned
demonstration is labeled as such and a route beyond the frozen explanatory
boundary becomes separate work.

The analysis reviewer runs a genuinely read-only regeneration/check mode
against the sealed inputs, applies the form-appropriate decision or
demonstration contract, compares planned and executed analyses, audits
units/uncertainty/axes/outliers, and tests that figures and metrics say exactly
what the canonical result says. If no read-only check exists, the review returns
`revise` so the analyst can add one; neither the reviewer nor coordinator
creates substitute scientific artifacts. The review explicitly challenges
alternative implementation and measurement explanations. For Research, a
clean null, falsification, negative result, or inconclusive verdict is
approvable. Understanding is judged on faithful reconstruction, explanatory
work, and observed limits rather than a verdict.

If review finds that an already registered, unchanged rerun is required, it may
use `registered_rerun -> execute`. The review report must cite the prospective
rule that authorized that rerun before result exposure. Anything newly chosen
after inspecting results takes `amend -> protocol_amendment`; it never returns
directly to setup or brainstorm.

### `write` -> `editorial_review`

The writer receives the accepted question, protocol, run review, analysis
packet, figures, metrics, and sources. The writer follows
`notes/blog-authoring.md` rather than reconstructing the science from memory:

- the form-appropriate front matter is complete;
- a Methods or reproducibility section names the exact execution boundary and
  implementation lineage;
- experiment-produced quantitative claims use `[metric_name]{.metric}` rather
  than hand-entered values, including repetitions across sections;
- source discrepancies use the site's learning-in-public stance rather than a
  gotcha frame;
- every figure/table/code block is numbered, captioned, and referenced;
- external sources use bibliography citations, and bibliography changes are
  append-only after author-and-year de-duplication.

For Research, contribution fields and IMRaD order are complete, Results passes
the printed-output test sentence by sentence including captions, Discussion
uses **supported**, **falsified**, or **inconclusive** and states relevance and
limits, and Conclusion names the next experiment without adapting the completed
one. For Understanding, the headings follow dependency order, equations make
every plotted quantity reconstructable, generated examples remain
demonstrations rather than evidence for broader claims, and a section states
where the model stops; there is no Research verdict or IMRaD structure.

The editorial reviewer checks scientific claims against the accepted analysis,
then checks stance, provenance, form-specific structure and claims, citations,
captions, links, metrics, limitations, and the public-file allowlist. It applies
the dry-Results/verdict tests only to Research and the dependency/model-boundary
tests only to Understanding. A claim that outruns the evidence returns to
`write` or `analyze`; it is not softened until it becomes unfalsifiable.

An editorial prose/citation defect uses `revise`; an evidence-to-claim issue
that the accepted analysis can resolve uses `reanalyze`. Any change to the
experiment after result exposure uses `amend`.

### Post-result change -> `protocol_amendment` -> `amendment_review`

The brainstormer owns a post-exposure amendment as a distinct role invocation,
not as permission to rewrite the original preregistration. Its small amendment
packet names:

- the exact exposed results and invalid or incomplete lineage;
- quarantined run, analysis, metric, figure, and prose artifacts;
- the defect or required post-exposure scientific/setup change that prompted
  review;
- the old and proposed protocol versions and byte-level digests;
- every changed choice and every decision intentionally held fixed;
- confirmation-bias risk and controls after exposure; and
- why the revision still answers the registered question rather than creating
  a new workflow.

`amendment_review` approves only a fully disclosed, scientifically defensible
revision. `approve` enters `amended_setup`, where code, tests, environment, and
commands are rebuilt for the approved version, then `amended_setup_review`
must approve them before execution. That review may revise the implementation
or request another amendment, but it cannot return to prospective brainstorm.
`revise` at amendment review returns to the amendment packet. `park` preserves
the honest failed lineage without publication. A new hypothesis,
outcome-driven expansion, or changed explanatory question is never an
amendment.

### `ready_for_pr` -> `pr_review` -> `ready_to_merge`

`ready_for_pr` is a coordinator work node, not a terminal approval. The
coordinator runs the cheap worktree checks, opens or updates the PR, waits for
the full CI build and human feedback, and submits a small PR receipt naming the
PR, candidate content commit, its CI run and result, content-artifact digests,
human-review status, and changes made since editorial approval.

The independent `pr_review` checks that those content bytes passed the deploy
build, that the current pending-review commit differs from the candidate only
by the PR receipt, its evidence snapshot, and its submission event, and that PR
changes did not invalidate earlier approvals. It also states that recording the
review may add only the review receipt, its evidence snapshot, and its review
event. It may
`approve -> ready_to_merge`, `revise -> write`, `reanalyze -> analyze`,
`amend -> protocol_amendment`, or `park`. `ready_to_merge` is the successful
terminal recommendation, not a self-certifying commit: the human integrator
waits for CI on the resulting head and confirms that the cumulative delta from
the candidate commit is limited to those PR/review receipts, evidence snapshots,
and ledger events. Human merge, automatic deploy, journal close, and repository
close-out still occur outside the graph.

## Avoiding confirmation bias

The graph enforces several controls that a single long session tends to blur:

1. For Research, freeze the hypothesis, falsifier, thresholds, decision
   branches, exclusions, stopping rule, and publish-the-other-outcome
   commitment before production. For Understanding, freeze the explanatory
   route, generated demonstrations, and model boundary.
2. Keep feasibility pilots in a named, excluded namespace. Use fresh registered
   seeds or inputs for confirmation where the design permits it.
3. Review question and setup artifacts before production results exist. No role
   approves its own work; reviewers start with fresh context.
4. Make advancement depend on validity and completeness, never on a desired
   Research verdict or a tidier Understanding demonstration.
5. Make the operator execute a sealed command. Health monitoring may trigger a
   same-run `resume` or a prospectively authorized fresh `registered_retry`, not
   outcome-dependent tuning.
6. Keep raw outputs immutable and checksummed. A `registered_retry`, a
   prospective `registered_rerun`, and an approved amended protocol receive new
   run identifiers and preserve the earlier lineage.
7. Generate form-appropriate outcomes, figures, and publication metrics from
   canonical artifacts with deterministic code; do not type preferred values
   into prose.
8. Label every post-hoc diagnostic and prevent it from changing a Research
   verdict or Understanding boundary. Turn a new hypothesis into a new shelf
   entry.
9. Require reviewers to state evidence, blocking severity, and the correct
   upstream route rather than editing the artifact themselves.
10. Record sources, pivots, exact results, and next actions in the research
    journal as they occur, including unhelpful and negative results.
11. After any result exposure, route scientific changes through an explicit
    amendment and independent amendment review. Do not use a generic backward
    edge to make a post-hoc choice look prospective.

## Safe execution fan-out

Only `execute` normally fans out. It may do so after setup approval when the
protocol defines independent cases, seeds, folds, geometries, or parameter
points.

Each worker receives the same approved code and environment digests plus one
immutable shard specification. It writes to a disjoint
`runs/<run-id>/<shard-id>/` namespace and cannot update a shared summary,
manifest, protocol, or source file. Worker completion order must not affect
canonical ordering. A coordinator or deterministic join command assembles the
manifest only after all workers finish, and `run_review` admits, quarantines, or
rejects shards under rules frozen in setup.

Do not fan out writing against changing analysis, let multiple agents append to
one run file, or let a worker decide to replace a failed case. Parallelism is a
compute property of the registered design, not permission for concurrent
scientific choices.

## Workflow CLI

`scripts/research-workflow.mjs` records and verifies handoffs. It does not run
the experiment, generate the analysis, write the post, or substitute for the
research journal.

Workflow submissions are small receipts under
`research/<experiment-slug>/workflow/`, not raw outputs or full logs. Start
stage packets from `research/_TEMPLATE/workflow/HANDOFF.example.md`, review
packets from `workflow/REVIEW.example.md`, post-exposure changes from
`workflow/AMENDMENT.example.md`, and PR evidence from
`workflow/PULL_REQUEST_RECEIPT.example.md`. Use a new versioned filename after
every backward transition rather than editing already snapshotted evidence. A
receipt references large artifacts by repository-relative path or durable
external URI, size, and checksum.

Keep submitted source receipts present and byte-identical while they belong to
the active accepted lineage or pending review. `status` reports an active source
that changed or disappeared as stale, and `verify`, `submit`, and `review` block
until it is restored or a valid reviewed backward route permits a new version.
Evidence snapshots never make an active source receipt disposable.

The append-only `workflow.jsonl`, receipts, and `workflow/evidence/` snapshots
are a tracked public ledger even when the site does not serve them. They must
not contain credentials, private transcripts, raw secret values, or local
absolute paths such as a checkout, home, scratch, cache, or mounted-data path.
Use repository-relative paths for tracked material and durable public/archive
identifiers for external material. Local absolute paths may appear in the
clone-private research journal when necessary for crash recovery, never in the
public workflow ledger.

The CLI keeps its own event paths repository-relative, but it does not inspect
free-form receipt or `--note` prose for private data or absolute path strings.
The producer and coordinator must check that content before submission.

Inspect the graph before starting:

```sh
node scripts/research-workflow.mjs graph
node scripts/research-workflow.mjs graph --format mermaid
node scripts/research-workflow.mjs graph --format json
```

Each workflow event pins both a graph version and its byte digest. Once a
workflow uses `research/workflow.graph.v1.json`, that file is immutable; a
future graph change must be a new versioned file, never an in-place v1 edit.

Initialize one workflow after creating the post worktree and selecting a ready
shelf question:

```sh
node scripts/research-workflow.mjs init \
  --experiment <experiment-slug> \
  --post-type research \
  --question "<falsifiable question>" \
  --journal <research-session-id> \
  --actor <coordinator-id> \
  --shelf-entry "<ready notes/questions.md heading>"
```

Use `--post-type understanding` with its explanatory question and omit
`--shelf-entry` for an Understanding note. Initialization binds the ledger to
the current `post/<slug>` branch. The CLI permits initialization, transitions,
and repair only from a linked non-primary worktree, and later mutations must
remain on that exact owning branch.

Inspect the current node, pending submission, accepted lineage, stale status,
and next allowed actions. JSON status additionally exposes the event count,
superseded lineage, routed reviews, stale sources, and recovery warnings:

```sh
node scripts/research-workflow.mjs status --experiment <experiment-slug>
node scripts/research-workflow.mjs status --experiment <experiment-slug> --json
```

The coordinator submits one or more small versioned receipts for the current
activity node. The replayed graph state determines that node; callers cannot
skip ahead by naming another one. Although the coordinator invokes the command,
`--actor` is a self-asserted label for the role session that produced the
submitted artifact. The handoff inventories and binds the stage's underlying
contract artifacts:

```sh
node scripts/research-workflow.mjs submit \
  --experiment <experiment-slug> \
  --actor <experiment-engineer-id> \
  --artifact research/<experiment-slug>/workflow/setup-v1.md \
  --note "Implementation packet ready for independent review"
```

Immediately before every `submit` or `review`, append a journal checkpoint
with an explicit next action and leave it as the open journal's final event.
The workflow records that checkpoint's event ID and rejects reuse. Optional
workflow notes are limited to 10,000 characters; put larger details in the
versioned handoff artifact.

After an independent reviewer returns findings, the coordinator saves or
references the report and records its decision, attributing `--actor` to that
reviewer session. Reviewers themselves remain read-only and do not run this
state-changing command. The CLI rejects an equal review/submission actor-ID
string, but it cannot authenticate either actor or prove independence; the
coordinator enforces a genuinely separate reviewer session or person:

```sh
node scripts/research-workflow.mjs review \
  --experiment <experiment-slug> \
  --actor <independent-reviewer-id> \
  --decision approve \
  --artifact research/<experiment-slug>/workflow/setup-review-v1.md \
  --note "Independent setup review returned no blockers"
```

Use only a decision allowed by the current review node. The review report names
the evidence and upstream route; inspect `status` before resubmitting.

Verify the complete event sequence, immutable evidence snapshots, artifact
digests, approvals, and current replayed state at any handoff and before opening
the PR:

```sh
node scripts/research-workflow.mjs verify --experiment <experiment-slug>
node scripts/research-workflow.mjs verify --all
```

`verify --experiment` validates one opted-in experiment. `verify --all`
discovers and validates only experiment directories that contain a tracked
`workflow.jsonl`; experiments that never opted into this graph are intentionally
outside that command's scope.

Verification checks graph replay, event and snapshot integrity, and active
receipt freshness. It does not authenticate actor IDs, evaluate scientific or
editorial findings, scan free-form text for private/local paths, or require the
workflow to be terminal. The coordinator and human integrator still enforce
those contracts and require `ready_to_merge` before merge.

If a command reports an incomplete final workflow record or unreferenced
snapshots left by an interrupted transition, use the explicit recovery command:

```sh
node scripts/research-workflow.mjs repair --experiment <experiment-slug>
```

It truncates only an incomplete final record and records/quarantines orphaned
snapshots. It does not repair middle-record corruption or active receipt drift;
never hand-edit `workflow.jsonl` or `workflow/evidence/`.

A process killed during the short transition critical section can leave
`workflow/.transition.lock`. Inspect the reported lock first. Only when its
same-host owner process is gone, run:

```sh
node scripts/research-workflow.mjs repair \
  --experiment <experiment-slug> \
  --unlock-stale
```

The CLI inode-checks the exact lock and refuses removal when the owner is live,
the host or owning post branch differs, the metadata is malformed, or the path
changes during inspection. If initialization died after taking the lock but
before installing `workflow.jsonl`, the same command clears the verified lock
before ledger loading and tells the coordinator to retry `init`. Do not remove
a lock by hand or use this option to interrupt a live transition.

Use the CLI's shared `--help` usage screen as the source of truth for accepted
flags. Do not edit workflow state by hand.

## Worktree, journal, PR, and close-out lifecycle

1. Read `notes/blog-authoring.md` and declare the form. Select a ready shelf
   question for Research or write the bounded explanatory question and route
   for Understanding. Create a `post/<slug>` worktree from `origin/main` before
   drafting.
2. Run `git worktree list` and `git branch -vv`; every foreign worktree and
   branch is presumed live. Stay within the post branch's allowed paths.
3. Start `scripts/research-log.mjs` before the first literature search,
   exploratory probe, or protocol command. Supply that journal identifier to
   workflow initialization.
4. Checkpoint immediately after each interpretable result and before another
   expensive command, delegation, context compaction, or branch/worktree
   change. The workflow ledger records approvals; the research journal records
   why choices and pivots occurred. Neither replaces the other.
5. Commit durable handoff artifacts on the post branch as appropriate so a new
   session can reproduce the accepted lineage. Never commit credentials,
   private data, or an unreviewed public bundle.
6. At `ready_for_pr`, run the cheap checks, open or update the PR into `main`,
   wait for the full build and human feedback, and submit the versioned PR
   receipt. Do not merge from this state.
7. An independent `pr_review` verifies the candidate content commit and CI
   evidence and routes any invalidating change backward. Recording approval
   creates the final attestation-only descendant. Merge only after the graph
   reaches `ready_to_merge`, the cumulative delta from the candidate is limited
   to the PR/review receipts, their evidence snapshots, and corresponding ledger
   events, and CI is green on the resulting head. A push to `main` deploys the
   live site.
8. For Research, record the Conclusion's next question on a separate shelf
   branch. Close the research journal, account for every branch, remove finished
   worktrees, prune, and leave the primary checkout clean on updated `main` with
   no stashes.

The graph's terminal states are `ready_to_merge` and `parked`. Neither closes a
session by itself: the repository close-out checklist in `notes/worktrees.md`
must still pass.
