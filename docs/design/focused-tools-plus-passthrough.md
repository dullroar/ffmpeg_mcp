---
gist: "Read when: adding a curated tool, changing ffmpeg_passthrough, or expanding glob/batch handling and output naming."
---

# Focused tools plus an explicit passthrough

**Decision.** Provide focused tools for common operations and an explicit `ffmpeg_passthrough` escape hatch for advanced native syntax, so the curated API need not grow indefinitely. Input globs are expanded inside the server so one tool call can express batch work, reducing agent-tool chatter while keeping per-file output naming deterministic.

**Contradicted by.** Pressure to wrap every FFmpeg option as its own parameter.
