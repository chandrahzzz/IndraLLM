"""Recompute every number in the IndraLLM manuscript from the raw prediction files.

Inputs (read-only):
  results/EXP-002/full_predictions.jsonl              EN-ORIG + four Indic conditions
  results/EXP-003-matched-en/matched_predictions.jsonl EN-MATCH

Writes paper_v2/output/numbers_original.json. The tokenizer section downloads the
Qwen/Qwen2.5-7B tokenizer (used by the original analysis) and the Qwen/Qwen3.8-27B
tokenizer (which reproduces the API's prompt-token counts; see tokenizer_check).

Usage (repo root):  python paper_v2/scripts/make_all.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.genmod.cov_struct import Independence
from statsmodels.genmod.families import Binomial
from statsmodels.genmod.generalized_estimating_equations import GEE

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stats_lib import (  # noqa: E402
    ALLAM, COND_LABEL, INCOMPLETE_KW, MATCHED5, ORDER, PRIMARY, QWEN, SECONDARY,
    brahmic_share, ends_mid_sentence, holm, mcnemar_exact, numerals_present,
    gold_numerals, script_transitions, signflip_exact, topic_bootstrap, wilson,
)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "paper_v2" / "output"
OUT.mkdir(parents=True, exist_ok=True)


def load(labels: str = "stored") -> pd.DataFrame:
    """labels='stored': verdicts saved with the predictions (EXP-002 judge T=0.3 with the
    generation system prompt; EXP-003 judge T=0).  labels='jqwen': the harmonised EXP-004
    re-judgement (same judge model, T=0, one system prompt) for every Qwen row.  ALLaM rows
    keep their stored verdicts in both cases."""
    rows = [json.loads(l) for l in open(ROOT / "results/EXP-002/full_predictions.jsonl", encoding="utf-8")]
    rows += [json.loads(l) for l in open(ROOT / "results/EXP-003-matched-en/matched_predictions.jsonl", encoding="utf-8")]
    df = pd.DataFrame(rows)
    df = df[(df.partition == "TEST-OOD")].copy()
    assert df.judge_label.isin([0, 1]).all(), "unparsed judge labels present"
    if labels == "jqwen":
        j = pd.DataFrame([json.loads(l) for l in open(ROOT / "results/EXP-004-budget-rejudge/judgements.jsonl", encoding="utf-8")])
        j = j[(j.source == "orig128") & (j.judge == "J-QWEN")].set_index("prompt_id")
        assert j.judge_label.isin([0, 1]).all() and len(j) == 600
        isq = df.model == QWEN
        df.loc[isq, "judge_label"] = df.loc[isq, "prompt_id"].map(j.judge_label).astype(int)
        df.loc[isq, "judge_reason"] = df.loc[isq, "prompt_id"].map(
            j.raw.str.split("REASON:", n=1).str[-1].str.strip())
    df["correct"] = (df.judge_label == 0).astype(int)
    return df


def contrasts(q: pd.DataFrame, col: str = "correct", seed: int = 0) -> list[dict]:
    piv = q.pivot(index="semantic_id", columns="condition", values=col)
    topic_of = q.drop_duplicates("semantic_id").set_index("semantic_id").target_entity
    out = []
    for ref, cmp_ in PRIMARY + SECONDARY:
        if ref not in piv or cmp_ not in piv:
            continue
        r = mcnemar_exact(piv[ref].values, piv[cmp_].values)
        diff = piv[cmp_] - piv[ref]
        per_topic = diff.groupby(topic_of).mean() * 100
        lo, hi = topic_bootstrap(per_topic.values, seed=seed)
        out.append({
            "ref": COND_LABEL[ref], "cmp": COND_LABEL[cmp_],
            "primary": (ref, cmp_) in PRIMARY,
            "delta_pp": float(diff.mean() * 100), **r,
            "topic_perm_p": signflip_exact(per_topic.values),
            "topic_boot_ci_pp": [lo, hi],
            "topics_nonzero": int((per_topic != 0).sum()),
        })
    prim = [c for c in out if c["primary"]]
    for c, a in zip(prim, holm([c["p_exact"] for c in prim])):
        c["holm_exact"] = a
    for c, a in zip(prim, holm([c["topic_perm_p"] for c in prim])):
        c["holm_topic"] = a
    return out


def gee_block(q: pd.DataFrame, col: str = "correct") -> dict:
    m5 = q[q.condition.isin(MATCHED5)].copy()
    m5["cond"] = pd.Categorical(m5.condition, categories=MATCHED5)
    res = {}
    X = pd.get_dummies(m5.cond, drop_first=True).astype(float)
    X = sm.add_constant(X)
    y = m5[col].astype(float)
    logit = sm.Logit(y, X).fit(disp=False)
    for unit, groups in [("prompt", m5.prompt_id), ("proposition", m5.semantic_id), ("topic", m5.target_entity)]:
        g = GEE(y, X, groups=pd.factorize(groups)[0], family=Binomial(), cov_struct=Independence()).fit()
        for c in MATCHED5[1:]:
            res.setdefault(COND_LABEL[c], {})[unit] = {
                "beta": float(g.params[c]), "se_robust": float(g.bse[c]), "p": float(g.pvalues[c]),
            }
    for c in MATCHED5[1:]:
        res[COND_LABEL[c]]["model_based_logit"] = {"se": float(logit.bse[c]), "p": float(logit.pvalues[c])}
    # MIXED vs CS-LAT on the 200 rows of those two conditions
    two = q[q.condition.isin(["D_CS", "E_MIXED_SCRIPT"])].copy()
    X2 = sm.add_constant((two.condition == "E_MIXED_SCRIPT").astype(float).rename("mixed"))
    y2 = two[col].astype(float)
    for unit, groups in [("prompt", two.prompt_id), ("proposition", two.semantic_id), ("topic", two.target_entity)]:
        g = GEE(y2, X2, groups=pd.factorize(groups)[0], family=Binomial(), cov_struct=Independence()).fit()
        res.setdefault("MIXED_vs_CS-LAT", {})[unit] = {
            "beta": float(g.params["mixed"]), "se_robust": float(g.bse["mixed"]), "p": float(g.pvalues["mixed"]),
            "or": float(np.exp(g.params["mixed"])),
            "or_ci": [float(np.exp(g.params["mixed"] - 1.959964 * g.bse["mixed"])),
                      float(np.exp(g.params["mixed"] + 1.959964 * g.bse["mixed"]))],
        }
    return res


def icc_block(q: pd.DataFrame, col: str = "correct") -> dict:
    m5 = q[q.condition.isin(MATCHED5)]
    k, m = m5.target_entity.nunique(), len(m5) // m5.target_entity.nunique()
    means = m5.groupby("target_entity")[col].mean()
    msb = m * ((means - m5[col].mean()) ** 2).sum() / (k - 1)
    ssw = m5.groupby("target_entity")[col].apply(lambda s: ((s - s.mean()) ** 2).sum()).sum()
    msw = ssw / (len(m5) - k)
    s2u = max(0.0, (msb - msw) / m)
    icc = s2u / (s2u + msw)
    deff = 1 + (m - 1) * icc
    return {"icc": icc, "deff": deff, "n_eff": len(m5) / deff, "m": m, "k": k}


def language_perm(q: pd.DataFrame, col: str = "correct", n_perm: int = 10000, seed: int = 0) -> dict:
    """Interaction SS of the language x condition accuracy table; null permutes
    language labels among the five propositions of each topic."""
    m5 = q[q.condition.isin(MATCHED5)]
    piv = m5.pivot(index="semantic_id", columns="condition", values=col)[MATCHED5]
    meta = m5.drop_duplicates("semantic_id").set_index("semantic_id").loc[piv.index]
    langs = meta.language.values
    topics = meta.target_entity.values

    def stat(lab):
        tab = pd.DataFrame(piv.values).groupby(lab).mean().values
        resid = tab - tab.mean(1, keepdims=True) - tab.mean(0, keepdims=True) + tab.mean()
        return float((resid ** 2).sum())

    obs = stat(langs)
    rng = np.random.default_rng(seed)
    idx_by_topic = [np.where(topics == t)[0] for t in np.unique(topics)]
    count = 0
    for _ in range(n_perm):
        lab = langs.copy()
        for idx in idx_by_topic:
            lab[idx] = rng.permutation(langs[idx])
        count += stat(lab) >= obs - 1e-12
    return {"stat": obs, "p": (count + 1) / (n_perm + 1), "n_perm": n_perm}


def tipping(acc_ref: float, acc_cmp: float, fprs=(0.0, 0.04, 0.08, 0.12, 0.16)) -> dict:
    """Judge sensitivity on the comparison condition at which its true accuracy
    equals the reference's, assuming the reference is judged without error."""
    return {f"{f:.2f}": (acc_cmp - f * (1 - acc_ref)) / acc_ref for f in fprs}


