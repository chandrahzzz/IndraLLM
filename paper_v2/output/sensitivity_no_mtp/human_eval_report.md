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
Resolved items: 201; unresolved: 0.

## Judge validation (primary collapse; weighted to all 900 outputs)

| Judge | Sensitivity | Specificity | Agreement | κ (sample) |
|---|---|---|---|---|
| J-QWEN | 0.88 | 0.71 | 0.80 | 0.43 |
| J-OSS | 0.86 | 0.91 | 0.88 | 0.63 |

| Budget × condition | Human accuracy % [95% CI] |
|---|---|
| 128|CS-LAT | 17 [7, 28] |
| 128|EN-MATCH | 40 [26, 55] |
| 128|MIXED | 14 [1, 35] |
| 512|CS-LAT | 58 [54, 67] |
| 512|EN-MATCH | 62 [58, 69] |
| 512|MIXED | 56 [46, 66] |
| 1024|CS-LAT | 72 [67, 81] |
| 1024|EN-MATCH | 74 [63, 85] |
| 1024|MIXED | 62 [51, 76] |

| Gap | Human estimate (pp) [95% CI] |
|---|---|
| 128|MIXED-CS-LAT | -3 [-22, 19] |
| 128|CS-LAT-EN-MATCH | -23 [-42, -5] |
| 512|MIXED-CS-LAT | -2 [-17, 12] |
| 512|CS-LAT-EN-MATCH | -3 [-15, 9] |
| 1024|MIXED-CS-LAT | -10 [-25, 5] |
| 1024|CS-LAT-EN-MATCH | -2 [-13, 13] |

## Judge validation (secondary collapse; weighted to all 900 outputs)

| Judge | Sensitivity | Specificity | Agreement | κ (sample) |
|---|---|---|---|---|
| J-QWEN | 0.88 | 0.79 | 0.84 | 0.55 |
| J-OSS | 0.81 | 0.94 | 0.86 | 0.61 |

| Budget × condition | Human accuracy % [95% CI] |
|---|---|
| 128|CS-LAT | 40 [25, 57] |
| 128|EN-MATCH | 53 [39, 68] |
| 128|MIXED | 17 [4, 37] |
| 512|CS-LAT | 58 [54, 67] |
| 512|EN-MATCH | 65 [58, 73] |
| 512|MIXED | 65 [63, 66] |
| 1024|CS-LAT | 72 [67, 81] |
| 1024|EN-MATCH | 80 [68, 85] |
| 1024|MIXED | 62 [51, 76] |

| Gap | Human estimate (pp) [95% CI] |
|---|---|
| 128|MIXED-CS-LAT | -24 [-46, 2] |
| 128|CS-LAT-EN-MATCH | -13 [-34, 9] |
| 512|MIXED-CS-LAT | +7 [-3, 12] |
| 512|CS-LAT-EN-MATCH | -7 [-19, 5] |
| 1024|MIXED-CS-LAT | -10 [-25, 5] |
| 1024|CS-LAT-EN-MATCH | -8 [-18, 6] |
