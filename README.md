# From information tasks to exclusivity and Bell bounds

Read the [final manuscript](information_tasks_bell_bounds.pdf). This research manuscript is
published on [Zenodo](https://doi.org/10.5281/zenodo.23245295), released with its calculations and supporting material.

## Release and verification

The final PDF was supplied separately from the source bundle. The bundled
LaTeX is an earlier revision: rebuilding it produces `paper.pdf`,
not the final manuscript above. The final PDF is preserved byte for byte.

On October 4, 2026, `bash build.sh` passed in a fresh validation copy using
Python 3.12.3 and pdfTeX 1.40.25 (TeX Live 2023/Debian). 1,276 exact finite checks passed.
The final LaTeX pass had no unresolved references, warnings, or overfull or
underfull boxes. There are no Lean sources or Lake projects in this bundle.
These checks concern the supplied source and finite examples; they do not
verify every argument in the final PDF.

See [the current validation record](verification/release.json) and
[execution log](verification/build.log). Earlier build records elsewhere in
the repository belong to the supplied source bundle.

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
python3 -m pip install -r requirements.txt
bash build.sh
```

The build requires pdfLaTeX and the standard AMS, graphics, microtype, natbib, float, TikZ, pgfplots, and quantikz packages. The unmodified `quantumarticle.cls` version 6.1 is included with its license notice. No font files are included. The reference build uses TeX Live 2025/dev (Debian), Python 3.13.5, and SymPy 1.14.0.

The script runs the exact certificate program and makes three LaTeX passes. It stops on a failed check, compilation error, warning, overfull box, or missing character. `paper.pdf` is the output. The actual page count, abstract length, certificate count, and diagnostic counts are in `results/build.json`. The reference release also contains reports from a fresh-extraction build and visual inspection of every rendered page.

## Files

`main.tex` contains the three principal results, the no-hypersignaling corollary, source-located premises, examples, and discussion. `appendices.tex` contains closure and calibration proofs, the running qubit calculation, event-counting certificates, spectator-capacity transport, standard quantum comparisons, and an exact verification of the published hypersignaling witness. The full noisy-interface construction from the earlier draft is not repeated. `references.tex` supplies the bibliography without requiring BibTeX.

`figures/` contains the TikZ task diagram, pgfplots graphs, and quantikz circuit. All graphs show explicit formulas. `scripts/check_certificates.py` uses integer enumeration, rational arithmetic, and symbolic algebra; it does not use floating-point acceptance tests.

The 1,276 finite checks cover the sixteen-set construction, all 128 ordered same-status pairs, 576 pairwise exclusivity comparisons, the residual polynomial, quantum parity and capacity witnesses, the five-event LO obstruction, exact frequency-risk formulas, the elementary identity communication game, and the published hypersignaling example. The identity-game group also enumerates all 3,005 deterministic five-label maps with image size at most four. Universal task and composition results have written proofs; these finite checks do not formalize those proofs.

Generated files include:

- `results/certificates.json`: exact constants and check groups.
- `results/checks.json`: individual finite checks.
- `results/sixteen_cliques.json`: generated events and exclusivity witnesses.
- `results/hypersignaling.json`: the published seven-input channel, payoff, all 35 four-column classical optima, and the identity-game certificate.
- `results/latex_build.log` and the build reports: actual compilation and reproducibility records.

## Relation to prior work

The manuscript distinguishes its task-domain formulation from Short and Barrett's state-versus-measurement trade-off, Czekaj, Horodecki, and Tylec's Bell-measurement constraints, and Dall'Arno and collaborators' no-hypersignaling principle. Cabello is credited for the two-copy counting construction; Chiribella and Yuan for the sharp-instrument route; Fritz and collaborators for local orthogonality; Navascués and collaborators for almost-quantum correlations; and Selby and collaborators for parity-reading measurement constraints. Constructor-theoretic premises have version-specific locators.

The hypersignaling model and its payoff gap 1/42 are published results, not new constructions. The appendix proves the readable-alphabet bounds and checks that witness exactly. The model violates information principle IV and is explicitly not a countermodel to the paper's constructor premises.

`SHA256SUMS` records the delivered files. A rebuild may change PDF timestamps and document identifiers without changing its text or mathematics.

## License and citation

The manuscript and original research material use [CC BY 4.0](LICENSES/CC-BY-4.0.txt).
Original code uses [MIT](LICENSES/MIT.txt). Third-party notices remain in effect.
See [LICENSE](LICENSE) for the scope and [CITATION.cff](CITATION.cff) for citation metadata.