def power(n_topics: int, icc: float, effect: float, p: float = 0.4, m: int = 5) -> dict:
    n = n_topics * m
    deff = 1 + (m - 1) * icc
    se = np.sqrt(2 * p * (1 - p) * deff / n)
    pw = stats.norm.cdf(effect / se - 1.959964)
    mde = (1.959964 + stats.norm.ppf(0.8)) * se
    return {"power": float(pw), "mde": float(mde)}


def tokenizer_block(q: pd.DataFrame) -> dict:
    from tokenizers import Tokenizer
    out = {}
    for name in ["Qwen/Qwen2.5-7B", "Qwen/Qwen3.8-27B"]:
        tok = Tokenizer.from_pretrained(name)
        n_tok = q.prompt_text.apply(lambda s: len(tok.encode(s, add_special_tokens=False).ids))
        offset = q.prompt_tokens - n_tok
        resp_tok = q.model_response.apply(lambda s: len(tok.encode(s, add_special_tokens=False).ids))
        cpt = q.prompt_text.str.len() / n_tok
        key = name.split("/")[1]
        q[f"cpt_{key}"] = cpt
        q[f"resp_tok_{key}"] = resp_tok
        out[key] = {
            "api_offset_counts": {str(k): int(v) for k, v in offset.value_counts().items()},
            "constant_offset": bool(offset.nunique() == 1),
            "resp_tokens_when_api_128": resp_tok[q.completion_tokens == 128].describe()[["mean", "min", "max"]].to_dict(),
            "cpt_by_condition": {COND_LABEL[c]: float(cpt[q.condition == c].mean()) for c in ORDER},
        }
    return out


