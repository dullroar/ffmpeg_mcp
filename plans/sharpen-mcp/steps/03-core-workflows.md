---
id: 03-core-workflows
status: pending
depends_on: [02-tool-boundary]
touches:
  - server.py
  - mcp_tools/**
  - tests/**
  - requirements.txt
  - Dockerfile
  - scripts/test_docker.sh
  - plans/sharpen-mcp/steps/03-core-workflows.md
lane: none
requirements: [R3]
gate: bash scripts/test_docker.sh && python3 scripts/check_context.py && git diff --check
evidence: ""
---

# Deliver the core workflows

Implement every Core row of the [catalog](../catalog.md) with the schema and defaults documented in step 01. Preserve output semantics from supported existing workflows or record a migration mapping where the new contract is deliberately different.

Use ffprobe JSON as the authority for stream selection, video orientation, duration, and artifacts. Report selected streams and discarded subtitles/chapters explicitly. A profile fixes a compatible container, codec, and pixel/audio format. Legacy AVI→MPEG uses MPEG program stream with MPEG-2 video and a supported MPEG audio codec, verified on the pinned backend. Separate lossless remux from re-encoding. Define accurate trim separately from keyframe-limited copy. Use finite typed offsets and dimensions. Keep filters/concat manifests server-authored. Test media properties and tolerances instead of comparing encoded bytes across builds.

Each workflow needs a successful real backend case and at least one applicable failure or unsupported case. Use MCP stdio to test representative calls and validate generated file contents or measured properties. Cover the explicitly named headline scenario end to end.

## Resume notes

Pending.
