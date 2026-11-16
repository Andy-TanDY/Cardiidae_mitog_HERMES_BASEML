#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_PREFIX="${HERMES_ENV_PREFIX:-$ROOT/.hermes_env_14gene}"
[[ -x "$ENV_PREFIX/bin/python" ]] || { echo "ERROR: no environment: $ENV_PREFIX; run bash setup_server.sh" >&2; exit 2; }
[[ -f "$ROOT/software/HERMES/HERMES-v3.0.py" ]] || { echo 'ERROR: HERMES source missing; run bash setup_server.sh' >&2; exit 2; }
export PATH="$ENV_PREFIX/bin:$PATH"
python - <<'PY'
import Bio
from Bio.SeqUtils import GC
from Bio.SeqFeature import SeqFeature, FeatureLocation
from ete3 import Tree
f=SeqFeature(FeatureLocation(0,3,strand=1),type='CDS')
assert f.strand == 1
print('Biopython', Bio.__version__, '| compatible legacy APIs OK | ETE3 OK')
PY
Rscript --vanilla -e 'library(psych); cat("R psych", as.character(packageVersion("psych")), "\n")'
found=0
for b in raxmlHPC-PTHREADS-AVX2 raxmlHPC-PTHREADS-AVX raxmlHPC-PTHREADS-SSE3 raxmlHPC-PTHREADS; do
  if command -v "$b" >/dev/null 2>&1; then echo "RAxML: $(command -v "$b")"; found=1; break; fi
done
(( found == 1 )) || { echo 'ERROR: RAxML 8 PTHREADS executable not found' >&2; exit 2; }
python "$ROOT/validate_inputs.py" "$ROOT/inputs"
# Check upstream R source contains the expected model-selection code before making any runs.
python - "$ROOT/software/HERMES/HERMES-v3.0.R" <<'PYCHK'
from pathlib import Path
import sys
s = Path(sys.argv[1]).read_text()
a = 'combination.order <- order(best.HERMES.data.frame$HERMES.performance,decreasing=TRUE)'
b = 'combination.order <- order(best.HERMES.data.frame$HERMES.performance,decreasing=FALSE)'
if s.count(a) + s.count(b) != 1:
    raise SystemExit('ERROR: Unexpected HERMES selection code, cannot safely patch.')
if 'HERMES.fa.scores <- as.numeric(HERMES.fa$scores)' not in s:
    raise SystemExit('ERROR: Cannot locate final factor-score computation.')
print('PASS: upstream R model-selection code recognised')
PYCHK
