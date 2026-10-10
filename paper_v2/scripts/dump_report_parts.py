"""Generate the data-driven parts of FULL_REVISION_REPORT.md (tables + final manuscript text).

Writes paper_v2/output/report_generated.md. Everything here is read from the JSON result files
or from the TEXT used by build_paper.py, so the report cannot drift from the numbers or the DOCX.
"""

import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_paper as bp  # noqa: E402
from build_revised_docx import L6, NE, NJ, NO, PROVISION, fp, sgn  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
NB = json.loads((ROOT / "paper_v2/output/numbers_budgets.json").read_text(encoding="utf-8"))
G3 = ["EN-MATCH", "CS-LAT", "MIXED"]
BUD = ["128", "512", "1024"]
out = io.StringIO()


def row(*a):
    print("| " + " | ".join(str(x) for x in a) + " |")


def sep(n):
    row(*["---"] * n)


def p(x):
    return "<0.001" if x < 0.001 else fp(x)


with redirect_stdout(out):
    print("## G1. Three-budget results (EXP-004 + EXP-005), both judges\n")
    print("### G1.1 Accuracy (%, n = 100 per cell) with Wilson 95% CI\n")
    row("Judge", "Budget", "EN-MATCH", "CS-LAT", "MIXED")
    sep(5)
    for j in ["J-QWEN", "J-OSS"]:
        for b in BUD:
            a = NB["accuracy"][j][b]
            row(j, b, *[f"{a[c]['pct']:.0f} [{a[c]['wilson'][0]:.1f}, {a[c]['wilson'][1]:.1f}]" for c in G3])
    print("\n### G1.2 Paired contrasts at each budget (comparison vs reference)\n")
    print("b = reference correct & comparison wrong; c = the reverse. Topic p = exact sign-flip over 2^20 patterns; "
          "topic CI = percentile bootstrap over 20 topics (10,000 resamples).\n")
    row("Judge", "Budget", "Contrast", "Ref %", "Cmp %", "Δ (pp)", "b", "c", "Exact p", "Topic p", "Topic 95% CI")
    sep(11)
    for j in ["J-QWEN", "J-OSS"]:
        for b in BUD:
            for x in NB["contrasts"][j][b]:
                lo, hi = x["topic_boot_ci"]
                row(j, b, f"{x['cmp']} vs {x['ref']}", f"{x['acc_ref']:.0f}", f"{x['acc_cmp']:.0f}", sgn(x["delta_pp"]),
                    x["b"], x["c"], p(x["p_exact"]), p(x["topic_perm_p"]), f"[{lo:.0f}, {hi:.0f}]")
    print("\n### G1.3 Within-condition change between budgets (same judge)\n")
    row("Judge", "Change", "Condition", "Acc before", "Acc after", "Lost (b)", "Gained (c)", "Exact p", "Topic p",
        "Topic 95% CI")
    sep(10)
    for j in ["J-QWEN", "J-OSS"]:
        for k, v in NB["within_condition"][j].items():
            for c, x in v.items():
                lo, hi = x["topic_boot_ci"]
                row(j, k, c, f"{x['acc0']:.0f}", f"{x['acc1']:.0f}", x["b"], x["c"], p(x["p_exact"]),
                    p(x["topic_perm_p"]), f"[{lo:.0f}, {hi:.0f}]")
    print("\n### G1.4 Change in each gap between budgets (per-topic difference-in-differences)\n")
    row("Judge", "Change", "Gap", "Gap before", "Gap after", "Change", "Topic 95% CI", "Topic p")
    sep(8)
    for j in ["J-QWEN", "J-OSS"]:
        for k, v in NB["gap_change"][j].items():
            for g, x in v.items():
                lo, hi = x["topic_boot_ci"]
                row(j, k, g, f"{x['gap0']:.0f}", f"{x['gap1']:.0f}", sgn(x["change"]), f"[{lo:.0f}, {hi:.0f}]",
                    p(x["topic_perm_p"]))
    print("\n### G1.5 MIXED vs CS-LAT on the 60 word-identical propositions (hi, ta, bn)\n")
    row("Judge", "Budget", "CS-LAT %", "MIXED %", "b", "c", "Exact p", "Topic p")
    sep(8)
    for j in ["J-QWEN", "J-OSS"]:
        for b in BUD:
            x = NB["word_identical_mixed_vs_cslat"][j][b]
            row(j, b, f"{x['acc_ref']:.1f}", f"{x['acc_cmp']:.1f}", x["b"], x["c"], p(x["p_exact"]), p(x["topic_perm_p"]))
    print("\n### G1.6 Generation descriptives by budget\n")
    row("Budget", "Condition", "Stopped before cap (of 100)", "Hit cap", "Mean completion tokens", "Mean chars",
        "Mostly Brahmic %")
    sep(7)
    for b in BUD:
        for c in G3:
            x = NB["generation"][b][c]
            row(b, c, x["stopped_before_cap"], 100 - x["stopped_before_cap"], f"{x['mean_completion_tokens']:.0f}",
                f"{x['mean_chars']:,.0f}", f"{x['mostly_brahmic_pct']:.0f}")
    pc = NB["prefix_consistency"]
    print(f"\nPrefix consistency (longer response begins with the shorter one, of 100): 512 starts with 128 — "
          + ", ".join(f"{k} {v}" for k, v in pc["512_starts_with_128"].items())
          + "; 1,024 starts with 512 — " + ", ".join(f"{k} {v}" for k, v in pc["1024_starts_with_512"].items()) + ".\n")

    print("## G2. Judge agreement (J-QWEN vs J-OSS) by budget and condition\n")
    row("Budget", "Condition", "n", "Both correct", "Both wrong", "Q correct / O wrong", "Q wrong / O correct",
        "Agreement", "κ", "κ topic 95% CI", "P(Q correct | O wrong)", "P(O correct | Q wrong)")
    sep(12)
    for b in BUD:
        for c, x in NB["judge_agreement"][b].items():
            lo, hi = x["kappa_topic_ci"]
            row(b, c, x["n"], x["both_correct"], x["both_wrong"], x["qwen_correct_oss_wrong"],
                x["qwen_wrong_oss_correct"], f"{x['agreement']:.3f}", f"{x['kappa']:.2f}", f"[{lo:.2f}, {hi:.2f}]",
                f"{x['p_qwen_correct_given_oss_wrong']:.2f}", f"{x['p_oss_correct_given_qwen_wrong']:.2f}")
    print("\nAgreement at 128 tokens across all six conditions (from EXP-004): 75.7% (146 both correct, 308 both "
          "wrong, 128 Q-correct/O-wrong, 18 Q-wrong/O-correct).\n")
    print("### G2.1 Per condition, all six conditions at 128 tokens (EXP-004)\n")
    row("Condition", "Stored vs J-QWEN", "J-QWEN vs J-OSS", "κ")
    sep(4)
    for c in L6:
        A = NE["agreement_orig128"][c]
        row(c, f"{A['stored_vs_jqwen']:.2f}", f"{A['jqwen_vs_joss']:.2f}", f"{A['kappa_jqwen_joss']:.2f}")

    print("\n## G3. Does the conclusion change? (α = 0.05)\n")
    row("Judge", "Budget", "Contrast", "Δ (pp)", "Exact p", "Topic p", "Significant (proposition)", "Significant (topic)")
    sep(8)
    for r in NB["conclusion_matrix"]:
        row(r["judge"], r["budget"], r["contrast"], sgn(r["delta_pp"]), p(r["p_exact"]), p(r["topic_p"]),
            "yes" if r["sig_prop"] else "no", "yes" if r["sig_topic"] else "no")

    print("\n## G4. EXP-005 cost and failures\n")
    for m, v in NB["exp005_tokens"].items():
        print(f"* {m}: {v['calls']} calls, {v['in']:,} input tokens, {v['out']:,} output tokens, "
              f"${NB['exp005_spend'][m]:.3f}")
    print(f"* Total EXP-005: ${NB['exp005_spend']['total']:.3f}")
    print(f"* Persistent failures logged: {len(NB['exp005_failures_logged'])}; parse failures: "
          + ", ".join(f"{k} {v}" for k, v in NB["parse_failures"].items()))

    print("\n## G5. 128-token results, all six conditions (harmonised J-QWEN labels)\n")
    row("Condition", "Acc %", "Wilson CI", "Topic-boot CI", "Stored", "J-OSS", "Topics 5/5", "Topics 0/5")
    sep(8)
    for c in L6:
        a = NJ["accuracy"][c]
        row(c, a["k"], f"[{a['wilson'][0]:.1f}, {a['wilson'][1]:.1f}]",
            f"[{a['topic_boot_ci'][0]:.0f}, {a['topic_boot_ci'][1]:.0f}]", NO["accuracy"][c]["k"],
            f"{NE['orig128']['J-OSS']['accuracy'][c]:.0f}", a["topics_all5"], a["topics_none"])
    print("\n### G5.1 All 11 pairwise contrasts (J-QWEN)\n")
    row("Contrast", "Δ", "b", "c", "Exact p", "Holm (primary)", "Topic p", "Holm topic", "Topic CI", "Topics differing")
    sep(10)
    for x in NJ["contrasts"]:
        lo, hi = x["topic_boot_ci_pp"]
        row(f"{x['cmp']} vs {x['ref']}", sgn(x["delta_pp"]), x["b"], x["c"], p(x["p_exact"]),
            p(x["holm_exact"]) if "holm_exact" in x else "–", p(x["topic_perm_p"]),
            p(x["holm_topic"]) if "holm_topic" in x else "–", f"[{lo:.0f}, {hi:.0f}]", x["topics_nonzero"])
    print("\n### G5.2 Same, stored labels (original PDF numbers)\n")
    row("Contrast", "Δ", "b", "c", "Exact p", "Holm (primary)", "Topic p", "Holm topic", "Topic CI")
    sep(9)
    for x in NO["contrasts"]:
        lo, hi = x["topic_boot_ci_pp"]
        row(f"{x['cmp']} vs {x['ref']}", sgn(x["delta_pp"]), x["b"], x["c"], p(x["p_exact"]),
            p(x["holm_exact"]) if "holm_exact" in x else "–", p(x["topic_perm_p"]),
            p(x["holm_topic"]) if "holm_topic" in x else "–", f"[{lo:.0f}, {hi:.0f}]")
    print("\n### G5.3 J-OSS primary contrasts at 128 tokens\n")
    row("Contrast", "Δ", "b", "c", "Exact p", "Holm", "Topic p", "Holm topic")
    sep(8)
    for x in NE["orig128"]["J-OSS"]["primary"]:
        row(f"{x['cmp']} vs {x['ref']}", sgn(x["delta_pp"]), x["b"], x["c"], p(x["p_exact"]), p(x["holm_exact"]),
            p(x["topic_perm_p"]), p(x["holm_topic"]))
    print("\n### G5.4 GEE (J-QWEN), log-odds vs EN-MATCH or CS-LAT\n")
    row("Contrast", "Unit", "β", "Robust SE", "p")
    sep(5)
    for c in ["CS-LAT", "ROMAN", "NATIVE", "MIXED", "MIXED_vs_CS-LAT"]:
        for u in ["prompt", "proposition", "topic"]:
            x = NJ["gee"][c][u]
            row(c, u, f"{x['beta']:.3f}", f"{x['se_robust']:.3f}", p(x["p"]))
    print("\n### G5.5 Per-language accuracy (J-QWEN, %)\n")
    row("Language", *L6)
    sep(7)
    for n, k in [("Hindi", "hi"), ("Bengali", "bn"), ("Tamil", "ta"), ("Telugu", "te"), ("Kannada", "kn")]:
        row(n, *[f"{NJ['by_language'][k][c]:.0f}" for c in L6])
    print("\n### G5.6 Per-topic correct languages (of 5), J-QWEN, with provision and gold status\n")
    row("Topic", "Provision verified", "Gold", *L6)
    sep(9)
    for t in sorted(NJ["by_topic"], key=lambda t: (-NJ["by_topic"][t]["EN-MATCH"], -NJ["by_topic"][t]["EN-ORIG"], t)):
        row(t, PROVISION[t][0], PROVISION[t][1], *[NJ["by_topic"][t][c] for c in L6])
    print("\n### G5.7 Response-side descriptors at 128 tokens (J-QWEN for errors/incompleteness)\n")
    R, T = NJ["response"], NJ["tokenizer_check"]
    row("Condition", "Script transitions", "Prompt chars/tok Qwen3.8", "Prompt chars/tok Qwen2.5 (old)",
        "Resp. chars", "Mostly Brahmic %", "Any Brahmic %", "Ends mid-sentence", "Hit 128", "Errors", "Incomplete rule")
    sep(11)
    for c in L6:
        row(c, f"{R[c]['prompt_script_transitions']:.1f}", f"{T['Qwen3.8-27B']['cpt_by_condition'][c]:.2f}",
            f"{T['Qwen2.5-7B']['cpt_by_condition'][c]:.2f}", f"{R[c]['mean_chars']:.0f}",
            f"{R[c]['brahmic_majority_pct']:.0f}", f"{R[c]['brahmic_any_pct']:.0f}", R[c]["ends_mid_sentence"],
            R[c]["cap_hit_128"], R[c]["errors"], R[c]["incomplete_rule"])
    print("\n### G5.8 Tipping points (J-QWEN)\n")
    row("FPR", "CS-LAT vs EN-MATCH", "MIXED vs EN-MATCH", "MIXED vs CS-LAT")
    sep(4)
    for f in ["0.00", "0.04", "0.08", "0.12", "0.16"]:
        row(f, *[f"{NJ['tipping'][k][f]:.2f}" for k in ["CS-LAT_vs_EN-MATCH", "MIXED_vs_EN-MATCH", "MIXED_vs_CS-LAT"]])

    print("\n## G6. Final manuscript text exactly as built into the DOCX (build_paper.py)\n")
    T_ = bp.TEXT
    order = [("Title", "title"), ("Abstract", "abstract"), ("Index Terms", "index"),
             ("I ¶3", 9), ("I Research questions", 13), ("I Contributions", 14), ("I Findings in brief", 15),
             ("II Multilingual evaluation", 18), ("II Tokenization", 19), ("II Judges", 20),
             ("Fig. 1 caption", "fig1"), ("Table I caption", "tab1"),
             ("III-A conditions", 28), ("III-B amendment", 30), ("III-C gold answers", 34),
             ("IV intro", 36), ("IV Models", 37), ("IV Prompting", 38), ("IV Judging", 39), ("IV Statistics", 40),
             ("V heading", 41), ("V-A", 43), ("Table II caption", "tab2"), ("Fig. 2 caption", "fig2"),
             ("Fig. 3 caption", "fig3"), ("V-A uncertainty", 53), ("V-B heading", 54), ("V-B", 55), ("V-B note", 57),
             ("V-C", 59), ("Fig. 4 caption", "fig4"), ("V-D languages", 65), ("V-D models", 66),
             ("VI heading", 67), ("VI-A heading", 68), ("VI-A tokenization", 69), ("Fig. 5 caption", "fig5"),
             ("VI-B heading", 74), ("VI-B response side", 75), ("VI-B budget reruns", 76),
             ("Table III caption", "tab3"), ("VI-B conclusions", 77), ("VII heading", 78),
             ("VII judge dependence", 79), ("Table IV caption", "tab4"), ("VII tipping", 80),
             ("Table V caption", "tab5"), ("VIII Discussion 1", 83), ("VIII Discussion 2", 84),
             ("Table VI caption", "tab6"), ("IX Limitations", 87), ("X Ethics", 89), ("Reproducibility", 91),
             ("App. A.1", 94), ("Table VII caption", "tab7"), ("App. B", "appB"), ("Table VIII caption", "tab8"),
             ("Table IX caption", "tab9"), ("App. C", 110), ("App. D", 112), ("App. E", 114)]
    for label, key in order:
        print(f"**{label}**\n")
        print("> " + T_[key] + "\n")
    print("**New references [23]–[27]**\n")
    for k, r in enumerate(bp.NEW_REFS, start=23):
        print(f"* [{k}] {r}")

(ROOT / "paper_v2/output/report_generated.md").write_text(out.getvalue(), encoding="utf-8")
print("wrote report_generated.md,", out.getvalue().count("\n"), "lines")
