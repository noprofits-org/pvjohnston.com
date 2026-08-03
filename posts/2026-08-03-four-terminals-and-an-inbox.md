---
title: "Four terminals and an inbox: growing agent skills from their own message history"
date: 2026-08-03
author: Peter Johnston
tags: claude code, agents, skills, workflow, orchestration, llm, architecture
description: I ran an app-development workflow as four separate Claude Code sessions — each owning one role, all talking through a shared inbox — and then pointed a fresh session at the accumulated messages and asked it to write the skills. This is how the bootstrap worked, why the distillation step is the interesting part, and what it cost.
post-type: understanding
question: How does a hand-run team of Claude Code sessions, passing messages through a shared inbox, become a set of skills that a single orchestrator session can drive?
---

This note answers one question: how does a workflow that starts as *four
separate Claude Code sessions in four terminals*, talking to each other through
a shared inbox, end up as *one session* that quietly knows when to scope, when
to provision, when to implement, and when to review? The route is in two
phases. First I ran the multi-session version by hand — expensively, and
without much of a plan — until the roles had settled and the inbox held a real
history of the agents doing their jobs. Then I pointed a fresh session at that
inbox and asked it to derive the skills. The second phase is the part I think
is worth writing down; the first phase exists to make the second one possible.

I wrote previously about the architecture I use for my day job — planners,
executors, and a single write path — in [an earlier
note](/posts/2026-06-16-running-my-day-job-on-claude-code.html). This one is
about software work, and about a different question: not *how should agents be
structured*, but *where should the structure come from*.

None of this was designed up front. It grew over a stretch of real use, and
several of the choices I describe below as if they were decisions were really
just the thing that survived. Where a piece didn't survive, I say so.

## The workflow, before any of this

Strip away the agents and the underlying workflow is the ordinary shape of
adding a feature to an app:

1. **Scope.** Talk through the feature request, read the existing code, and
   write down a contract: what will change, what won't, what done looks like.
2. **Provision.** Create a worktree and a branch, and keep the branch healthy
   against the default branch while work happens.
3. **Implement.** Write the code the contract describes.
4. **Review and gate.** Read the implementation adversarially, and either send
   it back or ship it as a pull request.

A single Claude Code session can do all four of these in one conversation, and
that's how I started. The trouble is that the four jobs want different
postures. Scoping wants a long, patient conversation with me and wide reading
of the codebase. Implementation wants a narrow contract and no chit-chat.
Review wants to *distrust* the implementation, which is hard for the same
context that just wrote it — a reviewer who watched the code being written has
already absorbed its assumptions. Splitting the roles into separate sessions
with separate context windows was the blunt way to get genuinely different
postures, including genuine adversarial distance for the reviewer.

## Phase one: a terminal per role

So I opened multiple terminals, started a Claude Code session in each, and
gave every session one subset of the workflow. Two further instructions turned
out to matter more than I expected at the time:

- **Talk to the other agents through an inbox.** Each session was told to
  communicate with the others by writing and reading messages in a shared
  inbox — plain files on disk — rather than through me. I stayed in every
  loop, but the coordination itself was theirs to write down.
- **Give yourself a code name.** Each session named itself. This started as
  flavor and became load-bearing: a message signed by a stable name is a
  message that can be attributed, addressed, and — much later — clustered.

The cast that settled out, for app development:

- **Bosun** provisions the worktree and manages GitHub branch health.
- **Sightline** talks to me about new feature requests, reads the code, and
  develops the contract.
- **Shipwright** implements against Sightline's contract.
- **Drawbridge** is the adversarial reviewer and the GitHub gate — the agent
  that ultimately decides whether a branch becomes a pull request.

Not every role earned a place in that list. A few other codenamed agents came
and went along the way; they either never worked well or their jobs were
absorbed by the four that remained. I don't think the failures were random —
the roles that survived each own a *decision* (what to build, where to build
it, what to write, whether to ship), while the ones that didn't tended to own
a chore that any of the others could do in passing.

