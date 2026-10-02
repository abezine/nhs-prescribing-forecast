# Backtest results

Rolling-origin backtest, 12 origins, horizons 1-3 months, 105 series (NHS region x BNF chapter), data 2021-01 to 2026-07.

## Overall

| model | MAE (items) | WAPE | MASE |
|---|---:|---:|---:|
| hgb | 30,125 | 3.09% | 0.819 |
| seasonal_naive | 36,310 | 3.73% | 0.876 |
| naive_last | 54,885 | 5.64% | 1.471 |

## WAPE by horizon

| horizon | hgb | seasonal_naive | naive_last |
|---|---:|---:|---:|
| h1 | 3.19% | 3.75% | 6.65% |
| h2 | 3.14% | 3.75% | 5.93% |
| h3 | 2.95% | 3.68% | 4.34% |

## WAPE by BNF chapter

| chapter | hgb | seasonal_naive | naive_last | model wins |
|---|---:|---:|---:|---|
| 01 Gastro-Intestinal System | 2.82% | 3.39% | 4.36% | yes |
| 02 Cardiovascular System | 2.82% | 3.93% | 4.40% | yes |
| 03 Respiratory System | 3.00% | 3.47% | 5.09% | yes |
| 04 Central Nervous System | 2.90% | 3.32% | 4.37% | yes |
| 05 Infections | 3.95% | 4.00% | 8.96% | yes |
| 06 Endocrine System | 2.91% | 4.45% | 4.62% | yes |
| 07 Obstetrics, Gynaecology and Urinary-Tract Disorders | 2.90% | 3.61% | 4.23% | yes |
| 08 Malignant Disease and Immunosuppression | 3.37% | 3.87% | 4.28% | yes |
| 09 Nutrition and Blood | 2.82% | 3.40% | 4.25% | yes |
| 10 Musculoskeletal and Joint Diseases | 2.98% | 3.05% | 4.35% | yes |
| 11 Eye | 3.46% | 2.91% | 4.81% | **no** |
| 12 Ear, Nose and Oropharynx | 3.31% | 3.11% | 6.20% | **no** |
| 13 Skin | 3.07% | 2.88% | 4.75% | **no** |
| 14 Immunological Products and Vaccines | 23.93% | 9.19% | 127.60% | **no** |
| 15 Anaesthesia | 3.93% | 3.65% | 5.96% | **no** |
