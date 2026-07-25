"""Phase 5 (optional): LITA — Language-Identity-aware Training with Adversarial feedback.

Run ONLY after the closed-loop decoder beats baseline. Three stages:

  Stage 1  Auxiliary-LID SFT: attach a per-token language-ID head to the base
           model; loss = LM + lambda * LID cross-entropy. Teaches the model to
           represent which language each token is.
  Stage 2  Adversarial generation: generate answers, run the detector, and for
           each flagged hallucination synthesize language-swap / boundary-shift /
           bleed-insert variants paired with the corrected gold target.
  Stage 3  Adversarial fine-tune: LM(gold) + a*LM(adv->corrected)
           + b*KL(LID_pred||LID_target) + g*BCE(detector(gen), not-halluc).

Needs a GPU. This module wires the pieces; heavy training loops assume Colab T4
with 4-bit + LoRA (reuse config `lora`). Usage:
    python -m indrallm.mitigation.lita_trainer --stage 1
    python -m indrallm.mitigation.lita_trainer --stage 2
    python -m indrallm.mitigation.lita_trainer --stage 3
"""

from __future__ import annotations

import argparse

import pandas as pd

from indrallm.config import CFG, path
from indrallm.detection.lidar.lid import token_lid, tokenize

LANGS = ["en", "ta", "hi", "te", "bn", "kn"]
_LID2I = {l: i for i, l in enumerate(LANGS)}


def _lid_targets(text: str, lang=None) -> list[int]:
    return [_LID2I.get(l, 0) for l in token_lid(text, lang)]


# ---- Stage 2 adversarial synthesis (CPU-runnable; no model needed) ----

def language_swap(answer: str, lang: str | None) -> str:
    """Swap a run of romanized-Indic tokens to English placeholders (surface perturbation)."""
    from indrallm.collection.codeswitch_filter import ROMANIZED_HINTS
    hints = ROMANIZED_HINTS.get(lang or "", set())
    return " ".join("<en>" if t.lower() in hints else t for t in tokenize(answer))


def boundary_shift(answer: str, lang: str | None) -> str:
    """Move the first language-switch point one token right."""
    toks = tokenize(answer)
    seq = token_lid(answer, lang)
    for i in range(1, len(seq)):
        if seq[i] != seq[i - 1] and i + 1 < len(toks):
            toks[i], toks[i + 1] = toks[i + 1], toks[i]
            break
    return " ".join(toks)


def bleed_insert(answer: str, lang: str | None) -> str:
    """Insert a dominant-language filler at the first switch point."""
    toks = tokenize(answer)
    seq = token_lid(answer, lang)
    for i in range(1, len(seq)):
        if seq[i] != seq[i - 1]:
            toks.insert(i, "actually")
            break
    return " ".join(toks)


def build_adversarial_set(limit: int | None = None) -> pd.DataFrame:
    """Stage 2 (detector-free surface variant): make adversarial->corrected pairs
    from judged-hallucinated rows. If a trained detector is available on GPU, prefer
    filtering to detector-flagged rows; here we use the judge label as the filter."""
    src = path("final") / "benchmark_judged.csv"
    df = pd.read_csv(src if src.exists() else path("final") / "benchmark.csv")
    df = df[(df["label"] == 1) & (df["answer"].fillna("").str.strip() != "")]
    if limit:
        df = df.head(limit)
    rows = []
    for r in df.itertuples():
        lang = getattr(r, "language", None)
        for fn in (language_swap, boundary_shift, bleed_insert):
            rows.append({"qid": r.qid, "language": lang, "question": r.question,
                         "adversarial": fn(r.answer, lang), "corrected": r.ground_truth,
                         "variant": fn.__name__})
    out = pd.DataFrame(rows)
    dest = path("annotations") / "adversarial_set.csv"
    out.to_csv(dest, index=False)
    print(f"stage 2: {len(out)} adversarial pairs -> {dest}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", type=int, choices=[1, 2, 3], required=True)
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()

    if args.stage == 2:
        build_adversarial_set(args.limit)
        return

    # Stages 1 & 3 need the base model on GPU.
    print(f"stage {args.stage}: requires GPU (Sarvam-2B). See docstring; wiring uses "
          f"config lora={CFG['lora']}. LID label space={LANGS}.")
    print("Stage 1: attach nn.Linear(hidden, 6) LID head, loss=LM+0.1*CE(LID).")
    print("Stage 3: LM(gold)+a*LM(adv->corrected)+b*KL(LID)+g*BCE(detector,0). "
          "Build adversarial pairs with --stage 2 first.")


if __name__ == "__main__":
    main()
