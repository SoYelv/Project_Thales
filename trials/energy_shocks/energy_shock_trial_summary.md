# Energy Shock Trial Summary

This is a trial-only screening output. It should not be cited as a production result without a separate identification memo and source validation.

## Scope

- Oil: WTI 1983 derivative-availability shock.
- Gas: NATGAS 1990 derivative-availability shock plus FERC 636 1992 restructuring check.
- Carbon: RGGI 2009 and California 2013 regional cap-and-trade proxies; these are exploratory because plant emissions and allowance holdings are not observed.

## Robustness Gate

A grouped candidate is flagged only when at least 3 specs have p<0.05, at least 80% of coefficients share the same sign, median |t| is at least 1.8, and minimum treated/control firm counts clear 20/50.

- Estimated specs: 1,278
- Successful specs: 1,203
- Failed/skipped specs: 75

## Robust Candidates

- `rsz` `FERC636_1992` `pre_energy_any` outcome=`rel_inv`, opp=l_margin: n_p05=6/6, median_beta=-0.0317, median_t=-2.53, sign_consistency=1.00, min treated/control firms=341/1651.
- `rsz` `FERC636_1992` `pre_gas_any` outcome=`rel_inv`, opp=l_margin: n_p05=4/6, median_beta=-0.0321, median_t=-2.36, sign_consistency=1.00, min treated/control firms=112/1880.
- `rsz` `GAS_SPIKE_2001` `energy_segment` outcome=`rel_inv`, opp=l_margin: n_p05=4/6, median_beta=-0.0257, median_t=-2.27, sign_consistency=1.00, min treated/control firms=376/3244.
- `rsz` `SO2_ALLOWANCE_1995` `pre_electric_any` outcome=`rel_inv`, opp=l_margin: n_p05=4/6, median_beta=+0.0388, median_t=+2.13, sign_consistency=1.00, min treated/control firms=142/1925.
- `rsz` `NATGAS_1990` `pre_energy_any` outcome=`rel_inv`, opp=sgrow: n_p05=4/6, median_beta=+0.0223, median_t=+2.10, sign_consistency=1.00, min treated/control firms=371/1803.

## Top Screened Groups

- PASS: `rsz` `FERC636_1992` `pre_energy_any` outcome=`rel_inv`, opp=l_margin; p<.05 6/6, median_t=-2.53, median_beta=-0.0317.
- PASS: `rsz` `FERC636_1992` `pre_gas_any` outcome=`rel_inv`, opp=l_margin; p<.05 4/6, median_t=-2.36, median_beta=-0.0321.
- PASS: `rsz` `GAS_SPIKE_2001` `energy_segment` outcome=`rel_inv`, opp=l_margin; p<.05 4/6, median_t=-2.27, median_beta=-0.0257.
- PASS: `rsz` `SO2_ALLOWANCE_1995` `pre_electric_any` outcome=`rel_inv`, opp=l_margin; p<.05 4/6, median_t=+2.13, median_beta=+0.0388.
- PASS: `rsz` `NATGAS_1990` `pre_energy_any` outcome=`rel_inv`, opp=sgrow; p<.05 4/6, median_t=+2.10, median_beta=+0.0223.
- screen: `rsz` `CA_CARBON_2013` `pre_electric_any` outcome=`rel_inv`, opp=l_margin; p<.05 6/6, median_t=+40.83, median_beta=+5.6710.
- screen: `rsz` `CA_CARBON_2013` `pre_electric_any` outcome=`rel_inv`, opp=sgrow; p<.05 6/6, median_t=+19.64, median_beta=+2.3294.
- screen: `rsz` `CA_CARBON_2013` `pre_energy_any` outcome=`rel_inv`, opp=l_margin; p<.05 6/6, median_t=+2.12, median_beta=+3.4920.
- screen: `firm_did` `GAS_SPIKE_2001` `pre_energy_any` outcome=`multi_seg`; p<.05 3/3, median_t=-5.48, median_beta=-0.0855.
- screen: `firm_did` `GAS_SPIKE_2001` `pre_oilgas_any` outcome=`multi_seg`; p<.05 3/3, median_t=-6.84, median_beta=-0.1193.
- screen: `firm_did` `NATGAS_1990` `pre_energy_share_z` outcome=`hhi`; p<.05 3/3, median_t=-6.05, median_beta=-0.0112.
- screen: `firm_did` `FERC636_1992` `pre_energy_share_z` outcome=`hhi`; p<.05 3/3, median_t=-4.89, median_beta=-0.0086.
- screen: `firm_did` `SO2_ALLOWANCE_1995` `pre_carbon_any` outcome=`multi_seg`; p<.05 3/3, median_t=-4.64, median_beta=-0.0399.
- screen: `firm_did` `GAS_SPIKE_2001` `pre_oilgas_any` outcome=`log_nseg`; p<.05 3/3, median_t=-4.28, median_beta=-0.0657.
- screen: `firm_did` `GAS_SPIKE_2001` `pre_energy_share_z` outcome=`multi_seg`; p<.05 3/3, median_t=-4.25, median_beta=-0.0169.

## Identification Notes

- WTI 1983 and NATGAS 1990 are the cleanest derivative-availability candidates in this trial.
- FERC 636 is a gas-market structure shock, so it should be interpreted separately from derivative contract availability.
- Carbon results require extra validation before use: firm exposure is based on HQ state plus high-carbon segment SIC, not facility emissions.
- Significant trial results should be re-estimated after freezing a single pre-specified sample and writing an identification memo.

