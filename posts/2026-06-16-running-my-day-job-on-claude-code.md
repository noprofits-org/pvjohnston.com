---
title: Running my day job on Claude Code — an agent architecture for non-software work
date: 2026-06-16
author: Peter Johnston
tags: claude code, agents, automation, project management, workflow, llm, architecture
description: My day job isn't writing software — it's coordinating insurance-restoration jobs, which is document-heavy and relentlessly repetitive. Over a few months I built a system of Claude Code agents around that workflow. This is the architecture, the decisions that made it hold together, and what I'd change.
---

Most of what I write here is about code or chemistry. This one is about my actual
day job, which is neither: I coordinate insurance-restoration construction jobs.
The work is document-heavy and relentlessly repetitive — every job runs the same
kickoff sequence, produces the same kinds of letters, and tracks the same state
through the same stages, only with different names and numbers each time. It is
exactly the shape of work that begs to be automated, and over a few months I built
a system of [Claude Code](https://claude.com/claude-code) agents around it.

I am not a software developer by trade, so the interesting part isn't the code —
it's the *architecture*. A pile of clever prompts will get you a demo. What makes
the difference between a demo and something you trust with real jobs is a handful
of boring structural decisions: where state lives, how it gets written, how the
work is split across agents, and where the human stays in the loop. This post is
those decisions.

## The problem shape

Strip the domain away and the workload is generic knowledge work:

- **A repeating pipeline.** Each new job triggers the same sequence — read the
  incoming documents, figure out what's in scope, generate a set of customer- and
  vendor-facing letters, build a schedule, and track the whole thing to completion.
- **Documents in, documents out.** The inputs are PDFs and spreadsheets; the
  outputs are more PDFs, letters, and spreadsheets. A lot of the "work" is
  extraction, classification, and templated generation.
- **State that has to stay correct.** Each job has a status, a set of dates,
  open questions, vendor assignments, and a history of what happened. Getting this
  wrong — or letting two copies of it drift apart — is worse than not tracking it
  at all.
- **Rules that don't bend.** The domain has hard conventions. Certain numbers are
  always computed one way; certain documents always go to multiple vendors, never
  one; when something is ambiguous, the right move is to *flag it*, never to guess.

That last point is the whole game. Automating knowledge work is not like automating
code, where a test either passes or it doesn't. Here, a confident wrong answer
costs real money and a phone call to apologize for it. So the system is built less
to be clever and more to be *correctable* — and to refuse to guess.

## The architecture

Here's the shape I landed on. Every figure on this blog is compiled from TikZ at
build time, so the diagram below is the actual source, not a screenshot:

```tikzpicture
\begin{tikzpicture}[
  font=\small,
  >={Stealth[length=2.4mm]},
  box/.style={draw, rounded corners=2pt, align=center, minimum height=11mm, thick},
  sess/.style={box, fill=black!7, draw=black!55, minimum width=24mm},
  agent/.style={box, fill=blue!8, draw=blue!55!black, minimum width=27mm},
  gate/.style={box, fill=orange!13, draw=orange!72!black, minimum width=24mm},
  store/.style={box, fill=green!10, draw=green!55!black, minimum width=28mm},
  flow/.style={->, thick, black!75},
  art/.style={->, thick, green!55!black},
  plan/.style={->, thick, blue!55!black, dashed},
  lbl/.style={font=\scriptsize, align=center},
]
  \node[sess]  (sess) at (0,0)      {Claude Code\\session\\[-1pt]{\scriptsize (orchestrator)}};
  \node[agent] (plan) at (4.7,2.0)  {Planner agent\\[-1pt]{\scriptsize returns a plan}};
  \node[agent] (exec) at (4.7,-2.0) {Executor agents\\[-1pt]{\scriptsize scope \(\cdot\) letters}\\[-1pt]{\scriptsize audit \(\cdot\) logging}};
  \node[gate]  (cli)  at (10.0,-0.7){Single CLI\\[-1pt]{\scriptsize validate + txn}};
  \node[store] (db)   at (14.8,-0.7){Job database\\[-1pt]{\scriptsize state \(\cdot\) events \(\cdot\) dates}};
  \node[store] (fs)   at (10.0,-3.6){File storage\\[-1pt]{\scriptsize PDF \(\cdot\) DOCX \(\cdot\) XLSX}};

  % plan loop
  \draw[flow] (sess) to[bend left=12]  node[lbl,above]{1.\,launch} (plan);
  \draw[plan] (plan) to[bend left=12]  node[lbl,below]{plan} (sess);
  % execute
  \draw[flow] (sess) to[bend right=12] node[lbl,below,pos=0.55]{2.\,execute} (exec);
  % write discipline
  \draw[flow] (exec) -- node[lbl,above,pos=0.55]{state} (cli);
  \draw[flow] (cli)  -- node[lbl,above]{one write path} (db);
  % artifacts
  \draw[art]  (exec) -- node[lbl,below,pos=0.55]{artifacts} (fs);
\end{tikzpicture}
```

Four decisions are doing all the work here. I'll take them in order.

### 1. One source of truth, and it isn't the files

The first version of this stored each job's state in a JSON file next to its
documents. This is the obvious thing to do and it was a mistake. The folder is
where *artifacts* live — the generated PDFs, the spreadsheets, the letters. State
is a different animal: it changes constantly, it's read from several places, and
two readers must never disagree about it. A file on disk that several agents and a
web UI all poke at is a drift machine.

So state moved into a database, and the on-disk JSON files were frozen and
demoted to read-only history. The rule became blunt: **the database is the only
authority for state; the folder only holds artifacts.** A document in the folder is
evidence that something happened; the database is what *did* happen. When the two
ever seem to disagree, the database wins and the folder is stale.

This split — state in the DB, artifacts in the file store — is the two green boxes
in the diagram, and it's the single most important decision in the whole system.
Everything else is in service of keeping that one source of truth honest.

### 2. Every write goes through one narrow gate

If the database is the source of truth, the next question is who's allowed to write
to it. The tempting answer is "any agent, directly." That's the second mistake I
got to skip.

Instead, **every state mutation goes through a single command-line tool.** No agent
writes the database directly — not the logger, not the planner, not the letter
generators. They all shell out to one CLI that wraps the same validation logic and
the same atomic transaction the web UI uses. That's the orange gate in the diagram,
and the payoff is large for how simple it is:

- **The schema is enforced in exactly one place.** Validation lives in the CLI, not
  scattered across a dozen prompts hoping each agent remembers the rules.
- **A CLI write is byte-identical to a UI write.** Same validators, same
  transaction. The agents and the humans can't produce two different kinds of
  "correct."
- **Writes are atomic.** State change and the event that records it land together
  or not at all. No half-written job.
- **The blast radius is tiny.** When a rule changes, I change the CLI. Every agent
  inherits it for free because none of them implemented it in the first place.

I think of this as *write-discipline*. The agents are smart and chatty and
occasionally wrong; the gate is dumb and strict and always the same. Putting the
strictness where the intelligence isn't is the whole trick.

### 3. Planners plan, executors execute — and they're separate agents

Claude Code's harness has a constraint that shaped the design more than I expected:
a subagent can't spawn another subagent. You'd hit this the moment you wanted a
"kickoff" agent that itself fans out to a scope agent, a letter agent, and a
schedule agent.

The clean way around it is to split planning from execution. A **planner** agent
reads the job folder and returns a *structured plan* — a list of steps, each naming
which executor to run and with what inputs. It doesn't do any of the work itself.
The top-level session (the orchestrator) takes that plan, shows it to me, and then
launches each **executor** agent in turn. That's the dashed `plan` arrow returning
to the session, followed by the `execute` arrow going back out.

The split turned out to be good design independent of the harness constraint:

- **The plan is reviewable before anything happens.** I see the whole sequence —
  every letter that's about to be generated, every vendor about to be contacted —
  and can veto or amend it before a single document is written.
- **Executors stay narrow.** Each one does a single job well: extract the scope,
  generate one kind of letter, audit readiness, log an event. Narrow agents are
  easier to get right, easier to test by hand, and reusable across pipelines.
- **Overrides have a natural home.** "Use this vendor, skip that letter" is just an
  input to the planner; it adjusts the plan, and the executors never need to know.

There's a related distinction between two kinds of executor: heavyweight
multi-step work (read three documents, cross-check them, generate a formatted
letter) runs as a dispatched **subagent**, while lightweight in-conversation tasks
(draft the email that accompanies a letter) run as **skills** right in the session.
I started with everything as subagents and gradually pulled the small,
conversational tasks back inline. A subagent has overhead and a cold context; for
"write three friendly paragraphs from this letter," that overhead isn't worth it.

### 4. The domain rules live in one place, and the default is "flag, don't guess"

The hard conventions of the domain — the always-computed-this-way numbers, the
this-document-goes-to-many-not-one rules, the never-skip-this-cross-check rules —
don't belong in any single agent. They're written once in a project instruction
file that every agent inherits. When a convention changes, it changes there, and
the whole fleet updates at once. This is the same "one place" instinct as the
write-discipline gate, applied to knowledge instead of code.

The most valuable rule of all is the cheapest to state: **when in doubt, flag it
for review rather than guessing.** Every agent is told this, and it's reinforced by
small structural choices — operations are idempotent where possible (re-running a
step doesn't silently create a duplicate; you have to explicitly opt into the same
identity to update in place), and agents are told never to construct a path or a
record from a name alone but to search first and *stop* if there's more than one
match. A system that confidently does the wrong thing is worse than one that stops
and asks. Mine is tuned, on purpose, to stop and ask.

## The plumbing: Drive, templates, and credentials

The four decisions above are the design. But there's a practical layer underneath
them — how the system actually reaches the documents and data in the first place —
that's worth spelling out, because it's where a lot of "can an LLM agent really do
my job?" skepticism quietly dissolves.

**It runs where the files already live.** Claude Code operates on a local
filesystem, and the trick is that the "local" filesystem is the Google Drive
desktop app's synced mount. The job folders the rest of the team sees in Drive are,
on my machine, just directories. The agents read and write them directly — no
upload step, no download step, no API call to fetch a document. An agent edits a
letter locally and the change syncs up to the cloud; a teammate drops a new PDF in
the folder and it syncs down to where the next agent will find it. Treating Drive
as an ordinary directory means the whole system gets cloud collaboration for free,
without a single line of integration code.

**Documents are cloned from templates, not written from scratch.** The letters
aren't generated character by character every time — that's how you get formatting
that drifts and the occasional mangled header. Instead each document type has a
template: a real `.docx` with the standard layout, headings, and boilerplate
already correct. The generator agent clones the template and fills in the
specifics, editing the file programmatically — `python-docx` for Word documents,
`openpyxl` for spreadsheets. Clone-and-edit beats generate-from-nothing on every
axis that matters here: the formatting is right because it was always right, only
the data changes, and two letters generated a month apart look identical. (The
agents are even told *which* library to use for each format, so they don't reach for
a worse one.)

**ADC bridges the data that isn't a file.** Not all the state lives on disk. Some
of it sits in a Google Sheet or a cloud database — and Claude Code can't open a
Google Sheet the way it opens a local file, because a Sheet isn't on the
filesystem at all; it's behind Google's APIs. The bridge is gcloud **Application
Default Credentials (ADC)**. I authenticate once at the command line
(`gcloud auth application-default login`), and from then on the small scripts the
agents shell out to can reach the Sheets and database APIs *as me*. So when an
agent needs data that lives in a spreadsheet, it doesn't fail trying to read a file
that isn't there — it runs a script that pulls the data through the API. This is
also exactly how the single-CLI write path from earlier reaches the cloud database:
the gate is a script, and ADC is what lets that script speak to the cloud with my
credentials. The same mechanism that lets the agents *read* a Sheet is what lets
the write-gate *commit* to the database.

Put together, this layer is what makes the whole thing feel less like a chatbot and
more like a coworker who happens to be very fast: it works in the same folders, it
produces documents that look like the ones we already use, and it can reach the
cloud data behind a login the same way I can.

## Where the human stays in the loop

The thread running through all four decisions is that the automation is built to be
*supervised*, not autonomous. The seams where it pauses for me are deliberate:

- **The plan, before execution.** Nothing fans out until I've seen the planner's
  list and approved it.
- **Readiness, before commitment.** A dedicated audit agent checks that every
  prerequisite for a job is actually met and renders a GO / NO-GO — but it pauses to
  ask me about open items rather than ruling on them blind.
- **Substance, before saving.** When an agent edits a document, it classifies the
  change: a cosmetic tweak saves in place silently, but a *substantive* change
  presents a plan and waits for my confirmation first.

None of these are technical limitations I'm working around. They're the points
where a human's judgment is cheap to add and expensive to omit.

## What worked, and what I'd change

**What worked.** The single source of truth and the single write path are the two
decisions I'd make again without hesitating. Together they killed an entire class
of bug — the "which copy of the truth is right?" bug — before it could start. The
planner/executor split aged well past the harness constraint that forced it. And
encoding the domain rules in one inherited instruction file means the system gets
*more* consistent as it grows, not less.

**What I'd change.** I leaned too hard on subagents early; a lot of what I dispatched
as a full subagent is really an in-conversation skill, and I'm still migrating those
back. I also under-invested at first in making operations idempotent, which meant a
re-run could leave a duplicate behind — cheap to prevent up front, annoying to clean
up after. And the boundary between "stable" job facts and "volatile" job state took
me a couple of rewrites to draw in the right place; getting that line right early
would have saved a schema migration or two.

The meta-lesson is the one I keep relearning: with LLM agents, the intelligence is
the easy part to add and the easy part to over-trust. The durable wins come from the
unglamorous scaffolding around it — one source of truth, one write path, a clean
split between planning and doing, and a system that would rather stop and ask than
guess. The agents are the cleverest part of this setup and the least important.
