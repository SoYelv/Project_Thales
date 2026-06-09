# Segment Data Exploration

Generated at UTC: 2026-06-01T01:49:14+00:00

## Proposal-Implied Data Requirements

The proposal needs a derivative-availability shock that can be linked to pre-existing firm exposure. The segment data is most useful if it supports:

1. segment operating performance, especially `ops / sales`, to estimate the pre-period moderator alpha;
2. segment investment or resources, especially `capxs`, `ias`, `ppents`, or `emps`, for internal capital allocation and information granularity outcomes;
3. a credible exposure proxy before the derivative launch, such as geography/currency or segment industry.

## Source Inventory

- Source file: `data/raw/segment_data.csv`
- Rows: 2,843,285
- Firms: 30,000
- Firm-years: 364,006
- Date range: 1976-2026
- SHA-256: `fe409fa34ee2c108587716d525814509a24ac9dcbdcf87fd47c3e917db82e5d4`

## Segment Type Coverage

| stype  | rows      | firms  | firm_years | min_year | max_year | unique_segment_names | unique_source_currencies |
| ------ | --------- | ------ | ---------- | -------- | -------- | -------------------- | ------------------------ |
| GEOSEG | 1,381,895 | 26,300 | 307,470    | 1,976    | 2,026    | 4,182                | 50                       |
| BUSSEG | 1,276,288 | 29,843 | 352,429    | 1,976    | 2,026    | 69,507               | 49                       |
| OPSEG  | 180,091   | 1,544  | 13,650     | 1,996    | 2,026    | 10,622               | 38                       |
| STSEG  | 5,011     | 73     | 432        | 1,997    | 2,025    | 301                  | 1                        |

## Key Variable Coverage

| stype  | rows      | sales_nonmissing_pct | ops_nonmissing_pct | capxs_nonmissing_pct | ias_nonmissing_pct | emps_nonmissing_pct | rds_nonmissing_pct | ppents_nonmissing_pct | alpha_ready_sales_ops_pct | allocation_ready_sales_ops_capxs_pct | full_ready_sales_ops_capxs_ias_pct |
| ------ | --------- | -------------------- | ------------------ | -------------------- | ------------------ | ------------------- | ------------------ | --------------------- | ------------------------- | ------------------------------------ | ---------------------------------- |
| GEOSEG | 1,381,895 | 94.90                | 25.10              | 19.10                | 31.40              | 22.20               | 6.20               | 21.80                 | 25.10                     | 15.70                                | 15.20                              |
| BUSSEG | 1,276,288 | 99.30                | 79.60              | 76.00                | 85.80              | 39.20               | 25.50              | 25.90                 | 79.60                     | 66.70                                | 64.40                              |
| OPSEG  | 180,091   | 98.50                | 66.50              | 65.70                | 74.70              | 16.80               | 9.90               | 8.10                  | 66.30                     | 47.70                                | 40.00                              |
| STSEG  | 5,011     | 98.80                | 56.30              | 64.20                | 70.40              | 5.40                | 40.80              | 0.10                  | 56.30                     | 36.70                                | 30.10                              |

## Reporting Granularity

| stype  | firm_years | mean_segment_rows | median_segment_rows | p75_segment_rows | p90_segment_rows | share_multi_segment |
| ------ | ---------- | ----------------- | ------------------- | ---------------- | ---------------- | ------------------- |
| BUSSEG | 352,429    | 3.62              | 3.00                | 3.00             | 9.00             | 64.00               |
| GEOSEG | 307,470    | 4.49              | 2.00                | 4.00             | 11.00            | 94.50               |
| OPSEG  | 13,650     | 13.19             | 12.00               | 18.00            | 22.00            | 99.90               |
| STSEG  | 432        | 11.60             | 12.00               | 15.00            | 18.00            | 99.80               |

## Duplicate Key Check

Using `gvkey`, `datadate`, `stype`, and `sid` as a provisional key produces duplicate keys, so future cleaning should not assume this is a unique identifier without additional segment-name or source-date logic.

| stype  | duplicate_keys | duplicate_rows | max_rows_per_key |
| ------ | -------------- | -------------- | ---------------- |
| GEOSEG | 344,400        | 969,093        | 3                |
| BUSSEG | 335,851        | 937,955        | 3                |
| OPSEG  | 58,251         | 158,642        | 3                |
| STSEG  | 1,579          | 4,259          | 3                |

Keeping the latest `srcdate` per provisional key gives the following de-duplicated row counts:

