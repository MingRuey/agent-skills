---
name: translate-quoted
description: translate text wrapped in double quotes into a target language. without a prefix, target is english. with a locale prefix like zh, zh-tw, or any other locale tag, target is that locale. preserve source tone, register, and ambiguity. supports image input when the user types empty quotes or a pointer like `this`.
when-to-use: the user message contains a double-quoted block, optionally preceded by a short locale tag (e.g. zh, zh-tw, fr).
allowed-tools: []
---

# Translate Quoted Content

## Command syntax

```
"日本語での内容..."           → English
zh"日本語での内容..."          → Traditional Chinese (Taiwan-style default)
zh-tw"日本語での内容..."       → Traditional Chinese (Taiwan-style)
<locale>"日本語での内容..."    → target locale (e.g. <fr>"..." → French)
```

## Behavior

- Preserve source meaning, tone, register, and ambiguity.
- If the source has multiple plausible meanings, give the most likely translation first and briefly note alternatives.
- If the source is not Japanese, still translate to the command's target locale when the locale is clear.
- For Traditional Chinese output, default to Taiwan-style unless the user indicates another region.
- For image input (empty quotes `""` or a pointer like `this`), translate the most prominent text visible. Preserve labels, speech bubbles, signs, captions, and speaker attribution where helpful.

## Output format

```markdown
[translation]

Nuance: [brief note only when useful]
```

## Examples

Input:
```
"お世話になっております。資料をご確認いただけますでしょうか。"
```
Translate to English; note the polite business Japanese register.

Input:
```
zh"やむを得ない事情により、日程を変更させていただきます。"
```
Translate to Traditional Chinese while preserving the formal apologetic tone.
