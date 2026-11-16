#!/usr/bin/env python3
"""Verify 14-gene PAML option-G alignment and three clock-model inputs."""
from pathlib import Path
import re, csv, sys, hashlib
root=Path(__file__).resolve().parent
expected=['Ffra','Fwhi','Fsue','Tgig','Tcro','Tder','Hhip','Fmut','Lcra','Cedu','Cgla','Atub']
seqlen=12185
lengths=[1217,114,1559,689,831,910,971,357,1359,276,1682,482,1068,670]
genes=['ATP6','ATP8','COX1','COX2','COX3','NAD1','NAD2','NAD3','NAD4','NAD4L','NAD5','NAD6','rrnL','rrnS']
assert sum(lengths)==seqlen
p=(root/'inputs'/'alignment_14gene_partitioned.phy')
lines=p.read_text().splitlines()
assert lines[0].split()==['12','12185','G'], f'Invalid header: {lines[0]}'
assert lines[1].split()==['G','14']+[str(n) for n in lengths], 'Invalid gene partition specification'
seqs={}
for line in lines[2:]:
    fields=line.split()
    if len(fields)!=2: raise ValueError('Expected one sequence per line, with taxon name: '+line[:80])
    name,seq=fields
    if name in seqs: raise ValueError('Repeated species '+name)
    if not re.fullmatch('[ACGTNRYKMSWBDHV?-]+',seq.upper()):raise ValueError('Unexpected characters in '+name)
    if len(seq)!=seqlen: raise ValueError(f'Incorrect length {name}: {len(seq)}')
    seqs[name]=seq
assert len(seqs)==12 and set(seqs)==set(expected),f'Wrong taxa {seqs.keys()}'
with (root/'inputs'/'partition_audit.tsv').open() as fh:
    records=[r for r in csv.DictReader(fh,delimiter='\t') if r['partition']!='TOTAL']
assert len(records)==14 and [r['partition'] for r in records]==genes, 'Audit partitions not same ordered genes'
for i,row in enumerate(records):
    assert int(row['aligned_length'])==lengths[i], row
for model,clock,nlab in [('M0_strict','1',0),('M1_stem_included','2',12),('M2_stem_included','2',12)]:
    md=root/'models'/model
    assert (md/'alignment.phy').read_bytes()==p.read_bytes(), f'Alignment differs: {model}'
    tree=(md/'tree.tre').read_text()
    assert tree.startswith('12 1\n'),f'Invalid tree header: {model}'
    assert all(re.search(r'\b'+name+r'\b',tree) for name in expected),f'Tree missing taxa: {model}'
    assert tree.count('(')==tree.count(')'),f'Unbalanced tree: {model}'
    assert tree.count('#')==nlab,f'Unexpected labels: {model} {tree.count("#")}'
    ctl=(md/'baseml.ctl').read_text()
    assert re.search(r'^clock\s*=\s*'+clock+r'\s*$',ctl,re.M)
    assert re.search(r'^Mgene\s*=\s*0\s*$',ctl,re.M)
    assert re.search(r'^Malpha\s*=\s*0\s*$',ctl,re.M)
print('PASS: 12 taxa, 12185 nt, 14 partitions, G alignment, correct model inputs.')
print('PHYLIP SHA256:',hashlib.sha256(p.read_bytes()).hexdigest())
