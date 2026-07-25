"""Phase 1: Linguistic Fidelity Filter — surface-only, CPU, <10ms/segment.

Computes a linguistic-coherence score for a text segment from code-switching
surface features. Trained to separate coherent gold text from artificially
corrupted text. Intended use (per the design): gate the expensive factual
detector — only text scoring below threshold gets the full factual check.

CRITICAL empirical caveat, measured on this project's judged labels: surface
linguistic features do NOT separate real (factual) hallucinations from correct
answers (best surface AUC 0.64, CLA 0.52). So this filter is honest at what it is
trained for — spotting *linguistic* corruption — but its value as a *hallucination*
gate must be proven, not assumed. `evaluate_gating()` runs exactly that test.

Feature extractors (surface, no model internals):
  switch_freq        language changes per 10 tokens (from token_lid)
  switch_burstiness  variance of gap lengths between switches
  cs_perplexity      per-word perplexity under a bigram LM fit on the CS corpus
  oov_rate           fraction of tokens unseen in the corpus vocabulary
  repetition         repeated-trigram ratio
  frac_indic/frac_en language mix (context, not coherence)
"""

from __future__ import annotations

import math
from collections import defaultdict

from indrallm.detection.lidar.lid import token_lid, tokenize

FEATURES = ["switch_freq", "switch_burstiness", "cs_perplexity", "oov_rate",
            "repetition", "frac_indic", "frac_en"]
_INDIC = {"ta", "hi", "te", "bn", "kn"}


class BigramLM:
    """Tiny word-bigram LM with add-1 smoothing; perplexity of a token sequence."""

    def __init__(self):
        self.uni: dict[str, int] = defaultdict(int)
        self.bi: dict[tuple[str, str], int] = defaultdict(int)
        self.vocab: set[str] = set()
        self.total = 0

    def fit(self, texts):
        for t in texts:
            toks = ["<s>"] + [w.lower() for w in tokenize(str(t))] + ["</s>"]
            for w in toks:
                self.uni[w] += 1
                self.vocab.add(w)
            for a, b in zip(toks, toks[1:]):
                self.bi[(a, b)] += 1
        self.total = sum(self.uni.values())
        return self

    def perplexity(self, text) -> float:
        toks = ["<s>"] + [w.lower() for w in tokenize(str(text))] + ["</s>"]
        V = max(len(self.vocab), 1)
        nll, n = 0.0, 0
        for a, b in zip(toks, toks[1:]):
            p = (self.bi.get((a, b), 0) + 1) / (self.uni.get(a, 0) + V)
            nll += -math.log(p)
            n += 1
        return math.exp(nll / n) if n else 0.0

    def oov_rate(self, text) -> float:
        toks = [w.lower() for w in tokenize(str(text))]
        if not toks:
            return 0.0
        return sum(1 for w in toks if w not in self.vocab) / len(toks)


def _repetition(text, n=3) -> float:
    toks = [w.lower() for w in tokenize(str(text))]
    if len(toks) < n + 1:
        return 0.0
    grams = [tuple(toks[i:i + n]) for i in range(len(toks) - n + 1)]
    return 1.0 - len(set(grams)) / len(grams)


def _switch_stats(text, lang=None) -> tuple[float, float]:
    seq = token_lid(str(text), lang)
    if len(seq) < 2:
        return 0.0, 0.0
    switch_idx = [i for i in range(1, len(seq)) if seq[i] != seq[i - 1]]
    freq = 10.0 * len(switch_idx) / len(seq)
    if len(switch_idx) < 2:
        return freq, 0.0
    gaps = [switch_idx[k] - switch_idx[k - 1] for k in range(1, len(switch_idx))]
    m = sum(gaps) / len(gaps)
    var = sum((g - m) ** 2 for g in gaps) / len(gaps)
    return freq, var


def extract(text, lm: BigramLM, lang=None) -> dict:
    seq = token_lid(str(text), lang)
    n = max(len(seq), 1)
    freq, burst = _switch_stats(text, lang)
    return {
        "switch_freq": freq,
        "switch_burstiness": burst,
        "cs_perplexity": lm.perplexity(text),
        "oov_rate": lm.oov_rate(text),
        "repetition": _repetition(text),
        "frac_indic": sum(s in _INDIC for s in seq) / n,
        "frac_en": sum(s == "en" for s in seq) / n,
    }


# ---- corruption: build negatives (linguistically broken code-switch) ----

def corrupt(text, lang=None, rng=None) -> str:
    import random
    rng = rng or random.Random(0)
    toks = tokenize(str(text))
    if len(toks) < 4:
        return text
    mode = rng.choice(["shuffle", "dup", "insert_switch"])
    if mode == "shuffle":
        rng.shuffle(toks)
    elif mode == "dup":
        i = rng.randrange(len(toks))
        toks = toks[:i] + [toks[i]] * rng.randint(3, 6) + toks[i:]
    else:  # scatter native-script noise to fake ungrammatical switches
        noise = {"ta": "இங்கே", "hi": "यहाँ", "te": "ఇక్కడ", "bn": "এখানে", "kn": "ಇಲ್ಲಿ"}.get(lang or "hi", "यहाँ")
        for _ in range(max(2, len(toks) // 4)):
            toks.insert(rng.randrange(len(toks)), noise)
    return " ".join(toks)


class LinguisticFidelityFilter:
    def __init__(self):
        self.lm = BigramLM()
        self.clf = None
        self.mu = None
        self.sd = None

    def _matrix(self, texts, langs):
        import numpy as np
        rows = [[extract(t, self.lm, l)[f] for f in FEATURES] for t, l in zip(texts, langs)]
        return np.asarray(rows, float)

    def fit(self, coherent_texts, langs):
        """Fit LM on coherent corpus; train LogReg on coherent vs corrupted."""
        import random
        import numpy as np
        from sklearn.linear_model import LogisticRegression
        self.lm.fit(coherent_texts)
        rng = random.Random(42)
        neg = [corrupt(t, l, rng) for t, l in zip(coherent_texts, langs)]
        X = np.vstack([self._matrix(coherent_texts, langs), self._matrix(neg, langs)])
        y = np.array([1] * len(coherent_texts) + [0] * len(neg))
        self.mu, self.sd = X.mean(0), X.std(0) + 1e-9
        self.clf = LogisticRegression(max_iter=1000).fit((X - self.mu) / self.sd, y)
        return self

    def score(self, text, lang=None) -> float:
        import numpy as np
        x = (self._matrix([text], [lang]) - self.mu) / self.sd
        return float(self.clf.predict_proba(x)[0][1])
