"""EXP-006: complete the answers that still hit the 1,024-token cap (residual-truncation fix).

Re-answers ONLY the EXP-005 responses whose finish_reason was "length" (EN-MATCH 5, CS-LAT 39,
MIXED 64 = 108 prompts) with max_tokens = 3,072; model, system prompt and decoding (T=0, top_p=1)
are unchanged.  The 192 responses that already finished at 1,024 tokens are reused as they are.
Both judges (J-QWEN, J-OSS; EXP-004 settings) grade the new outputs, so the analysis can compare
EN-MATCH / CS-LAT / MIXED on a set where (nearly) every answer is complete.

Usage:
  python scripts/run_exp006_complete_answers.py --dry-run          # cost estimate only, no API calls
  python scripts/run_exp006_complete_answers.py --stage gen
  python scripts/run_exp006_complete_answers.py --stage judge
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
OUT = ROOT / "results" / "EXP-006-complete"
MAX_TOKENS = 3072
OUT.mkdir(parents=True, exist_ok=True)
GEN_FILE = OUT / "gen3072_predictions.jsonl"
SRC_1024 = ROOT / "results" / "EXP-005-budget1024" / "gen1024_predictions.jsonl"
FAIL_FILE = OUT / "failures.jsonl"
JUDGE_FILE = OUT / "judgements.jsonl"
SPEND_FILE = OUT / "spend_log.jsonl"

GEN_MODEL = "qwen/qwen3.8-27b"
PRICES = {  # USD per 1M tokens (input, output), Groq console 2026-10-10
    "qwen/qwen3.8-27b": (0.80, 4.00),
    "openai/gpt-oss-120b": (0.15, 0.60),
}
SYSTEM_PROMPT = (
    "You are a helpful assistant answering questions from Indian users. "
    "Questions may mix an Indian language with English. "
    "Answer factually, accurately, and concisely."
)
JUDGE_SYSTEM = "You are an expert factuality evaluator."
JUDGE_PROMPT = """You are grading whether a model's ANSWER to a user QUESTION is factually correct.
You are given a trusted GOLD answer. The answer may mix an Indian language with English
(code-switching) and may be phrased very differently from the gold — that is fine.
Judge ONLY factual correctness and whether it actually addresses the question.

Reply on a single line in exactly this format:
VERDICT: <CORRECT or HALLUCINATED> | REASON: <max 12 words>

