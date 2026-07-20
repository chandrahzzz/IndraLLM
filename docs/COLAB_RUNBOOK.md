# Colab Runbook — exact cells, in order

Everything below is copy-paste. Prereqs (once): accept Llama-3 + Gemma-2
licenses on HF with the same account as HF_TOKEN; add `HF_TOKEN` in Colab
Secrets (key icon); Runtime -> T4 GPU.

## Cell 0 — setup (run at the START of EVERY session)

```python
!git clone https://github.com/chandrahzzz/IndraLLM.git
%cd IndraLLM
!pip install -q -r requirements.txt -e .

import os
from google.colab import userdata
os.environ["HF_TOKEN"] = userdata.get("HF_TOKEN")
```

## Cell 0b — upload data (every session)

Repo data/ is git-ignored, so upload the needed CSVs via the Files sidebar
(folder icon -> drag files into the right dirs), or mount Drive:

```python
from google.colab import drive
drive.mount('/content/drive')
# after copying your local data/ to Drive as IndraLLM-data/
!cp -r /content/drive/MyDrive/IndraLLM-data/questions data/ 2>/dev/null
!cp -r /content/drive/MyDrive/IndraLLM-data/final data/ 2>/dev/null
!cp -r /content/drive/MyDrive/IndraLLM-data/answers data/ 2>/dev/null
```

Minimum needed per phase:
- PHASE A (generation): `data/questions/questions.csv`
- PHASE B (detector): `data/final/train.csv val.csv test.csv`
- PHASE C (mitigation): `data/questions/questions.csv` (+ PHASE B model for scoring later)

---

## PHASE A — generate answers (4 sessions, ONE model each)

Session 1:
```python
!python -m indrallm.generation.generate_answers --models sarvam
from google.colab import files; files.download("data/answers/sarvam.csv")
```

Then **Runtime -> Restart session** (clears VRAM), rerun Cell 0 + 0b, next model:

Session 2: same but `--models llama3` -> download `llama3.csv`
Session 3: same but `--models airavata` -> download `airavata.csv`
Session 4: same but `--models gemma` -> download `gemma.csv`

Put all 4 CSVs back into local `data/answers/` on the laptop.
(Interrupted? Just rerun — the script skips already-answered qids.)

---

## PHASE B — train detector (1 session, after laptop makes splits)

Needs `data/final/{train,val,test}.csv` uploaded (Cell 0b).

```python
!python -m indrallm.detection.train_indicbert
# save the model out before runtime dies:
!zip -r detector.zip models/indicbert-halludetect/best
from google.colab import files; files.download("detector.zip")
```

Unzip into local `models/indicbert-halludetect/best/`.

---

## PHASE C — mitigation (1 session)

```python
# baseline vs contrastive over benchmark questions (capped):
!python -m indrallm.mitigation.contrastive_decoding --eval --limit 1000
from google.colab import files; files.download("data/answers/mitigation_comparison.csv")
```

Optional (stronger paper) — QLoRA SFT, needs train.csv uploaded:
```python
!python -m indrallm.mitigation.lora_finetune
!zip -r sarvam-lora.zip models/sarvam-lora/adapter
from google.colab import files; files.download("sarvam-lora.zip")
```

---

## Back on the laptop after each phase

- After A: `python -m indrallm.annotation.auto_label` then
  `python -m indrallm.annotation.aggregate_labels --auto`
- After B: `python -m indrallm.evaluation.run_benchmark --detector --nli`
- After C: `python -m indrallm.evaluation.run_benchmark --mitigation`
- Finally: `python -m indrallm.publish.push_to_hub --detector` and
  `uvicorn indrallm.api.server:app --port 8000`

## OOM / errors

- OOM: confirm T4 selected; drop `detection.max_length` 256 -> 128 in config.yaml.
- 403 on llama3/gemma: license not accepted with the HF_TOKEN account.
- Gemini 429 on laptop scripts: daily free cap hit — rerun tomorrow, scripts resume.
