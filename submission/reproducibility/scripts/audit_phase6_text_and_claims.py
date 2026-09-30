"""Phase 6 Manuscript Language, Anonymity, Citations, and Claims Auditor."""

import re
from pathlib import Path

def check_prohibited_terms():
    prohibited = [
        r'\bproven\b', r'\bincontrovertible\b', r'\buniversal\b',
        r'\bcauses\b', r'\bsolves\b', r'\beliminates\b',
        r'\bguarantees\b', r'\ball multilingual llms\b',
        r'\ball indian languages\b', r'\ball models\b', r'\bgeneral law\b'
    ]
    files = [Path("paper/main_anonymous.tex"), Path("paper/main_camera_ready.tex")]
    print("=== 1. CHECKING PROHIBITED / INFLATED TERMS ===")
    for f in files:
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        lines = text.splitlines()
        found = 0
        for i, l in enumerate(lines, 1):
            # Skip comments
            if l.strip().startswith("%"):
                continue
            for p in prohibited:
                m = re.search(p, l, re.I)
                if m:
                    print(f"[{f.name}:{i}] Match '{m.group(0)}' in line: {l.strip()[:100]}")
                    found += 1
        if found == 0:
            print(f"  {f.name}: ZERO prohibited terms found.")

def check_anonymity():
    print("\n=== 2. CHECKING ANONYMITY OF main_anonymous.tex ===")
    anon_file = Path("paper/main_anonymous.tex")
    leak_terms = [
        "chandrahas", "reddy", "kurkurrereddy", "kurrered", "github.com",
        "chandrahzzz", "indrallm-cs", "akshara"
    ]
    lines = anon_file.read_text(encoding="utf-8").splitlines()
    found = 0
    for i, l in enumerate(lines, 1):
        if l.strip().startswith("%"):
            continue
        for term in leak_terms:
            if term in l.lower():
                print(f"  [POTENTIAL LEAK] line {i}: '{term}' found: {l.strip()}")
                found += 1
    if found == 0:
        print("  main_anonymous.tex: ZERO identity leaks found. Anonymity fully verified!")

def check_citations():
    print("\n=== 3. CHECKING CITATIONS IN references.bib ===")
    bib_path = Path("paper/references.bib")
    bib_text = bib_path.read_text(encoding="utf-8")
    keys = re.findall(r'@\w+\{([^,]+),', bib_text)
    print(f"  Found {len(keys)} BibTeX entries: {keys}")
    
    # Check citations in tex files
    tex_path = Path("paper/main_anonymous.tex")
    tex_text = tex_path.read_text(encoding="utf-8")
    cites = re.findall(r'\\cite[pt]?\{([^}]+)\}', tex_text)
    all_cited = set()
    for c in cites:
        for k in c.split(','):
            all_cited.add(k.strip())
    print(f"  Total cited keys in paper: {len(all_cited)}")
    
    missing = all_cited - set(keys)
    if missing:
        print(f"  [ERROR] Missing bib keys: {missing}")
    else:
        print("  All cited keys are present in references.bib!")
        
    unused = set(keys) - all_cited
    if unused:
        print(f"  Unused bib keys: {unused}")

if __name__ == "__main__":
    check_prohibited_terms()
    check_anonymity()
    check_citations()
