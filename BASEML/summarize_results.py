#!/usr/bin/env python3
"""Summarise three nested PAML BASEML clock models; uses Python stdlib only."""
import re, csv, math, sys
from pathlib import Path
root=Path(__file__).resolve().parent
models=['M0_strict','M1_stem_included','M2_stem_included']
pat=re.compile(r'lnL\([^\n]*?np:\s*(\d+)\):\s*([-+]?\d+(?:\.\d+)?(?:[Ee][-+]?\d+)?)')
float_pat=re.compile(r'[-+]?\d+(?:\.\d+)?(?:[Ee][-+]?\d+)?')
result={}
for model in models:
    f=root/'models'/model/'baseml.out'
    if not f.exists():
        print('Missing',f,file=sys.stderr);sys.exit(1)
    txt=f.read_text(errors='replace')
    matches=pat.findall(txt)
    if len(matches)!=1:
        print('WARNING: expected one lnL record; found',len(matches),'in',f,file=sys.stderr)
        if not matches:sys.exit(1)
    np,ll=matches[-1]
    result[model]={'np':int(np),'lnL':float(ll)}
    rates=re.findall(r'^rates for branches:\s*(.+)$',txt,re.M)
    result[model]['rates']=[float(x) for x in rates[-1].split()] if rates else []
    if re.search(r'(?i)\b(?:nan|inf(?:inity)?)\b',txt):
        print('CHECK possible numerical issues:',model,file=sys.stderr)
    if ('check convergence' in txt.lower() or 'failed to converge' in txt.lower() or 'not converged' in txt.lower()):
        print('CHECK convergence warning:',model,file=sys.stderr)
with (root/'model_fits.tsv').open('w',newline='') as fh:
    w=csv.writer(fh,delimiter='\t')
    w.writerow(['model','log_likelihood','n_parameters','AIC','delta_AIC'])
    aics={m:2*v['np']-2*v['lnL'] for m,v in result.items()}
    best=min(aics.values())
    for m,v in result.items():
        w.writerow([m,f"{v['lnL']:.6f}",v['np'],f"{aics[m]:.6f}",f"{aics[m]-best:.6f}"])
with (root/'LRT_comparisons.tsv').open('w',newline='') as fh:
    w=csv.writer(fh,delimiter='\t')
    w.writerow(['null','alternative','LR','df_from_parameters','p_chisq','warning'])
    for m0,m1 in [('M0_strict','M1_stem_included'),('M1_stem_included','M2_stem_included'),('M0_strict','M2_stem_included')]:
        lr=2*(result[m1]['lnL']-result[m0]['lnL'])
        df=result[m1]['np']-result[m0]['np']
        warnings=[]
        expected=2 if (m0,m1)==('M0_strict','M2_stem_included') else 1
        if df!=expected:warnings.append('Parameter count difference differs from expected')
        if lr<-0.001:warnings.append('Alternative has worse lnL: convergence issue')
        if df==1:p=math.erfc(math.sqrt(max(0.,lr)/2))
        elif df==2:p=math.exp(-max(0.,lr)/2)
        else:p=None;warnings.append('Unsupported df for builtin chi-square')
        w.writerow([m0,m1,f'{lr:.6f}',df,f'{p:.8g}' if p is not None else '', '; '.join(warnings)])
with (root/'relative_rates.tsv').open('w',newline='') as fh:
    w=csv.writer(fh,delimiter='\t')
    w.writerow(['model','branch_group','relative_rate','notes'])
    w.writerow(['M0_strict','All branches',1.0,'fixed reference'])
    w.writerow(['M1_stem_included','Background',1.0,'fixed reference'])
    w.writerow(['M2_stem_included','Background',1.0,'fixed reference'])
    for m,groups in [('M1_stem_included',['Photosymbiotic stem+crown']),('M2_stem_included',['Fraginae stem+crown','Tridacninae stem+crown'])]:
        rates=result[m]['rates']
        if rates and len(rates)==len(groups)+1:
            for group,rate in zip(groups,rates[1:]):w.writerow([m,group,f'{rate:.6f}','from BASEML rates for branches'])
        else:
            print('WARNING: rate parsing failed for',m,rates,file=sys.stderr)
print('MODEL FITS')
for m,v in result.items():print(m,'lnL',v['lnL'],'np',v['np'],'rate multipliers',v['rates'])
print('Wrote model_fits.tsv, LRT_comparisons.tsv, relative_rates.tsv.')
print('Check M2_stem_included/baseml.out for standard errors, numerical warnings and convergence.')
