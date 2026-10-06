# Self-Hosted / Open-Weight Models — Model Optimization Tactics

Self-hosted and open-weight models (Llama, Mistral, Qwen, DeepSeek, and similar served via vLLM,
TGI, Ollama, or custom infrastructure) need different tactics than frontier hosted chat models
because the operator controls the decoding stack directly and typically does not get automatic
prompt caching.

## Decoding Controls Still Matter

Unlike frontier chat-tuned models (where prompt structure and instruction clarity dominate
output quality and decoding parameters are mostly left at sane defaults), smaller or less
heavily RLHF'd open-weight models are noticeably more sensitive to decoding parameters:

- **Temperature**: lower (0.0–0.3) for deterministic/structured tasks (code generation, JSON
  extraction, classification); higher only for tasks that benefit from varied phrasing. Do not
  assume a default temperature tuned for a frontier chat model transfers cleanly.
- **Top-p / top-k**: tightening these can materially reduce malformed output and hallucinated
  tokens on smaller models in a way it rarely does on frontier models. Worth tuning per task
  rather than leaving at library defaults.
- **Repetition/frequency penalties**: smaller models are more prone to repetition loops in long
  outputs; tune these rather than truncating output and retrying.

Treat decoding-parameter tuning as a first-class part of the IDS determinism boundary for
self-hosted models. For frontier models, structure and prompt design alone usually get you
there.

## Smaller Context Windows Force More Aggressive Chunking

Many open-weight deployments run with meaningfully smaller effective context windows than
frontier hosted models (either genuinely smaller trained context, or deliberately capped for
memory/throughput reasons on self-hosted infrastructure). This means:

- Context-budget discipline (see main SKILL.md) is not optional headroom; it is a hard
  constraint. Reference material that would comfortably fit in a frontier model's context may
  need to be chunked, summarized, or fetched on demand instead of included wholesale.
- Long documents, large codebases, or extended conversation history need explicit chunking
  strategies (sliding window, hierarchical summarization, retrieval) rather than "just include
  it": that approach silently truncates or errors on smaller-context deployments.
- Test against the actual deployed context limit, not the model family's maximum theoretical
  context: quantized or throughput-optimized serving configurations often run with a reduced
  window.

## No Prompt Caching by Default

Most self-hosted serving stacks do not provide automatic prompt caching equivalent to hosted
frontier APIs (though some, like vLLM, support prefix caching if explicitly configured). Static-
content-first ordering matters even more here:

- If the serving stack supports prefix/KV caching (vLLM prefix caching, similar features
  elsewhere), structuring every request with an identical stable prefix is what makes that
  caching effective at all; inconsistent prefixes get zero benefit.
- Without any caching, every token of static content (system prompt, tool definitions, few-shot
  examples) is paid for on every single request. This raises the bar for justifying large
  always-included content even further than on cached frontier APIs. Trim aggressively, and
  prefer retrieval/on-demand injection over static inclusion of reference material.
- Batch inference patterns (processing many similar requests together) benefit disproportionately
  from a shared static prefix even without formal caching, since serving frameworks can often
  share KV computation across a batch when the prefix is identical.
