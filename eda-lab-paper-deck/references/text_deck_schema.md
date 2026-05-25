# Text Deck JSON Schema

Use this JSON shape with `scripts/build_text_deck.py` when creating text-only
EDA Lab paper-presentation decks.

```json
{
  "slides": [
    {
      "kind": "title",
      "title": "Paper Title",
      "venue": "ISPD'26",
      "authors": "A. Author, B. Author",
      "affiliations": "University / Institute",
      "date": "2026-05-23",
      "presenter": "Zhih-Chi Huang"
    },
    {
      "kind": "outline",
      "current": "Introduction"
    },
    {
      "kind": "previous-work",
      "title": "Previous Work",
      "topics": [
        {
          "topic": "Two-stage synthesis [LiB'91, BonnCell'20]",
          "details": [
            "Separate placement and routing to scale to larger cells",
            {
              "kind": "equation",
              "text": "minimize  ∑ₑ∈E cₑxₑ"
            }
          ]
        }
      ],
      "references": [
        "[LiB'91] Y. C. Hsich et al., \"LiB: a CMOS cell compiler,\" IEEE TCAD, 1991."
      ]
    }
  ]
}
```

## Slide Kinds

- `title` uses template slide 1.
- `outline` uses template slide 2 unless `source` is set.
- `outline-introduction`, `outline-preliminaries`, `outline-problem-formulation`,
  `outline-methodology`, `outline-experimental-results`, and
  `outline-conclusion` reuse the dimmed outline variants.
- `content` uses template slide 16.
- `previous-work` uses template slide 5 and enables the reference box.
- `remarks` uses template slide 20.
- `thank-you` uses template slide 21.

Set `"source": 4`, `"source": 12`, or another template slide number to force a
specific source slide.

## Topic Rules

Write each body item as a noun phrase in `topic`, then put the explanatory
content in `details`. Avoid colon-led constructions. Prefer this:

```json
{
  "topic": "Pin-access constraints [Cheng et al., ISCAS'20]",
  "details": ["Guarantee valid access points with MPL / MPO / PS rules"]
}
```

Avoid this:

```json
"Pin-access constraints: MPL / MPO / PS guarantee valid access points"
```

## Typography Applied By The Script

- Slide title: direct-formatted Arial, 28 pt.
- L0 topic: black Arial, 24 pt, bullet dot.
- L1 detail: muted navy Arial, 20 pt, indented bullet dot.
- In-body citation brackets: 18 pt, formatted as `[Author et al., Venue'YY]`.
- Previous-work references: black Arial, 10 pt, bottom reference box.
- Outline title: direct-formatted Arial, 28 pt.
- Outline current section: black regular, 24 pt.
- Outline inactive sections: light gray, 24 pt.
- Title-slide authors and affiliations: black Arial, 14 pt, below venue.

Body slides do not have a hard cap on L0 topic bullets. Keep topics and details
concise enough to avoid footer overflow. If a slide needs more space, split it
into two slides rather than shrinking text.

Prefer L0 topics that read as clear take-away sentences, not vague noun-only
labels. Use L1 details for the mechanism, constraint, or number that supports
the take-away.

## Equation Lines

Keep math out of inline prose when the user wants equation blocks. Put the
surrounding explanation in normal bullets, then add a detail object:

```json
{
  "topic": "The objective minimizes weighted routing cost",
  "details": [
    "Use a binary decision variable for each routing edge",
    {
      "kind": "equation",
      "text": "minimize  ∑ₑ∈E cₑxₑ"
    }
  ]
}
```

Equation details render as no-bullet Cambria Math text blocks aligned under the
detail text. Use Unicode math characters for simple equations; do not use LaTeX
syntax because the text-only builder does not reliably create native PowerPoint
equation objects.

## Previous Work Reference Rules

For `previous-work`, always include `references`. Use the same citation keys in
the visible topics and in the reference box. If the paper's bibliography does
not contain the requested citation key, do not invent it; add the closest
accurate reference and mention the mismatch to the user.

Each citation key must use one bracketed paper in author/venue/year format, e.g.
`[Cheng et al., TVLSI'21]`. Do not use tool-only keys such as `[BonnCell'20]`,
and do not combine papers in one bracket such as
`[Cheng et al., TVLSI'21; Seo et al., DAC'17]`.
