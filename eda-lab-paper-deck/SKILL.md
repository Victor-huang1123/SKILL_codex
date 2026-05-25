---
name: eda-lab-paper-deck
description: Use this skill whenever the user wants to build or revise a paper presentation deck in the NTU GIEE EDA Lab group-meeting style, using the bundled PowerPoint template and Python builder scripts. Trigger for conference or journal paper decks, group meeting slides, lab meeting presentations, Apollo/EDA Lab style slides, requests that reference group_meeting templates, or requests that supply a paper PDF/link and ask for slides. Include paper figures/tables extracted from the PDF when they are useful for methodology, problem formulation, or experimental-results slides, and still include the EDA Lab outline rhythm plus a Remarks critique slide.
---

# EDA Lab Paper Presentation Deck

Build an academic paper-presentation `.pptx` in the NTU GIEE EDA Lab group-meeting style. Use the bundled template as the visual source of truth and use Python scripts for repeatable deck generation, figure extraction, and image insertion.

## Core Workflow

1. **Read the paper first.** Identify the title, venue, authors, problem, contributions, method pipeline, experiments, limitations, and candidate figures/tables.
2. **Plan the slide list.** Map the paper into the fixed EDA Lab section order. Mark slides that should include a figure/table, with the source paper page and figure/table number.
3. **Prepare paper visuals when useful.** Use original paper visuals for methodology, problem formulation, and experimental results when they make the idea faster to understand. Avoid decorative images.
4. **Build with `scripts/build_deck.py`.** Import the helper functions, start from `assets/template_python.pptx`, delete template example slides, and add slides programmatically.
5. **Render and inspect.** Visually check every slide for text overflow, distorted images, footer collisions, missing citations, and unreadable cropped figures/tables.

## Python Builder

Use `scripts/build_deck.py` for new decks, especially decks that need figures. It requires:

```bash
pip install python-pptx
```

Import the script from the skill directory:

```python
from pathlib import Path
import sys

SKILL_DIR = Path("/path/to/eda-lab-paper-deck")
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from build_deck import (
    Presentation,
    TEMPLATE_PATH,
    add_bullet_slide,
    add_figure_slide,
    add_outline_slide,
    add_title_slide,
    add_two_column_slide,
    delete_all_slides,
)

prs = Presentation(str(TEMPLATE_PATH))
delete_all_slides(prs)

sections = [
    "Introduction",
    "Preliminaries",
    "Problem Formulation",
    "Methodology",
    "Experimental Results",
    "Conclusion",
]

add_title_slide(prs, "Paper Title", "2026-05-27\nPresenter: Your Name\nThe Electronic Design Automation Laboratory\nNational Taiwan University")
add_outline_slide(prs, sections)
add_figure_slide(
    prs,
    "Routing Graph Construction",
    [
        (0, "Connection graph captures legal routing resources"),
        (1, "Vertices represent candidate access and routing locations"),
        (1, "Edges encode design-rule-compatible connections"),
    ],
    image_path="figures/fig3_graph.png",
    caption="Fig. 3 from the paper",
)
prs.save("eda_lab_paper_deck.pptx")
```

Bullet items use `(level, text)` or `(level, text, kind)`, where `kind` is `"bullet"`, `"plain"`, or `"equation"`.

Use `add_figure_slide()` for the common layout with bullets on the left and one fitted figure/table on the right. Use `add_picture_fit(slide, image_path, box)` directly only when a slide needs custom placement. Always preserve image aspect ratio.

## Extracting Figures And Tables

Use `scripts/extract_pdf_assets.py` when the paper figure/table should be copied into a slide. It requires:

```bash
pip install pymupdf pillow
```

Prefer this workflow:

```bash
python scripts/extract_pdf_assets.py render paper.pdf --pages 4,7-8 --dpi 220 --out figures/pages
python scripts/extract_pdf_assets.py crop figures/pages/page_004.png --bbox 120,260,1420,980 --out figures/fig2_pipeline.png
python scripts/extract_pdf_assets.py extract-images paper.pdf --pages 4,7-8 --out figures/raw
```

Figure rules:

- Extract or crop only visuals that support the slide's technical claim.
- Crop generously around the visual. Prefer including a little surrounding whitespace, caption text, or adjacent page content over cutting off figure/table edges, labels, axes, legends, or captions.
- Keep the paper's figure/table number in speaker notes or the slide caption.
- Do not stretch images; use a fitted box and preserve aspect ratio.
- Use tables as images when the paper table is dense or formatting matters; summarize the headline result in bullets.
- If embedded image extraction returns fragments or low-quality pieces, render the page and crop the figure manually.

