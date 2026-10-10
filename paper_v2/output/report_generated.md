## G1. Three-budget results (EXP-004 + EXP-005), both judges

### G1.1 Accuracy (%, n = 100 per cell) with Wilson 95% CI

| Judge | Budget | EN-MATCH | CS-LAT | MIXED |
| --- | --- | --- | --- | --- |
| J-QWEN | 128 | 60 [50.2, 69.1] | 49 [39.4, 58.7] | 26 [18.4, 35.4] |
| J-QWEN | 512 | 80 [71.1, 86.7] | 59 [49.2, 68.1] | 63 [53.2, 71.8] |
| J-QWEN | 1024 | 85 [76.7, 90.7] | 61 [51.2, 70.0] | 58 [48.2, 67.2] |
| J-OSS | 128 | 37 [28.2, 46.8] | 25 [17.5, 34.3] | 17 [10.9, 25.5] |
| J-OSS | 512 | 58 [48.2, 67.2] | 54 [44.3, 63.4] | 48 [38.5, 57.7] |
| J-OSS | 1024 | 63 [53.2, 71.8] | 56 [46.2, 65.3] | 51 [41.3, 60.6] |

### G1.2 Paired contrasts at each budget (comparison vs reference)

b = reference correct & comparison wrong; c = the reverse. Topic p = exact sign-flip over 2^20 patterns; topic CI = percentile bootstrap over 20 topics (10,000 resamples).

| Judge | Budget | Contrast | Ref % | Cmp % | Δ (pp) | b | c | Exact p | Topic p | Topic 95% CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J-QWEN | 128 | CS-LAT vs EN-MATCH | 60 | 49 | −11 | 27 | 16 | 0.13 | 0.42 | [-34, 13] |
| J-QWEN | 128 | MIXED vs CS-LAT | 49 | 26 | −23 | 30 | 7 | <0.001 | 0.004 | [-35, -11] |
| J-QWEN | 128 | MIXED vs EN-MATCH | 60 | 26 | −34 | 45 | 11 | <0.001 | 0.030 | [-59, -7] |
| J-QWEN | 512 | CS-LAT vs EN-MATCH | 80 | 59 | −21 | 28 | 7 | <0.001 | 0.082 | [-41, -1] |
| J-QWEN | 512 | MIXED vs CS-LAT | 59 | 63 | +4 | 12 | 16 | 0.57 | 0.65 | [-8, 15] |
| J-QWEN | 512 | MIXED vs EN-MATCH | 80 | 63 | −17 | 24 | 7 | 0.003 | 0.13 | [-35, 3] |
| J-QWEN | 1024 | CS-LAT vs EN-MATCH | 85 | 61 | −24 | 27 | 3 | <0.001 | 0.018 | [-42, -8] |
| J-QWEN | 1024 | MIXED vs CS-LAT | 61 | 58 | −3 | 15 | 12 | 0.70 | 0.72 | [-14, 8] |
| J-QWEN | 1024 | MIXED vs EN-MATCH | 85 | 58 | −27 | 29 | 2 | <0.001 | 0.003 | [-42, -13] |
| J-OSS | 128 | CS-LAT vs EN-MATCH | 37 | 25 | −12 | 22 | 10 | 0.050 | 0.22 | [-29, 4] |
| J-OSS | 128 | MIXED vs CS-LAT | 25 | 17 | −8 | 18 | 10 | 0.18 | 0.24 | [-19, 2] |
| J-OSS | 128 | MIXED vs EN-MATCH | 37 | 17 | −20 | 29 | 9 | 0.002 | 0.067 | [-39, -2] |
| J-OSS | 512 | CS-LAT vs EN-MATCH | 58 | 54 | −4 | 16 | 12 | 0.57 | 0.76 | [-22, 15] |
| J-OSS | 512 | MIXED vs CS-LAT | 54 | 48 | −6 | 17 | 11 | 0.34 | 0.44 | [-18, 6] |
| J-OSS | 512 | MIXED vs EN-MATCH | 58 | 48 | −10 | 19 | 9 | 0.087 | 0.31 | [-26, 6] |
| J-OSS | 1024 | CS-LAT vs EN-MATCH | 63 | 56 | −7 | 15 | 8 | 0.21 | 0.52 | [-24, 10] |
| J-OSS | 1024 | MIXED vs CS-LAT | 56 | 51 | −5 | 14 | 9 | 0.40 | 0.52 | [-17, 7] |
| J-OSS | 1024 | MIXED vs EN-MATCH | 63 | 51 | −12 | 21 | 9 | 0.043 | 0.22 | [-28, 5] |

### G1.3 Within-condition change between budgets (same judge)

| Judge | Change | Condition | Acc before | Acc after | Lost (b) | Gained (c) | Exact p | Topic p | Topic 95% CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| J-QWEN | 128->512 | EN-MATCH | 60 | 80 | 0 | 20 | <0.001 | 0.12 | [5, 40] |
| J-QWEN | 128->512 | CS-LAT | 49 | 59 | 11 | 21 | 0.11 | 0.22 | [-2, 24] |
| J-QWEN | 128->512 | MIXED | 26 | 63 | 5 | 42 | <0.001 | 0.003 | [18, 57] |
| J-QWEN | 512->1024 | EN-MATCH | 80 | 85 | 0 | 5 | 0.062 | 1.00 | [0, 15] |
| J-QWEN | 512->1024 | CS-LAT | 59 | 61 | 3 | 5 | 0.73 | 0.73 | [-3, 7] |
| J-QWEN | 512->1024 | MIXED | 63 | 58 | 8 | 3 | 0.23 | 0.19 | [-11, 0] |
| J-QWEN | 128->1024 | EN-MATCH | 60 | 85 | 0 | 25 | <0.001 | 0.062 | [10, 45] |
| J-QWEN | 128->1024 | CS-LAT | 49 | 61 | 9 | 21 | 0.043 | 0.11 | [0, 25] |
| J-QWEN | 128->1024 | MIXED | 26 | 58 | 5 | 37 | <0.001 | 0.003 | [15, 50] |
| J-OSS | 128->512 | EN-MATCH | 37 | 58 | 3 | 24 | <0.001 | 0.043 | [5, 39] |
| J-OSS | 128->512 | CS-LAT | 25 | 54 | 3 | 32 | <0.001 | <0.001 | [16, 43] |
| J-OSS | 128->512 | MIXED | 17 | 48 | 3 | 34 | <0.001 | <0.001 | [19, 43] |
| J-OSS | 512->1024 | EN-MATCH | 58 | 63 | 2 | 7 | 0.18 | 0.50 | [-1, 15] |
| J-OSS | 512->1024 | CS-LAT | 54 | 56 | 2 | 4 | 0.69 | 0.69 | [-3, 7] |
| J-OSS | 512->1024 | MIXED | 48 | 51 | 6 | 9 | 0.61 | 0.59 | [-4, 10] |
| J-OSS | 128->1024 | EN-MATCH | 37 | 63 | 4 | 30 | <0.001 | 0.021 | [8, 45] |
| J-OSS | 128->1024 | CS-LAT | 25 | 56 | 2 | 33 | <0.001 | <0.001 | [18, 45] |
| J-OSS | 128->1024 | MIXED | 17 | 51 | 3 | 37 | <0.001 | <0.001 | [23, 45] |

### G1.4 Change in each gap between budgets (per-topic difference-in-differences)

| Judge | Change | Gap | Gap before | Gap after | Change | Topic 95% CI | Topic p |
| --- | --- | --- | --- | --- | --- | --- | --- |
| J-QWEN | 128->512 | CS-LAT-EN-MATCH | -11 | -21 | −10 | [-31, 9] | 0.41 |
| J-QWEN | 128->512 | MIXED-CS-LAT | -23 | 4 | +27 | [7, 45] | 0.018 |
| J-QWEN | 128->512 | MIXED-EN-MATCH | -34 | -17 | +17 | [-4, 39] | 0.18 |
| J-QWEN | 512->1024 | CS-LAT-EN-MATCH | -21 | -24 | −3 | [-16, 6] | 0.86 |
| J-QWEN | 512->1024 | MIXED-CS-LAT | 4 | -3 | −7 | [-14, 1] | 0.14 |
| J-QWEN | 512->1024 | MIXED-EN-MATCH | -17 | -27 | −10 | [-22, -1] | 0.094 |
| J-QWEN | 128->1024 | CS-LAT-EN-MATCH | -11 | -24 | −13 | [-36, 7] | 0.31 |
| J-QWEN | 128->1024 | MIXED-CS-LAT | -23 | -3 | +20 | [5, 34] | 0.023 |
| J-QWEN | 128->1024 | MIXED-EN-MATCH | -34 | -27 | +7 | [-15, 29] | 0.62 |
| J-OSS | 128->512 | CS-LAT-EN-MATCH | -12 | -4 | +8 | [-8, 23] | 0.42 |
| J-OSS | 128->512 | MIXED-CS-LAT | -8 | -6 | +2 | [-11, 16] | 0.89 |
| J-OSS | 128->512 | MIXED-EN-MATCH | -20 | -10 | +10 | [-6, 26] | 0.30 |
| J-OSS | 512->1024 | CS-LAT-EN-MATCH | -4 | -7 | −3 | [-12, 4] | 0.66 |
| J-OSS | 512->1024 | MIXED-CS-LAT | -6 | -5 | +1 | [-8, 10] | 1.00 |
| J-OSS | 512->1024 | MIXED-EN-MATCH | -10 | -12 | −2 | [-13, 7] | 0.88 |
| J-OSS | 128->1024 | CS-LAT-EN-MATCH | -12 | -7 | +5 | [-11, 20] | 0.63 |
| J-OSS | 128->1024 | MIXED-CS-LAT | -8 | -5 | +3 | [-7, 13] | 0.71 |
| J-OSS | 128->1024 | MIXED-EN-MATCH | -20 | -12 | +8 | [-9, 24] | 0.43 |

