import os
import re
import json
import pandas as pd
import numpy as np
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

cand_dir = 'data/questions/IndraLLM-CS-v1.1-CANDIDATE'

splits = ['development', 'validation', 'test_id', 'test_ood']
dfs = {s: pd.read_csv(os.path.join(cand_dir, f"{s}.csv")) for s in splits}

def normalize(text):
    text = str(text).lower()
    text = re.sub(r'[^\w\s]', '', text)
    return ' '.join(text.split())

# Check exact and normalized question text overlaps across partition pairs
results = {}

split_pairs = [
    ('development', 'validation'),
    ('development', 'test_id'),
    ('development', 'test_ood'),
    ('validation', 'test_id'),
    ('validation', 'test_ood'),
    ('test_id', 'test_ood')
]

print("=== PARTITION PAIR LEAKAGE ANALYSIS ===")

for s1, s2 in split_pairs:
    df1 = dfs[s1]
    df2 = dfs[s2]
    
    # 1. Exact string match
    prompts1 = set(df1['prompt_text'])
    prompts2 = set(df2['prompt_text'])
    exact_matches = prompts1 & prompts2
    
    # 2. Normalized string match
    norm1 = {normalize(t) for t in prompts1}
    norm2 = {normalize(t) for t in prompts2}
    norm_matches = norm1 & norm2
    
    # 3. Entity overlap
    entities1 = set(df1['target_entity'].dropna())
    entities2 = set(df2['target_entity'].dropna())
    entity_matches = entities1 & entities2
    
    # 4. Evidence snippet overlap
    ev1 = set(df1['evidence_snippet'].dropna())
    ev2 = set(df2['evidence_snippet'].dropna())
    ev_matches = ev1 & ev2
    
    # 5. Evidence URL overlap
    url1 = set(df1['evidence_source_url'].dropna())
    url2 = set(df2['evidence_source_url'].dropna())
    url_matches = url1 & url2
    
    # 6. Template family overlap
    tf1 = set(df1['template_family_id'].dropna())
    tf2 = set(df2['template_family_id'].dropna())
    tf_matches = tf1 & tf2
    
    # 7. TF-IDF max cosine similarity
    tfidf = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    all_texts = list(df1['prompt_text']) + list(df2['prompt_text'])
    tfidf_mat = tfidf.fit_transform(all_texts)
    mat1 = tfidf_mat[:len(df1)]
    mat2 = tfidf_mat[len(df1):]
    
    # Sample 500 for fast sim calculation if large
    sub1 = mat1[:min(500, mat1.shape[0])]
    sub2 = mat2[:min(500, mat2.shape[0])]
    cos_sim = cosine_similarity(sub1, sub2)
    max_sim = float(cos_sim.max())
    mean_sim = float(cos_sim.mean())
    high_sim_count = int((cos_sim > 0.85).sum())

    results[f"{s1}_vs_{s2}"] = {
        'exact_matches': len(exact_matches),
        'norm_matches': len(norm_matches),
        'entity_overlap': len(entity_matches),
        'evidence_overlap': len(ev_matches),
        'url_overlap': len(url_matches),
        'tf_overlap': list(tf_matches),
        'max_tfidf_sim': round(max_sim, 4),
        'mean_tfidf_sim': round(mean_sim, 4),
        'pairs_sim_gt_85': high_sim_count
    }
    print(f"\n--- {s1} vs {s2} ---")
    print(f"Exact Matches: {len(exact_matches)}")
    print(f"Norm Matches: {len(norm_matches)}")
    print(f"Entity Overlap: {len(entity_matches)}")
    print(f"Evidence Snippet Overlap: {len(ev_matches)}")
    print(f"Evidence URL Overlap: {len(url_matches)}")
    print(f"Template Family Overlap: {len(tf_matches)} -> {sorted(list(tf_matches))}")
    print(f"Max TF-IDF Cosine Sim: {max_sim:.4f}, Mean: {mean_sim:.4f}, Count(Sim > 0.85): {high_sim_count}")

with open('research/scratch_leakage_results.json', 'w') as f:
    json.dump(results, f, indent=2)
