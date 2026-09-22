# DESIGN.md

# ffmpeg-mcp Design

## Boundary

The server is a thin FastMCP adapter over installed FFmpeg and ffprobe binaries. README.md describes installation and tool use; this document records why the server delegates rather than reimplements media processing.

## Core decisions

- Use FFmpeg as the execution engine. The MCP server validates and assembles common command shapes but does not attempt to duplicate codec, container, or filter-graph semantics in Python.
- Provide focused tools for common operations and an explicit `ffmpeg_passthrough` escape hatch for advanced native syntax. The escape hatch avoids expanding a curated API indefinitely.
- Expand input globs inside the server. A single tool call can express batch work, reducing agent-tool chatter while retaining deterministic per-file output naming.
- Probe media with ffprobe rather than infer media properties from conversion output.
- Return native command output or explicit errors so callers retain diagnostic detail.

## Constraints

The server assumes FFmpeg is installed on the host. It is not a media library, job queue, or sandbox for arbitrary untrusted command execution.


