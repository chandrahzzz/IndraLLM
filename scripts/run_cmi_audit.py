import os
import pandas as pd
import numpy as np
from indrallm.collection.cmi import compute_cmi

cand_dir = 'data/questions/IndraLLM-CS-v1.1-CANDIDATE'
df = pd.read_csv(os.path.join(cand_dir, 'condition_prompts_7500.csv'))

output_lines = []
output_lines.append("=== CMI SUMMARY BY CONDITION ===")
for cond, grp in df.groupby('condition'):
    output_lines.append(f"{cond}: Mean CMI = {grp['measured_cmi'].mean():.2f}%, SD = {grp['measured_cmi'].std():.2f}%, Min = {grp['measured_cmi'].min():.2f}%, Max = {grp['measured_cmi'].max():.2f}%")
    output_lines.append(f"  Script transitions: Mean = {grp['script_transitions'].mean():.2f}")
    output_lines.append(f"  Language switches: Mean = {grp['language_switch_count'].mean():.2f}")
    output_lines.append(f"  English ratio: Mean = {grp['english_token_ratio'].mean():.4f}")
    output_lines.append(f"  Indic ratio: Mean = {grp['indic_token_ratio'].mean():.4f}")

output_lines.append("\n=== INSPECTION OF 20 EXAMPLES FROM B_NATIVE ===")
b_native_samples = df[df['condition'] == 'B_NATIVE'].head(20)
for idx, row in b_native_samples.iterrows():
    cmi_info = compute_cmi(row['prompt_text'])
    output_lines.append(f"[{row['semantic_id']}] Lang: {row['language']}, Entity: '{row['target_entity']}'")
    output_lines.append(f"  Text: {row['prompt_text']}")
    output_lines.append(f"  English tokens: {cmi_info['english_tokens']}, Indic tokens: {cmi_info['indic_tokens']}, Other/Punct: {cmi_info['other_tokens']}")
    output_lines.append(f"  Calculated CMI: {cmi_info['cmi']:.2f}% (Dataset recorded: {row['measured_cmi']:.2f}%)")
    output_lines.append("-" * 60)

with open('research/scratch_cmi_inspection.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(output_lines))
print("Inspection written to research/scratch_cmi_inspection.txt successfully!")