| stype  | raw_rows  | latest_srcdate_rows | dropped_rows | dropped_pct |
| ------ | --------- | ------------------- | ------------ | ----------- |
| GEOSEG | 1,381,895 | 757,202             | 624,693      | 45.20       |
| BUSSEG | 1,276,288 | 674,184             | 602,104      | 47.20       |
| OPSEG  | 180,091   | 79,700              | 100,391      | 55.70       |
| STSEG  | 5,011     | 2,331               | 2,680        | 53.50       |

Latest-source-date key variable coverage:

| stype  | rows    | sales_nonmissing_pct | ops_nonmissing_pct | capxs_nonmissing_pct | ias_nonmissing_pct | emps_nonmissing_pct | rds_nonmissing_pct | ppents_nonmissing_pct | alpha_ready_sales_ops_pct | allocation_ready_sales_ops_capxs_pct | full_ready_sales_ops_capxs_ias_pct |
| ------ | ------- | -------------------- | ------------------ | -------------------- | ------------------ | ------------------- | ------------------ | --------------------- | ------------------------- | ------------------------------------ | ---------------------------------- |
| GEOSEG | 757,202 | 94.20                | 25.40              | 15.10                | 29.60              | 15.40               | 4.50               | 15.20                 | 25.30                     | 12.60                                | 12.20                              |
| BUSSEG | 674,184 | 99.00                | 83.00              | 77.70                | 86.00              | 40.20               | 25.20              | 19.10                 | 82.90                     | 70.50                                | 68.20                              |
| OPSEG  | 79,700  | 96.90                | 65.20              | 63.30                | 69.90              | 15.40               | 9.50               | 7.20                  | 65.10                     | 45.90                                | 37.50                              |
| STSEG  | 2,331   | 98.20                | 56.10              | 61.90                | 67.40              | 5.00                | 36.40              | 0.10                  | 56.10                     | 35.00                                | 26.90                              |

## Geography/Currency Readiness

Geographic segment rows are abundant, but operating variables are thin. This makes geography useful for identifying foreign exposure or segment granularity, but weaker as the main source for alpha or internal capital allocation tests.

Top geographic segment names:

| segment_name   | rows    |
| -------------- | ------- |
| United States  | 314,433 |
|                | 306,839 |
| Europe         | 54,765  |
| Canada         | 48,610  |
| Other          | 35,615  |
| United Kingdom | 27,389  |
| North America  | 25,930  |
| China          | 22,818  |
| International  | 20,147  |
| Japan          | 19,924  |
| Asia           | 17,941  |
| Germany        | 17,632  |
| Domestic       | 15,167  |
| Asia Pacific   | 14,389  |
| Mexico         | 12,113  |
| Foreign        | 11,533  |
| Americas       | 11,428  |
| France         | 10,341  |
| Australia      | 10,205  |
| Other Foreign  | 9,592   |

Top source currencies in geographic rows:

| source_currency | rows      |
| --------------- | --------- |
|                 | 1,243,687 |
| EUR             | 40,065    |
| CAD             | 17,253    |
| CNY             | 12,136    |
| GBP             | 11,102    |
| JPY             | 9,457     |
| SEK             | 6,482     |
| BRL             | 4,381     |
| MXN             | 3,520     |
| NOK             | 3,507     |
| AUD             | 3,325     |
| CHF             | 2,655     |
| CLP             | 2,461     |
| KRW             | 2,281     |
| HKD             | 2,265     |
| TWD             | 2,086     |
| USD             | 2,014     |
| INR             | 1,766     |
| ZAR             | 1,661     |
| ARS             | 1,265     |

## Industry Shock Proxy Coverage

Business and operating segments have much better operating-performance and investment fields. SIC-based industry proxies are therefore the stronger match for the proposal's alpha and capital-allocation tests.

