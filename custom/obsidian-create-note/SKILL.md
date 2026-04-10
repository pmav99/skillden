---
name: obsidian-create-note
description: 'Create a new note in the local Obsidian vault from a user-provided Markdown file. Use when Codex needs to import or add a Markdown document into `~/zettelkasten`: inspect available MOCs in `~/zettelkasten/MOCs`, preserve the file''s existing title when present, generate a title when missing, suggest a better title when the existing title is misleading, prefer reusing existing MOCs, create new MOC notes only when needed, create the note with the Obsidian CLI, and append the source Markdown verbatim.'
---

# Obsidian Create Note

## Overview

Create a note in the user's `zettelkasten` Obsidian vault from a source Markdown file. Keep the judgment calls in the agent loop, and use the helper scripts for the deterministic vault operations.

## Workflow

1. Confirm that the user provided a Markdown file path, then read the file before making any title or tag decisions.
2. Read [references/vault-conventions.md](references/vault-conventions.md) if you need to verify the vault path, vault name, MOC directory, or note template.
3. List the current MOC inventory with `python3 scripts/list_mocs.py`. Reuse existing MOCs exactly, including case and spacing.
4. Determine the title:
   - Prefer YAML frontmatter `title:` when present.
   - Otherwise use the first level-1 heading.
   - If no clear title exists, generate a concise retrieval-friendly title from the content.
   - If the existing title is weak or misleading, keep it by default but tell the user and suggest a better alternative before creating the note.
5. Choose MOCs:
   - Prefer 2-6 strong MOCs.
   - Reuse the existing MOC vocabulary whenever it fits.
   - Create a new MOC note only when no existing MOC or note captures an important concept.
   - Deduplicate MOCs and stay below 10.
   - Format MOCs later as wiki links such as `[[python]] [[snippet]]`.
6. Use [vendored/obsidian-cli/SKILL.md](vendored/obsidian-cli/SKILL.md) in order to create the document.
8. Use the provided source Markdown verbatim. Do not summarize it, strip sections, or rewrite headings before appending.
9. Report the created note path, the MOCs you applied, any new MOC notes you created, and any alternative title you suggested.

## Title Judgment

Prefer titles that are specific, searchable, and stable over time. Avoid filler like `notes`, raw export filenames, or dates unless the content genuinely requires them.

Keep the existing title when it is already representative, even if you can imagine a slightly better one. Only raise an alternative when the current title would materially hurt retrieval or mislead a future reader.

## MOC Judgment

Prefer concrete topic MOCs over vague workflow labels. For example, prefer `python`, `dem`, `dataset`, or `security` over generic buckets like `misc`.

Treat the local MOC list as the default vocabulary. When you must create a new MOC, keep it short, noun-like, and consistent with the existing corpus.

If the source Markdown contains code snippets, then include the `snippet` MOC + a `MOC` for the relevant programming languages (e.g. `python`).

## Resources

- `scripts/list_mocs.py`: list current MOC names from `~/zettelkasten/MOCs`
- `scripts/create_note.py`: create the note with the Obsidian CLI, ensure missing MOC notes exist when needed, set the `mocs:` line, and append the source Markdown
- `references/vault-conventions.md`: vault-specific details for this user's Obsidian setup
