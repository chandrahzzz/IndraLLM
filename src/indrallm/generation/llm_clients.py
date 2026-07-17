"""Unified interface over the LLM providers used to generate candidate answers.

Each client exposes `generate(prompt: str) -> str`. API clients run on a laptop;
`hf_local` clients need a GPU (run on Colab/Kaggle, see docs/COLAB.md).
"""

from __future__ import annotations

from indrallm.config import CFG, api_key

SYSTEM_PROMPT = (
    "You are a helpful assistant answering questions from Indian users. "
    "Questions may mix an Indian language with English (code-switching). "
    "Answer accurately and concisely in the same mixed style the user used."
)


class OpenAIClient:
    def __init__(self, model: str):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key("OPENAI_API_KEY"))
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


class AnthropicClient:
    def __init__(self, model: str):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key("ANTHROPIC_API_KEY"))
        self.model = model

    def generate(self, prompt: str) -> str:
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=CFG["generation"]["max_tokens"],
            temperature=CFG["generation"]["temperature"],
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in resp.content if b.type == "text")


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


class HFLocalClient:
    """Local HuggingFace causal LM. Needs GPU for reasonable speed."""

    def __init__(self, model: str):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model)
        self.model = AutoModelForCausalLM.from_pretrained(
            model, torch_dtype=torch.bfloat16, device_map="auto")
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
    "openai": OpenAIClient,
    "anthropic": AnthropicClient,
    "google": GoogleClient,
    "hf_local": HFLocalClient,
}


def get_client(name: str):
    """Build a client from a `generation.models` entry in config.yaml."""
    spec = CFG["generation"]["models"][name]
    return PROVIDERS[spec["provider"]](spec["model"])
