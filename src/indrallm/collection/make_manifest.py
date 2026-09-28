"""Generate data_manifest.json with SHA256 checksums and provenance metadata."""

import hashlib
import json
from pathlib import Path
from indrallm.config import PROJECT_ROOT


def make_manifest():
    p = PROJECT_ROOT / "data" / "questions" / "IndraLLM-CS-v1.0"
    manifest = {
        "dataset_version": "IndraLLM-CS-v1.0",
        "release_tag": "IndraLLM-CS-v1.0",
        "generation_date": "2026-09-29T00:28:09Z",
        "number_of_semantic_groups": 2000,
        "number_of_condition_prompts": 10000,
        "languages": ["hi", "ta", "te", "bn", "kn"],
        "domains": ["governance", "science", "agriculture", "history", "education", "public_health"],
        "conditions": ["A_EN", "B_NATIVE", "C_ROMAN", "D_CS", "E_MIXED_SCRIPT"],
        "validation_status": "FROZEN_VALIDATED",
        "code_commit": "282e4bdaa56be571a5697bba7671e22d29225ffe",
        "checksums": {},
    }
    for f in sorted(p.glob("*.*")):
        if f.name != "data_manifest.json":
            sha = hashlib.sha256(f.read_bytes()).hexdigest()
            manifest["checksums"][f.name] = sha

    out_file = p / "data_manifest.json"
    out_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"data_manifest.json created -> {out_file}")
    for k, v in manifest["checksums"].items():
        print(f"  {k}: {v[:16]}...")


if __name__ == "__main__":
    make_manifest()