| shock_family_proxy    | rows      | firms  | firm_years | min_year | max_year | sales_nonmissing_pct | ops_nonmissing_pct | capxs_nonmissing_pct | ias_nonmissing_pct |
| --------------------- | --------- | ------ | ---------- | -------- | -------- | -------------------- | ------------------ | -------------------- | ------------------ |
| Other industries      | 1,182,414 | 26,873 | 313,019    | 1,976    | 2,026    | 99.20                | 77.20              | 72.20                | 83.70              |
| Utilities and power   | 67,685    | 1,150  | 17,009     | 1,976    | 2,025    | 99.20                | 75.60              | 86.70                | 88.60              |
| Metals and mining     | 63,838    | 1,766  | 18,181     | 1,976    | 2,026    | 98.60                | 81.50              | 87.70                | 88.70              |
| Oil/gas and petroleum | 63,171    | 2,109  | 21,751     | 1,976    | 2,025    | 99.20                | 82.80              | 90.50                | 90.80              |
| Transport and freight | 39,799    | 1,237  | 12,501     | 1,976    | 2,025    | 99.20                | 85.70              | 79.10                | 86.20              |
| Agriculture and food  | 39,472    | 1,173  | 12,050     | 1,976    | 2,026    | 99.00                | 84.90              | 77.60                | 79.70              |

The same coverage after keeping only the latest `srcdate` per provisional segment key:

| shock_family_proxy    | rows    | firms  | firm_years | min_year | max_year | sales_nonmissing_pct | ops_nonmissing_pct | capxs_nonmissing_pct | ias_nonmissing_pct |
| --------------------- | ------- | ------ | ---------- | -------- | -------- | -------------------- | ------------------ | -------------------- | ------------------ |
| Other industries      | 612,527 | 26,868 | 312,840    | 1,976    | 2,026    | 98.80                | 80.50              | 74.00                | 83.70              |
| Oil/gas and petroleum | 34,307  | 2,108  | 21,722     | 1,976    | 2,025    | 99.00                | 86.00              | 90.40                | 90.90              |
| Utilities and power   | 33,185  | 1,145  | 16,965     | 1,976    | 2,025    | 98.50                | 78.40              | 87.00                | 87.80              |
| Metals and mining     | 32,630  | 1,763  | 18,115     | 1,976    | 2,026    | 97.60                | 83.60              | 86.90                | 88.10              |
| Agriculture and food  | 21,082  | 1,171  | 12,008     | 1,976    | 2,026    | 98.60                | 86.90              | 78.80                | 80.30              |
| Transport and freight | 20,153  | 1,234  | 12,456     | 1,976    | 2,025    | 98.70                | 87.20              | 80.10                | 86.30              |

## Candidate Shock Window Readiness

The table below is a mechanical coverage check, not a causal design. It asks whether the current segment file has enough observations around plausible derivative-availability windows for the affected segment industries.

| event               | proxy_groups                               | window         | start_year | end_year | rows   | firms | firm_years | alpha_ready_sales_ops_pct | allocation_ready_sales_ops_capxs_pct |
| ------------------- | ------------------------------------------ | -------------- | ---------- | -------- | ------ | ----- | ---------- | ------------------------- | ------------------------------------ |
| crude_oil_1983      | Oil/gas and petroleum                      | minus5_plus5   | 1,978      | 1,988    | 8,110  | 1,149 | 6,617      | 98.90                     | 94.90                                |
| crude_oil_1983      | Oil/gas and petroleum                      | minus10_minus1 | 1,973      | 1,982    | 4,171  | 841   | 3,289      | 96.60                     | 88.00                                |
| crude_oil_1983      | Oil/gas and petroleum                      | plus1_plus10   | 1,984      | 1,993    | 6,760  | 1,064 | 5,603      | 98.70                     | 95.20                                |
| natural_gas_1990    | Oil/gas and petroleum; Utilities and power | minus5_plus5   | 1,985      | 1,995    | 12,234 | 1,474 | 9,213      | 98.90                     | 96.00                                |
| natural_gas_1990    | Oil/gas and petroleum; Utilities and power | minus10_minus1 | 1,980      | 1,989    | 11,841 | 1,500 | 8,830      | 99.20                     | 96.20                                |
| natural_gas_1990    | Oil/gas and petroleum; Utilities and power | plus1_plus10   | 1,991      | 2,000    | 17,912 | 1,277 | 7,723      | 86.50                     | 80.10                                |
| weather_1997_1999   | Utilities and power; Agriculture and food  | minus5_plus5   | 1,993      | 2,003    | 24,239 | 1,202 | 7,220      | 79.80                     | 71.30                                |
| weather_1997_1999   | Utilities and power; Agriculture and food  | minus10_minus1 | 1,988      | 1,997    | 8,218  | 1,057 | 6,369      | 99.10                     | 95.60                                |
| weather_1997_1999   | Utilities and power; Agriculture and food  | plus1_plus10   | 1,999      | 2,008    | 35,852 | 1,011 | 6,304      | 72.60                     | 63.70                                |
| freight_derivatives | Transport and freight                      | minus5_plus5   | 1,987      | 1,997    | 3,287  | 510   | 2,850      | 98.70                     | 94.30                                |
| freight_derivatives | Transport and freight                      | minus10_minus1 | 1,982      | 1,991    | 2,937  | 515   | 2,575      | 99.00                     | 93.70                                |
| freight_derivatives | Transport and freight                      | plus1_plus10   | 1,993      | 2,002    | 7,020  | 492   | 2,670      | 88.00                     | 77.30                                |

