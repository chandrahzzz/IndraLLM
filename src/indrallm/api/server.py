"""FastAPI server exposing the trained IndicBERT hallucination detector.

Endpoints:
    GET  /health           -> {"status": "ok", "model_loaded": bool}
    POST /detect           -> {"label": "correct"|"hallucinated", "hallucination_prob": float}
        body: {"question": "...", "answer": "..."}
    POST /detect/batch     -> [{...}, ...]   body: {"pairs": [{"question","answer"}, ...]}

Run (after training the detector):
    uvicorn indrallm.api.server:app --host 0.0.0.0 --port 8000
    # or: python -m indrallm.api.server

Docs UI at http://localhost:8000/docs
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from indrallm.config import CFG, path

MODEL_DIR = path("models") / "indicbert-halludetect" / "best"
MAX_LEN = CFG["detection"]["max_length"]

_state: dict = {"model": None, "tokenizer": None, "device": "cpu"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    if MODEL_DIR.exists():
        _state["tokenizer"] = AutoTokenizer.from_pretrained(str(MODEL_DIR))
        model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_DIR))
        model.eval()
        if torch.cuda.is_available():
            model.cuda()
            _state["device"] = "cuda"
        _state["model"] = model
    yield
    _state.update(model=None, tokenizer=None)


app = FastAPI(title="IndraLLM Hallucination Detector",
              description="Detects hallucinated answers to code-switched Indian-language questions.",
              lifespan=lifespan)


class Pair(BaseModel):
    question: str
    answer: str


class BatchRequest(BaseModel):
    pairs: list[Pair]


def _predict(pairs: list[Pair]) -> list[dict]:
    import torch

    if _state["model"] is None:
        raise HTTPException(503, "detector not trained — run detection.train_indicbert "
                                 f"(expected model at {MODEL_DIR})")
    tok, model = _state["tokenizer"], _state["model"]
    enc = tok([p.question for p in pairs], [p.answer for p in pairs],
              truncation=True, max_length=MAX_LEN, padding=True,
              return_tensors="pt").to(model.device)
    with torch.no_grad():
        probs = model(**enc).logits.softmax(-1)[:, 1].cpu().tolist()
    return [{"label": "hallucinated" if p >= 0.5 else "correct",
             "hallucination_prob": round(p, 4)} for p in probs]


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": _state["model"] is not None,
            "device": _state["device"]}


@app.post("/detect")
def detect(pair: Pair):
    return _predict([pair])[0]


@app.post("/detect/batch")
def detect_batch(req: BatchRequest):
    if not req.pairs:
        raise HTTPException(400, "pairs is empty")
    if len(req.pairs) > 256:
        raise HTTPException(400, "max 256 pairs per request")
    return _predict(req.pairs)


def main() -> None:
    import uvicorn
    uvicorn.run("indrallm.api.server:app",
                host=str(CFG["api"]["host"]), port=int(CFG["api"]["port"]))


if __name__ == "__main__":
    main()
