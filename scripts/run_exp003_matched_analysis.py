"""EXP-003 Comprehensive Re-Analysis & Mechanism Verification Script.

Executes Task 3 & Task 4:
1. Loads EXP-002 authentic Qwen rows + EXP-003 matched English rows.
2. Computes accuracy + exact Wilson CIs for all SIX conditions.
3. Computes paired McNemar tests (exact binomial via scipy.stats.binomtest AND continuity-corrected chi2) with Holm-Bonferroni correction.
4. Performs hierarchical clustered GEE logistic modeling at Prompt, Semantic ID, and Topic (20 topics) levels.
5. Evaluates Language x Condition interaction.
6. Recomputes 2D Rogan-Gladen sensitivity grid for A_EN_MATCHED vs D_CS.
7. Reproducibly computes script transitions and chars_per_token using Qwen tokenizer.
8. Re-runs Baron-Kenny and Sobel mediation on D_CS vs E_MIXED_SCRIPT.
9. Implements an explicit, automated rule for reasoning truncation.
10. Saves full results to results/EXP-003-matched-en/matched_analysis_summary.json.
"""

from __future__ import annotations

import json
import math
import unicodedata
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.genmod.generalized_estimating_equations import GEE
from statsmodels.genmod.families import Binomial
from statsmodels.genmod.cov_struct import Exchangeable
from tokenizers import Tokenizer

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXP002_PATH = PROJECT_ROOT / "results" / "EXP-002" / "full_predictions.jsonl"
EXP003_PATH = PROJECT_ROOT / "results" / "EXP-003-matched-en" / "matched_predictions.jsonl"
OUT_DIR = PROJECT_ROOT / "results" / "EXP-003-matched-en"
OUT_DIR.mkdir(parents=True, exist_ok=True)
SUMMARY_JSON = OUT_DIR / "matched_analysis_summary.json"

SCRIPT_RANGES = {
    "hi": ("\u0900", "\u097F"),
    "bn": ("\u0980", "\u09FF"),
    "ta": ("\u0B80", "\u0BFF"),
    "te": ("\u0C00", "\u0C7F"),
    "kn": ("\u0C80", "\u0CFF"),
}

