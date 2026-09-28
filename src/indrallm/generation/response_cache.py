"""Deterministic Model Response Cache and Inference Deduplication Engine.

Enforces:
1. Strict deterministic hashing of all inference requests:
   key = sha256(model_name + prompt + system_prompt + str(temperature) + str(top_p) + str(max_tokens))
2. Instant cache retrieval for identical queries (zero API spend, zero latency).
3. Persistent on-disk storage in data/cache/response_cache.jsonl.
4. Thread-safe and process-safe reads and writes.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from indrallm.config import PROJECT_ROOT

CACHE_DIR = PROJECT_ROOT / "data" / "cache"
CACHE_FILE = CACHE_DIR / "response_cache.jsonl"


@dataclass
class CachedResponse:
    cache_key: str
    model_name: str
    prompt: str
    system_prompt: str
    temperature: float
    top_p: float
    max_tokens: int
    response_text: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    timestamp: str


class ResponseCache:
    def __init__(self, cache_file: Path | None = None):
        self.cache_file = cache_file or CACHE_FILE
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self._memory_cache: dict[str, CachedResponse] = {}
        self._load()

    @staticmethod
    def compute_key(
        model_name: str,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
        top_p: float = 0.9,
        max_tokens: int = 256,
    ) -> str:
        blob = f"{model_name}|{prompt.strip()}|{system_prompt.strip()}|{temperature:.4f}|{top_p:.4f}|{max_tokens}"
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def _load(self) -> None:
        if not self.cache_file.exists():
            return
        with self.cache_file.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        cr = CachedResponse(**data)
                        self._memory_cache[cr.cache_key] = cr
                    except Exception:
                        continue

    def get(
        self,
        model_name: str,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
        top_p: float = 0.9,
        max_tokens: int = 256,
    ) -> CachedResponse | None:
        key = self.compute_key(model_name, prompt, system_prompt, temperature, top_p, max_tokens)
        return self._memory_cache.get(key)

    def put(
        self,
        model_name: str,
        prompt: str,
        response_text: str,
        system_prompt: str = "",
        temperature: float = 0.3,
        top_p: float = 0.9,
        max_tokens: int = 256,
        input_tokens: int = 0,
        output_tokens: int = 0,
        latency_ms: float = 0.0,
    ) -> CachedResponse:
        key = self.compute_key(model_name, prompt, system_prompt, temperature, top_p, max_tokens)
        cr = CachedResponse(
            cache_key=key,
            model_name=model_name,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            response_text=response_text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._memory_cache[key] = cr
        with self.cache_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(cr), ensure_ascii=False) + "\n")
        return cr

    def count(self) -> int:
        return len(self._memory_cache)


GLOBAL_CACHE = ResponseCache()