The inbox filled up with real traffic: Sightline posting contracts, Shipwright
reporting progress and asking clarifying questions, Bosun announcing branch
state, Drawbridge filing objections. The agents argued — genuinely, in
writing, over the inbox — about whether an implementation met its contract.
Drawbridge rejected branches that looked done and were not, and has caught
real problems that I would plausibly have merged. Two of my own sessions
disputing a point of implementation, in messages neither of them knew I would
later reuse, was one of the genuinely fun parts of the whole exercise — and,
I suspect, one of the most useful.

```tikzpicture
\begin{tikzpicture}[
  font=\small,
  >={Stealth[length=2.4mm]},
  box/.style={draw, rounded corners=2pt, align=center, minimum height=11mm, thick},
  agent/.style={box, fill=blue!8, draw=blue!55!black, minimum width=27mm},
  store/.style={box, fill=green!10, draw=green!55!black, minimum width=30mm},
  flow/.style={<->, thick, black!75},
  lbl/.style={font=\scriptsize, align=center},
]
  \node[store] (inbox) at (0,0)      {Shared inbox\\[-1pt]{\scriptsize message files on disk}};
  \node[agent] (sight) at (-4.9,1.9) {Sightline\\[-1pt]{\scriptsize scope \(\cdot\) contract}};
  \node[agent] (bosun) at (-4.9,-1.9){Bosun\\[-1pt]{\scriptsize worktree \(\cdot\) branch health}};
  \node[agent] (ship)  at (4.9,1.9)  {Shipwright\\[-1pt]{\scriptsize implementation}};
  \node[agent] (draw)  at (4.9,-1.9) {Drawbridge\\[-1pt]{\scriptsize review \(\cdot\) merge gate}};

  \draw[flow] (sight) -- node[lbl,above,sloped]{post \(\cdot\) read} (inbox);
  \draw[flow] (bosun) -- node[lbl,below,sloped]{post \(\cdot\) read} (inbox);
  \draw[flow] (ship)  -- node[lbl,above,sloped]{post \(\cdot\) read} (inbox);
  \draw[flow] (draw)  -- node[lbl,below,sloped]{post \(\cdot\) read} (inbox);
\end{tikzpicture}
```

**Figure 1.** The bootstrap phase. Four Claude Code sessions, each running in
its own terminal under my supervision, coordinate exclusively by posting and
reading messages in a shared on-disk inbox; no agent talks to another
directly, and every message is signed with the agent's code name.

## The inbox is a blackboard

I want to be clear about how little of phase one is new. A set of specialist
processes that never call each other directly, and instead cooperate by
reading and writing a shared data structure, is the **blackboard
architecture** — the design at the heart of the Hearsay-II speech
understanding system in the 1970s, and generalized by Barbara Hayes-Roth in
the 1980s.[@Erman1980Hearsay; @HayesRoth1985Blackboard] The inbox is a
blackboard with timestamps and signatures. The specialists are LLM sessions
instead of knowledge sources, but the coordination geometry in Figure 1 is
forty-five years old.

It is also, by now, close to product. Claude Code ships an experimental
agent-teams feature in which one session leads, teammates run as separate
sessions, and — the detail worth pausing on — each agent gets a **mailbox**, a
per-agent message file on disk, as the inter-agent communication
channel.[@ClaudeCodeAgentTeams] I hand-rolled a worse version of
a feature that was arriving anyway. I take that as convergence rather than
invention: when independent people keep reaching for message files on disk,
it's because separate context windows genuinely need an explicit, inspectable
channel, and a file is the cheapest one that a coding agent can already read
and write.

So if the multi-session phase is old news twice over, what's left? The part
that neither the blackboard literature nor the current tooling hands you:
where the *role definitions* come from.

## The distillation: the inbox as training data

The standard way to build specialist agents in Claude Code is top-down. You
write a subagent definition or a skill — a Markdown file stating the role's
instructions, tools, and boundaries — and iterate on the wording when the
agent misbehaves.[@ClaudeCodeSubagents; @ClaudeCodeSkills] I've built agents
that way, and the hard part is always the same: the first draft of the role
boundary is a guess. You are writing a job description for a job nobody has
done yet.

