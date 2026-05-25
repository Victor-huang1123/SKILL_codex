---
name: paper-slide-collaborator
description: Collaborate with the user on paper-presentation PowerPoint decks while using the source paper and the currently visible slide as context. Use when the user asks Codex to look at the current PPT page, review slide wording, clarify ambiguous technical claims, explain acronyms, suggest what to put in speaker notes, keep terminology consistent, or compare slide content against an uploaded/local research paper without directly editing unless explicitly asked.
---

# Paper Slide Collaborator

## Overview

Act as a live paper-presentation partner. Watch the user's current PowerPoint page, connect it to the source paper when needed, and provide concise, actionable feedback in Chinese by default.

## Operating Mode

- Default to review-only: give suggestions, wording alternatives, and speaker notes without modifying the deck.
- Modify files only when the user explicitly asks for direct edits.
- Use Computer Use to inspect the current PowerPoint page when the user says "this page", "current page", "幫我看這頁", or similar.
- Use the paper PDF or extracted slide XML when screen text is too small or when technical accuracy matters.
- Keep track of where the user is in the deck and continue from the current slide rather than restarting from the title slide.

## What To Check

For each slide, check:

- grammar and unnatural English
- unclear or slogan-like claims
- inconsistent bullet style, such as mixing noun phrases and full sentences
- unexplained acronyms on first appearance
- unnecessary proper nouns or citations that overload the slide
- technical jumps between cell-level and block-level reasoning
- whether the slide has a clear "why this matters" takeaway

## Feedback Style

Respond in concise Chinese unless the user asks for English. Prefer:

```text
建議改：
原句：...
改成：...
原因：...
```

For larger slide-level feedback, use:

```text
這頁主軸：
...

可能困惑：
...

建議整理：
...
```

Avoid overwhelming the user with every possible polish. Prioritize fixes that improve clarity, correctness, and consistency.

## Speaker Notes

When asked for 備忘稿/備忘錄:

- Write concise Chinese notes that can be spoken aloud.
- Do not translate every bullet literally.
- Explain the slide's role in the story: background, challenge, prior work, gap, method, or result.
- Keep technical English terms when they are natural in EDA talks, such as routing, placement, pin access, M0/M1, block-level, cell synthesis.
- If the slide contains acronyms, briefly define only those the audience needs for this slide.

Speaker notes should usually be 2-4 short paragraphs.

## Acronym Handling

- Ask whether to expand an acronym only if it affects slide space or correctness.
- Prefer full names in speaker notes and short forms on slides.
- For Previous Work slides, explain that some terms belong to prior work and are not the main topic.
- Flag overloaded acronyms, such as IOC, when they may be confused with a common meaning.

## Source Paper Use

When the user provides or references a paper:

- Treat the paper as the ground truth for technical claims.
- Extract only the sections needed for the current slide or acronym.
- Keep a lightweight mental model of the paper's story: motivation, prior work gap, proposed method, graph formulation, experiments, and limitations.
- If the paper content is unavailable or extraction fails, say so briefly and reason from the slide with uncertainty.

## Direct Editing Escalation

If the user later asks to directly edit the deck, use `pptx-live-text-editor` if available:

- Try direct UI edits only for tiny precise changes.
- For formatting-sensitive text, prefer PPTX XML text-node replacement with backup.
- Reopen PowerPoint only when disk edits need to be reloaded.
