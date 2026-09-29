# IndraLLM — Experiment Budget & API Spend Ledger

**Last Updated:** 2026-09-29T05:06:53.741920+00:00
**Hard Budget Ceiling:** $10.00 USD
**Target Spend Ceiling:** $5.00 USD
**Current Cumulative Spend:** **$0.1040 USD**
**Remaining Usable Budget:** **$9.8960 USD**

---

## Transaction Ledger

| Timestamp | Exp ID | Provider | Model | Calls | Input Tokens | Output Tokens | Cost (USD) | Notes |
|---|---|---|---|---|---|---|---|---|
| 2026-09-28T18:58:50 | EXP-001 | groq | llama-3.1-8b | 100 | 2108 | 5000 | $0.0080 | Pilot inference over 100 prompts |
| 2026-09-28T18:59:03 | EXP-001 | groq | llama-3.1-8b | 100 | 2108 | 5000 | $0.0080 | Pilot inference over 100 prompts |
| 2026-09-28T18:59:08 | EXP-001 | groq | llama-3.3-70b | 100 | 2108 | 5000 | $0.0080 | Pilot inference over 100 prompts |
| 2026-09-28T18:59:49 | EXP-001 | groq | qwen-2.5-32b | 100 | 2108 | 27756 | $0.0080 | Pilot inference over 100 prompts |
| 2026-09-28T18:59:49 | EXP-001 | local | sarvam-2b-v0.5 | 100 | 2108 | 3538 | $0.0000 | Pilot inference over 100 prompts |
| 2026-09-28T19:00:07 | EXP-001 | groq | llama-3.1-8b | 50 | 1072 | 2500 | $0.0040 | Pilot inference over 50 prompts |
| 2026-09-28T19:00:07 | EXP-001 | groq | llama-3.3-70b | 50 | 1072 | 2500 | $0.0040 | Pilot inference over 50 prompts |
| 2026-09-28T19:00:08 | EXP-001 | groq | qwen-2.5-32b | 50 | 1072 | 13786 | $0.0040 | Pilot inference over 50 prompts |
| 2026-09-28T19:00:08 | EXP-001 | local | sarvam-2b-v0.5 | 50 | 1072 | 1802 | $0.0000 | Pilot inference over 50 prompts |
| 2026-09-28T19:22:08 | EXP-001 | groq | llama-3.1-8b | 250 | 5342 | 12500 | $0.0200 | Pilot inference over 250 prompts |
| 2026-09-28T19:22:13 | EXP-001 | groq | llama-3.3-70b | 250 | 5342 | 12500 | $0.0200 | Pilot inference over 250 prompts |
| 2026-09-28T19:22:44 | EXP-001 | groq | qwen-2.5-32b | 250 | 5342 | 69626 | $0.0200 | Pilot inference over 250 prompts |
| 2026-09-28T19:22:44 | EXP-001 | local | sarvam-2b-v0.5 | 250 | 5342 | 8952 | $0.0000 | Pilot inference over 250 prompts |

---

## Budget Guard Protocol
1. Every paid API batch requires `estimate_cost()` and `check_budget_approval()` prior to invocation.
2. If `cumulative_spend + estimated_cost > $10.00`, the system raises `BudgetExceededError` and aborts.
3. Local, zero-cost (free tier / local weights) models are prioritized at all times.