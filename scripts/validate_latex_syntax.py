"""Phase 6 LaTeX Syntax, Structure, Reference, and Asset Validator."""

import re
from pathlib import Path

def validate_latex_file(tex_path: Path):
    print(f"\n=== VALIDATING {tex_path.name} ===")
    if not tex_path.exists():
        print(f"Error: {tex_path} does not exist.")
        return False
        
    text = tex_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    
    # 1. Check matching braces
    clean_text = re.sub(r'\\.', '', text)  # remove escaped characters
    clean_text = re.sub(r'%.*', '', clean_text)  # remove comments
    open_braces = clean_text.count('{')
    close_braces = clean_text.count('}')
    print(f"Braces balance: open={open_braces}, close={close_braces}")
    if open_braces != close_braces:
        print(f"  [ERROR] Unbalanced curly braces! Difference: {open_braces - close_braces}")
    else:
        print("  Braces are perfectly balanced.")
        
    # 2. Check matching environments
    env_begins = re.findall(r'\\begin\{([^}]+)\}', text)
    env_ends = re.findall(r'\\end\{([^}]+)\}', text)
    print(f"Environments: begins={len(env_begins)}, ends={len(env_ends)}")
    if env_begins != env_ends[::-1] and sorted(env_begins) != sorted(env_ends):
        print(f"  [ERROR] Environment mismatch! Begins: {sorted(env_begins)} vs Ends: {sorted(env_ends)}")
    else:
        print("  All LaTeX environments match.")

    # 3. Check \input{} files
    inputs = re.findall(r'\\input\{([^}]+)\}', text)
    for inp in inputs:
        inp_p = tex_path.parent / inp
        if not inp_p.suffix:
            inp_p = inp_p.with_suffix(".tex")
        if inp_p.exists():
            print(f"  [OK] \\input{{{inp}}} exists ({inp_p.name})")
        else:
            print(f"  [ERROR] \\input{{{inp}}} NOT FOUND at {inp_p}")

    # 4. Check \includegraphics{} files
    figs = re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', text)
    for fig in figs:
        fig_p = tex_path.parent / fig
        if fig_p.exists():
            print(f"  [OK] \\includegraphics{{{fig}}} exists ({fig_p.stat().st_size} bytes)")
        else:
            print(f"  [ERROR] \\includegraphics{{{fig}}} NOT FOUND at {fig_p}")

    # 5. Check labels and refs
    labels = set(re.findall(r'\\label\{([^}]+)\}', text))
    # Also collect labels in input files
    for inp in inputs:
        inp_p = tex_path.parent / inp
        if not inp_p.suffix:
            inp_p = inp_p.with_suffix(".tex")
        if inp_p.exists():
            inp_labels = re.findall(r'\\label\{([^}]+)\}', inp_p.read_text(encoding="utf-8"))
            labels.update(inp_labels)
            
    refs = set(re.findall(r'\\(?:ref|eqref)\{([^}]+)\}', text))
    missing_refs = refs - labels
    if missing_refs:
        print(f"  [WARNING] Unresolved references: {missing_refs}")
    else:
        print(f"  All {len(refs)} \\ref{{}} cross-references resolve to existing labels.")

    return True

if __name__ == "__main__":
    for f in [Path("paper/main_anonymous.tex"), Path("paper/main_camera_ready.tex")]:
        validate_latex_file(f)
