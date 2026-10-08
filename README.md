# From information tasks to exclusivity and Bell bounds

Read the [final manuscript](information_tasks_bell_bounds.pdf). This research manuscript is
published on [Zenodo](https://doi.org/10.5281/zenodo.23245295), released with its calculations and supporting material.

## Release and verification

The bundled LaTeX reproduces the published manuscript's text, equations,
figures, and all 18 pages. The final source was recovered from the author's
revision bundle and includes the published reference-title correction.
The published PDF is preserved byte for byte.

On October 8, 2026, a fresh three-pass build produced `paper.pdf` with identical
position-sorted text and page rendering on all 18 pages at 144 dpi. The build
reproduces the published v2 citation formatting in reference [13] using a
checked, one-line Latin Modern font step after LaTeX compilation.
See the [source reproduction record](verification/source-reproduction.json)
and [build log](verification/source-build.log) for the exact comparison and diagnostics.

On October 4, 2026, `bash build.sh` passed in a fresh validation copy using
Python 3.12.3 and pdfTeX 1.40.25 (TeX Live 2023/Debian). 1,276 exact finite checks passed.
The final LaTeX pass had no unresolved references, warnings, or overfull or
underfull boxes. There are no Lean sources or Lake projects in this bundle.
These checks concern the supplied source and finite examples; they do not
verify every argument in the final PDF.

See the [October 4 validation record](verification/release.json) and
[execution log](verification/build.log) for the earlier source bundle.
The existing `results/` records also belong to that earlier build;
running the build script regenerates its current outputs.

Samuel Mausberg, Independent Researcher. Manuscript prepared in the *Quantum* article format.

## Results and scope

The manuscript proves three conditional results without assuming quantum state-space geometry in the task theorems. Operational frequency homogeneity H and compositional calibration coverage C give calibrated weight neutrality and consistent exclusivity. Completing the aligned and crossed parity discriminators with residual records gives

    B^2 <= 8 + 4 (epsilon_0 + epsilon_1) + 288 kappa.

T2 supplies four aligned parity sectors. With a spectator of information capacity n, failure of full aligned coverage supplies at least 4n+1 mutually distinguishable attributes on the composite. A matching capacity upper bound and a reversible setting-interchange task imply parity-domain coverage P and the sharp CHSH bound.

Section 5.3 relates this certificate to no-hypersignaling. The latter constrains signaling dimension, not only the number of jointly readable labels. A corollary states the extra requirements precisely: local signaling dimensions 2 and n, preparation access for the discrimination frames including a proposed residual, and no-hypersignaling on the relevant composite. A missing domain then supplies a (4n+1)-label communication game that defeats every 4n-symbol simulator when the total preparation-and-readout error is below 1/(4n+1).

The capacity upper bound and reversible setting interchange are not derived from T2. H, C, the finite-record rules, factorization, and the hypotheses of the no-hypersignaling corollary are stated assumptions. This is not a complete superquantum countermodel. The remaining implication is described in the discussion.

## Build

From this directory, run:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
bash build.sh
```

The build requires pdfLaTeX and the standard AMS, graphics, microtype, natbib,
TikZ, pgfplots, and caption packages. The unmodified `quantumarticle.cls`
version 6.1 is included with its license notice. No font files are included;
the installed TeX distribution must provide `lmroman10-regular.otf` (Latin Modern).
The verified final-source build used TeX Live 2023/Debian, Python 3.12.3,
and SymPy 1.14.0.

The script runs both exact certificate programs and makes three LaTeX passes.
It then uses the pinned PyMuPDF dependency to reproduce the font and spacing of
the already-correct reference [13] line. This step locates Latin Modern with
`kpsewhich`, checks its font hash and the unique line location, and checks that
the text and every pixel outside that line remain unchanged. It does not read
the published PDF.
It stops on a failed check, compilation error, warning, overfull box, or missing
character. Underfull-line notices are retained in the log. `paper.pdf` is the
output. The actual page count, abstract length, certificate count, and
diagnostic counts are written to `results/build.json`.

## Files

`main.tex` contains the published main text and its native TikZ/pgfplots figures.
`appendices.tex` contains the published appendices, including the qutrit
sector example, closure and calibration proofs, and the published hypersignaling
witness. `references.tex` supplies the numbered bibliography without BibTeX.

`figures/` retains diagrams from the earlier source bundle; the final manuscript
does not load those files. `scripts/check_certificates.py` retains the earlier
finite checks. `scripts/verify_certificates.py`, recovered with the final source,
also checks its qutrit sector and the revised finite examples. Both programs use
integer enumeration, rational arithmetic, and symbolic algebra, without
floating-point acceptance tests.

The retained 1,276 finite checks cover the earlier finite examples. The final-source
checker adds eight groups covering the final event construction, five-event
obstruction, residual polynomial, frequency limits, quantum projectors,
frequency domains, qutrit embedding, and hypersignaling witness. Universal task
and composition results have written proofs; these finite checks do not
formalize those proofs.

Generated files include:

- `results/certificates.json`: exact constants and check groups.
- `results/checks.json`: individual finite checks.
- `results/final_source_checks.txt`: the final-source certificate groups.
- `results/sixteen_cliques.json`: generated events and exclusivity witnesses.
- `results/hypersignaling.json`: the published seven-input channel, payoff, all 35 four-column classical optima, and the identity-game certificate.
- `results/latex_build.log` and the build reports: actual compilation and reproducibility records.

## Relation to prior work

The manuscript distinguishes its task-domain formulation from Short and Barrett's state-versus-measurement trade-off, Czekaj, Horodecki, and Tylec's Bell-measurement constraints, and Dall'Arno and collaborators' no-hypersignaling principle. Cabello is credited for the two-copy counting construction; Chiribella and Yuan for the sharp-instrument route; Fritz and collaborators for local orthogonality; Navascués and collaborators for almost-quantum correlations; and Selby and collaborators for parity-reading measurement constraints. Constructor-theoretic premises have version-specific locators.

The hypersignaling model and its payoff gap 1/42 are published results, not new constructions. The appendix proves the readable-alphabet bounds and checks that witness exactly. The model violates information principle IV and is explicitly not a countermodel to the paper's constructor premises.

`SHA256SUMS` records the delivered files. PDF timestamps and document identifiers
may differ on rebuild without changing its text or page rendering.

## License and citation

The manuscript and original research material use [CC BY 4.0](LICENSES/CC-BY-4.0.txt).
Original code uses [MIT](LICENSES/MIT.txt). Third-party notices remain in effect.
See [LICENSE](LICENSE) for the scope and [CITATION.cff](CITATION.cff) for citation metadata.