## Candidate Drilldown

- FAIL: `FERC636_1992` `pre_energy_any` opp=`l_margin`; pre p<.10=1, placebo p<.10=0, leave-one p<.05=8/11, leave-one sign consistency=1.00.
- FAIL: `FERC636_1992` `pre_gas_any` opp=`l_margin`; pre p<.10=1, placebo p<.10=0, leave-one p<.05=10/11, leave-one sign consistency=1.00.
- FAIL: `GAS_SPIKE_2001` `energy_segment` opp=`l_margin`; pre p<.10=0, placebo p<.10=1, leave-one p<.05=9/11, leave-one sign consistency=1.00.
- FAIL: `NATGAS_1990` `pre_energy_any` opp=`sgrow`; pre p<.10=0, placebo p<.10=1, leave-one p<.05=5/11, leave-one sign consistency=1.00.
- FAIL: `SO2_ALLOWANCE_1995` `pre_electric_any` opp=`l_margin`; pre p<.10=2, placebo p<.10=2, leave-one p<.05=5/11, leave-one sign consistency=1.00.

## Firm-Year Drilldown

- FAIL: `EU_ETS_2005` `pre_energy_any` outcome=`log_nseg`; baseline p<.05=3/3, pre p<.10=4, placebo p<.10=3, leave-one p<.05=11/11.
- FAIL: `EU_ETS_2005` `pre_energy_any` outcome=`multi_seg`; baseline p<.05=3/3, pre p<.10=4, placebo p<.10=3, leave-one p<.05=11/11.
- FAIL: `FERC636_1992` `pre_energy_share_z` outcome=`hhi`; baseline p<.05=3/3, pre p<.10=4, placebo p<.10=3, leave-one p<.05=11/11.
- FAIL: `FERC636_1992` `pre_energy_share_z` outcome=`n_op_seg`; baseline p<.05=3/3, pre p<.10=1, placebo p<.10=3, leave-one p<.05=11/11.
- FAIL: `GAS_SPIKE_2001` `pre_energy_any` outcome=`multi_seg`; baseline p<.05=3/3, pre p<.10=4, placebo p<.10=2, leave-one p<.05=11/11.
- FAIL: `GAS_SPIKE_2001` `pre_energy_share_z` outcome=`multi_seg`; baseline p<.05=3/3, pre p<.10=3, placebo p<.10=1, leave-one p<.05=11/11.
- FAIL: `NATGAS_1990` `pre_energy_share_z` outcome=`hhi`; baseline p<.05=3/3, pre p<.10=2, placebo p<.10=2, leave-one p<.05=11/11.
- FAIL: `NATGAS_1990` `pre_energy_share_z` outcome=`log_nseg`; baseline p<.05=3/3, pre p<.10=3, placebo p<.10=3, leave-one p<.05=11/11.
- FAIL: `NATGAS_1990` `pre_energy_share_z` outcome=`n_op_seg`; baseline p<.05=3/3, pre p<.10=3, placebo p<.10=3, leave-one p<.05=11/11.
- FAIL: `OIL_COLLAPSE_1986` `pre_oilgas_share_z` outcome=`hhi`; baseline p<.05=3/3, pre p<.10=4, placebo p<.10=0, leave-one p<.05=11/11.
- FAIL: `OIL_COLLAPSE_1986` `pre_oilgas_share_z` outcome=`log_nseg`; baseline p<.05=3/3, pre p<.10=4, placebo p<.10=0, leave-one p<.05=11/11.
- FAIL: `OIL_COLLAPSE_1986` `pre_oilgas_share_z` outcome=`n_op_seg`; baseline p<.05=3/3, pre p<.10=4, placebo p<.10=0, leave-one p<.05=11/11.

## Trend-Adjusted Checks

- FAIL: `firm_did_trend` `GAS_SPIKE_2001` `pre_energy_share_z` outcome=`multi_seg`; p<.05=0/3, median_beta=+0.0006, median_t=+0.19.
- PASS: `firm_did_trend` `OIL_COLLAPSE_1986` `pre_oilgas_share_z` outcome=`hhi`; p<.05=3/3, median_beta=-0.0077, median_t=-2.85.
- FAIL: `firm_did_trend` `OIL_COLLAPSE_1986` `pre_oilgas_share_z` outcome=`log_nseg`; p<.05=1/3, median_beta=+0.0046, median_t=+1.69.
- PASS: `firm_did_trend` `OIL_COLLAPSE_1986` `pre_oilgas_share_z` outcome=`n_op_seg`; p<.05=3/3, median_beta=+0.0190, median_t=+2.52.
- FAIL: `rsz_trend` `FERC636_1992` `pre_energy_any` outcome=`rel_inv`, opp=`l_margin`; p<.05=1/3, median_beta=-0.0363, median_t=-1.83.
- PASS: `rsz_trend` `FERC636_1992` `pre_gas_any` outcome=`rel_inv`, opp=`l_margin`; p<.05=3/3, median_beta=-0.0599, median_t=-2.42.
- FAIL: `rsz_trend` `GAS_SPIKE_2001` `energy_segment` outcome=`rel_inv`, opp=`l_margin`; p<.05=0/3, median_beta=-0.0125, median_t=-0.78.