### G1.5 MIXED vs CS-LAT on the 60 word-identical propositions (hi, ta, bn)

| Judge | Budget | CS-LAT % | MIXED % | b | c | Exact p | Topic p |
| --- | --- | --- | --- | --- | --- | --- | --- |
| J-QWEN | 128 | 51.7 | 26.7 | 18 | 3 | 0.001 | 0.016 |
| J-QWEN | 512 | 61.7 | 63.3 | 7 | 8 | 1.00 | 1.00 |
| J-QWEN | 1024 | 65.0 | 60.0 | 8 | 5 | 0.58 | 0.64 |
| J-OSS | 128 | 30.0 | 16.7 | 13 | 5 | 0.096 | 0.19 |
| J-OSS | 512 | 55.0 | 48.3 | 11 | 7 | 0.48 | 0.53 |
| J-OSS | 1024 | 56.7 | 53.3 | 9 | 7 | 0.80 | 0.84 |

### G1.6 Generation descriptives by budget

| Budget | Condition | Stopped before cap (of 100) | Hit cap | Mean completion tokens | Mean chars | Mostly Brahmic % |
| --- | --- | --- | --- | --- | --- | --- |
| 128 | EN-MATCH | 0 | 100 | 128 | 529 | 0 |
| 128 | CS-LAT | 1 | 99 | 128 | 423 | 2 |
| 128 | MIXED | 0 | 100 | 128 | 303 | 88 |
| 512 | EN-MATCH | 58 | 42 | 438 | 1,771 | 0 |
| 512 | CS-LAT | 15 | 85 | 484 | 1,601 | 2 |
| 512 | MIXED | 5 | 95 | 508 | 1,122 | 96 |
| 1024 | EN-MATCH | 95 | 5 | 510 | 1,988 | 0 |
| 1024 | CS-LAT | 61 | 39 | 812 | 2,679 | 2 |
| 1024 | MIXED | 36 | 64 | 936 | 2,054 | 97 |

Prefix consistency (longer response begins with the shorter one, of 100): 512 starts with 128 — EN-MATCH 84, CS-LAT 85, MIXED 84; 1,024 starts with 512 — EN-MATCH 91, CS-LAT 78, MIXED 80.

## G2. Judge agreement (J-QWEN vs J-OSS) by budget and condition

| Budget | Condition | n | Both correct | Both wrong | Q correct / O wrong | Q wrong / O correct | Agreement | κ | κ topic 95% CI | P(Q correct | O wrong) | P(O correct | Q wrong) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 128 | EN-MATCH | 100 | 35 | 38 | 25 | 2 | 0.730 | 0.49 | [0.21, 0.77] | 0.40 | 0.05 |
| 128 | CS-LAT | 100 | 23 | 49 | 26 | 2 | 0.720 | 0.43 | [0.22, 0.65] | 0.35 | 0.04 |
| 128 | MIXED | 100 | 11 | 68 | 15 | 6 | 0.790 | 0.39 | [0.15, 0.61] | 0.18 | 0.08 |
| 128 | ALL | 300 | 69 | 155 | 66 | 10 | 0.747 | 0.47 | [0.29, 0.66] | 0.30 | 0.06 |
| 512 | EN-MATCH | 100 | 58 | 20 | 22 | 0 | 0.780 | 0.51 | [0.16, 0.86] | 0.52 | 0.00 |
| 512 | CS-LAT | 100 | 48 | 35 | 11 | 6 | 0.830 | 0.66 | [0.39, 0.84] | 0.24 | 0.15 |
| 512 | MIXED | 100 | 45 | 34 | 18 | 3 | 0.790 | 0.58 | [0.36, 0.76] | 0.35 | 0.08 |
| 512 | ALL | 300 | 151 | 89 | 51 | 9 | 0.800 | 0.59 | [0.37, 0.77] | 0.36 | 0.09 |
| 1024 | EN-MATCH | 100 | 63 | 15 | 22 | 0 | 0.780 | 0.46 | [0.00, 0.83] | 0.59 | 0.00 |
| 1024 | CS-LAT | 100 | 50 | 33 | 11 | 6 | 0.830 | 0.65 | [0.42, 0.82] | 0.25 | 0.15 |
| 1024 | MIXED | 100 | 46 | 37 | 12 | 5 | 0.830 | 0.66 | [0.41, 0.86] | 0.24 | 0.12 |
| 1024 | ALL | 300 | 159 | 85 | 45 | 11 | 0.813 | 0.61 | [0.40, 0.78] | 0.35 | 0.11 |

Agreement at 128 tokens across all six conditions (from EXP-004): 75.7% (146 both correct, 308 both wrong, 128 Q-correct/O-wrong, 18 Q-wrong/O-correct).

### G2.1 Per condition, all six conditions at 128 tokens (EXP-004)

| Condition | Stored vs J-QWEN | J-QWEN vs J-OSS | κ |
| --- | --- | --- | --- |
| EN-ORIG | 0.94 | 0.64 | 0.33 |
| EN-MATCH | 1.00 | 0.73 | 0.49 |
| CS-LAT | 0.90 | 0.72 | 0.43 |
| ROMAN | 0.94 | 0.81 | 0.56 |
| NATIVE | 0.92 | 0.85 | 0.62 |
| MIXED | 0.92 | 0.79 | 0.39 |

## G3. Does the conclusion change? (α = 0.05)

| Judge | Budget | Contrast | Δ (pp) | Exact p | Topic p | Significant (proposition) | Significant (topic) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| J-QWEN | 128 | CS-LAT vs EN-MATCH | −11 | 0.13 | 0.42 | no | no |
| J-QWEN | 128 | MIXED vs CS-LAT | −23 | <0.001 | 0.004 | yes | yes |
| J-QWEN | 128 | MIXED vs EN-MATCH | −34 | <0.001 | 0.030 | yes | yes |
| J-QWEN | 512 | CS-LAT vs EN-MATCH | −21 | <0.001 | 0.082 | yes | no |
| J-QWEN | 512 | MIXED vs CS-LAT | +4 | 0.57 | 0.65 | no | no |
| J-QWEN | 512 | MIXED vs EN-MATCH | −17 | 0.003 | 0.13 | yes | no |
| J-QWEN | 1024 | CS-LAT vs EN-MATCH | −24 | <0.001 | 0.018 | yes | yes |
| J-QWEN | 1024 | MIXED vs CS-LAT | −3 | 0.70 | 0.72 | no | no |
| J-QWEN | 1024 | MIXED vs EN-MATCH | −27 | <0.001 | 0.003 | yes | yes |
| J-OSS | 128 | CS-LAT vs EN-MATCH | −12 | 0.050 | 0.22 | no | no |
| J-OSS | 128 | MIXED vs CS-LAT | −8 | 0.18 | 0.24 | no | no |
| J-OSS | 128 | MIXED vs EN-MATCH | −20 | 0.002 | 0.067 | yes | no |
| J-OSS | 512 | CS-LAT vs EN-MATCH | −4 | 0.57 | 0.76 | no | no |
| J-OSS | 512 | MIXED vs CS-LAT | −6 | 0.34 | 0.44 | no | no |
| J-OSS | 512 | MIXED vs EN-MATCH | −10 | 0.087 | 0.31 | no | no |
| J-OSS | 1024 | CS-LAT vs EN-MATCH | −7 | 0.21 | 0.52 | no | no |
| J-OSS | 1024 | MIXED vs CS-LAT | −5 | 0.40 | 0.52 | no | no |
| J-OSS | 1024 | MIXED vs EN-MATCH | −12 | 0.043 | 0.22 | yes | no |

