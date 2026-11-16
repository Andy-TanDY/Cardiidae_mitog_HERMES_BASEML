# Mitochondrial genome divergence in Cardiidae: HERMES and BASEML analyses

Reproducible analysis scripts, mitochondrial genome annotations, sequence alignments, model inputs, outputs and supplementary tables accompanying a comparative study of **photosymbiotic and non-photosymbiotic cardiid bivalves**.

This repository documents two complementary analyses of 12 cardiid species:

- **HERMES v3.0:** genome-wide composite evolutionary divergence, evaluated using three alternative reference taxa and gene-partitioned RAxML sequence distances.
- **PAML BASEML:** relative nucleotide substitution rates under strict-clock and local-clock models with separate Fraginae and Tridacninae branch-rate categories.

> **Manuscript:** Citation and DOI to be added after acceptance/publication. The code and data here pertain to the **14-gene partitioned analyses** and not to older unpartitioned exploratory runs.

## Dataset and analytical scope

The analyses use **12 taxa** and a **12,185-nucleotide alignment of 14 mitochondrial genes** (12 protein-coding genes and two rRNAs). The `cob`/`CYTB` gene is **excluded from the concatenated alignment**, though it remains annotated in the full-mitogenome GenBank inputs. The rooted tree places *Acanthocardia tuberculata* and the two *Cerastoderma* species in the basal reference clade. The complete mitochondrial genome annotations are used to calculate HERMES genomic variables; the 14-gene alignment is used for sequence-distance or nucleotide substitution-rate estimation.

## Repository structure

```text
.
├── README.md
├── HERMES/
│   ├── README.md                 # HERMES-specific workflow and interpretation
│   ├── environment.yml
│   ├── setup_server.sh           # Creates environment, fetches pinned HERMES source
│   ├── preflight.sh
│   ├── validate_inputs.py
│   ├── patch_hermes_r.py         # Documented factor-selection correction
│   ├── run_hermes.sh
│   ├── run_reference_sensitivity.sh
│   ├── inputs/                   # GenBank, alignment, tree, mapping, RAxML partitions
│   ├── original_sequences/       # Original reordered mitogenome FASTAs
│   ├── original_annotations/     # Original annotation CSVs
│   ├── supplementary/            # S1, S2, S6, S7, S8 and supporting TSVs
│   └── results/                  # Published outputs for Atub, Cedu and Cgla
├── BASEML/
│   ├── README.md                 # BASEML-specific workflow and interpretation
│   ├── run_all.sh
│   ├── validate_inputs.py
│   ├── summarize_results.py
│   ├── inputs/                   # Gene partition audit and common alignment
│   ├── models/                   # Clean M0/M1/M2 ctl, tree and alignment inputs
│   ├── supplementary/            # S3, S4, S5 and S9 TSVs
│   └── results/                  # Published model outputs and summaries
└── docs/
    ├── DATA_AVAILABILITY.md
    ├── CITATION_AND_LICENSING.md
    └── GITHUB_REPOSITORY_DETAILS.md
```

The directories called `results/` contain **completed, archived outputs** from the reported analyses. The original scripts are set up to write fresh HERMES outputs to `HERMES/runs/` and BASEML outputs to `BASEML/models/*/`. Thus, archived results are not reused when the scripts are rerun.

## Quick start

### HERMES

On Linux, with Conda or Micromamba, Git, and Internet access for initial setup:

```bash
cd HERMES
bash setup_server.sh
bash preflight.sh
bash run_reference_sensitivity.sh 4
```

This runs the Atub, Cedu and Cgla analyses sequentially using four RAxML threads per reference. The script refuses to overwrite an existing run directory. See [HERMES/README.md](HERMES/README.md).

### BASEML

Install and activate a working PAML environment that provides `baseml`, then:

```bash
cd BASEML
python3 validate_inputs.py
bash run_all.sh
```

This fits M0, M1 and M2 sequentially using **the supplied stem-inclusive branch labels**. Each run uses the 14-gene `G` alignment with gene-rate multipliers (`Mgene = 0`); it does *not* fit a separate GTR matrix for each gene. See [BASEML/README.md](BASEML/README.md).

