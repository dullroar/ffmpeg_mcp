---
gist: "Read when: changing the repository's design, boundaries or dependencies, or before simplifying a deliberate seam."
---

# Architecture premises

One durable design decision per file: the constraint, the choice, why, and what would contradict it. Open only the premise whose **Read when** line matches the task.

<!-- BEGIN GENERATED CONTEXT INDEX -->

* [delegate-to-ffmpeg.md](./delegate-to-ffmpeg.md).
  Read when: tempted to reimplement codec, container or filter-graph behavior in Python, or to change how command output and errors are returned.
* [focused-tools-plus-passthrough.md](./focused-tools-plus-passthrough.md).
  Read when: adding a curated tool, changing ffmpeg_passthrough, or expanding glob/batch handling and output naming.

<!-- END GENERATED CONTEXT INDEX -->
