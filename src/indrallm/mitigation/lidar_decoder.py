"""Type-aware selective-intervention decoder (Claim Family 2 scaffold).

The intervention architecture is preserved: a per-step decode loop, a signature
lookup that maps a detected hallucination to a type, type-specific interventions,
and a position-aware intensity modulator (stronger correction early, lighter
late). What is NOT wired yet is DETECTION: the surface/cross-lingual detector was
removed, and the replacement — a detector over model-internal probes (HSD/AE/UC)
evaluated on the partial output — depends on the internal-probe gate passing
first. Until then `self._detect` is a stub returning 0.0, so `generate` behaves
as the base model and `generate_baseline` gives the comparison point.

To finish this once a working internal detector exists:
  - compute InternalProbes features on the partial output every `check_every`
    steps, feed the trained detector, set p = hallucination probability;
  - keep the signature match + intervention + intensity code below unchanged.

Needs a GPU. Usage:
    from indrallm.mitigation.lidar_decoder import LidarDecoder, get_intensity
    dec = LidarDecoder()
    print(dec.generate_baseline("Enna medicine edukkanum? fever iruku"))
"""

from __future__ import annotations

from indrallm.config import CFG
from indrallm.detection.signatures import SignatureDB
from indrallm.mitigation import interventions as itv


def get_intensity(t: int, base_intensity: float = 1.0) -> float:
    """Position-aware intensity: aggressive early (errors compound), light late."""
    if t < 10:
        return base_intensity * 1.5
    if t < 50:
        return base_intensity * 1.0
    return base_intensity * 0.5


class LidarDecoder:
    def __init__(self, threshold: float = 0.6, check_every: int = 8, max_new: int | None = None):
        import torch
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
        self.sig = SignatureDB.load()

    # --- DETECTION STUB ---
    # Surface/cross-lingual detection was removed. Wire an internal-probe detector
    # here (see module docstring) once the internal-probe gate passes.
    def _detect(self, question: str, partial: str, lang=None) -> tuple[float, dict]:
        return 0.0, {}

    def _prep(self, prompt: str):
        return self.tokenizer(f"Question: {prompt}\nAnswer:",
                              return_tensors="pt").input_ids.to(self.model.device)

    def generate(self, prompt: str, lang=None) -> str:
        torch = self.torch
        from indrallm.detection.lidar.lid import token_lid
        ids = self._prep(prompt)
        out: list[int] = []
        eos = self.tokenizer.eos_token_id
        with torch.no_grad():
            for step in range(self.max_new):
                logits = self.model(ids).logits[0, -1]
                if out and step % self.check_every == 0:
                    partial = self.tokenizer.decode(out, skip_special_tokens=True)
                    p, feats = self._detect(prompt, partial, lang)
                    if p >= self.threshold:
                        _type, action = self.sig.match(feats)
                        intensity = get_intensity(step)
                        if action == "repetition_penalty":
                            logits = itv.repetition_penalty(logits, out[-16:], penalty=1.0 + 0.5 * intensity)
                        elif action == "language_constraint":
                            exp = [lang] if lang else "ta hi te bn kn en".split()
                            logits = itv.language_constraint(
                                logits, self.tokenizer, set(exp),
                                lambda s: token_lid(s, lang), boost=3.0 * intensity)
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