## Primary results (14-gene partitioned analyses)

| Analysis | Finding |
| --- | --- |
| HERMES (Atub) | Photosymbiotic mean 0.438; non-photosymbiotic mean −0.766 |
| HERMES (Cedu) | Photosymbiotic mean 0.295; non-photosymbiotic mean −0.516 |
| HERMES (Cgla) | Photosymbiotic mean 0.483; non-photosymbiotic mean −0.846 |
| BASEML M2 | Fraginae/background rate ratio 1.161; Tridacninae/background rate ratio 1.836 |
| BASEML model choice | Three-rate M2 has the lowest AIC among M0, M1 and M2 (232,704.887) |

HERMES group differences are **descriptive and not phylogenetically corrected tests**. HERMES is primarily a composite measure of genome architecture and composition in these selected factor models; it is **not** a direct estimate of the nucleotide substitution rate. BASEML estimates *relative* substitution rates under specified topology and clock-group assumptions, not absolute rates or evidence of photosymbiosis as a causal mechanism.

## Manuscript supplementary tables

(Same as manuscript Supplementary Data S5 and S6. )

| Table | Location | Contents |
| --- | --- | --- |
| S1 | `HERMES/supplementary/` | HERMES scores for all 33 reference-specific observations; Panel A data |
| S2 | `HERMES/supplementary/` | Selected factor models and fit diagnostics |
| S3 | `HERMES/supplementary/` | Factor loadings and communalities |
| S4 | `HERMES/supplementary/` | Candidate factor-model tie-break audit |
| S5 | `HERMES/supplementary/` | Ecological group descriptives |
| S1 | `BASEML/supplementary/` | BASEML model-fit statistics |
| S2 | `BASEML/supplementary/` | Nested likelihood-ratio tests |
| S3 | `BASEML/supplementary/` | BASEML rate estimates, standard errors and confidence intervals; Panel B data |
| S4 | `BASEML/supplementary/` | Gene-specific BASEML rate multipliers |

TSV files are UTF-8 and tab-delimited. The complete raw model output files used to generate the tables are available in the corresponding `results/` folders.

## Software and provenance

- [HERMES v3.0](https://github.com/federicoplazzi/HERMES), upstream revision `e774346121d99ff24997c003dd623cbfbbf11566`. HERMES code is retrieved from its original repository by the setup script; **third-party HERMES source is not vendored** here.
- RAxML **8.2.12** (`GTRGAMMA`), confirmed in the original HERMES run logs. The supplied `environment.yml` requests the RAxML 8 series; a fresh solve may select a different patch build.
- R **4.3.3** and Python **3.9.23** in the completed HERMES runs.
- [PAML BASEML](https://github.com/abacus-gene/paml), **version 4.10.10** (as reported by the uploaded BASEML model outputs).

The HERMES workflow applies a transparent one-line **factor-selection tie-break correction** in a temporary per-run R script: the upstream code sorts a diagnostic mean-ratio in descending order even though its adjacent comment specifies minimisation. Here it sorts in ascending order and exports final factor loadings. See `HERMES/patch_hermes_r.py` and the HERMES-specific README. The correction does not enforce any predetermined biological outcome.

## Reproducibility boundaries

- This repository reproduces the **HERMES and BASEML analyses from their provided alignments, genome annotations and tree**, but does not reproduce raw sequencing, assembly, original gene alignments, or phylogeny inference.
- Gene rate partitioning differs between the tools: RAxML uses separate GTR+Γ partition models for the HERMES distance analysis; BASEML shares substitution parameters and estimates gene-rate multipliers.
- HERMES model fitting can produce warnings for unsuccessful candidate factors; inspect the selected-model diagnostics, not only process completion. Full original server logs are retained by the study authors but excluded from this public snapshot because they contain local filesystem paths and third-party execution copies.
- Where included, run metadata and source input checksums are preserved, except for local machine-specific executable paths removed for public distribution.
