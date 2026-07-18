# Running GPU steps on Google Colab / Kaggle

GPU needed for: `detection.train_indicbert`, `mitigation.contrastive_decoding`,
`mitigation.lora_finetune`, and `generation.generate_answers` with `hf_local`
models (sarvam/llama3/airavata/gemma). Everything else runs on your laptop.

**Golden rule: ONE hf_local model per Colab session.** Generate answers, save
the CSV, Runtime -> Restart session (clears VRAM), then run the next model:

```bash
python -m indrallm.generation.generate_answers --models sarvam
# restart runtime
python -m indrallm.generation.generate_answers --models llama3
# restart runtime
python -m indrallm.generation.generate_answers --models airavata
# restart runtime
python -m indrallm.generation.generate_answers --models gemma
```

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

All hf_local + mitigation models load in **4-bit by default**
(`generation.load_in_4bit` / `mitigation.load_in_4bit` in config.yaml), so
Sarvam-2B (~7 GB) and even Llama-3-8B fit a free T4 (16 GB). If OOM anyway:
reduce `detection.max_length` 256 -> 128 for training.

## Kaggle alternative

30 GPU-hours/week free (P100/T4). Same steps; put secrets in
Add-ons -> Secrets, data in a private Kaggle Dataset.

## Gated models

Llama-3 and Gemma require accepting license terms on their HF model pages with
the same account as HF_TOKEN, else download 403s.
