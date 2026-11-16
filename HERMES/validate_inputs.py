#!/usr/bin/env python3
"""Validate the 12-genome Cardiidae input set and all 14 partition blocks."""
from pathlib import Path
from collections import Counter
import csv
import re
import sys
from Bio import SeqIO, Phylo, AlignIO

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('inputs')
FILES = {
    'genbank': ROOT / 'Cardiidae_12taxa_corrected_annotations.gb',
    'mapping': ROOT / 'Cardiidae_12taxa_abbreviated_entry_names.csv',
    'tree': ROOT / 'Cardiidae_12taxa_IQTREE_ML_ROOTED_Atub_Cedu_Cgla.tre',
    'alignment': ROOT / 'Cardiidae_12taxa_14gene_alignment.phy',
    'partitions': ROOT / 'RAxML_14gene_partitions.txt'
}
for key, path in FILES.items():
    if not path.is_file() or path.stat().st_size == 0:
        raise SystemExit(f'ERROR: missing/empty {key}: {path}')

records = list(SeqIO.parse(FILES['genbank'], 'genbank'))
assert len(records) == 12, f'Expected 12 genomes, found {len(records)}'
accessions = {r.id.split('.')[0] for r in records}
assert len(accessions) == 12, 'Duplicated GenBank accessions'
with FILES['mapping'].open(newline='') as h:
    rows = list(csv.reader(h))
assert len(rows) == 12 and all(len(r) in (2, 3) for r in rows), 'Mapping should have 12 rows'
names = [r[0] for r in rows]
assert len(set(names)) == 12, 'Duplicated mapping identifiers'
assert {r[1].split('.')[0] for r in rows} == accessions, 'Mapping/GenBank accession mismatch'

alignment = AlignIO.read(str(FILES['alignment']), 'phylip-relaxed')
assert len(alignment) == 12, 'Expected 12 alignment sequences'
L = alignment.get_alignment_length()
assert L == 12185, f'Expected 12185 sites; found {L}'
assert {r.id for r in alignment} == set(names), 'Alignment/mapping names differ'
tree = Phylo.read(str(FILES['tree']), 'newick')
assert {t.name for t in tree.get_terminals()} == set(names), 'Tree/mapping names differ'
assert len(tree.get_terminals()) == 12, 'Expected 12 tree tips'
root_sets = [{t.name for t in c.get_terminals()} for c in tree.root.clades]
assert {'Atub', 'Cedu', 'Cgla'} in root_sets, 'Root does not separate Atub+Cedu+Cgla'

for record in records:
    assert record.annotations.get('topology') == 'circular', f'{record.id}: topology mismatch'
    assert record.features and record.features[0].type == 'source', f'{record.id}: no source feature'
    assert int(record.features[0].location.start) == 0, f'{record.id}: source not full length'
    assert int(record.features[0].location.end) == len(record), f'{record.id}: source not full length'
    types = Counter(feat.type for feat in record.features)
    assert types['CDS'] >= 13 and types['rRNA'] == 2, f'{record.id}: unexpected genes {types}'
    for feat in record.features:
        for part in feat.location.parts:
            assert 0 <= int(part.start) < int(part.end) <= len(record), f'{record.id}: feature out of bounds'

expected_names = {'ATP6','ATP8','COX1','COX2','COX3','NAD1','NAD2','NAD3',
                  'NAD4','NAD4L','NAD5','NAD6','rrnL','rrnS'}
seen = []
covered = [0] * (L + 1)
for number, line in enumerate(FILES['partitions'].read_text().splitlines(), 1):
    line = line.strip()
    if not line or line.startswith('#'):
        continue
    m = re.fullmatch(r'DNA\s*,\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*(\d+)\s*-\s*(\d+)', line)
    if not m:
        raise SystemExit(f'ERROR: invalid partition line {number}: {line}')
    name, start, end = m.group(1), int(m.group(2)), int(m.group(3))
    assert 1 <= start <= end <= L, f'{name}: outside alignment coordinates'
    seen.append(name)
    for pos in range(start, end + 1):
        covered[pos] += 1
assert len(seen) == 14 and set(seen) == expected_names, f'Expected 14 named genes; found {seen}'
assert all(x == 1 for x in covered[1:]), 'Partition coverage has gaps or overlaps'

print('PASS: 12 GenBank sequences, 12 mapping names, 12 aligned sequences, 12 tree tips')
print('PASS: 14 gene partitions cover all 12,185 aligned sites exactly once')
print('PASS: basal Atub+Cedu+Cgla clade and genomic feature bounds checked')
print('NOTE: CYTB is retained in GenBank annotations but excluded from the 14-gene alignment')
