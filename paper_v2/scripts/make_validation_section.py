"""Write paper_v2/VALIDATION_RESULTS.md: the human-validation, complete-answer (EXP-006) and
second-model (EXP-007) results, with tables and paste-ready paragraphs for the paper.

Inputs (all produced by other scripts; nothing is recomputed here):
  paper_v2/output/numbers_human_eval.json                    scripts/analyze_human_eval.py
  paper_v2/output/sensitivity_no_mtp/numbers_human_eval.json   same, --exclude-topic "Medical Termination of Pregnancy Act"
  paper_v2/output/numbers_followups.json                      paper_v2/scripts/analyze_followups.py
Run:  python paper_v2/scripts/make_validation_section.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "paper_v2" / "output"
LANG = {"en": "English", "hi": "Hindi", "te": "Telugu", "ta": "Tamil", "kn": "Kannada", "bn": "Bengali"}
CELLS = [f"{b}|{c}" for b in (128, 512, 1024) for c in ("EN-MATCH", "CS-LAT", "MIXED")]
GAPS = [f"{b}|{g}" for b in (128, 512, 1024) for g in ("MIXED-CS-LAT", "CS-LAT-EN-MATCH")]


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def f2(x):
    return "–" if x is None else f"{x:.2f}"


def ci(d):
    return f"{d['estimate']:+.0f} [{d['ci'][0]:+.0f}, {d['ci'][1]:+.0f}]"


def acc(d):
    return f"{d['estimate']:.0f} [{d['ci'][0]:.0f}, {d['ci'][1]:.0f}]"


def human_section(H, S) -> list[str]:
    ia, fl, rv = H["inter_annotator"], H["final_labels"], H["reviewers"]
    n_items = sum(v["assigned"] for v in rv.values())
    L = ["## 1. Human validation of the judge labels", ""]
    L += [f"- Sample: 216 of the 900 Qwen3.8-27B outputs (EN-MATCH, CS-LAT, MIXED × 128/512/1,024 tokens), "
          f"stratified within each budget × condition cell by judge-agreement pattern; inverse-probability weights "
          f"make the estimates describe all 900 outputs.",
          f"- {len(rv)} fluent readers (CSE students), {n_items} labels; reviewers saw question, gold and answer only "
          f"(no condition, budget or judge label).",
          f"- Double-labelled items: {ia['n_double_labelled']}; binary agreement {ia['binary_agreement']:.2f}; "
          f"Cohen's κ = {ia['kappa_binary']:.2f} (primary collapse), {ia['kappa_binary_secondary']:.2f} (secondary).",
          f"- Disagreements: {H['adjudication']['binary_disagreements']}; adjudicated {H['adjudication']['adjudicated']}; "
          f"unresolved items ({fl['unresolved']}) are excluded from the estimates below.",
          "- Bengali has one reader only, so no Bengali agreement figure.", ""]
    L += ["| Language | Double-labelled | Agreement | κ |", "|---|---|---|---|"]
    for l, v in ia["by_language"].items():
        L.append(f"| {LANG.get(l, l)} | {v['n']} | {v['binary_agreement']:.2f} | {f2(v['kappa'])} |")
    L += ["", "### Judge accuracy against the human label (weighted to all 900 outputs)", "",
          "| Collapse | Judge | Sensitivity | Specificity | Agreement | κ |", "|---|---|---|---|---|---|"]
    for tag in ("primary", "secondary"):
        for j in ("J-QWEN", "J-OSS"):
            o = H["judge_validation"][tag][j]["overall"]
            L.append(f"| {tag} | {j} | {f2(o['sensitivity'])} | {f2(o['specificity'])} | {f2(o['agreement'])} | {f2(o['kappa_unweighted'])} |")
    if S:
        for j in ("J-QWEN", "J-OSS"):
            o = S["judge_validation"]["primary"][j]["overall"]
            L.append(f"| primary, MTP topic excluded | {j} | {f2(o['sensitivity'])} | {f2(o['specificity'])} | {f2(o['agreement'])} | {f2(o['kappa_unweighted'])} |")
    L += ["", "Primary collapse: CORRECT = 1, everything else 0. Secondary: CORRECT, PARTIAL and CORRECT_OTHER_READING = 1.", ""]
    L += ["### Human-estimated accuracy and gaps (primary collapse; % with stratified-bootstrap 95% CI)", "",
          "| Budget × condition | Human accuracy |" + (" MTP excluded |" if S else ""), "|---|---|" + ("---|" if S else "")]
    for c in CELLS:
        row = f"| {c.replace('|', ' / ')} | {acc(H['human_accuracy']['primary']['cells'][c])} |"
        if S:
            row += f" {acc(S['human_accuracy']['primary']['cells'][c])} |"
        L.append(row)
    L += ["", "| Gap (pp) | Human estimate |" + (" MTP excluded |" if S else ""), "|---|---|" + ("---|" if S else "")]
    for g in GAPS:
        row = f"| {g.replace('|', ' / ')} | {ci(H['human_accuracy']['primary']['gaps'][g])} |"
        if S:
            row += f" {ci(S['human_accuracy']['primary']['gaps'][g])} |"
        L.append(row)
    flags = {f["item_id"] for f in H["gold_problem_flags"]}
    L += ["", f"Gold-answer flags: reviewers flagged {len(flags)} items, all on the Medical Termination of Pregnancy "
          "Act question (the 2021 amendment allows one practitioner up to 20 weeks; the gold names two). The gold "
          "ledger already marks this question AMBIGUOUS; the MTP-excluded column is the sensitivity check.", ""]
    return L


def followup_section(F) -> list[str]:
    L = []
    e6 = F and F.get("exp006_complete_answers")
    L += ["## 2. Complete answers (EXP-006: capped 1,024-token answers re-run at 3,072 tokens)", ""]
    if not e6:
        L += ["Not run yet.", ""]
    else:
        L += [f"- Responses re-answered: {e6['rerun_count']}; still capped at 3,072: {e6['still_capped_at_3072']}.", "",
              "| Judge | EN-MATCH | CS-LAT | MIXED |", "|---|---|---|---|"]
        for j in ("J-QWEN", "J-OSS"):
            a = e6[j]["accuracy"]
            L.append(f"| {j} | " + " | ".join(f"{a.get(c, float('nan')):.0f}" for c in ("EN-MATCH", "CS-LAT", "MIXED")) + " |")
        L += ["", "| Judge | Contrast | Δ pp | McNemar p | topic sign-flip p | topic bootstrap 95% CI |", "|---|---|---|---|---|---|"]
        for j in ("J-QWEN", "J-OSS"):
            for c in e6[j]["contrasts"]:
                L.append(contrast_row(j, c))
        L.append("")
    e7 = F and F.get("exp007_second_model")
    L += ["## 3. Second answering model (EXP-007)", ""]
    if not e7:
        L += ["Not run yet.", ""]
    else:
        L += [f"Model: {', '.join(e7['model'])} (temperature 0, thinking off); same prompts, same two judges.", ""]
        for b, e in e7["budgets"].items():
            L += [f"### {b} tokens (n = {e['n']}; hit cap: {e['hit_cap']})", "",
                  "| Judge | EN-MATCH | CS-LAT | MIXED |", "|---|---|---|---|"]
            for j in ("J-QWEN", "J-OSS"):
                a = e[j]["accuracy"]
                L.append(f"| {j} | " + " | ".join(f"{a.get(c, float('nan')):.0f}" for c in ("EN-MATCH", "CS-LAT", "MIXED")) + " |")
            L += ["", "| Judge | Contrast | Δ pp | McNemar p | topic sign-flip p | topic bootstrap 95% CI |", "|---|---|---|---|---|---|"]
            for j in ("J-QWEN", "J-OSS"):
                for c in e[j]["contrasts"]:
                    L.append(contrast_row(j, c))
            ag = e.get("judge_agreement")
            if ag:
                L += ["", f"Judge agreement {ag['agreement']:.3f} (κ = {f2(ag['kappa'])}); J-QWEN correct / J-OSS wrong "
                      f"{ag['qwen_correct_oss_wrong']}, reverse {ag['qwen_wrong_oss_correct']}."]
            L.append("")
    return L


def contrast_row(j, c):
    p, tp, bc = c["p_exact"], c.get("topic_perm_p"), c.get("topic_boot_ci")
    tp_s = "–" if tp is None else f"{tp:.3f}"
    bc_s = "–" if not bc else f"[{bc[0]:+.1f}, {bc[1]:+.1f}]"
    return f"| {j} | {c['cmp']} − {c['ref']} | {c['delta_pp']:+.1f} | {p:.3f} | {tp_s} | {bc_s} |"


def main():
    H = load(OUT / "numbers_human_eval.json")
    S = load(OUT / "sensitivity_no_mtp" / "numbers_human_eval.json")
    F = load(OUT / "numbers_followups.json")
    L = ["# Validation results (generated — do not edit by hand)", "",
         "Generated by `paper_v2/scripts/make_validation_section.py` from the JSON files in `paper_v2/output/`.", ""]
    L += human_section(H, S) if H else ["Human evaluation not analysed yet.", ""]
    L += followup_section(F)
    (ROOT / "paper_v2" / "VALIDATION_RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("wrote paper_v2/VALIDATION_RESULTS.md")


if __name__ == "__main__":
    main()
