---
gist: "Read me when: you change, run or roll back the pinned deterministic-controls library, the check_context.py shim or the secret guard."
---

# Controls adoption

This repository runs the pinned `deterministic-controls` library in advisory mode. The CI job `controls` is not a required check yet.

## How it works

- `scripts/check_context.py` is a shim. It keeps the old output lines (`ok  <script>` or `FAIL <script>`) and the exit codes `0` and `1`. It accepts an optional root argument (the Docker run passes `/app`).
- `scripts/controls-requirements.txt` holds the pin: one install line with a full commit. The shim reads the commit from this file.
- `controls.toml` lists the enabled checks and the profile.
- The shim runs the library from a cached virtual environment. The path is `$XDG_CACHE_HOME/deterministic-controls/<commit>/` (default `~/.cache/deterministic-controls/<commit>/`).
- The first run for a commit needs the network. The shim builds the cache then.
- If the library cannot run, the shim exits `2`. It never passes without a result. It never falls back to the old scripts.
- The old check scripts stay in `scripts/`. The shim does not call them.

## How the adoption was made

1. Audit: step `a01-audit` wrote `docs/controls-audit.json` (read-only).
2. Plan: `adopt plan --commit <pin>` gave a dry run. It showed the files to write.
3. Apply: `adopt apply --commit <pin>` wrote the shim, the pin, `controls.toml` and the `controls` CI job. The step then added the Dockerfile change, the `AGENTS.md` rule and this document.

## Where the tools did not fit

- **Docker has no network.** The test container runs with `--network none`, so the shim cannot build its cache there. The `Dockerfile` now installs `git` (the pinned install needs it, and the secret guard test needs it). It also builds the shim cache at image build time as user `app`, because the cache is under that user's home. The run commands, `--network none`, the `CMD`, the requirements and the base image did not change.
- **`apply` wrote a file outside the step scope.** It rewrote `scripts/install_hooks.sh` (a `secretguard.path` fallback). That file is outside `touches`. It was restored to its earlier content. Apply it in a later, separate change if wanted.
- **`.dockerignore` is an allowlist.** `apply` does not know this. The image did not get `controls.toml`, so the check failed in the container with "manifest not found". The step added `!controls.toml`. The excludes for secrets did not change.
- **`apply` does not commit.** The step made the commit.
- **`apply` does not write this document.** It was written by hand.
- **The shim and the old scripts.** The old `scan_secrets.py` maps to two library checks. The shim groups library checks under the old script names for the output lines.

## Probes

Run date (UTC): 2026-11-24.

Each probe ran in its own clone of `HEAD` under `.probe/`. The command was `python3 -m deterministic_controls check --root <copy> --profile ci --format json` (the text format gave the same rule IDs). The real tree was not changed. The secret probe built its token at run time and committed it only in the clone. The token is not in this repository.

| Probe | Expected rule ID | Exit code | Result |
| --- | --- | --- | --- |
| Broken relative link in a Markdown file | `markdown.local-links` | 1 | Failed with `markdown.local-links.missing-file`. |
| Script changed, generated index not rebuilt | `context.index-freshness` | 1 | Failed with `context.index-freshness.stale`. |
| Plan step without `gate` | `plans.schema` | 1 | Failed with `plans.schema.missing-gate`. `plans.graph` also failed (a side effect of the changed step). |
| Synthetic token in a Markdown file (committed in the copy) | `security.secrets` | 1 | Failed with `security.secrets.aws-access-key-id`. `security.personal-data` also failed. |
| Tracked `driver.out` file | `repo.forbidden-artifacts` | 1 | Failed with `repo.forbidden-artifacts.tracked`. |
| Unreadable Markdown file (mode `000`) | none (internal error) | 3 | Did not pass. Two checks reported a `PermissionError` and the status was `error`. |
| Clean clone of `HEAD` | none | 0 | Passed. All seven checks passed. |
| Unreadable file restored (mode `644`) | none | 0 | Passed. |
| Shim `scripts/check_context.py` on the bad plan step | none | 1 | Printed `FAIL check_plan.py`. |
| Shim on the clean clone | none | 0 | Passed. |

## Rollback

Run date (UTC): 2026-11-24.

