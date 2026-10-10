"""Assemble paper_v2/NEXT_SESSION_PROMPT_FULL.md.

Part A: paper_v2/NEXT_SESSION_PROMPT.md (handoff rules and task).
Part B: paper_v2/handoff_extra.md (detailed build specification).
Part C: generated from repository files: prompt templates (from the protocol), the gold ledger
        (from the CSV), the file inventory (from git), and every results table plus the final
        manuscript text (paper_v2/output/report_generated.md).
"""

import csv
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def section(text: str, start: str, end: str) -> str:
    i = text.index(start)
    j = text.index(end, i + len(start))
    return text[i:j].strip()


parts = []
parts.append((ROOT / "paper_v2/NEXT_SESSION_PROMPT.md").read_text(encoding="utf-8").replace(
    "# Handoff: build the IndraLLM paper", "# PART A — Handoff: build the IndraLLM paper", 1))
parts.append((ROOT / "paper_v2/handoff_extra.md").read_text(encoding="utf-8"))

proto = (ROOT / "research/PROMPT_VALIDATION_PROTOCOL.md").read_text(encoding="utf-8")
parts.append("## C1. Prompt templates, findings and fluent-speaker review record (from research/PROMPT_VALIDATION_PROTOCOL.md)\n")
parts.append(section(proto, "## 0. Fluent-speaker review record", "## 3. Consequences").replace("## ", "### "))

rows = list(csv.DictReader(open(ROOT / "research/gold_verification_ledger.csv", encoding="utf-8")))
lines = ["\n## C2. Gold-answer ledger (from research/gold_verification_ledger.csv)\n",
         "| Topic | Gold answer | Provision | Factual status | Completeness | Currency / notes |",
         "|---|---|---|---|---|---|"]
for r in rows:
    note = "; ".join(x for x in [r["currency_note"], r["notes"]] if x)
    lines.append(f"| {r['topic']} | {r['gold_answer']} | {r['governing_provision_or_authority']} | "
                 f"{r['factual_status']} | {r['completeness_for_generic_question']} | {note} |")
lines.append(f"\nAuthor verification record (all rows): {rows[0]['author_verification_record']}.\n")
parts.append("\n".join(lines))

files = subprocess.check_output(["git", "ls-files", "paper_v2", "research/gold_verification_ledger.csv",
                                 "research/HUMAN_EVAL_PROTOCOL.md", "research/PROMPT_VALIDATION_PROTOCOL.md",
                                 "results/EXP-004-budget-rejudge", "results/EXP-005-budget1024",
                                 "scripts/run_exp004_budget_rejudge.py", "scripts/run_exp005_budget1024.py",
                                 "scripts/build_human_eval_sample.py"], cwd=ROOT, text=True).split()
inv = ["\n## C3. File inventory (tracked files produced or used in the revision)\n", "| File | Size (KB) |", "|---|---|"]
for f in files:
    p = ROOT / f
    if p.exists():
        inv.append(f"| `{f}` | {p.stat().st_size / 1024:.1f} |")
parts.append("\n".join(inv))

gen = (ROOT / "paper_v2/output/report_generated.md").read_text(encoding="utf-8")
parts.append("\n## C4. All results tables and the final manuscript text (from report_generated.md)\n\n"
             + ("\n" + gen).replace("\n### ", "\n#### ").replace("\n## G", "\n### G"))

out = ROOT / "paper_v2/NEXT_SESSION_PROMPT_FULL.md"
text = "\n\n".join(parts) + "\n"
out.write_text(text, encoding="utf-8")
print("wrote", out, text.count("\n"), "lines")