Latest-source-date de-duplicated version:

| event               | proxy_groups                               | window         | start_year | end_year | rows   | firms | firm_years | alpha_ready_sales_ops_pct | allocation_ready_sales_ops_capxs_pct |
| ------------------- | ------------------------------------------ | -------------- | ---------- | -------- | ------ | ----- | ---------- | ------------------------- | ------------------------------------ |
| crude_oil_1983      | Oil/gas and petroleum                      | minus5_plus5   | 1,978      | 1,988    | 8,110  | 1,149 | 6,617      | 98.90                     | 94.90                                |
| crude_oil_1983      | Oil/gas and petroleum                      | minus10_minus1 | 1,973      | 1,982    | 4,171  | 841   | 3,289      | 96.60                     | 88.00                                |
| crude_oil_1983      | Oil/gas and petroleum                      | plus1_plus10   | 1,984      | 1,993    | 6,752  | 1,064 | 5,603      | 98.70                     | 95.20                                |
| natural_gas_1990    | Oil/gas and petroleum; Utilities and power | minus5_plus5   | 1,985      | 1,995    | 12,206 | 1,474 | 9,213      | 98.90                     | 96.00                                |
| natural_gas_1990    | Oil/gas and petroleum; Utilities and power | minus10_minus1 | 1,980      | 1,989    | 11,841 | 1,500 | 8,830      | 99.20                     | 96.20                                |
| natural_gas_1990    | Oil/gas and petroleum; Utilities and power | plus1_plus10   | 1,991      | 2,000    | 12,332 | 1,276 | 7,718      | 90.20                     | 84.30                                |
| weather_1997_1999   | Utilities and power; Agriculture and food  | minus5_plus5   | 1,993      | 2,003    | 12,952 | 1,196 | 7,191      | 83.00                     | 74.90                                |
| weather_1997_1999   | Utilities and power; Agriculture and food  | minus10_minus1 | 1,988      | 1,997    | 8,128  | 1,057 | 6,369      | 99.10                     | 95.60                                |
| weather_1997_1999   | Utilities and power; Agriculture and food  | plus1_plus10   | 1,999      | 2,008    | 14,715 | 1,005 | 6,273      | 71.90                     | 62.00                                |
| freight_derivatives | Transport and freight                      | minus5_plus5   | 1,987      | 1,997    | 3,262  | 510   | 2,850      | 98.70                     | 94.40                                |
| freight_derivatives | Transport and freight                      | minus10_minus1 | 1,982      | 1,991    | 2,937  | 515   | 2,575      | 99.00                     | 93.70                                |
| freight_derivatives | Transport and freight                      | plus1_plus10   | 1,993      | 2,002    | 3,879  | 491   | 2,661      | 89.50                     | 80.00                                |

## Bottom Line

Based on this file alone, commodity/energy derivative shocks are the best-supported starting point. Business and operating segments provide enough sales, operating profit, assets, and capex coverage to estimate segment operating margins and internal capital allocation around energy-related launch windows. Currency shocks are conceptually closest to the motivating example, and the file has many geographic rows, but the key operating variables in `GEOSEG` are too sparse for alpha and allocation tests without another data source or substantial text parsing. Weather shocks are attractive theoretically because prior work exists, but this file has very limited state-level segment data and country/region geography is too coarse for clean weather exposure. Freight is feasible only as a narrow robustness or extension because transport/freight segments are identifiable but much smaller.

Recommended next empirical path:

1. Start with oil/gas and energy derivative availability as the primary shock family.
2. Use `BUSSEG` and `OPSEG` to construct segment operating margin and segment capex/investment outcomes.
3. Treat `GEOSEG` as a secondary source for foreign-exposure controls or reporting-granularity outcomes, not as the primary alpha dataset.
4. Build the next script around a firm-segment-year panel with clean keys, segment exclusions for corporate/eliminations/other, winsorized operating margins, and SIC/NAICS exposure groups.
