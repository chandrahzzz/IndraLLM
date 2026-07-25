"""Phase 4: closed-loop decoder — detect and correct hallucinations mid-generation.

Wraps the base model's step-by-step decoding. At each step it forms features on
the partial output, runs the trained multi-view detector, and if the
hallucination probability crosses threshold it matches the signature database and
applies the corresponding intervention (Section 9 of docs/BUILD_INDRALLM.md).

Runs a windowed re-featurization every `check_every` tokens (not every token) to
hold the <20% latency budget; the detector itself is a tiny MLP so the dominant
cost stays the base model's own forward pass.

Needs a GPU + a trained detector. Usage:
    from indrallm.mitigation.lidar_decoder import LidarDecoder
    dec = LidarDecoder()
    print(dec.generate("Enna medicine edukkanum? fever iruku"))
    print(dec.generate_baseline(prompt))   # for the reduction comparison
"""

from __future__ import annotations

from indrallm.config import CFG, path
from indrallm.detection.lidar.features import (extract_features, fit_transition_matrix,
                                               _make_embedder)
from indrallm.detection.lidar.cross_lingual import cla_features
from indrallm.detection.lidar.feature_cache import repetition_score
from indrallm.detection.signatures import SignatureDB
from indrallm.detection.multi_view.views import resolve_views
from indrallm.detection.multi_view.detector import build_detector
from indrallm.mitigation import interventions as itv


class LidarDecoder:
    def __init__(self, threshold: float = 0.65, check_every: int = 8, max_new: int | None = None):
        import torch
        import pandas as pd
        from transformers import AutoModelForCausalLM, AutoTokenizer
        m = CFG["mitigation"]
        self.torch = torch
        self.threshold = threshold
        self.check_every = check_every
        self.max_new = max_new or m["max_new_tokens"]
        name = m["model"]
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

        # feature scaffolding
        fp = path("features") / "answer_features.parquet"
        feats_df = pd.read_parquet(fp) if fp.exists() else None
        q = feats_df["qid_model"] if feats_df is not None else []
        self.tm = fit_transition_matrix(
            (pd.read_csv(path("final") / "benchmark_judged.csv")["question"].tolist()
             if (path("final") / "benchmark_judged.csv").exists() else []))
        self.embed = _make_embedder(True)
        self.sig = SignatureDB.load()

        # trained detector (view layout inferred from the cache columns)
        self.views = resolve_views(list(feats_df.columns)) if feats_df is not None else \
            resolve_views(["bcs", "switch_rate", "frac_en", "frac_indic", "frac_other",
                           "n_tokens", "repetition_score", "perplexity", "logit_var_mean",
                           "cla_mean", "cla_min", "cla_max_drop", "n_boundaries"])
        self.detector = None
        dpath = path("models") / "multi_view_detector" / "detector.pt"
        if dpath.exists():
            self.detector = build_detector({v: len(c) for v, c in self.views.items()})
            self.detector.load_state_dict(torch.load(dpath, map_location="cpu"))
            self.detector.eval()

    def _detect(self, question: str, partial: str, lang=None) -> float:
        if self.detector is None:
            return 0.0
        row = extract_features(partial, self.tm, lang, self.embed)
        row["repetition_score"] = repetition_score(partial)
        row.update(cla_features(partial, lang))
        import numpy as np
        batch = {}
        for v, cols in self.views.items():
            arr = np.array([[row.get(c, 0.0) for c in cols]], dtype=np.float32)
            batch[v] = self.torch.tensor(arr)
        with self.torch.no_grad():
            p, _, _ = self.detector(batch)
        return float(p.item())

    def _prep(self, prompt: str):
        return self.tokenizer(f"Question: {prompt}\nAnswer:", return_tensors="pt").input_ids.to(self.model.device)

    def generate(self, prompt: str, lang=None) -> str:
        torch = self.torch
        ids = self._prep(prompt)
        out: list[int] = []
        eos = self.tokenizer.eos_token_id
        from indrallm.detection.lidar.lid import token_lid
        with torch.no_grad():
            for step in range(self.max_new):
                logits = self.model(ids).logits[0, -1]
                if out and step % self.check_every == 0:
                    partial = self.tokenizer.decode(out, skip_special_tokens=True)
                    p = self._detect(prompt, partial, lang)
                    if p >= self.threshold:
                        feats = {**extract_features(partial, self.tm, lang, self.embed),
                                 "repetition_score": repetition_score(partial),
                                 **cla_features(partial, lang)}
                        _type, action = self.sig.match(feats)
                        if action == "repetition_penalty":
                            logits = itv.repetition_penalty(logits, out[-16:])
                        elif action == "language_constraint":
                            exp = [lang] if lang else list("ta hi te bn kn en".split())
                            logits = itv.language_constraint(
                                logits, self.tokenizer, set(exp), lambda s: token_lid(s, lang))
                        elif action == "rollback":
                            out = list(itv.rollback(out, 2))
                            ids = torch.cat([self._prep(prompt),
                                             torch.tensor([out], device=ids.device)], dim=1) \
                                if out else self._prep(prompt)
                            continue
                nxt = int(logits.argmax())
                if nxt == eos:
                    break
                out.append(nxt)
                ids = torch.cat([ids, torch.tensor([[nxt]], device=ids.device)], dim=1)
        return self.tokenizer.decode(out, skip_special_tokens=True).strip()

    def generate_baseline(self, prompt: str) -> str:
        torch = self.torch
        ids = self._prep(prompt)
        with torch.no_grad():
            o = self.model.generate(ids, max_new_tokens=self.max_new, do_sample=False,
                                    pad_token_id=self.tokenizer.eos_token_id)
        return self.tokenizer.decode(o[0][ids.shape[1]:], skip_special_tokens=True).strip()