## G4. EXP-005 cost and failures

* openai/gpt-oss-120b: 300 calls, 261,224 input tokens, 25,234 output tokens, $0.054
* qwen/qwen3.8-27b: 600 calls, 299,795 input tokens, 233,669 output tokens, $1.175
* Total EXP-005: $1.229
* Persistent failures logged: 0; parse failures: 128|J-QWEN 0, 128|J-OSS 0, 512|J-QWEN 0, 512|J-OSS 0, 1024|J-QWEN 0, 1024|J-OSS 0

## G5. 128-token results, all six conditions (harmonised J-QWEN labels)

| Condition | Acc % | Wilson CI | Topic-boot CI | Stored | J-OSS | Topics 5/5 | Topics 0/5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EN-ORIG | 70 | [60.4, 78.1] | [50, 90] | 64 | 40 | 14 | 6 |
| EN-MATCH | 60 | [50.2, 69.1] | [40, 80] | 60 | 37 | 12 | 8 |
| CS-LAT | 49 | [39.4, 58.7] | [34, 64] | 43 | 25 | 3 | 4 |
| ROMAN | 37 | [28.2, 46.8] | [24, 50] | 33 | 24 | 1 | 6 |
| NATIVE | 32 | [23.7, 41.7] | [18, 46] | 28 | 21 | 0 | 8 |
| MIXED | 26 | [18.4, 35.4] | [12, 41] | 24 | 17 | 0 | 11 |

### G5.1 All 11 pairwise contrasts (J-QWEN)

| Contrast | Δ | b | c | Exact p | Holm (primary) | Topic p | Holm topic | Topic CI | Topics differing |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CS-LAT vs EN-MATCH | −11 | 27 | 16 | 0.13 | 0.13 | 0.42 | 0.42 | [-34, 13] | 15 |
| ROMAN vs EN-MATCH | −23 | 35 | 12 | 0.001 | 0.002 | 0.087 | 0.17 | [-46, 0] | 17 |
| NATIVE vs EN-MATCH | −28 | 36 | 8 | <0.001 | <0.001 | 0.031 | 0.12 | [-49, -6] | 15 |
| MIXED vs EN-MATCH | −34 | 45 | 11 | <0.001 | <0.001 | 0.030 | 0.12 | [-59, -7] | 15 |
| MIXED vs CS-LAT | −23 | 30 | 7 | <0.001 | <0.001 | 0.004 | 0.018 | [-35, -11] | 14 |
| EN-MATCH vs EN-ORIG | −10 | 20 | 10 | 0.099 | – | 0.69 | – | [-35, 15] | 6 |
| MIXED vs ROMAN | −11 | 19 | 8 | 0.052 | – | 0.069 | – | [-21, -1] | 11 |
| MIXED vs NATIVE | −6 | 14 | 8 | 0.29 | – | 0.46 | – | [-18, 6] | 9 |
| ROMAN vs CS-LAT | −12 | 25 | 13 | 0.073 | – | 0.057 | – | [-22, -2] | 16 |
| NATIVE vs CS-LAT | −17 | 27 | 10 | 0.008 | – | 0.033 | – | [-30, -4] | 13 |
| NATIVE vs ROMAN | −5 | 16 | 11 | 0.44 | – | 0.37 | – | [-13, 3] | 10 |

### G5.2 Same, stored labels (original PDF numbers)

| Contrast | Δ | b | c | Exact p | Holm (primary) | Topic p | Holm topic | Topic CI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CS-LAT vs EN-MATCH | −17 | 30 | 13 | 0.014 | 0.014 | 0.19 | 0.19 | [-39, 5] |
| ROMAN vs EN-MATCH | −27 | 37 | 10 | <0.001 | <0.001 | 0.036 | 0.073 | [-48, -5] |
| NATIVE vs EN-MATCH | −32 | 39 | 7 | <0.001 | <0.001 | 0.014 | 0.072 | [-53, -10] |
| MIXED vs EN-MATCH | −36 | 47 | 11 | <0.001 | <0.001 | 0.021 | 0.072 | [-61, -10] |
| MIXED vs CS-LAT | −19 | 29 | 10 | 0.003 | 0.007 | 0.015 | 0.072 | [-32, -6] |
| EN-MATCH vs EN-ORIG | −4 | 16 | 12 | 0.57 | – | 0.84 | – | [-26, 19] |
| MIXED vs ROMAN | −9 | 20 | 11 | 0.15 | – | 0.14 | – | [-19, 1] |
| MIXED vs NATIVE | −4 | 15 | 11 | 0.56 | – | 0.64 | – | [-16, 8] |
| ROMAN vs CS-LAT | −10 | 26 | 16 | 0.16 | – | 0.15 | – | [-21, 1] |
| NATIVE vs CS-LAT | −15 | 30 | 15 | 0.036 | – | 0.10 | – | [-30, 0] |
| NATIVE vs ROMAN | −5 | 18 | 13 | 0.47 | – | 0.37 | – | [-13, 3] |

### G5.3 J-OSS primary contrasts at 128 tokens

| Contrast | Δ | b | c | Exact p | Holm | Topic p | Holm topic |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CS-LAT vs EN-MATCH | −12 | 22 | 10 | 0.050 | 0.10 | 0.22 | 0.45 |
| ROMAN vs EN-MATCH | −13 | 22 | 9 | 0.029 | 0.088 | 0.15 | 0.44 |
| NATIVE vs EN-MATCH | −16 | 20 | 4 | 0.002 | 0.008 | 0.035 | 0.18 |
| MIXED vs EN-MATCH | −20 | 29 | 9 | 0.002 | 0.008 | 0.067 | 0.27 |
| MIXED vs CS-LAT | −8 | 18 | 10 | 0.18 | 0.18 | 0.24 | 0.45 |

### G5.4 GEE (J-QWEN), log-odds vs EN-MATCH or CS-LAT

| Contrast | Unit | β | Robust SE | p |
| --- | --- | --- | --- | --- |
| CS-LAT | prompt | -0.445 | 0.286 | 0.12 |
| CS-LAT | proposition | -0.445 | 0.264 | 0.091 |
| CS-LAT | topic | -0.445 | 0.493 | 0.37 |
| ROMAN | prompt | -0.938 | 0.291 | 0.001 |
| ROMAN | proposition | -0.938 | 0.273 | <0.001 |
| ROMAN | topic | -0.938 | 0.494 | 0.058 |
| NATIVE | prompt | -1.159 | 0.296 | <0.001 |
| NATIVE | proposition | -1.159 | 0.263 | <0.001 |
| NATIVE | topic | -1.159 | 0.473 | 0.014 |
| MIXED | prompt | -1.451 | 0.306 | <0.001 |
| MIXED | proposition | -1.451 | 0.310 | <0.001 |
| MIXED | topic | -1.451 | 0.606 | 0.017 |
| MIXED_vs_CS-LAT | prompt | -1.006 | 0.303 | <0.001 |
| MIXED_vs_CS-LAT | proposition | -1.006 | 0.257 | <0.001 |
| MIXED_vs_CS-LAT | topic | -1.006 | 0.293 | <0.001 |

### G5.5 Per-language accuracy (J-QWEN, %)

| Language | EN-ORIG | EN-MATCH | CS-LAT | ROMAN | NATIVE | MIXED |
| --- | --- | --- | --- | --- | --- | --- |
| Hindi | 70 | 60 | 45 | 40 | 40 | 30 |
| Bengali | 70 | 60 | 60 | 20 | 20 | 35 |
| Tamil | 70 | 60 | 50 | 35 | 35 | 15 |
| Telugu | 70 | 60 | 40 | 50 | 30 | 35 |
| Kannada | 70 | 60 | 50 | 40 | 35 | 15 |

### G5.6 Per-topic correct languages (of 5), J-QWEN, with provision and gold status

