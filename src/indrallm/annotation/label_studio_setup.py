"""Export (question, answer) tasks for Label Studio and import completed annotations.

Export: writes data/annotations/tasks_<lang>.json — one Label Studio JSON task file
per language, so each annotator pair imports only their language.

Import: converts a Label Studio JSON export back to a flat CSV
data/annotations/annotator_<name>.csv with columns
    qid, model, verdict, category, ground_truth, annotator

Setup:
    pip install label-studio && label-studio start
    Create project per language -> Labeling Setup -> paste label_config.xml
    -> Import tasks_<lang>.json

Usage:
    python -m indrallm.annotation.label_studio_setup --export
    python -m indrallm.annotation.label_studio_setup --import-file export.json --annotator anita
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from indrallm.config import LANGUAGES, path


def export_tasks() -> None:
    answer_files = sorted(path("answers").glob("*.csv"))
    if not answer_files:
        raise SystemExit("no answer CSVs — run generate_answers first")
    df = pd.concat([pd.read_csv(f) for f in answer_files], ignore_index=True)
    for lang in LANGUAGES:
        sub = df[df["language"] == lang]
        tasks = [{"data": {"qid": r.qid, "model": r.model, "language": r.language,
                           "question": r.question, "answer": r.answer}}
                 for r in sub.itertuples()]
        out = path("annotations") / f"tasks_{lang}.json"
        out.write_text(json.dumps(tasks, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{lang}: {len(tasks)} tasks -> {out}")


def _extract(result: list[dict], name: str) -> str:
    for item in result:
        if item.get("from_name") == name:
            val = item["value"]
            if "choices" in val:
                return val["choices"][0]
            if "text" in val:
                return " ".join(val["text"])
    return ""


def import_export(file: Path, annotator: str) -> None:
    tasks = json.loads(file.read_text(encoding="utf-8"))
    rows = []
    for t in tasks:
        data = t["data"]
        for ann in t.get("annotations", []):
            res = ann.get("result", [])
            rows.append({
                "qid": data["qid"], "model": data["model"],
                "verdict": _extract(res, "verdict"),
                "category": _extract(res, "category"),
                "ground_truth": _extract(res, "ground_truth"),
                "annotator": annotator,
            })
    out = path("annotations") / f"annotator_{annotator}.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"{len(rows)} annotations -> {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--export", action="store_true")
    ap.add_argument("--import-file", type=Path)
    ap.add_argument("--annotator", help="name for the imported annotator")
    args = ap.parse_args()

    if args.export:
        export_tasks()
    elif args.import_file:
        if not args.annotator:
            raise SystemExit("--annotator required with --import-file")
        import_export(args.import_file, args.annotator)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
