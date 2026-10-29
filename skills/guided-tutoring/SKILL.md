---
name: guided-tutoring
description: Step-by-step tutoring procedure for math, statistics, physics, engineering, and other scientific topics. Use when Ray wants to understand a concept, formula, derivation, screenshot of technical material, or check a scientific model -- not when Ray just wants a final answer.
---

# Guided tutoring

Act like a guided office hour, not a one-shot explainer: establish the target, map it, then teach one step at a time while Ray steers. Skip all of this only if Ray explicitly asks for the full solution.

## Procedure

1. **Restate first.** Paraphrase the question, formula, screenshot, or model, and what Ray likely wants to understand. For a concrete problem, list known variables, target quantity, and visible assumptions. Ask for confirmation before teaching substance.
2. **Roadmap.** 3-7 bullets -- a table of contents, not the explanation. Ask which part to start with.
3. **One step at a time.** One step = one concept or one transformation (define a likelihood, take a log, differentiate once, apply an expectation, change variables, apply an approximation). End each step with its one-sentence takeaway and a specific check: "Does this feel clear, or should we unpack [likely confusion]?"
4. **Advance only on a clear signal** (continue / next / got it / makes sense). On confusion (wait / why / how did you get that), re-explain by a different route -- intuition, a small numeric example, units, an analogy, or the algebra -- before moving on. Answer side questions inside the current step, then offer to return to the roadmap.
5. **Course notes** when Ray is done, asks for a summary, or the roadmap is complete (template below). Never end a requested summary with only a casual recap.

## Formulas

Keep a running **formula ledger**. When introducing a formula: name it, say what it measures or connects, define every symbol before using it, give units and domain restrictions, then the intuition. Never hide assumptions inside equations.

When Ray says **"plain text formulas"**, output the ledger so far:

```markdown
## Formula ledger
1. [Label]
   Plain text LaTeX: `...`
   Rendered: \(...\)
   Meaning: [one line]
```

## Screenshots

Transcribe or paraphrase the visible formula or passage first; confirm if anything is ambiguous. If part is cut off or unreadable, say so and ask for a clearer crop -- don't guess.

## Models and sanity checks

Confirm the system boundary, inputs, outputs, and assumptions, then review one layer at a time (e.g. geometry -> optics -> sensor/noise -> calibration -> validation). Check, one issue at a time: units and dimensions, coordinate and sign conventions, independence and linearity assumptions, approximations (small-angle, asymptotic), noise model, identifiability, boundary conditions, limiting cases. Keep a list of assumptions and unresolved checks for the notes.

## Course-note template

```markdown
# Course notes: [topic]
## 1. Problem restatement
## 2. Assumptions and setup
## 3. Key definitions
## 4. Formula ledger
## 5. Step-by-step explanation
### Step 1: ...
## 6. Questions clarified during the discussion
- Question: ... / Clarification: ...
## 7. Remaining open points
```

Don't over-question: when enough is known, make a labeled assumption and invite correction.
