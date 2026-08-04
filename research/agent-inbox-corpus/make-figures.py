#!/usr/bin/env python3
"""Scratch generator: emit TikZ bodies for the inbox-archaeology post from the
committed aggregate CSVs so the drawn figures cannot drift from the metrics."""
import csv, datetime, pathlib, collections

here = pathlib.Path(__file__).resolve().parent
senders = list(csv.DictReader(open(here / "senders.csv")))
daily = list(csv.DictReader(open(here / "daily.csv")))

d = lambda s: datetime.date.fromisoformat(s)
D0 = d(min(r["first_date"] for r in senders))
D1 = d(max(r["last_date"] for r in senders))
SPAN = (D1 - D0).days

SURV = {"sightline", "bosun", "shipwright", "drawbridge"}
NOTE = {"gh-gate", "lookout", "quartermaster", "trim", "joiner", "shakedown",
        "portcullis", "porticulis", "scout", "keelson", "purser"}

rows = sorted(senders, key=lambda r: (r["first_date"], r["last_date"], r["sender"]))

W = 12.4          # cm of drawing width for the full span
ROW = 0.235       # cm per row
X = lambda dt: (d(dt) - D0).days / SPAN * W

out = []
out.append(r"""\begin{tikzpicture}[
  font=\small,
  x=1cm, y=1cm,
  lbl/.style={font=\fontsize{4.4}{5}\selectfont, anchor=east, inner sep=0pt},
  surv/.style={draw=blue!55!black, fill=blue!45!white, line width=0.15pt},
  dead/.style={draw=black!45, fill=black!22, line width=0.15pt},
  axis/.style={black!55, line width=0.35pt},
  tick/.style={font=\fontsize{5.2}{6}\selectfont, anchor=north, text=black!70},
  note/.style={font=\fontsize{4.4}{5}\selectfont, anchor=west, text=black!60, inner sep=1pt},
]""")

n = len(rows)
for i, r in enumerate(rows):
    y = -i * ROW
    x0, x1 = X(r["first_date"]), X(r["last_date"])
    if x1 - x0 < 0.06:
        x1 = x0 + 0.06
    style = "surv" if r["sender"] in SURV else "dead"
    out.append(f"  \\fill[{style}] ({x0:.3f},{y-0.075:.3f}) rectangle ({x1:.3f},{y+0.075:.3f});")
    weight = r"\bfseries " if r["sender"] in SURV else ""
    out.append(f"  \\node[lbl] at (-0.12,{y:.3f}) {{{weight}\\texttt{{{r['sender']}}}}};")
    if r["sender"] in SURV or r["sender"] in NOTE:
        out.append(f"  \\node[note] at ({x1+0.08:.3f},{y:.3f}) {{{r['messages']}}};")

base = -(n - 1) * ROW - 0.28
out.append(f"  \\draw[axis] (0,{base:.3f}) -- ({W:.3f},{base:.3f});")
for month, day, label in [(5, 2, "2 May"), (5, 16, "16 May"), (6, 1, "1 Jun"),
                          (6, 15, "15 Jun"), (7, 1, "1 Jul"), (7, 15, "15 Jul"), (7, 28, "28 Jul")]:
    xt = X(f"2026-{month:02d}-{day:02d}")
    out.append(f"  \\draw[axis] ({xt:.3f},{base:.3f}) -- ({xt:.3f},{base-0.09:.3f});")
    out.append(f"  \\node[tick] at ({xt:.3f},{base-0.12:.3f}) {{{label}}};")
out.append(r"\end{tikzpicture}")
fig1 = "\n".join(out)

# ---- Figure 2: weekly volume -------------------------------------------------
weeks = collections.OrderedDict()
for r in daily:
    dt = d(r["date"])
    monday = dt - datetime.timedelta(days=dt.weekday())
    w = weeks.setdefault(monday, [0, 0])
    w[0] += int(r["messages"])
    w[1] += int(r["bytes"])
keys = sorted(weeks)
coords_msg = " ".join(f"({i},{weeks[k][0]})" for i, k in enumerate(keys))
coords_kb = " ".join(f"({i},{weeks[k][1]/1000:.1f})" for i, k in enumerate(keys))
ticks = ",".join(str(i) for i in range(len(keys)))
labels = ",".join(k.strftime("%-d %b") for k in keys)

fig2 = rf"""\begin{{tikzpicture}}[font=\small]
  \begin{{axis}}[
    width=13cm, height=6.2cm,
    ybar, bar width=6.5pt,
    ymin=0, ymax=420,
    xmin=-0.7, xmax={len(keys)-0.3},
    axis lines=left,
    xtick={{{ticks}}},
    xticklabels={{{labels}}},
    xticklabel style={{font=\fontsize{{5.6}}{{7}}\selectfont, rotate=45, anchor=east}},
    yticklabel style={{font=\fontsize{{6}}{{7}}\selectfont}},
    ylabel={{messages per week}},
    ylabel style={{font=\fontsize{{6.6}}{{8}}\selectfont}},
    xlabel={{week beginning}},
    xlabel style={{font=\fontsize{{6.6}}{{8}}\selectfont}},
    ymajorgrids, grid style={{black!12, line width=0.3pt}},
    axis line style={{black!55, line width=0.35pt}},
    tick style={{black!55}},
    clip=false,
  ]
    \addplot[draw=blue!55!black, fill=blue!35!white, line width=0.2pt] coordinates {{{coords_msg}}};
  \end{{axis}}
\end{{tikzpicture}}"""

print("%%% FIGURE 1 %%%")
print(fig1)
print()
print("%%% FIGURE 2 %%%")
print(fig2)
print()
print("%% weekly series:", [(k.isoformat(), weeks[k][0]) for k in keys])
