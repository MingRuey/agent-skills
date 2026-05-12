---
name: find-expression
description: find idiomatic, natural-sounding equivalent expressions in a target language for a phrase, idiom, or idea. triggered when the user prefixes content with an angle-bracket locale tag like <en>, <ja>, <zh-tw>. the tag is the target language; the source can be any language.
when-to-use: the user message begins with an angle-bracket locale tag such as <en>, <ja>, <zh-tw>, <fr>, etc.
allowed-tools: []
---

# Find Equivalent Expression

## Command syntax

```
<en> 楽あれば苦あり          → English equivalents of the Japanese proverb
<ja> 吃醋                   → Japanese equivalents of the Chinese expression
<zh-tw> sour grapes          → Traditional Chinese equivalents of the English idiom
```

## Behavior

- The locale inside `<...>` is the **target** expression language; source can be any language.
- Find expressions in the target language that capture the same idea, idiom, or sentiment.
- Prefer expressions that sound natural to native speakers over literal translations.
- Provide multiple options when no single exact equivalent exists.
- **Write the entire response — section labels, when-to-use notes, and nuance commentary — in the target language.** The locale tag controls the *output* language, not just the expressions.
- For image input, infer the source expression from visible text and look up equivalents in the target locale.

## Output format

Use the section labels appropriate to the target locale; the structure is the same, only the language changes.

For `<en>`:
```markdown
Best match: [expression]

Other options:
- [expression] — [when to use it]
- [expression] — [when to use it]

Nuance: [how close the match is and what differs]
```

For `<ja>`:
```markdown
最適な訳：[表現]

その他の候補：
- [表現] — [使う場面]
- [表現] — [使う場面]

ニュアンス：[どのくらい近いか、何が違うか]
```

For `<zh-tw>`:
```markdown
最佳對應：[表達]

其他選項：
- [表達] — [使用情境]
- [表達] — [使用情境]

語感差異：[貼近程度與差別]
```

For other locales, use the idiomatic equivalents of these section meanings in that language.

## Examples

Input:
```
<en> 楽あれば苦あり
```
Respond entirely in English with idioms like "Every rose has its thorn", "No pain, no gain", or "Life has its ups and downs", and a brief English nuance note on which is closest.

Input:
```
<ja> 吃醋
```
Respond entirely in Japanese: equivalents such as `やきもちを焼く` and `嫉妬（しっと）する`, with section labels and casual-vs-formal notes also in Japanese.

Input:
```
<zh-tw> sour grapes
```
Respond entirely in Traditional Chinese: equivalents like 「酸葡萄心理」, with section labels and usage notes also in Traditional Chinese.
