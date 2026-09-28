"""Budget Safety Guard and Expense Tracking System for IndraLLM.

Enforces absolute budget caps:
- HARD CEILING: $10.00 USD
- TARGET CEILING: $5.00 USD

Before any API call or experiment run:
1. Estimate input/output tokens and cost.
2. Verify that current_spend + estimated_cost <= HARD_CEILING.
3. If exceeded, immediately aborts execution with BudgetExceededError.
4. Logs all estimates and actual expenditures to research/BUDGET.md and data/budget_ledger.json.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from indrallm.config import PROJECT_ROOT

HARD_BUDGET_CEILING_USD = 10.00
TARGET_BUDGET_CEILING_USD = 5.00
LEDGER_PATH = PROJECT_ROOT / "data" / "budget_ledger.json"
BUDGET_MD_PATH = PROJECT_ROOT / "research" / "BUDGET.md"

# Standard pricing rates per 1M tokens (USD)
TOKEN_PRICING_PER_MILLION = {
    "groq:llama-3.1-8b-instant": {"input": 0.05, "output": 0.08},
    "groq:llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79},
    "groq:qwen/qwen3.6-27b": {"input": 0.35, "output": 0.40},
    "groq:openai/gpt-oss-20b": {"input": 0.30, "output": 0.35},
    "google:gemini-2.5-flash": {"input": 0.075, "output": 0.30, "free_tier_safe": True},
    "google:gemini-2.5-flash-lite": {"input": 0.0375, "output": 0.15, "free_tier_safe": True},
    "local:sarvam-2b-v0.5": {"input": 0.0, "output": 0.0},
    "local:ai4bharat/IndicBERTv2-MLM-only": {"input": 0.0, "output": 0.0},
    "local:xlm-roberta-base": {"input": 0.0, "output": 0.0},
}


class BudgetExceededError(RuntimeError):
    """Raised when an operation would violate the strict budget ceiling."""


@dataclass
class CostEstimate:
    experiment_id: str
    provider: str
    model: str
    estimated_calls: int
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_cost_usd: float
    current_cumulative_spend: float
    remaining_budget_usd: float
    approved: bool
    timestamp: str


def _load_ledger() -> dict[str, Any]:
    if not LEDGER_PATH.exists():
        LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
        initial = {
            "hard_ceiling_usd": HARD_BUDGET_CEILING_USD,
            "target_ceiling_usd": TARGET_BUDGET_CEILING_USD,
            "cumulative_spend_usd": 0.0,
            "transactions": [],
            "estimates": [],
        }
        with LEDGER_PATH.open("w", encoding="utf-8") as f:
            json.dump(initial, f, indent=2)
        return initial
    with LEDGER_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_ledger(ledger: dict[str, Any]) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER_PATH.open("w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2)
    _sync_budget_markdown(ledger)


def _sync_budget_markdown(ledger: dict[str, Any]) -> None:
    """Keep research/BUDGET.md synchronized with current expenditures."""
    cum_spend = ledger.get("cumulative_spend_usd", 0.0)
    rem_budget = HARD_BUDGET_CEILING_USD - cum_spend
    txs = ledger.get("transactions", [])

    lines = [
        "# IndraLLM — Experiment Budget & API Spend Ledger",
        "",
        f"**Last Updated:** {datetime.now(timezone.utc).isoformat()}",
        f"**Hard Budget Ceiling:** ${HARD_BUDGET_CEILING_USD:.2f} USD",
        f"**Target Spend Ceiling:** ${TARGET_BUDGET_CEILING_USD:.2f} USD",
        f"**Current Cumulative Spend:** **${cum_spend:.4f} USD**",
        f"**Remaining Usable Budget:** **${rem_budget:.4f} USD**",
        "",
        "---",
        "",
        "## Transaction Ledger",
        "",
        "| Timestamp | Exp ID | Provider | Model | Calls | Input Tokens | Output Tokens | Cost (USD) | Notes |",
        "|---|---|---|---|---|---|---|---|---|",
    ]

    if not txs:
        lines.append("| - | - | - | - | 0 | 0 | 0 | $0.0000 | Initialized ledger. No paid calls executed yet. |")
    else:
        for tx in txs:
            lines.append(
                f"| {tx.get('timestamp', '')[:19]} | {tx.get('experiment_id', '')} | "
                f"{tx.get('provider', '')} | {tx.get('model', '')} | {tx.get('calls', 0)} | "
                f"{tx.get('input_tokens', 0)} | {tx.get('output_tokens', 0)} | "
                f"${tx.get('cost_usd', 0.0):.4f} | {tx.get('notes', '')} |"
            )

    lines.extend([
        "",
        "---",
        "",
        "## Budget Guard Protocol",
        "1. Every paid API batch requires `estimate_cost()` and `check_budget_approval()` prior to invocation.",
        "2. If `cumulative_spend + estimated_cost > $10.00`, the system raises `BudgetExceededError` and aborts.",
        "3. Local, zero-cost (free tier / local weights) models are prioritized at all times.",
    ])

    BUDGET_MD_PATH.parent.mkdir(parents=True, exist_ok=True)
    BUDGET_MD_PATH.write_text("\n".join(lines), encoding="utf-8")


def estimate_cost(
    experiment_id: str,
    provider: str,
    model: str,
    num_calls: int,
    avg_input_tokens: int = 120,
    avg_output_tokens: int = 150,
    is_free_tier: bool = False,
) -> CostEstimate:
    """Calculate projected cost for a proposed API run."""
    ledger = _load_ledger()
    current_spend = ledger.get("cumulative_spend_usd", 0.0)

    key = f"{provider}:{model}"
    rates = TOKEN_PRICING_PER_MILLION.get(key, {"input": 0.50, "output": 1.00})

    if is_free_tier or rates.get("input", 0.0) == 0.0:
        est_cost = 0.0
    else:
        in_cost = (num_calls * avg_input_tokens / 1_000_000) * rates["input"]
        out_cost = (num_calls * avg_output_tokens / 1_000_000) * rates["output"]
        est_cost = in_cost + out_cost

    approved = (current_spend + est_cost) <= HARD_BUDGET_CEILING_USD
    remaining = max(0.0, HARD_BUDGET_CEILING_USD - (current_spend + est_cost))

    estimate = CostEstimate(
        experiment_id=experiment_id,
        provider=provider,
        model=model,
        estimated_calls=num_calls,
        estimated_input_tokens=num_calls * avg_input_tokens,
        estimated_output_tokens=num_calls * avg_output_tokens,
        estimated_cost_usd=round(est_cost, 5),
        current_cumulative_spend=round(current_spend, 5),
        remaining_budget_usd=round(remaining, 5),
        approved=approved,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    ledger["estimates"].append(asdict(estimate))
    _save_ledger(ledger)
    return estimate


def assert_budget_approved(estimate: CostEstimate) -> None:
    """Ensure that the proposed run does not breach the budget cap."""
    if not estimate.approved:
        raise BudgetExceededError(
            f"ABORT: Run {estimate.experiment_id} projected cost ${estimate.estimated_cost_usd:.4f} "
            f"exceeds remaining budget ${HARD_BUDGET_CEILING_USD - estimate.current_cumulative_spend:.4f} "
            f"(Hard Ceiling: ${HARD_BUDGET_CEILING_USD:.2f})."
        )


def record_spend(
    experiment_id: str,
    provider: str,
    model: str,
    calls: int,
    input_tokens: int,
    output_tokens: int,
    cost_usd: float,
    notes: str = "",
) -> float:
    """Record verified expense in the ledger."""
    ledger = _load_ledger()
    ledger["cumulative_spend_usd"] = round(ledger.get("cumulative_spend_usd", 0.0) + cost_usd, 5)
    tx = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "experiment_id": experiment_id,
        "provider": provider,
        "model": model,
        "calls": calls,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": round(cost_usd, 5),
        "notes": notes,
    }
    ledger["transactions"].append(tx)
    _save_ledger(ledger)
    return ledger["cumulative_spend_usd"]


def get_budget_status() -> dict[str, Any]:
    """Retrieve current spend and remaining balance."""
    ledger = _load_ledger()
    spend = ledger.get("cumulative_spend_usd", 0.0)
    return {
        "hard_ceiling_usd": HARD_BUDGET_CEILING_USD,
        "target_ceiling_usd": TARGET_BUDGET_CEILING_USD,
        "cumulative_spend_usd": spend,
        "remaining_budget_usd": round(HARD_BUDGET_CEILING_USD - spend, 4),
        "target_remaining_usd": round(TARGET_BUDGET_CEILING_USD - spend, 4),
    }


if __name__ == "__main__":
    _sync_budget_markdown(_load_ledger())
    print("Budget Guard initialized:", get_budget_status())
