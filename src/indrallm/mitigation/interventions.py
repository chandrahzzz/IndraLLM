"""Phase 4 interventions: type-specific logit / sequence corrections.

Each function takes the current decoding context and returns either modified
logits (language_constraint, repetition_penalty) or a signal to the decoder
(rollback), or a re-ranked next-token id (fact_rerank). Kept dependency-free of
the detector so they can be unit-tested in isolation.
"""

from __future__ import annotations


def language_constraint(logits, tokenizer, expected_langs, lid_fn, boost: float = 3.0):
    """Bias logits toward tokens whose decoded piece reads as an expected language.

    Cheap approximation: boost the logits of the current top-k candidate tokens
    that the token-level LID assigns to an expected language, penalize the rest.
    """
    import torch
    topk = torch.topk(logits, k=min(50, logits.shape[-1]))
    for idx in topk.indices.tolist():
        piece = tokenizer.decode([idx]).strip()
        if not piece:
            continue
        lang = lid_fn(piece)[0] if lid_fn(piece) else "other"
        logits[idx] += boost if lang in expected_langs else -boost
    return logits


def repetition_penalty(logits, recent_ids, penalty: float = 1.5):
    """Divide logits of recently-emitted tokens (classic repetition penalty)."""
    for tid in set(recent_ids):
        if logits[tid] > 0:
            logits[tid] /= penalty
        else:
            logits[tid] *= penalty
    return logits


def rollback(output_ids, n: int = 2):
    """Return output truncated by n tokens; the decoder regenerates from here."""
    return output_ids[:-n] if len(output_ids) > n else output_ids[:0]


def fact_rerank(candidate_ids, context, answer_so_far, tokenizer, nli):
    """Re-rank top-k next tokens by entailment of the extended answer vs context.

    `nli` is a callable (premise, hypothesis) -> entailment_prob. Picks the token
    whose one-step extension is most entailed by the question context. Falls back
    to the model's own top candidate if no NLI judge is available.
    """
    if nli is None or not candidate_ids:
        return candidate_ids[0] if candidate_ids else None
    best, best_score = candidate_ids[0], -1.0
    for tid in candidate_ids:
        hyp = answer_so_far + tokenizer.decode([tid])
        score = nli(context, hyp)
        if score > best_score:
            best, best_score = tid, score
    return best
