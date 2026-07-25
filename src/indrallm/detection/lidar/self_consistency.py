"""Phase 1 Probe 5: Recursive Self-Consistency (RSC).

Re-sample the base model K times on the same prompt; a well-grounded answer is
stable across samples, a hallucinated one diverges. Because it re-decodes K times
it is the one expensive probe — gate it behind a flag and cache.

Two answer-level signals:
  rsc_token_div   mean per-position unique-token ratio across K greedy-with-seed
                  samples (proxy; low = consistent).
  rsc_embed_div   1 - mean pairwise multilingual-embedding cosine across the K
                  full samples (semantic disagreement; robust to surface variance).

Needs a GPU. Neutral (0.0) if the model/encoder is unavailable.
"""

from __future__ import annotations

from indrallm.config import CFG

_NEUTRAL = {"rsc_token_div": 0.0, "rsc_embed_div": 0.0}


class SelfConsistency:
    def __init__(self, model_name: str | None = None, k: int = 5, max_new: int = 64):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        m = CFG["mitigation"]
        name = model_name or m["model"]
        self.torch = torch
        self.k = k
        self.max_new = max_new
        self.tokenizer = AutoTokenizer.from_pretrained(name)
        kwargs: dict = {"device_map": "auto"}
        if m.get("load_in_4bit") and torch.cuda.is_available():
            from transformers import BitsAndBytesConfig
            kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)
        else:
            kwargs["torch_dtype"] = torch.bfloat16 if torch.cuda.is_available() else torch.float32
        self.model = AutoModelForCausalLM.from_pretrained(name, **kwargs)
        self.model.eval()
        self._enc = None

    def _encoder(self):
        if self._enc is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._enc = SentenceTransformer(
                    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
            except Exception:
                self._enc = False
        return self._enc or None

    def _sample(self, prompt: str, seed: int) -> tuple[list[int], str]:
        torch = self.torch
        torch.manual_seed(seed)
        ids = self.tokenizer(f"Question: {prompt}\nAnswer:", return_tensors="pt").input_ids.to(self.model.device)
        out = self.model.generate(ids, max_new_tokens=self.max_new, do_sample=True,
                                  temperature=0.8, top_p=0.95,
                                  pad_token_id=self.tokenizer.eos_token_id)
        new = out[0][ids.shape[1]:].tolist()
        return new, self.tokenizer.decode(new, skip_special_tokens=True)

    def extract(self, question: str) -> dict:
        try:
            seqs, texts = [], []
            for s in range(self.k):
                toks, txt = self._sample(question, seed=1234 + s)
                seqs.append(toks)
                texts.append(txt)
            L = min((len(s) for s in seqs), default=0)
            if L == 0:
                return dict(_NEUTRAL)
            divs = []
            for pos in range(L):
                uniq = len({s[pos] for s in seqs})
                divs.append(uniq / self.k)
            token_div = sum(divs) / len(divs)

            embed_div = 0.0
            enc = self._encoder()
            if enc is not None:
                import itertools
                v = enc.encode(texts, normalize_embeddings=True, show_progress_bar=False)
                sims = [float(v[i] @ v[j]) for i, j in itertools.combinations(range(len(texts)), 2)]
                embed_div = 1.0 - (sum(sims) / len(sims) if sims else 1.0)
            return {"rsc_token_div": token_div, "rsc_embed_div": embed_div}
        except Exception:
            return dict(_NEUTRAL)
