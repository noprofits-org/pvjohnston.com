#!/usr/bin/env python
"""Build summary.csv, spectra.png, results.md from results/<label>.json."""
import os, json, csv, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
EV2CM = 8065.543937
EV2NM = 1239.841984
ORDER = ["benzene", "aniline", "nitrobenzene", "pNA"]
FUNCS = ["b3lyp", "cam-b3lyp"]
FUNC_LBL = {"b3lyp": "B3LYP", "cam-b3lyp": "CAM-B3LYP"}
COLORS = {"benzene": "#4C4C4C", "aniline": "#1f77b4",
          "nitrobenzene": "#ff7f0e", "pNA": "#d62728"}
FWHM_EV = 0.35                                  # stated broadening
SIGMA_CM = (FWHM_EV * EV2CM) / (2 * math.sqrt(math.log(2)))   # Gaussian width

# lowest-bright experimental references (literature; gas-phase/solution as noted)
EXPT = {   # eV, nm, note
    "benzene":      (6.94, 179, "E1u pi->pi*, gas (weak 1B2u band at 254 nm/4.9 eV)"),
    "aniline":      (4.40, 282, "1La/1Lb pi->pi*, vapor band max ~280-294 nm"),
    "nitrobenzene": (4.90, 253, "pi->pi*, soln; weak n->pi* ~340 nm/3.6 eV"),
    "pNA":          (4.24, 292, "CT, gas-phase vertical; redshifts to ~3.3 eV/380 nm in water"),
}


def load():
    data = {}
    for lbl in ORDER:
        p = os.path.join(HERE, "results", f"{lbl}.json")
        if os.path.exists(p):
            data[lbl] = json.load(open(p))
    return data


def eps(nm_grid, states):
    """ORCA/Gaussian oscillator-strength -> molar absorptivity broadening."""
    nu = 1e7 / nm_grid                                   # cm^-1
    out = np.zeros_like(nu)
    for s in states:
        nu_i = s["energy_eV"] * EV2CM
        out += 1.3063e8 * (s["f"] / SIGMA_CM) * np.exp(-((nu - nu_i) / SIGMA_CM) ** 2)
    return out


def write_csv(data):
    with open(os.path.join(HERE, "summary.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["molecule", "functional", "state", "energy_eV", "wavelength_nm",
                    "f", "hole_particle_dist_ang", "type", "dominant_transition",
                    "dominant_weight_pct"])
        for lbl in ORDER:
            if lbl not in data:
                continue
            for func in FUNCS:
                fd = data[lbl]["functionals"].get(func)
                if not fd:
                    continue
                for s in fd["states"]:
                    dom = s["dominant"][0] if s["dominant"] else {}
                    trans = f"{dom.get('from','')}->{dom.get('to','')}" if dom else ""
                    w.writerow([lbl, FUNC_LBL[func], s["state"], s["energy_eV"],
                                s["wavelength_nm"], s["f"], s["hole_particle_dist_ang"],
                                s["type"], trans, dom.get("weight_pct", "")])
    print("wrote summary.csv")


def write_curve(data):
    """Wide table of broadened eps(lambda) for pgfplots \\addplot table[x=nm,y=<col>].
    Also writes the stick list (nm,f) per molecule/functional for TikZ verticals."""
    grid = np.linspace(200, 500, 601)            # 0.5 nm steps
    cols = {"nm": grid}
    for lbl in ORDER:
        if lbl not in data:
            continue
        for func in FUNCS:
            fd = data[lbl]["functionals"].get(func)
            if not fd:
                continue
            cols[f"{lbl}_{func.replace('-', '')}"] = eps(grid, fd["states"])
    names = list(cols.keys())
    with open(os.path.join(HERE, "spectra_curve.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(names)
        for i in range(len(grid)):
            w.writerow(["%.4g" % cols[n][i] for n in names])
    # sticks
    with open(os.path.join(HERE, "spectra_sticks.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["molecule", "functional", "wavelength_nm", "energy_eV", "f"])
        for lbl in ORDER:
            if lbl not in data:
                continue
            for func in FUNCS:
                fd = data[lbl]["functionals"].get(func)
                if not fd:
                    continue
                for s in fd["states"]:
                    if s["f"] > 1e-4:
                        w.writerow([lbl, FUNC_LBL[func], s["wavelength_nm"],
                                    s["energy_eV"], s["f"]])
    print("wrote spectra_curve.csv + spectra_sticks.csv (TikZ/pgfplots-ready)")


def plot(data):
    grid = np.linspace(200, 500, 1200)
    fig, axes = plt.subplots(2, 1, figsize=(8, 8.5), sharex=True)
    for ax, func in zip(axes, FUNCS):
        for lbl in ORDER:
            if lbl not in data:
                continue
            fd = data[lbl]["functionals"].get(func)
            if not fd:
                continue
            y = eps(grid, fd["states"])
            ax.plot(grid, y, color=COLORS[lbl], lw=1.8,
                    label=data[lbl]["name"])
            # sticks (scaled f onto a light twin so they read as intensity)
            for s in fd["states"]:
                if 200 <= s["wavelength_nm"] <= 500 and s["f"] > 0.005:
                    ax.vlines(s["wavelength_nm"], 0, s["f"] * 1.0e4,
                              color=COLORS[lbl], lw=0.8, alpha=0.35)
        ax.set_title(f"{FUNC_LBL[func]} / def2-TZVP  (Gaussian FWHM {FWHM_EV} eV)",
                     fontsize=11)
        ax.set_ylabel(r"$\varepsilon$  (L mol$^{-1}$ cm$^{-1}$)")
        ax.legend(fontsize=9, frameon=False)
        ax.set_xlim(200, 500)
        ax.margins(y=0.02)
    axes[1].set_xlabel("wavelength (nm)")
    fig.suptitle("Donor / acceptor / push-pull UV-Vis on a fixed benzene bridge",
                 fontsize=12, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    fig.savefig(os.path.join(HERE, "spectra.png"), dpi=150)
    print("wrote spectra.png")


def md_table(data):
    rows = []
    for lbl in ORDER:
        if lbl not in data:
            continue
        for func in FUNCS:
            fd = data[lbl]["functionals"].get(func)
            if not fd or not fd["lowest_bright"]:
                rows.append((data[lbl]["name"], FUNC_LBL[func], "-", "-", "-", "-", "-"))
                continue
            b = fd["lowest_bright"]
            rows.append((data[lbl]["name"], FUNC_LBL[func],
                         f"{b['wavelength_nm']:.0f}", f"{b['energy_eV']:.2f}",
                         f"{b['f']:.3f}", f"{b['tau_rad_ns']:.1f}", b["type"]))
    out = ["| molecule | functional | λmax (nm) | E (eV) | f | τ_rad (ns) | band |",
           "|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


if __name__ == "__main__":
    data = load()
    print("loaded:", list(data.keys()))
    write_csv(data)
    write_curve(data)
    plot(data)
    # markdown table fragment (full prose written separately)
    open(os.path.join(HERE, "_table.md"), "w").write(md_table(data))
    print("wrote _table.md\n")
    print(md_table(data))
