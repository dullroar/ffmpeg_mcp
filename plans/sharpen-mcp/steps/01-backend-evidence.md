---
id: 01-backend-evidence
status: pending
depends_on: []
touches:
  - docs/backend-notes.md
  - docs/README.md
  - plans/sharpen-mcp/steps/01-backend-evidence.md
lane: none
requirements: [R1]
gate: test -s docs/backend-notes.md && python3 scripts/check_context.py && git diff --check
evidence: ""
---

# Verify the backend capabilities

Read the installed `ffmpeg`, `ffprobe`, `ffmpeg-formats`, and `ffmpeg-filters` man pages. Inventory `ffmpeg -version`, `-encoders`, `-muxers`, and `-filters` in the Docker image. Record which profile/encoder pairs can actually work in supported builds. Confirm supported local subtitle formats and seek behavior empirically.

Build a small synthetic corpus in temporary storage. Record installed versions, official references with sections, real operation examples, output fields and tolerances, and options that do not work. Compare the proposed catalog against actual native behavior. For each tool, identify its finite parameter schema, numeric limits, output contract, examples, and the exact backend feature that supports it. Treat community examples as leads and verify behavior against the official backend and installed build.

Use ffprobe JSON as the authority for stream selection, video orientation, duration, and artifacts. Report selected streams and discarded subtitles/chapters explicitly. A profile fixes a compatible container, codec, and pixel/audio format. Legacy AVI→MPEG uses MPEG program stream with MPEG-2 video and a supported MPEG audio codec, verified on the pinned backend. Separate lossless remux from re-encoding. Define accurate trim separately from keyframe-limited copy. Use finite typed offsets and dimensions. Keep filters/concat manifests server-authored. Test media properties and tolerances instead of comparing encoded bytes across builds.

Prioritize profile compatibility, stream selection, seek semantics, and the measured properties of generated media.

Write the results to `docs/backend-notes.md` and link it from `docs/README.md`. Record the exact commands and results for successful and unsupported cases.

## Resume notes

Pending.
