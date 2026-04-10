# skillden

Vendor and manage Agent Skills from upstream Git repositories, keep them in `./vendored/`, add your own skills in `./custom/`, then symlink both into Claude Code and Codex CLI.

## Quick start

```bash
./skillden add              # add a vendored skill to manifest.json
./skillden update-all       # fetch and refresh vendored skills
./skillden install          # symlink vendored and custom skills into target dirs
```

## Commands

### `./skillden list`

Fetch upstream state and show the status of every skill in the manifest.

### `./skillden update-all`

Fetch upstream changes and update every vendored skill.

### `./skillden update <name>`

Fetch upstream changes and update a single vendored skill.

### `./skillden add`

Interactively add a new vendored skill. Prompts for name, repo URL, upstream path, and ref, then writes a manifest entry with empty `commit` and `tree` values. Run `update` afterwards to fetch it into `./vendored/`.

### `./skillden install`

Symlink every skill from `./vendored/` and `./custom/` into `~/.claude/skills/` and `~/.codex/skills/`.

- Creates absolute symlinks using the skill's directory name.
- Idempotent -- re-running skips symlinks that are already correct.
- Removes stale symlinks that point into this repo's `vendored/` or `custom/` directories but whose skill no longer exists.
- Fails with exit 1 if duplicate skill names exist across `./vendored/` and `./custom/`.
- Fails with exit 1 if a skill name collides with an existing non-skillden entry in a target directory.

## Local layout

- `./vendored/<name>/` contains skills fetched from upstream repos and tracked in `manifest.json`.
- `./custom/<name>/` contains local skills you maintain by hand.
- `manifest.json` is vendored-only. The `path` field is the path inside the upstream repo, not the local path in this repo.

## Manifest

Sync state lives in `manifest.json`:

```json
{
  "skills": {
    "example": {
      "repo": "https://github.com/example/agent-skills.git",
      "path": "skills/example",
      "ref": "main",
      "commit": "",
      "tree": ""
    }
  }
}
```

| Field    | Description                                                    |
|----------|----------------------------------------------------------------|
| `repo`   | Upstream Git repository URL                                    |
| `path`   | Directory inside the upstream repo containing the skill        |
| `ref`    | Branch or tag to track                                         |
| `commit` | Pinned upstream commit currently installed                     |
| `tree`   | Git tree hash for the skill directory, used to detect changes  |

## How updates work

For each update the script shallow-clones the requested `ref`, sparse-checks out only the skill's directory, verifies it contains a `SKILL.md`, copies it into `./vendored/<name>`, and rewrites the pinned `commit` and `tree` in `manifest.json`. Repos that disappear upstream are reported and skipped rather than aborting the whole run.

## Why not subtrees or submodules

This repo tracks skills, not upstream repositories.

`skillden` vendors exactly the skill directory named in `manifest.json` and records the pinned upstream `commit` plus the directory `tree`. That keeps the local layout small and focused on the installed artifact.

Git submodules are a poor fit here because they attach an entire upstream repository at a fixed path in your working tree. That is awkward when one upstream repo contains many unrelated skills, or when you only want one nested directory from that repo.

Git subtrees are closer, but they still operate at the repository level and are designed around merging repository history into your own history. That adds Git-level complexity this tool does not need, and it still does not naturally model "track this one directory inside that repo and ignore the rest."

The current approach keeps the contract simple:

- `manifest.json` is the source of truth for vendored skills
- `vendored/` contains only the fetched skill directories
- `custom/` contains only local skills
- `install` works from the local skill directories, not from Git wiring

In short, submodules and subtrees solve repository composition. `skillden` solves directory-level skill vendoring.
