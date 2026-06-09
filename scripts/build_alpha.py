#!/usr/bin/env python3
"""Construct firm-level alpha moderators (pre-event), per Delv3-2.pdf sec 4.2.

alpha = extent to which exposure is informative about operations. Proxies:
  a_intensity : pre-event electric/energy segment sales share (operations
                determined by exposure -> high alpha)
  a_vol       : pre-event within-firm std of ROA (operations more sensitive to
                hedgeable shocks -> high alpha)
  a_segvol    : pre-event within-firm std of segment operating margin
  a_pricebeta : |slope| of pre-event firm ROA on energy price index (the
                paper's preferred operating-sensitivity measure)

Output: reports/panel/alpha.parquet  (gvkey, event, alpha proxies)
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "reports" / "panel"
reg = pd.read_parquet(P / "regdata.parquet")
funda = pd.read_parquet(P / "funda.parquet")
seg = pd.read_parquet(P / "seg_busseg.parquet")

# --- energy price index (annual, nominal) for operating-sensitivity alpha ---
# WTI crude ($/bbl) and Henry Hub / wellhead natural gas ($/mcf), public annual
# averages (EIA). Used only to compute a pre-event operating beta.
wti = {1976:13.1,1977:14.4,1978:14.9,1979:25.1,1980:37.4,1981:36.7,1982:33.6,
       1983:30.4,1984:29.4,1985:27.1,1986:14.4,1987:18.4,1988:15.0,1989:18.2,
       1990:23.8,1991:20.0,1992:19.3,1993:17.0,1994:15.7,1995:17.2,1996:20.6,
       1997:18.6,1998:11.9,1999:16.6,2000:27.4,2001:23.0,2002:22.8,2003:27.6,
       2004:36.8,2005:50.0}
gas = {1976:0.58,1977:0.79,1978:0.91,1979:1.18,1980:1.59,1981:1.98,1982:2.46,
       1983:2.59,1984:2.66,1985:2.51,1986:1.94,1987:1.67,1988:1.69,1989:1.69,
       1990:1.71,1991:1.64,1992:1.74,1993:2.04,1994:1.85,1995:1.55,1996:2.17,
       1997:2.32,1998:1.96,1999:2.19,2000:4.31,2001:4.00,2002:2.95,2003:4.88,
       2004:5.46,2005:7.51}
# fossil fuel composite (drives electric utility operating cost) = avg of std'd wti & gas
pr = pd.DataFrame({"year":list(wti), "wti":[wti[y] for y in wti],
                   "gas":[gas[y] for y in wti]})
pr["fuel"] = ((pr.wti-pr.wti.mean())/pr.wti.std() + (pr.gas-pr.gas.mean())/pr.gas.std())/2

funda = funda.rename(columns={"fyear":"year"}).dropna(subset=["year"])
funda["year"]=funda["year"].astype(int)
funda["roa"]=funda["oibdp"]/funda["at"]
funda = funda.merge(pr[["year","fuel"]],on="year",how="left")

def build(event, pre_lo, pre_hi):
    # intensity from regdata
    sub = reg[(reg.year>=pre_lo)&(reg.year<=pre_hi)]
    intens = sub.groupby("gvkey").agg(
        a_share_elec=("share_electric","mean"),
        a_share_energy=("share_energy","mean")).reset_index()
    # roa volatility + price beta from funda
    f = funda[(funda.year>=pre_lo)&(funda.year<=pre_hi)].copy()
    f["roa"]=f["roa"].replace([np.inf,-np.inf],np.nan)
    def beta(g):
        g=g.dropna(subset=["roa","fuel"])
        if g.year.nunique()<4 or g.fuel.std()==0: return np.nan
        return np.polyfit(g.fuel,g.roa,1)[0]
    vol = f.groupby("gvkey").agg(a_vol=("roa",lambda x: x.std())).reset_index()
    pb = f.groupby("gvkey").apply(beta,include_groups=False).rename("a_pricebeta").reset_index()
    pb["a_pricebeta"]=pb["a_pricebeta"].abs()
    # segment op margin volatility
    s = seg[(seg.year>=pre_lo)&(seg.year<=pre_hi)&(seg.is_op==1)].copy()
    s["m"]=s["op_margin"].replace([np.inf,-np.inf],np.nan).clip(-2,2)
    segvol = s.groupby("gvkey").agg(a_segvol=("m",lambda x:x.std())).reset_index()
    out = intens.merge(vol,on="gvkey",how="outer").merge(pb,on="gvkey",how="outer").merge(segvol,on="gvkey",how="outer")
    out["event"]=event
    return out

alpha = pd.concat([
    build("ELEC1996",1990,1995),
    build("NG1990",1985,1989),
    build("WTI1983",1978,1982),
], ignore_index=True)
alpha.to_parquet(P/"alpha.parquet",index=False)
print("alpha rows:",len(alpha))
print(alpha.groupby("event")[["a_share_elec","a_share_energy","a_vol","a_pricebeta","a_segvol"]].describe().T.round(3).to_string())
