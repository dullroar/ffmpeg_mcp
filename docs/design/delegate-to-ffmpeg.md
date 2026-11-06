---
gist: "Read when: tempted to reimplement codec, container or filter-graph behavior in Python, or to change how command output and errors are returned."
---

# Delegate media processing to FFmpeg

**Decision.** FFmpeg is the execution engine. The server validates and assembles common command shapes but does not duplicate codec, container, or filter-graph semantics in Python. Media properties come from ffprobe rather than being inferred from conversion output, and native command output or explicit errors are returned so callers keep diagnostic detail.

**Boundary.** The server assumes FFmpeg is installed on the host. It is not a media library, job queue, or sandbox for arbitrary untrusted command execution.
