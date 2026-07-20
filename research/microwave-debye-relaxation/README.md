# Microwave Debye-relaxation demonstration

This experiment accompanies “Why a microwave oven is not tuned to water.” It
evaluates the single-relaxation-time Debye model for liquid water and ice using
only the Python and Node.js standard libraries, then projects the values quoted
by the post into typed publication metrics.

## Question and boundary

- Post type: Understanding
- Question: How does Debye relaxation turn an oscillating electric field into
  heat, and what does this model predict for absorption and penetration depth
  at microwave frequencies?
- Mechanism exposed: the complex Debye permittivity is evaluated at declared
  frequencies; its loss component supplies a loss tangent, attenuation
  coefficient, and 1/e power penetration depth.
- What this can establish: that the committed parameters and standard-library
  calculation regenerate the canonical values and every projected model input
  or result quoted by the post.
- What it cannot establish: that the selected textbook parameters describe a
  particular food, that a single Debye time captures all real water or ice
  losses, or that traceability proves the model and interpretation correct.
- Traceability: traceable
- Highest reproduction level: end-to-end reproducible in the documented
  environment
- Archived-evidence or rerun constraints: none

The material parameters are representative selected inputs, not measurements
made for the article. The ice relaxation frequency at −10 °C is 2.80 kHz from
[Bittelli, Flury, and Roth (2004)](https://doi.org/10.1029/2003WR002343); the
calculation derives $\tau=1/(2\pi f_r)$. The ice permittivities 97 and 3.2 are
approximate, separately sourced representative inputs and are not attributed
to that paper. Their full literature provenance remains in the post's normal
bibliography. There is no downloaded dataset, so this experiment needs no
external-source manifest.

## Model

For angular frequency $\omega=2\pi f$, the calculation uses

$$
\hat\varepsilon(\omega)=\varepsilon_\infty+
\frac{\varepsilon_s-\varepsilon_\infty}{1-i\omega\tau}.
$$

The convention is fields proportional to $e^{-i\omega t}$, so passive loss is
$\hat\varepsilon=\varepsilon'+i\varepsilon''$ with
$\varepsilon''=\operatorname{Im}\hat\varepsilon>0$. The calculation then
evaluates

$$
\tan\delta=\frac{\varepsilon''}{\varepsilon'},\qquad
\alpha=\frac{\omega}{c}\operatorname{Im}\sqrt{\varepsilon'+i\varepsilon''},
\qquad D_p=\frac{1}{2\alpha}.
$$

$D_p$ is the 1/e transmitted-power depth. The liquid-water dielectric-loss-
factor $\varepsilon''$ peak is calculated from
$f_{\varepsilon''\!,\rm peak}=1/(2\pi\tau)$ rather than declared as an input.
That point is not an absorption-coefficient or attenuation maximum: the
calculation's 60 GHz single-Debye extrapolation, for example, has a shorter
penetration depth even though $\varepsilon''$ is below its peak value.

## Reproduce

```sh
python3 research/microwave-debye-relaxation/calculate.py
python3 research/microwave-debye-relaxation/calculate.py --check
node research/microwave-debye-relaxation/generate-metrics.mjs
node research/microwave-debye-relaxation/generate-metrics.mjs --check
node scripts/verify-metrics.mjs
```

`calculate.py` writes the canonical `results.json` with native floating-point
values. It evaluates liquid water at 915 MHz, 2.45 GHz, the computed
dielectric-loss-factor peak, and 60 GHz, and compares liquid water with ice at
2.45 GHz. It also records the photon-versus-$k_BT$ and water-versus-ice
timescale comparisons used in the article.

The internal checks confirm the analytic $\omega\tau=1$ condition for the
dielectric-loss-factor peak, its identity
$\varepsilon''=(\varepsilon_s-\varepsilon_\infty)/2$, exact agreement between
two independently evaluated water rows at 2.45 GHz, and finite positive loss
and attenuation quantities. These checks are consistency tests, not empirical
validation.

During normal verification, `generate-metrics.mjs --check` first reruns the
cheap calculation in check mode and then proves that `metrics.json` is its
exact current projection. A fresh write stamps `generated_at` from the wall
clock; check mode preserves the committed timestamp for deterministic byte
comparison.

## Data and publication

`inputs.json` is the complete computational input. The Planck, elementary
charge, and Boltzmann constants use their exact SI defining values. The speed
of light remains the rounded $2.998\times10^8$ m/s value used by the original
article calculation. Liquid water's $\varepsilon_\infty=5.2$ is an effective
background for this one-pole fit, not the true infinite-frequency or optical
limit. The 60 GHz result is explicitly an extrapolation of that single-Debye
model, not a claim that it includes every measured water-loss channel.

`PUBLIC_FILES.txt` lists the reviewed reader-facing bundle. No files are
excluded for privacy, rights, size, secrets, unavailable services, or special
hardware. The repository-root `LICENSE` covers the code; no duplicate license
file is required in this directory.
