# Colab — Train the IndraLLM Detector (copy-paste, cell by cell)

Trains the IndicBERT hallucination detector on your **judged** labels.
Runtime → Change runtime type → **T4 GPU** before you start.

You will upload 3 files from your laptop: `data/final/train.csv`, `val.csv`, `test.csv`
(the judge-labeled splits). Nothing else is needed.

---

### CELL 1 — check you have a GPU
```python
!nvidia-smi
```
Expect to see "Tesla T4". If it errors: Runtime → Change runtime type → T4 GPU.

---

### CELL 2 — get the code + install
```python
!git clone https://github.com/chandrahzzz/IndraLLM.git
%cd IndraLLM
!pip install -q -e .
!pip install -q "numpy<2" transformers datasets evaluate accelerate scikit-learn sentencepiece pandas
```
If the repo is private, replace the clone line with:
`!git clone https://<YOUR_GITHUB_TOKEN>@github.com/chandrahzzz/IndraLLM.git`

---

### CELL 3 — upload your judged splits
```python
from google.colab import files
import os, shutil
os.makedirs('data/final', exist_ok=True)
print("Pick train.csv, val.csv, test.csv from your laptop's data/final/ folder:")
up = files.upload()
for fn in up:
    shutil.move(fn, f'data/final/{fn}')
print("uploaded:", os.listdir('data/final'))
```
When the file picker opens, select all **three** CSVs at once.

---

### CELL 4 — sanity check the data
```python
import pandas as pd
for s in ['train', 'val', 'test']:
    d = pd.read_csv(f'data/final/{s}.csv')
    print(s, len(d), "rows,  hallucinated rate", round(d.label.mean(), 3),
          ",  cols ok:", all(c in d.columns for c in ['question','answer','label','language']))
```
Expect roughly: train 1454, val 312, test 312, rate ~0.09, cols ok: True.

---

### CELL 5 — (optional) 1-epoch smoke test first
```python
!python -m indrallm.detection.train_indicbert --no-wandb --epochs 1
```
Confirms the whole thing runs end-to-end in ~2-3 min before the full run.

---

### CELL 6 — full training run
```python
!python -m indrallm.detection.train_indicbert --no-wandb
```
Takes ~15-25 min on a T4 (5 epochs). At the end it prints:
- `== test set ==` with F1 and accuracy
- per-language F1 (ta / hi / te / bn / kn)

**Copy that output — those are your detector results.**

---

### CELL 7 — download the trained detector
```python
!cd models && zip -r -q indicbert-halludetect.zip indicbert-halludetect/best
from google.colab import files
files.download('models/indicbert-halludetect.zip')
```
Unzip into your laptop's `models/` folder to keep it.

---

## What to expect / how to read it

- **Class imbalance is real** (~9% hallucinated). Watch **F1 and per-language F1**, not accuracy — a model can get 91% accuracy by calling everything "correct" and be useless. F1 is the honest number.
- If F1 is low (say < 0.3): the 195 positives may be too few for a 5-way-balanced fine-tune. That's a real finding, not a failure — tell me and we adjust (class weights, threshold tuning, or more judged data).
- If F1 is decent (> 0.5): you have a working detector — the paper's headline detection result.

## After this
Bring the printed metrics back here. Next step is mitigation (teacher distillation) — but the detector number decides whether we even need the internal-probes path. One thing at a time.
