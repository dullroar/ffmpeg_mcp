# Proposed ffmpeg_mcp methods

Each row is a bounded public workflow. Grouping controls implementation order. Confirm capabilities against the pinned Docker backend before advertising a method. Keep source provenance and unsupported cases visible in the shipped documentation.

## Core

| Tool | Use this when | Acceptance focus |
| --- | --- | --- |
| `probe` | Inspect a local file before editing. | ffprobe JSON with selected container, duration, dimensions, codec and audio/subtitle streams. |
| `convert_video` | Convert an old AVI to a legacy MPEG program stream, or prepare an MP4 for playback. | Fixed container/codec profiles with stream mapping. |
| `convert_audio` | Convert one recording or a folder of WAV files to FLAC or a podcast-friendly format. | Fixed audio profiles and bounded server-side batch. |
| `extract_audio` | Save the audio from an interview, or just a time range. | Selected audio stream and accurate offset/duration. |
| `compress_video` | Make a smaller sharing copy under a named size or quality policy. | Explicit encoder profile, output dimensions, and reported size. |
| `generate_thumbnail` | Extract a still at a supplied timestamp. | Single-frame output with bounds and documented out-of-range result. |
| `trim_media` | Cut a clip between two timestamps. | Accurate decode/trim and re-encode with verified output duration. |
| `resize_video` | Fit portrait or landscape video within a 720p frame. | Aspect-preserving scale with explicit fit or pad and even dimensions. |
| `remux_video` | Move compatible H.264/AAC streams into MP4 without re-encoding. | Stream copy after compatibility preflight. |

## Expanded

| Tool | Use this when | Acceptance focus |
| --- | --- | --- |
| `join_clips` | Combine ordered local clips into one shareable recording. | Server-owned concat with compatible copy or explicit normalization profile. |
| `normalize_audio` | Level a spoken recording before publication. | Two-pass loudnorm with measured output and speech preset. |
| `create_contact_sheet` | Review a recording using a grid of sampled frames. | Bounded sampling and server-generated tile filter. |
| `rotate_video` | Correct a sideways video. | Enumerated quarter turns, rotation metadata and display geometry tests. |
| `extract_subtitles` | Save one compatible text subtitle track as SRT. | Typed stream selector and a text-only output contract. |
| `burn_subtitles` | Deliver a captioned copy from a local SRT file. | Server-owned subtitle filter and supported build check. |
| `split_audio_channels` | Export left/right channels or make a mono listening copy. | Approved channel layouts only. |
| `create_waveform` | Render a preview of a short audio recording. | Bounded duration, dimensions, and approved showwaves settings. |
| `trim_silence` | Trim leading or trailing silence from voice recordings. | Fixed numeric threshold and measured before/after duration. |

## Primary references

- [FFmpeg CLI manual](https://ffmpeg.org/ffmpeg.html)
- [FFmpeg formats and muxers](https://ffmpeg.org/ffmpeg-formats.html)
- [FFmpeg filters, examples, and signal analysis](https://ffmpeg.org/ffmpeg-filters.html)
- [ffprobe JSON and stream inspection](https://ffmpeg.org/ffprobe.html)
- [FFmpeg Wiki scaling examples](https://trac.ffmpeg.org/wiki/Scaling)
