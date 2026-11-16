#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_PREFIX="${HERMES_ENV_PREFIX:-$ROOT/.hermes_env_14gene}"
REFERENCE="${1:-Atub}"
THREADS="${2:-4}"
RUN_TAG="14gene_partitioned_fixed"
case "$REFERENCE" in Atub|Cedu|Cgla) ;; *) echo 'ERROR: reference must be Atub, Cedu, or Cgla' >&2; exit 2 ;; esac
[[ "$THREADS" =~ ^[0-9]+$ ]] && (( THREADS >= 1 && THREADS <= 48 )) || { echo 'ERROR: threads must be 1..48' >&2; exit 2; }
export PATH="$ENV_PREFIX/bin:$PATH"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1

# Run preflight first, including partition coverage and package requirements.
bash "$ROOT/preflight.sh"

RA=''
for b in raxmlHPC-PTHREADS-AVX2 raxmlHPC-PTHREADS-AVX raxmlHPC-PTHREADS-SSE3 raxmlHPC-PTHREADS; do
  if command -v "$b" >/dev/null 2>&1; then RA="$(command -v "$b")"; break; fi
done
[[ -n "$RA" ]] || { echo 'ERROR: RAxML 8 PTHREADS binary missing' >&2; exit 2; }

OUT="$ROOT/runs/${REFERENCE}_${THREADS}threads_${RUN_TAG}"
[[ ! -e "$OUT" ]] || { echo "ERROR: run directory already exists: $OUT" >&2; exit 2; }
mkdir -p "$OUT"

# Copy upstream scripts into an independent run folder, never patch the clone.
for f in HERMES-v3.0.py HERMES-v3.0.R Genes.dict colors; do
  cp "$ROOT/software/HERMES/$f" "$OUT/$f"
done
python "$ROOT/patch_hermes_r.py" "$OUT/HERMES-v3.0.R"
ln -s "$RA" "$OUT/raxml"

GB='Cardiidae_12taxa_corrected_annotations.gb'
MAP='Cardiidae_12taxa_abbreviated_entry_names.csv'
TREE='Cardiidae_12taxa_IQTREE_ML_ROOTED_Atub_Cedu_Cgla.tre'
ALN='Cardiidae_12taxa_14gene_alignment.phy'
PART='RAxML_14gene_partitions.txt'
for f in "$GB" "$MAP" "$TREE" "$ALN" "$PART"; do
  ln -s "$ROOT/inputs/$f" "$OUT/$f"
done

{
  printf 'Reference\t%s\nThreads\t%s\nRun_tag\t%s\n' "$REFERENCE" "$THREADS" "$RUN_TAG"
  printf 'Partitions\t%s\nModel\tGTRGAMMA\nGenetic_code\t5\n' "$PART"
  printf 'Date_UTC\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'Python\t%s\n' "$(python --version 2>&1)"
  printf 'R\t%s\n' "$(Rscript --version 2>&1)"
  printf 'RAxML\t%s\n' "$RA"
  if [[ -f "$ROOT/software/HERMES_COMMIT.txt" ]]; then
    printf 'HERMES_commit\t%s\n' "$(cat "$ROOT/software/HERMES_COMMIT.txt")"
  fi
} > "$OUT/run_metadata.tsv"
if command -v sha256sum >/dev/null 2>&1; then
  (cd "$OUT" && sha256sum "$GB" "$MAP" "$TREE" "$ALN" "$PART" HERMES-v3.0.R) > "$OUT/input_and_script_sha256.txt"
fi

printf '\nSTART %s reference: %s (%s RAxML threads)\n' "$RUN_TAG" "$REFERENCE" "$THREADS"
if ! (
  cd "$OUT"
  python -u HERMES-v3.0.py \
    -I "$GB" \
    -D "$MAP" \
    -L "$TREE" \
    -O "$REFERENCE" \
    -s "$ALN" \
    -q "$PART" \
    -m GTRGAMMA \
    -G 5 \
    -t "$THREADS"
) > "$OUT/run.log" 2>&1; then
  echo "ERROR: HERMES failed: $OUT/run.log" >&2
  tail -n 60 "$OUT/run.log" >&2
  exit 1
fi

for f in HERMES_variables.txt HERMES-v3.0_scores.txt HERMES-v3.0_parameters.txt best.HERMES.out HERMES_factor_loadings.tsv; do
  [[ -s "$OUT/Results/$f" ]] || {
    echo "ERROR: expected HERMES output is missing/empty: $OUT/Results/$f" >&2
    tail -n 60 "$OUT/run.log" >&2
    exit 1
  }
done

echo "SUCCESS: $OUT"
cat "$OUT/Results/HERMES-v3.0_scores.txt"
