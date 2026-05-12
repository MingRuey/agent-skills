---
name: translator-tutor
description: japanese, english, and traditional chinese language helper for text or image-based translation, textbook-style explanation, and expression lookup. use when the user writes quoted japanese text for translation, attaches a picture with language-helper syntax, prefixes japanese text or image content with question marks for explanation, or uses locale-tagged requests to find equivalent expressions in another language. supports locale prefixes such as zh and zh-tw, nuance-aware translations, grammar and vocabulary explanations, visual text extraction, and kanji pronunciation guidance for japanese outputs.
---

# Japanese Translation Helper

## Overview

Use this skill to handle compact language-helper commands for Japanese translation, Japanese explanations, and equivalent-expression lookup across Japanese, English, Traditional Chinese, and other requested locales. The source content may be typed text or text visible in an attached image.

Prioritize the user's command syntax over conversational interpretation. Keep answers useful for a Japanese learner: clear, nuance-aware, and not overexplained unless the user uses `??` or asks for depth. For images, use visual understanding first; rely on OCR-style extraction only as needed.

## Command routing

Interpret the user's message by matching these patterns first.

### 1. Quoted content means translation

Use when the user enters double-quoted content:

```text
"日本語での内容..."
zh"日本語での内容..."
zh-tw"日本語での内容..."
<locale>"日本語での内容..."
```

Behavior:

- Without a locale prefix, translate Japanese content into English.
- With `zh` or `zh-tw`, translate into Traditional Chinese.
- With another locale prefix, translate into that locale's natural written form.
- Preserve the source meaning, tone, register, and ambiguity when possible.
- If the source has multiple plausible meanings, give the most likely translation first, then briefly note alternatives.
- If the source is not Japanese, still translate according to the command's target locale when clear.

Default output:

```markdown
[translation]

Nuance: [brief note only when useful]
```

For Traditional Chinese output, use natural Taiwan-style Traditional Chinese unless the user indicates another region.

### 2. Question mark prefix means Japanese explanation

Use when the user prefixes Japanese content with `?` or `??`:

```text
? 日本語での内容...
?? 日本語での内容...
zh? 日本語での内容...
zh?? 日本語での内容...
zh-tw? 日本語での内容...
```

Behavior:

- Explain the Japanese content like a language textbook.
- Without a locale prefix, explain in English.
- With `zh` or `zh-tw`, explain in Traditional Chinese.
- `?` means concise explanation.
- `??` means deeper explanation with more grammar, vocabulary, nuance, and example usage.

Default concise output for `?`:

```markdown
Meaning: [natural translation]

Breakdown:
- [word or phrase]: [meaning and role]
- [grammar point]: [brief explanation]

Nuance: [tone, context, implication]
```

Default detailed output for `??`:

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

### 3. Locale tag means expression learner

Use when the user prefixes content with a locale tag in angle brackets:

```text
<ja> 吃醋
<en> 楽あれば苦あり
<zh-tw> sour grapes
```

Behavior:

- Interpret the locale inside angle brackets as the target expression language.
- Find similar, equivalent, idiomatic, or natural ways to express the source meaning in the target locale.
- The source content can be in any language.
- Prefer expressions that sound natural to native speakers over literal translations.
- Provide multiple options when no single exact equivalent exists.
- Explain differences in nuance, register, and use case.

Default output:

```markdown
Best match: [target-language expression]

Other options:
- [expression] — [when to use it]
- [expression] — [when to use it]

Nuance: [how close the match is and what differs]
```

## Image-based input

The same command syntax applies when the user attaches a picture instead of, or in addition to, typed source text. Treat the attached image as the content source when the text after the command is absent, minimal, or clearly refers to the picture.

Supported image patterns include:

```text
? [attached image]
?? [attached image]
zh? [attached image]
<en> [attached image]
<ja> [attached image]
zh"" [attached image]
"" [attached image]
```

Behavior:

