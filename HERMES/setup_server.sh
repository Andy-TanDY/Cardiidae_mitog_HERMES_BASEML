#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# A distinct prefix avoids using a copied, non-relocatable Conda environment.
ENV_PREFIX="${HERMES_ENV_PREFIX:-$ROOT/.hermes_env_14gene}"
mkdir -p "$ROOT/software" "$ROOT/runs" "$ROOT/original_sequences"

if [[ -x "$ENV_PREFIX/bin/python" ]]; then
  echo "Environment already exists: $ENV_PREFIX"
else
  if command -v micromamba >/dev/null 2>&1; then
    micromamba env create -y -p "$ENV_PREFIX" -f "$ROOT/environment.yml"
  elif command -v conda >/dev/null 2>&1; then
    conda env create -p "$ENV_PREFIX" -f "$ROOT/environment.yml"
  else
    echo 'ERROR: conda/micromamba missing.' >&2
    exit 2
  fi
fi

if [[ ! -f "$ROOT/software/HERMES/HERMES-v3.0.py" ]]; then
  if [[ -e "$ROOT/software/HERMES" ]]; then
    echo "ERROR: incomplete HERMES source folder at $ROOT/software/HERMES" >&2
    exit 2
  fi
  git clone https://github.com/federicoplazzi/HERMES.git "$ROOT/software/HERMES"
fi
# Reproduce the exact upstream HERMES revision used for the published analyses.
PIN_FILE="$ROOT/software/HERMES_COMMIT.txt"
if [[ -f "$PIN_FILE" ]] && [[ -d "$ROOT/software/HERMES/.git" ]]; then
  PIN="$(tr -d '\r\n' < "$PIN_FILE")"
  [[ "$PIN" =~ ^[0-9a-fA-F]{40}$ ]] || { echo 'ERROR: invalid HERMES commit pin' >&2; exit 2; }
  git -C "$ROOT/software/HERMES" fetch --quiet origin "$PIN"
  git -C "$ROOT/software/HERMES" checkout --quiet --detach "$PIN"
  ACTUAL="$(git -C "$ROOT/software/HERMES" rev-parse HEAD)"
  [[ "$ACTUAL" == "$PIN" ]] || { echo 'ERROR: HERMES source revision mismatch' >&2; exit 2; }
  echo "Pinned upstream HERMES commit: $ACTUAL"
fi
bash "$ROOT/preflight.sh"
