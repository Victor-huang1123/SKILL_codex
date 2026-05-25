---
name: eda-lab-deck-reviewer
description: Critiques an existing EDA Lab paper-presentation deck for writing style, structural issues, content accuracy, and figure placement against the source paper. Use whenever the user uploads a draft .pptx, especially group_meeting_*.pptx or any deck in EDA Lab style, together with the source paper and asks for review, feedback, critique, how to improve, or which paper figures to add. Trigger on phrases like "how is this slide written", "review my deck", "suggest improvements", or "which figures should I include". Do NOT use this skill for creating a deck from scratch; use eda-lab-paper-deck for that.
---

# EDA Lab Deck Reviewer

Review a draft paper-presentation deck against the source paper. Produce a written critique covering writing style, structural issues, content accuracy, and figure-to-slide mapping. Do not auto-edit the file unless the user explicitly asks.

## Inputs Required

Two files are required:

1. Draft `.pptx` or already-rendered slide images
2. Source paper PDF

If only one is provided, ask for the other before starting. Do not review from the deck alone because terminology and figure placement require the paper.

## Workflow

### Step 1: Render Every Slide

Thumbnail grids are not enough. Render every slide at full resolution so overflow, line-wrap, and footer collisions are visible.

Use the available presentation or office tooling. A typical workflow is:

```bash
cp <uploaded>.pptx ./deck.pptx
python /mnt/skills/public/pptx/scripts/office/soffice.py --headless --convert-to pdf deck.pptx
pdftoppm -jpeg -r 100 deck.pdf slide
```

Then inspect every `slide-NN.jpg` one by one. Do not skim.

### Step 2: Map Slide Order to Sections

Walk the deck. Each Outline-divider slide marks the start of a new section. Build a list of `(position, slide_file, title, section)` so misplaced slides can be flagged.

### Step 3: Apply the Four Checklists

Read each slide against the checklists below. Note issues with slide number and a concrete fix.

### Step 4: Build the Figure-to-Slide Mapping

Catalog every figure and table in the source paper with a one-line description. For each, decide the best target slide.

### Step 5: Write the Review

Use the output format below. Skip sections that have nothing to report.

## Checklist 1: Writing Style

**Bullets should be scannable.** Prefer concise take-away phrases over long handout prose. If the draft uses full sentences, either shorten them or keep the direct claim only when it helps the audience understand the slide faster.

| Too Wordy | Better |
|---|---|
| The framework is written in C++ and runs on Linux | C++ on Linux |
| 46 standard cells are synthesized from NS3K netlists | 46 cells from NS3K netlists |
| An LP heuristic assigns the longest M0 wire as the M0 pin | LP: longest M0 wire -> pin |
| The SMT model estimates how many external access paths can succeed | SMT maximizes successful access paths |
| The flow tries compact single-row cells before adding extra rows | Single-row first; multi-row fallback |

**Avoid repeated "The X is/are/does..." chains.** Three consecutive bullets starting with "The" is a smell. Rewrite some to verb-first or noun-first phrasing.

**Treat hedging as a precision warning.** Watch for: may, should, can, often, usually, still, generally. Remove them or replace them with concrete paper-backed claims.

**Prefer active verbs.** "X improves Y" is clearer than "Improvement of Y is achieved by X".

**Match the paper's terminology exactly.** If the paper says "maximize", do not soften it to "estimate". If it says "constrain", do not soften it to "prefer".

For every style issue found, output the slide number and a one-line before -> after rewrite.

## Checklist 2: Structural Issues

**Section coherence.** Each content slide must fit the section divider before it. Common misplacements:

- Motivation in Preliminaries belongs in Introduction
- Notation tables in Methodology belong in Preliminaries
- Results discussion in Conclusion belongs in Experimental Results

**Slide redundancy.** Two consecutive slides covering the same ground should usually be merged or differentiated more sharply.

**Body overflow.** Look at rendered slides. If the last bullet collides with `GIEE, NTU`, `The EDA Lab`, or the slide number, suggest stripping blank spacers, dropping sub-bullets, or shortening main bullets.

**Title quality.** Titles must be noun phrases with no trailing punctuation. Bad: `How Virtual Nodes Help.` Good: `Virtual Node Access Model`.

**Concept conflation.** A single slide should cover one concept. Flag slides that mix unrelated mechanisms.

## Checklist 3: Content Accuracy

**Domain-term typos.**

- `Gated-All-Around` -> `Gate-All-Around`
- `Hsich` -> `Hsieh` when referring to the LiB author
- Layer abbreviations must be uppercase: M0, M1, M2

**Wrong verb or claim strength.**

- `Estimates` vs `Maximizes`
- `Optimizes` vs `Constrains`
- `Reduces` vs `Eliminates`

**Grammar bugs introduced by rewriting.**

- `X are placed and redesigned alternatives` -> `X are replaced with redesigned alternatives`
- `The flow tries compact single-row cells` -> `The flow starts with compact single-row cells`

**Citation consistency.** Pick one citation style and use it consistently. For EDA Lab decks created with `eda-lab-paper-deck`, prefer `[Author et al., Venue'YY]` in visible bullets and full bibliography only in the small reference box.

## Checklist 4: Figure and Table Placement

For every source-paper figure and table, decide:

**Which slide it goes on.**

1. List every figure/table with a one-line description.
2. Match it to the slide whose title and bullets describe that content.
3. If two slides match equally, prefer the later one.
4. If the content is split across slides, recommend cropping the figure.

**How prominent it should be.**

- Core conceptual figures: half the slide, shrink bullets to make room
- Numerical tables: whole content area is acceptable
- Background figures: small inset or skip
- Algorithm pseudocode: usually skip; cite the paper instead

**Whether to crop or annotate.**

- Crop `(a)` / `(b)` panels to the matching panel
- Crop wide tables to key columns
- Add an arrow/callout for a specific row or region

**Slides with no corresponding paper figure.** Recommend either a simple presenter-drawn block diagram or leaving the slide text-only.

## Output Format

Always structure the review in this exact order. Skip sections with nothing to report.

```markdown
## Overall impression
2-4 sentences. What's strongest? What's weakest? Compare to the template or prior version if useful.

## Per-slide writing improvements
- **Slide N — <Title>**
  - Issue: <one line>
  - Rewrite: <before> -> <after>

## Structural issues
- Wrong section: slide N (<title>) belongs in section Y, not Z
- Redundancy: slides N and M cover the same ground
- Overflow: slide N body collides with footer
- Concept conflation: slide N mixes A with B

## Content accuracy
- Typos: <list>
- Wrong terminology: <list with paper wording>
- Grammar bugs: <list with fix>
- Citation inconsistencies: <list>

## Paper figure -> slide mapping
| Paper Fig/Table | Content (one line) | Suggested slide | Why |
|---|---|---|---|
| Fig. 1 | ... | Slide N | ... |

## Closing offer
Want me to apply these changes to the .pptx, or leave it for you to edit?
```

## Tone and Scope

- Be direct but not harsh.
- Acknowledge what works.
- Give concrete suggestions only; always show a rewrite for style issues.
- Do not pile up. If a slide has many issues, pick the two most impactful.
- Do not auto-apply edits unless explicitly asked.
- Do not flatten technical content in rewrites.
- Do not focus on colors, fonts, or spacing beyond overflow; those belong to the EDA Lab template.
- Do not second-guess section structure unless the mismatch is clear.

## Companion Skill

This skill reviews existing decks. Use `eda-lab-paper-deck` to create or revise a deck.