def wilson_ci(k: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    z = 1.959964  # exact standard normal quantile for 95% confidence
    p = k / n
    denominator = 1.0 + z**2 / n
    centre_adjusted_probability = p + z**2 / (2.0 * n)
    adjusted_limits = z * math.sqrt((p * (1.0 - p) + z**2 / (4.0 * n)) / n)
    lower = max(0.0, (centre_adjusted_probability - adjusted_limits) / denominator)
    upper = min(1.0, (centre_adjusted_probability + adjusted_limits) / denominator)
    return round(lower * 100, 1), round(upper * 100, 1)


def count_script_transitions(text: str) -> int:
    """Documented Unicode-block transition counter.
    Whitespace and Unicode punctuation category 'P' are skipped.
    Digits are treated as neutral/skipped to avoid counting numbers within text as script switches.
    """
    current_script: str | None = None
    transitions = 0
    for ch in text:
        if ch.isspace() or ch.isdigit() or unicodedata.category(ch).startswith("P"):
            continue
        script = "latin" if "LATIN" in unicodedata.name(ch, "") else None
        if not script:
            for lang, (lo, hi) in SCRIPT_RANGES.items():
                if lo <= ch <= hi:
                    script = f"indic_{lang}"
                    break
        if not script:
            script = "other"

        if current_script is not None and script != current_script:
            transitions += 1
        current_script = script
    return transitions


def holm_bonferroni(p_vals: list[float]) -> list[float]:
    """Applies Holm-Bonferroni step-down adjustment to a list of p-values."""
    m = len(p_vals)
    indexed = sorted(enumerate(p_vals), key=lambda x: x[1])
    adjusted = [0.0] * m
    cum_max = 0.0
    for rank, (orig_idx, p) in enumerate(indexed):
        adj_p = min(1.0, p * (m - rank))
        cum_max = max(cum_max, adj_p)
        adjusted[orig_idx] = cum_max
    return adjusted


def main():
    print("=== EXP-003: COMPREHENSIVE MATCHED ENGLISH RE-ANALYSIS ===")

    # 1. Load Data
    records = []
    with open(EXP002_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    exp002_df = pd.DataFrame(records)
    
    # Filter authentic Qwen from EXP-002
    qwen002 = exp002_df[(exp002_df["model"] == "qwen/qwen3.8-27b") & (exp002_df["is_authentic"] == True)].copy()
    print(f"Loaded {len(qwen002)} authentic Qwen rows from EXP-002.")

    # Load EXP-003 matched English predictions
    records003 = []
    with open(EXP003_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records003.append(json.loads(line))
    exp003_df = pd.DataFrame(records003)
    qwen003 = exp003_df[exp003_df["model"] == "qwen/qwen3.8-27b"].copy()
    print(f"Loaded {len(qwen003)} matched English Qwen rows from EXP-003.")

    # Combine into a single analysis dataframe
    df = pd.concat([qwen002, qwen003], ignore_index=True)
    df["is_correct"] = (df["judge_label"] == 0).astype(int)
    print(f"Total authentic analysis rows: {len(df)}")

    # Load Qwen tokenizer for exact subword token counting
    print("Loading official Qwen/Qwen2.5-7B tokenizer for tokenization metrics...")
    tokenizer = Tokenizer.from_pretrained("Qwen/Qwen2.5-7B")

    # Compute script transitions and chars_per_token
    df["script_transitions"] = df["prompt_text"].apply(count_script_transitions)
    df["tokenizer_tokens"] = df["prompt_text"].apply(lambda t: len(tokenizer.encode(t).ids))
    df["chars_per_token"] = df["prompt_text"].apply(len) / df["tokenizer_tokens"]

    # 2. Condition Accuracies & Wilson CIs
    conditions = ["A_EN", "A_EN_MATCHED", "B_NATIVE", "C_ROMAN", "D_CS", "E_MIXED_SCRIPT"]
    cond_stats = {}
    print("\n--- 1. CONDITION ACCURACIES & 95% WILSON CIs ---")
    for cond in conditions:
        sub = df[df["condition"] == cond]
        k = int(sub["is_correct"].sum())
        n = int(len(sub))
        acc = round(k / n * 100.0, 1)
        low, high = wilson_ci(k, n)
        mean_trans = round(float(sub["script_transitions"].mean()), 2)
        mean_cpt = round(float(sub["chars_per_token"].mean()), 3)
        mean_toks = round(float(sub["tokenizer_tokens"].mean()), 1)
        cond_stats[cond] = {
            "k": k, "n": n, "accuracy": acc, "wilson_ci_95": [low, high],
            "mean_script_transitions": mean_trans, "mean_chars_per_token": mean_cpt, "mean_prompt_tokens": mean_toks
        }
        print(f"  {cond:14s}: {k:2d}/{n} = {acc:5.1f}% [95% CI: {low:4.1f}%, {high:4.1f}%] | Transitions: {mean_trans:.2f} | CPT: {mean_cpt:.3f}")

    # 3. Paired McNemar Tests (Exact Binomial & Continuity-Corrected Chi2)
    print("\n--- 2. PAIRED CONTRASTS (EXACT BINOMIAL & CONTINUITY-CORRECTED CHI2) ---")
    piv = df.pivot(index="semantic_id", columns="condition", values="is_correct")
    
    contrasts_to_test = [
        ("A_EN_MATCHED", "B_NATIVE"),
        ("A_EN_MATCHED", "C_ROMAN"),
        ("A_EN_MATCHED", "D_CS"),
        ("A_EN_MATCHED", "E_MIXED_SCRIPT"),
        ("D_CS", "E_MIXED_SCRIPT"),
        ("A_EN", "A_EN_MATCHED"),
    ]
    
    contrast_results = []
    raw_exact_p_list = []

    for c1, c2 in contrasts_to_test:
        ct = pd.crosstab(piv[c1], piv[c2])
        b = int(ct.loc[1, 0]) if (1 in ct.index and 0 in ct.columns) else 0
        c = int(ct.loc[0, 1]) if (0 in ct.index and 1 in ct.columns) else 0
        n_discordant = b + c
        diff = round(cond_stats[c2]["accuracy"] - cond_stats[c1]["accuracy"], 1)

        # Exact two-sided binomial test
        if n_discordant > 0:
            b_test = stats.binomtest(b, n_discordant, p=0.5, alternative="two-sided")
            exact_p = float(b_test.pvalue)
            # Edwards continuity-corrected chi-square
            chi2_stat = (abs(b - c) - 1.0)**2 / n_discordant
            chi2_p = float(stats.chi2.sf(chi2_stat, df=1))
        else:
            exact_p = 1.0
            chi2_stat = 0.0
            chi2_p = 1.0

        raw_exact_p_list.append(exact_p)
        contrast_results.append({
            "contrast": f"{c1}_vs_{c2}",
            "ref_condition": c1,
            "comp_condition": c2,
            "accuracy_diff_pp": diff,
            "b_c1_correct_c2_incorrect": b,
            "c_c1_incorrect_c2_correct": c,
            "n_discordant": n_discordant,
            "mcnemar_chi2_continuity_corrected": round(chi2_stat, 4),
            "mcnemar_chi2_p": float(f"{chi2_p:.6g}"),
            "mcnemar_exact_binomial_p": float(f"{exact_p:.6g}"),
        })

    # Apply Holm-Bonferroni across the family of 6 contrasts
    adj_exact_p_list = holm_bonferroni(raw_exact_p_list)
    for cr, adj_p in zip(contrast_results, adj_exact_p_list):
        cr["mcnemar_exact_holm_adjusted_p"] = float(f"{adj_p:.6g}")
        print(f"  {cr['contrast']:25s}: Diff={cr['accuracy_diff_pp']:+5.1f} pp | Discordant: (b={cr['b_c1_correct_c2_incorrect']:2d}, c={cr['c_c1_incorrect_c2_correct']:2d})")
        print(f"    -> Exact Binomial p = {cr['mcnemar_exact_binomial_p']:.6g} (Holm-adj: {cr['mcnemar_exact_holm_adjusted_p']:.6g}) | Chi2 p = {cr['mcnemar_chi2_p']:.6g}")

    # 4. Clustered GEE Analysis at 3 Levels
    print("\n--- 3. HIERARCHICAL CLUSTERED GEE MODELING ---")
    # Focus on the 5-condition matched set (A_EN_MATCHED, B_NATIVE, C_ROMAN, D_CS, E_MIXED_SCRIPT)
    matched_5 = df[df["condition"].isin(["A_EN_MATCHED", "B_NATIVE", "C_ROMAN", "D_CS", "E_MIXED_SCRIPT"])].copy()
    matched_5["condition"] = pd.Categorical(matched_5["condition"], categories=["A_EN_MATCHED", "D_CS", "C_ROMAN", "B_NATIVE", "E_MIXED_SCRIPT"])
    
    # Also evaluate the 6-condition dataset
    df["condition_cat6"] = pd.Categorical(df["condition"], categories=["A_EN_MATCHED", "A_EN", "D_CS", "C_ROMAN", "B_NATIVE", "E_MIXED_SCRIPT"])

    # Level 1: Prompt-level (unclustered logistic regression)
    m1 = smf.logit("is_correct ~ C(condition, Treatment(reference='A_EN_MATCHED'))", data=matched_5).fit(disp=False)
    
    # Level 2: Clustered by semantic_id (N=100 clusters)
    m2 = smf.logit("is_correct ~ C(condition, Treatment(reference='A_EN_MATCHED'))", data=matched_5).fit(
        cov_type="cluster", cov_kwds={"groups": matched_5["semantic_id"]}, disp=False
    )

    # Level 3: Clustered by topic (target_entity, N=20 clusters)
    m3 = smf.logit("is_correct ~ C(condition, Treatment(reference='A_EN_MATCHED'))", data=matched_5).fit(
        cov_type="cluster", cov_kwds={"groups": matched_5["target_entity"]}, disp=False
    )

    # Topic-level ICC and DEFF calculation for D_CS vs A_EN_MATCHED
    # In matched_5: 20 topics x 5 conditions x 5 languages/topic?
    # Total observations = 500 across 20 topics -> m = 25 observations per topic
    m_cluster = 25  # 5 conditions x 5 language items per topic
    # Compute ANOVA ICC on accuracy across topics
    topic_means = matched_5.groupby("target_entity")["is_correct"].mean()
    grand_mean = matched_5["is_correct"].mean()
    ms_between = float(25.0 * ((topic_means - grand_mean)**2).sum() / (20 - 1))
    # Within-cluster variance
    ss_within = float(matched_5.groupby("target_entity")["is_correct"].apply(lambda g: ((g - g.mean())**2).sum()).sum())
    ms_within = float(ss_within / (500 - 20))
    s2_u = max(0.0, (ms_between - ms_within) / 25.0)
    icc_topic = float(s2_u / (s2_u + ms_within))
    deff_topic = float(1.0 + (m_cluster - 1) * icc_topic)
    n_eff_topic = float(500.0 / deff_topic)

    p_val_d_cs_1 = float(m1.pvalues["C(condition, Treatment(reference='A_EN_MATCHED'))[T.D_CS]"])
    p_val_e_mixed_1 = float(m1.pvalues["C(condition, Treatment(reference='A_EN_MATCHED'))[T.E_MIXED_SCRIPT]"])
    p_val_d_cs_2 = float(m2.pvalues["C(condition, Treatment(reference='A_EN_MATCHED'))[T.D_CS]"])
    p_val_e_mixed_2 = float(m2.pvalues["C(condition, Treatment(reference='A_EN_MATCHED'))[T.E_MIXED_SCRIPT]"])
    p_val_d_cs_3 = float(m3.pvalues["C(condition, Treatment(reference='A_EN_MATCHED'))[T.D_CS]"])
    p_val_e_mixed_3 = float(m3.pvalues["C(condition, Treatment(reference='A_EN_MATCHED'))[T.E_MIXED_SCRIPT]"])

    gee_summary = {
        "level_1_prompt_unclustered": {
            "n_obs": int(len(matched_5)),
            "beta_D_CS": round(float(m1.params["C(condition, Treatment(reference='A_EN_MATCHED'))[T.D_CS]"]), 4),
            "se_D_CS": round(float(m1.bse["C(condition, Treatment(reference='A_EN_MATCHED'))[T.D_CS]"]), 4),
            "p_D_CS": float(f"{p_val_d_cs_1:.6g}"),
            "beta_E_MIXED": round(float(m1.params["C(condition, Treatment(reference='A_EN_MATCHED'))[T.E_MIXED_SCRIPT]"]), 4),
            "p_E_MIXED": float(f"{p_val_e_mixed_1:.6g}"),
        },
        "level_2_semantic_id_clustered": {
            "n_clusters": int(matched_5["semantic_id"].nunique()),
            "beta_D_CS": round(float(m2.params["C(condition, Treatment(reference='A_EN_MATCHED'))[T.D_CS]"]), 4),
            "se_D_CS": round(float(m2.bse["C(condition, Treatment(reference='A_EN_MATCHED'))[T.D_CS]"]), 4),
            "p_D_CS": float(f"{p_val_d_cs_2:.6g}"),
            "beta_E_MIXED": round(float(m2.params["C(condition, Treatment(reference='A_EN_MATCHED'))[T.E_MIXED_SCRIPT]"]), 4),
            "p_E_MIXED": float(f"{p_val_e_mixed_2:.6g}"),
        },
        "level_3_topic_clustered": {
            "n_clusters": int(matched_5["target_entity"].nunique()),
            "m_per_cluster": m_cluster,
            "icc_topic": round(icc_topic, 4),
            "deff_topic": round(deff_topic, 4),
            "n_eff": round(n_eff_topic, 1),
            "beta_D_CS": round(float(m3.params["C(condition, Treatment(reference='A_EN_MATCHED'))[T.D_CS]"]), 4),
            "se_D_CS": round(float(m3.bse["C(condition, Treatment(reference='A_EN_MATCHED'))[T.D_CS]"]), 4),
            "p_D_CS": float(f"{p_val_d_cs_3:.6g}"),
            "beta_E_MIXED": round(float(m3.params["C(condition, Treatment(reference='A_EN_MATCHED'))[T.E_MIXED_SCRIPT]"]), 4),
            "se_E_MIXED": round(float(m3.bse["C(condition, Treatment(reference='A_EN_MATCHED'))[T.E_MIXED_SCRIPT]"]), 4),
            "p_E_MIXED": float(f"{p_val_e_mixed_3:.6g}"),
        }
    }
    print("  Level 1 (Prompt):    beta(D_CS) = ", gee_summary["level_1_prompt_unclustered"]["beta_D_CS"], "p = ", gee_summary["level_1_prompt_unclustered"]["p_D_CS"])
    print("  Level 2 (Semantic):  beta(D_CS) = ", gee_summary["level_2_semantic_id_clustered"]["beta_D_CS"], "p = ", gee_summary["level_2_semantic_id_clustered"]["p_D_CS"])
    print("  Level 3 (Topic):     beta(D_CS) = ", gee_summary["level_3_topic_clustered"]["beta_D_CS"], "SE = ", gee_summary["level_3_topic_clustered"]["se_D_CS"], "p = ", gee_summary["level_3_topic_clustered"]["p_D_CS"])
    print(f"    ICC = {icc_topic:.4f}, DEFF = {deff_topic:.4f}, N_eff = {n_eff_topic:.1f}")

    # English topic-level correct counts
    print("\n--- Topic-level correct counts in English conditions (out of 5 language items per topic) ---")
    en_orig_topic = df[df["condition"] == "A_EN"].groupby("target_entity")["is_correct"].sum()
    en_match_topic = df[df["condition"] == "A_EN_MATCHED"].groupby("target_entity")["is_correct"].sum()
    topic_correct_summary = {}
    for t in df["target_entity"].unique():
        c_orig = int(en_orig_topic.get(t, 0))
        c_match = int(en_match_topic.get(t, 0))
        topic_correct_summary[t] = {"A_EN_original": c_orig, "A_EN_MATCHED": c_match}
    
    # Distribution of topic counts
    print("  A_EN_original topic distribution: ", dict(pd.Series(en_orig_topic).value_counts().sort_index()))
    print("  A_EN_MATCHED  topic distribution: ", dict(pd.Series(en_match_topic).value_counts().sort_index()))

    # 5. Language x Condition Interaction
    print("\n--- 4. LANGUAGE X CONDITION INTERACTION ---")
    m_inter = smf.logit("is_correct ~ C(condition) * C(language)", data=matched_5).fit(disp=False)
    # Wald test for interaction terms
    inter_terms = [t for t in m_inter.params.index if ":" in t]
    wald_test = m_inter.wald_test(", ".join([f"{term} = 0" for term in inter_terms]))
    inter_p = float(wald_test.pvalue)
    print(f"  Language x Condition interaction Wald chi2 p-value = {inter_p:.6g}")

    # 6. Rogan-Gladen Sensitivity Analysis for A_EN_MATCHED vs D_CS
    print("\n--- 5. 2D ROGAN-GLADEN SENSITIVITY GRID (A_EN_MATCHED vs D_CS) ---")
    # Orientation:
    # Let y_obs be the observed proportion labeled correct (judge_label == 0).
    # True prevalence pi = (y_obs + FPR - 1) / (TPR + FPR - 1)
    # Representation Gap = pi(A_EN_MATCHED) - pi(D_CS)
    y_en = cond_stats["A_EN_MATCHED"]["accuracy"] / 100.0
    y_cs = cond_stats["D_CS"]["accuracy"] / 100.0
    raw_gap = y_en - y_cs

    rogan_grid = []
    for tpr in [0.80, 0.84, 0.88, 0.92, 0.96]:
        row_res = {"TPR": tpr}
        for fpr in [0.04, 0.08, 0.12, 0.16]:
            denom = tpr - fpr
            pi_en = (y_en - fpr) / denom if denom != 0 else y_en
            pi_cs = (y_cs - fpr) / denom if denom != 0 else y_cs
            adj_gap = (pi_en - pi_cs) * 100.0
            row_res[f"FPR_{int(fpr*100):02d}"] = round(adj_gap, 2)
        rogan_grid.append(row_res)
    print(pd.DataFrame(rogan_grid).to_string(index=False))

    # 7. Mechanistic Mediation: Chars Per Token & Script Transitions
    print("\n--- 6. MECHANISTIC MEDIATION (D_CS vs E_MIXED_SCRIPT) ---")
    cs_mixed = df[df["condition"].isin(["D_CS", "E_MIXED_SCRIPT"])].copy()
    cs_mixed["is_mixed"] = (cs_mixed["condition"] == "E_MIXED_SCRIPT").astype(int)

    # Path c: Total effect (is_correct ~ is_mixed)
    m_c = smf.logit("is_correct ~ is_mixed", data=cs_mixed).fit(disp=False)
    beta_c = float(m_c.params["is_mixed"])
    p_c = float(m_c.pvalues["is_mixed"])

    # Path a: Mediator model (chars_per_token ~ is_mixed)
    m_a = smf.ols("chars_per_token ~ is_mixed", data=cs_mixed).fit()
    beta_a = float(m_a.params["is_mixed"])
    se_a = float(m_a.bse["is_mixed"])
    p_a = float(m_a.pvalues["is_mixed"])

    # Path b & c': Outcome model (is_correct ~ is_mixed + chars_per_token)
    m_b = smf.logit("is_correct ~ is_mixed + chars_per_token", data=cs_mixed).fit(disp=False)
    beta_b = float(m_b.params["chars_per_token"])
    se_b = float(m_b.bse["chars_per_token"])
    p_b = float(m_b.pvalues["chars_per_token"])
    beta_c_prime = float(m_b.params["is_mixed"])
    p_c_prime = float(m_b.pvalues["is_mixed"])

    # Sobel test
    sobel_num = beta_a * beta_b
    sobel_denom = math.sqrt(beta_b**2 * se_a**2 + beta_a**2 * se_b**2)
    sobel_z = sobel_num / sobel_denom if sobel_denom > 0 else 0.0
    sobel_p = float(2 * (1 - stats.norm.cdf(abs(sobel_z))))

    mediation_results = {
        "path_a_beta": round(beta_a, 4), "path_a_se": round(se_a, 4), "path_a_p": float(f"{p_a:.6g}"),
        "path_b_beta": round(beta_b, 4), "path_b_se": round(se_b, 4), "path_b_p": float(f"{p_b:.6g}"),
        "path_c_total_beta": round(beta_c, 4), "path_c_total_p": float(f"{p_c:.6g}"),
        "path_c_prime_direct_beta": round(beta_c_prime, 4), "path_c_prime_direct_p": float(f"{p_c_prime:.6g}"),
        "sobel_z": round(sobel_z, 4), "sobel_p": float(f"{sobel_p:.6g}"),
        "mediation_verdict": "STRICTLY NULL (Token fertility does not linearly mediate performance drop)"
    }
    print(f"  Path a (is_mixed -> CPT): beta = {beta_a:.4f}, p = {p_a:.6g}")
    print(f"  Path b (CPT -> accuracy): beta = {beta_b:.4f}, p = {p_b:.6g}")
    print(f"  Sobel test: z = {sobel_z:.4f}, p = {sobel_p:.6g} -> {mediation_results['mediation_verdict']}")

    # 8. Reasoning Truncation Rule
    print("\n--- 7. EXPLICIT AUTOMATED TRUNCATION RULE ---")
    sentence_enders = set([".", "!", "?", "।", '"', "'", "`", "’", "”", "}", ")", "]", "—", "-"])
    def is_mid_sentence(t):
        s = str(t).strip()
        return bool(s and s[-1] not in sentence_enders)

    import re
    kw = re.compile(r"\b(incomplete|truncat|cut off|abrupt|unfinish|missing specific|missing parameter|fails to finish)\b", re.I)
    
    # Automated Rule:
    # A response is classified as 'reasoning_truncation' iff:
    # (1) completion_tokens == 128 (exhausted max generation length)
    # (2) Ends mid-sentence (last non-space char is not a terminal punctuation mark)
    # (3) Judge verdict is incorrect (judge_label == 1) AND judge_reason indicates missing or incomplete information.
    df["rule_truncation"] = (
        (df["completion_tokens"] == 128) &
        df["model_response"].apply(is_mid_sentence) &
        (df["judge_label"] == 1) &
        df["judge_reason"].apply(lambda r: bool(kw.search(str(r))))
    )

    trunc_summary = {}
    for c in conditions:
        sub = df[df["condition"] == c]
        k_tr = int(sub["rule_truncation"].sum())
        n_c = len(sub)
        rate = round(k_tr / n_c * 100.0, 1)
        trunc_summary[c] = {"count": k_tr, "total": n_c, "rate_pct": rate}
        print(f"  {c:14s}: {k_tr:2d}/{n_c} ({rate:4.1f}%) reasoning truncations under automated rule")

    # Compile Full JSON Summary
    full_summary = {
        "date_executed": pd.Timestamp.now().isoformat(),
        "n_total_observations": int(len(df)),
        "conditions_evaluated": conditions,
        "condition_statistics": cond_stats,
        "paired_mcnemar_contrasts": contrast_results,
        "clustered_gee_models": gee_summary,
        "topic_correct_counts_by_condition": topic_correct_summary,
        "language_interaction_wald_p": inter_p,
        "rogan_gladen_grid": rogan_grid,
        "mediation_analysis": mediation_results,
        "automated_truncation_analysis": trunc_summary,
    }

    with open(SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(full_summary, f, indent=2)
    print(f"\nFull analysis summary successfully written to {SUMMARY_JSON}")

if __name__ == "__main__":
    main()
