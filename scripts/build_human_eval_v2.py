"""Build the v2 human-validation set for the judges (all three budgets) and per-reviewer workbooks.

Sample frame: the 900 Qwen3.8-27B outputs for EN-MATCH, CS-LAT and MIXED at 128, 512 and 1,024 tokens,
each labelled by J-QWEN and J-OSS.  Within each budget x condition cell (9 cells) we stratify by the
judge-agreement pattern and draw up to 8 items per pattern group:
    both-correct (QC_OC), both-wrong (QW_OW), disagreement (QC_OW + QW_OC, rarer pattern drawn first)
-> at most 216 items.  Inverse sampling weights (stratum size / sampled) are stored in the key so the
analysis can estimate cell accuracy and judge error rates for the whole frame.

Each item is assigned to two reviewers where two readers of its language exist (see READERS); reviewers
see only item_id, language, question, gold answer and model answer (no condition, budget, judge labels).

Outputs (results/human_eval_v2/):
    key_v2.csv                      item -> prompt, condition, budget, language, judge labels, weights
    assignments_v2.csv              item -> reviewer
    to_annotate/<Reviewer>.xlsx     one workbook per reviewer (Instructions + Items sheets)
No API calls.  Seed fixed for reproducibility.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "human_eval_v2"
SEED = 20261011
PER_GROUP = 8
LABELS = ["CORRECT", "PARTIAL", "INCOMPLETE_NO_ERROR", "INCORRECT", "CORRECT_OTHER_READING", "UNREADABLE"]
COND = {"A_EN_MATCHED": "EN-MATCH", "D_CS": "CS-LAT", "E_MIXED_SCRIPT": "MIXED"}

# Who can read what.  EDIT THIS before running if it is wrong.  Placeholders (TBD_*) mark languages that
# still need a second reader; their items are assigned to one real reviewer plus the placeholder.
READERS = {
    "en": ["Chandrahas", "Akshith"],   # EN-MATCH answers are in English
    "te": ["Chandrahas", "Akshith"],
    "hi": ["Akshith", "Chandrahas"],
    "ta": ["Kapilan", "Chandrahas"],
    "kn": ["Akshith", "TBD_second_Kannada_reader"],
    "bn": ["Shamik", "TBD_second_Bengali_reader"],
}

INSTRUCTIONS = [
    ("What you are doing", "For each row, decide whether the MODEL ANSWER correctly answers the QUESTION, "
     "using the GOLD ANSWER as the reference. You are checking an AI system's answers; the gold answers "
     "have already been verified."),
    ("Do not look anything up", "Judge only against the gold answer. If you think the gold answer itself is "
     "wrong or outdated, still label the answer against the gold, and put Y in 'gold_problem' with a note."),
    ("Answers are cut off", "Many answers stop mid-sentence because of a length limit. A cut-off is NOT an "
     "error by itself. Judge only what the answer actually says."),
    ("Language", "Questions and answers may be in English, an Indian language, Romanized text, or a mix. "
     "Only label rows in languages you read well; otherwise choose UNREADABLE."),
    ("CORRECT", "States the gold fact (paraphrase/translation/transliteration is fine) and says nothing that "
     "contradicts it."),
    ("PARTIAL", "States part of the gold fact (e.g. one of two contrasted properties, one of three "
     "thresholds) and nothing that contradicts it."),
    ("INCOMPLETE_NO_ERROR", "Never reaches the gold fact (generic or cut off before it) but makes no false "
     "statement about the asked fact."),
    ("INCORRECT", "Says something that contradicts the gold fact, or a false fact central to the question "
     "(wrong number, wrong date, wrong expansion of a scheme name, etc.)."),
    ("CORRECT_OTHER_READING", "Wrong against the gold, but correct for a different reasonable reading of the "
     "(generic) question, e.g. the Rs 20 lakh GST threshold for services when the gold is Rs 40 lakh for goods."),
    ("UNREADABLE", "You cannot assess it (language you do not read, garbled text)."),
    ("Independence", "Work alone. Do not discuss items with the other reviewer until everyone has finished. "
     "Do not change labels after seeing anyone else's."),
    ("Time", "About 1-2 minutes per item. Take breaks. Save often."),
    ("When done", "Save the file with the same name and return it. Fill in the 'Reviewer' sheet once."),
]


def jl(p):
    return [json.loads(l) for l in open(ROOT / p, encoding="utf-8") if l.strip()]


def load_frame() -> pd.DataFrame:
    orig = pd.DataFrame(jl("results/EXP-002/full_predictions.jsonl") + jl("results/EXP-003-matched-en/matched_predictions.jsonl"))
    orig = orig[(orig.model == "qwen/qwen3.8-27b") & (orig.partition == "TEST-OOD") & orig.condition.isin(COND)]
    resp = {"128": orig, "512": pd.DataFrame(jl("results/EXP-004-budget-rejudge/gen512_predictions.jsonl")),
            "1024": pd.DataFrame(jl("results/EXP-005-budget1024/gen1024_predictions.jsonl"))}
    J = pd.DataFrame(jl("results/EXP-004-budget-rejudge/judgements.jsonl") + jl("results/EXP-005-budget1024/judgements.jsonl"))
    J["budget"] = J.source.map({"orig128": "128", "gen512": "512", "gen1024": "1024"})
    J["correct"] = (J.judge_label == 0).astype(int)
    lab = J.pivot_table(index=["budget", "prompt_id"], columns="judge", values="correct", aggfunc="first").reset_index()
    frames = []
    for b, r in resp.items():
        f = r[["prompt_id", "semantic_id", "condition", "language", "target_entity", "prompt_text",
               "reference_answer", "model_response"]].copy()
        f["budget"] = b
        frames.append(f.merge(lab[lab.budget == b].drop(columns="budget"), on="prompt_id"))
    df = pd.concat(frames, ignore_index=True)
    df["pattern"] = np.select([(df["J-QWEN"] == 1) & (df["J-OSS"] == 1), (df["J-QWEN"] == 0) & (df["J-OSS"] == 0),
                               (df["J-QWEN"] == 1) & (df["J-OSS"] == 0)], ["QC_OC", "QW_OW", "QC_OW"], "QW_OC")
    return df


def draw(group: pd.DataFrame, n: int, rng) -> list:
    """Language-balanced draw: round-robin over languages in random order."""
    by_lang = {l: list(rng.permutation(g.index)) for l, g in group.groupby("language")}
    order = list(rng.permutation(sorted(by_lang)))
    picked = []
    while len(picked) < n and any(by_lang.values()):
        for l in order:
            if by_lang[l] and len(picked) < n:
                picked.append(by_lang[l].pop())
    return picked


def main():
    rng = np.random.default_rng(SEED)
    df = load_frame()
    rows = []
    for (b, c), cell in df.groupby(["budget", "condition"]):
        for grp, pats in [("agree_correct", ["QC_OC"]), ("agree_wrong", ["QW_OW"]), ("disagree", ["QW_OC", "QC_OW"])]:
            budget_left = PER_GROUP
            for pat in pats:          # rarer disagreement pattern first
                s = cell[cell.pattern == pat]
                take = draw(s, min(budget_left, len(s)), rng)
                for i in take:
                    rows.append((i, pat, len(s), len(take)))
                budget_left -= len(take)
    key = df.loc[[r[0] for r in rows]].copy()
    key["stratum"] = [r[1] for r in rows]
    key["stratum_size"] = [r[2] for r in rows]
    key["stratum_sampled"] = [r[3] for r in rows]
    key["weight"] = key.stratum_size / key.stratum_sampled
    key = key.sample(frac=1, random_state=SEED).reset_index(drop=True)
    key["item_id"] = [f"V{k:03d}" for k in range(1, len(key) + 1)]
    key["condition"] = key.condition.map(COND)
    key["reader_language"] = np.where(key.condition == "EN-MATCH", "en", key.language)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "to_annotate").mkdir(exist_ok=True)
    cols = ["item_id", "prompt_id", "semantic_id", "budget", "condition", "language", "reader_language",
            "target_entity", "stratum", "stratum_size", "stratum_sampled", "weight", "J-QWEN", "J-OSS"]
    key[cols].to_csv(OUT / "key_v2.csv", index=False, encoding="utf-8-sig")

    assign = [(r.item_id, rev) for r in key.itertuples() for rev in READERS[r.reader_language]]
    pd.DataFrame(assign, columns=["item_id", "reviewer"]).to_csv(OUT / "assignments_v2.csv", index=False)

    by_rev = {}
    for item, rev in assign:
        by_rev.setdefault(rev, []).append(item)
    items = key.set_index("item_id")
    for rev, ids in by_rev.items():
        wb = Workbook()
        ws = wb.active
        ws.title = "Instructions"
        ws.column_dimensions["A"].width = 26
        ws.column_dimensions["B"].width = 110
        ws.append(["IndraLLM answer-checking task", f"Reviewer: {rev} — {len(ids)} items"])
        ws["A1"].font = Font(bold=True, size=13)
        for k, v in INSTRUCTIONS:
            ws.append([k, v])
        for row in ws.iter_rows(min_row=2):
            row[0].font = Font(bold=True)
            row[1].alignment = Alignment(wrap_text=True, vertical="top")
        it = wb.create_sheet("Items")
        head = ["item_id", "language", "question", "gold_answer", "model_answer", "label", "gold_problem (Y/N)", "note"]
        it.append(head)
        for cell in it[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill("solid", fgColor="DDEBF7")
        for i in rng.permutation(ids):      # per-reviewer random order
            r = items.loc[i]
            it.append([i, r.reader_language, r.prompt_text, r.reference_answer, r.model_response, "", "", ""])
        widths = {"A": 9, "B": 9, "C": 40, "D": 34, "E": 90, "F": 24, "G": 12, "H": 30}
        for col, w in widths.items():
            it.column_dimensions[col].width = w
        for row in it.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
        n = len(ids) + 1
        dv = DataValidation(type="list", formula1='"' + ",".join(LABELS) + '"', allow_blank=True)
        dv.add(f"F2:F{n}")
        it.add_data_validation(dv)
        dv2 = DataValidation(type="list", formula1='"Y,N"', allow_blank=True)
        dv2.add(f"G2:G{n}")
        it.add_data_validation(dv2)
        it.freeze_panes = "A2"
        rv = wb.create_sheet("Reviewer")
        rv.append(["reviewer_name", rev])
        rv.append(["languages_read_well", ""])
        rv.append(["background (e.g. student, field)", ""])
        rv.append(["date_completed", ""])
        rv.append(["paid? (Y/N)", ""])
        rv.append(["ok to be thanked by name in the paper? (Y/N)", ""])
        rv.column_dimensions["A"].width = 45
        rv.column_dimensions["B"].width = 40
        wb.save(OUT / "to_annotate" / f"{rev}.xlsx")

    summary = key.groupby(["budget", "condition", "stratum"]).size().unstack(fill_value=0)
    print(summary)
    print("items:", len(key), "| labels to collect:", len(assign))
    print({rev: len(ids) for rev, ids in by_rev.items()})


if __name__ == "__main__":
    main()
