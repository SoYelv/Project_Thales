#!/usr/bin/env python3
"""Matrix of (treatment x shock) for the internal-capital-allocation (RSZ) test.
Escalates from narrow power-producer treatment to the BOLD design: the entire
multi-segment universe with continuous electricity-INPUT intensity as treatment.

Outcome  = segment investment (capx/lagged assets), within-firm-year demeaned.
Key term = rel_opp x TREAT x post  (allocation-to-profitability sensitivity).
Prediction: after electricity becomes hedgeable, electricity-exposed firms
allocate more to high-margin segments -> positive.
"""
from __future__ import annotations
import warnings
from pathlib import Path
import numpy as np, pandas as pd
from linearmodels.panel import PanelOLS
warnings.filterwarnings("ignore")
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/"reports"/"panel"
g=pd.read_parquet(P/"seg_invest2.parquet")
fe=pd.read_parquet(P/"firm_event.parquet").drop_duplicates("gvkey")

g["inv_la"]=g["inv_la"].replace([np.inf,-np.inf],np.nan)
g["l_margin"]=g["l_margin"].replace([np.inf,-np.inf],np.nan)
g["sgrow"]=g["sgrow"].replace([np.inf,-np.inf],np.nan)
g=g.merge(fe[["gvkey","region","event_year"]],on="gvkey",how="left")
g=g[g.n_seg_fy>=2].copy()                    # multi-segment universe

def zc(s):
    s=s.replace([np.inf,-np.inf],np.nan); return (s-s.mean())/s.std()
g["fint_z"]=zc(g["firm_elec_int"])
g["sint_z"]=zc(g["elec_int"])

def relmeasures(d,opp):
    d=d.dropna(subset=["inv_la",opp]).copy()
    for c in ["inv_la",opp]:
        d[c]=d[c].clip(d[c].quantile(.01),d[c].quantile(.99))
    d["rel_inv"]=d["inv_la"]-d.groupby(["cohort","gvkey","year"])["inv_la"].transform("mean")
    d["rel_opp"]=d[opp]-d.groupby(["cohort","gvkey","year"])[opp].transform("mean")
    return d

def fit(d,keyterms,label):
    d=d.copy()
    cy=pd.get_dummies(d["cohort"].astype(str)+"_"+d["year"].astype(str),prefix="cy",drop_first=True).astype(float)
    d["cseg"]=d["cohort"].astype(str)+"_"+d["gvkey"]+"_"+d["snms_u"]
    idx=pd.MultiIndex.from_arrays([d["cseg"].values,d["year"].values])
    X=pd.concat([d[list(keyterms)].reset_index(drop=True),cy.reset_index(drop=True)],axis=1); X.index=idx
    y=pd.Series(d["rel_inv"].values,index=idx); cl=pd.DataFrame({"f":d["gvkey"].values},index=idx)
    r=PanelOLS(y,X,entity_effects=True,check_rank=False,drop_absorbed=True).fit(cov_type="clustered",clusters=cl)
    kk=keyterms[0]
    return r.params[kk],r.std_errors[kk],r.tstats[kk],r.pvalues[kk],int(r.nobs),d.gvkey.nunique()

# ---- shock builders: return df with cohort, treat/intensity, post ----
def national1996(df,treatcol):
    d=df[(df.year>=1991)&(df.year<=2001)].copy(); d["cohort"]=0; d["post"]=(d.year>=1996).astype(int)
    d["T"]=df.loc[d.index,treatcol].values
    return d
def strict_staggered(df,treatcol):
    """Strict regional stacked design using firm_event.event_year.

    For dose treatments, the dose is switched on only for firms in the cohort's
    treated hub-state group; not-yet and never-treated firms carry dose 0.
    """
    parts=[]
    for Tn in [1996,1998,1999]:
        eligible=df.event_year.gt(Tn)|df.event_year.isna()|df.event_year.eq(Tn)
        c=df[(df.year>=Tn-5)&(df.year<=Tn+5)&eligible].copy()
        c["cohort"]=Tn
        c["post"]=(c.year>=Tn).astype(int)
        c["regional_treat"]=c.event_year.eq(Tn).astype(int)
        c["T"]=c[treatcol]*c["regional_treat"]
        parts.append(c)
    return pd.concat(parts,ignore_index=False)

def run(treat_name,treatcol,binary,shock):
    df=g.copy()
    if binary:
        df["TR"]=df[treatcol].astype(int)
    else:
        df["TR"]=df[treatcol]
    build=national1996 if shock=="nat1996" else strict_staggered
    d=build(df,"TR")
    for opp in ["l_margin","sgrow"]:
        dd=relmeasures(d,opp)
        dd["ro"]=dd["rel_opp"]; dd["rop"]=dd.ro*dd.post; dd["roT"]=dd.ro*dd["T"]; dd["roTp"]=dd.ro*dd["T"]*dd.post
        b,se,t,p,N,nf=fit(dd,["roTp","rop","roT","ro"],treat_name)
        tag="margin" if opp=="l_margin" else "salesgrow"
        print(f"  {treat_name:34s} x {shock:9s} [{tag:9s}]  rel_opp*T*post={b:+.4f} (t={t:+.2f}, p={p:.3f}) N={N:,} firms={nf}")

# firm electricity-intensity treatments
g["t_high"]=(g["firm_elec_int"]>=3).astype(int)         # high-intensity firms (consumers+producers)
g["t_vhigh"]=(g["firm_elec_int"]>=6).astype(int)
g["t_elec"]=g["elec"].fillna(0).astype(int)             # power-producer segment
g["t_energy"]=g["energy"].fillna(0).astype(int)

print("="*100)
print("CAPITAL-ALLOCATION (RSZ) MATRIX: treatment x shock  | key = rel_opp x TREAT x post (>0 predicted)")
print("="*100)
print("\n-- A) narrow: electric power producers --")
run("A elec producer (binary)","t_elec",True,"nat1996")
run("A elec producer (binary)","t_elec",True,"strict_staggered")
print("\n-- B) energy producers --")
run("B energy producer (binary)","t_energy",True,"nat1996")
print("\n-- C) high electricity-INPUT intensity firms (binary, >=3%) --")
run("C high-elec-input (binary)","t_high",True,"nat1996")
run("C high-elec-input (binary)","t_high",True,"strict_staggered")
run("C vhigh-elec-input (>=6%)","t_vhigh",True,"nat1996")
print("\n-- D) BOLD: entire multi-seg universe, CONTINUOUS firm electricity intensity (z) --")
run("D firm-intensity (cont, z)","fint_z",False,"nat1996")
run("D firm-intensity (cont, z)","fint_z",False,"strict_staggered")
print("\n-- D') BOLD: continuous SEGMENT electricity intensity (within-firm reallocation, z) --")
run("D' seg-intensity (cont, z)","sint_z",False,"nat1996")
run("D' seg-intensity (cont, z)","sint_z",False,"strict_staggered")
