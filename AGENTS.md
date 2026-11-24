# Agent contract

A thin FastMCP adapter over the installed FFmpeg and ffprobe binaries.

## Standing rules

- Start work on a branch. Run plans in worktrees with their own branches. Keep runtime logs, locks,
  and usage records outside the repository.
- Write documents in Simplified Technical English. Use short sentences and consistent terms.
- Before changing this repository's structure, read [repo-template](https://github.com/dullroar/repo-template)
  and [ralph-looper](https://github.com/dullroar/ralph-looper). Account for their layout, plan format,
  generated indexes, worktree rules, and validation commands in the change.

## Load context in this order

1. Read this file.
2. Read `README.md`, `docs/README.md`, `memory/AGENTS.md`, `plans/AGENTS.md`, and `scripts/AGENTS.md`.
3. Open only the entries whose descriptions, **Read me when**, **Read when**, or **Run me when** lines match the task.
4. For a large file, search its headings and read only the relevant ranges.
5. Stop loading when the decision, intended files, constraints and validation method are known.

User instructions take precedence over repository guidance. When sources conflict, prefer: user
instruction, this file, `docs/design/`, the named plan, domain documentation and references,
`memory/`, implementation and tests, historical notes.

## Context ownership

- Universal rules belong here.
- Architectural reasons belong in `docs/design/` (one premise per file).
- Non-obvious findings that cost time to discover belong in `memory/` (one topic per file; edit the existing topic, do not append a rival).
- Execution state belongs in `plans/`; deterministic automation in `scripts/`.
- Give each routed Markdown file a `gist` in its front matter. Start the gist with `Read me when:`
  or `Read when:`. Add a `Run me when:` line to each script.
- Run `python3 scripts/build_indexes.py` to update indexes. Edit only the hand-written parts of an index.

Do not duplicate a fact across layers. Correct its canonical source.

## Planned work (spec-driven)

- Work only on a named plan in `plans/<plan>/` or an explicitly identified off-plan task. Copy
  `plans/for-each-plan/` to start a plan. State the goal and loop prompt in `goal.md`, the approach
  in `plan.md`, and numbered requirements and protected checks in `spec.md`. Give each step its
  own file in `steps/` and list the requirements that it covers.
- Once its spec is approved, proceed through the steps without asking permission for routine work. Failed tests and dead ends inside scope: diagnose, repair, continue. Return to the user only for a new decision: contradictory requirements, scope expansion, or an action outside the spec's delegated authority.
- Acceptance checks named in the spec are protected. Never weaken, skip or delete one to get green; if one cannot pass as written, escalate.
- Parallel steps must have no dependency between them and no overlapping `touches`; if independence is uncertain, serialize. After parallel steps merge, run the spec's combined validation.
- A step is done only with recorded evidence. Report unavailable verification honestly. Record work
  that remains and any blocker under **Resume notes** so another agent can continue from the files.
- Retiring a rule, correcting documentation, and tolerating a known violation are different outcomes; record which one (see `plans/for-each-plan/spec.md`).

## Controls

- Do not weaken the controls. You may run the local checks at any time. CI runs them in all cases. Do not change or disable the controls, the pin (`scripts/controls-requirements.txt`), `controls.toml` or the workflows to make an unrelated task pass. The driver checks the gate and `touches` of each step. A change to the gate or a file outside `touches` fails the step. Send each piece of work to the cheapest executor that can do it, and let the gate decide if the work is done. The full policy is at https://github.com/dullroar/ralph-looper/blob/main/docs/routing.md.

## Validation

Run the smallest check that proves the change, then `python3 scripts/check_context.py` for any change to context files.

## Safety

Do not commit credentials, personal data, personal filesystem paths or sensitive record-level examples. Use placeholders and aggregate evidence. Do not push, publish, force-push or add a remote without authorization.
