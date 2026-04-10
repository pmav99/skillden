#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path


DEFAULT_MOCS_DIR = Path.home() / "zettelkasten" / "MOCs"


def list_mocs(mocs_dir: Path) -> list[str]:
    if not mocs_dir.is_dir():
        raise FileNotFoundError(f"MOC directory does not exist: {mocs_dir}")

    return [path.stem for path in sorted(mocs_dir.glob("*.md"), key=lambda item: item.name.casefold())]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List available Obsidian MOCs from the local MOC directory.")
    parser.add_argument("--mocs-dir", type=Path, default=DEFAULT_MOCS_DIR)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    mocs = list_mocs(args.mocs_dir.expanduser())

    if args.format == "json":
        print(json.dumps(mocs, ensure_ascii=True, indent=2))
        return 0

    for moc in mocs:
        print(moc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
