"""EXP-003: Matched English Inference and Evaluation Runner.

Executes:
1. Qwen-2.5-27B (qwen/qwen3.8-27b) and Allam-2-7B (allam-2-7b) on 100 matched English prompts.
2. Identical inference parameters as EXP-002: greedy decoding (T=0.0), top_p=1.0, max_tokens=128, exact system prompt.
3. Identical judge setup as EXP-002: qwen/qwen3.8-27b, exact rubric, T=0.0, max_tokens=256.
4. Saves rows to results/EXP-003-matched-en/matched_predictions.jsonl in exact full_predictions.jsonl schema.
5. Logs cost in append-only fashion via indrallm.utils.budget_guard.
"""

from __future__ import annotations

import datetime
import json
import math
import os
import subprocess
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
from scipy import stats
from tqdm import tqdm

from indrallm.annotation.llm_judge_label import _VERDICT_RE
from indrallm.collection.cmi import compute_cmi
from indrallm.config import PROJECT_ROOT
from indrallm.experiments.run_exp002 import REFUSAL_TRIGGERS, detect_refusal
from indrallm.utils.budget_guard import (
    assert_budget_approved,
    estimate_cost,
    record_spend,
)

load_dotenv(PROJECT_ROOT / ".env")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found in environment or .env")

OUT_DIR = PROJECT_ROOT / "results" / "EXP-003-matched-en"
OUT_DIR.mkdir(parents=True, exist_ok=True)
PROMPTS_FILE = OUT_DIR / "matched_prompts_100.jsonl"
PREDICTIONS_FILE = OUT_DIR / "matched_predictions.jsonl"

SYSTEM_PROMPT = (
    "You are a helpful assistant answering questions from Indian users. "
    "Questions may mix an Indian language with English. "
    "Answer factually, accurately, and concisely."
)

JUDGE_PROMPT_TEMPLATE = """You are grading whether a model's ANSWER to a user QUESTION is factually correct.
You are given a trusted GOLD answer. The answer may mix an Indian language with English
(code-switching) and may be phrased very differently from the gold — that is fine.
Judge ONLY factual correctness and whether it actually addresses the question.

Reply on a single line in exactly this format:
VERDICT: <CORRECT or HALLUCINATED> | REASON: <max 12 words>

QUESTION: {question}
GOLD ANSWER: {gold}
MODEL ANSWER: {answer}"""


def get_git_commit() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(PROJECT_ROOT))
        return out.decode().strip()
    except Exception:
        return "unknown_commit"


def wilson_ci(k: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    z = 1.959964  # exact standard normal quantile for 95% CI
    p = k / n
    denominator = 1.0 + z**2 / n
    centre_adjusted_probability = p + z**2 / (2.0 * n)
    adjusted_limits = z * math.sqrt((p * (1.0 - p) + z**2 / (4.0 * n)) / n)
    lower = max(0.0, (centre_adjusted_probability - adjusted_limits) / denominator)
    upper = min(1.0, (centre_adjusted_probability + adjusted_limits) / denominator)
    return round(lower * 100, 1), round(upper * 100, 1)


def execute_call(
    client: OpenAI,
    model: str,
    prompt: str,
    max_tokens: int = 128,
    temperature: float = 0.0,
    system_prompt: str = SYSTEM_PROMPT,
    max_retries: int = 4,
) -> tuple[str, float, int, int]:
    last_err = None
    for attempt in range(max_retries):
        try:
            t0 = time.time()
            resp = client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=1.0,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
            )
            lat = (time.time() - t0) * 1000.0
            text = resp.choices[0].message.content or ""
            if not text and hasattr(resp.choices[0].message, "reasoning"):
                text = getattr(resp.choices[0].message, "reasoning", "") or ""
            p_tok = resp.usage.prompt_tokens if (hasattr(resp, "usage") and resp.usage) else len(prompt.split()) * 2
            c_tok = resp.usage.completion_tokens if (hasattr(resp, "usage") and resp.usage) else len(text.split()) * 2
            return text.strip(), lat, p_tok, c_tok
        except Exception as e:
            last_err = e
            time.sleep(1.5 * (2**attempt))
    raise RuntimeError(f"API call persistently failed for model {model}: {last_err}")


def judge_response(
    client: OpenAI,
    judge_model: str,
    question: str,
    gold: str,
    answer: str,
) -> tuple[int, str, int, int]:
    prompt = JUDGE_PROMPT_TEMPLATE.format(question=question, gold=gold, answer=answer)
    raw, lat, p_tok, c_tok = execute_call(
        client=client,
        model=judge_model,
        prompt=prompt,
        max_tokens=256,
        temperature=0.0,
        system_prompt="You are an expert factuality evaluator.",
    )
    m = _VERDICT_RE.search(raw or "")
    if not m:
        # fallback parsing
        if "CORRECT" in (raw or "").upper() and "HALLUCINATED" not in (raw or "").upper():
            return 0, raw[:120], p_tok, c_tok
        return 1, (raw or "").strip()[:120], p_tok, c_tok
    label = 0 if m.group(1).upper() == "CORRECT" else 1
    reason = raw.split("REASON:", 1)[1].strip()[:120] if "REASON:" in raw else raw[:120]
    return label, reason, p_tok, c_tok


