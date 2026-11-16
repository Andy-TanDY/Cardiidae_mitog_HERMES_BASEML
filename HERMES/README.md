# HERMES analysis: three references, 14 gene partitions

This directory contains the original mitogenome inputs, archived outputs and reproducible shell/Python workflow for HERMES v3.0 analyses of 12 cardiid bivalves. The three alternative references are **Atub** (*Acanthocardia tuberculata*), **Cedu** (*Cerastoderma edule*) and **Cgla** (*C. glaucum*).

## Files

- `inputs/`: 12-taxon corrected GenBank file (genome-wide features), 12,185-site 14-gene PHYLIP alignment, rooted Newick tree, reference-name mapping and `RAxML_14gene_partitions.txt`.
- `original_sequences/`, `original_annotations/`: archival FASTA and annotation CSV files; the running HERMES workflow uses the assembled `inputs/` files.
- `environment.yml`, `setup_server.sh`, `preflight.sh`, `validate_inputs.py`: environment setup and validation.
- `run_hermes.sh`: one reference analysis; `run_reference_sensitivity.sh`: all three analyses, sequentially.
- `patch_hermes_r.py`: applies the documented factor-selection tie-break correction **to a copy** of upstream HERMES R code, then exports the selected factor loadings.
- `results/`: completed outputs from the manuscript analyses, three reference folders. Each folder contains the `Results/` files (`HERMES-v3.0_scores.txt`, `HERMES-v3.0_parameters.txt`, `HERMES_variables.txt`, `best.HERMES.out`, `HERMES_factor_loadings.tsv`, the HERMES PDF) and input/run provenance.
- `supplementary/`: S1, S2, S3, S4, S5, plus genomic variables, ecology lookup and cross-reference score summaries.

## Run from scratch

```bash
cd HERMES
bash setup_server.sh
bash preflight.sh
bash run_reference_sensitivity.sh 4
```

Requires a Linux system, Conda/Micromamba, Git and an Internet connection during setup. The setup script clones [upstream HERMES](https://github.com/federicoplazzi/HERMES) and checks out **commit `e774346121d99ff24997c003dd623cbfbbf11566`**, matching the original study runs. It creates the environment under `.hermes_env_14gene/`; neither its environment nor the upstream checkout is committed here. The analysis creates new results under `runs/` and never reads `results/`.

Run just one reference with `bash run_hermes.sh Atub 4` (substitute Cedu or Cgla). Re-running the same reference/thread count in the same directory stops to prevent overwriting generated output. For production use, run through your HPC scheduler rather than on a login node.

## Alignment and reference sensitivity

The 14-gene alignment comprises **12 protein-coding genes and two rRNAs**, totalling **12,185 positions**. `CYTB/cob` is *not* in this alignment, although it remains annotated in the complete mitogenomic GenBank file. RAxML 8 estimates sequence distances with 14 distinct DNA partitions under GTR+Γ (`GTRGAMMA`). The same rooted phylogram is supplied to the three reference analyses.

Each analysis scores the 11 species other than its chosen reference taxon: **7 photosymbiotic** and **4 non-photosymbiotic** species. Group means are descriptive:

| Reference | Photosymbiotic mean | Non-photosymbiotic mean | Difference |
| --- | ---: | ---: | ---: |
| Atub | 0.438 | −0.766 | 1.204 |
| Cedu | 0.295 | −0.516 | 0.811 |
| Cgla | 0.483 | −0.846 | 1.329 |

Raw scores are in `supplementary/S1_HERMES_scores_all_references.tsv`; candidate diagnostics and factor loadings are in S2, S6 and S7. The HERMES models selected here consistently include unassigned-region proportion, but do not select maximum-likelihood sequence distance. They represent a multivariate architectural/compositional index, not an independent estimator of substitutions/site/time.

## HERMES model-selection correction

In upstream HERMES R code, tied candidate models (those meeting the same maximum count of diagnostic criteria) are ranked using a mean threshold-ratio (`HERMES.performance`). The nearby comment says to select the **minimum** of this statistic, while the executable code instead sorts `decreasing=TRUE`. The supplied `patch_hermes_r.py` changes this to `decreasing=FALSE` **only inside the working copy** of `HERMES-v3.0.R` used for each run. It also writes `HERMES_factor_loadings.tsv` for auditing.

The original upstream source is left unchanged. The correction is an implementation consistency fix, not a biological constraint. Small sample size (11 taxa/reference) and failed candidate-factor optimisations call for careful interpretation of model-selection stability and communalities.

## Reproducibility notes

- HERMES Git revision: `e774346121d99ff24997c003dd623cbfbbf11566`.
- The completed analysis logs identify **RAxML 8.2.12**, **Python 3.9.23** and **R 4.3.3**. Exact versions may differ in a newly solved Conda environment; inspect local preflight results.
- The public `results/` snapshot excludes the upstream HERMES source copies and raw execution logs containing personal workstation/server filesystem paths. Those files are not needed to locate the reported scores and selected-factor diagnostics.
- The published HERMES comparisons are **not phylogenetically controlled tests** of an ecological association; they do not establish causation by photosymbiosis.