| Topic | Provision verified | Gold | EN-ORIG | EN-MATCH | CS-LAT | ROMAN | NATIVE | MIXED |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Citizenship Amendment Act Cut-off | Citizenship (Amendment) Act 2019, s. 2 | ok | 5 | 5 | 1 | 3 | 4 | 2 |
| Companies Act CSR Mandate | Companies Act 2013, s. 135(1) | ok | 5 | 5 | 3 | 2 | 0 | 0 |
| Covaxin vs Covishield | CDSCO approvals, Jan. 2021 | ok | 5 | 5 | 5 | 4 | 2 | 4 |
| GST Registration Exemption | CGST Act s. 22; Notif. 10/2019-CT | narrow | 5 | 5 | 4 | 2 | 4 | 1 |
| ISRO PSLV vs GSLV Mk III | ISRO launcher specifications | ok | 5 | 5 | 2 | 0 | 1 | 0 |
| Kharif vs Rabi Rice | ICAR crop-season references | simpl. | 5 | 5 | 5 | 4 | 4 | 4 |
| Lok Sabha vs Rajya Sabha Money Bill | Constitution, Arts. 109–110 | ok | 5 | 5 | 2 | 3 | 3 | 3 |
| National Park vs Wildlife Sanctuary | Wild Life (Protection) Act 1972, ss. 33, 35 | ok | 5 | 5 | 3 | 2 | 2 | 0 |
| Patents Act Compulsory License | Patents Act 1970, s. 84(1) | ok | 5 | 5 | 3 | 3 | 3 | 0 |
| SEBI Insider Trading Pre-Clearance | SEBI PIT Regulations 2015, Sch. B | ok | 5 | 5 | 4 | 2 | 1 | 1 |
| Arbitration Act Time Limit | Arbitration Act 1996, s. 29A | ok | 0 | 5 | 1 | 0 | 0 | 0 |
| PMFBY vs WBCIS | PMFBY/RWBCIS operational guidelines | ok | 0 | 5 | 0 | 0 | 0 | 0 |
| Classical Tamil vs Sanskrit Grammar | Philological references | ok | 5 | 0 | 3 | 1 | 0 | 3 |
| Medical Termination of Pregnancy Act | MTP Act 1971 (am. 2021), s. 3(2) | narrow | 5 | 0 | 0 | 1 | 0 | 0 |
| NEFT vs RTGS | RBI NEFT/RTGS directions | ok | 5 | 0 | 4 | 5 | 4 | 4 |
| RTI Third Party Information | RTI Act 2005, s. 11(1) | ok | 5 | 0 | 1 | 0 | 0 | 0 |
| Environment Clearance Public Hearing | EIA Notification 2006, para. 7 | narrow | 0 | 0 | 0 | 0 | 0 | 0 |
| IBC Section 7 Default Threshold | IBC 2016, s. 4 (₹1 crore from 2020) | ok | 0 | 0 | 0 | 0 | 0 | 0 |
| PM-KISAN vs Rythu Bandhu | PM-KISAN guidelines; Telangana G.O.s | dated | 0 | 0 | 3 | 2 | 1 | 0 |
| Supreme Court vs High Court Writ Jurisdiction | Constitution, Arts. 32, 226 | ok | 0 | 0 | 5 | 3 | 3 | 4 |

### G5.7 Response-side descriptors at 128 tokens (J-QWEN for errors/incompleteness)

| Condition | Script transitions | Prompt chars/tok Qwen3.8 | Prompt chars/tok Qwen2.5 (old) | Resp. chars | Mostly Brahmic % | Any Brahmic % | Ends mid-sentence | Hit 128 | Errors | Incomplete rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EN-ORIG | 0.0 | 5.83 | 5.82 | 538 | 0 | 0 | 82 | 100 | 30 | 0 |
| EN-MATCH | 0.0 | 4.65 | 4.64 | 529 | 0 | 0 | 87 | 100 | 40 | 0 |
| CS-LAT | 0.0 | 4.11 | 4.02 | 423 | 2 | 2 | 90 | 99 | 51 | 11 |
| ROMAN | 0.0 | 3.15 | 2.90 | 390 | 8 | 8 | 91 | 99 | 63 | 18 |
| NATIVE | 1.0 | 2.43 | 1.24 | 279 | 98 | 100 | 95 | 100 | 68 | 36 |
| MIXED | 5.0 | 3.70 | 2.49 | 303 | 88 | 98 | 92 | 100 | 74 | 38 |

### G5.8 Tipping points (J-QWEN)

| FPR | CS-LAT vs EN-MATCH | MIXED vs EN-MATCH | MIXED vs CS-LAT |
| --- | --- | --- | --- |
| 0.00 | 0.82 | 0.43 | 0.53 |
| 0.04 | 0.79 | 0.41 | 0.49 |
| 0.08 | 0.76 | 0.38 | 0.45 |
| 0.12 | 0.74 | 0.35 | 0.41 |
| 0.16 | 0.71 | 0.33 | 0.36 |

## G6. Final manuscript text exactly as built into the DOCX (build_paper.py)

**Title**

> Representation Effects in Indic Factual Question Answering: Script, Output Budget, and Judge Dependence

**Abstract**

> Comparisons of LLM factual accuracy across languages and scripts usually change the question along with its representation. We hold 100 propositions on 20 Indian public-policy topics fixed and render each in English, native script, Romanized text, Latin-script code-switching (CS-LAT) and mixed-script code-switching (MIXED) in five Indic languages (Hindi, Bengali, Tamil, Telugu, Kannada), and ask how much the measured differences depend on two evaluation choices: the output-token budget and the judge. With Qwen3.8-27B and a 128-token cap, judge-assessed accuracy is 60% for a template-matched English prompt and 49%, 37%, 32% and 26% for CS-LAT, Romanized, native-script and MIXED prompts, and MIXED is 23 points below CS-LAT (p < 0.001; topic-level p = 0.004). Almost every response hit that cap, and Brahmic-script answers fit half as many characters into it. Re-answering the key conditions with 512 and 1,024 tokens removes the MIXED–CS-LAT gap under both a self-judge (+4 and −3 points; p ≥ 0.57) and a judge from another model family (−6 and −5; p ≥ 0.34). The English–CS-LAT gap behaves differently: under the self-judge it grows with the budget, to 24 points at 1,024 tokens (topic-level p = 0.018), while under the second judge it is 4–12 points and never significant. The two judges agree on 75–81% of outputs (κ = 0.47–0.61), and no human validation of either was performed. Measured representation effects are therefore sensitive to the output budget and to the evaluator, and should not be read as effects of representation without checking both. Prompts, outputs, judgements, a gold-answer ledger and code are released.

**Index Terms**

> multilingual evaluation, code-switching, script, Indic languages, output budget, LLM-as-a-judge, judge agreement, paired evaluation

**I ¶3**

> We build the comparison so that they can be. Each of 100 propositions is rendered in five paired representations (Table I). Two of them, CS-LAT and MIXED, are meant to differ only in whether the Indic words are written in Latin or Brahmic script; this holds word for word in Hindi, Bengali and Tamil, while in Telugu and Kannada the question word also differs (Section III-A). We add a second English condition after finding that the original English template was more specific than the template shared by the other four conditions (Section III-B). We then ask whether the differences we measure survive two changes to the evaluation that representation studies rarely make: a larger output budget (512 and 1,024 tokens instead of 128) and a judge from a different model family.

**I Research questions**

> **Research questions.** RQ1: at a fixed output budget and judge, does judge-assessed accuracy depend on representation when the proposition is held fixed? RQ2: does mixed-script code-switching lower accuracy relative to the same code-switched words in Latin script? RQ3: do these differences change when the output budget grows? RQ4: do they change with the judge, and how far do two judges agree? RQ5: is the script contrast associated with input tokenization length? Hallucination detectors and mitigation are outside the scope of this paper.

**I Contributions**

> **Contributions.** (1) A paired six-condition design for Indic factual QA, with a matched-English control that removes a template confound we found in our first run. (2) A controlled three-budget rerun showing that the 23-point mixed-script penalty measured at 128 tokens disappears at 512 and 1,024 tokens under two judges, while the English–code-switching gap moves in the opposite direction under one judge only. (3) Judge disagreement as a result: harmonising the judge configuration shrinks the English–code-switching gap at 128 tokens from 17 to 11 points, the two judges agree on 75–81% of outputs, and whether the English advantage is significant depends on which judge is used. (4) Inference that treats the 20 topics as the unit of independent evidence, and a release of prompts, outputs, both judges' labels, a gold-answer ledger and evaluation scripts.

**I Findings in brief**

> **Findings in brief.** Evaluating multilingual LLMs across representation conditions is sensitive to the output-token budget and to the choice of evaluator, and observed differences should not automatically be interpreted as representation effects. At 128 tokens, accuracy falls from English to the Indic representations and mixed script is lowest. Almost every response hits that cap and Brahmic-script answers are about half as long in characters; with 512 or 1,024 tokens, MIXED and CS-LAT do not differ under either judge. The English advantage over Latin-script code-switching is significant at the topic level only under the self-judge at 1,024 tokens; under the cross-family judge it is small at every budget. Neither judge has been validated against human labels, so we report this as judge sensitivity, not as evidence that either judge is right.

**II Multilingual evaluation**

> **Multilingual evaluation for Indic languages.** IndicNLPSuite and IndicXTREME provide corpora and task benchmarks for Indic languages [2], [3], and MEGA compares generative models across many languages and tasks [1]. Such benchmarks answer how well a model performs per language, but their per-language items are not the same questions. Romanized input has itself been proposed as a bridge to Indic languages for LLMs [23]; our ROMAN condition measures the same factor on fixed propositions.

