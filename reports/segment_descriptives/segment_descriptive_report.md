# Segment Data Descriptive Tables

This memo is a generated companion to the segment project-space reports. It describes the original segment source file without choosing a research design.

## Source And Units

- Generated at: `2026-06-09T19:26:41+00:00`
- Source file: `data/raw/segment_data.csv`
- Source SHA-256: `fe409fa34ee2c108587716d525814509a24ac9dcbdcf87fd47c3e917db82e5d4`
- Raw rows: `2,843,285`
- Latest-source rows: `1,513,417`
- Latest-source rule: sort rows within `gvkey, datadate, stype, sid` by parsed `srcdate`, then keep the last row.
- Segment types are kept separate because BUSSEG, GEOSEG, and OPSEG are overlapping reporting dimensions rather than mutually exclusive samples.

## Table 1. Source Rows By Segment Type

This table shows how many rows are in the raw file, how many remain after the latest-source rule, and how many older source snapshots are removed.

| stype      | raw_rows  | latest_source_rows | dropped_older_srcdate_rows | dropped_pct_of_raw | latest_firms | latest_firm_years | latest_min_year | latest_max_year | latest_unique_nonblank_segment_names | latest_source_currencies | raw_firms | raw_firm_years |
| ---------- | --------- | ------------------ | -------------------------- | ------------------ | ------------ | ----------------- | --------------- | --------------- | ------------------------------------ | ------------------------ | --------- | -------------- |
| ALL_STYPES | 2,843,285 | 1,513,417          | 1,329,868                  | 46.800             | 30,000       | 364,006           | 1,976           | 2,026           | 76,602                               | 51                       | 30,000    | 364,006        |
| GEOSEG     | 1,381,895 | 757,202            | 624,693                    | 45.200             | 26,300       | 307,470           | 1,976           | 2,026           | 3,990                                | 50                       | 26,300    | 307,470        |
| BUSSEG     | 1,276,288 | 674,184            | 602,104                    | 47.200             | 29,843       | 352,429           | 1,976           | 2,026           | 64,614                               | 49                       | 29,843    | 352,429        |
| OPSEG      | 180,091   | 79,700             | 100,391                    | 55.700             | 1,544        | 13,650            | 1,996           | 2,026           | 10,187                               | 38                       | 1,544     | 13,650         |
| STSEG      | 5,011     | 2,331              | 2,680                      | 53.500             | 73           | 432               | 1,997           | 2,025           | 295                                  | 1                        | 73        | 432            |

## Table 2. Segments Per Firm-Year

The unit is `gvkey + datadate + stype`. The `ALL_STYPES` rows are only an inventory check because segment types overlap.

| stype      | measure               | firm_year_units | mean  | p25   | p50   | p75   | p90   | p95    | max    | share_gt1_pct |
| ---------- | --------------------- | --------------- | ----- | ----- | ----- | ----- | ----- | ------ | ------ | ------------- |
| ALL_STYPES | reported_segment_rows | 364,006         | 4.158 | 3.000 | 3.000 | 5.000 | 8.000 | 10.000 | 67.000 | 89.200        |
| BUSSEG     | reported_segment_rows | 352,429         | 1.913 | 1.000 | 1.000 | 3.000 | 4.000 | 5.000  | 21.000 | 34.300        |
| GEOSEG     | reported_segment_rows | 307,470         | 2.463 | 2.000 | 2.000 | 2.000 | 4.000 | 6.000  | 62.000 | 76.900        |
| OPSEG      | reported_segment_rows | 13,650          | 5.839 | 4.000 | 5.000 | 7.000 | 9.000 | 11.000 | 29.000 | 99.800        |
| STSEG      | reported_segment_rows | 432             | 5.396 | 4.000 | 5.000 | 6.000 | 8.000 | 9.000  | 15.000 | 99.800        |

## Table 3. Segment-Level Variable Distributions

The preview below uses latest-source rows. The full CSV includes raw-source and latest-source views, each segment type, pooled `ALL_STYPES`, raw variables, and derived ratios.