QUESTION: {question}
GOLD ANSWER: {gold}
MODEL ANSWER: {answer}"""
VERDICT_RE = re.compile(r"VERDICT:\s*\**\s*(CORRECT|HALLUCINATED)", re.I)
JUDGES = {
    "J-QWEN": {"model": "qwen/qwen3.8-27b", "max_tokens": 256, "extra": {}},
    "J-OSS": {"model": "openai/gpt-oss-120b", "max_tokens": 1024, "extra": {"reasoning_effort": "low"}},
}
GEN_CONDITIONS = ["A_EN_MATCHED", "D_CS", "E_MIXED_SCRIPT"]

client = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1", timeout=90.0, max_retries=0)
lock = threading.Lock()
spent = {"usd": 0.0}


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
    except Exception:
        return "unknown"


def prior_spend() -> float:
    if not SPEND_FILE.exists():
        return 0.0
    return sum(json.loads(l)["usd"] for l in open(SPEND_FILE, encoding="utf-8") if l.strip())


def call(model: str, system: str, user: str, max_tokens: int, extra: dict, max_usd: float) -> dict:
    if spent["usd"] > max_usd:
        raise RuntimeError(f"budget ceiling {max_usd} reached")
    last = None
    for attempt in range(10):
        try:
            t0 = time.time()
            r = client.chat.completions.create(
                model=model, temperature=0.0, top_p=1.0, max_tokens=max_tokens,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                **extra,
            )
            ch = r.choices[0]
            usage = r.usage
            pin, pout = usage.prompt_tokens, usage.completion_tokens
            usd = (pin * PRICES[model][0] + pout * PRICES[model][1]) / 1e6
            with lock:
                spent["usd"] += usd
                with open(SPEND_FILE, "a", encoding="utf-8") as f:
                    f.write(json.dumps({"model": model, "in": pin, "out": pout, "usd": usd}) + "\n")
            return {
                "content": ch.message.content or "",
                "reasoning": getattr(ch.message, "reasoning", None),
                "finish_reason": ch.finish_reason,
                "prompt_tokens": pin, "completion_tokens": pout,
                "served_model": r.model, "system_fingerprint": getattr(r, "system_fingerprint", None),
                "request_id": r.id, "latency_ms": round((time.time() - t0) * 1000, 1), "usd": usd,
            }
        except Exception as e:  # rate limits / transient errors
            last = e
            print(f"  retry {attempt} {model}: {repr(e)[:160]}", flush=True)
            time.sleep(min(60.0, 3.0 * (2 ** attempt)))
    raise RuntimeError(f"persistent failure for {model}: {last}")


def safe(fn):
    def wrapped(item):
        try:
            fn(item)
        except Exception as e:  # leave for the next resumable pass; log the failure
            print(f"  skipped: {repr(e)[:160]}", flush=True)
            key = item["prompt_id"] if isinstance(item, dict) else f"{item[1]['prompt_id']}|{item[2]}"
            with lock, open(FAIL_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps({"item": key, "error": repr(e)[:400],
                                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()}) + "\n")
    return wrapped


def load_jsonl(p: Path) -> list[dict]:
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if p.exists() else []


def original_qwen_rows() -> list[dict]:
    rows = load_jsonl(ROOT / "results/EXP-002/full_predictions.jsonl")
    rows += load_jsonl(ROOT / "results/EXP-003-matched-en/matched_predictions.jsonl")
    return [r for r in rows if r["model"] == GEN_MODEL and r["partition"] == "TEST-OOD"]


def stage_gen(limit: int | None, max_usd: float) -> None:
    src = [r for r in load_jsonl(SRC_1024) if r.get("finish_reason") == "length"]
    done = {r["prompt_id"] for r in load_jsonl(GEN_FILE)}
    todo = [r for r in src if r["prompt_id"] not in done][: limit or None]
    print(f"gen: {len(todo)} to run ({len(done)} done)")
    commit = git_commit()

    def work(r):
        res = call(GEN_MODEL, SYSTEM_PROMPT, r["prompt_text"], MAX_TOKENS, {}, max_usd)
        text = res["content"].strip() or (res["reasoning"] or "").strip()
        rec = {k: r[k] for k in ["semantic_id", "prompt_id", "language", "condition", "partition",
                                 "target_entity", "prompt_text", "reference_answer", "evidence_snippet"]}
        rec.update({"experiment_id": "EXP-006", "stage": "gen3072", "model": GEN_MODEL, "max_tokens": MAX_TOKENS,
                    "temperature": 0.0, "top_p": 1.0, "git_commit": commit,
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "model_response": text, **{k: res[k] for k in res if k not in ("content",)}})
        with lock, open(GEN_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    with ThreadPoolExecutor(3) as ex:
        list(ex.map(safe(work), todo))
    print(f"gen done; session spend ${spent['usd']:.4f}")


def stage_judge(limit: int | None, max_usd: float) -> None:
    items = [("gen3072", r) for r in load_jsonl(GEN_FILE)]
    done = {(j["source"], j["prompt_id"], j["judge"]) for j in load_jsonl(JUDGE_FILE)}
    todo = [(s, r, j) for s, r in items for j in JUDGES if (s, r["prompt_id"], j) not in done][: limit or None]
    print(f"judge: {len(todo)} to run ({len(done)} done)")

    def work(t):
        source, r, jname = t
        cfg = JUDGES[jname]
        user = JUDGE_PROMPT.format(question=r["prompt_text"], gold=r["reference_answer"], answer=r["model_response"])
        res = call(cfg["model"], JUDGE_SYSTEM, user, cfg["max_tokens"], cfg["extra"], max_usd)
        raw = res["content"] or ""
        m = VERDICT_RE.search(raw)
        label = (0 if m.group(1).upper() == "CORRECT" else 1) if m else -1
        rec = {"source": source, "prompt_id": r["prompt_id"], "semantic_id": r["semantic_id"],
               "condition": r["condition"], "language": r["language"], "target_entity": r["target_entity"],
               "judge": jname, "judge_model": cfg["model"], "judge_label": label, "raw": raw[:400],
               "finish_reason": res["finish_reason"], "prompt_tokens": res["prompt_tokens"],
               "completion_tokens": res["completion_tokens"], "served_model": res["served_model"],
               "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()}
        with lock, open(JUDGE_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    with ThreadPoolExecutor(3) as ex:
        list(ex.map(safe(work), todo))
    print(f"judge done; session spend ${spent['usd']:.4f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["gen", "judge"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--max-usd", type=float, default=1.80, help="ceiling on cumulative EXP-006 spend")
    ap.add_argument("--dry-run", action="store_true", help="print the cost estimate and exit (no API calls)")
    a = ap.parse_args()
    if a.dry_run:
        n = sum(1 for r in load_jsonl(SRC_1024) if r.get("finish_reason") == "length")
        gen_worst = n * (110 * PRICES[GEN_MODEL][0] + MAX_TOKENS * PRICES[GEN_MODEL][1]) / 1e6
        gen_likely = n * (110 * PRICES[GEN_MODEL][0] + 1800 * PRICES[GEN_MODEL][1]) / 1e6
        jq = n * ((400 + MAX_TOKENS) * 0.80 + 30 * 4.00) / 1e6
        jo = n * ((450 + MAX_TOKENS) * 0.15 + 300 * 0.60) / 1e6
        print(f"prompts to re-answer: {n}")
        print(f"generation: likely ${gen_likely:.2f}, worst ${gen_worst:.2f}")
        print(f"judging (J-QWEN + J-OSS, worst): ${jq + jo:.2f}")
        print(f"TOTAL: likely ~${gen_likely + 0.6 * (jq + jo):.2f}, worst ${gen_worst + jq + jo:.2f}")
        raise SystemExit(0)
    if not a.stage:
        ap.error("--stage is required unless --dry-run")
    spent["usd"] = prior_spend()
    print(f"prior EXP-006 spend ${spent['usd']:.4f}; ceiling ${a.max_usd}")
    {"gen": stage_gen, "judge": stage_judge}[a.stage](a.limit, a.max_usd)
