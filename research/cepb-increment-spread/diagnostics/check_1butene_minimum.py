#!/usr/bin/env python3
"""Post-hoc diagnostic, outside the frozen protocol and recorded as such.

The committed 1-butene structures optimized to the planar anti conformation
(C1=C2-C3-C4 dihedral 180 degrees), which is the symmetry of the committed
starting structure; a gradient-following optimizer cannot leave a symmetric
stationary point. This script computes harmonic frequencies at frozen-core
DF-MP2/cc-pVDZ on the committed cc-pVDZ geometry to determine whether that
stationary point is a minimum. It changes nothing in the registered analysis
or verdicts; its result is reported in the post's Discussion as a post-hoc
diagnostic.
"""

import json
from pathlib import Path

import psi4

HERE = Path(__file__).resolve().parent
GEOM = HERE.parent / "runs" / "1-butene" / "cc-pVDZ" / "optimized.xyz"
OUT = HERE / "1butene-dz-frequencies.json"

lines = GEOM.read_text().strip().splitlines()
atoms = [ln for ln in lines if len(ln.split()) == 4]
geometry = "\n".join(atoms) + "\nunits angstrom\n"

psi4.set_memory("9 GB")
psi4.set_num_threads(7)
psi4.core.set_output_file(str(HERE / "1butene-dz-frequencies.out"), False)
psi4.geometry(geometry)
psi4.set_options(
    {
        "freeze_core": "true",
        "scf_type": "df",
        "mp2_type": "df",
        "basis": "cc-pVDZ",
        "e_convergence": 1e-9,
        "d_convergence": 1e-9,
    }
)

energy, wfn = psi4.frequencies("mp2", return_wfn=True)
freqs = [float(f) for f in wfn.frequencies().to_array()]
record = {
    "diagnostic": "post-hoc harmonic frequencies on the committed 1-butene structure",
    "level": "frozen-core DF-MP2/cc-pVDZ, findif of gradients",
    "geometry": str(GEOM.relative_to(HERE.parent)),
    "frequencies_cm1": freqs,
    "imaginary_mode_count": sum(1 for f in freqs if f < 0.0),
    "lowest_frequency_cm1": min(freqs),
    "psi4_version": psi4.__version__,
}
OUT.write_text(json.dumps(record, indent=2) + "\n")
print(json.dumps(record, indent=2))