def main():
    print("=== EXP-003: RUNNING MATCHED ENGLISH INFERENCE & EVALUATION ===")
    git_hash = get_git_commit()
    print(f"Git commit: {git_hash}")

    # Load 100 matched prompts
    prompts = []
    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            prompts.append(json.loads(line))
    print(f"Loaded {len(prompts)} matched prompts.")

    models = ["qwen/qwen3.8-27b", "allam-2-7b"]
    judge_model = "qwen/qwen3.8-27b"
    total_calls = len(prompts) * len(models) * 2  # generation + judge

    # Check budget
    est = estimate_cost(
        experiment_id="EXP-003",
        provider="groq",
        model="qwen/qwen3.8-27b",
        num_calls=total_calls,
        avg_input_tokens=100,
        avg_output_tokens=128,
    )
    assert_budget_approved(est)
    print(f"Budget approved. Estimated cost: ${est.estimated_cost_usd:.5f} USD (Ceiling: $10.00 USD).")

    client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

    # Load existing completed rows if any
    completed_keys = set()
    if PREDICTIONS_FILE.exists():
        with open(PREDICTIONS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    completed_keys.add((r["model"], r["prompt_id"]))
    print(f"Resumability: {len(completed_keys)} rows already completed.")

    total_cost_usd = 0.0
    total_in_tokens = 0
    total_out_tokens = 0
    records_written = 0

    with open(PREDICTIONS_FILE, "a", encoding="utf-8") as out_f:
        for model in models:
            print(f"\n--- Running Model: {model} ---")
            pbar = tqdm(prompts, desc=f"EXP-003 {model}")
            for row in pbar:
                key = (model, row["prompt_id"])
                if key in completed_keys:
                    continue

                prompt_text = row["prompt_text"]
                ref_ans = str(row["reference_answer"])

                # 1. Model Generation
                resp_text, lat_ms, in_tok, out_tok = execute_call(
                    client=client,
                    model=model,
                    prompt=prompt_text,
                    max_tokens=128,
                    temperature=0.0,
                    system_prompt=SYSTEM_PROMPT,
                )

                # Cost estimate for generation (Groq $0.08 per 1M tokens)
                call_tokens = in_tok + out_tok
                call_cost = (call_tokens / 1_000_000.0) * 0.08

                # 2. Judge evaluation
                judge_label, judge_reason, j_in_tok, j_out_tok = judge_response(
                    client=client,
                    judge_model=judge_model,
                    question=prompt_text,
                    gold=ref_ans,
                    answer=resp_text,
                )
                j_tokens = j_in_tok + j_out_tok
                j_cost = (j_tokens / 1_000_000.0) * 0.08

                refusal = detect_refusal(resp_text)
                resp_cmi_data = compute_cmi(resp_text, expected_lang=row["language"])

                row_cost = round(call_cost + j_cost, 6)
                total_cost_usd += row_cost
                total_in_tokens += in_tok + j_in_tok
                total_out_tokens += out_tok + j_out_tok

                rec = {
                    "experiment_id": "EXP-003",
                    "stage": "matched_en",
                    "model": model,
                    "git_commit": git_hash,
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "semantic_id": row["semantic_id"],
                    "prompt_id": row["prompt_id"],
                    "language": row["language"],
                    "condition": "A_EN_MATCHED",
                    "partition": row["partition"],
                    "is_authentic": True,
                    "template_family_id": "TF-MATCHED",
                    "difficulty_level": int(row["difficulty_level"]),
                    "target_entity": row["target_entity"],
                    "prompt_text": prompt_text,
                    "reference_answer": ref_ans,
                    "evidence_snippet": str(row["evidence_snippet"]),
                    "model_response": resp_text,
                    "latency_ms": round(lat_ms, 2),
                    "prompt_tokens": in_tok,
                    "completion_tokens": out_tok,
                    "total_tokens": call_tokens,
                    "cost_usd": row_cost,
                    "judge_label": judge_label,
                    "judge_reason": judge_reason,
                    "is_refusal": refusal,
                    "response_cmi": resp_cmi_data["cmi"],
                }

                out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                out_f.flush()
                completed_keys.add(key)
                records_written += 1

    # Record actual expenditure in ledger
    if total_cost_usd > 0:
        cum_spend = record_spend(
            experiment_id="EXP-003",
            provider="groq",
            model="qwen/qwen3.8-27b",
            calls=records_written * 2,
            input_tokens=total_in_tokens,
            output_tokens=total_out_tokens,
            cost_usd=total_cost_usd,
            notes="EXP-003 Matched English inference and judge evaluation",
        )
        print(f"\nRecorded spend: ${total_cost_usd:.5f} USD. Cumulative project spend: ${cum_spend:.5f} USD.")

    # Calculate and print accuracy for A_EN_MATCHED
    print("\n=======================================================")
    print("=== EXP-003 ACCURACY RESULTS (A_EN_MATCHED) ===")
    print("=======================================================")
    with open(PREDICTIONS_FILE, "r", encoding="utf-8") as f:
        all_pred = [json.loads(line) for line in f if line.strip()]

    for m in models:
        m_rows = [r for r in all_pred if r.get("model") == m and r.get("condition") == "A_EN_MATCHED"]
        k = sum(1 for r in m_rows if r.get("judge_label") == 0)
        n = len(m_rows)
        acc = (k / n * 100.0) if n > 0 else 0.0
        low, high = wilson_ci(k, n)
        print(f"Model: {m}")
        print(f"  Accuracy: {k}/{n} = {acc:.1f}%")
        print(f"  Wilson 95% CI (z=1.959964): [{low}%, {high}%]")
        print()


if __name__ == "__main__":
    main()
