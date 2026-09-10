---
name: cost-aware-llm-pipeline
description: Cost optimization patterns for LLM API usage — model routing between local Docker Model Runner and Cloud LLMs, token budget tracking, retry logic, and prompt caching. Use when LLM spend needs to come down, or when routing tasks across model tiers and budgets.
metadata:
  origin: ECC (adapted for VeriScholar)
---

# Cost-Aware LLM Pipeline

Patterns for controlling LLM API costs while maintaining quality. Combines multi-tier model routing (Local Docker Model Runner vs. Cloud LLMs), budget tracking, retry logic, and prompt caching into a composable pipeline.

## When to Activate

- Routing inference requests between local Docker Model Runner and Cloud LLMs (OpenAI, Gemini)
- Processing batches of academic documents with varying reasoning complexity
- Staying within budget limits for API spend
- Optimizing cost without sacrificing grounding accuracy on complex synthesis tasks

## Core Concepts

### 1. Multi-Tier Model Routing (Local Zero-Cost vs. Cloud)

Automatically route routine tasks (summarization, keyword extraction, initial classification) to local Docker Model Runner (0 API cost), reserving cloud frontier models (`gpt-5.6-luna`, `claude-sonnet`) for deep cross-paper synthesis and complex reasoning.

```python
from enum import StrEnum

class ModelTier(StrEnum):
    LOCAL_DMR = "docker-model-runner"   # ai/smollm2, ai/llama3.2 - Free, 0ms network latency
    CLOUD_FAST = "gemini-1.5-flash"      # Fast, low-cost cloud extraction
    CLOUD_REASONING = "gpt-5.6-luna"     # Complex multi-paper synthesis & proof checking

def route_inference_request(
    prompt_token_count: int,
    requires_deep_reasoning: bool,
    force_local: bool = False,
) -> ModelTier:
    """Select the optimal model tier based on task complexity and budget."""
    if force_local or (prompt_token_count < 1000 and not requires_deep_reasoning):
        return ModelTier.LOCAL_DMR
    if requires_deep_reasoning or prompt_token_count > 8000:
        return ModelTier.CLOUD_REASONING
    return ModelTier.CLOUD_FAST
```

### 2. Immutable Cost Tracking

Track cumulative spend with frozen dataclasses. Each API call returns a new tracker — never mutates state.

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class CostRecord:
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float

@dataclass(frozen=True, slots=True)
class CostTracker:
    records: tuple[CostRecord, ...] = ()
    budget_limit_usd: float = 10.0

    @property
    def total_cost_usd(self) -> float:
        return sum(r.cost_usd for r in self.records)

    def record(self, model: str, input_tokens: int, output_tokens: int, cost_usd: float) -> "CostTracker":
        new_record = CostRecord(model, input_tokens, output_tokens, cost_usd)
        new_records = self.records + (new_record,)
        if sum(r.cost_usd for r in new_records) > self.budget_limit_usd:
            raise BudgetExceededError(f"Budget limit of ${self.budget_limit_usd} exceeded")
        return CostTracker(records=new_records, budget_limit_usd=self.budget_limit_usd)
```

### 3. Prompt Caching & Token Reduction
- Maintain deterministic system prompts at the top of context for KV cache reuse.
- Pre-filter retrieved chunks with BM25 / Reranker to keep context concise before sending to LLM.
- Redact redundant whitespace and repetitive bibliographic headers.
