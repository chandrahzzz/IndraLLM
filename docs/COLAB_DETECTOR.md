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
!pip install -q transformers datasets evaluate accelerate scikit-learn sentencepiece
```
If the repo is private, replace the clone line with:
`!git clone https://<YOUR_GITHUB_TOKEN>@github.com/chandrahzzz/IndraLLM.git`

---

### CELL 2.5 — RESTART (do not skip)

After the installs above, **Runtime → Restart session** (keeps your files, clears
stale numpy from memory). Mandatory: pip changed numpy on disk, but the kernel
still holds the old one — importing pandas before restarting throws
`numpy.dtype size changed`. Restart once here and it never happens again.

Then run:
```python
%cd /content/IndraLLM
```

> Never run `pip install --force-reinstall numpy pandas`. If Colab suggests it,
> ignore it — it makes the ABI error worse. The fix is always: restart the runtime.

---

### CELL 2.6 — patch the trainer (required — GitHub main is stale)

The cloned `train_indicbert.py` crashes on variable-length batches and, if you
patch just that, collapses to F1=0 (predicts "correct" for everything — labels
are ~10% positive). Both fixes exist only on a local branch that hasn't been
pushed, so patch them in here:
```python
f = 'src/indrallm/detection/train_indicbert.py'
s = open(f).read()
if 'DataCollatorWithPadding' not in s:
    # insert right after `from __future__ import annotations` (must stay first
    # statement in the file) — avoids matching the indented in-function import line
    s = s.replace(
        'from __future__ import annotations',
        'from __future__ import annotations\n\nfrom transformers import DataCollatorWithPadding', 1)
    s = s.replace(
        '    f1 = evaluate.load("f1")',
        '    import collections\n'
        '    counts = collections.Counter(train_ds["label"])\n'
        '    class_w = torch.tensor([1.0, counts[0] / max(counts[1], 1)])\n'
        '    print(f"class counts {dict(counts)} -> hallucinated weight {class_w[1]:.1f}")\n\n'
        '    class WeightedTrainer(Trainer):\n'
        '        def compute_loss(self, model, inputs, return_outputs=False, **kw):\n'
        '            labels = inputs.pop("labels")\n'
        '            out = model(**inputs)\n'
        '            loss = torch.nn.CrossEntropyLoss(weight=class_w.to(out.logits.device))(\n'
        '                out.logits, labels)\n'
        '            return (loss, out) if return_outputs else loss\n\n'
        '    f1 = evaluate.load("f1")')
    s = s.replace(
        '    trainer = Trainer(model=model, args=training_args, train_dataset=train_ds,\n'
        '                      eval_dataset=val_ds, compute_metrics=compute_metrics)',
        '    trainer = WeightedTrainer(model=model, args=training_args, train_dataset=train_ds,\n'
        '                              eval_dataset=val_ds, compute_metrics=compute_metrics,\n'
        '                              data_collator=DataCollatorWithPadding(tokenizer))')
    open(f, 'w').write(s)
    print("patched: padding collator + class-weighted loss ✓")
else:
    print("already patched")
```

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
Expect roughly: train 1852, val 394, test 403, rate ~0.10, cols ok: True.

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

### CELL 7 — save the trained detector to Google Drive

The model is ~1GB — the browser `files.download()` reliably fails/stalls at
that size. Save to Drive instead (this always works):
```python
from google.colab import drive
drive.mount('/content/drive')
!cp -r models/indicbert-halludetect/best "/content/drive/MyDrive/indicbert-detector"
print("saved to Google Drive -> MyDrive/indicbert-detector")
```
Grab it later from drive.google.com whenever you actually need the weights —
no rush, the important output is the printed metrics in Cell 6.

---

## What to expect / how to read it

- **Class imbalance is real** (~10% hallucinated). Watch **F1, AUC, and per-language F1**, not accuracy — a model can get ~90% accuracy by calling everything "correct" and be useless. Without the Cell 2.6 patch, this collapses to F1=0 with fake 90% accuracy — that is the exact failure mode being prevented here.
- Previous run (2078 rows, before this data-growth round): **AUC 0.717, F1 0.279** (tuned threshold), per-language AUC ta 0.86 / te 0.77 / bn 0.77 / kn 0.69 / hi 0.63. This run has more data, especially for hi and kn — compare against these numbers.
- If F1/AUC drop: more data isn't automatically better if the new positives are noisier — a real finding, tell me and we look at it.
- If hi/kn AUC improved specifically: the targeted data growth worked.

## After this
Bring the printed metrics back here. Next step is mitigation (teacher distillation) — but the detector number decides whether we even need the internal-probes path. One thing at a time.
