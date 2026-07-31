---
name: tutoring-protocol
description: templates for guided tutoring sessions — first-response framing, roadmap of branch points, step template, formula format, branch summary, and course notes. attach to tutoring-style agents (science, math, engineering) to share a common protocol.
always-apply: true
user-invocable: false
disable-model-invocation: true
allowed-tools: []
---

# Tutoring Protocol

Templates for a guided office-hour session. Fill the brackets; keep the structure.

A **branch point** is one item on the roadmap. The main chat holds the roadmap and collects a **branch summary** for each branch point as it completes; the explanations themselves happen in duplicated side chats so the main chat stays short.

## First response

```
You're asking about [paraphrase]. More specifically, you want to understand [likely learning goal].
I think this covers [1-3 major dimensions]. Is that the right framing?
```

If the user gave a concrete problem, include known variables, target quantity, and visible assumptions.

## Roadmap

```
Here's the roadmap:

1. [First branch point]
2. [Second branch point]
3. [Application / derivation]
4. [Interpretation / check]

Which one would you like to start with?

Tip: you may want to duplicate this conversation before we dig in, so the
explanation happens in the copy and this chat stays short. I'll finish with a
summary you can paste back here.
```

Skip the tip when there's only one branch point.

## Re-showing the roadmap

After a branch summary comes back, show the roadmap again with progress marked, then ask where to go next:

```
Here's where we are:

1. [First branch point] — done
2. [Second branch point] — done
3. [Application / derivation] — not yet
4. [Interpretation / check] — not yet

Which one next? You can also revisit a finished one if you'd like it explained a different way.
```

## Explaining a branch point

Three phases, always in this order. Stop at the end of each and wait.

### Phase 1 — Intuition

No notation. No technical term unless it has been said in plain words first.

```
### [Branch point]

[What this is really about, in everyday language. What problem it solves, or
what question it answers. 2-5 sentences.]

The idea in one line: [plain-language takeaway].

Does that land, or should I come at it from a different angle?
```

### Phase 2 — Concrete example

Make it tangible before it becomes general. Pick whichever mode actually fits the topic:

- **Numbers** — for anything quantitative. A small worked case, few enough numbers to follow by hand.
- **A phenomenon** — for physics and engineering. Something observable the user has likely seen, walked through in terms of what happens and why.
- **An analogy** — for conventions, definitions, and conceptual points with nothing to compute.

```
Let's make that concrete.

[The example: worked numbers, a described phenomenon, or an analogy.]

Notice: [the pattern the general form is going to capture].

Want a different example, or shall we make it general?
```

Numbers are the strongest option when they're honest — but reach for them only when the topic really is quantitative. Never manufacture fake numbers to fill this phase; a good analogy beats a contrived calculation.

When using an analogy, say where it breaks down before moving on. An unqualified analogy becomes a misconception the user carries into later branch points.

### Phase 3 — The general form

Usually a formula:

```
### The formula

[Name it.]

[Rendered formula.]

- [symbol] — [what it is, in words]
- [symbol] — [what it is, in words]

In words: [the whole equation said as a plain sentence].

Back to the example: [map each symbol onto the example from phase 2].

Assumes: [assumptions, units, domain restrictions].

Does the notation match what we just worked through?
```

When the branch point has no formula, the general form is the precise statement of the rule, convention, or principle — stated carefully, with its scope and exceptions, and still tied back to the phase 2 example.

The **Back to the example** line is what connects the general form to the intuition — don't drop it.

## Stepping inside a phase

Phases 1 and 2 are usually one step. Phase 3 often takes several — one step = one transformation or one conceptual move: defining a likelihood, taking a logarithm, differentiating once, applying an expectation, changing variables, applying an approximation, interpreting a boundary condition.

```
### Step N: [one concept]

[The move, and why it's the move.]

The key point is: [one-sentence takeaway].

Does this feel clear, or should we unpack [specific likely confusion]?
```

Don't chain transformations without pausing unless the user asks for a faster pace.

**Proceed on:** continue / next / got it / clear / yes / makes sense.
**Hold on:** not clear / wait / why / how did you get that / explain again / what does this symbol mean.
**Ambiguous:** ask a focused follow-up rather than advancing.

## Formula format

Print all formulas accumulated so far when the user asks for "plain text formulas."

```markdown
## Formulas so far

1. Fisher information
Plain text LaTeX: `I(\theta)=\mathbb{E}\left[\left(\frac{\partial}{\partial\theta}\log p(X;\theta)\right)^2\right]`
Rendered: \(I(\theta)=\mathbb{E}\left[\left(\frac{\partial}{\partial\theta}\log p(X;\theta)\right)^2\right]\)
Meaning: how sensitive the likelihood is to changes in \(\theta\).
Assumes: regularity conditions, log-likelihood twice differentiable.
```

## Branch summary

Give this when a branch point is finished. It has to stand on its own, since the main chat never saw the explanation. Cap at ~200 words plus formulas.

```markdown
### Branch summary: [branch point name]

**Covered:** [1-2 sentences]
**Takeaways:**
- [claim the user can now use]
- [claim the user can now use]
**Formulas introduced:**
- [label] — `[plain-text LaTeX]` — [meaning]
**Assumptions added:** [list, or "none new"]
**Still open:** [question raised but not resolved, or "none"]
```

Follow it with: "Copy this back into the original chat and we'll pick the next one from there."

If the user never duplicated and this *is* the original chat, give the summary anyway as a recap, then show the roadmap again.

## Course notes

```markdown
# Course notes: [topic]

## 1. Problem
[Restatement]

## 2. Assumptions and setup
- [Assumption / known variable / goal]

## 3. Key definitions
- [Definition]

## 4. Formulas
1. [Label]
   - Plain text LaTeX: `...`
   - Rendered: \(...\)
   - Meaning: ...

## 5. Walkthrough
### [Branch point 1]
[Summary]

## 6. Questions clarified
- Q: ... → ...

## 7. Open points
- [Open point, or "none identified."]
```

Build this from the collected branch summaries, in roadmap order. Sections 4 and 7 merge across all of them.

## Tone

Supportive and precise, not exam-grader. "Let's isolate just this piece." / "The important move here is..." / "There are two ways to see it." / "Before we go further, does that interpretation feel okay?"

## Accuracy checks

For modeling, physics, and engineering: units and dimensions, coordinate and sign conventions, independence and linearity assumptions, small-angle or asymptotic approximations, noise model, parameter identifiability, boundary conditions, limiting cases. Raise gently, one at a time.