- For quoted translation commands with an image, translate the relevant visible text in the image. If the user typed empty quotes or only a short pointer such as `this`, use the image text as the quoted content.
- For `?` and `??` commands with an image, explain the relevant Japanese text visible in the image using the same concise or detailed explanation formats.
- For angle-bracket locale commands with an image, infer the source expression or phrase from the image and provide natural equivalent expressions in the target locale.
- If the target locale is provided outside the image, follow that locale even if the image contains another language.
- If the user marks, crops, circles, highlights, points to, or otherwise emphasizes part of the image, prioritize that part.
- If no region is marked, translate or explain the most prominent language content first. If multiple plausible regions exist, process as much readable text as practical, grouped by visible section.
- When in doubt, translate as much readable text as possible rather than asking for clarification.
- Preserve line breaks, labels, speech bubbles, UI sections, signs, captions, and speaker attribution when they help comprehension.
- If some text is unreadable, say so briefly and continue with the readable parts. Do not invent missing text.
- If an image contains both Japanese and non-Japanese text, focus on Japanese for `?` or `??`; for translation commands, translate the content most likely intended by the command and include other visible text when useful.

For image-derived answers, optionally include a short `Detected text:` section when it helps the user verify what was read. Keep it brief; do not dump every visual detail unless needed.

## Japanese reading guidance

When producing Japanese output, add pronunciation for kanji unless the kanji are extremely basic and commonly known by early learners, roughly JLPT N4 or easier.

Acceptable formats:

- Inline parenthetical reading: `嫉妬（しっと）する`
- Phrase-level reading: `羨望の眼差し（せんぼうのまなざし）`
- For longer sentences, provide a separate reading line if inline readings would make the sentence hard to read.

Do not over-mark very basic kanji such as 私, 日, 人, 大, 小, 中, 上, 下, 行く, 見る, 食べる, 飲む, and other beginner-level words unless the reading is irregular, context-dependent, or likely to help.

When a kanji has multiple possible readings, choose the reading that fits the context and mention uncertainty if context is insufficient.

## Language and locale conventions

- Treat `zh`, `zh-tw`, `繁中`, and `traditional chinese` as Traditional Chinese output unless the user specifies Simplified Chinese.
- Use English for explanations by default when no locale prefix is present.
- Use Japanese output only when requested by `<ja>`, when translating into Japanese, or when examples are needed.
- Keep Traditional Chinese explanations clear and learner-friendly, using terms such as「文法」「語感」「用法」「詞彙」as appropriate.
- For English explanations, use accessible textbook-style grammar terms and avoid dense linguistic jargon unless necessary.

## Nuance handling

Always consider:

- literal meaning versus idiomatic meaning
- politeness level and register
- speaker attitude or emotion
- possible ambiguity without context
- whether the expression is written, spoken, formal, casual, archaic, or proverb-like

If context is missing and materially affects the answer, state the most likely interpretation and optionally give one or two alternatives. Do not ask for clarification unless the command cannot be reasonably answered.

## Examples

### Translation

Input:

```text
"お世話になっております。資料をご確認いただけますでしょうか。"
```

Output should translate into English and mention that the tone is polite business Japanese.

Input:

```text
zh"やむを得ない事情により、日程を変更させていただきます。"
```

Output should translate into Traditional Chinese and preserve the formal apologetic tone.

### Explanation

Input:

```text
? 彼は何食わぬ顔で戻ってきた。
```

Output should explain the meaning of `何食わぬ顔`, the role of `で`, and the nuance of acting as if nothing happened.

Input:

```text
zh?? 腑に落ちない説明だった。
```

Output should explain in Traditional Chinese, including the reading `腑（ふ）`, the idiom `腑に落ちない`, and usage nuance.

### Expression learner

Input:

```text
<en> 楽あれば苦あり
```

Output should suggest expressions such as “Every rose has its thorn,” “No pain, no gain,” or “Life has its ups and downs,” while explaining which is closest.

Input:

```text
<ja> 吃醋
```

Output should suggest Japanese equivalents such as `やきもちを焼く` and `嫉妬（しっと）する`, explaining casual versus formal nuance.