| stype      | variable       | segment_rows | nonmissing_n | missing_pct | mean       | sd         | p25     | p50       | p75       | p95        |
| ---------- | -------------- | ------------ | ------------ | ----------- | ---------- | ---------- | ------- | --------- | --------- | ---------- |
| ALL_STYPES | capx_to_assets | 1,513,417    | 630,001      | 58.400      | 0.076      | 1.530      | 0.007   | 0.032     | 0.077     | 0.235      |
| ALL_STYPES | capxs          | 1,513,417    | 689,497      | 54.400      | 108.170    | 1,062.340  | 0.142   | 2.587     | 24.300    | 386.949    |
| ALL_STYPES | emps           | 1,513,417    | 400,367      | 73.500      | 4,703.811  | 23,704.398 | 51.000  | 330.000   | 2,020.000 | 19,651.400 |
| ALL_STYPES | ias            | 1,513,417    | 861,612      | 43.100      | 4,007.447  | 47,415.588 | 12.135  | 103.621   | 728.900   | 9,351.450  |
| ALL_STYPES | op_margin      | 1,513,417    | 731,309      | 51.700      | -4.730     | 244.662    | -0.003  | 0.078     | 0.179     | 0.530      |
| ALL_STYPES | ops            | 1,513,417    | 804,849      | 46.800      | 139.482    | 1,735.478  | -0.411  | 3.785     | 46.174    | 590.531    |
| ALL_STYPES | rds            | 1,513,417    | 212,007      | 86.000      | 38.997     | 376.476    | 0.000   | 0.197     | 6.305     | 106.000    |
| ALL_STYPES | sales          | 1,513,417    | 1,460,084    | 3.500       | 1,097.786  | 8,874.734  | 3.083   | 48.451    | 378.442   | 4,257.967  |
| BUSSEG     | capx_to_assets | 674,184      | 494,854      | 26.600      | 0.076      | 1.271      | 0.008   | 0.034     | 0.079     | 0.241      |
| BUSSEG     | capxs          | 674,184      | 523,659      | 22.300      | 88.414     | 629.954    | 0.146   | 2.160     | 19.000    | 300.348    |
| BUSSEG     | emps           | 674,184      | 271,135      | 59.800      | 4,114.681  | 20,897.762 | 46.000  | 280.000   | 1,670.000 | 16,476.300 |
| BUSSEG     | ias            | 674,184      | 580,118      | 14.000      | 2,778.432  | 33,687.794 | 10.615  | 82.668    | 578.158   | 7,454.000  |
| BUSSEG     | op_margin      | 674,184      | 510,137      | 24.300      | -5.488     | 279.170    | -0.017  | 0.073     | 0.171     | 0.523      |
| BUSSEG     | ops            | 674,184      | 559,574      | 17.000      | 118.201    | 1,455.238  | -0.714  | 2.725     | 36.089    | 487.000    |
| BUSSEG     | rds            | 674,184      | 169,810      | 74.800      | 45.469     | 408.153    | 0.000   | 0.533     | 8.424     | 128.000    |
| BUSSEG     | sales          | 674,184      | 667,191      | 1.000       | 1,034.381  | 6,218.645  | 4.665   | 53.425    | 378.912   | 4,026.133  |
| GEOSEG     | capx_to_assets | 757,202      | 94,281       | 87.500      | 0.070      | 2.012      | 0.002   | 0.024     | 0.068     | 0.208      |
| GEOSEG     | capxs          | 757,202      | 113,975      | 84.900      | 154.064    | 2,092.508  | 0.050   | 2.868     | 35.547    | 620.856    |
| GEOSEG     | emps           | 757,202      | 116,851      | 84.600      | 5,689.328  | 29,350.310 | 63.000  | 430.000   | 2,660.500 | 23,800.000 |
| GEOSEG     | ias            | 757,202      | 224,222      | 70.400      | 5,498.257  | 66,295.389 | 12.727  | 123.998   | 853.014   | 10,651.189 |
| GEOSEG     | op_margin      | 757,202      | 174,729      | 76.900      | -3.019     | 120.572    | 0.010   | 0.083     | 0.183     | 0.505      |
| GEOSEG     | ops            | 757,202      | 191,997      | 74.600      | 164.688    | 2,390.083  | 0.000   | 5.956     | 56.851    | 636.019    |
| GEOSEG     | rds            | 757,202      | 33,809       | 95.500      | 12.445     | 209.465    | 0.000   | 0.000     | 1.211     | 42.665     |
| GEOSEG     | sales          | 757,202      | 713,367      | 5.800       | 1,015.267  | 6,776.590  | 1.646   | 37.000    | 313.459   | 3,887.085  |
| OPSEG      | capx_to_assets | 79,700       | 39,929       | 49.900      | 0.093      | 2.710      | 0.007   | 0.031     | 0.074     | 0.236      |
| OPSEG      | capxs          | 79,700       | 50,421       | 36.700      | 212.159    | 1,180.580  | 1.000   | 14.700    | 92.000    | 865.200    |
| OPSEG      | emps           | 79,700       | 12,264       | 84.600      | 8,380.187  | 21,219.016 | 200.000 | 1,719.000 | 7,000.000 | 37,516.150 |
| OPSEG      | ias            | 79,700       | 55,702       | 30.100      | 10,905.638 | 72,059.981 | 82.882  | 503.610   | 2,562.879 | 39,981.475 |
| OPSEG      | op_margin      | 79,700       | 45,268       | 43.200      | -3.085     | 176.449    | 0.023   | 0.114     | 0.247     | 0.683      |
| OPSEG      | ops            | 79,700       | 51,970       | 34.800      | 278.180    | 1,646.676  | -0.528  | 25.000    | 185.982   | 1,483.741  |
| OPSEG      | rds            | 79,700       | 7,539        | 90.500      | 16.696     | 178.731    | 0.000   | 0.000     | 0.000     | 6.109      |
| OPSEG      | sales          | 79,700       | 77,237       | 3.100       | 2,435.930  | 26,996.094 | 16.950  | 245.285   | 1,370.779 | 8,731.097  |

