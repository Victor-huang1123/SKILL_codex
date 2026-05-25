---
name: pptx-live-text-editor
description: Edit wording in an existing or currently open PowerPoint deck while preserving the original slide layout, bullets, fonts, colors, and indentation. Use when the user asks Codex to revise grammar, wording, motivation slides, paper-presentation slides, or other PPTX text directly in their PowerPoint file, especially when live UI paste operations might damage formatting and a precise PPTX XML text replacement is safer.
---

# PPTX Live Text Editor

## Overview

Revise PowerPoint text with minimal formatting disturbance. Prefer small, targeted edits; preserve slide structure, visual hierarchy, bullet levels, and the user's active working context.

## Workflow

1. Inspect the current PowerPoint state with Computer Use when the user refers to the open deck or current slide.
2. Read visible text and decide whether the requested change is grammar, wording clarity, or content restructuring.
3. For one-off short edits, try direct UI editing only if the selection is precise and PowerPoint will preserve formatting.
4. If paste or direct editing changes bullet levels, font size, color, or line breaks, immediately undo and switch to PPTX XML replacement.
5. Before modifying a PPTX file on disk, create a sibling backup named like `<name>.before_<task>_edit.pptx`.
6. Replace only text nodes in the target slide XML, usually `ppt/slides/slideN.xml`, leaving all shape, paragraph, run, theme, and layout XML untouched.
7. Reopen or refresh the deck in PowerPoint and visually verify the edited slide.

## XML Replacement Path

Use this path when formatting fidelity matters.

1. Locate the active file from Computer Use state, usually shown as a `file:///...pptx` URL.
2. Inspect the target slide text:

```bash
python3 scripts/replace_pptx_slide_text.py --list /path/to/deck.pptx --slide 4
```

3. Prepare exact old-to-new replacements. Keep replacements concise enough to fit the existing text box unless the user asks for layout changes.
4. Run the script with a JSON replacement map:

```bash
python3 scripts/replace_pptx_slide_text.py /path/to/deck.pptx --slide 4 --backup-tag motivation --replace-json '{"old text":"new text"}'
```

5. Reopen the deck if PowerPoint had a stale in-memory copy. If PowerPoint asks whether to save stale UI edits that were already undone, choose not to save.

## Editing Guidance

- Preserve technical meaning over making prose sound polished.
- Prefer direct academic slide language: short noun phrases for headings, clear cause-effect statements for motivation.
- Expand ambiguous claims when the audience needs the connection, for example change slogan-like text into an explicit relationship.
- Keep technology terms conventional: `Gate-All-Around`, `advanced technology nodes`, `drive current`, `block-level routability`, `M0/M1`.
- Avoid broad rewrites of unrelated slides unless the user asks for deck-wide revision.

## Failure Handling

- If a UI edit causes formatting drift, undo before trying another method.
- If a text replacement does not appear, list the slide text and match the exact existing string.
- If the PPTX is open in PowerPoint, disk edits may not appear until the deck is reopened.
- If PowerPoint prompts to save after a failed UI attempt, do not save unless the user explicitly wants to keep those live edits.
