# Backtest results

Rolling-origin backtest, 12 origins, horizons 1-3 months, 105 series (NHS region x BNF chapter), data 2021-01 to 2026-08.

## Overall

| model | MAE (items) | WAPE | MASE |
|---|---:|---:|---:|
| hgb | 29,205 | 2.99% | 0.801 |
| seasonal_naive | 36,118 | 3.70% | 0.871 |
| naive_last | 55,818 | 5.72% | 1.501 |

## WAPE by horizon

| horizon | hgb | seasonal_naive | naive_last |
|---|---:|---:|---:|
| h1 | 3.12% | 3.75% | 6.76% |
| h2 | 3.07% | 3.68% | 6.36% |
| h3 | 2.78% | 3.67% | 4.05% |

## WAPE by BNF chapter

| chapter | hgb | seasonal_naive | naive_last | model wins |
|---|---:|---:|---:|---|
| 01 Gastro-Intestinal System | 2.69% | 3.32% | 4.44% | yes |
| 02 Cardiovascular System | 2.71% | 3.94% | 4.46% | yes |
| 03 Respiratory System | 2.95% | 3.26% | 5.24% | yes |
| 04 Central Nervous System | 2.80% | 3.33% | 4.45% | yes |
| 05 Infections | 4.03% | 3.57% | 9.04% | **no** |
| 06 Endocrine System | 2.75% | 4.54% | 4.70% | yes |
| 07 Obstetrics, Gynaecology and Urinary-Tract Disorders | 2.73% | 3.68% | 4.32% | yes |
| 08 Malignant Disease and Immunosuppression | 3.32% | 4.06% | 4.37% | yes |
| 09 Nutrition and Blood | 2.70% | 3.21% | 4.35% | yes |
| 10 Musculoskeletal and Joint Diseases | 2.90% | 3.00% | 4.46% | yes |
| 11 Eye | 3.43% | 2.88% | 5.00% | **no** |
| 12 Ear, Nose and Oropharynx | 3.24% | 3.10% | 6.39% | **no** |
| 13 Skin | 2.98% | 2.78% | 4.92% | **no** |
| 14 Immunological Products and Vaccines | 24.27% | 9.18% | 127.91% | **no** |
| 15 Anaesthesia | 3.91% | 3.61% | 6.04% | **no** |
