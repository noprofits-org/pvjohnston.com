---
title: "A spreadsheet that runs payroll: a pipeline in Google Apps Script"
date: 2026-07-12
author: Peter Johnston
tags: google apps script, clasp, spreadsheets, automation, javascript, workflow
description: "Every two weeks I used to open a time-clock export and copy each employee's shifts, by hand, into a payroll workbook — an afternoon of careful, error-prone transcription. Now it's a one-minute import from a menu inside the spreadsheet itself. This post is the big-picture tour of how that works: what Google Apps Script is, bound versus standalone projects, converting an uploaded .xlsx on the fly, writing live formulas so a hand edit still cascades, and getting the code out of the browser and into local files and git with clasp."
---

Every two weeks, the same afternoon disappeared. A time-clock system spat out a
spreadsheet of everybody's shifts for the pay period, and turning that into
paychecks meant opening a payroll workbook and copying each person's rows into
their own block — name, dates, times, hours — one employee at a time. Ten, twelve,
fifteen people, each a little island of copy-paste, each an opportunity to drop a
row or fat-finger a time. Then the same arithmetic for everyone: hours, overtime,
gross pay. It was a couple of hours of work that felt like it should be zero.

It is now closer to zero. The whole thing lives inside the spreadsheet as a
**Google Apps Script** project: the person running payroll picks *Import time
clock file* from a menu, drops in the export, and about forty seconds later every
employee's hours, overtime split, and gross pay are laid out exactly the way the
old workbook looked — except nobody typed any of it. This post is the big-picture
tour of how a pipeline like that is built. I'll skip the domain-specific pay rules
(those are their own tangle) and stay on the parts that transfer to any
spreadsheet-shaped problem: what Apps Script is, the two kinds of project you can
build, how an uploaded Excel file gets turned into data, the one idea that makes
the automation *correctable* instead of brittle, and how you edit the code like a
normal repo instead of in a browser text box.

## What Google Apps Script actually is

Apps Script is JavaScript that runs on Google's servers with the Workspace apps
wired in as built-in objects. There is no `npm install`, no server to deploy, no
credentials to manage for the common case — you write a function, and inside it
`SpreadsheetApp`, `DriveApp`, and `GmailApp` are just *there*, already
authenticated as you. `SpreadsheetApp.getActive()` hands you the current
spreadsheet; `DriveApp.getFileById(id)` opens a file in your Drive; a few lines
create a Gmail draft with an attachment. The runtime is modern V8, so the language
is ordinary JavaScript, but the interesting surface area is that standard library
of Workspace bindings.

The other thing that makes it feel different from normal web programming is how
code gets *triggered*. A function named `onOpen` runs automatically every time the
document is opened, and that's your chance to build a menu:

```javascript
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Payroll')
    .addItem('Import time clock file…', 'showImportDialog')
    .addItem('Run All (Labor + Payout)', 'menuRunAll')
    .addItem('Archive period', 'archivePeriod')
    .addToUi();
}
```

That's the entire user interface for most of this project. The person running
payroll never sees code or a script editor — they see a *Payroll* menu next to
*Help*, and every capability hangs off it. Turning a script into a product that a
non-programmer can run is mostly this: a good menu and honest dialog boxes.

## Bound versus standalone

The first real decision is which of two kinds of project to make, and it's worth
understanding because it shapes everything after.

A **standalone** script is its own object in Drive, like a document. It has a URL,
it can be shared, it can run on a schedule, and it can reach out to *many*
spreadsheets by ID. A **container-bound** script has no independent existence — it
lives *inside* one specific spreadsheet (or doc, or form) and travels with it. If
you copy the spreadsheet, you copy the script; if you delete the spreadsheet, the
script goes with it.

This project is bound, on purpose. Two things fall out of that choice for free.
The first is `onOpen`: bound scripts get the automatic menu-building trigger, so
the tool installs itself the moment you open the file. The second is
`SpreadsheetApp.getActive()` — "the active spreadsheet" only *means* anything when
the script is attached to one. A bound script never has to be told which workbook
it operates on; it *is* the workbook's script. The code is littered with
`SpreadsheetApp.getActive().getSheetByName('Payout Totals')` and never once has to
look up or store the spreadsheet's ID, because there's only ever one answer.

The trade-off is reach. A bound script is the right shape for "this tool belongs to
this document." If I wanted one script orchestrating twenty separate client
workbooks, standalone — reaching each by ID — would be the move. For a payroll
workbook that a single office keeps and reuses, bound wins: it ships *with* the
thing it automates, and there's no second artifact to keep in sync.

## The general flow

Under the menu, the work is a straight pipeline. Each stage reads what the last one
produced and writes the next tab; nothing loops back.

