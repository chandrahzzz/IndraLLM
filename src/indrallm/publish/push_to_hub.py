"""Publish the benchmark (and optionally the detector) to HuggingFace Hub.

Needs HF_TOKEN in .env with write access. Repo names come from config.yaml `hub`.

Usage:
    python -m indrallm.publish.push_to_hub                 # dataset only
    python -m indrallm.publish.push_to_hub --detector      # also push the model
    python -m indrallm.publish.push_to_hub --private       # private repo first
"""

from __future__ import annotations

import argparse

import pandas as pd

from indrallm.config import CFG, api_key, path


def push_dataset(private: bool) -> None:
    from datasets import Dataset, DatasetDict

    splits = {}
    for name in ("train", "val", "test"):
        f = path("final") / f"{name}.csv"
        if not f.exists():
            raise SystemExit(f"{f} missing — run aggregate_labels first")
        df = pd.read_csv(f)
        splits["validation" if name == "val" else name] = Dataset.from_pandas(df)
    ds = DatasetDict(splits)
    repo = CFG["hub"]["dataset_repo"]
    ds.push_to_hub(repo, token=api_key("HF_TOKEN"), private=private)
    print(f"dataset pushed -> https://huggingface.co/datasets/{repo}")


def push_detector(private: bool) -> None:
    from huggingface_hub import HfApi

    model_dir = path("models") / "indicbert-halludetect" / "best"
    if not model_dir.exists():
        raise SystemExit("detector not trained — run detection.train_indicbert first")
    repo = CFG["hub"]["detector_repo"]
    api = HfApi(token=api_key("HF_TOKEN"))
    api.create_repo(repo, repo_type="model", private=private, exist_ok=True)
    api.upload_folder(folder_path=str(model_dir), repo_id=repo, repo_type="model")
    print(f"model pushed -> https://huggingface.co/{repo}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--detector", action="store_true")
    ap.add_argument("--private", action="store_true")
    args = ap.parse_args()

    push_dataset(args.private)
    if args.detector:
        push_detector(args.private)


if __name__ == "__main__":
    main()