def mediation(q: pd.DataFrame, cpt_col: str, col: str = "correct") -> dict:
    two = q[q.condition.isin(["D_CS", "E_MIXED_SCRIPT"])].copy()
    two["mixed"] = (two.condition == "E_MIXED_SCRIPT").astype(int)
    two["cpt"] = two[cpt_col]
    tot = smf.logit(f"{col} ~ mixed", two).fit(disp=False)
    a = smf.ols("cpt ~ mixed", two).fit()
    b = smf.logit(f"{col} ~ mixed + cpt", two).fit(disp=False)
    ab = a.params["mixed"] * b.params["cpt"]
    se = np.sqrt(b.params["cpt"] ** 2 * a.bse["mixed"] ** 2 + a.params["mixed"] ** 2 * b.bse["cpt"] ** 2)
    z = ab / se
    # Within-condition spread of the mediator (identification depends on it).
    within_sd = two.groupby("mixed").cpt.std().to_dict()
    return {
        "a": float(a.params["mixed"]), "a_se": float(a.bse["mixed"]),
        "b": float(b.params["cpt"]), "b_se": float(b.bse["cpt"]), "b_p": float(b.pvalues["cpt"]),
        "b_ci": [float(b.params["cpt"] - 1.959964 * b.bse["cpt"]), float(b.params["cpt"] + 1.959964 * b.bse["cpt"])],
        "total": float(tot.params["mixed"]), "direct": float(b.params["mixed"]),
        "sobel_z": float(z), "sobel_p": float(2 * stats.norm.sf(abs(z))),
        "mediator_within_condition_sd": {str(k): float(v) for k, v in within_sd.items()},
        "corr_mediator_condition": float(np.corrcoef(two.mixed, two.cpt)[0, 1]),
    }