## Table 4. Firm-Year Segment Structure

This table summarizes firm-year-stype aggregates, including segment concentration. The full CSV includes raw-source and latest-source views.

| stype      | variable                | firm_year_units | nonmissing_n | missing_pct | mean       | sd         | p25     | p50       | p75       | p95        |
| ---------- | ----------------------- | --------------- | ------------ | ----------- | ---------- | ---------- | ------- | --------- | --------- | ---------- |
| ALL_STYPES | reported_segment_rows   | 364,006         | 364,006      | 0.000       | 4.158      | 3.060      | 3.000   | 3.000     | 5.000     | 10.000     |
| ALL_STYPES | sales_hhi               | 364,006         | 343,330      | 5.700       | 0.470      | 0.193      | 0.363   | 0.500     | 0.500     | 1.000      |
| ALL_STYPES | top_segment_sales_share | 364,006         | 343,330      | 5.700       | 0.524      | 0.167      | 0.500   | 0.500     | 0.500     | 1.000      |
| ALL_STYPES | total_positive_sales    | 364,006         | 364,006      | 0.000       | 4,430.192  | 30,931.960 | 19.622  | 166.812   | 1,238.602 | 16,437.780 |
| BUSSEG     | reported_segment_rows   | 352,429         | 352,429      | 0.000       | 1.913      | 1.592      | 1.000   | 1.000     | 3.000     | 5.000      |
| BUSSEG     | sales_hhi               | 352,429         | 331,526      | 5.900       | 0.843      | 0.244      | 0.662   | 1.000     | 1.000     | 1.000      |
| BUSSEG     | top_segment_sales_share | 352,429         | 331,526      | 5.900       | 0.878      | 0.201      | 0.790   | 1.000     | 1.000     | 1.000      |
| BUSSEG     | total_positive_sales    | 352,429         | 352,429      | 0.000       | 1,971.884  | 11,555.005 | 9.871   | 80.482    | 572.666   | 7,219.455  |
| GEOSEG     | reported_segment_rows   | 307,470         | 307,470      | 0.000       | 2.463      | 1.976      | 2.000   | 2.000     | 2.000     | 6.000      |
| GEOSEG     | sales_hhi               | 307,470         | 299,076      | 2.700       | 0.843      | 0.243      | 0.689   | 1.000     | 1.000     | 1.000      |
| GEOSEG     | top_segment_sales_share | 307,470         | 299,076      | 2.700       | 0.883      | 0.195      | 0.813   | 1.000     | 1.000     | 1.000      |
| GEOSEG     | total_positive_sales    | 307,470         | 307,470      | 0.000       | 2,364.606  | 13,743.526 | 15.934  | 108.954   | 730.821   | 8,961.550  |
| OPSEG      | reported_segment_rows   | 13,650          | 13,650       | 0.000       | 5.839      | 2.701      | 4.000   | 5.000     | 7.000     | 11.000     |
| OPSEG      | sales_hhi               | 13,650          | 13,475       | 1.300       | 0.428      | 0.206      | 0.275   | 0.382     | 0.532     | 0.858      |
| OPSEG      | top_segment_sales_share | 13,650          | 13,475       | 1.300       | 0.539      | 0.205      | 0.381   | 0.508     | 0.680     | 0.924      |
| OPSEG      | total_positive_sales    | 13,650          | 13,650       | 0.000       | 13,940.861 | 97,713.398 | 661.715 | 2,568.501 | 9,869.681 | 53,296.850 |

## Generated Files

- `reports/segment_descriptives/tables/table1_source_rows_by_segment_type.csv`
- `reports/segment_descriptives/tables/table2_segments_per_firm_year_distribution.csv`
- `reports/segment_descriptives/tables/table3_segment_variable_quartiles.csv`
- `reports/segment_descriptives/tables/table4_firm_year_segment_structure.csv`
- `reports/segment_descriptives/tables/table5_descriptive_definitions.csv`

## Reading Notes

- The latest-source view is the cleaner default for paper-style descriptive tables because repeated source snapshots are removed.
- The raw-source view is retained for auditing the original file exactly as received.
- `operating_candidate_segment_rows` is a descriptive name screen, not a final research-sample restriction.
- Missingness percentages use the displayed table unit: segment rows for Table 3 and firm-year-stype rows for Table 4.
