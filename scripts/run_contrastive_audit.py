import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Contrastive pairs testing negation, numbers, dates, quantifiers, polarity
contrastive_pairs = [
    {
        "category": "Negation",
        "sentence_A": "The scheme provides a subsidy to eligible small farmers.",
        "sentence_B": "The scheme does not provide a subsidy to eligible small farmers.",
        "inverted_meaning": True
    },
    {
        "category": "Quantifier (at least vs at most)",
        "sentence_A": "The applicant must own at least 2 hectares of cultivable land.",
        "sentence_B": "The applicant must own at most 2 hectares of cultivable land.",
        "inverted_meaning": True
    },
    {
        "category": "Temporal Scope (before vs after)",
        "sentence_A": "The registration deadline was completed before March 31, 2023.",
        "sentence_B": "The registration deadline was completed after March 31, 2023.",
        "inverted_meaning": True
    },
    {
        "category": "Numeric Magnitude",
        "sentence_A": "The annual financial assistance under the statutory clause is 6,000 rupees.",
        "sentence_B": "The annual financial assistance under the statutory clause is 60,000 rupees.",
        "inverted_meaning": True
    },
    {
        "category": "Exclusivity (only)",
        "sentence_A": "Only rural institutional accounts are eligible for interest subvention.",
        "sentence_B": "Rural and urban institutional accounts are eligible for interest subvention.",
        "inverted_meaning": True
    },
    {
        "category": "Comparator (more than vs less than)",
        "sentence_A": "The parameter threshold requires more than 50 units for compliance.",
        "sentence_B": "The parameter threshold requires less than 50 units for compliance.",
        "inverted_meaning": True
    }
]

print("=== CONTRASTIVE SEMANTIC EQUIVALENCE TEST ===")
for item in contrastive_pairs:
    tfidf = TfidfVectorizer(ngram_range=(1, 2))
    mat = tfidf.fit_transform([item['sentence_A'], item['sentence_B']])
    sim = cosine_similarity(mat[0:1], mat[1:2])[0][0]
    print(f"[{item['category']}]")
    print(f"  A: {item['sentence_A']}")
    print(f"  B: {item['sentence_B']}")
    print(f"  TF-IDF Cosine Similarity: {sim:.4f} (Inverted Meaning: {item['inverted_meaning']})")
    print("-" * 60)
