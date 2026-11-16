#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
if ! command -v baseml >/dev/null 2>&1; then
  echo 'ERROR: baseml not on PATH. Activate your PAML conda environment first.' >&2
  exit 1
fi
python3 validate_inputs.py
models=(M0_strict M1_stem_included M2_stem_included)
# Refuse before starting any models if prior output is present.
for model in "${models[@]}"; do
  if [[ -e "models/$model/baseml.out" || -e "models/$model/stdout.log" ]]; then
    echo "ERROR: Existing outputs in models/$model; refusing to overwrite." >&2
    echo "Extract a fresh copy of this ZIP for a new run." >&2
    exit 1
  fi
done
printf 'Using BASEML executable: %s\n' "$(command -v baseml)"
for model in "${models[@]}"; do
  echo "===== Running $model ====="
  (
    cd "models/$model"
    baseml baseml.ctl > stdout.log 2>&1
    if [[ ! -s baseml.out ]] || ! grep -qE 'lnL\(' baseml.out; then
      echo "ERROR: No fitted lnL for $model. See models/$model/stdout.log" >&2
      exit 1
    fi
    grep -E 'lnL\(' baseml.out | tail -n 1
  )
done
python3 summarize_results.py