```tikzpicture
\begin{tikzpicture}[
  font=\small,
  >={Stealth[length=2.4mm]},
  box/.style={draw, rounded corners=2pt, align=center, minimum height=11mm, thick},
  inbox/.style={box, fill=orange!13, draw=orange!72!black, minimum width=26mm},
  stepbox/.style={box, fill=blue!8, draw=blue!55!black, minimum width=26mm},
  outbox/.style={box, fill=green!10, draw=green!55!black, minimum width=26mm},
  flow/.style={->, thick, black!75},
  lbl/.style={font=\scriptsize, align=center},
]
  \node[inbox]   (up)  at (0,0)      {Upload\\[-1pt]{\scriptsize .xls/.xlsx/.csv}};
  \node[stepbox] (imp) at (3.6,0)    {Import tab\\[-1pt]{\scriptsize raw grid}};
  \node[stepbox] (lab) at (7.4,0)    {Labor Hours\\[-1pt]{\scriptsize hours + OT}};
  \node[stepbox] (pay) at (11.2,0)   {Payout\\[-1pt]{\scriptsize gross pay}};
  \node[outbox]  (exp) at (11.2,-2.4){Exports\\[-1pt]{\scriptsize files \(\cdot\) drafts \(\cdot\) CSV}};
  \draw[flow] (up)  -- (imp);
  \draw[flow] (imp) -- (lab);
  \draw[flow] (lab) -- (pay);
  \draw[flow] (pay) -- (exp);
\end{tikzpicture}
```

The *Import* tab is just the raw export, dropped in as-is. *Labor Hours* is the
computed heart: one block per employee, their shifts, and the regular/overtime
summary. *Payout* rolls each person up to a single row of gross pay. From there the
exports fan out — a per-worker file, an email draft, a CSV for the payroll
provider. Keeping it a one-directional pipeline is what makes it comprehensible:
to understand any tab, you only have to understand the one before it.

## Turning an uploaded Excel file into data

The upload is the part that looks like magic and is actually a nice trick. The
payroll clerk has an `.xlsx` on their computer. Apps Script runs on a server and
can't reach the local filesystem. So how does the file get in?

A small HTML dialog does the client half. Apps Script can serve an HTML page as a
modal, and inside that page ordinary browser JavaScript reads the chosen file with
a `FileReader`, encodes it as base64, and ships the string to the server:

```javascript
const reader = new FileReader();
reader.onload = function () {
  const b64 = reader.result.split(',')[1];      // strip the "data:" prefix
  google.script.run
    .withSuccessHandler(onDone)
    .withFailureHandler(onErr)
    .processTimeClockUpload({ name: file.name, mimeType: file.type, b64: b64 });
};
reader.readAsDataURL(file);
```

`google.script.run` is the bridge: it calls a server-side Apps Script function by
name, asynchronously, and hands the result to a callback. On the server,
`processTimeClockUpload` decodes the bytes — and now it has to read an Excel file,
which Apps Script has no native parser for.

The move is to let Google do it. Drive can *convert* an uploaded `.xls`/`.xlsx`
into a native Google Sheet, and a Google Sheet is something Apps Script reads
fluently. So the server drops the bytes into a temporary Drive file with the
"convert" flag, opens the result as a spreadsheet, reads the grid out of it, and
trashes the temp file:

```javascript
const inserted = Drive.Files.insert(
  { title: '(tmp) ' + name, mimeType: MimeType.GOOGLE_SHEETS },
  blob,
  { convert: true });                 // let Drive parse the Excel for us
const grid = SpreadsheetApp.openById(inserted.id)
  .getSheetByName('All Shifts').getDataRange().getValues();
```

Two details make this robust rather than merely clever. First, the code finds the
header row *by name* — it scans the first several rows for the cells that say
`Time In` and `Time Out` — so the exact column order in the export doesn't matter,
and a future change to the report's layout doesn't silently corrupt the import. (It
even handles the vendor splitting a single `Name` column into `First Name` /
`Last Name` between two versions of the export.) Second, it *validates before it
writes*: the grid is parsed and checked while it's still just a variable in memory,
and only a grid that actually looks like a time-clock report is allowed to
overwrite the Import tab. Upload the wrong file and you get an error message, not a
half-clobbered sheet.

That's the whole minute: decode, convert, read, validate, compute, render.

## Live formulas: the automation seeds, the human still edits

Here is the idea I'd most want a reader to take away, because it's the difference
between an automation people trust and one they route around.

The naive version of this tool would compute every number in JavaScript and write
the *values* into the sheet. Hours: 82.5. Pay: \$2,145. Done. And it would be
fragile in a specific, maddening way: the moment a human needs to correct one
figure — a mistyped clock time, a wage that changed mid-period — they'd change the
cell, and *nothing downstream would move*. The overtime split wouldn't recompute,
the gross pay wouldn't update, the rollup on the next tab would still show the old
number. The person would either give up and do the math by hand, or worse, trust a
total that no longer matched its parts.

