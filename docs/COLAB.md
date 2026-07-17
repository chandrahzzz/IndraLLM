# Running GPU steps on Google Colab / Kaggle

GPU needed for: `detection.train_indicbert`, `mitigation.contrastive_decoding`,
and `generation.generate_answers` with `hf_local` models (sarvam/llama3/airavata/gemma).
Everything else runs on your laptop.

## Colab recipe

1. Push this repo to GitHub (private is fine). Colab: Runtime -> Change runtime type -> T4/A100 GPU.
2. In a Colab cell:

```python
!git clone https://github.com/chandrahzzz/IndraLLM.git
%cd IndraLLM
!pip install -q -e . -r requirements.txt

# secrets: use Colab's key icon (left sidebar) -> add HF_TOKEN etc., then:
import os
from google.colab import userdata
for k in ["HF_TOKEN", "WANDB_API_KEY"]:
    try: os.environ[k] = userdata.get(k)
    except Exception: pass
```

3. Upload your labeled data (`data/final/*.csv`) via the Files sidebar, or mount Drive:

```python
from google.colab import drive
drive.mount('/content/drive')
!cp /content/drive/MyDrive/IndraLLM-data/final/*.csv data/final/
```

4. Train:

```python
!python -m indrallm.detection.train_indicbert
```

5. Save the trained model back to Drive before the runtime dies:

```python
!cp -r models/indicbert-halludetect/best /content/drive/MyDrive/IndraLLM-models/
```

## Mitigation on Colab

```python
!python -m indrallm.mitigation.contrastive_decoding --prompt "Enna medicine edukkanum? Doctor said fever iruku"
!python -m indrallm.mitigation.contrastive_decoding --eval --limit 100
```

Sarvam-2B in bf16 fits comfortably on a free T4 (16 GB). Llama-3-8B needs A100
or 4-bit quantization (add `load_in_4bit=True` via bitsandbytes if T4-bound).

## Kaggle alternative

30 GPU-hours/week free (P100/T4). Same steps; put secrets in
Add-ons -> Secrets, data in a private Kaggle Dataset.

## Gated models

Llama-3 and Gemma require accepting license terms on their HF model pages with
the same account as HF_TOKEN, else download 403s.