## Fixed Section Order

Use this order for group-meeting paper decks:

1. **Introduction** - motivation, previous work, gap, contributions.
2. **Preliminaries** - concepts needed to understand the method.
3. **Problem Formulation** - given, output, constraints, objective.
4. **Methodology** - the technical core; usually the most figure-heavy section.
5. **Experimental Results** - setup, baselines, tables, metrics, ablations.
6. **Conclusion** - final contribution summary and headline numbers.

End with:

- **Remarks** - Pros, Cons, and My comments from the presenter's perspective.
- **Thank You!** - final closing slide.

Insert an Outline slide before each major section. Keep the section names exactly as above unless the user explicitly asks for a different structure.
Use the template's dimmed Outline variants: the current section remains dark, while the other section names use the template's light gray theme color.

## Slide Writing Rules

- Use short slide titles; prefer noun phrases or compact claims.
- Use 3-6 top-level bullets per content slide.
- Do not force every slide into exactly three L0 bullets. Vary the count by slide role: figure-heavy slides often need 2 focused L0 bullets, process/contribution/conclusion slides may need 4, and formulation or metric-comparison slides may naturally use 3.
- Write L0 bullets as audience-facing claims or topic phrases that can be understood at a glance.
- Use L1 bullets for mechanisms, constraints, consequences, or numerical evidence that explain the L0 claim.
- Keep bullet grammar parallel within a slide: do not mix paper-transcript sentences, noun fragments, and implementation notes in the same list.
- Avoid full-sentence paragraphs and avoid manually typed bullet symbols.
- Put citations at the end of the relevant L0 bullet when possible; the builder renders L0 citation brackets at 18 pt while preserving the template size for the main text.
- Preserve the template's inherited font faces, bullet styles, and body font sizes. If title placeholders are detached for editability, explicitly restore the template title style size and color so titles do not fall back to a smaller default.
- Add citations for previous work and comparison claims.
- Put dense formulas on `"equation"` lines so the builder removes bullets and applies Cambria Math. Do not attempt LaTeX-to-PowerPoint equation conversion.
- Split crowded content instead of shrinking text below the template's readable sizes.

## Figure Placement Rules

- Use one strong visual per slide unless the paper itself compares two visuals side by side.
- Put the visual on the right or bottom; keep the main claim in the bullets.
- If a figure conflicts with the template text area, keep the text box and typography unchanged; place the figure roughly and as large as practical so the user can crop or reposition it later.
- For method diagrams, point the bullets at the current step instead of narrating every label in the figure.
- For experimental tables, make the first bullet the headline number and let the table support it.
- Re-crop with more padding if any figure edge, caption, axis label, legend, or table border is clipped after insertion.

## Optional Text-Only Builder

Use `scripts/build_text_deck.py` only when the user explicitly wants a text-only draft or text-only repair. Read `references/text_deck_schema.md` before writing its JSON spec:

```bash
python scripts/build_text_deck.py spec.json output.pptx
```

Do not use the text-only builder for figure-heavy slides.

## QA Checklist

- Render the finished deck to images or PDF with available presentation tooling.
- Check every slide for body overflow into the footer.
- Check that cropped figures are sharp and not distorted.
- Check that template sample figures do not bleed through.
- Check that each outline appears before the corresponding section.
- Check that Remarks is an honest critique, not a restatement of the paper's claims.

## Bundled Resources

- `assets/template_python.pptx` - template used by the Python builder.
- `assets/template.pptx` - legacy template used by the optional text-only builder.
- `scripts/build_deck.py` - `python-pptx` deck builder with title, outline, bullet, two-column, and figure-slide helpers.
- `scripts/extract_pdf_assets.py` - PDF page rendering, embedded image extraction, and crop helper for paper figures/tables.
- `scripts/build_text_deck.py` - optional JSON-to-PPTX text-only builder.
- `references/text_deck_schema.md` - schema for the optional text-only builder.

## Output Expectations

Return the final `.pptx` path and mention the visual QA performed. A typical finished deck has 20-35 slides, follows the fixed section order, uses paper figures/tables only when they clarify the technical story, and ends with Remarks plus Thank You.
