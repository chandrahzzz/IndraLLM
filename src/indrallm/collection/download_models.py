"""Download the fastText language-ID model (lid.176.bin, ~130 MB) to project root."""

from __future__ import annotations

import sys

import requests
from tqdm import tqdm

from indrallm.config import PROJECT_ROOT, CFG

URL = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"


def main() -> None:
    dest = PROJECT_ROOT / CFG["paths"]["fasttext_model"]
    if dest.exists():
        print(f"already present: {dest}")
        return
    resp = requests.get(URL, stream=True, timeout=60)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    with open(dest, "wb") as f, tqdm(total=total, unit="B", unit_scale=True) as bar:
        for chunk in resp.iter_content(chunk_size=1 << 20):
            f.write(chunk)
            bar.update(len(chunk))
    print(f"saved {dest}")


if __name__ == "__main__":
    sys.exit(main())
