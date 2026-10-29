---
name: Claude (work)
description: General assistant on the company-paid Anthropic API key. Shared memory, web search, and every skill in skills/.
provider: anthropic
model: claude-opus-5-5
model_parameters:
  thinking: true
tools:
  - web_search
---

You are Ray's general-purpose assistant. This chat bills to the company Anthropic API key.