What the inbox gave me, almost by accident, was the alternative: **the roles
had already been done, and the doing was written down.** After a few sessions'
worth of work, the message history contained, for each code name, what that
agent was asked, what it produced, what it handed off and to whom, what
questions it needed answered before it could proceed, and where it clashed
with its neighbors. That is precisely the material a job description should be
distilled from — not a guess at the boundary, but a record of where the
boundary actually fell under load.

So the distillation step was almost anticlimactic. I opened one fresh Claude
Code session, pointed it at the inbox, and asked it to develop skills and
agents from what it found there. It read the history, recovered the four
roles, and wrote the definitions — Sightline's scoping-and-contract
procedure, Bosun's provisioning checklist, Shipwright's
implement-to-contract posture, Drawbridge's review standard and its authority
to kick work back. The code names survived into the skill names, which I
recommend for a mundane reason: months later, "run Drawbridge on this" is an
instruction I can give without looking anything up.

The analogy I keep reaching for is promotion versus org design. Writing skill
definitions top-down is drawing an org chart and hoping the jobs are real.
Distilling them from the inbox is promoting people who already demonstrably do
the job — the boundary between Sightline and Shipwright is wherever their
messages say it was, including the disputed cases, because the arguments are
in the history too. I suspect the arguments were some of the most valuable
training material: a fight over whether an implementation met its contract is
a precise record of what the contract format failed to specify.

## Phase two: one orchestrator

The end state is a single session. I tell an orchestrator what I want, and it
knows — without me restating the protocol — to bring up Sightline to scope the
feature and produce the contract, Bosun to provision the worktree, Shipwright
to implement, and Drawbridge to review. Drawbridge keeps its authority: it
either kicks the branch back to Shipwright with objections, or, if the
implementation is strong and free of major errors, ships it as a new pull
request (Figure 2).

```tikzpicture
\begin{tikzpicture}[
  font=\small,
  >={Stealth[length=2.4mm]},
  box/.style={draw, rounded corners=2pt, align=center, minimum height=11mm, thick},
  sess/.style={box, fill=black!7, draw=black!55, minimum width=26mm},
  agent/.style={box, fill=blue!8, draw=blue!55!black, minimum width=25mm},
  gate/.style={box, fill=orange!13, draw=orange!72!black, minimum width=25mm},
  store/.style={box, fill=green!10, draw=green!55!black, minimum width=24mm},
  flow/.style={->, thick, black!75},
  back/.style={->, thick, orange!72!black, dashed},
  lbl/.style={font=\scriptsize, align=center},
]
  \node[sess]  (orch)  at (0,2.6)   {Orchestrator\\[-1pt]{\scriptsize one Claude Code session}};
  \node[agent] (sight) at (-6.4,0)  {Sightline\\[-1pt]{\scriptsize contract}};
  \node[agent] (bosun) at (-2.2,0)  {Bosun\\[-1pt]{\scriptsize worktree}};
  \node[agent] (ship)  at (2.2,0)   {Shipwright\\[-1pt]{\scriptsize implement}};
  \node[gate]  (draw)  at (6.4,0)   {Drawbridge\\[-1pt]{\scriptsize review \(\cdot\) gate}};
  \node[store] (pr)    at (6.4,-2.7){Pull request};

  \draw[flow] (orch) -- node[lbl,above,sloped]{1} (sight);
  \draw[flow] (orch) -- node[lbl,left]{2} (bosun);
  \draw[flow] (orch) -- node[lbl,right]{3} (ship);
  \draw[flow] (orch) -- node[lbl,above,sloped]{4} (draw);
  \draw[back] (draw) to[bend left=18] node[lbl,below]{kick back} (ship);
  \draw[flow] (draw) -- node[lbl,right]{ship} (pr);
\end{tikzpicture}
```