def response_block(q: pd.DataFrame) -> dict:
    q = q.copy()
    q["bshare"] = q.model_response.apply(brahmic_share)
    q["chars"] = q.model_response.str.len()
    q["mid"] = q.model_response.apply(ends_mid_sentence)
    q["kw"] = q.judge_reason.astype(str).apply(lambda r: bool(INCOMPLETE_KW.search(r)))
    q["rule"] = (q.completion_tokens == 128) & q.mid & (q.correct == 0) & q.kw
    out = {}
    for c in ORDER:
        s = q[q.condition == c]
        out[COND_LABEL[c]] = {
            "n": len(s), "acc": float(s.correct.mean()),
            "cap_hit_128": int((s.completion_tokens == 128).sum()),
            "ends_mid_sentence": int(s.mid.sum()),
            "mean_chars": float(s.chars.mean()),
            "brahmic_majority_pct": float((s.bshare > 0.5).mean() * 100),
            "brahmic_any_pct": float((s.bshare > 0.0).mean() * 100),
            "errors": int((s.correct == 0).sum()),
            "incomplete_rule": int(s.rule.sum()),
            "prompt_script_transitions": float(s.prompt_text.apply(script_transitions).mean()),
        }
    return out


def numeral_block(q: pd.DataFrame) -> dict:
    s = q[q.reference_answer.apply(lambda g: len(gold_numerals(g)) > 0)].copy()
    res = {"n_rows": len(s), "n_topics": int(s.target_entity.nunique())}
    for nd in (False, True):
        s["num_ok"] = s.apply(lambda r: numerals_present(r.reference_answer, r.model_response, nd), axis=1)
        agree = (s.num_ok.astype(int) == s.correct).mean()
        res["native_digits_normalised" if nd else "ascii_only"] = {
            "agreement": float(agree),
            "judge_correct_without_numeral": int(((s.correct == 1) & ~s.num_ok).sum()),
            "judge_wrong_with_numeral": int(((s.correct == 0) & s.num_ok).sum()),
            "by_condition_agreement": {COND_LABEL[c]: float((s[s.condition == c].num_ok.astype(int) == s[s.condition == c].correct).mean()) for c in ORDER},
        }
    return res


