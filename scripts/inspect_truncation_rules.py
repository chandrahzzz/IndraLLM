"""Inspect automated truncation definitions on EXP-002 authentic Qwen rows."""

import json
import pandas as pd
import re

def main():
    pred_path = "results/EXP-002/full_predictions.jsonl"
    with open(pred_path, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f]
    
    auth_qwen = [r for r in records if r.get("is_authentic") and r.get("model") == "qwen/qwen3.8-27b"]
    df = pd.DataFrame(auth_qwen)

    sentence_enders = set([".", "!", "?", "।", '"', "'", "`", "’", "”", "}", ")", "]", "—", "-"])

    def is_mid_sentence(text):
        t = text.strip()
        if not t:
            return False
        return t[-1] not in sentence_enders

    trunc_keywords = re.compile(r"\b(incomplete|truncat|cut off|abrupt|unfinish|missing specific|missing parameter|fails to finish)\b", re.I)

    # Rule 1: Ends mid-sentence (syntactic truncation at token limit)
    df["mid_sentence"] = df["model_response"].apply(is_mid_sentence)
    
    # Rule 2: Judge reason explicitly notes incomplete / truncated answer
    df["judge_notes_incomplete"] = df["judge_reason"].apply(lambda r: bool(trunc_keywords.search(str(r))))
    
    # Rule 3: Strict composite rule:
    # (ends mid-sentence AND completion_tokens == 128) OR judge explicitly mentions incomplete/truncation
    df["composite_truncation"] = df["mid_sentence"] & (df["completion_tokens"] == 128)

    print("=== AUTOMATED TRUNCATION DETECTION BY CONDITION ===")
    for cond in ["A_EN", "B_NATIVE", "C_ROMAN", "D_CS", "E_MIXED_SCRIPT"]:
        sub = df[df["condition"] == cond]
        n = len(sub)
        mid = sub["mid_sentence"].sum()
        j_inc = sub["judge_notes_incomplete"].sum()
        comp = sub["composite_truncation"].sum()
        print(f"Condition: {cond:14s} (N={n})")
        print(f"  Rule 1 (Ends mid-sentence):                    {mid}/{n} ({mid/n*100:.1f}%)")
        print(f"  Rule 2 (Judge reason cites incomplete):       {j_inc}/{n} ({j_inc/n*100:.1f}%)")
        print(f"  Rule 3 (Mid-sentence @ 128 tokens):          {comp}/{n} ({comp/n*100:.1f}%)")

if __name__ == "__main__":
    main()
