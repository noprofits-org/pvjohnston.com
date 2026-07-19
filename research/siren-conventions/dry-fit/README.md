# SIREN initialization accuracy dry fit

This directory preserves an abandoned exploratory run that led to the focused
Adam parameterization experiment. It is research history, **not publication
evidence**, and its summaries should not be used to compare the three SIREN
schemes.

The frozen dataset contains 324 full-batch Adam trainings: three initialization
schemes, three high-fidelity sample sizes, four repetitions, and nine learning
rates. `siren-init-accuracy.py` generated `siren_accuracy_raw.json`, and
`siren-init-accuracy-analyse.py` prints exploratory reductions of those records.
Run the reduction from this directory because both scripts use paths relative
to their current working directory:

```sh
cd research/siren-conventions/dry-fit
python3 siren-init-accuracy-analyse.py
```

Three design choices confound the apparent accuracy differences:

- Regularization was fixed at zero even though the source study searches its
  penalties jointly with the learning rate.
- Each scheme used a scheme-specific initialization seed, so comparisons do
  not start from paired, functionally matched parameter draws.
- Some summaries select the learning rate directly by test error. That oracle
  selection is optimistic and is a diagnostic, not a valid evaluation
  protocol.

The later Adam experiment replaced this design with matched initial functions
and tested the parameterization mechanism directly. These files remain only so
the provenance of that exploratory lead is not lost.