**II Tokenization**

> **Tokenization.** Subword vocabularies fragment low-resource scripts into more tokens [7], [10], with measurable differences in cost and quality across languages [5], [6]. The same premium applies to generated text: an answer in a script that costs more tokens per character fits less content into a fixed output limit, which is the mechanism our budget experiment isolates. Our mediation analysis asks whether the input-side quantity explains the script contrast.

**II Judges**

> **Factuality evaluation and LLM judges.** We use closed-book questions with a gold answer, closer in spirit to TruthfulQA-style checks than to long-form factual precision scoring [11], [12]. LLM graders are convenient but biased, for example towards their own outputs, answer position and length [13], [24], [25], and their agreement with humans and with each other is lower in many non-English languages, including Indic languages [26], [27]. We therefore grade with two judges from different model families and report their disagreement as a result.

**Fig. 1 caption**

> Fig. 1. Study design. Each proposition is rendered in six conditions and answered once by Qwen3.8-27B under greedy decoding with a 128-token limit; responses are graded against the gold answer by the same model (J-QWEN). The follow-up (Section VI-B) re-answers three conditions with 512 and 1,024-token limits and grades every budget with J-QWEN and with gpt-oss-120b (J-OSS). Key contrasts: EN-MATCH vs. CS-LAT (code-switching) and CS-LAT vs. MIXED (script).

**Table I caption**

> One proposition in all six conditions (Hindi). In Hindi, CS-LAT and MIXED contain the same words in the same order and differ only in the script of *ke*, *ya*, *kya hai* (also true for Bengali and Tamil; in Telugu and Kannada the question word differs, Section III-A). The topic string stays in Latin script in every condition, so NATIVE contains one Latin–Brahmic boundary per prompt.

**III-A conditions**

> Table I defines the six conditions. In NATIVE, ROMAN, CS-LAT and MIXED the question frame is one fixed template (“main rule, date or parameter regarding *X*”) with *X* the topic string; only the rendering varies. ROMAN and NATIVE render the same Indic frame in Latin and Brahmic script, except in Hindi, where ROMAN uses *tareekh* and NATIVE *tithi* for “date”. CS-LAT replaces part of the frame with English words (“main rule”, “date”, “parameter”, and in Hindi and Bengali also “regarding”), and MIXED writes the remaining Indic words of CS-LAT in native script. In Hindi, Bengali and Tamil, CS-LAT and MIXED are word-for-word transliterations of each other. In Telugu and Kannada they are not: the question word is *enti* vs. ఏమిటి (*emiti*) in Telugu and *yenu* vs. ಯಾವುದು (*yāvudu*, “which”) in Kannada. We report the CS-LAT–MIXED contrast on all 100 propositions, as planned, and on the 60 word-identical ones as a sensitivity analysis. Fluent speakers of all five languages, including the author (Telugu) and a teammate (Hindi, Telugu, Kannada), reviewed the prompt templates and judged them natural and correct. This was a yes/no check without item-level ratings; the reviewers saw the templates, not the model's outputs, and the check establishes neither full semantic equivalence nor the validity of the judges.

**III-B amendment**

> In the first run (EXP-002) the English prompts used two question templates (“key structural or operational difference between *X*” and “specific prerequisite condition or timeline applies to *X*”), while all other conditions used the single generic template. English-versus-Indic comparisons were therefore confounded with question type, a flaw we found only when auditing the raw prompt strings. We added EN-MATCH, the generic template in English (100 prompts, same gold answers), and ran it in a second run (EXP-003) with the same model and decoding settings, without modifying the earlier results. The two runs did not grade alike: EXP-002 called the judge at temperature 0.3 with the answering system prompt, EXP-003 at temperature 0 with an evaluator system prompt (Section IV). We therefore re-graded all 600 outputs with the EXP-003 configuration; all comparisons below use these harmonised labels and EN-MATCH as the English reference. EN-ORIG and EN-MATCH do not differ detectably (70% vs. 60%; exact p = 0.10, topic-level p = 0.69).

**III-C gold answers**

