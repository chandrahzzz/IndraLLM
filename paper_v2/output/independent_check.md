# Independent check of reported numbers

Re-derived from raw files with statsmodels (exact McNemar, Wilson), scikit-learn (Cohen's kappa), a Monte Carlo sign-flip test (200,000 draws, tolerance 0.005 against the exact enumeration) and a bootstrap with a different seed (tolerance 2.5 points on the CI bound).

| Check | Independent value | Reported value | Tolerance | Result |
|---|---|---|---|---|
| J-QWEN 128 accuracy EN-ORIG | 70 | 70 | 0 | PASS |
| J-QWEN 128 Wilson low EN-ORIG | 60.4151 | 60.4151 | 0.05 | PASS |
| J-QWEN 128 accuracy EN-MATCH | 60 | 60 | 0 | PASS |
| J-QWEN 128 Wilson low EN-MATCH | 50.2003 | 50.2003 | 0.05 | PASS |
| J-QWEN 128 accuracy CS-LAT | 49 | 49 | 0 | PASS |
| J-QWEN 128 Wilson low CS-LAT | 39.422 | 39.422 | 0.05 | PASS |
| J-QWEN 128 accuracy ROMAN | 37 | 37 | 0 | PASS |
| J-QWEN 128 Wilson low ROMAN | 28.1824 | 28.1824 | 0.05 | PASS |
| J-QWEN 128 accuracy NATIVE | 32 | 32 | 0 | PASS |
| J-QWEN 128 Wilson low NATIVE | 23.6691 | 23.6691 | 0.05 | PASS |
| J-QWEN 128 accuracy MIXED | 26 | 26 | 0 | PASS |
| J-QWEN 128 Wilson low MIXED | 18.4047 | 18.4047 | 0.05 | PASS |
| exact McNemar CS-LAT vs EN-MATCH | 0.126289 | 0.126289 | 1e-09 | PASS |
| topic sign-flip (MC) CS-LAT vs EN-MATCH | 0.422155 | 0.422485 | 0.005 | PASS |
| exact McNemar ROMAN vs EN-MATCH | 0.00108854 | 0.00108854 | 1e-09 | PASS |
| topic sign-flip (MC) ROMAN vs EN-MATCH | 0.08536 | 0.0867615 | 0.005 | PASS |
| exact McNemar NATIVE vs EN-MATCH | 2.54486e-05 | 2.54486e-05 | 1e-09 | PASS |
| topic sign-flip (MC) NATIVE vs EN-MATCH | 0.03008 | 0.0308228 | 0.005 | PASS |
| exact McNemar MIXED vs EN-MATCH | 5.37832e-06 | 5.37832e-06 | 1e-09 | PASS |
| topic sign-flip (MC) MIXED vs EN-MATCH | 0.02914 | 0.0303345 | 0.005 | PASS |
| exact McNemar MIXED vs CS-LAT | 0.000191076 | 0.000191076 | 1e-09 | PASS |
| topic sign-flip (MC) MIXED vs CS-LAT | 0.003725 | 0.00366211 | 0.005 | PASS |
| exact McNemar EN-MATCH vs EN-ORIG | 0.0987371 | 0.0987371 | 1e-09 | PASS |
| topic sign-flip (MC) EN-MATCH vs EN-ORIG | 0.68637 | 0.6875 | 0.005 | PASS |
| exact McNemar MIXED vs ROMAN | 0.052239 | 0.052239 | 1e-09 | PASS |
| topic sign-flip (MC) MIXED vs ROMAN | 0.06837 | 0.0693359 | 0.005 | PASS |
| exact McNemar MIXED vs NATIVE | 0.286279 | 0.286279 | 1e-09 | PASS |
| topic sign-flip (MC) MIXED vs NATIVE | 0.456095 | 0.457031 | 0.005 | PASS |
| exact McNemar ROMAN vs CS-LAT | 0.0729514 | 0.0729514 | 1e-09 | PASS |
| topic sign-flip (MC) ROMAN vs CS-LAT | 0.057765 | 0.0567322 | 0.005 | PASS |
| exact McNemar NATIVE vs CS-LAT | 0.00763208 | 0.00763208 | 1e-09 | PASS |
| topic sign-flip (MC) NATIVE vs CS-LAT | 0.03355 | 0.0334473 | 0.005 | PASS |
| exact McNemar NATIVE vs ROMAN | 0.442068 | 0.442068 | 1e-09 | PASS |
| topic sign-flip (MC) NATIVE vs ROMAN | 0.36912 | 0.369141 | 0.005 | PASS |
| J-QWEN 128 accuracy EN-MATCH | 60 | 60 | 1e-09 | PASS |
| J-QWEN 128 accuracy CS-LAT | 49 | 49 | 1e-09 | PASS |
| J-QWEN 128 accuracy MIXED | 26 | 26 | 1e-09 | PASS |
| J-QWEN 128 McNemar CS-LAT vs EN-MATCH | 0.126289 | 0.126289 | 1e-09 | PASS |
| J-QWEN 128 topic p (MC) CS-LAT vs EN-MATCH | 0.422155 | 0.422485 | 0.005 | PASS |
| J-QWEN 128 topic CI low (seed 999) CS-LAT vs EN-MATCH | -34 | -34 | 2.5 | PASS |
| J-QWEN 128 McNemar MIXED vs CS-LAT | 0.000191076 | 0.000191076 | 1e-09 | PASS |
| J-QWEN 128 topic p (MC) MIXED vs CS-LAT | 0.003725 | 0.00366211 | 0.005 | PASS |
| J-QWEN 128 topic CI low (seed 999) MIXED vs CS-LAT | -35 | -35 | 2.5 | PASS |
| J-QWEN 128 McNemar MIXED vs EN-MATCH | 5.37832e-06 | 5.37832e-06 | 1e-09 | PASS |
| J-QWEN 128 topic p (MC) MIXED vs EN-MATCH | 0.02914 | 0.0303345 | 0.005 | PASS |
| J-QWEN 128 topic CI low (seed 999) MIXED vs EN-MATCH | -60 | -59 | 2.5 | PASS |
| J-QWEN 512 accuracy EN-MATCH | 80 | 80 | 1e-09 | PASS |
| J-QWEN 512 accuracy CS-LAT | 59 | 59 | 1e-09 | PASS |
| J-QWEN 512 accuracy MIXED | 63 | 63 | 1e-09 | PASS |
| J-QWEN 512 McNemar CS-LAT vs EN-MATCH | 0.00050826 | 0.00050826 | 1e-09 | PASS |
| J-QWEN 512 topic p (MC) CS-LAT vs EN-MATCH | 0.08053 | 0.081543 | 0.005 | PASS |
| J-QWEN 512 topic CI low (seed 999) CS-LAT vs EN-MATCH | -41 | -41 | 2.5 | PASS |
| J-QWEN 512 McNemar MIXED vs CS-LAT | 0.571588 | 0.571588 | 1e-09 | PASS |
| J-QWEN 512 topic p (MC) MIXED vs CS-LAT | 0.64882 | 0.647949 | 0.005 | PASS |
| J-QWEN 512 topic CI low (seed 999) MIXED vs CS-LAT | -8 | -8 | 2.5 | PASS |
| J-QWEN 512 McNemar MIXED vs EN-MATCH | 0.00332689 | 0.00332689 | 1e-09 | PASS |
| J-QWEN 512 topic p (MC) MIXED vs EN-MATCH | 0.127745 | 0.128906 | 0.005 | PASS |
| J-QWEN 512 topic CI low (seed 999) MIXED vs EN-MATCH | -36 | -35.025 | 2.5 | PASS |
| J-QWEN 1024 accuracy EN-MATCH | 85 | 85 | 1e-09 | PASS |
| J-QWEN 1024 accuracy CS-LAT | 61 | 61 | 1e-09 | PASS |
| J-QWEN 1024 accuracy MIXED | 58 | 58 | 1e-09 | PASS |
| J-QWEN 1024 McNemar CS-LAT vs EN-MATCH | 8.43033e-06 | 8.43033e-06 | 1e-09 | PASS |
| J-QWEN 1024 topic p (MC) CS-LAT vs EN-MATCH | 0.0178 | 0.0180664 | 0.005 | PASS |
| J-QWEN 1024 topic CI low (seed 999) CS-LAT vs EN-MATCH | -42 | -42 | 2.5 | PASS |
| J-QWEN 1024 McNemar MIXED vs CS-LAT | 0.701108 | 0.701108 | 1e-09 | PASS |
| J-QWEN 1024 topic p (MC) MIXED vs CS-LAT | 0.72072 | 0.720703 | 0.005 | PASS |
| J-QWEN 1024 topic CI low (seed 999) MIXED vs CS-LAT | -14 | -14 | 2.5 | PASS |
| J-QWEN 1024 McNemar MIXED vs EN-MATCH | 4.62867e-07 | 4.62867e-07 | 1e-09 | PASS |
| J-QWEN 1024 topic p (MC) MIXED vs EN-MATCH | 0.003325 | 0.00341797 | 0.005 | PASS |
| J-QWEN 1024 topic CI low (seed 999) MIXED vs EN-MATCH | -42 | -42 | 2.5 | PASS |
| J-OSS 128 accuracy EN-MATCH | 37 | 37 | 1e-09 | PASS |
| J-OSS 128 accuracy CS-LAT | 25 | 25 | 1e-09 | PASS |
| J-OSS 128 accuracy MIXED | 17 | 17 | 1e-09 | PASS |
| J-OSS 128 McNemar CS-LAT vs EN-MATCH | 0.0501025 | 0.0501025 | 1e-09 | PASS |
| J-OSS 128 topic p (MC) CS-LAT vs EN-MATCH | 0.223845 | 0.223633 | 0.005 | PASS |
| J-OSS 128 topic CI low (seed 999) CS-LAT vs EN-MATCH | -29 | -29 | 2.5 | PASS |
| J-OSS 128 McNemar MIXED vs CS-LAT | 0.184933 | 0.184933 | 1e-09 | PASS |
| J-OSS 128 topic p (MC) MIXED vs CS-LAT | 0.24048 | 0.240234 | 0.005 | PASS |
| J-OSS 128 topic CI low (seed 999) MIXED vs CS-LAT | -19 | -19 | 2.5 | PASS |
| J-OSS 128 McNemar MIXED vs EN-MATCH | 0.00165805 | 0.00165805 | 1e-09 | PASS |
| J-OSS 128 topic p (MC) MIXED vs EN-MATCH | 0.067875 | 0.0668945 | 0.005 | PASS |
| J-OSS 128 topic CI low (seed 999) MIXED vs EN-MATCH | -39 | -39 | 2.5 | PASS |
| J-OSS 512 accuracy EN-MATCH | 58 | 58 | 1e-09 | PASS |
| J-OSS 512 accuracy CS-LAT | 54 | 54 | 1e-09 | PASS |
| J-OSS 512 accuracy MIXED | 48 | 48 | 1e-09 | PASS |
| J-OSS 512 McNemar CS-LAT vs EN-MATCH | 0.571588 | 0.571588 | 1e-09 | PASS |
| J-OSS 512 topic p (MC) CS-LAT vs EN-MATCH | 0.760045 | 0.760742 | 0.005 | PASS |
| J-OSS 512 topic CI low (seed 999) CS-LAT vs EN-MATCH | -22 | -22 | 2.5 | PASS |
| J-OSS 512 McNemar MIXED vs CS-LAT | 0.344928 | 0.344928 | 1e-09 | PASS |
| J-OSS 512 topic p (MC) MIXED vs CS-LAT | 0.44375 | 0.441895 | 0.005 | PASS |
| J-OSS 512 topic CI low (seed 999) MIXED vs CS-LAT | -18 | -18 | 2.5 | PASS |
| J-OSS 512 McNemar MIXED vs EN-MATCH | 0.0871586 | 0.0871586 | 1e-09 | PASS |
| J-OSS 512 topic p (MC) MIXED vs EN-MATCH | 0.308815 | 0.308594 | 0.005 | PASS |
| J-OSS 512 topic CI low (seed 999) MIXED vs EN-MATCH | -26 | -26 | 2.5 | PASS |
| J-OSS 1024 accuracy EN-MATCH | 63 | 63 | 1e-09 | PASS |
| J-OSS 1024 accuracy CS-LAT | 56 | 56 | 1e-09 | PASS |
| J-OSS 1024 accuracy MIXED | 51 | 51 | 1e-09 | PASS |
| J-OSS 1024 McNemar CS-LAT vs EN-MATCH | 0.21004 | 0.21004 | 1e-09 | PASS |
| J-OSS 1024 topic p (MC) CS-LAT vs EN-MATCH | 0.51768 | 0.519531 | 0.005 | PASS |
| J-OSS 1024 topic CI low (seed 999) CS-LAT vs EN-MATCH | -24 | -24 | 2.5 | PASS |
| J-OSS 1024 McNemar MIXED vs CS-LAT | 0.404873 | 0.404873 | 1e-09 | PASS |
| J-OSS 1024 topic p (MC) MIXED vs CS-LAT | 0.52308 | 0.52124 | 0.005 | PASS |
| J-OSS 1024 topic CI low (seed 999) MIXED vs CS-LAT | -17 | -17 | 2.5 | PASS |
| J-OSS 1024 McNemar MIXED vs EN-MATCH | 0.0427739 | 0.0427739 | 1e-09 | PASS |
| J-OSS 1024 topic p (MC) MIXED vs EN-MATCH | 0.21959 | 0.220215 | 0.005 | PASS |
| J-OSS 1024 topic CI low (seed 999) MIXED vs EN-MATCH | -28 | -28 | 2.5 | PASS |
| kappa 128 EN-MATCH (sklearn) | 0.486692 | 0.486692 | 1e-09 | PASS |
| kappa 128 CS-LAT (sklearn) | 0.434343 | 0.434343 | 1e-09 | PASS |
| kappa 128 MIXED (sklearn) | 0.385246 | 0.385246 | 1e-09 | PASS |
| agreement 128 all | 0.746667 | 0.746667 | 1e-09 | PASS |
| kappa 512 EN-MATCH (sklearn) | 0.513274 | 0.513274 | 1e-09 | PASS |
| kappa 512 CS-LAT (sklearn) | 0.655032 | 0.655032 | 1e-09 | PASS |
| kappa 512 MIXED (sklearn) | 0.584323 | 0.584323 | 1e-09 | PASS |
| agreement 512 all | 0.8 | 0.8 | 1e-09 | PASS |
| kappa 1024 EN-MATCH (sklearn) | 0.462103 | 0.462103 | 1e-09 | PASS |
| kappa 1024 CS-LAT (sklearn) | 0.650781 | 0.650781 | 1e-09 | PASS |
| kappa 1024 MIXED (sklearn) | 0.658909 | 0.658909 | 1e-09 | PASS |
| agreement 1024 all | 0.813333 | 0.813333 | 1e-09 | PASS |

**118 checks, 118 passed, 0 failed.**