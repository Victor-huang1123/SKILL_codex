# Paper Database Rules

## Target

- Notion database name: `Paper`
- Data source ID: `collection://2f01dd39-dd62-80d1-a8cd-000b5698aa56`
- Source folder: Google Drive `Paper/Unupdated`

## Classification Rules

Map paper content to `Flow Design` as follows:

- Placement, floorplanning, macro placement, standard-cell placement: `Physical Design: Placement`
- Routing, detailed routing, global routing, routability: `Physical Design: Routing`
- Timing, STA, signoff, WNS, TNS, clock: `Timing Closure / Signoff`
- 3D IC, chiplet, advanced package, hybrid bonding, TSV, multi-die: `Multi-Physics / Package-CoDesign`
- EDA framework, automation, tool infrastructure, benchmark: `EDA Tool / Infrastructure` or `End-to-End Flow Automation`

Map paper content to `Field` as follows:

- ML, foundation model, GNN, diffusion, reinforcement learning, or generative model: choose the matching options such as `Generative Models`, `GNN for Structured Data`, `Reinforcement Learning`, `Diffusion`, or `Supervised`
- 3D IC content: add `2.5D/3D`
- Placement content: use relevant options such as `StdCell Placement`, `Macro Placement`, `Legalization`, or `Floorplanning`
- Routing content: use relevant options such as `Global Routing`, `Detailed Routing`, `PCB Routing`, or `Optical Routing`
- Power, IR, thermal, SI, or PI content: use relevant options such as `Power Analysis`, `IR Drop`, `Power Integrity`, `Thermal Analysis`, or `SI/PI Co-Design`

## Deduplication

Before creating a new page, search the Paper database for:

- Exact or normalized title match.
- Same DOI when DOI is available.
- Highly similar title, including differences in punctuation, subtitle formatting, or capitalization.

If a matching page exists, update missing or weak fields instead of creating a duplicate. Preserve existing user-curated values unless they are clearly blank or incorrect.

## Quality Bar

- Use the PDF's DOI, abstract, keywords, and ACM/IEEE reference information before external sources.
- Keep `Comments` short, accurate, and skimmable.
- Use a Google Drive sharing link for `Link`; do not use DOI URLs or local file paths.
- Track uncertain metadata, especially title, year, publication, DOI, and classification.
- Report every created or updated paper with its Notion page URL.

## Final Report

After writing to Notion, include:

- Number of newly created papers.
- Number of existing records updated.
- Number of skipped PDFs with reasons.
- Papers with uncertain metadata and what is uncertain.
- Notion page URL for each created or updated paper.
