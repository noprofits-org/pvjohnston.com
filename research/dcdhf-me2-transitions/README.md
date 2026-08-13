# How many transitions hide under one absorption band: DCDHF-Me2

The merged post *From blinking to absorption* treats a dye as a two-level
system and says so twice — §2 ("Within the two-level model there is no state
above $|e\rangle$") and §8 ("the two-level approximation itself hides the
higher excited states"). This experiment pays off that promissory note by
computing the actual singlet manifold of a real push-pull dye and showing how
much of the absorption the two-level picture leaves out.

DCDHF-Me2 is the chromophore from the 2025 computational-tools posts, which is
why it is the example here: the geometry survives in `posts/ai-comp-tools-SI.md`
even though the original calculation scripts do not.

## Question and boundary

- Post type: understanding
- Question: How many distinct electronic transitions lie under what a
  spectrometer reports as a single absorption band, for a real donor–acceptor
  dye?
- Research falsifier (Research only): n/a
- Demonstration mechanism or observation (Understanding only): TD-DFT vertical
  excitation manifold of DCDHF-Me2 — every computed singlet with its
  oscillator strength and orbital character, rather than only the bright
  lowest transition. The demonstration succeeds if more than one transition
  carries non-negligible oscillator strength in the region a spectrometer
  would read as one band.
- What this experiment can establish:
  - That the computed manifold places several states, not one, in and around
    the main absorption band at this level of theory.
  - The relative positions, oscillator strengths, and dominant orbital
    character of those states, including which are charge-transfer in
    character (hole–particle centroid separation).
  - How far a UFF force-field starting structure sits from the DFT minimum for
    a conjugated push-pull dye, measured as the inter-ring twist angle.
- What it cannot establish:
  - Absolute agreement with a measured spectrum. These are gas-phase vertical
    excitations with no solvent model; a real DCDHF-Me2 spectrum is recorded
    in solution, and charge-transfer states are solvatochromic.
  - Anything about **band width**. No vibronic (Franck–Condon) or
    inhomogeneous broadening is computed. The Gaussian applied in the figure is
    cosmetic, matching the convention of `calcs/uvvis-pushpull` and the 2025
    DCDHF figure, and is labelled as such everywhere it appears.
  - Which of these transitions are experimentally *resolvable*. The claim is
    about the computed manifold, not about what a spectrometer can separate.
  - Excited-state ordering to better than the ~0.2–0.3 eV typical error of
    TD-DFT for charge-transfer states, which is why CAM-B3LYP and B3LYP are
    both reported.
- Traceability: traceable
- Highest reproduction level: end-to-end reproducible
- Archived-evidence or rerun constraints: Psi4 1.9.1 under the recorded conda
  environment. The full pipeline is a few CPU-hours on 8 cores; the
  optimization and each TD-DFT leg are separate commands so a memory failure in
  one does not cost the others.

### Pre-committed analysis choices

Recorded here before the canonical run, because they are the choices that
could otherwise be tuned after seeing results:

1. **CAM-B3LYP is the primary functional.** Range-separated functionals are the
   a priori correct choice for charge-transfer excitations in a push-pull dye;
   B3LYP is known to underestimate CT energies. B3LYP is reported alongside as
   a sensitivity check, not as an alternative headline.
2. **A state counts as bright at f ≥ 0.01**, the same threshold used by
   `calcs/uvvis-pushpull/run_one.py`.
3. **The "band" is defined as ±0.35 eV around the lowest bright state**, the
   same width as the cosmetic broadening, chosen to match the published
   push-pull convention rather than to maximise the state count.
4. A state is labelled **CT only if** its hole–particle centroid separation is
   ≥ 2.0 Å *and* it is bright; dark states are never assigned n→π* character
   automatically, since that needs orbital-symmetry inspection.

### A bug the contrast molecule caught

Worth recording because the failure mode generalizes. `state_gaps()` originally
selected the second-brightest state with a strict `energy > lowest`, which
silently skips a state at *exactly* the same energy. That was invisible for
DCDHF-Me2, which has no degeneracies. When benzene arrived it paired S3 with
S8 and reported that one transition carries 98% of the strength — the precise
inverse of the 50/50 split that is benzene's entire reason for being in this
experiment.

The general shape: **code written while only the non-degenerate case existed
encoded an assumption that the case added to exhibit degeneracy then broke.**
A contrast case is not only evidence about the science; it is a test of the
analysis written before it. Any comparison that picks "the next" item by
strict inequality deserves this scrutiny.

## Run

```sh
research/dcdhf-me2-transitions/run_all.sh
```

That script runs the three stages in series, which is deliberate: the box this
was developed on has 15 GB of RAM and 8 cores, and running the TD-DFT legs
concurrently will exhaust memory. The stages are also separately invocable:

```sh
python run_tddft.py optimize --basis def2-svp --functional b3lyp --threads 6 --memory "6 GB"
python run_tddft.py excite  --basis def2-tzvp --functional cam-b3lyp --threads 6 --memory "6 GB" \
    --geometry geometry/dcdhf-me2-def2-svp-opt.xyz
python postprocess.py
```

If the def2-TZVP TD-DFT leg exhausts memory, the documented fallback ladder is,
in order: `--basis def2-svp`, then `--tda`, then `--states 8`. Any fallback used
must be recorded in `results/` — every `states_*.json` file records its own
basis, method, and environment, so a fallback run is self-describing.

Note that Psi4 1.9.1 caps the TD-DFT eigensolver at 60 iterations and provides
no way to raise it: neither the `maxiter` keyword argument nor the
`TDSCF_MAXITER` global option has any effect, though `r_convergence` does work.
Each results file records `tdscf_requested` alongside `tdscf_effective`, the
latter parsed from the solver's own printed header, so the two are visibly
different rather than silently conflated. See `environment.md`.

## Generate publication metrics

```sh
node research/dcdhf-me2-transitions/generate-metrics.mjs
node research/dcdhf-me2-transitions/generate-metrics.mjs --check
node scripts/verify-metrics.mjs
```

## Data and publication

The only external input is the DCDHF-Me2 starting geometry, recovered from this
repository's own published SI post rather than from an upstream data source;
`sources.json` records that provenance and the literature structure it was built
from. No external datasets, credentials, or private data are involved.

`PUBLIC_FILES.txt` lists the reviewed files routed onto the live site. Psi4
output logs and scratch are **neither committed nor published** (see
`.gitignore`): they are large, regenerable, and they embed absolute scratch
paths from the machine that produced them. The canonical evidence is
`results/` — the per-state JSON records energies, oscillator strengths,
orbital character, the convergence thresholds the solver actually used, and
the environment, which is everything a reader needs to check the numbers or
re-run the work.
