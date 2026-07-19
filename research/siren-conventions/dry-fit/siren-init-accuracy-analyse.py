"""Explore the abandoned SIREN accuracy dry fit; no tables were published."""
import json
import numpy as np
from collections import defaultdict

rows = json.load(open("siren_accuracy_raw.json"))
SCHEMES = ("described", "official", "specified")
NHS = (8, 16, 32)
LRS = sorted({r["lr"] for r in rows})
REPS = sorted({r["rep"] for r in rows})
print(f"{len(rows)} runs | {len(LRS)} lrs {LRS[0]:.1e}..{LRS[-1]:.1e} | reps {REPS}")

D = {(r["n_h"], r["scheme"], r["rep"], round(r["lr"], 12)): r for r in rows}


def geo(v):
    v = np.asarray(v, float)
    return float(np.exp(np.mean(np.log(np.maximum(v, 1e-30)))))


def cov(v):
    v = np.asarray(v, float)
    return float(np.std(v) / np.mean(v)) if np.mean(v) > 0 else float("nan")


# ---- Table: fixed lr = 1e-3 (the pilot's setting; top of the paper's range)
print("\n=== fixed lr = 1e-3 : mean normalized test MSE (CoV) ===")
print(f"{'N_H':>4} " + "".join(f"{s:>26}" for s in SCHEMES))
for n_h in NHS:
    cells = []
    for s in SCHEMES:
        v = [D[(n_h, s, r, round(1e-3, 12))]["test"] for r in REPS]
        cells.append(f"{np.mean(v):>14.3e} ({cov(v):.2f})")
    print(f"{n_h:>4} " + "".join(f"{c:>26}" for c in cells))

# ---- Table: lr selected per (scheme, n_h, rep) by TRAINING loss
print("\n=== lr selected per config by training loss : mean normalized test MSE (CoV) ===")
sel_train = defaultdict(list)
for n_h in NHS:
    for s in SCHEMES:
        for r in REPS:
            cand = [D[(n_h, s, r, round(lr, 12))] for lr in LRS]
            best = min(cand, key=lambda z: z["train"])
            sel_train[(n_h, s)].append(best)
print(f"{'N_H':>4} " + "".join(f"{s:>26}" for s in SCHEMES))
for n_h in NHS:
    cells = []
    for s in SCHEMES:
        v = [b["test"] for b in sel_train[(n_h, s)]]
        cells.append(f"{np.mean(v):>14.3e} ({cov(v):.2f})")
    print(f"{n_h:>4} " + "".join(f"{c:>26}" for c in cells))

# ---- Diagnostic only: TEST-loss selection is an optimistic oracle, not valid model selection
print("\n=== lr selected per config by test loss (oracle) : mean normalized test MSE (CoV) ===")
sel_or = defaultdict(list)
for n_h in NHS:
    for s in SCHEMES:
        for r in REPS:
            cand = [D[(n_h, s, r, round(lr, 12))] for lr in LRS]
            sel_or[(n_h, s)].append(min(cand, key=lambda z: z["test"]))
print(f"{'N_H':>4} " + "".join(f"{s:>26}" for s in SCHEMES))
for n_h in NHS:
    cells = []
    for s in SCHEMES:
        v = [b["test"] for b in sel_or[(n_h, s)]]
        cells.append(f"{np.mean(v):>14.3e} ({cov(v):.2f})")
    print(f"{n_h:>4} " + "".join(f"{c:>26}" for c in cells))

# ---- which lr wins, per scheme
print("\n=== oracle-selected lr, by scheme (all N_H, all reps) ===")
for s in SCHEMES:
    got = [b["lr"] for n_h in NHS for b in sel_or[(n_h, s)]]
    print(f"{s:<11} geometric mean lr = {geo(got):.3e}   "
          f"min={min(got):.1e} max={max(got):.1e}")

# ---- ratio, oracle-selected
print("\n=== oracle-selected: ratio of scheme mean to 'specified' mean ===")
for n_h in NHS:
    base = np.mean([b["test"] for b in sel_or[(n_h, "specified")]])
    out = " ".join(f"{s}={np.mean([b['test'] for b in sel_or[(n_h,s)]])/base:8.2f}x"
                   for s in SCHEMES)
    print(f"N_H={n_h:>3}  {out}")

# ---- paired comparison across reps, oracle-selected
print("\n=== paired per-rep comparison (oracle lr): specified vs each intact scheme ===")
for s in ("described", "official"):
    wins = tot = 0
    for n_h in NHS:
        for i, r in enumerate(REPS):
            a = sel_or[(n_h, "specified")][i]["test"]
            b = sel_or[(n_h, s)][i]["test"]
            wins += a < b
            tot += 1
    print(f"specified beats {s:<10}: {wins}/{tot} paired (n_h, rep) cells")

# ---- post-training hidden pre-activation scale (did the sines escape?)
print("\n=== hidden layer-1 pre-activation std AFTER training (oracle-selected lr) ===")
for s in SCHEMES:
    v = [b["zstd"] for n_h in NHS for b in sel_or[(n_h, s)]]
    print(f"{s:<11} median={np.median(v):.4f}  min={np.min(v):.4f}  max={np.max(v):.4f}")

# ---- train fit quality, to separate underfit from overfit
print("\n=== oracle-selected: mean normalized TRAIN MSE (fit quality on the samples) ===")
print(f"{'N_H':>4} " + "".join(f"{s:>18}" for s in SCHEMES))
for n_h in NHS:
    print(f"{n_h:>4} " + "".join(
        f"{np.mean([b['train'] for b in sel_or[(n_h,s)]]):>18.2e}" for s in SCHEMES))
