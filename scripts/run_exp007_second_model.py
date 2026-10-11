"""EXP-007: a second answering model (Gemini 3.1 Flash-Lite, free tier) on the same prompts.

Answers EN-MATCH, CS-LAT and MIXED (default; add NATIVE/ROMAN with --conditions) at 128 and 1,024 output
tokens (--budgets), with the same system prompt as EXP-002..006, temperature 0, top_p 1, and thinking
disabled (thinking_budget = 0) so that the whole budget goes to the visible answer.  The answers are
graded by the SAME two judges as before (J-QWEN = qwen/qwen3.8-27b, J-OSS = openai/gpt-oss-120b on Groq,
EXP-004 settings).  Gemini is a third model family, so neither judge is grading its own family's output.

Cost: Gemini answers are free (free-tier key; rate-limited, so the run is slow and resumable across
days).  Judging uses Groq and costs money; see --dry-run.

Usage:
  python scripts/run_exp007_second_model.py --dry-run                 # estimate only, no API calls
  python scripts/run_exp007_second_model.py --stage gen [--limit 5]   # Gemini answers (free)
  python scripts/run_exp007_second_model.py --stage judge             # Groq judges (paid)
Outputs, finish reasons, failures and a spend log: results/EXP-007-second-model/.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
OUT = ROOT / "results" / "EXP-007-second-model"
GEN_FILE = OUT / "gemini_predictions.jsonl"
JUDGE_FILE = OUT / "judgements.jsonl"
SPEND_FILE = OUT / "spend_log.jsonl"
FAIL_FILE = OUT / "failures.jsonl"
ANSWER_MODEL = "gemini-3.1-flash-lite"   # gemini-2.5-* is closed to new API keys (checked 2026-10-11)
SYSTEM_PROMPT = ("You are a helpful assistant answering questions from Indian users. "
                 "Questions may mix an Indian language with English. "
                 "Answer factually, accurately, and concisely.")
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
JUDGES = {"J-QWEN": {"model": "qwen/qwen3.8-27b", "max_tokens": 256, "extra": {}},
          "J-OSS": {"model": "openai/gpt-oss-120b", "max_tokens": 1024, "extra": {"reasoning_effort": "low"}}}
PRICES = {"qwen/qwen3.8-27b": (0.80, 4.00), "openai/gpt-oss-120b": (0.15, 0.60)}  # Groq list, 2026-10-10
ALL_CONDITIONS = {"EN-MATCH": "A_EN_MATCHED", "CS-LAT": "D_CS", "MIXED": "E_MIXED_SCRIPT",
                  "NATIVE": "B_NATIVE", "ROMAN": "C_ROMAN"}
lock = threading.Lock()


def jl(p: Path):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if p.exists() else []


def prompts(conditions):
    rows = jl(ROOT / "results/EXP-002/full_predictions.jsonl") + jl(ROOT / "results/EXP-003-matched-en/matched_predictions.jsonl")
    want = {ALL_CONDITIONS[c] for c in conditions}
    seen, out = set(), []
    for r in rows:
        if r["model"] == "qwen/qwen3.8-27b" and r["partition"] == "TEST-OOD" and r["condition"] in want and r["prompt_id"] not in seen:
            seen.add(r["prompt_id"])
            out.append(r)
    return out


def log_fail(item, err):
    with lock, open(FAIL_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps({"item": item, "error": repr(err)[:400],
                            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()}) + "\n")


def stage_gen(conditions, budgets, limit, sleep_s):
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    done = {(r["prompt_id"], r["max_tokens"]) for r in jl(GEN_FILE)}
    todo = [(r, b) for b in budgets for r in prompts(conditions) if (r["prompt_id"], b) not in done][: limit or None]
    print(f"gen: {len(todo)} to run ({len(done)} done)", flush=True)
    for r, b in todo:
        for attempt in range(8):
            try:
                t0 = time.time()
                resp = client.models.generate_content(
                    model=ANSWER_MODEL, contents=r["prompt_text"],
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT, temperature=0.0, top_p=1.0, max_output_tokens=b,
                        thinking_config=types.ThinkingConfig(thinking_budget=0)))
                cand = resp.candidates[0] if resp.candidates else None
                um = resp.usage_metadata
                rec = {k: r[k] for k in ["semantic_id", "prompt_id", "language", "condition", "partition",
                                         "target_entity", "prompt_text", "reference_answer"]}
                rec.update({"experiment_id": "EXP-007", "model": ANSWER_MODEL, "max_tokens": b,
                            "temperature": 0.0, "top_p": 1.0, "thinking_budget": 0,
                            "model_response": (resp.text or "").strip(),
                            "finish_reason": str(cand.finish_reason) if cand else "NO_CANDIDATE",
                            "prompt_tokens": getattr(um, "prompt_token_count", None),
                            "completion_tokens": getattr(um, "candidates_token_count", None),
                            "latency_ms": round((time.time() - t0) * 1000, 1),
                            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()})
                with open(GEN_FILE, "a", encoding="utf-8") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                break
            except Exception as e:
                msg = repr(e)
                print(f"  retry {attempt} {r['prompt_id']}@{b}: {msg[:140]}", flush=True)
                if "PerDay" in msg or "per day" in msg.lower():
                    print("Daily free-tier quota reached. Re-run tomorrow; finished rows are kept.", flush=True)
                    return
                time.sleep(min(90, 10 * (2 ** attempt)))
        else:
            log_fail(f"{r['prompt_id']}@{b}", "persistent failure")
        time.sleep(sleep_s)
    print("gen done", flush=True)


def stage_judge(max_usd):
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1", timeout=90.0, max_retries=0)
    spent = {"usd": sum(json.loads(l)["usd"] for l in open(SPEND_FILE)) if SPEND_FILE.exists() else 0.0}
    done = {(j["prompt_id"], j["max_tokens"], j["judge"]) for j in jl(JUDGE_FILE)}
    todo = [(r, jn) for r in jl(GEN_FILE) for jn in JUDGES if (r["prompt_id"], r["max_tokens"], jn) not in done]
    print(f"judge: {len(todo)} to run; prior spend ${spent['usd']:.3f}; ceiling ${max_usd}", flush=True)

    def work(t):
        r, jn = t
        cfg = JUDGES[jn]
        if spent["usd"] > max_usd:
            raise RuntimeError("budget ceiling reached")
        user = JUDGE_PROMPT.format(question=r["prompt_text"], gold=r["reference_answer"], answer=r["model_response"])
        for attempt in range(10):
            try:
                res = client.chat.completions.create(model=cfg["model"], temperature=0.0, top_p=1.0, max_tokens=cfg["max_tokens"],
                                                     messages=[{"role": "system", "content": JUDGE_SYSTEM},
                                                               {"role": "user", "content": user}], **cfg["extra"])
                break
            except Exception as e:
                print(f"  retry {attempt} {cfg['model']}: {repr(e)[:120]}", flush=True)
                time.sleep(min(60, 3 * (2 ** attempt)))
        else:
            log_fail(f"{r['prompt_id']}@{r['max_tokens']}|{jn}", "persistent failure")
            return
        u = res.usage
        usd = (u.prompt_tokens * PRICES[cfg["model"]][0] + u.completion_tokens * PRICES[cfg["model"]][1]) / 1e6
        raw = res.choices[0].message.content or ""
        m = VERDICT_RE.search(raw)
        rec = {"prompt_id": r["prompt_id"], "semantic_id": r["semantic_id"], "condition": r["condition"],
               "language": r["language"], "target_entity": r["target_entity"], "max_tokens": r["max_tokens"],
               "judge": jn, "judge_model": cfg["model"],
               "judge_label": (0 if m.group(1).upper() == "CORRECT" else 1) if m else -1, "raw": raw[:400],
               "finish_reason": res.choices[0].finish_reason,
               "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()}
        with lock:
            spent["usd"] += usd
            with open(SPEND_FILE, "a") as f:
                f.write(json.dumps({"model": cfg["model"], "in": u.prompt_tokens, "out": u.completion_tokens, "usd": usd}) + "\n")
            with open(JUDGE_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def safe(t):
        try:
            work(t)
        except Exception as e:  # logged; re-run the stage to retry
            log_fail(f"{t[0]['prompt_id']}@{t[0]['max_tokens']}|{t[1]}", e)

    with ThreadPoolExecutor(3) as ex:
        list(ex.map(safe, todo))
    print(f"judge done; spend ${spent['usd']:.3f}", flush=True)


def dry_run(conditions, budgets):
    n = len(prompts(conditions)) * len(budgets)
    worst = 0.0
    for b in budgets:
        k = len(prompts(conditions))
        worst += k * ((400 + b) * 0.80 + 30 * 4.00) / 1e6          # J-QWEN
        worst += k * ((450 + b) * 0.15 + 300 * 0.60) / 1e6         # J-OSS
    print(f"answers to generate with {ANSWER_MODEL}: {n} (free tier; about {n * 7 / 60:.0f} min at ~7 s/call)")
    print(f"judge calls on Groq: {2 * n}; worst-case cost ${worst:.2f}; likely ~${0.6 * worst:.2f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["gen", "judge"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--conditions", nargs="+", default=["EN-MATCH", "CS-LAT", "MIXED"], choices=list(ALL_CONDITIONS))
    ap.add_argument("--budgets", nargs="+", type=int, default=[128, 1024])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--model", default=ANSWER_MODEL, help="Gemini model id (fixed ids only; avoid *-latest aliases)")
    ap.add_argument("--sleep", type=float, default=6.5, help="seconds between Gemini calls (free-tier rate limit)")
    ap.add_argument("--max-usd", type=float, default=1.20, help="ceiling on EXP-007 Groq judging spend")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    ANSWER_MODEL = a.model
    if a.dry_run:
        dry_run(a.conditions, a.budgets)
    elif a.stage == "gen":
        stage_gen(a.conditions, a.budgets, a.limit, a.sleep)
    elif a.stage == "judge":
        stage_judge(a.max_usd)
    else:
        ap.error("--stage or --dry-run required")
