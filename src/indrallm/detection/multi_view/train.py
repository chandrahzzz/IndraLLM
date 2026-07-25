"""Train the multi-view detector on cached features + judged labels.

Uses only the features the gate kept (pass --keep or point at docs/feature_analysis.md;
by default uses every numeric feature present, but you should gate first). Splits
by qid|model using data/final/{train,val,test}.csv when present, else a stratified
random split. Saves weights + a metrics summary.

Usage:
    python -m indrallm.detection.multi_view.train
    python -m indrallm.detection.multi_view.train --keep hsd_mean ae_mean cla_min uc_mean
"""

from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd

from indrallm.config import path
from indrallm.detection.multi_view.views import resolve_views
from indrallm.detection.multi_view.detector import build_detector, TYPES


def _split_ids(name: str) -> set[str] | None:
    p = path("final") / f"{name}.csv"
    if not p.exists():
        return None
    d = pd.read_csv(p)
    if "qid" not in d or "model" not in d:
        return None
    return set(d["qid"].astype(str) + "|" + d["model"].astype(str))


def _tensors(df: pd.DataFrame, views: dict, torch, dev):
    import numpy as np
    out = {}
    for v, cols in views.items():
        arr = df[cols].to_numpy(np.float32)
        mu, sd = arr.mean(0), arr.std(0) + 1e-6
        out[v] = torch.tensor((arr - mu) / sd, device=dev)
    return out


def main() -> None:
    import torch
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--keep", nargs="*", help="feature names to use (default: all present)")
    ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--lr", type=float, default=1e-3)
    args = ap.parse_args()

    fp = path("features") / "answer_features.parquet"
    if not fp.exists():
        print("no answer_features.parquet — run feature_cache first")
        return
    df = pd.read_parquet(fp).fillna(0.0)
    views = resolve_views(list(df.columns), args.keep)
    print("views:", {v: cols for v, cols in views.items()})

    tr_ids, va_ids = _split_ids("train"), _split_ids("val")
    if tr_ids and va_ids:
        train = df[df["qid_model"].isin(tr_ids)]
        val = df[df["qid_model"].isin(va_ids)]
    else:
        from sklearn.model_selection import train_test_split
        train, val = train_test_split(df, test_size=0.2, stratify=df["label"], random_state=42)
    print(f"train={len(train)} val={len(val)}  pos-rate train={train.label.mean():.1%}")

    dev = "cuda" if torch.cuda.is_available() else "cpu"
    Xtr = _tensors(train, views, torch, dev)
    Xva = _tensors(val, views, torch, dev)
    ytr = torch.tensor(train["label"].to_numpy(np.float32), device=dev)
    yva = val["label"].to_numpy()

    model = build_detector({v: len(c) for v, c in views.items()}).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    pos_w = torch.tensor([(ytr == 0).sum() / max((ytr == 1).sum(), 1)], device=dev)
    bce = torch.nn.BCELoss(reduction="none")

    from sklearn.metrics import roc_auc_score, average_precision_score
    best_ap, best_state = -1.0, None
    for ep in range(args.epochs):
        model.train()
        opt.zero_grad()
        prob, _, _ = model(Xtr)
        w = torch.where(ytr == 1, pos_w, torch.ones_like(ytr))
        loss = (bce(prob.clamp(1e-6, 1 - 1e-6), ytr) * w).mean()
        loss.backward()
        opt.step()
        if (ep + 1) % 10 == 0 or ep == args.epochs - 1:
            model.eval()
            with torch.no_grad():
                pv = model(Xva)[0].cpu().numpy()
            ap = average_precision_score(yva, pv) if len(set(yva)) > 1 else 0.0
            auc = roc_auc_score(yva, pv) if len(set(yva)) > 1 else 0.5
            print(f"ep{ep+1:3d} loss={loss.item():.4f} val AUC={auc:.3f} PR-AUC={ap:.3f}")
            if ap > best_ap:
                best_ap, best_state = ap, {k: v.cpu().clone() for k, v in model.state_dict().items()}

    if best_state:
        model.load_state_dict(best_state)
    outdir = path("models") / "multi_view_detector"
    outdir.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), outdir / "detector.pt")

    model.eval()
    with torch.no_grad():
        pv = model(Xva)[0].cpu().numpy()
    metrics = {"val_auc": float(roc_auc_score(yva, pv)) if len(set(yva)) > 1 else 0.5,
               "val_pr_auc": float(best_ap), "n_train": len(train), "n_val": len(val),
               "views": {v: c for v, c in views.items()}, "types": TYPES}
    # per-language AUC
    per_lang = {}
    for lang, g in val.assign(p=pv).groupby("language"):
        if g["label"].nunique() > 1:
            per_lang[str(lang)] = round(float(roc_auc_score(g["label"], g["p"])), 3)
    metrics["per_language_auc"] = per_lang
    (outdir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"saved -> {outdir/'detector.pt'}")
    print("per-language val AUC:", per_lang)


if __name__ == "__main__":
    main()
