"""Unified interface over the LLM providers used to generate candidate answers.

Each client exposes `generate(prompt: str) -> str`.
  - `google`   — Gemini free tier, runs on a laptop.
  - `groq`     — Groq-hosted open models (Llama-3, Gemma) over an OpenAI-compatible
    API; fast + very cheap, runs on a laptop (no GPU). Needs GROQ_API_KEY.
  - `hf_local` — local HF causal LM, 4-bit by default so a model fits a free Colab
    T4 (see docs/COLAB.md). Only for Indic models Groq doesn't host (Sarvam,
    Airavata). Load ONE per Colab session; restart the runtime between models.
"""

from __future__ import annotations

from indrallm.config import CFG, api_key

SYSTEM_PROMPT = (
    "You are a helpful assistant answering questions from Indian users. "
    "Questions may mix an Indian language with English (code-switching). "
    "Answer accurately and concisely in the same mixed style the user used."
)


class GoogleClient:
    def __init__(self, model: str):
        import google.generativeai as genai
        genai.configure(api_key=api_key("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(model, system_instruction=SYSTEM_PROMPT)

    def generate(self, prompt: str) -> str:
        resp = self.model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": CFG["generation"]["max_tokens"],
                "temperature": CFG["generation"]["temperature"],
            },
        )
        return resp.text


class GroqClient:
    """Groq-hosted open models via the OpenAI-compatible endpoint. CPU-only laptop."""

    def __init__(self, model: str):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key("GROQ_API_KEY"),
                             base_url="https://api.groq.com/openai/v1")
        self.model = model

    def generate(self, prompt: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            max_tokens=CFG["generation"]["max_tokens"],
            temperature=CFG["generation"]["temperature"],
            messages=[{"role": "system", "content": SYSTEM_PROMPT},
                      {"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content or ""


class HFLocalClient:
    """Local HuggingFace causal LM. Needs GPU; 4-bit (config generation.load_in_4bit)."""

    def __init__(self, model: str):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        kwargs: dict = {"device_map": "auto"}
        if CFG["generation"].get("load_in_4bit"):
            from transformers import BitsAndBytesConfig
            kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16)
        else:
            kwargs["torch_dtype"] = torch.bfloat16
        self.model = AutoModelForCausalLM.from_pretrained(model, **kwargs)
        self.chat = self.tokenizer.chat_template is not None

    def generate(self, prompt: str) -> str:
        if self.chat:
            text = self.tokenizer.apply_chat_template(
                [{"role": "system", "content": SYSTEM_PROMPT},
                 {"role": "user", "content": prompt}],
                tokenize=False, add_generation_prompt=True)
        else:
            text = f"{SYSTEM_PROMPT}\n\nQuestion: {prompt}\nAnswer:"
        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)
        out = self.model.generate(
            **inputs,
            max_new_tokens=CFG["generation"]["max_tokens"],
            temperature=CFG["generation"]["temperature"],
            do_sample=CFG["generation"]["temperature"] > 0,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        return self.tokenizer.decode(out[0][inputs["input_ids"].shape[1]:],
                                     skip_special_tokens=True).strip()


PROVIDERS = {
    "google": GoogleClient,
    "groq": GroqClient,
    "hf_local": HFLocalClient,
}


def get_client(name: str):
    """Build a client from a `generation.models` entry in config.yaml."""
    spec = CFG["generation"]["models"][name]
    return PROVIDERS[spec["provider"]](spec["model"])
