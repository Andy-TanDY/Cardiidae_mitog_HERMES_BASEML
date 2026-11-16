#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THREADS="${1:-4}"

printf 'Partitioned HERMES v3.0 with corrected factor-selection tie-break\n'
printf 'References: Atub, Cedu, Cgla | Threads per RAxML run: %s\n' "$THREADS"
printf 'Outputs: %s/runs/*_14gene_partitioned_fixed/\n' "$ROOT"

# Before starting any reference, refuse to mix new runs with existing outputs.
for ref in Atub Cedu Cgla; do
  target="$ROOT/runs/${ref}_${THREADS}threads_14gene_partitioned_fixed"
  if [[ -e "$target" ]]; then
    echo "ERROR: Existing run directory: $target" >&2
    echo 'Archive or use a newly extracted copy; nothing has been overwritten.' >&2
    exit 2
  fi
done

for ref in Atub Cedu Cgla; do
  echo "===== $ref ====="
  bash "$ROOT/run_hermes.sh" "$ref" "$THREADS"
done

echo 'All three reference runs completed. Original inputs and HERMES source unchanged.'
