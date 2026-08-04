# Agent inbox corpus census

This experiment accompanies "Counting the inbox: what an agent message corpus
records about roles nobody designed." It takes a filename-level census of a
private corpus of coordination messages written by Claude Code sessions to each
other, and projects the resulting aggregate tables into the typed metrics the
post quotes.

## Question and boundary

- Post type: Understanding
- Question: What does the message history of a hand-run team of Claude Code
  sessions actually contain, and what can counting and quoting it establish
  about how the roles formed?
- Mechanism exposed: every message filename in the corpus is parsed for its
  date, time, self-assigned sender label and optional recipient, and each
  file's size is recorded; the resulting per-label, per-day and per-token
  aggregates are the analysis inputs, and the projection turns them into
  message counts, label lifespans, weekly volumes and filename-vocabulary
  counts.
- What this can establish: that the committed aggregate tables regenerate every
  count quoted by the post and every bar coordinate drawn in its first two
  figures.
- What it cannot establish: that the filename census reflects the work — sender
  labels are self-assigned and unvalidated, message counts are not token counts
  and not cost, and one label may denote the same seat as another (the corpus
  contains `portcullis` and `porticulis`, which are one seat and are counted
  here as two labels).
- Traceability: traceable
- Highest reproduction level: analysis-reproducible
- Archived-evidence or rerun constraints: the input corpus is private working
  correspondence from a real business and is not published, so the step from
  message files to the committed aggregate tables cannot be rerun by a reader.

## Inputs

The four CSV tables in this directory are the analysis inputs of record. They
contain no message text, no filenames, no recipients, and nothing about the
business the messages discuss.

- `corpus-totals.csv` — whole-corpus counts: message files, total bytes,
  messages with a parsable date and with a parsable sender, distinct sender
  labels, distinct inbox directories, filenames encoding an explicit recipient,
  and filenames carrying an all-capitals status token.
- `senders.csv` — one row per sender label: first and last dated message,
  message count, total bytes.
- `daily.csv` — one row per calendar day carrying at least one message:
  message count and total bytes.
- `filename-tokens.csv` — one row per status token counted in the filename
  vocabulary, with the number of filenames carrying it. Case variants are
  counted separately here; the post's table merges them and says so.
- `joiner-window.csv` — the clock times bounding the `joiner` label's
  messages, transcribed from the withheld corpus so the derived career length
  rests on a fingerprinted input rather than a constant in code.

## Procedure

1. An indexing pass over the private corpus walks the message tree, parses
   `YYYY-MM-DD_HHMM_from_<sender>[_to_<recipient>]` out of each filename, reads
   each file's size, and writes the four tables above. The corpus is not
   committed, so this step is not reproducible from this repository.
2. `generate-metrics.mjs` reads the five tables and projects them into
   `metrics.json`, merging status-token case variants the way the post's
   Table 1 documents. Calendar weeks start on Monday. The four surviving role
   names are declared as constants in the generator and are stated in the
   post.
3. `generate-metrics.mjs --check` recomputes the projection from the committed
   tables and compares it to the committed `metrics.json`, failing on any
   difference. It writes nothing.
4. `make-figures.py` emits the TikZ bodies for the post's first two figures
   from the same tables, so a drawn bar and a quoted metric cannot disagree.
5. `check_figure_tokens.py` compares the token counts drawn into Figure 4's
   transition labels with `filename-tokens.csv` under the same case-variant
   merge, failing when the committed drawing and the committed table disagree.

The `generated_at` stamp in `metrics.json` is fixed rather than taken from the
wall clock, so a regeneration is byte-identical to the committed file.
