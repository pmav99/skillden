#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


DEFAULT_VAULT_NAME = "zettelkasten"
DEFAULT_VAULT_PATH = Path.home() / "zettelkasten"
DEFAULT_TEMPLATE = "Main Template"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create an Obsidian note from a source Markdown file.")
    parser.add_argument("--source", type=Path, required=True, help="Path to the source Markdown file.")
    parser.add_argument("--title", required=True, help="Title for the new note.")
    parser.add_argument("--mocs", nargs="*", default=[], help="MOCs to add to the note.")
    parser.add_argument("--tags", nargs="*", dest="legacy_tags", default=[], help=argparse.SUPPRESS)
    parser.add_argument("--vault-name", default=DEFAULT_VAULT_NAME)
    parser.add_argument("--vault-path", type=Path, default=DEFAULT_VAULT_PATH)
    parser.add_argument("--template", default=DEFAULT_TEMPLATE)
    return parser.parse_args()


def fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 1


def dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def validate_note_name(name: str, label: str) -> str:
    value = name.strip()
    if not value:
        raise ValueError(f"{label} must not be empty.")
    if "/" in value or "\\" in value:
        raise ValueError(f"{label} must not contain path separators: {value!r}")
    return value


def run_obsidian(vault_name: str, *args: str) -> str:
    command = ["obsidian", f"vault={vault_name}", *args]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        output = result.stderr.strip() or result.stdout.strip() or "unknown error"
        raise RuntimeError(f"Obsidian command failed: {' '.join(command)}\n{output}")
    return result.stdout


def find_existing_note(vault_path: Path, title: str) -> list[Path]:
    target_name = f"{title}.md"
    return sorted(path for path in vault_path.rglob("*.md") if path.name == target_name)


def resolve_note_path(vault_name: str, vault_path: Path, title: str) -> Path:
    output = run_obsidian(vault_name, "file", f"file={title}")
    for line in output.splitlines():
        key, separator, value = line.partition("\t")
        if separator and key == "path":
            note_path = vault_path / value.strip()
            if note_path.is_file():
                return note_path
            raise RuntimeError(f"Resolved note path does not exist on disk: {note_path}")
    raise RuntimeError(f"Could not resolve a note path for title {title!r}")


def ensure_moc_files(vault_path: Path, mocs_dir: Path, mocs: list[str]) -> list[Path]:
    created: list[Path] = []
    mocs_dir.mkdir(parents=True, exist_ok=True)
    for moc in mocs:
        moc_name = validate_note_name(moc, "MOC")
        if find_existing_note(vault_path, moc_name):
            continue
        moc_path = mocs_dir / f"{moc_name}.md"
        moc_path.touch()
        created.append(moc_path)
    return created


def replace_mocs_and_append_source(note_text: str, mocs: list[str], source_text: str) -> str:
    lines = note_text.splitlines()
    mocs_line = "mocs:"
    if mocs:
        mocs_line = "mocs: " + " ".join(f"[[{moc}]]" for moc in mocs)

    replaced = False
    for index, line in enumerate(lines):
        if line.startswith("mocs:") or line.startswith("tags:"):
            lines[index] = mocs_line
            replaced = True
            break

    if not replaced:
        if lines:
            lines = [lines[0], "", mocs_line, "", *lines[1:]]
        else:
            lines = [mocs_line]

    header = "\n".join(lines).rstrip("\n")
    source = source_text.rstrip("\n")
    return f"{header}\n\n{source}\n"


def main() -> int:
    args = parse_args()
    vault_path = args.vault_path.expanduser().resolve()
    mocs_dir = vault_path / "MOCs"

    try:
        title = validate_note_name(args.title, "Title")
        source_path = args.source.expanduser().resolve()
        if not source_path.is_file():
            return fail(f"Source file does not exist: {source_path}")
        if not vault_path.is_dir():
            return fail(f"Vault path does not exist: {vault_path}")

        raw_mocs = dedupe_preserve_order([*args.mocs, *args.legacy_tags])
        mocs = [validate_note_name(moc, "MOC") for moc in raw_mocs]
        existing = find_existing_note(vault_path, title)
        if existing:
            existing_paths = ", ".join(str(path) for path in existing)
            return fail(f"Refusing to create a duplicate note named {title!r}: {existing_paths}")

        created_mocs = ensure_moc_files(vault_path, mocs_dir, mocs)
        run_obsidian(args.vault_name, "create", f"name={title}", f"template={args.template}")

        note_path = resolve_note_path(args.vault_name, vault_path, title)
        note_text = note_path.read_text(encoding="utf-8")
        source_text = source_path.read_text(encoding="utf-8")
        updated_text = replace_mocs_and_append_source(note_text, mocs, source_text)
        note_path.write_text(updated_text, encoding="utf-8")

        print(f"note_path\t{note_path}")
        if created_mocs:
            print("created_mocs\t" + "\t".join(str(path) for path in created_mocs))
        else:
            print("created_mocs")
        return 0
    except (OSError, RuntimeError, ValueError) as error:
        return fail(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
