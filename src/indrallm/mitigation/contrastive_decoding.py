"""Multilingual contrastive decoding for code-switched input.

Idea: hallucinations on code-switched input often come from the model anchoring
on the *weaker* monolingual reading of the prompt. We decode with two contexts:

  expert  = full code-switched prompt
  amateur = prompt with non-English (Indic) tokens stripped (degraded context)

At each step:  score = expert_logits - beta * amateur_logits   (on the expert's
plausibility-truncated candidate set, as in Li et al. 2023 contrastive decoding).
Tokens the amateur likes *despite missing the Indic context* are exactly the
generic/anchored continuations that produce hallucinations — they get penalized.

Needs a GPU. Usage:
    python -m indrallm.mitigation.contrastive_decoding --prompt "Enna medicine edukkanum? Doctor said fever iruku"
    python -m indrallm.mitigation.contrastive_decoding --eval --limit 100
"""

from __future__ import annotations

import argparse
import re
import unicodedata

import pandas as pd
from tqdm import tqdm

from indrallm.config import CFG, path
from indrallm.collection.codeswitch_filter import ROMANIZED_HINTS, SCRIPT_RANGES


def strip_indic(text: str) -> str:
    """Degrade the prompt: drop native-script tokens and known romanized Indic words."""
    hints = set().union(*ROMANIZED_HINTS.values())
    kept = []
    for tok in text.split():
        core = re.sub(r"\W+", "", tok).lower()
        if core in hints:
            continue
        if any(lo <= ch <= hi for ch in tok for lo, hi in SCRIPT_RANGES.values()):
            continue
        kept.append(tok)
    return " ".join(kept)


class ContrastiveDecoder:
    def __init__(self, model_name: str | None = None,
                 alpha: float | None = None, beta: float | None = None):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        m = CFG["mitigation"]
        self.alpha = alpha if alpha is not None else m["alpha"]
        self.beta = beta if beta is not None else m["beta"]
        self.max_new = m["max_new_tokens"]
        name = model_name or m["model"]
        self.tokenizer = AutoTokenizer.from_pretrained(name)
        self.model = AutoModelForCausalLM.from_pretrained(
            name, torch_dtype=torch.bfloat16, device_map="auto")
        self.torch = torch

    def _prep(self, prompt: str):
        text = f"Question: {prompt}\nAnswer:"
        return self.tokenizer(text, return_tensors="pt").input_ids.to(self.model.device)

    def generate(self, prompt: str) -> str:
        torch = self.torch
        expert_ids = self._prep(prompt)
        amateur_ids = self._prep(strip_indic(prompt))
        eos = self.tokenizer.eos_token_id
        out: list[int] = []

        with torch.no_grad():
            for _ in range(self.max_new):
                e_logits = self.model(expert_ids).logits[0, -1]
                a_logits = self.model(amateur_ids).logits[0, -1]
                e_logprobs = torch.log_softmax(e_logits, dim=-1)
                a_logprobs = torch.log_softmax(a_logits, dim=-1)

                # adaptive plausibility constraint (alpha-mass of expert dist)
                cutoff = torch.log(torch.tensor(0.1)) + e_logprobs.max()
                score = self.alpha * e_logprobs - self.beta * a_logprobs
                score[e_logprobs < cutoff] = float("-inf")

                nxt = int(score.argmax())
                if nxt == eos:
                    break
                out.append(nxt)
                nxt_t = torch.tensor([[nxt]], device=expert_ids.device)
                expert_ids = torch.cat([expert_ids, nxt_t], dim=1)
                amateur_ids = torch.cat([amateur_ids, nxt_t], dim=1)

        return self.tokenizer.decode(out, skip_special_tokens=True).strip()

    def generate_baseline(self, prompt: str) -> str:
        """Plain greedy decoding for comparison."""
        ids = self._prep(prompt)
        out = self.model.generate(ids, max_new_tokens=self.max_new, do_sample=False,
                                  pad_token_id=self.tokenizer.eos_token_id)
        return self.tokenizer.decode(out[0][ids.shape[1]:], skip_special_tokens=True).strip()


def run_eval(limit: int | None) -> None:
    """Generate baseline + contrastive answers for benchmark questions, save both.

    The two answer sets go through the trained IndicBERT detector
    (evaluation.run_benchmark --mitigation) to measure hallucination-rate reduction.
    """
    questions = pd.read_csv(path("questions") / "questions.csv")
    if limit:
        questions = questions.groupby("language").head(limit // 5 or 1)
    dec = ContrastiveDecoder()
    rows = []
    for r in tqdm(questions.itertuples(), total=len(questions)):
        rows.append({"qid": r.qid, "language": r.language, "question": r.question,
                     "baseline": dec.generate_baseline(r.question),
                     "contrastive": dec.generate(r.question)})
    out = path("answers") / "mitigation_comparison.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"saved -> {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--prompt", help="single prompt demo")
    ap.add_argument("--eval", action="store_true", help="run over benchmark questions")
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()

    if args.prompt:
        dec = ContrastiveDecoder()
        print("baseline:   ", dec.generate_baseline(args.prompt))
        print("contrastive:", dec.generate(args.prompt))
    elif args.eval:
        run_eval(args.limit)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
