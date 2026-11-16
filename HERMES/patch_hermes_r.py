#!/usr/bin/env python3
"""Patch only a per-run copy of HERMES-v3.0.R, never the source clone.

The upstream script documents minimisation of the mean diagnostic-threshold
ratio, but sorts that ratio in decreasing order. Correct it to increasing order
and export final factor loadings for downstream audit. Fail on unexpected code.
"""
from pathlib import Path
import argparse

OLD = 'combination.order <- order(best.HERMES.data.frame$HERMES.performance,decreasing=TRUE)'
NEW = 'combination.order <- order(best.HERMES.data.frame$HERMES.performance,decreasing=FALSE)'
ANCHOR = 'HERMES.fa.scores <- as.numeric(HERMES.fa$scores)'
EXPORT = ('write.table(as.matrix(HERMES.fa$loadings), '
          'file="./Results/HERMES_factor_loadings.tsv", '
          'sep="\\t", quote=FALSE, col.names=NA)\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('script', type=Path)
    args = parser.parse_args()
    f = args.script
    text = f.read_text(encoding='utf-8')
    if text.count(OLD) == 1 and text.count(NEW) == 0:
        text = text.replace(OLD, NEW)
        print('Applied corrected ascending HERMES tie-break.')
    elif text.count(NEW) == 1 and text.count(OLD) == 0:
        print('Tie-break already ascending; keeping it.')
    else:
        raise SystemExit('ERROR: unexpected HERMES R tie-break line; refusing an unsafe patch.')

    if EXPORT in text:
        print('Factor loadings export already present.')
    elif text.count(ANCHOR) == 1:
        text = text.replace(ANCHOR, EXPORT + ANCHOR)
        print('Added selected-factor loadings export.')
    else:
        raise SystemExit('ERROR: cannot uniquely locate final-factor score line.')

    assert text.count(NEW) == 1 and OLD not in text
    f.write_text(text, encoding='utf-8')
    print('Verified local R patch:', f)


if __name__ == '__main__':
    main()
