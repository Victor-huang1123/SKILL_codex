---
name: obsidian-inbox-triage
description: Review and classify Markdown notes in an Obsidian vault Inbox, especially `99 - Inbox`, and recommend destination folders without deleting notes. Use when Codex needs to inspect Obsidian note titles, content, tags, wikilinks, and existing vault structure to produce a triage table, identify empty notes, duplicate candidates, notes needing review, and notes that can be moved into formal folders such as Knowledge points, Routing, Placement, AI for EDA, Optical Routing, Convex Optimization, Advanced Algorithm, or Program Language.
---

# Obsidian Inbox Triage

## Overview

Classify notes in `99 - Inbox` into formal Obsidian vault folders by reading the note title, body, tags, wikilinks, and nearby existing notes. Produce recommendations only unless the user explicitly asks to move files.

## Safety Rules

- Do not delete notes.
- Do not move notes unless the user explicitly asks for file moves.
- Keep uncertain notes in `99 - Inbox/Needs Review/`.
- Put empty or near-empty notes in `99 - Inbox/Empty Notes/`.
- Put likely duplicates in `99 - Inbox/Duplicate Candidates/`.
- Treat the requested output table as the primary deliverable.

## Workflow

1. Locate the vault root from the current working directory or the path named by the user.
2. Inspect `99 - Inbox` recursively for Markdown files. Ignore files already under `99 - Inbox/Empty Notes`, `99 - Inbox/Duplicate Candidates`, and `99 - Inbox/Needs Review` unless the user asks to re-review them.
3. Run `scripts/inbox_snapshot.py <vault-root>` to produce a compact JSONL snapshot with paths, titles, tags, wikilinks, word counts, and near-empty flags.
4. Sample the formal folder structure and candidate duplicate notes with `rg --files` and targeted reads. Compare by title, aliases, core terms, tags, and wikilinks.
5. Classify each Inbox note according to the destination rules below.
6. Return the table and the four requested summary lists. Include confidence as `高`, `中`, or `低`.

## Destination Rules

Use the note's main purpose, not incidental mentions.

- `Knowledge points`: concept notes that define reusable ideas, terms, math, algorithms, EDA concepts, or theory that many notes could cite.
- `Routing`, `Placement`, `AI for EDA`, `Optical Routing (光繞線)`, `Convex Optimization`, `Advanced Algorithm`, `Program Language`: papers, methods, systems, experiments, algorithm applications, and topic notes whose primary purpose belongs to that topic.
- `99 - Inbox/Empty Notes/`: blank notes, title-only notes, or notes with only a stub link/tag and no usable content.
- `99 - Inbox/Duplicate Candidates/`: notes whose topic is highly overlapping with an existing formal note. Prefer this even if the destination topic is otherwise clear.
- `99 - Inbox/Needs Review/`: ambiguous notes, mixed-purpose notes, personal scratch notes without enough context, or notes where two destinations are equally plausible.

## Folder Map

Concept notes:

- `Knowledge points/EDA/Core EDA`
- `Knowledge points/EDA/Physical Design`
- `Knowledge points/EDA/PCB and Signal Integrity`
- `Knowledge points/EDA/Circuit and Semiconductor`
- `Knowledge points/EDA/Digital Design`
- `Knowledge points/EDA/Photonics`
- `Knowledge points/Algorithm/Graph Algorithms`
- `Knowledge points/Algorithm/Combinatorial Optimization`
- `Knowledge points/Algorithm/Dynamic Programming`
- `Knowledge points/Algorithm/Numerical Methods`
- `Knowledge points/Algorithm/Optimization Methods`
- `Knowledge points/Algorithm/Heuristic and Metaheuristic`
- `Knowledge points/Math/Foundations`
- `Knowledge points/Math/Linear Algebra`
- `Knowledge points/Math/Optimization`
- `Knowledge points/Math/Abstract Algebra`
- `Knowledge points/Math/Geometry`
- `Knowledge points/Math/Statistics and ML`
- `Knowledge points/Math/Numerical Analysis`

Research and topic notes:

- `Routing/Global Routing`
- `Routing/Detailed Routing`
- `Routing/PCB and Package Routing`
- `Routing/PDN and Clock`
- `Routing/ML and Data Driven Routing`
- `Routing/Routing Algorithms`
- `Placement/Analytical Placement`
- `Placement/Legalization`
- `AI for EDA/Information Theory`
- `AI for EDA/Representation and Explainability`
- `Optical Routing (光繞線)`
- `Convex Optimization`
- `Advanced Algorithm`
- `Program Language`

## Output Format

Return this table:

| 原始筆記 | 建議移動到 | 判斷原因 | 信心 |
|---|---|---|---|

Then list:

1. 可以直接移動的筆記
2. 建議人工確認的筆記
3. 可能重複的筆記
4. 空白或低內容量筆記

Use `高` when the folder is clear, `中` when another folder is plausible, and `低` when human review is needed.