> **Gold answers.** Each topic has one gold answer, shared by its five language groups and all six conditions. The benchmark stores an evidence snippet and a source URL with each; the snippets are template-generated paraphrases rather than quotations, and the URLs point to agency home pages (e.g. rbi.org.in) rather than to specific documents. The author and, separately, volunteer reviewers checked the gold answers for factual correctness against public sources, and the author verified each answer against its governing provision, as in force in October 2026, for currency and for completeness relative to the question actually asked (Appendix A, Table VII; a per-topic ledger is released). The volunteer check was not logged item by item and no agreement statistic was computed, so we report it as a check rather than a measurement. All 20 answers are consistent with the provision identified. One describes a scheme that has since been replaced (Telangana's Rythu Bandhu, now Rythu Bharosa). Three are narrower than the generic question allows, so that other correct answers exist: the GST registration threshold (₹40 lakh applies to suppliers of goods, ₹20 lakh to services), the MTP Act (two practitioners are required only between 20 and 24 weeks) and the environmental-clearance public hearing (the gold lists two of several exemptions). Removing these three topics changes no conclusion (Appendix B). Gold-answer checks establish that the reference is right; they do not show that the judge grades model answers correctly, which no human has yet assessed on these outputs (Section VII). Agreement figures in older project documents (e.g. κ = 0.719) concern a different, earlier pilot whose annotation files are not in the repository; they are not used.

**IV intro**

> Fig. 1 summarizes the pipeline: 100 propositions are rendered in six conditions, answered once by the primary model under greedy decoding, graded against the gold answer, and analysed at three levels of clustering. Section VI-B adds a follow-up run with a larger output budget.

**IV Models**

> **Models.** The primary model is served by Groq under the API identifier `qwen/qwen3.8-27b`, which is recorded in every prediction row and in the response metadata of the follow-up. The provider lists it as an Alibaba Cloud model, and a public checkpoint of that name exists (Qwen/Qwen3.8-27B, 27.8B parameters, Apache-2.0). That checkpoint's tokenizer reproduces the API's prompt-token counts for all 600 prompts up to a constant chat-template offset of 48 tokens, and counts 125–128 tokens for responses the API reports as 128, so the tokenizer is established; whether the provider serves exactly those weights, and at what numerical precision, we cannot verify. We call the model Qwen3.8-27B. Older project documents call it “Qwen-2.5-27B” and the repository configuration lists `qwen/qwen3.6-27b`; neither produced the reported outputs. The second model is ALLaM-2-7B (`allam-2-7b`) [14]. All results are single-run. Greedy decoding on the hosted API was not fully deterministic: 84–85% of 512-token responses begin with exactly the 128-token response to the same prompt, and 78–91% of 1,024-token responses with the 512-token response; the rest diverge.

**IV Prompting**

> **Prompting and output budget.** Each prompt is sent with the system message “You are a helpful assistant answering questions from Indian users. Questions may mix an Indian language with English. Answer factually, accurately, and concisely.” Decoding is greedy (temperature 0, top-p 1) with at most 128 output tokens in the main runs. The model almost never stops on its own: 598 of 600 responses used all 128 tokens, and 82–95% end mid-sentence in every condition, English included. The provider's finish reason was not logged in the main runs; it was logged in both follow-up runs.

**IV Judging**

> **Judging.** A judge receives the question as the model saw it, the gold answer and the response, and returns CORRECT or HALLUCINATED with a short reason (Appendix C). Three label sets exist. *Stored*: the labels saved with the predictions; EXP-002 obtained them from Qwen3.8-27B at temperature 0.3 with the answering system prompt (a side effect of reusing the generation client), EXP-003 at temperature 0 with the system prompt “You are an expert factuality evaluator.” *J-QWEN*: all 600 outputs re-graded by Qwen3.8-27B with the EXP-003 configuration, the one the study intended; these labels are the primary analysis. *J-OSS*: the same rubric applied by gpt-oss-120b (`openai/gpt-oss-120b`, temperature 0, low reasoning effort), a judge from a different model family that did not produce the answers. J-QWEN reproduces the stored labels on all 100 EN-MATCH items (same configuration) and on 90–94% of items in the other conditions. No judge has been validated against human labels on these outputs, and we do not treat either as the more accurate one. “Accuracy” below is the share of responses a judge labels CORRECT: a judge-assessed quantity, not a direct measurement of recall.

**IV Statistics**

> **Statistics.** Observations are nested. A *prompt* is one string sent to the model. A *proposition* is a fact in one language group, rendered as six paired prompts. A *topic* (e.g. NEFT vs. RTGS) contains five propositions, one per language, with the same gold answer; across the five matched-template conditions it contributes 25 prompts. A proposition-level test asks whether the model, given these 100 facts, does better in one representation than in another. A topic-level test asks whether the difference should be expected to recur on new topics; with 20 topics it has much less power, but it matches the generalisation most readers want, so we report both. At the proposition level we use exact McNemar tests [15] with Holm correction [16] within a pre-specified family of five contrasts: each of NATIVE, ROMAN, CS-LAT and MIXED against EN-MATCH, and MIXED against CS-LAT. At the topic level we use an exact sign-flip permutation test over all 2²⁰ sign patterns of the 20 per-topic accuracy differences and a percentile bootstrap over topics (10,000 resamples, fixed seed), with Holm correction within the same family. Logistic GEE with independence working correlation and robust covariance clustered at prompt, proposition and topic level [18] is reported in Appendix B; with 20 clusters robust standard errors are anti-conservative [19], [20], so topic-level conclusions do not rest on it. Wilson intervals [17] are given for single proportions; the design effect is 1 + (*m* − 1)ρ with ρ from the one-way ANOVA estimator [21]. The follow-up (Section VI-B) has the same three contrasts at every budget, fixed in the analysis scripts before its outputs were graded: CS-LAT vs. EN-MATCH, MIXED vs. CS-LAT and MIXED vs. EN-MATCH, plus the change in each gap between budgets, each under both judges. Everything else is exploratory. All numbers are recomputed from the raw files by the scripts in Appendix E.

**V heading**

> V. RESULTS AT A 128-TOKEN BUDGET

**V-A**

> Table II and Fig. 2 give the main result under the harmonised judge. Relative to EN-MATCH (60%), accuracy is 49% for CS-LAT, 37% for ROMAN, 32% for NATIVE and 26% for MIXED, differences of 11, 23, 28 and 34 points. At the proposition level the ROMAN, NATIVE and MIXED differences are significant after Holm correction (adjusted p ≤ 0.002); the CS-LAT difference is not (p = 0.13). With the stored labels, which graded EN-MATCH and the Indic conditions under different judge settings, the CS-LAT gap was 17 points (p = 0.014): about a third of it came from the grading difference. The ordering among the three non-English-script conditions is uncertain: ROMAN vs. MIXED gives p = 0.052 and NATIVE vs. MIXED p = 0.29 (Table VIII).

**Table II caption**

> Qwen3.8-27B accuracy on the 100 paired propositions at a 128-token budget, harmonised judge (J-QWEN). Δ: difference in correct answers out of 100 relative to EN-MATCH. Exact p: two-sided exact McNemar; Holm: within the five primary contrasts (MIXED vs. CS-LAT is in the text and Table VIII). Topic p: exact sign-flip permutation test on the 20 per-topic differences, Holm-adjusted in parentheses. Stored, J-OSS: accuracy (%) under the original labels and under the cross-family judge. †EN-ORIG vs. EN-MATCH, exploratory.

**Fig. 2 caption**

> Fig. 2. (a) Accuracy (J-QWEN) with Wilson 95% intervals (n = 100 per condition; points not independent within topic). (b) Number of languages (of five) in which each topic is answered correctly, per condition. Topics sorted by EN-MATCH, then EN-ORIG.

**Fig. 3 caption**

> Fig. 3. Accuracy by language and condition (J-QWEN; n = 20 per cell).

**V-A uncertainty**

> The uncertainty is larger than the Wilson intervals imply. Topic-bootstrap intervals are wider (for EN-MATCH [40, 80] against Wilson [50.2, 69.1]) because accuracy is concentrated by topic: two topics (Environment Clearance Public Hearing, IBC Section 7) are wrong in every condition, and twelve are right for English in all five languages (Fig. 2b). The two all-wrong topics fail for different reasons. For IBC the model gives the pre-2020 default threshold of ₹1 lakh, a genuine error; for Environment Clearance the gold answer lists exemptions that the generic question does not ask for (Section III-C).

**V-B heading**

> B. Mixed vs. Latin-script code-switching

**V-B**

> Writing the code-switched prompt with its Indic words in Brahmic rather than Latin script lowers accuracy from 49% to 26%, a 23-point drop. Of 37 propositions that differ, 30 favour CS-LAT and 7 favour MIXED (exact p < 0.001, Holm p < 0.001). The drop appears in all five languages (Fig. 3); the mean of the 20 per-topic differences is 23 points (bootstrap 95% CI [11, 35]; permutation p = 0.004, Holm-adjusted 0.018; 14 of 20 topics differ), and the GEE odds ratio is 0.37 (topic-clustered 95% CI 0.21–0.65). On the 60 propositions in Hindi, Bengali and Tamil, where the two prompts are word-for-word identical, the drop is 25 points (p = 0.0015; topic-level p = 0.016). Excluding the three topics with narrow gold answers leaves it at 23.5 points (p < 0.001). Under the stored labels it was 19 points (p = 0.003; topic-level p = 0.015, Holm-adjusted 0.072). At a 128-token budget, then, the mixed-script penalty is the most consistent result in the study.

**V-B note**

> Section VI shows that this result does not survive a larger output budget. Here we note only why that check is needed: 88% of MIXED responses are written mostly in Brahmic script, against 2% of CS-LAT responses, so the prompt script also changes the script of the answer, and with it how much answer fits into 128 tokens.

**V-C**

> Observations within a topic are strongly dependent. In the five matched-template conditions the intra-topic correlation is ρ = 0.27, the design effect 7.5 and the effective sample size 67 out of 500. Fig. 4a and Table IX show what this does. For CS-LAT against EN-MATCH, the GEE p value is 0.12 at prompt level, 0.09 at proposition level and 0.37 at topic level, and the topic-level permutation test gives p = 0.42 (bootstrap 95% CI for the mean per-topic difference [−34, 13] points). For ROMAN, NATIVE and MIXED against EN-MATCH the topic-level permutation p values are 0.087, 0.031 and 0.030, and none survives Holm correction at topic level (smallest adjusted value 0.12). Only MIXED vs. CS-LAT survives Holm correction at every level (adjusted topic-level p = 0.018). At this budget the English-vs-Indic differences are consistent in direction, but at the level of topics only the larger ones approach significance, and the English–CS-LAT gap does not.

**Fig. 4 caption**

> Fig. 4. (a) GEE log-odds differences from EN-MATCH (J-QWEN) with robust 95% CIs at three clustering levels (circle: prompt; square: proposition; diamond: topic). Intervals widen at topic level, where the CS-LAT and ROMAN intervals include zero. (b) Per-topic accuracy difference, CS-LAT minus MIXED (20 topics; band: bootstrap 95% CI of the mean; line: mean).

**V-D languages**

> Accuracy by language is in Fig. 3. MIXED is below CS-LAT in all five languages; EN-MATCH is above CS-LAT in four and tied with it in Bengali. A permutation test of whether the condition profile depends on language (statistic: interaction sum of squares of the language × condition accuracy table; null: language labels permuted among the five propositions of each topic; 10,000 permutations) gives p = 0.17. With 20 observations per cell this test has little power, so we report no detectable language dependence, not that languages behave alike; Bengali and Telugu differ visibly in the ROMAN column (20% vs. 50%), and nothing here can separate chance from effect.

**V-D models**

> ALLaM-2-7B answers 10% of matched-English questions correctly and 5%, 2%, 2% and 3% in CS-LAT, ROMAN, NATIVE and MIXED (stored labels), so the representation contrast cannot be measured on it. The five-condition rank correlation with Qwen3.8-27B under the stored labels (ρ = 0.67, p = 0.22) describes a floor, not a replication. We make no claim about other model families.

**VI heading**

> VI. TOKENIZATION AND THE OUTPUT BUDGET

**VI-A heading**

> A. Input tokenization (exploratory)

**VI-A tokenization**

> Subword fragmentation is a standard explanation for weaker performance on non-Latin scripts. Our earlier analysis measured characters per token with the Qwen2.5-7B tokenizer, which does not match the served model: it disagrees with the API's prompt-token counts and would put capped 128-token responses at 120–305 tokens. With the Qwen3.8-27B tokenizer, which does match (Section IV), Brahmic text is less fragmented than that analysis implied: prompts average 2.43 characters per token in NATIVE and 3.70 in MIXED, against 4.65 in EN-MATCH and 4.11 in CS-LAT (previously 1.24 and 2.49 for NATIVE and MIXED). Within the CS-LAT–MIXED contrast, MIXED lowers characters per token (*a* = −0.41, SE 0.10), but once condition is controlled the mediator's association with correctness is not significant and has the wrong sign for a fragmentation account (*b* = −0.40, SE 0.23, p = 0.08; 95% CI −0.85 to 0.05; Sobel p = 0.11). The implied indirect effect is positive while the total effect is negative (−1.01). Because characters per token is almost determined by condition and language in this design, the test has little leverage: it is exploratory and does not rule out a tokenization effect. Across the six conditions, characters per token and accuracy are rank-correlated (ρ = 0.83), but six points that differ in language frame, script and answer length identify nothing (Fig. 5c).

**Fig. 5 caption**

> Fig. 5. (a) Mean response length for EN-MATCH, CS-LAT and MIXED at 128, 512 and 1,024 tokens; labels give the % of responses that hit the cap. (b) Accuracy of the same 300 prompts at each budget, graded by J-QWEN (solid) and J-OSS (dashed). (c) Condition-level prompt characters per token (Qwen3.8 tokenizer) against accuracy at 128 tokens (six points; descriptive only).

**VI-B heading**

> B. Response script, length and the output budget

**VI-B response side**

> The prompt script largely determines the response script: 98% of NATIVE and 88% of MIXED responses are written mostly in Brahmic script (more than half of their letters), against 8% and 2% for ROMAN and CS-LAT and none for English. Brahmic answers cost more tokens per character (2.2–2.4 characters per token in NATIVE and MIXED responses against 4.1 in English ones), and nearly all responses used the full 128 tokens, so mean response length is 529 characters in EN-MATCH but 279 in NATIVE and 303 in MIXED (Fig. 5a). Among errors, the share whose judge reason mentions an incomplete or missing answer (a keyword rule, Appendix C) is 0 of 40 in EN-MATCH, 11 of 51 in CS-LAT, 36 of 68 in NATIVE and 38 of 74 in MIXED. The rule depends on the judge's wording and does not measure truncation, but it points the same way.

**VI-B budget reruns**

> To separate script from budget we re-ran EN-MATCH, CS-LAT and MIXED (300 prompts) twice, with 512 and with 1,024-token limits, changing nothing else: same model identifier, system prompt, decoding settings and prompts. Every budget was graded by J-QWEN and by J-OSS, so each comparison across budgets uses one judge (Table III, Fig. 5b). At 1,024 tokens the cap no longer binds for English (95 of 100 responses stop on their own) and binds less for code-switched answers (61 CS-LAT and 36 MIXED responses stop). The MIXED–CS-LAT gap, −23 points at 128 tokens under J-QWEN, is +4 at 512 and −3 at 1,024 (p = 0.57 and 0.70); under J-OSS it is −8, −6 and −5, never significant. Between 128 and 1,024 tokens it narrows by 20 points under J-QWEN (topic-bootstrap CI [5, 34], permutation p = 0.023). On the 60 word-identical propositions the picture is the same (J-QWEN at 1,024 tokens: 65% vs. 60%, p = 0.58). The English–CS-LAT gap moves the other way under J-QWEN, from −11 at 128 to −21 at 512 and −24 at 1,024 tokens (exact p < 0.001; topic-level p = 0.018, Holm-adjusted 0.036 within the three follow-up contrasts), whereas under J-OSS it is −12, −4 and −7 and not significant at any budget (p ≥ 0.050).

**Table III caption**

> Output-budget follow-up: the same 300 prompts answered with 128, 512 and 1,024 tokens, each budget graded by both judges. Accuracy (%) per condition; gaps in points with exact McNemar p / topic-level permutation p. Cap: responses (of 100) that hit the output limit, EN-MATCH / CS-LAT / MIXED.

**VI-B conclusions**

> Three conclusions follow. First, the 128-token MIXED penalty is not evidence that script alternation harms recall: once the budget allows longer answers, mixed-script and Latin-script code-switched prompts yield similar accuracy under both judges. Its most likely source is that Brahmic-script answers reach the cap before reaching the fact, and answers a human would call incomplete are then graded as wrong; the EN-MATCH answer on the MTP Act, for instance, correctly states the one-practitioner rule for the first 20 weeks, is cut off before the 20–24-week rule, and is graded HALLUCINATED. Second, NATIVE and MIXED behave alike at 128 tokens (32% and 26%, p = 0.29) although MIXED has five script boundaries per prompt and NATIVE one, which also argues against a boundary-density account. Third, the English advantage is unstable: it grows with the budget under one judge and stays small under the other. We cannot tell from these data which judge is closer to a careful human reader, so the instability itself is the finding.

**VII heading**

> VII. JUDGE DEPENDENCE

**VII judge dependence**

> The judge matters in three ways. *Configuration.* Our first run graded the Indic conditions at temperature 0.3 with the answering system prompt and EN-MATCH at temperature 0 with an evaluator prompt. Harmonising the configuration changed 6–10% of the labels in each re-graded condition and moved CS-LAT accuracy from 43% to 49%, so the stored English–CS-LAT gap (17 points) exceeded the harmonised one (11). *Family.* Table IV gives agreement between J-QWEN and J-OSS by budget and condition. Agreement is 74.7% at 128 tokens (κ = 0.47), 80.0% at 512 (κ = 0.59) and 81.3% at 1,024 (κ = 0.61), with wide topic-bootstrap intervals for κ. Disagreements run mostly one way: J-QWEN labels CORRECT 30–36% of the answers J-OSS labels wrong, whereas J-OSS labels CORRECT 6–11% of the answers J-QWEN labels wrong. In the disagreements we inspected, J-QWEN accepted answers that were on topic and accurate but did not state the gold fact (for example, answers that only name the governing Act), and J-OSS rejected them; the rubric (“judge only factual correctness and whether it actually addresses the question”) does not say which reading is intended, and truncated answers make such cases common. *Conclusions.* The MIXED–CS-LAT conclusion depends on the judge at 128 tokens (significant under J-QWEN only) but not at 512 or 1,024 tokens (not significant under either). The English–CS-LAT conclusion depends on the judge at both larger budgets. No human gold-standard labels were collected for any output, so these results establish that conclusions are sensitive to the judge, not which judge is right.

**Table IV caption**

> Agreement between the two judges on the same 300 outputs at each budget. Agree: share of identical labels; κ: Cohen's kappa with topic-bootstrap 95% CI; Q✓O✗: J-QWEN CORRECT and J-OSS wrong; Q✗O✓: the reverse. No human labels were collected.

**VII tipping**

> Table V turns the remaining uncertainty into tipping points. Assuming English answers are judged without error, it gives the sensitivity the judge would need on the comparison condition for that condition's true accuracy to equal the reference's. A correction applied equally to both conditions (the Rogan–Gladen estimator [22]) divides a gap by TPR − FPR and can only enlarge it, so a common-error grid cannot show robustness; the relevant threat is differential error. At a false-accept rate of 0.08, erasing the CS-LAT gap would need a judge that rejects 24% of truly correct CS-LAT answers (sensitivity 0.76), and erasing the MIXED gap one that rejects 62% (0.38). These are hypothetical error rates, not estimates of the judge's actual errors, which are unknown; the cross-family disagreement shows they are not small. A crude check agrees: on the 330 outputs whose gold answer contains numerals, the J-QWEN label matches whether all gold numerals appear in the response 67% of the time, with disagreements in both directions (73 accepted answers lack the figure; 35 rejected ones contain it).

**Table V caption**

> Sensitivity the judge would need on the comparison condition for its true accuracy to equal the reference condition's, at the given false-accept rate (J-QWEN, 128 tokens). Reference answers assumed judged without error. Lower entries mean a larger error would be needed.

**VIII Discussion 1**

> What the data support is narrower than the design promised, and different from what our first run suggested. Evaluating multilingual LLMs across representation conditions is sensitive to the output-token budget and to the choice of evaluator, and observed differences should not automatically be interpreted as representation effects. For this model and these 20 topics, the clearest representation effect at a 128-token budget, the mixed-script penalty, disappears when answers can be longer, under both judges; the English advantage over code-switching appears or disappears with the judge. We do not claim that native script or code-switching damages factual recall, and we make no claim about other models.

**VIII Discussion 2**

> The practical lesson is methodological. Output caps are often set low to save cost, and tokenizers make some scripts more expensive per character, so a shared cap gives answers in those scripts less room. Studies that compare languages or scripts through generated answers should report how often the cap binds in each condition and show that conclusions hold at a non-binding budget; judges should be configured identically across conditions, at least two judges from different families should be used, and their agreement should be reported per condition. Whether this cautionary result is novel enough for a given venue depends on prior work on tokenization premiums and multilingual judge reliability [5], [6], [26], [27], which documents the ingredients but, to our knowledge, not their combined effect on paired representation contrasts. Table VI lists claims we examined.

**Table VI caption**

> Claims examined and not supported, or supported only under some evaluation settings.

**IX Limitations**

> **Topics.** Twenty topics with heavy within-topic concentration bound what any statistic can show (effective n ≈ 67 of 500). A 25-proposition expansion has been written but not evaluated. **Output budget.** At 1,024 tokens, 39 CS-LAT and 64 MIXED responses still hit the cap; we re-ran three of the six conditions and did not test an instruction fixing the answer language. **Judges.** Two LLM judges that disagree on a fifth to a quarter of items, and no human labels on any output; a stratified, blinded sample of 210 outputs and an annotation protocol are released but not annotated. **Questions and gold answers.** One generic template that under-specifies the target for several topics; volunteer gold checks without an item-level record; one superseded scheme. **Prompts.** The fluent-speaker review was an informal yes/no check of the templates; CS-LAT and MIXED differ by one word in Telugu and Kannada, and Hindi ROMAN is not a transliteration of Hindi NATIVE. **Models and languages.** One informative model, served under an API identifier whose underlying weights we cannot independently verify, and five languages. **Single run.** No repeated sampling; hosted greedy decoding was not fully deterministic, and API behaviour can change over time.

**X Ethics**

> Evaluations like this one guide where civic and legal information systems are considered safe to deploy for speakers who write the way our conditions do. Overstated gaps could discourage building for these users; understated ones could hide failures. We therefore report effect sizes with their dependence on clustering, output budget and judge. The prompts contain no personal data. The benchmark contains legal and policy facts that become outdated (one already has) and should not be used as legal advice. We do not estimate how many people use each representation, and make no claim about it.

**Reproducibility**

> All numbers, tables and figures are produced from the raw files by the scripts in `paper_v2/scripts/` (Appendix E). The two follow-up runs cost $1.10 (512 tokens plus re-grading of the 128-token outputs) and $1.23 (1,024 tokens) at the provider's list prices in October 2026; all 2,700 follow-up judgements parsed, and no call failed after retries. The project's budget ledger records $0.21 for the earlier runs but priced every call at a flat $0.08 per million tokens; at list prices the Qwen3.8-27B generation and grading in EXP-002 and EXP-003 would cost about $2.1. The provider's billing record is the authoritative figure.

**App. A.1**

> Table VII lists the 20 topics, the provision against which each gold answer was verified, the outcome, and the number of languages (of five) in which each condition was answered correctly under J-QWEN. Topics are Indian public-policy and regulatory subjects, several comparing two schemes or institutions (e.g. NEFT vs. RTGS, Covaxin vs. Covishield, PSLV vs. GSLV Mk III); not all are statutes, so we call them public-policy topics. Gold column: *ok*, consistent and adequate; *simpl.*, a correct simplification; *narrow*, other correct answers to the generic question exist; *dated*, the scheme has been superseded.

**Table VII caption**

> Topics, provision used to verify the gold answer, verification outcome, and languages (of five) answered correctly per condition (Qwen3.8-27B, J-QWEN, 128 tokens).

**App. B**

> Excluding the three topics with narrow gold answers (GST, MTP Act, Environment Clearance; 85 propositions), the J-QWEN differences from EN-MATCH are −12 (CS-LAT, p = 0.16), −25 (ROMAN, p = 0.002), −32 (NATIVE, p < 0.001) and −35 points (MIXED, p < 0.001), and MIXED vs. CS-LAT is −23.5 points (p < 0.001; topic-level p = 0.007). Table VIII gives all pairwise contrasts and Table IX the GEE estimates.

**Table VIII caption**

> All pairwise contrasts, J-QWEN labels, 128 tokens (proposition-level exact McNemar; b: the second-named (reference) condition correct and the first wrong; c: the reverse; topic-level permutation p and bootstrap CI for the change, uncorrected). The first five rows are the primary family.

**Table IX caption**

> Logistic GEE (independence working correlation, robust covariance), J-QWEN labels, 128 tokens. β̂ is the log-odds difference from EN-MATCH (first four blocks, 500 observations) or from CS-LAT (last block, 200). Topic-level robust SEs with 20 clusters are anti-conservative.

**App. C**

> **Incompleteness rule.** A response is flagged when (i) it used the full 128 completion tokens, (ii) its last non-space character is not a sentence-final mark, (iii) the judge labelled it incorrect, and (iv) the judge's reason matches one of *incomplete, truncated, cut off, abrupt, unfinished, missing specific, missing parameter, fails to finish*. Condition (iv) depends on the judge's wording; the rule is a descriptive device, not a measure of truncation. **Judge prompt.** “You are grading whether a model's ANSWER to a user QUESTION is factually correct. You are given a trusted GOLD answer. The answer may mix an Indian language with English (code-switching) and may be phrased very differently from the gold—that is fine. Judge ONLY factual correctness and whether it actually addresses the question.” Output: `VERDICT: <CORRECT or HALLUCINATED> | REASON: <max 12 words>`. **Judge settings.** Stored, EXP-002: Qwen3.8-27B, temperature 0.3, at most 256 tokens, system prompt “You are a helpful assistant answering questions from Indian users. Questions may mix an Indian language with English (code-switching). Answer accurately and concisely in the same mixed style the user used.” Stored, EXP-003, and J-QWEN: temperature 0, top-p 1, at most 256 tokens, system prompt “You are an expert factuality evaluator.” J-OSS: gpt-oss-120b, temperature 0, top-p 1, low reasoning effort, at most 1,024 tokens, same system prompt. All 2,700 follow-up judgements (1,800 at 128/512 tokens, 900 at 1,024 tokens) were parsed. **Script transitions.** Words are maximal letter runs, each labelled Latin or Brahmic (U+0900–U+0DFF); transitions are label changes between consecutive words, giving 5.0 per MIXED prompt, 1.0 per NATIVE prompt (the Latin topic string) and 0 elsewhere. **Mostly Brahmic.** More than half of a response's letters and combining marks lie in U+0900–U+0DFF. **Templates.** All 20 Indic templates are listed in the released prompt-validation protocol.

**App. D**

> A normal-approximation calculation for a 45-topic design (225 paired propositions, design effect 1 + (5 − 1)ρ, binary variance at p̄ = 0.4, two-sided α = 0.05) with ρ = 0.2663 and a 21-point effect gives power 88.6% (minimum detectable effect 18.6 points); the same formula gives 55.9% for the 20 evaluated topics. Those parameters come from the first English template and the stored labels. With the harmonised labels (ρ = 0.27) the 11-point English–CS-LAT gap would have power 38% with 45 topics and 19% with 20, and a 23-point gap 93% and 63%. The formula ignores pairing and is a rough projection; the 25 new propositions have not been evaluated.

**App. E**

> Python 3.11 with numpy, pandas, scipy, statsmodels, tokenizers and matplotlib. From the repository root, `python paper_v2/scripts/make_all.py` (stored labels) and `make_all.py --labels jqwen` read the two prediction files; `scripts/run_exp004_budget_rejudge.py` and `scripts/run_exp005_budget1024.py` (`--stage gen|judge`; Groq key required) produced the follow-ups, with finish reasons, failures and a per-call spend log in `results/EXP-004-budget-rejudge/` and `results/EXP-005-budget1024/`; `analyze_exp004.py`, `analyze_budgets.py` and `make_figures.py` write the remaining numbers and figures. The tokenizer check downloads the Qwen/Qwen2.5-7B and Qwen/Qwen3.8-27B tokenizers. Sign-flip tests enumerate all 2²⁰ patterns; bootstraps and the language permutation use fixed seeds. Topic-level p values in an earlier draft were Monte Carlo approximations and differ from the exact values here in the third decimal. That draft's language-dependence p value (0.15) and numeral check (60% agreement) could not be reproduced because the script that produced them was not in the repository; they are replaced by the procedures described above.

**New references [23]–[27]**

* [23] J. A. Husain *et al.*, “RomanSetu: Efficiently unlocking multilingual capabilities of large language models via Romanization,” in *Proceedings of the 62nd annual meeting of the association for computational linguistics*, 2024.
* [24] P. Wang *et al.*, “Large language models are not fair evaluators,” in *Proceedings of the 62nd annual meeting of the association for computational linguistics*, 2024.
* [25] Y. Dubois, B. Galambosi, P. Liang, and T. B. Hashimoto, “Length-controlled AlpacaEval: A simple way to debias automatic evaluators,” *arXiv preprint arXiv:2404.04475*, 2024.
* [26] I. Watts, V. Gumma, A. Yadavalli, V. Seshadri, M. Swaminathan, and S. Sitaram, “PARIKSHA: A large-scale investigation of human-LLM evaluator agreement on multilingual and multi-cultural data,” in *Proceedings of the 2024 conference on empirical methods in natural language processing*, 2024, pp. 7900–7932.
* [27] X. Fu and W. Liu, “How reliable is multilingual LLM-as-a-judge?” in *Findings of the association for computational linguistics: EMNLP 2025*, 2025, pp. 11040–11053.
