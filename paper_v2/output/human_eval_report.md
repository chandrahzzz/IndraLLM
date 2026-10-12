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

Binary disagreements: 14; adjudicated: 0 (file `C:\Users\Chandrahas Reddy\MYallPROJECTS\IndraLLM\results\human_eval_v2\adjudication.xlsx`).
Resolved items: 202; unresolved: 14.

## Judge validation (primary collapse; weighted to all 900 outputs)

| Judge | Sensitivity | Specificity | Agreement | κ (sample) |
|---|---|---|---|---|
| J-QWEN | 0.88 | 0.71 | 0.80 | 0.44 |
| J-OSS | 0.86 | 0.93 | 0.89 | 0.65 |

| Budget × condition | Human accuracy % [95% CI] |
|---|---|
| 128|CS-LAT | 19 [8, 32] |
| 128|EN-MATCH | 42 [26, 59] |
| 128|MIXED | 12 [0, 31] |
| 512|CS-LAT | 58 [54, 67] |
| 512|EN-MATCH | 62 [58, 69] |
| 512|MIXED | 52 [46, 60] |
| 1024|CS-LAT | 66 [56, 75] |
| 1024|EN-MATCH | 70 [63, 78] |
| 1024|MIXED | 62 [51, 76] |

| Gap | Human estimate (pp) [95% CI] |
|---|---|
| 128|MIXED-CS-LAT | -7 [-26, 14] |
| 128|CS-LAT-EN-MATCH | -23 [-44, -3] |
| 512|MIXED-CS-LAT | -7 [-19, 3] |
| 512|CS-LAT-EN-MATCH | -3 [-11, 9] |
| 1024|MIXED-CS-LAT | -4 [-21, 13] |
| 1024|CS-LAT-EN-MATCH | -5 [-18, 9] |

## Judge validation (secondary collapse; weighted to all 900 outputs)

| Judge | Sensitivity | Specificity | Agreement | κ (sample) |
|---|---|---|---|---|
| J-QWEN | 0.87 | 0.74 | 0.81 | 0.48 |
| J-OSS | 0.84 | 0.95 | 0.89 | 0.67 |

| Budget × condition | Human accuracy % [95% CI] |
|---|---|
| 128|CS-LAT | 37 [21, 55] |
| 128|EN-MATCH | 47 [35, 64] |
| 128|MIXED | 14 [2, 33] |
| 512|CS-LAT | 58 [54, 67] |
| 512|EN-MATCH | 62 [58, 69] |
| 512|MIXED | 52 [46, 60] |
| 1024|CS-LAT | 66 [56, 75] |
| 1024|EN-MATCH | 70 [63, 78] |
| 1024|MIXED | 62 [51, 76] |

| Gap | Human estimate (pp) [95% CI] |
|---|---|
| 128|MIXED-CS-LAT | -23 [-46, 0] |
| 128|CS-LAT-EN-MATCH | -9 [-32, 13] |
| 512|MIXED-CS-LAT | -7 [-19, 3] |
| 512|CS-LAT-EN-MATCH | -3 [-11, 9] |
| 1024|MIXED-CS-LAT | -4 [-20, 13] |
| 1024|CS-LAT-EN-MATCH | -5 [-18, 9] |
