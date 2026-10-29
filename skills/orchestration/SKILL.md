---
name: orchestration
description: Procedure for long or multi-part work -- help Ray sharpen their own goal and steps, track them as a task list, delegate self-contained pieces to subagents, verify each result, and stay on goal over many steps. Use when a request needs more than a few steps, splits into independent parts (a batch over many files, items or sources), or Ray asks to plan, batch, or orchestrate. Not for questions answerable in one or two steps.
---

# Orchestration

Ray owns the goal and the plan; you help sharpen it, then run it: track it, hand self-contained pieces to workers, accept nothing unchecked. Skip this for small tasks -- planning overhead must pay for itself.

## 1. Ray writes the plan; you help

Ray writes the goal and the steps. Don't write them for Ray. Given only a goal, ask for Ray's steps; draft some only if asked.

Help make the plan runnable, as suggestions Ray accepts or rejects:

- Restate the goal and steps in one short block so Ray can confirm you read them right.
- Point out gaps: a step with no clear output, no **done when** for the goal or a step, a missing dependency, an ambiguous term, a step that looks much bigger than the others.
- Say which steps you'd run in parallel or delegate, and how you'd check each one.
- Ask only questions whose answer changes what you'd do; list your other assumptions.

Read-only exploration to give better suggestions is fine. Start work only when Ray says go. Keep Ray's wording; never silently reword, reorder, merge or drop Ray's steps.

## 2. Keep the task list and re-read it every turn

The list is Ray's steps, in Ray's order and words. Statuses: `[ ]` pending, `[~]` in progress, `[x]` done (with how it was verified), `[!]` failed or blocked (with why).

- Use the app's task tool if there is one; otherwise end every reply with the list as a markdown block under the heading `Tasks`.
- At the start of each turn, re-read the goal and the list before acting. Update statuses the moment they change, not in batches.
- You may break one of Ray's steps into indented sub-items for execution (e.g. one per worker in a batch); Ray's step stays as written above them.
- New work found along the way: propose it as a new step and wait for Ray; don't add it and don't take a silent detour.

## 3. Delegate self-contained pieces

Delegate when a piece is independent, reads a lot to produce a little, or there are many alike (batch). Keep inline: small steps, steps needing this conversation's context, and anything needing Ray's input.

A worker starts with a blank context and sees only the brief, so the brief must stand alone:

```
Goal: <the overall goal, one line, so the worker knows why>
Task: <exactly this piece>
Inputs: <files, URLs, data, prior results -- verbatim, not "the file we discussed">
Constraints: <scope limits, what not to touch, style rules>
Done when: <checkable criteria>
Return: <shape of the reply: summary <=N lines, a table, a diff, file paths; list anything unsure or skipped>
```

- Independent pieces: launch them together in one turn. Dependent pieces: wait for the result first.
- For a batch, give every worker the same template and one item each, or a few items each.
- Ask for summaries back, not transcripts. Put full outputs in files when the app allows, and return paths.

## 4. Check every result

A worker's "done" is a claim, not a fact. For each result:

- Check it against its **done when**: run the test, open the file, spot-check figures and citations, confirm the shape asked for.
- On failure: retry once with a sharper brief that names what went wrong. On a second failure, do it inline or mark `[!]` and tell Ray -- don't loop.
- For high-stakes or subjective output, use a fresh reviewer worker given the criteria and the result, but not the producer's reasoning.
- Merge results only after they pass. Report failures and skipped steps plainly in the final summary.

## 5. Stay on track over long runs

- Every turn: goal + task list first, then act.
- Keep the conversation light: summaries in, details in files or worker contexts.
- Every ~5 steps, or after a surprise, check: does the plan still reach the goal? If not, stop and propose the change to Ray.
- If context is summarized or a session resumes, rebuild from the goal, the done-when criteria and the task list, never from memory of earlier turns. Write the goal and the list so they survive summarization.
- Stop and ask when blocked on a decision that is Ray's, when cost or scope grows past the plan, or before anything hard to undo.

## Finish

Final report: what was done, how each part was verified, what failed or was skipped and why, and what's left. Then the closed task list.

## By app

| | Claude Code | LibreChat | claude.ai |
|---|---|---|---|
| Ray's plan | in Ray's message; suggest, then wait for go | same | same |
| Task list | task tool (TaskCreate / TodoWrite) | markdown `Tasks` block each reply | markdown `Tasks` block each reply |
| Workers | `Agent` tool; several calls in one turn run in parallel | `subagent` tool (`description` = the brief, `subagent_type` = which agent, `run_in_background` for long pieces), if the agent has subagents enabled | none: do pieces one at a time inline, each against its own brief and criteria |
| Long runs | automatic compaction | summarization, if enabled on the server | none; keep the list current and suggest a new chat seeded with goal + list |
