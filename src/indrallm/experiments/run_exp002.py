"""EXP-002: Main Empirical Factuality & Representation Experiment.

Executes Phase 3:
- Evaluates candidate models on decontaminated IndraLLM-CS-v1.1-CANDIDATE partitions (Test-ID & Test-OOD).
- Disaggregates by:
  - Language (hi, ta, te, bn, kn)
  - Condition (A_EN, B_NATIVE, C_ROMAN, D_CS, E_MIXED_SCRIPT)
  - Partition (Test-ID vs Test-OOD)
  - Dataset Composition (Authentic Core vs Synthetic Scaling Tier)
- Logs granular metrics: response text, latency, token counts, cost, and tri-layer factual judge verdict.
- Enforces strict Budget Guard ($10.00 USD hard ceiling).
- NO MOCK FALLBACKS ALLOWED: Any API failure is logged and retried with backoff; real outputs only.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from tqdm import tqdm

from indrallm.annotation.llm_judge_label import _judge
from indrallm.collection.cmi import compute_cmi
from indrallm.config import PROJECT_ROOT, api_key
from indrallm.generation.llm_clients import GroqClient
from indrallm.generation.response_cache import GLOBAL_CACHE
from indrallm.utils.budget_guard import (
    assert_budget_approved,
    estimate_cost,
    get_budget_status,
    record_spend,
)

CANDIDATE_DIR = PROJECT_ROOT / "data" / "questions" / "IndraLLM-CS-v1.1-CANDIDATE"
RESULTS_DIR = PROJECT_ROOT / "results" / "EXP-002"

REFUSAL_TRIGGERS = [
    "i cannot answer",
    "as an ai",
    "i do not have access",
    "i am unable to",
    "i apologize, but",
    "as a language model",
    "nenu cheppalenu",
    "ennaal mudiyathu",
    "main nahi bata sakta",
]


def detect_refusal(text: str) -> bool:
    low = (text or "").lower()
    return any(trig in low for trig in REFUSAL_TRIGGERS)


def verify_dataset_integrity() -> bool:
    manifest_p = CANDIDATE_DIR / "data_manifest.json"
    if not manifest_p.exists():
        raise FileNotFoundError(f"Manifest missing at {manifest_p}")
    with open(manifest_p, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    for fname, exp_hash in manifest.get("checksums", {}).items():
        fpath = CANDIDATE_DIR / fname
        if not fpath.exists():
            raise FileNotFoundError(f"Missing partition file {fpath}")
        with open(fpath, "rb") as fp:
            h = hashlib.sha256(fp.read()).hexdigest()
        if h != exp_hash:
            raise ValueError(f"Checksum mismatch for {fname}: expected {exp_hash}, got {h}")
    return True


def get_git_commit() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(PROJECT_ROOT))
        return out.decode().strip()
    except Exception:
        return "unknown_commit"


def execute_model_call(client: GroqClient, prompt: str, max_retries: int = 3) -> tuple[str, float, int, int]:
    """Call Groq API with retries; return (response_text, latency_ms, prompt_tokens, completion_tokens)."""
    last_err = None
    for attempt in range(max_retries):
        try:
            t0 = time.time()
            resp = client.client.chat.completions.create(
                model=client.model,
                max_tokens=128,
                temperature=0.0,  # greedy for scientific reproducibility
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant answering questions from Indian users. "
                            "Questions may mix an Indian language with English. "
                            "Answer factually, accurately, and concisely."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            lat = (time.time() - t0) * 1000.0
            text = resp.choices[0].message.content or ""
            # Handle potential reasoning trace from reasoning models
            if not text and hasattr(resp.choices[0].message, "reasoning"):
                text = getattr(resp.choices[0].message, "reasoning", "") or ""
            
            p_tok = resp.usage.prompt_tokens if hasattr(resp, "usage") and resp.usage else len(prompt.split()) * 2
            c_tok = resp.usage.completion_tokens if hasattr(resp, "usage") and resp.usage else len(text.split()) * 2
            return text.strip(), lat, p_tok, c_tok
        except Exception as e:
            last_err = e
            time.sleep(1.0 * (2 ** attempt))
    raise RuntimeError(f"API call persistently failed for model {client.model}: {last_err}")


def run_exp002_stage(
    stage: str = "smoke",
    models: list[str] | None = None,
    limit_groups: int | None = None,
) -> dict[str, Any]:
    """Execute EXP-002 stage: 'smoke', 'val_sample', or 'full'."""
    if models is None:
        models = ["qwen/qwen3.8-27b", "allam-2-7b"]

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    predictions_file = RESULTS_DIR / f"{stage}_predictions.jsonl"
    failures_file = RESULTS_DIR / f"{stage}_failures.jsonl"
    summary_file = RESULTS_DIR / f"{stage}_summary.json"

    # Checkpoint A & B
    print("=== CHECKPOINT A: Verifying Dataset Hashes ===")
    verify_dataset_integrity()
    git_hash = get_git_commit()
    print(f"Dataset integrity VERIFIED. Git commit: {git_hash}")

    # Load evaluation splits
    df_tid = pd.read_csv(CANDIDATE_DIR / "test_id.csv")
    df_tood = pd.read_csv(CANDIDATE_DIR / "test_ood.csv")
    eval_df = pd.concat([df_tid, df_tood], ignore_index=True)

    if stage == "smoke":
        # Smoke test: 2 groups from Test-ID, 2 groups from Test-OOD (4 groups x 5 conditions = 20 prompts)
        sample_sids = list(df_tid["semantic_id"].unique()[:2]) + list(df_tood["semantic_id"].unique()[:2])
        eval_df = eval_df[eval_df["semantic_id"].isin(sample_sids)].copy()
    elif stage == "val_sample":
        # Validation sample: 10 groups from Test-ID, 10 groups from Test-OOD (20 groups x 5 = 100 prompts)
        sample_sids = list(df_tid["semantic_id"].unique()[:10]) + list(df_tood["semantic_id"].unique()[:10])
        eval_df = eval_df[eval_df["semantic_id"].isin(sample_sids)].copy()
    elif limit_groups is not None:
        sample_sids = list(eval_df["semantic_id"].unique()[:limit_groups])
        eval_df = eval_df[eval_df["semantic_id"].isin(sample_sids)].copy()

    total_prompts_per_model = len(eval_df)
    total_inferences = total_prompts_per_model * len(models)
    print(f"[{stage.upper()}] Selected {eval_df['semantic_id'].nunique()} semantic groups ({total_prompts_per_model} prompts per model). Total inferences: {total_inferences}")

    # Checkpoint F: Budget Projection & Approval
    est_total_calls = total_inferences * 2  # model inference + judge call
    cost_est = estimate_cost(
        experiment_id="EXP-002",
        provider="groq",
        model="qwen/qwen3.8-27b",
        num_calls=est_total_calls,
        avg_input_tokens=60,
        avg_output_tokens=70,
    )
    assert_budget_approved(cost_est)
    print(f"=== CHECKPOINT F: Budget Approved. Estimated stage cost: ${cost_est.estimated_cost_usd:.5f} USD ===")

    # Initialize Clients & Judge
    clients = {m: GroqClient(m) for m in models}
    judge_client = GroqClient("qwen/qwen3.8-27b")

    all_records: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    total_tokens_spent = 0
    actual_cost_spent = 0.0
    # Load existing completed prompts if file exists for resumability
    completed_keys = set()
    if predictions_file.exists():
        with open(predictions_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    completed_keys.add((obj["model"], obj["prompt_id"]))
                    all_records.append(obj)
                except Exception:
                    pass
        print(f"Resuming run: found {len(completed_keys)} previously completed inferences.")

    import threading
    from concurrent.futures import ThreadPoolExecutor, as_completed

    print("Beginning Inference Execution (Multithreaded with 8 workers)...")
    pbar = tqdm(total=total_inferences, desc=f"EXP-002 {stage}", initial=len(completed_keys))

    pred_fp = open(predictions_file, "a", encoding="utf-8")
    write_lock = threading.Lock()

    # Build queue of pending items
    tasks_to_run = []
    for model_name, client in clients.items():
        for row in eval_df.itertuples():
            if (model_name, row.prompt_id) in completed_keys:
                continue
            tasks_to_run.append((model_name, client, row))

    def worker(task_item):
        nonlocal total_tokens_spent, actual_cost_spent
        model_name, client, row = task_item
        prompt = row.prompt_text
        ref_ans = str(row.reference_answer)
        is_auth = not ("Registry_Unit" in str(row.target_entity))

        try:
            resp_text, lat_ms, in_tok, out_tok = execute_model_call(client, prompt)
            if resp_text.startswith("Answer to:") and f"[{ref_ans}]" in resp_text:
                raise RuntimeError(f"CRITICAL CONTAMINATION: Deterministic mock fallback detected for {model_name}!")

            call_tokens = in_tok + out_tok
            call_cost = (call_tokens / 1_000_000.0) * 0.08

            judge_label, judge_reason = _judge(judge_client, prompt, ref_ans, resp_text)
            judge_tokens = (len(prompt.split()) + len(ref_ans.split()) + len(resp_text.split())) * 2 + 30
            judge_cost = (judge_tokens / 1_000_000.0) * 0.08

            refusal = detect_refusal(resp_text)
            resp_cmi_data = compute_cmi(resp_text, expected_lang=row.language)

            rec = {
                "experiment_id": "EXP-002",
                "stage": stage,
                "model": model_name,
                "git_commit": git_hash,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "semantic_id": row.semantic_id,
                "prompt_id": row.prompt_id,
                "language": row.language,
                "condition": row.condition,
                "partition": row.partition,
                "is_authentic": is_auth,
                "template_family_id": row.template_family_id,
                "difficulty_level": int(row.difficulty_level),
                "target_entity": row.target_entity,
                "prompt_text": prompt,
                "reference_answer": ref_ans,
                "evidence_snippet": str(row.evidence_snippet),
                "model_response": resp_text,
                "latency_ms": round(lat_ms, 2),
                "prompt_tokens": in_tok,
                "completion_tokens": out_tok,
                "total_tokens": call_tokens,
                "cost_usd": round(call_cost + judge_cost, 6),
                "judge_label": judge_label,
                "judge_reason": judge_reason,
                "is_refusal": refusal,
                "response_cmi": resp_cmi_data["cmi"],
            }
            with write_lock:
                total_tokens_spent += call_tokens + judge_tokens
                actual_cost_spent += call_cost + judge_cost
                all_records.append(rec)
                pred_fp.write(json.dumps(rec, ensure_ascii=False) + "\n")
                pred_fp.flush()
                pbar.update(1)
        except Exception as e:
            with write_lock:
                failures.append({
                    "model": model_name,
                    "prompt_id": row.prompt_id,
                    "semantic_id": row.semantic_id,
                    "error": str(e),
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                })
                pbar.update(1)
                print(f"\n[FAIL] {model_name} on {row.prompt_id}: {e}")

    with ThreadPoolExecutor(max_workers=3) as executor:
        list(executor.map(worker, tasks_to_run))

    pbar.close()
    pred_fp.close()

    if failures:
        with open(failures_file, "w", encoding="utf-8") as f:
            for fr in failures:
                f.write(json.dumps(fr, ensure_ascii=False) + "\n")

    # Record spend in ledger
    if actual_cost_spent > 0:
        record_spend(
            experiment_id="EXP-002",
            provider="groq",
            model="multi-model",
            calls=total_inferences * 2,
            input_tokens=total_tokens_spent // 2,
            output_tokens=total_tokens_spent // 2,
            cost_usd=actual_cost_spent,
            notes=f"EXP-002 {stage} stage inference and evaluation",
        )

    # Compute high-level summary metrics
    results_df = pd.DataFrame(all_records)
    summary_data: dict[str, Any] = {
        "stage": stage,
        "git_commit": git_hash,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_inferences_attempted": total_inferences,
        "successful_inferences": len(all_records),
        "failed_inferences": len(failures),
        "models_evaluated": models,
        "total_tokens_spent": total_tokens_spent,
        "actual_cost_spent_usd": round(actual_cost_spent, 5),
        "cumulative_budget_status": get_budget_status(),
    }

    if not results_df.empty:
        # Factual Accuracy (% where judge_label == 0)
        results_df["is_correct"] = (results_df["judge_label"] == 0).astype(int)
        
        # Accuracy by Model & Condition
        by_model_cond = results_df.groupby(["model", "condition"])["is_correct"].agg(["mean", "count"]).to_dict("index")
        summary_data["by_model_and_condition"] = {f"{k[0]}_{k[1]}": round(v["mean"] * 100, 2) for k, v in by_model_cond.items()}

        # Accuracy by Model & Language
        by_model_lang = results_df.groupby(["model", "language"])["is_correct"].agg(["mean", "count"]).to_dict("index")
        summary_data["by_model_and_language"] = {f"{k[0]}_{k[1]}": round(v["mean"] * 100, 2) for k, v in by_model_lang.items()}

        # Accuracy by Partition (Test-ID vs Test-OOD)
        by_part = results_df.groupby(["model", "partition"])["is_correct"].agg(["mean", "count"]).to_dict("index")
        summary_data["by_model_and_partition"] = {f"{k[0]}_{k[1]}": round(v["mean"] * 100, 2) for k, v in by_part.items()}

        # Accuracy by Core vs Synthetic
        by_auth = results_df.groupby(["model", "is_authentic"])["is_correct"].agg(["mean", "count"]).to_dict("index")
        summary_data["by_model_and_composition"] = {f"{k[0]}_authentic_{k[1]}": round(v["mean"] * 100, 2) for k, v in by_auth.items()}

        # Overall Model Accuracy
        summary_data["overall_model_accuracy"] = {m: round(float(results_df[results_df["model"] == m]["is_correct"].mean() * 100), 2) for m in models}

    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    print(f"\n[{stage.upper()} COMPLETE] Saved results to {predictions_file} and {summary_file}")
    print("Summary:", json.dumps(summary_data, indent=2))
    return summary_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EXP-002 Staged Inference Execution")
    parser.add_argument("--stage", choices=["smoke", "val_sample", "full"], default="smoke")
    parser.add_argument("--limit-groups", type=int, default=None)
    args = parser.parse_args()

    run_exp002_stage(stage=args.stage, limit_groups=args.limit_groups)
