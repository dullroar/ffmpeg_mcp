"""FFmpeg Media Processing MCP Server

WHEN TO USE THIS SERVER
========================

Prefer these tools over writing subprocess calls to ffmpeg. This server handles
FFmpeg CLI syntax correctly, saves tokens by offloading encoding to FFmpeg itself,
and provides a promptable workflow for media tasks. Use ffmpeg_passthrough when
the pre-built tools don't cover the needed operation (filter graphs, multi-output,
two-pass encoding, stream mapping, etc.).

BULK OPERATIONS (pass a glob, skip the loop)
=============================================

All file-input tools accept a glob pattern for the input argument. Supply a
directory path (trailing slash, e.g. "out/") as the output — the tool expands
the glob internally and processes every match in one call. This is almost always
the right choice for batch work: one tool call beats N sequential calls.

    convert_video("raw/*.mp4", "encoded/", output_format="mkv")
    convert_audio("sessions/*.flac", "mp3/", output_format="mp3", bitrate="320k")
    extract_audio("lectures/*.mp4", "audio/", output_format="mp3")
    compress_video("originals/*.mp4", "web/", quality_preset="fast", max_bitrate="1500k")
    generate_thumbnail("episodes/*.mp4", "thumbs/")
    probe("media/*.mkv")   # returns info for every matched file

WORKED EXAMPLES
================

Convert MP4 to MKV and save beside original:
    convert_video("movie.mp4", "movie.mkv", output_format="mkv")

Convert all MP4s in a folder to MKV (one call, no loop):
    convert_video("raw/*.mp4", "encoded/", output_format="mkv")

Extract audio from 30s to 90s in FLAC:
    extract_audio("movie.mp4", "audio.flac", timestamp="30", duration="60")

Extract audio from every video in a folder (one call, no loop):
    extract_audio("lectures/*.mp4", "audio/", output_format="mp3")

Generate thumbnail at 2:30:
    generate_thumbnail("movie.mp4", "thumb.jpg", timestamp="00:02:30")

Generate thumbnails for all videos in a folder (one call, no loop):
    generate_thumbnail("episodes/*.mp4", "thumbs/")

Compress video for web upload (fast, 800kb max):
    compress_video("input.mp4", "web.mp4", quality_preset="fast", max_bitrate="800k")

Normalize audio volume using loudnorm filter (passthrough):
    ffmpeg_passthrough([
        "-i", "input.mp4",
        "-af", "loudnorm",
        "-c:v", "copy",
        "output.mp4",
    ])

Two-pass encoding example (passthrough):
    ffmpeg_passthrough([
        "-i", "input.mp4",
        "-pass", "1",
        "-passlogfile", "pass",
        "-y",
        "-pass", "2",
        "-passlogfile", "pass",
        "output.mp4",
    ])

PASSTHROUGH GUIDANCE
=====================

Use ffmpeg_passthrough for advanced operations beyond the pre-built tools:
- Complex filter graphs (split, overlay, transpose, etc.)
- Multi-output scenarios (stream mapping with -map)
- Two-pass encoding patterns
- Custom audio/video filters (loudnorm, volumeter, eq, etc.)
- Copy streams without re-encoding (-c copy)
- CRF/custom bitrate control (-crf, -b:v)

Examples from native FFmpeg syntax:

1. Split video into two outputs:
   ffmpeg_passthrough([
       "-i", "input.mp4",
       "-filter_complex", "split[v0][v1]",
       "-map", "[v0]", "out1.mp4",
       "-map", "[v1]", "out2.mp4",
   ])

2. Normalize audio with loudnorm:
   ffmpeg_passthrough([
       "-i", "input.mp4",
       "-af", "loudnorm=I=-14:LR=0:TP=-1.5:NR=M:L=40",
       "-c:v", "copy",
       "-c:a", "aac",
       "output.mp4",
   ])

3. Two-pass encoding for consistent quality:
   ffmpeg_passthrough([
       "-i", "input.mp4",
       "-pass", "1",
       "-passlogfile", "pass",
       "-pass", "2",
       "output.mp4",
   ])

See README.md for full tool reference and configuration options.
"""