def main() -> None:
    labels = sys.argv[sys.argv.index("--labels") + 1] if "--labels" in sys.argv else "stored"
    df = load(labels)
    q = df[df.model == QWEN].copy()
    a = df[df.model == ALLAM].copy()
    assert len(q) == 600 and q.groupby("condition").size().eq(100).all()

    N = {"model_ids": sorted(df.model.unique().tolist()),
         "git_commits": sorted(df.git_commit.unique().tolist())}
    N["accuracy"] = {}
    for c in ORDER:
        s = q[q.condition == c]
        k = int(s.correct.sum())
        per_topic = s.groupby("target_entity").correct.mean() * 100
        N["accuracy"][COND_LABEL[c]] = {
            "k": k, "n": len(s), "wilson": [x * 100 for x in wilson(k, len(s))],
            "topic_boot_ci": list(topic_bootstrap(per_topic.values)),
            "topics_all5": int((per_topic == 100).sum()), "topics_none": int((per_topic == 0).sum()),
        }
    N["contrasts"] = contrasts(q)
    N["gee"] = gee_block(q)
    N["icc"] = icc_block(q)
    N["language_perm"] = language_perm(q)
    lang = q[q.condition.isin(ORDER)].groupby(["language", "condition"]).correct.mean().unstack() * 100
    N["by_language"] = {l: {COND_LABEL[c]: float(lang.loc[l, c]) for c in ORDER} for l in lang.index}
    topic = q.groupby(["target_entity", "condition"]).correct.sum().unstack()
    N["by_topic"] = {t: {COND_LABEL[c]: int(topic.loc[t, c]) for c in ORDER} for t in topic.index}

    acc = {COND_LABEL[c]: q[q.condition == c].correct.mean() for c in ORDER}
    N["tipping"] = {
        "CS-LAT_vs_EN-MATCH": tipping(acc["EN-MATCH"], acc["CS-LAT"]),
        "MIXED_vs_EN-MATCH": tipping(acc["EN-MATCH"], acc["MIXED"]),
        "MIXED_vs_CS-LAT": tipping(acc["CS-LAT"], acc["MIXED"]),
    }
    allam_k = {COND_LABEL[c]: int(a[a.condition == c].correct.sum()) for c in ORDER}
    N["allam"] = {k: {"k": v, "wilson": [x * 100 for x in wilson(v, 100)]} for k, v in allam_k.items()}
    five = ["EN-MATCH", "CS-LAT", "ROMAN", "NATIVE", "MIXED"]
    rho = stats.spearmanr([acc[c] for c in five], [allam_k[c] for c in five])
    N["allam_spearman"] = {"rho": float(rho.statistic), "p": float(rho.pvalue)}

    N["response"] = response_block(q)
    N["numerals"] = numeral_block(q)
    N["power"] = {
        "orig_45": power(45, 0.2663, 0.21), "orig_20": power(20, 0.2663, 0.21),
        "matched_45": power(45, N["icc"]["icc"], 0.17), "matched_20": power(20, N["icc"]["icc"], 0.17),
    }
    try:
        N["tokenizer_check"] = tokenizer_block(q)
        for key in ["Qwen2.5-7B", "Qwen3.8-27B"]:
            N.setdefault("mediation", {})[key] = mediation(q, f"cpt_{key}")
            cpt = N["tokenizer_check"][key]["cpt_by_condition"]
            r = stats.spearmanr([cpt[COND_LABEL[c]] for c in ORDER], [acc[COND_LABEL[c]] for c in ORDER])
            N["tokenizer_check"][key]["spearman_cpt_acc_6cond"] = float(r.statistic)
            N["tokenizer_check"][key]["resp_chars_per_token"] = {
                COND_LABEL[c]: float((q[q.condition == c].model_response.str.len() / q[q.condition == c][f"resp_tok_{key}"]).mean())
                for c in ORDER}
    except Exception as e:  # tokenizer download unavailable
        N["tokenizer_check"] = {"error": str(e)}

    N["labels"] = labels
    # Sensitivity: CS-LAT vs MIXED on word-identical languages; primary family without
    # the three topics whose gold answer is narrower than the generic question.
    ident = q[q.language.isin(["hi", "ta", "bn"])]
    N["sensitivity"] = {"cslat_mixed_word_identical_hi_ta_bn": contrasts(ident)[4]}
    amb = ["GST Registration Exemption", "Medical Termination of Pregnancy Act", "Environment Clearance Public Hearing"]
    N["sensitivity"]["primary_excluding_ambiguous_gold"] = [c for c in contrasts(q[~q.target_entity.isin(amb)]) if c["primary"]]
    name = "numbers_original.json" if labels == "stored" else f"numbers_{labels}.json"
    (OUT / name).write_text(json.dumps(N, indent=2, ensure_ascii=False), encoding="utf-8")
    print("wrote", OUT / name)


if __name__ == "__main__":
    main()