**Figure 2.** The distilled phase. One orchestrator session invokes the four
roles — now skills derived from the inbox history — in their working order:
Sightline scopes and writes the contract (1), Bosun provisions the worktree
(2), Shipwright implements (3), and Drawbridge reviews (4), either kicking the
branch back to Shipwright with objections (dashed) or shipping it as a pull
request.

Figures 1 and 2 are two representations of the same workflow, and the
difference between them is where the protocol lives. In Figure 1 the protocol
exists only in the running sessions and in my head; close the terminals and it
evaporates, and a cold session has to be re-taught the whole dance. In
Figure 2 the protocol lives in the skill definitions, so a cold orchestrator
inherits it for free. That is the payoff sentence of this whole note: **the
multi-session phase was scaffolding, and the deliverable was the transcripts.**

Two honest qualifications. First, phase two loses something. Skills invoked
from one session do not have the full independence of four separate context
windows — Drawbridge-the-skill runs closer to the code's author than
Drawbridge-the-session did, and I don't yet know how much adversarial distance
survived the compression. It has still caught bad branches, so not zero; but I
haven't measured it, and "the reviewer got friendlier after the reorg" is
exactly the failure mode to watch for. Second, the orchestrator arrangement
works because the roles were stable *before* they were codified. Distilling an
inbox full of confused, overlapping agents would presumably codify the
confusion.

## What it cost

Phase one was very token-expensive, and the mechanism is easy to state: every
coordination message was written by one full session and read by others, each
carrying its own context, so the inbox traffic was effectively multiplied by
the number of agents attending to it. The agent-teams documentation makes the
same warning about its own architecture — token usage scales with the number
of active teammates, because each is a separate full
instance.[@ClaudeCodeAgentTeams] I did not record usage figures at the time,
which I regret, so "very expensive" is the most precise statement this note
can honestly make.

The cost has a shape worth noticing, though: it is a *capital* cost, not an
operating cost. The expensive multi-session phase ran for a bounded period and
produced a durable artifact — the skills. The steady state is one session
invoking skills, which is close to what the workflow would cost with no
history behind it at all. Whether the capital cost was worth it depends
entirely on how often the workflow runs afterward; for a workflow I use
continually, it has been. For a one-off task it would be absurd.

## Notes on the figures

Both diagrams are compiled from the TikZ source shown in this post's Markdown
at site build time, through the Hakyll-and-dvisvgm pipeline described in [an
earlier note](/posts/2026-06-14-rich-tikz-with-dvisvgm.html); they are
generated artifacts of the build, not screenshots, and the source in the
repository is the exact input. They are the only computer-generated artifacts
in this note. The workflow itself — the sessions, the inbox, the distillation
— ran on my own machine and is described here from memory and from its
surviving outputs, not re-executed for this post.

## Where this account stops

This is one person's account of one workflow, and its evidentiary limits are
worth stating plainly:

- **n = 1, described from memory.** The inbox transcripts live on another
  machine and are not quoted or published here; nothing in this note lets a
  reader check my characterization of what the agents wrote against what they
  wrote.
- **No measurements.** I have no token counts for the bootstrap phase, no
  count of Drawbridge's catches versus its false alarms, and no controlled
  comparison between the distilled skills and either the original
  four-session arrangement or top-down skill definitions written from
  scratch. "The distilled orchestrator works well" is a user's impression,
  not a result.
- **Untested generality.** The claim that message history makes better role
  boundaries than up-front design is exactly the kind of thing that ought to
  be testable — same workflow, skills authored both ways, judged blind — and I
  have not tested it. It is a hypothesis this note surfaces, not one it
  settles.
- **The substrate is moving.** The hand-rolled inbox already has a
  first-class analogue in an experimental Claude Code
  feature,[@ClaudeCodeAgentTeams] and the practice described here may be
  obsolete, or absorbed, within months.

If you've tried something similar — especially if you've distilled agent
definitions from transcripts and been burned by it, or if this pattern already
has a name and a literature I've missed — I'd genuinely like to hear about it.
"New to us" is the only novelty claim on offer here.

## References
