import os
import json
import hashlib
import pandas as pd
import numpy as np

cand_dir = 'data/questions/IndraLLM-CS-v1.1-CANDIDATE'
print("Checking directory:", cand_dir)

manifest_path = os.path.join(cand_dir, 'data_manifest.json')
with open(manifest_path, 'r', encoding='utf-8') as f:
    manifest = json.load(f)

print(f"Manifest: groups={manifest.get('semantic_groups')}, prompts={manifest.get('condition_prompts')}")

for f, chk in manifest.get('checksums', {}).items():
    p = os.path.join(cand_dir, f)
    with open(p, 'rb') as fp:
        actual = hashlib.sha256(fp.read()).hexdigest()
    assert actual == chk, f"Checksum mismatch in {f}"
    print(f"Verified {f}: {chk[:16]}... OK")

dfs = {}
for split in ['development', 'validation', 'test_id', 'test_ood']:
    csv_p = os.path.join(cand_dir, f"{split}.csv")
    df = pd.read_csv(csv_p)
    dfs[split] = df
    print(f"{split}: rows={len(df)}, unique_semantic_ids={df['semantic_id'].nunique()}")
    print("  Languages:", dict(df['language'].value_counts()))
    print("  Conditions:", dict(df['condition'].value_counts()))
    print("  Domains:", dict(df['domain'].value_counts()))
    print("  Template Families:", dict(df['template_family_id'].value_counts()))

# Disjointness checks
s_dev = set(dfs['development']['semantic_id'])
s_val = set(dfs['validation']['semantic_id'])
s_tid = set(dfs['test_id']['semantic_id'])
s_tood = set(dfs['test_ood']['semantic_id'])

assert len(s_dev & s_val) == 0, 'Dev/Val overlap'
assert len(s_dev & s_tid) == 0, 'Dev/Test-ID overlap'
assert len(s_dev & s_tood) == 0, 'Dev/Test-OOD overlap'
assert len(s_val & s_tid) == 0, 'Val/Test-ID overlap'
assert len(s_val & s_tood) == 0, 'Val/Test-OOD overlap'
assert len(s_tid & s_tood) == 0, 'Test-ID/Test-OOD overlap'
print("All partition semantic_ids strictly disjoint!")

# 5 conditions per semantic group
for split, df in dfs.items():
    grp_counts = df.groupby('semantic_id')['condition'].nunique()
    assert (grp_counts == 5).all(), f"Incomplete condition count in {split}"
    grp_rows = df.groupby('semantic_id').size()
    assert (grp_rows == 5).all(), f"Row count per semantic_id != 5 in {split}"
print("All groups contain exactly 5 representations within their assigned partition!")