Test of the rollback path. There is no earlier pin, so the test used the pre-adoption scripts.

1. The base commit is the parent of the adoption commit (`step(adopt-controls/a02-apply): adopt pinned controls in advisory mode`). In a clone under `.probe/`, that commit ran its own `python3 scripts/check_context.py` on a clean tree. Exit code: `0`. All four old checks passed.
2. The new shim ran on a clean clone of `HEAD`. Exit code: `0`.

Both pass. The adoption can be removed without loss of the old checks.

Files of the adoption:

- Added: `controls.toml`, `scripts/controls-requirements.txt`, `docs/controls-adoption.md`.
- Changed: `scripts/check_context.py` (now a shim), `.github/workflows/context.yml` (new `controls` job), `Dockerfile` (installs `git`, builds the shim cache), `.dockerignore` (allows `controls.toml`), `AGENTS.md`, `docs/README.md`, `scripts/AGENTS.md`.
- Kept: the old check scripts, `scripts/test_docker.sh`, the tests, the `check` CI job and the Docker run commands.

Steps to roll back:

1. Option A, change the pin. Put the previous commit in the install line of `scripts/controls-requirements.txt`. Run `python3 scripts/check_context.py` once to build its environment.
2. Option B, remove the adoption. Create a new branch. Run `git revert` on the adoption commits. Revert the Dockerfile and `.dockerignore` changes too.
3. Run `python3 scripts/check_context.py`. It must pass.

The cache under `$XDG_CACHE_HOME/deterministic-controls/<commit>/` is safe to delete. The shim builds it again when needed.

## Receipt

Run date (UTC): 2026-11-24.

Command, run in a clean clone of `HEAD` under `.probe/`:

`python3 -m deterministic_controls adopt receipt --root <clean clone> --commit 3a2e9f3d95136958c54f73c831e84b971fc9a054`

```json
{
  "base_revision": "86629409e23d5985b00eaa51f83e9304f6e11707",
  "checks_run": [
    {"check_id": "context.index-freshness", "status": "passed"},
    {"check_id": "markdown.local-links", "status": "passed"},
    {"check_id": "plans.graph", "status": "passed"},
    {"check_id": "plans.schema", "status": "passed"},
    {"check_id": "repo.forbidden-artifacts", "status": "passed"},
    {"check_id": "security.personal-data", "status": "passed"},
    {"check_id": "security.secrets", "status": "passed"}
  ],
  "commands_kept": [
    "scripts/build_context_indexes.py",
    "scripts/build_indexes.py",
    "scripts/check_links.py",
    "scripts/check_plan.py",
    "scripts/ctx_common.py",
    "scripts/scan_context_secrets.py",
    "scripts/scan_secrets.py",
    "scripts/test_docker.sh",
    "test: python3 -m unittest discover -s tests",
    "test: docker build (Dockerfile)",
    "ci-job: check"
  ],
  "control_pin": "3a2e9f3d95136958c54f73c831e84b971fc9a054",
  "date": "2026-11-24",
  "enabled_checks": [
    "context.index-freshness",
    "markdown.local-links",
    "plans.graph",
    "plans.schema",
    "repo.forbidden-artifacts",
    "security.personal-data",
    "security.secrets"
  ],
  "enforcement_state": "advisory",
  "files_added": [],
  "files_changed": [],
  "profile": "ci",
  "repository": "good",
  "rollback": [
    "To restore the previous pin: edit scripts/controls-requirements.txt, put the previous commit in the install line, and run scripts/check_context.py once to build its environment.",
    "To remove the adoption: run 'git revert' on the adoption commit, or restore these files from the base revision with 'git checkout <base> -- <file>' and delete the files that were added.",
    "The cached environment is in the user cache directory under deterministic-controls/<commit>/. It is safe to delete."
  ],
  "schema_version": 1
}
```

Notes:

- The JSON is shortened in two places: some objects use one line, and the `rollback` texts omit the list of files and the full base revision. The other fields are as printed.
- `repository` is the name of the temporary clone, not the name of this repository.
- `files_added` and `files_changed` are empty in a clean clone. This is a known library defect. The list of adoption files is in the Rollback section.
- `enforcement_state` is `advisory`. The `controls` CI job is not a required check.

## Secret guard exceptions

none
