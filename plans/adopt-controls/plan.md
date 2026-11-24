---
gist: "Read me when: you adopt the pinned deterministic-controls library and the secret guard in ffmpeg_mcp, in advisory mode, with the existing Docker gate kept."
---

# Plan: adopt the pinned controls in ffmpeg_mcp

This file is the high-level plan. State requirements in [spec.md](./spec.md). The detail is in `steps/`. Every step is self-contained. Read this file for the shared facts.

## Approach

The repository came from `repo-template`. It has the old context checks (`scripts/check_context.py` and the scripts that it runs), a Dockerfile, `scripts/test_docker.sh` and a CI workflow with one job (`check`). The library `deterministic-controls` gives the same checks from one pinned release. `scripts/check_context.py` becomes a shim that runs the library. The adoption is advisory: the CI job is not required yet. Keep all existing scripts, gates and CI job names. Do not delete the old check scripts in this plan.

Order: secret guard first (a00), then a read-only audit (a01), then the adoption (a02), then probes, rollback and receipt (a03), then verification from a clean clone with the Docker gate (a04).

## Facts

- Library: `deterministic-controls` `v0.1.2`. Install line: `python3 -m pip install "deterministic-controls @ git+https://github.com/dullroar/deterministic-controls@3a2e9f3d95136958c54f73c831e84b971fc9a054"`. The commit is `3a2e9f3d95136958c54f73c831e84b971fc9a054`. Pass it as `--commit` to `adopt plan`.
- Commands: `python3 -m deterministic_controls {list,check,explain,version,adopt}`. `adopt` has `audit`, `plan`, `apply` and `receipt`. `check --root DIR --profile quick|ci|full [--format text|json] [--report FILE]`. Exit codes: `0` pass, `1` defects, `2` bad configuration, invocation or no result, `3` internal error. Use `--help` for details.
- **No installs in agent steps.** An agent session has no network and no install right. Do not create a virtual environment and do not run `pip install`. The operator puts a checkout of the pinned release on `PYTHONPATH`, so `python3 -m deterministic_controls ...` works in a step. If it does not work, write that under "Resume notes" and stop.
- The shim (`scripts/check_context.py`) runs the library from a cached virtual environment for the pinned commit, under `$XDG_CACHE_HOME/deterministic-controls/<commit>/` (default `~/.cache/...`). The first run for a commit needs the network. If the library cannot run, the shim exits `2`. It never passes without a result and never falls back to the old scripts.
- `adopt apply` works only on a clean tree and on the current branch. It never pushes. It is idempotent. Run it before any other edit of the step.
- `adopt apply` writes `scripts/controls-requirements.txt`. If that file has no `Run me when:` line in its first 25 lines, add one. Then `python3 scripts/build_indexes.py --check` passes.
- `adopt apply` does not write `docs/controls-adoption.md`. Write it by hand.
- `adopt apply` adds a `controls` job next to the existing job. It repeats the secret guard steps of the `check` job. Accept the repeat. Keep the existing job and their steps. Do not delete the old job in this plan.
- Do not compare literal versions or wheel digests in tests or docs. Assert behavior and exit codes.
- Run the full test suite that the step names before each commit, not only one test file.
- Routing in one sentence (for `AGENTS.md`): send each piece of work to the cheapest executor that can do it, and let the gate decide if the work is done.
- The first run of the shim for a commit needs the network. The operator runs it once before the wave, so the cache exists. If the library still cannot run, write that under "Resume notes" and stop.
- Baseline: the existing Docker gate passes at the base commit. If it fails before your change, write that under "Resume notes", set the status `blocked` and stop. Do not repair product code in this plan.
- Your session cannot run Docker, use `/dev/fuse` or write outside the worktree. The gate runs Docker and the clean clone. Run only what your session can run (for example `python3 scripts/secret_guard.py --history`, the host tests and the context checks).
- Scratch copies go in `.probe/` inside the worktree (the operator excludes it from Git). Delete `.probe/` before the gate.
- Base branch: `main`.

## Repository brief

This text is copied from the archived repository-specific Docker gates.

> Install the repo's Python requirements and FFmpeg with `ffprobe`. Add a deterministic stdio test under `tests/`. Use the MCP client to initialize and list tools, then probe or convert a tiny synthetic input and assert a property of the result with `ffprobe`. Use temporary files. Document the stdio container command with stdin open and the test entry point. Preserve existing tool names and arguments.

The Docker gate in the repository today is `bash scripts/test_docker.sh`. It builds the image (`Dockerfile`: `python:3.12-slim-bookworm`, FFmpeg, user `app`, workdir `/app`) and runs this in a container with `--network none`:

```bash
python -m unittest discover -s tests -v
python scripts/check_context.py /app
```

Keep this gate and its commands unchanged. Note that the Docker run passes `/app` as an argument to `check_context.py`. The shim must still work with that argument. If it does not, record it under "Where the tools did not fit" and fix the shim, not the run command.

Local rules:

- Keep the tool names and the tool arguments of the MCP server.
- The stdio test uses temporary files and a synthetic input. Do not add a binary file to the repository.
- Base branch: `main`.

## Steps

| Step | Executor | Goal | Depends on |
| --- | --- | --- | --- |
| [a00-secret-guard](./steps/a00-secret-guard.md) | cloud agent, light | Secret guard, hooks and a blocking CI step. | none |
| [a01-audit](./steps/a01-audit.md) | script | Read-only audit with the pinned library. | a00 |
| [a02-apply](./steps/a02-apply.md) | cloud agent | Adopt the library in advisory mode. Keep all gates. | a01 |
| [a03-probes](./steps/a03-probes.md) | cloud agent | Known-bad probes, rollback test and receipt. | a02 |
| [a04-verify](./steps/a04-verify.md) | cloud agent, light | Full gates from a clean clone, including Docker. | a03 |

## Parallelism

None. The steps run one after the other. Each step changes files that the next step reads.

## Risks

- **A secret is committed.** `a00` installs the guard first. Do not add an exception to pass a step. A new exception needs a reason and a fingerprint, and the owner reviews it.
- **The shim cannot get the library (no network).** Write that under "Resume notes" and stop. Do not change the gate. Do not use the old scripts as a replacement.
- **The Docker run has no network.** The shim cannot build its cache in the container. `a02` prepares the cache at image build time.
- **The audit says `blocked`.** `a01` fails. Stop for review. Do not force it.
- **The shim does not accept the `/app` argument.** The Docker run passes it. Make the shim accept it. Do not change the run command.
