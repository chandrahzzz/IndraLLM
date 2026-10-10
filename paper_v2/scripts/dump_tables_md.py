"""Print every manuscript table as Markdown, straight from the result JSON files."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_revised_docx import L6, NE, NJ, NO, PROVISION, fp, sgn  # noqa: E402


def row(*a):
    print("| " + " | ".join(str(x) for x in a) + " |")


def sep(n):
    row(*["---"] * n)


def by(N, c, r):
    return next(x for x in N["contrasts"] if x["cmp"] == c and x["ref"] == r)


print("### T2")
row("Condition", "Acc. % (k/100)", "Wilson 95% CI", "Topic-bootstrap CI", "Δ vs EN-MATCH", "Exact p", "Holm p",
    "Topic p (Holm)", "Stored labels", "J-OSS")
sep(10)
for c in L6:
    a = NJ["accuracy"][c]
    st = NO["accuracy"][c]["k"]
    oss = NE["orig128"]["J-OSS"]["accuracy"][c]
    w = f"[{a['wilson'][0]:.1f}, {a['wilson'][1]:.1f}]"
    b = f"[{a['topic_boot_ci'][0]:.0f}, {a['topic_boot_ci'][1]:.0f}]"
    if c == "EN-MATCH":
        row(c, f"{a['k']} (60/100)", w, b, "ref.", "–", "–", "–", st, f"{oss:.0f}")
    elif c == "EN-ORIG":
        x = by(NJ, "EN-MATCH", "EN-ORIG")
        row(c, f"{a['k']} ({a['k']}/100)", w, b, "+10 †", fp(x["p_exact"]), "–", fp(x["topic_perm_p"]), st, f"{oss:.0f}")
    else:
        x = by(NJ, c, "EN-MATCH")
        row(c, f"{a['k']} ({a['k']}/100)", w, b, sgn(a["k"] - 60), fp(x["p_exact"]), fp(x["holm_exact"]),
            f"{fp(x['topic_perm_p'])} ({fp(x['holm_topic'])})", st, f"{oss:.0f}")

print("### T3")
row("Contrast", "Clustering unit", "β̂", "Robust SE", "p")
sep(5)
units = [("prompt", "prompt"), ("proposition", "proposition (100)"), ("topic", "topic (20)")]
for c in ["CS-LAT", "ROMAN", "NATIVE", "MIXED"]:
    for u, l in units:
        g = NJ["gee"][c][u]
        row(f"{c} vs EN-MATCH" if u == "prompt" else "", "prompt (500)" if u == "prompt" else l,
            f"{g['beta']:.3f}", f"{g['se_robust']:.3f}", fp(g["p"]))
for u, l in units:
    g = NJ["gee"]["MIXED_vs_CS-LAT"][u]
    row("MIXED vs CS-LAT" if u == "prompt" else "", "prompt (200)" if u == "prompt" else l,
        f"{g['beta']:.3f}", f"{g['se_robust']:.3f}", fp(g["p"]))

print("### T5")
row("Condition", "Stored vs J-QWEN (share identical)", "J-QWEN vs J-OSS (share identical)", "Cohen κ (J-QWEN, J-OSS)")
sep(4)
for c in L6:
    A = NE["agreement_orig128"][c]
    row(c, f"{A['stored_vs_jqwen']:.2f}", f"{A['jqwen_vs_joss']:.2f}", f"{A['kappa_jqwen_joss']:.2f}")

print("### T6")
row("FPR", "CS-LAT vs EN-MATCH", "MIXED vs EN-MATCH", "MIXED vs CS-LAT")
sep(4)
for f in ["0.00", "0.04", "0.08", "0.12", "0.16"]:
    row(f, *[f"{NJ['tipping'][k][f]:.2f}" for k in ["CS-LAT_vs_EN-MATCH", "MIXED_vs_EN-MATCH", "MIXED_vs_CS-LAT"]])

print("### T8")
row("Topic", "Provision reviewed", "Gold status", *L6)
sep(9)
for t in sorted(NJ["by_topic"], key=lambda t: (-NJ["by_topic"][t]["EN-MATCH"], -NJ["by_topic"][t]["EN-ORIG"], t)):
    row(t, PROVISION[t][0], PROVISION[t][1], *[NJ["by_topic"][t][c] for c in L6])

print("### T9")
row("Contrast (comparison vs reference)", "Δ (pp)", "b", "c", "Exact p", "Topic p", "Topic 95% CI (pp)")
sep(7)
for c, r in [("CS-LAT", "EN-MATCH"), ("ROMAN", "EN-MATCH"), ("NATIVE", "EN-MATCH"), ("MIXED", "EN-MATCH"),
             ("MIXED", "CS-LAT"), ("EN-MATCH", "EN-ORIG"), ("MIXED", "ROMAN"), ("MIXED", "NATIVE"),
             ("ROMAN", "CS-LAT"), ("NATIVE", "CS-LAT"), ("NATIVE", "ROMAN")]:
    x = by(NJ, c, r)
    lo, hi = x["topic_boot_ci_pp"]
    row(f"{c} vs {r}", sgn(x["delta_pp"]), x["b"], x["c"], fp(x["p_exact"]), fp(x["topic_perm_p"]), f"[{lo:.0f}, {hi:.0f}]")

print("### T10")
row("Language", *L6)
sep(7)
for n, k in [("Hindi", "hi"), ("Bengali", "bn"), ("Tamil", "ta"), ("Telugu", "te"), ("Kannada", "kn")]:
    row(n, *[f"{NJ['by_language'][k][c]:.0f}" for c in L6])
row("All", *[NJ["accuracy"][c]["k"] for c in L6])

print("### T11")
row("Condition", "Qwen stored", "Qwen J-QWEN", "ALLaM-2-7B (stored)", "ALLaM Wilson 95% CI")
sep(5)
for c in L6:
    w = NO["allam"][c]["wilson"]
    row(c, NO["accuracy"][c]["k"], NJ["accuracy"][c]["k"], NO["allam"][c]["k"], f"[{w[0]:.1f}, {w[1]:.1f}]")

print("### T12")
row("Condition", "Script transitions/prompt", "Prompt chars/token (Qwen3.8)", "Prompt chars/token (old, Qwen2.5)",
    "Mean response chars", "Mostly Brahmic %", "Ends mid-sentence (of 100)", "Errors (J-QWEN)", "Incomplete rule (J-QWEN)")
sep(9)
R, T = NJ["response"], NJ["tokenizer_check"]
for c in L6:
    row(c, f"{R[c]['prompt_script_transitions']:.1f}", f"{T['Qwen3.8-27B']['cpt_by_condition'][c]:.2f}",
        f"{T['Qwen2.5-7B']['cpt_by_condition'][c]:.2f}", f"{R[c]['mean_chars']:.0f}", f"{R[c]['brahmic_majority_pct']:.0f}",
        R[c]["ends_mid_sentence"], R[c]["errors"], R[c]["incomplete_rule"])

for name, rows in [("STORED primary", NO["contrasts"][:5]), ("J-OSS primary", NE["orig128"]["J-OSS"]["primary"])]:
    print("###", name)
    row("Contrast", "Δ", "b", "c", "Exact p", "Holm", "Topic p", "Holm topic")
    sep(8)
    for x in rows:
        row(f"{x['cmp']} vs {x['ref']}", sgn(x["delta_pp"]), x["b"], x["c"], fp(x["p_exact"]), fp(x["holm_exact"]),
            fp(x["topic_perm_p"]), fp(x["holm_topic"]))

print("### budget raw")
for j in ["J-QWEN", "J-OSS"]:
    B = NE["budget"][j]
    for k, v in B["within_condition"].items():
        print(j, "within", k, B["accuracy"][k], "b", v["b"], "c", v["c"], "p", fp(v["p_exact"]),
              "topic", fp(v["topic_perm_p"]), "CI", v["topic_boot_ci"])
    for bud in ["128", "512"]:
        for x in B["contrasts_" + bud]:
            print(j, bud, x["cmp"], "vs", x["ref"], sgn(x["delta_pp"]), x["b"], x["c"], fp(x["p_exact"]),
                  fp(x["topic_perm_p"]), [round(v) for v in x["topic_boot_ci"]])
    for k, v in B["gap_change"].items():
        print(j, "gapchange", k, v["gap128"], v["gap512"], v["change"], [round(z) for z in v["topic_boot_ci"]],
              fp(v["topic_perm_p"]))
print(NE["gen512_descriptives"])
print(NE["mixed512_vs_en128"])
print(NE["spend_usd"])
print(NE["tokens"])
