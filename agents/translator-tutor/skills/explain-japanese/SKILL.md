---
name: explain-japanese
description: explain japanese text in textbook style when prefixed with one or two question marks, optionally with a locale prefix like zh or zh-tw to switch the explanation language. one question mark means concise; two means detailed grammar, vocabulary, nuance, and example usage.
when-to-use: the user message begins with `?` or `??`, optionally preceded by a locale tag like zh / zh-tw.
allowed-tools: []
---

# Explain Japanese Content

## Command syntax

```
? 日本語での内容...         → concise English explanation
?? 日本語での内容...        → detailed English explanation
zh? 日本語での内容...       → concise Traditional Chinese explanation
zh?? 日本語での内容...      → detailed Traditional Chinese explanation
zh-tw? 日本語での内容...    → concise Traditional Chinese (Taiwan) explanation
```

## Behavior

- `?` → concise: meaning, brief breakdown, nuance.
- `??` → detailed: meaning, grammar, vocabulary, nuance and usage, similar examples.
- Without a locale prefix, explain in English. With `zh` / `zh-tw`, explain in Traditional Chinese.
- For image input, explain the most prominent Japanese text visible.

## Concise output (`?`)

```markdown
Meaning: [natural translation]

Breakdown:
- [word or phrase]: [meaning and role]
- [grammar point]: [brief explanation]

Nuance: [tone, context, implication]
```

## Detailed output (`??`)

```markdown
Meaning: [natural translation]

Grammar:
- [structure]: [textbook-style explanation]

Vocabulary:
- [term]: [reading if useful, meaning, nuance]

Nuance and usage:
[register, context, possible interpretations]

Similar examples:
- [Japanese example] — [translation]
```

## Examples

Input:
```
? 彼は何食わぬ顔で戻ってきた。
```
Explain `何食わぬ顔`, the role of `で`, and the nuance of acting as if nothing happened.

Input:
```
zh?? 腑に落ちない説明だった。
```
Explain in Traditional Chinese, including the reading `腑（ふ）`, the idiom `腑に落ちない`, and usage nuance.