So the automation doesn't write final numbers. It writes **live formulas**, exactly
the way a person building the sheet by hand would, and leaves the spreadsheet's own
recalculation engine to do the arithmetic. When the script renders an employee's
block, the net-hours cell isn't a number — it's a formula referring to that row's
own time-in, time-out, and break cells. The pay cell is `=H12*I12` (hours times
rate). And the rollup on the *Payout* tab doesn't copy the pay over; it holds a
cross-sheet reference straight back to the source:

```javascript
// On Payout Totals, the "Regular Labor" cell points at the live PAY cell
// over on the Labor Hours tab — not a copied value.
regularCell.setFormula("='Labor Hour Totals'!J" + laborRow);
```

The consequence is that a hand edit *cascades*. Correct a clock time and the row's
net hours recompute, which shifts the weekly overtime split, which changes the pay
cell, which — because Payout only *references* that cell — updates the gross pay and
the grand total, all without re-running the script. The automation's job is to lay
down the inputs and wire the formulas; the recalculation is the spreadsheet's job,
and the human keeps working in the tool they already know, with corrections that
actually propagate.

The same instinct shows up in the per-project rollups, which are built as `SUMIF`
formulas over the labor rows rather than sums computed in code:

```javascript
cell.setFormula("=SUMIF('Labor Hour Totals'!C:C, A" + row +
                ", 'Labor Hour Totals'!I:I)");
```

Written this way, the rollup can never disagree with the sheet it summarizes,
because it *is* the sheet, added up live. This is the spreadsheet analogue of a
lesson I keep relearning with automation generally: keep one source of truth, and
make everything else *reference* it rather than *copy* it. The subtle part — and the
one genuinely hard problem in a system like this — is that there are now two
representations of every number: the JavaScript model that generated the sheet, and
the live formulas the sheet recalculates. Keeping those two honest with each other,
especially once a human starts hand-editing cells the model can't see, is where all
the real care goes. But that's a post of its own.

## Working on it locally: clasp

Apps Script has a perfectly good in-browser editor, and for a ten-line script
that's fine. For seventeen files that I want under version control, it isn't. The
bridge is **clasp** — Google's command-line tool for Apps Script (the name is
"Command Line Apps Script Projects").

The basics are about as heavy as `git`, and no heavier. You authenticate once with
`clasp login`. In an existing project you run `clasp clone <scriptId>` to pull the
files down to your machine, or `clasp pull` to refresh them; you edit in your normal
editor, commit to git like anything else, and `clasp push` sends the files back up
to the Apps Script project. A small `.clasp.json` ties the local folder to the
remote project:

```json
{
  "scriptId": "17yv…HcULg",
  "rootDir": "",
  "filePushOrder": ["Config.js", "Helpers.js"]
}
```

The `scriptId` is the only line that matters at first — it's which cloud project
these files belong to. `filePushOrder` is a nicety: Apps Script concatenates all
your files into one global scope, so listing the files that define shared constants
first keeps things tidy.

It's worth being clear that clasp and git are doing two unrelated jobs over the
same folder, because it's easy to blur them. Git records history and pushes to
GitHub — versions, diffs, backup — and has no idea Apps Script exists. Clasp is
just the sync line to Google's copy of the code: `clasp push` sends the local
files up, `clasp pull` brings them down, and it has no idea GitHub exists. They
coexist because they happen to operate on the same directory, not because either
depends on the other. There's no build step between the two — `clasp push`
uploads the files as-is — so once this is set up, the fact that the code runs on
Google's servers mostly stops mattering to your workflow. You write JavaScript,
commit it to git like anything else, and `clasp push` when you want the live
script to catch up; the whole project — every file quoted in this post — sits in
version control where it belongs.

## From an afternoon to a minute

The honest measure of a project like this isn't lines of code; it's the afternoon I
no longer spend. The old process was a human being carefully transcribing a
spreadsheet into another spreadsheet, fifteen times over, and then doing the same
arithmetic fifteen times — the kind of work that is both boring and unforgiving,
where the tedium is exactly what causes the mistakes. The new process is: export
the report, pick a menu item, drop the file, wait about forty seconds, and spend
the rest of the time *reviewing* numbers instead of typing them.

None of the pieces are exotic. Apps Script gives you JavaScript with the Workspace
apps built in and an `onOpen` menu to hang a UI on. Binding the script to the
workbook means it ships with the thing it automates. Drive's convert-on-upload turns
an Excel file into readable data without a parser. Live formulas and cross-sheet
references mean the automation cooperates with human corrections instead of fighting
them. And clasp lets the whole thing live in git like any other code. Put together,
they turn a recurring afternoon into a recurring minute — which, over a year of
pay periods, is most of a work week handed back.

The most satisfying part isn't the speed, though. It's that the output looks
*exactly* like the workbook the office was already using, down to the yellow name
cells and the column widths — so the tool didn't ask anyone to change how they
work. It just quietly stopped making them do the typing.
