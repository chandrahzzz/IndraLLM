# Colab — Teacher Distillation to Reduce Sarvam-2B Hallucination (copy-paste)

Fine-tunes Sarvam-2B (LoRA, 4-bit) on clean **code-switched, correct** teacher
answers (from llama-3.3-70b), then measures the hallucination-rate drop vs the
untuned base model. Runtime → Change runtime type → **T4 GPU**.

You upload 2 files from your laptop:
`data/final/distill_set.csv` (teacher targets) and `data/final/test.csv`.

---

### CELL 1 — GPU + clone + install
```python
!nvidia-smi
!git clone https://github.com/chandrahzzz/IndraLLM.git
%cd IndraLLM
!pip install -q -e .
!pip install -q transformers datasets accelerate peft bitsandbytes sentencepiece openai
```

---

### CELL 2 — RESTART (do not skip)
**Runtime → Restart session**, then:
```python
%cd /content/IndraLLM
```

---

### CELL 3 — upload the two CSVs
```python
from google.colab import files
import os, shutil
os.makedirs('data/final', exist_ok=True)
print("Pick distill_set.csv and test.csv from your laptop data/final/:")
up = files.upload()
for fn in up:
    shutil.move(fn, f'data/final/{fn}')
print("in data/final:", os.listdir('data/final'))
```

---

### CELL 4 — set your Groq key (for judging in eval)
Not stored in the notebook — typed at runtime:
```python
import getpass, os
os.environ['GROQ_API_KEY'] = getpass.getpass('GROQ_API_KEY: ')
```

---

### CELL 5 — train the LoRA distillation adapter
```python
!python -m indrallm.mitigation.distill --train
```
~10-20 min on a T4. Prints `distilling on N teacher targets ...` then loss.
Saves the adapter to `models/sarvam-distill/adapter`.

---

### CELL 6 — evaluate: baseline vs distilled, judged
```python
!python -m indrallm.mitigation.distill --eval --limit 100
```
Generates answers from base Sarvam and distilled Sarvam on ~100 test questions,
judges both with Groq, and prints:
```
== hallucination rate (lower = better) ==
  baseline : XX%
  distilled: YY%
  reduction: -ZZ% relative
per-language hallucination rate: ...
```
That reduction number is the mitigation result. `--limit 100` keeps it fast +
cheap; drop it to run the full test set.

---

### CELL 7 — save the adapter to Google Drive
The adapter is small (~10-30 MB — LoRA, not the full model), so browser download
is fine, but Drive is safer:
```python
from google.colab import drive
drive.mount('/content/drive')
!cp -r models/sarvam-distill/adapter "/content/drive/MyDrive/sarvam-distill-adapter"
print("saved -> MyDrive/sarvam-distill-adapter")
```

---

## How to read it
- **reduction > 0** (distilled hallucinates less than baseline) = distillation worked.
  Target from the plan was ~25%+ relative reduction.
- Also eyeball a few answers in `data/answers/distill_comparison.csv` — the
  distilled ones should stay **code-switched** (not collapse to English) while
  being more accurate. If they went English, the teacher targets weren't
  code-switched enough — tell me.
- If reduction is ~0 or negative: honest finding. Likely the teacher targets are
  too few or too noisy; we judge the teacher answers first, or try more epochs.

Bring the reduction numbers back here.
