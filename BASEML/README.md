# PAML BASEML: 14-gene partitioned local-clock models

This directory contains the 12-taxon partitioned PHYLIP alignment, branch-labelled trees, BASEML control files, execution/validation scripts, and archived model outputs for the 14-gene analysis.

## Models and assumptions

| Model | Branch-rate groups | `clock` |
| --- | --- | --- |
| `M0_strict` | One global rate | `1` |
| `M1_stem_included` | Non-photosymbiotic background; shared photosymbiotic stem+crown | `2` |
| `M2_stem_included` | Background; Fraginae stem+crown; Tridacninae stem+crown | `2` |

The same topology and stem-inclusive labelling are used throughout. The PHYLIP `G` input contains **14 gene blocks** spanning 12,185 aligned sites (12 protein-coding genes plus two rRNAs; `cob` excluded). BASEML uses `model = 7` (GTR/REV), `Mgene = 0` (separate *overall gene-rate multipliers* with shared substitution parameters), `Malpha = 0`, estimated gamma shape (`fix_alpha = 0`, `ncatG = 8`) and `cleandata = 0`. This is **not** an independently estimated GTR model for each gene. `getSE = 1` for M2 enables standard errors.

## Directory guide

- `inputs/alignment_14gene_partitioned.phy`: `G`-formatted alignment; `inputs/partition_audit.tsv` documents gene lengths and sites.
- `models/M0_strict/`, `models/M1_stem_included/`, `models/M2_stem_included/`: **clean runnable inputs** (`alignment.phy`, `tree.tre`, `baseml.ctl`), without pre-existing output files.
- `run_all.sh`: validates and fits M0, M1 and M2 sequentially; refuses overwriting an existing output.
- `summarize_results.py`: produces model-fit summaries, nested LRTs and branch-rate ratios from new BASEML outputs using Python standard-library tools.
- `results/`: **archived published outputs** (`model_fits.tsv`, `LRT_comparisons.tsv`, `relative_rates.tsv` and each model's `baseml.out`/`stdout.log`). These are separate from the clean run inputs.
- `supplementary/`: S1, S2, S3 and S4, including the independently checked M2 approximate 95% Wald intervals.

## Run independently

Install [PAML BASEML](https://github.com/abacus-gene/paml) (original output: **PAML 4.10.10**) and make `baseml` available on `PATH`. For instance, after activating an environment containing PAML:

```bash
cd BASEML
python3 validate_inputs.py
bash run_all.sh
cat model_fits.tsv
cat LRT_comparisons.tsv
cat relative_rates.tsv
```

Each model runs sequentially, generally on one core; the scripts are designed for Linux Bash. The outputs are written to `models/*/` and do not read the archived `results/` directory. An existing `baseml.out` or `stdout.log` causes the script to stop; use a clean checkout to rerun.

## Results included in the repository

| Model | lnL | Parameters | AIC |
| --- | ---: | ---: | ---: |
| M0 strict | −116421.264502 | 30 | 232902.529004 |
| M1 shared photosymbiotic rate | −116377.100657 | 31 | 232816.201314 |
| M2 separate photosymbiotic rates | −116320.443285 | 32 | **232704.886570** |

Nested likelihood-ratio comparisons: M0→M1, LR=88.328 (df=1, p=5.55×10⁻²¹); M1→M2, LR=113.315 (df=1, p=1.84×10⁻²⁶). M2 relative rate multipliers are **1.161** for Fraginae and **1.836** for Tridacninae, against a background fixed at 1. Approximate 95% Wald confidence intervals are **1.051–1.271** and **1.660–2.013**, respectively, based on M2 output standard errors.

These tests compare *rate-group model fits* conditional on the branch assignments and topology. They are not direct tests that photosymbiosis caused an increased nucleotide substitution rate. The branch length warning in BASEML output refers to the printed tree lengths, not the estimated branch-rate multipliers. Additional unclocked or lineage-specific restricted models are not included in this three-model archive.

## Notes for data reuse

- `S1` and `S2` are derived from the nested model fits. `S3` includes manually verified SE/CI values that are not exported by `summarize_results.py`, and `S4` contains gene-rate multipliers. Cite the relevant version of this repository and the associated manuscript.
- The provided alignments and tree are already curated inputs. This directory does not contain the preprocessing workflow used to assemble, align or infer the input phylogeny.
- Sequence lengths and branch labels can be checked using `python3 validate_inputs.py` before optimisation.
