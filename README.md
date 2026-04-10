# Skill Sync

This directory vendors specific Agent Skills from upstream Git repositories.

The sync state lives in `manifest.json`.

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

- `name`: the key under `skills`
- `repo`: upstream Git repository URL
- `ref`: branch or tag used when checking for updates
- `path`: directory inside the upstream repo that contains the skill
- `commit`: exact upstream commit currently installed
- `tree`: exact Git tree hash for the synced directory, used to detect path-level updates

Usage:

```bash
./sync-skill
./sync-skill list
./sync-skill update-all
./sync-skill update <name>
./sync-skill add
```

Running `./sync-skill` without arguments prints the available subcommands.

`list`, `update-all`, and `update <name>` fetch upstream state before deciding what to print or update. Repos that disappear upstream are reported as status rows or skipped updates instead of aborting the whole run.

`add` prompts for a skill name, repo URL, upstream path, and ref, then writes a new manifest entry with empty `commit` and `tree` values.

For each update, the script fetches the requested `ref`, checks out only the requested directory, verifies that the result contains `SKILL.md`, copies it into `./skills/<name>`, and rewrites the pinned `commit` and `tree` values in `manifest.json`.
