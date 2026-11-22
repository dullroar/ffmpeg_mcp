---
id: 03-verify-integration
status: done
depends_on: [02-build-and-test]
touches:
  - plans/ralphify/steps/03-verify-integration.md
lane: none
requirements: [R3]
gate: python3 scripts/check_context.py && bash scripts/test_docker.sh && git diff --check
evidence: gate passed 2026-11-22 (driver-verified)
claimed_by: codex cli-default
claimed_at: "2026-11-22T20:34:42Z"
---

# 03-verify-integration

Depends on `02-build-and-test`. Update only the step file. Rerun the context and Docker gate from the integrated worktree as the driver would. Check the template and runner links in `AGENTS.md` and the structural-change rule. Verify README commands and the existing entry points. Record the worktree base commit, exact commands, build result, test counts or concrete smoke assertions, expected opt-in skips, real FUSE result where required, and UTC date. Keep logs outside Git. Gate: `python3 scripts/check_context.py && bash scripts/test_docker.sh && git diff --check`.

The driver writes its own `evidence` field. Put detailed test evidence in the body of the verification step and commit it. The parent verifies the final child commit and result. A green build alone cannot satisfy R2 or R3.

## Repository gate

Install the repo's Python requirements and FFmpeg with `ffprobe`. Add a deterministic stdio test under `tests/`. Use the MCP client to initialize and list tools, then probe or convert a tiny synthetic input and assert a property of the result with `ffprobe`. Use temporary files. Document the stdio container command with stdin open and the test entry point. Preserve existing tool names and arguments.

Run `git merge-base HEAD plan/ralphify` to identify the integrated base commit. Replace each pending value in the results below. For each passing check, put details after `PASS`. Include the actual Docker commands or image reference and test counts or concrete smoke results. Record `n/a` in the FUSE field for other repos. If a required test fails or skips, record that in resume notes and leave the result pending.

## Results

- Base commit: `f2f666d6481ebbb496f3cad9f741c14150622061` from `git merge-base HEAD plan/ralphify`.
- Commands: PASS. `python3 scripts/check_context.py && bash scripts/test_docker.sh && git diff --check` exited 0.
- Docker build: PASS. The test script ran `docker build --tag "$image" "$repo_root"` from the integrated worktree. It used `python:3.12-slim-bookworm` and reused cached dependency layers. The script removed the temporary image tag after the run.
- Tests: PASS. The container ran `python -m unittest discover -s tests -v` and `python scripts/check_context.py /app` as the application user with `--network none`. One test passed. The MCP client initialized, listed all seven tools, and converted a synthetic WAV file with `convert_audio`. `ffprobe` reported FLAC, one channel, 8 kHz, and 800 samples. The index, plan, link, and secret checks passed in the worktree and in the image.
- Skips: None. The test suite has no opt-in checks.
- FUSE: n/a.
- UTC date: 2026-11-22.

## README and agent contract

- PASS. The Docker README build and stdio launch worked with a temporary image tag and an empty temporary directory mounted at `/media`. The server returned an MCP `initialize` response with tool capabilities and exited when stdin closed.
- PASS. `python server.py --help` listed `--transport` with `stdio` and `sse`, as well as `--host` and `--port`. A Git comparison against the plan seed found no changes to `server.py` or `requirements.txt`.
- PASS. Both upstream links in `AGENTS.md` resolved through the GitHub API. The structural change rule requires agents to read both projects and account for their layout, plan format, generated indexes, worktree rules, and validation commands.
- PASS. The README Ralph commands match the local runner's help and option parser. The runner's summary helper reported two done steps and one pending step. Verification used the helper because the full runner commands can create worktrees.

## Resume notes

None.
