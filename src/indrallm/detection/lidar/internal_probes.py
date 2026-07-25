"""Phase 1 internal probes: Hidden-State Divergence, Attention Entropy, Uncertainty.

Reads the base model's own internals over a fixed (question, answer) pair in a
SINGLE forward pass (output_hidden_states + output_attentions), so no generation
is needed — cheap enough to run over the whole benchmark on a Colab T4.

  HSD  Hidden-State Divergence  cosine distance between consecutive token hidden
       states, per decoder layer. A hallucinated span tends to lurch in
       representation space; a grounded span moves smoothly.
  AE   Attention Entropy        Shannon entropy of each head's attention over the
       context. Diffuse (high) or collapsed (low) attention flags trouble.
  UC   Uncertainty Calibration  UC = 1 - confidence/(1+logit_variance); high =
       uncertain-yet-overconfident next-token distribution.

All three are emitted per answer-token and also aggregated to the answer level
(mean/max/var/slope). GPU strongly recommended; degrades to CPU (slow) or to
neutral zeros if the model can't be loaded, never crashes the caller.

Usage (Colab):
    from indrallm.detection.lidar.internal_probes import InternalProbes
    probes = InternalProbes()                 # loads Sarvam-2B 4-bit
    feats = probes.extract(question, answer)  # -> {"tokens":[...], "per_token":{...}, "answer":{...}}
"""

from __future__ import annotations

import math

from indrallm.config import CFG

_NEUTRAL_ANSWER = {
    "hsd_mean": 0.0, "hsd_max": 0.0, "hsd_var": 0.0, "hsd_slope": 0.0,
    "ae_mean": 0.0, "ae_max": 0.0, "ae_var": 0.0, "ae_spike_rate": 0.0,
    "uc_mean": 0.0, "uc_max": 0.0, "uc_var": 0.0, "logit_var_mean": 0.0,
    "conf_mean": 0.0, "perplexity": 0.0, "n_tokens": 0.0,
}


def _slope(xs: list[float]) -> float:
    """Least-squares slope of xs vs index; 0 for <2 points."""
    n = len(xs)
    if n < 2:
        return 0.0
    mx = (n - 1) / 2
    my = sum(xs) / n
    num = sum((i - mx) * (x - my) for i, x in enumerate(xs))
    den = sum((i - mx) ** 2 for i in range(n))
    return num / den if den else 0.0


def _agg(xs: list[float]) -> tuple[float, float, float]:
    if not xs:
        return 0.0, 0.0, 0.0
    m = sum(xs) / len(xs)
    v = sum((x - m) ** 2 for x in xs) / len(xs)
    return m, max(xs), v


class InternalProbes:
    def __init__(self, model_name: str | None = None, load_in_4bit: bool | None = None):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        m = CFG["mitigation"]
        name = model_name or m["model"]
        self.torch = torch
        self.tokenizer = AutoTokenizer.from_pretrained(name)
        kwargs: dict = {"device_map": "auto", "output_hidden_states": True,
                        "output_attentions": True, "attn_implementation": "eager"}
        want_4bit = m.get("load_in_4bit") if load_in_4bit is None else load_in_4bit
        if want_4bit and torch.cuda.is_available():
            from transformers import BitsAndBytesConfig
            kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)
        else:
            kwargs["torch_dtype"] = torch.float32 if not torch.cuda.is_available() else torch.bfloat16
        self.model = AutoModelForCausalLM.from_pretrained(name, **kwargs)
        self.model.eval()

    def _answer_span(self, question: str, answer: str):
        """Token ids for 'Q..\nA:..' and the [start,end) slice covering the answer."""
        pre = self.tokenizer(f"Question: {question}\nAnswer:", add_special_tokens=True)
        full = self.tokenizer(f"Question: {question}\nAnswer: {answer}", add_special_tokens=True)
        start = len(pre["input_ids"])
        ids = full["input_ids"]
        return ids, max(start, 1), len(ids)

    def extract(self, question: str, answer: str) -> dict:
        torch = self.torch
        if not (answer or "").strip():
            return {"tokens": [], "per_token": {}, "answer": dict(_NEUTRAL_ANSWER)}
        try:
            ids, a0, a1 = self._answer_span(question, answer)
            input_ids = torch.tensor([ids], device=self.model.device)
            with torch.no_grad():
                out = self.model(input_ids)
            hs = out.hidden_states          # tuple[L+1] (1, T, H)
            attn = out.attentions           # tuple[L] (1, heads, T, T)
            logits = out.logits[0]          # (T, V)

            hsd_tok, ae_tok, uc_tok, lv_tok, conf_tok, nll = [], [], [], [], [], []
            for t in range(a0, a1):
                # HSD across layers at position t vs t-1
                layer_d = []
                for L in range(1, len(hs)):
                    a = hs[L][0, t]
                    b = hs[L][0, t - 1]
                    cos = torch.nn.functional.cosine_similarity(a, b, dim=0).item()
                    layer_d.append(1.0 - cos)
                hsd_tok.append(sum(layer_d) / len(layer_d))

                # AE: mean over layers of mean-over-heads entropy of attn row t
                l_ents = []
                for L in range(len(attn)):
                    row = attn[L][0, :, t, : t + 1]        # (heads, t+1)
                    p = row.clamp_min(1e-12)
                    ent = -(p * p.log()).sum(-1)            # (heads,)
                    norm = math.log(t + 1) if t + 1 > 1 else 1.0
                    l_ents.append((ent.mean().item()) / norm)
                ae_tok.append(sum(l_ents) / len(l_ents))

                # UC from next-token logits predicted at position t-1
                lp = logits[t - 1]
                probs = torch.softmax(lp, dim=-1)
                conf = probs.max().item()
                lvar = lp.var(unbiased=False).item()
                uc_tok.append(1.0 - conf / (1.0 + lvar))
                lv_tok.append(lvar)
                conf_tok.append(conf)
                nll.append(-math.log(max(probs[ids[t]].item(), 1e-12)))

            hsd_m, hsd_mx, hsd_v = _agg(hsd_tok)
            ae_m, ae_mx, ae_v = _agg(ae_tok)
            uc_m, uc_mx, uc_v = _agg(uc_tok)
            ae_thr = ae_m + 2 * (ae_v ** 0.5)
            spike = sum(1 for x in ae_tok if x > ae_thr) / len(ae_tok) if ae_tok else 0.0
            ppl = math.exp(sum(nll) / len(nll)) if nll else 0.0
            answer = {
                "hsd_mean": hsd_m, "hsd_max": hsd_mx, "hsd_var": hsd_v, "hsd_slope": _slope(hsd_tok),
                "ae_mean": ae_m, "ae_max": ae_mx, "ae_var": ae_v, "ae_spike_rate": spike,
                "uc_mean": uc_m, "uc_max": uc_mx, "uc_var": uc_v,
                "logit_var_mean": sum(lv_tok) / len(lv_tok) if lv_tok else 0.0,
                "conf_mean": sum(conf_tok) / len(conf_tok) if conf_tok else 0.0,
                "perplexity": ppl, "n_tokens": float(len(hsd_tok)),
            }
            per_token = {"hsd": hsd_tok, "ae": ae_tok, "uc": uc_tok,
                         "logit_var": lv_tok, "confidence": conf_tok}
            toks = self.tokenizer.convert_ids_to_tokens(ids[a0:a1])
            return {"tokens": toks, "per_token": per_token, "answer": answer}
        except Exception as e:  # never break the batch loop
            neutral = dict(_NEUTRAL_ANSWER)
            neutral["error"] = str(e)[:120]
            return {"tokens": [], "per_token": {}, "answer": neutral}
