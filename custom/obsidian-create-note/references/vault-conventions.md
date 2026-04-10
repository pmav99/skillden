# Vault Conventions

- Vault name: `zettelkasten`
- Vault path: `/home/panos/zettelkasten`
- Existing MOCs live in `/home/panos/zettelkasten/MOCs`
- Existing MOCs are represented by Markdown files named `<moc>.md`. Many MOC files are empty. Creating a new MOC means creating a new file in `MOCs/`.
- The note template folder is `Templates`
- The note template name to use with the CLI is either `Main` or `Simple`. Use `Simple` if the document already has a title, `Main` otherwise.

Current template body:

```md
{{date}}T{{time}}

mocs:

## {{Title}}
```

MOC syntax inside notes:

```md
mocs: [[python]] [[snippet]] [[dem]]
```

Useful commands:

```bash
python3 scripts/list_mocs.py
python3 scripts/create_note.py --source /path/to/source.md --title "My Title" --mocs python snippet
obsidian vault=zettelkasten file file="My Title"
```

`obsidian vault=zettelkasten file file="<title>"` returns a TSV-like block that includes a `path` row. The `path` value is relative to the vault root and can be joined with `/home/panos/zettelkasten` to get the concrete file path.