import glob as _glob
import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("FFmpeg Media Processing Server")

FFMPEG_PATH = None


def _get_ffmpeg_path():
    global FFMPEG_PATH
    if FFMPEG_PATH is None:
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=5)
            FFMPEG_PATH = "ffmpeg"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            FFMPEG_PATH = None
    return FFMPEG_PATH


def _call_ffmpeg(args: list[str], timeout: int = 300) -> str:
    if _get_ffmpeg_path() is None:
        return "Error: ffmpeg is not installed or not in PATH. Please install ffmpeg: https://ffmpeg.org/download.html"
    try:
        result = subprocess.run(
            ["ffmpeg", "-y"] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stderr or result.stdout
    except subprocess.TimeoutExpired:
        return "Error: ffmpeg command timed out"
    except Exception as e:
        return f"Error: {e}"


def _expand(pattern: str) -> list[str]:
    """Expand a glob pattern; return [pattern] if no wildcards."""
    if any(c in pattern for c in ("*", "?", "[")):
        return sorted(_glob.glob(pattern, recursive=True))
    return [pattern]


def _bulk_out(src: str, output_dir: str, ext: str) -> str:
    """Derive per-file output path for bulk operations."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    return str(out / f"{Path(src).stem}.{ext}")


@mcp.tool()
def convert_video(
    input: str,
    output: str,
    output_format: str = "mp4",
    quality_preset: str | None = None,
) -> str:
    """Convert video from one format to another.

    Accepts a glob pattern for `input` to process multiple files in one call.
    When using a glob, set `output` to a directory path (e.g. "encoded/") and the
    tool places each converted file there — no loop needed.

    Parameters
    ----------
    input : str
        Path to the input video file, or a glob pattern (e.g. "raw/*.mp4").
    output : str
        Path to write the output file, or a directory path when input is a glob.
    output_format : str, default "mp4"
        Output format: mp4, mkv, avi, mov, webm, flv, wmv, m4v, 3gp, etc.
    quality_preset : str, optional
        Video quality/bitrate preset: fast, medium, slow, veryfast, superfast, ultrafast.

    Returns
    -------
    str
        Output from ffmpeg showing conversion progress and statistics.

    Examples
    --------
    Convert MP4 to MKV:
        convert_video("input.mp4", "output.mkv", output_format="mkv")

    Convert all MP4s in a folder to MKV (one call, no loop):
        convert_video("raw/*.mp4", "encoded/", output_format="mkv")
    """
    files = _expand(input)
    if len(files) > 1:
        results = []
        for f in files:
            out = _bulk_out(f, output, output_format)
            results.append(f"[{Path(f).name}] → {Path(out).name}\n" + _convert_video_one(f, out, output_format, quality_preset))
        return "\n\n".join(results)
    return _convert_video_one(input, output, output_format, quality_preset)


def _convert_video_one(input: str, output: str, output_format: str, quality_preset: str | None) -> str:
    args = ["-i", input, "-c:v", "libx264", "-c:a", "aac"]
    if quality_preset:
        preset_map = {
            "fast": "veryfast", "medium": "medium", "slow": "slow",
            "veryfast": "veryfast", "superfast": "superfast", "ultrafast": "ultrafast",
        }
        preset = preset_map.get(quality_preset.lower(), quality_preset.lower())
        if preset:
            args.extend(["-preset", preset])
    if not output.lower().endswith(output_format.lower()):
        output = output.rsplit(".", 1)[0] + f".{output_format}"
    args.append(output)
    return _call_ffmpeg(args)


@mcp.tool()
def convert_audio(
    input: str,
    output: str,
    output_format: str = "mp3",
    bitrate: str | None = "192k",
) -> str:
    """Convert audio from one format to another (e.g., FLAC to MP3, WAV to FLAC).

    Accepts a glob pattern for `input` to process multiple files in one call.
    When using a glob, set `output` to a directory path (e.g. "mp3/").

    Parameters
    ----------
    input : str
        Path to the input audio file, or a glob pattern (e.g. "lossless/*.flac").
    output : str
        Path to write the output file, or a directory path when input is a glob.
    output_format : str, default "mp3"
        Output format: mp3, flac, wav, aac, ogg, opus, m4a, wma, ac3.
    bitrate : str, default "192k"
        Bitrate for lossy formats. Examples: "192k", "320k", "128k".
        Ignored for lossless formats (flac, wav).

    Returns
    -------
    str
        Output from ffmpeg showing conversion progress and statistics.

    Examples
    --------
    Convert FLAC to MP3:
        convert_audio("song.flac", "song.mp3", output_format="mp3", bitrate="320k")

    Convert all FLACs in a folder to MP3 (one call, no loop):
        convert_audio("lossless/*.flac", "mp3/", output_format="mp3", bitrate="320k")
    """
    files = _expand(input)
    if len(files) > 1:
        results = []
        for f in files:
            out = _bulk_out(f, output, output_format)
            results.append(f"[{Path(f).name}] → {Path(out).name}\n" + _convert_audio_one(f, out, output_format, bitrate))
        return "\n\n".join(results)
    return _convert_audio_one(input, output, output_format, bitrate)


def _convert_audio_one(input: str, output: str, output_format: str, bitrate: str | None) -> str:
    args = ["-i", input]
    encoder_map = {
        "mp3": "libmp3lame", "m4a": "aac", "aac": "aac", "ogg": "libvorbis",
        "opus": "libopus", "wma": "wmav2", "ac3": "ac3", "flac": "flac", "wav": "pcm_s16le",
    }
    encoder = encoder_map.get(output_format.lower(), "libmp3lame")
    args.extend(["-c:a", encoder])
    if output_format.lower() in ["mp3", "m4a", "aac", "ogg", "opus", "wma", "ac3"]:
        args.extend(["-b:a", bitrate or "192k"])
    if not output.lower().endswith(output_format.lower()):
        output = output.rsplit(".", 1)[0] + f".{output_format}"
    args.append(output)
    return _call_ffmpeg(args)


@mcp.tool()
def extract_audio(
    input: str,
    output: str,
    output_format: str = "mp3",
    timestamp: str | None = None,
    duration: str | None = None,
) -> str:
    """Extract audio track from a video file.

    Accepts a glob pattern for `input` to process multiple files in one call.
    When using a glob, set `output` to a directory path (e.g. "audio/").
    The timestamp/duration parameters apply identically to every matched file.

    Parameters
    ----------
    input : str
        Path to the input video file, or a glob pattern (e.g. "lectures/*.mp4").
    output : str
        Path to write the output audio file, or a directory path when input is a glob.
    output_format : str, default "mp3"
        Output format: mp3, flac, wav, aac, ogg, opus.
    timestamp : str, optional
        Start time for extraction in seconds (e.g., "30" for 30 seconds in).
    duration : str, optional
        Duration to extract in seconds (e.g., "60" for 60 seconds).

    Returns
    -------
    str
        Output from ffmpeg showing extraction progress and statistics.

    Examples
    --------
    Extract entire audio track:
        extract_audio("movie.mp4", "audio.mp3", output_format="mp3")

    Extract audio from all videos in a folder (one call, no loop):
        extract_audio("lectures/*.mp4", "audio/", output_format="mp3")
    """
    files = _expand(input)
    if len(files) > 1:
        results = []
        for f in files:
            out = _bulk_out(f, output, output_format)
            results.append(f"[{Path(f).name}] → {Path(out).name}\n" + _extract_audio_one(f, out, output_format, timestamp, duration))
        return "\n\n".join(results)
    return _extract_audio_one(input, output, output_format, timestamp, duration)


def _extract_audio_one(input: str, output: str, output_format: str, timestamp: str | None, duration: str | None) -> str:
    # Pre-input seek is faster; post-input is accurate — use pre-input here
    args = []
    if timestamp:
        args.extend(["-ss", timestamp])
    args.extend(["-i", input, "-vn"])
    encoder_map = {
        "mp3": "libmp3lame", "flac": "flac", "wav": "pcm_s16le",
        "aac": "aac", "ogg": "libvorbis", "opus": "libopus",
    }
    encoder = encoder_map.get(output_format.lower(), "libmp3lame")
    args.extend(["-c:a", encoder])
    if output_format.lower() in ["mp3", "aac", "ogg", "opus"]:
        args.extend(["-b:a", "192k"])
    if duration:
        args.extend(["-t", duration])
    if not output.lower().endswith(output_format.lower()):
        output = output.rsplit(".", 1)[0] + f".{output_format}"
    args.append(output)
    return _call_ffmpeg(args)


@mcp.tool()
def generate_thumbnail(
    input: str,
    output: str,
    timestamp: str = "00:00:01",
) -> str:
    """Extract a single frame from video as an image at a given timestamp.

    Accepts a glob pattern for `input` to generate thumbnails for multiple videos
    in one call. When using a glob, set `output` to a directory path (e.g. "thumbs/").

    Parameters
    ----------
    input : str
        Path to the input video file, or a glob pattern (e.g. "episodes/*.mp4").
    output : str
        Path to write the output image file (saved as .jpg), or a directory path
        when input is a glob.
    timestamp : str, default "00:00:01"
        Timestamp in HH:MM:SS format to extract the frame.

    Returns
    -------
    str
        Output from ffmpeg showing frame extraction and image statistics.

    Examples
    --------
    Extract frame at 2:30:
        generate_thumbnail("movie.mp4", "thumbnail.jpg", timestamp="00:02:30")

    Generate thumbnails for all videos in a folder (one call, no loop):
        generate_thumbnail("episodes/*.mp4", "thumbs/", timestamp="00:00:05")
    """
    files = _expand(input)
    if len(files) > 1:
        results = []
        for f in files:
            out = _bulk_out(f, output, "jpg")
            results.append(f"[{Path(f).name}] → {Path(out).name}\n" + _generate_thumbnail_one(f, out, timestamp))
        return "\n\n".join(results)
    return _generate_thumbnail_one(input, output, timestamp)


def _generate_thumbnail_one(input: str, output: str, timestamp: str) -> str:
    args = [
        "-i", input,
        "-ss", timestamp,
        "-vframes", "1",
        "-vf", "scale=320:-1",
        "-y",
    ]
    if not output.lower().endswith(".jpg"):
        output = output.rsplit(".", 1)[0] + ".jpg"
    args.append(output)
    return _call_ffmpeg(args)


@mcp.tool()
def compress_video(
    input: str,
    output: str,
    output_format: str = "mp4",
    quality_preset: str = "medium",
    max_bitrate: str | None = None,
) -> str:
    """Re-encode video at a lower bitrate/quality for size reduction.

    Accepts a glob pattern for `input` to compress multiple files in one call.
    When using a glob, set `output` to a directory path (e.g. "compressed/").

    Parameters
    ----------
    input : str
        Path to the input video file, or a glob pattern (e.g. "originals/*.mp4").
    output : str
        Path to write the output file, or a directory path when input is a glob.
    output_format : str, default "mp4"
        Output format: mp4, mkv, webm, mov.
    quality_preset : str, default "medium"
        FFmpeg preset controlling speed/quality tradeoff:
        ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow.
    max_bitrate : str, optional
        Maximum bitrate in kbps (e.g., "1000k" for 1 Mbps).

    Returns
    -------
    str
        Output from ffmpeg showing re-encoding progress and statistics.

    Examples
    --------
    Compress video with medium quality:
        compress_video("input.mp4", "output.mp4")

    Compress all videos in a folder for web (one call, no loop):
        compress_video("originals/*.mp4", "web/", quality_preset="fast", max_bitrate="1500k")
    """
    files = _expand(input)
    if len(files) > 1:
        results = []
        for f in files:
            out = _bulk_out(f, output, output_format)
            results.append(f"[{Path(f).name}] → {Path(out).name}\n" + _compress_video_one(f, out, output_format, quality_preset, max_bitrate))
        return "\n\n".join(results)
    return _compress_video_one(input, output, output_format, quality_preset, max_bitrate)


def _compress_video_one(input: str, output: str, output_format: str, quality_preset: str, max_bitrate: str | None) -> str:
    args = [
        "-i", input,
        "-c:v", "libx264",
        "-preset", quality_preset,
        "-crf", "23",  # Constant Rate Factor (18-28, 23 is good balance)
        "-c:a", "aac",
    ]
    if max_bitrate:
        args.extend(["-b:v", max_bitrate])
    args.extend(["-b:a", "128k"])
    if not output.lower().endswith(output_format.lower()):
        output = output.rsplit(".", 1)[0] + f".{output_format}"
    args.append(output)
    return _call_ffmpeg(args)


@mcp.tool()
def probe(
    input: str,
) -> str:
    """Inspect a media file and return streams/format info (uses ffprobe).

    Accepts a glob pattern for `input` to probe multiple files in one call.

    Parameters
    ----------
    input : str
        Path to the media file to probe, or a glob pattern (e.g. "media/*.mkv").

    Returns
    -------
    str
        Formatted information about the media file(s) including format, streams, metadata.

    Examples
    --------
    Probe a video file:
        probe("movie.mp4")

    Probe all MKV files in a folder (one call, no loop):
        probe("media/*.mkv")
    """
    files = _expand(input)
    if len(files) > 1:
        results = []
        for f in files:
            results.append(f"=== {Path(f).name} ===\n" + _probe_one(f))
        return "\n\n".join(results)
    return _probe_one(input)


def _probe_one(input: str) -> str:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_format", "-show_streams", input],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout or result.stderr
    except FileNotFoundError:
        return "Error: ffprobe is not installed. It ships with ffmpeg — install ffmpeg: https://ffmpeg.org/download.html"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def ffmpeg_passthrough(
    args: list[str],
) -> str:
    """Execute arbitrary ffmpeg arguments for advanced use cases.

    Parameters
    ----------
    args : list[str]
        List of arguments to pass directly to ffmpeg. Example:
        ["-i", "input.mp4", "-filter_complex", "split[v0][v1]", "-map", "[v0]", "output1.mp4", "-map", "[v1]", "output2.mp4"]

    Returns
    -------
    str
        Output from ffmpeg showing the result of the command.

    Examples
    --------
    Split a video into multiple outputs:
        ffmpeg_passthrough([
            "-i", "input.mp4",
            "-filter_complex", "split[v0][v1]",
            "-map", "[v0]", "output1.mp4",
            "-map", "[v1]", "output2.mp4",
        ])

    Add audio filter (normalize volume):
        ffmpeg_passthrough([
            "-i", "input.mp4",
            "-af", "loudnorm",
            "-c:v", "copy",
            "output.mp4",
        ])
    """
    if _get_ffmpeg_path() is None:
        return "Error: ffmpeg is not installed or not in PATH. Please install ffmpeg: https://ffmpeg.org/download.html"
    try:
        result = subprocess.run(
            ["ffmpeg"] + args,
            capture_output=True,
            text=True,
            timeout=300,
        )
        return result.stderr or result.stdout
    except subprocess.TimeoutExpired:
        return "Error: ffmpeg command timed out"
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="FFmpeg Media Processing MCP server")
    parser.add_argument(
        "--transport",
        default="stdio",
        choices=["stdio", "sse"],
        help="stdio (default) for Claude Desktop/Code; sse for HTTP/SSE clients",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind host for SSE transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Bind port for SSE transport (default: 8000)",
    )
    args = parser.parse_args()

    if args.transport == "sse":
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.run(transport="sse")
    else:
        mcp.run()
