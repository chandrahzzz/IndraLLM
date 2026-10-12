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
Resolved items: 187; unresolved: 14.

## Judge validation (primary collapse; weighted to all 900 outputs)

| Judge | Sensitivity | Specificity | Agreement | κ (sample) |
|---|---|---|---|---|
| J-QWEN | 0.88 | 0.78 | 0.84 | 0.52 |
| J-OSS | 0.86 | 0.91 | 0.88 | 0.63 |

| Budget × condition | Human accuracy % [95% CI] |
|---|---|
| 128|CS-LAT | 19 [8, 32] |
| 128|EN-MATCH | 43 [26, 62] |
| 128|MIXED | 13 [0, 33] |
| 512|CS-LAT | 66 [61, 75] |
| 512|EN-MATCH | 64 [58, 74] |
| 512|MIXED | 65 [63, 66] |
| 1024|CS-LAT | 72 [67, 81] |
| 1024|EN-MATCH | 85 [85, 85] |
| 1024|MIXED | 62 [51, 75] |

| Gap | Human estimate (pp) [95% CI] |
|---|---|
| 128|MIXED-CS-LAT | -6 [-26, 17] |
| 128|CS-LAT-EN-MATCH | -24 [-46, -3] |
| 512|MIXED-CS-LAT | -1 [-11, 5] |
| 512|CS-LAT-EN-MATCH | +2 [-9, 17] |
| 1024|MIXED-CS-LAT | -10 [-25, 5] |
| 1024|CS-LAT-EN-MATCH | -13 [-18, -4] |

## Judge validation (secondary collapse; weighted to all 900 outputs)

| Judge | Sensitivity | Specificity | Agreement | κ (sample) |
|---|---|---|---|---|
| J-QWEN | 0.87 | 0.81 | 0.85 | 0.56 |
| J-OSS | 0.84 | 0.94 | 0.88 | 0.65 |

| Budget × condition | Human accuracy % [95% CI] |
|---|---|
| 128|CS-LAT | 37 [22, 55] |
| 128|EN-MATCH | 48 [35, 66] |
| 128|MIXED | 15 [2, 36] |
| 512|CS-LAT | 66 [61, 75] |
| 512|EN-MATCH | 64 [58, 74] |
| 512|MIXED | 65 [63, 66] |
| 1024|CS-LAT | 72 [67, 81] |
| 1024|EN-MATCH | 85 [85, 85] |
| 1024|MIXED | 62 [51, 75] |

| Gap | Human estimate (pp) [95% CI] |
|---|---|
| 128|MIXED-CS-LAT | -22 [-46, 3] |
| 128|CS-LAT-EN-MATCH | -10 [-32, 12] |
| 512|MIXED-CS-LAT | -1 [-11, 5] |
| 512|CS-LAT-EN-MATCH | +2 [-9, 17] |
| 1024|MIXED-CS-LAT | -10 [-25, 5] |
| 1024|CS-LAT-EN-MATCH | -13 [-18, -4] |
