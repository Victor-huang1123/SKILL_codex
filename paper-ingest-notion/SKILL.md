---
name: paper-ingest-notion
description: Organize EDA and IC design research PDFs from Google Drive into a Notion Paper database. Use when Codex needs to process PDFs in Google Drive folders such as Paper/Unupdated, extract paper metadata from abstracts/keywords/DOIs/first pages, classify papers by Flow Design and Field, create or update records in the Notion Paper database, avoid duplicate paper entries, and report Notion page URLs.
---

# Paper Ingest Notion

## Core Workflow

Use Google Drive as the source of truth for PDFs and Notion as the destination database.

1. Locate the Google Drive folder `Paper/Unupdated`.
2. List all PDF files in that folder.
3. Fetch or export each PDF enough to inspect metadata, first-page text, title block, abstract, keywords, references, DOI, and venue clues.
4. Read `references/paper-database-rules.md` before assigning `Publication`, `Flow Design`, or `Field`.
5. Fetch the Notion `Paper` data source schema before writing:
   `collection://2f01dd39-dd62-80d1-a8cd-000b5698aa56`
6. Check for existing database records with the same title, DOI, or highly similar title. Update incomplete existing records instead of creating duplicates.
7. Create or update one Notion page per paper.
8. Report counts for created, updated, skipped, and uncertain papers, then list each paper's Notion page URL.

## Required Fields

Fill these properties for each paper:

- `Name`: full paper title.
- `Year`: publication year.
- `Publication`: conference, journal, or source such as `ISPD`, `DAC`, `ICCAD`, `ASP-DAC`, `IEEE TCAD`, `IEEE Access`, or `arXiv`.
- `Flow Design`: multi-select classification from paper content.
- `Field`: multi-select technical-topic classification from paper content.
- `Link`: Google Drive sharing link for the PDF, not a DOI and not a local path.
- `Comments`: 1-2 concise English sentences summarizing the main point, method, contribution, or reason to track the paper.
- `Status`: set to `Unread` for new entries.
- `Starred`: leave unchecked for new entries.

## Metadata Rules

Prefer evidence from the PDF itself: ACM/IEEE reference text, DOI, abstract, keywords, title block, and first page. If the metadata remains uncertain, look up the DOI or official publisher page when available, and mark uncertainty in the final report instead of guessing.

When the publication does not match an existing Notion option, choose the closest existing option. If none is appropriate, use `arXiv` when applicable or mention the actual venue in `Comments`.

Do not classify only from the filename. Use the abstract, keywords, contribution statement, and experimental context.

## Reference

Read `references/paper-database-rules.md` for taxonomy rules, deduplication checks, and output expectations.
