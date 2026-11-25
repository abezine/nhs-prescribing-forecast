# Backtest results

Rolling-origin backtest, 12 origins, horizons 1-3 months, 105 series (NHS region x BNF chapter), data 2021-01 to 2026-09.

## Overall

| model | MAE (items) | WAPE | MASE |
|---|---:|---:|---:|
| hgb | 28,432 | 2.91% | 0.781 |
| seasonal_naive | 35,395 | 3.62% | 0.853 |
| naive_last | 56,028 | 5.73% | 1.512 |

## WAPE by horizon

| horizon | hgb | seasonal_naive | naive_last |
|---|---:|---:|---:|
| h1 | 3.03% | 3.68% | 6.56% |
| h2 | 3.03% | 3.67% | 6.70% |
| h3 | 2.66% | 3.51% | 3.94% |

## WAPE by BNF chapter

| chapter | hgb | seasonal_naive | naive_last | model wins |
|---|---:|---:|---:|---|
| 01 Gastro-Intestinal System | 2.61% | 3.18% | 4.44% | yes |
| 02 Cardiovascular System | 2.63% | 3.87% | 4.46% | yes |
| 03 Respiratory System | 2.90% | 3.08% | 5.35% | yes |
| 04 Central Nervous System | 2.73% | 3.29% | 4.46% | yes |
| 05 Infections | 3.93% | 3.24% | 9.06% | **no** |
| 06 Endocrine System | 2.64% | 4.56% | 4.69% | yes |
| 07 Obstetrics, Gynaecology and Urinary-Tract Disorders | 2.58% | 3.67% | 4.32% | yes |
| 08 Malignant Disease and Immunosuppression | 3.26% | 4.12% | 4.36% | yes |
| 09 Nutrition and Blood | 2.55% | 2.92% | 4.31% | yes |
| 10 Musculoskeletal and Joint Diseases | 2.78% | 2.88% | 4.45% | yes |
| 11 Eye | 3.38% | 2.83% | 5.04% | **no** |
| 12 Ear, Nose and Oropharynx | 3.15% | 3.09% | 6.44% | **no** |
| 13 Skin | 2.89% | 2.68% | 5.09% | **no** |
| 14 Immunological Products and Vaccines | 24.31% | 9.17% | 128.27% | **no** |
| 15 Anaesthesia | 3.95% | 3.54% | 6.19% | **no** |
