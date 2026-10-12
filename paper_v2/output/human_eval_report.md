# Human validation of the judges — results

## Completeness

| Reviewer | Assigned | Labelled | Blank | Invalid | Unreadable |
|---|---|---|---|---|---|
| Akshith | 161 | 161 | 0 | 0 | 0 |
| Chandrahas | 157 | 157 | 0 | 0 | 0 |
| Kapilan | 28 | 28 | 0 | 0 | 0 |
| Shamik | 27 | 27 | 0 | 0 | 0 |
| TBD_second_Kannada_reader | 32 | 32 | 0 | 0 | 0 |

## Inter-annotator agreement

Double-labelled items: 189
Six-way agreement 0.90; binary agreement 0.93; Cohen's κ (primary) 0.85; κ (secondary) 0.90.

Binary disagreements: 14; adjudicated: 14 (file `C:\Users\Chandrahas Reddy\MYallPROJECTS\IndraLLM\results\human_eval_v2\adjudication.xlsx`).
Resolved items: 216; unresolved: 0.

## Judge validation (primary collapse; weighted to all 900 outputs)

| Judge | Sensitivity | Specificity | Agreement | κ (sample) |
|---|---|---|---|---|
| J-QWEN | 0.88 | 0.66 | 0.76 | 0.37 |
| J-OSS | 0.86 | 0.92 | 0.89 | 0.65 |

| Budget × condition | Human accuracy % [95% CI] |
|---|---|
| 128|CS-LAT | 17 [7, 28] |
| 128|EN-MATCH | 40 [26, 53] |
| 128|MIXED | 13 [1, 31] |
| 512|CS-LAT | 58 [54, 67] |
| 512|EN-MATCH | 61 [58, 66] |
| 512|MIXED | 51 [46, 58] |
| 1024|CS-LAT | 66 [56, 78] |
| 1024|EN-MATCH | 68 [63, 77] |
| 1024|MIXED | 62 [50, 75] |

| Gap | Human estimate (pp) [95% CI] |
|---|---|
| 128|MIXED-CS-LAT | -4 [-22, 18] |
| 128|CS-LAT-EN-MATCH | -23 [-41, -4] |
| 512|MIXED-CS-LAT | -8 [-19, 1] |
| 512|CS-LAT-EN-MATCH | -2 [-11, 9] |
| 1024|MIXED-CS-LAT | -4 [-20, 12] |
| 1024|CS-LAT-EN-MATCH | -3 [-15, 11] |

## Judge validation (secondary collapse; weighted to all 900 outputs)

| Judge | Sensitivity | Specificity | Agreement | κ (sample) |
|---|---|---|---|---|
| J-QWEN | 0.88 | 0.72 | 0.80 | 0.47 |
| J-OSS | 0.81 | 0.95 | 0.87 | 0.64 |

| Budget × condition | Human accuracy % [95% CI] |
|---|---|
| 128|CS-LAT | 40 [25, 58] |
| 128|EN-MATCH | 52 [39, 66] |
| 128|MIXED | 15 [4, 34] |
| 512|CS-LAT | 58 [54, 67] |
| 512|EN-MATCH | 64 [58, 69] |
| 512|MIXED | 54 [47, 62] |
| 1024|CS-LAT | 66 [56, 75] |
| 1024|EN-MATCH | 71 [66, 80] |
| 1024|MIXED | 62 [51, 75] |

| Gap | Human estimate (pp) [95% CI] |
|---|---|
| 128|MIXED-CS-LAT | -25 [-46, -0] |
| 128|CS-LAT-EN-MATCH | -12 [-32, 9] |
| 512|MIXED-CS-LAT | -4 [-17, 7] |
| 512|CS-LAT-EN-MATCH | -5 [-15, 5] |
| 1024|MIXED-CS-LAT | -4 [-20, 13] |
| 1024|CS-LAT-EN-MATCH | -6 [-18, 7] |
