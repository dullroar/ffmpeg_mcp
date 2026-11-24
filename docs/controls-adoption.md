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
- **`apply` does not commit.** The step made the commit.
- **`apply` does not write this document.** It was written by hand.
- **The shim and the old scripts.** The old `scan_secrets.py` maps to two library checks. The shim groups library checks under the old script names for the output lines.

## Secret guard exceptions

none
