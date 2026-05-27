"""FFmpeg Media Processing MCP Server

WHEN TO USE THIS SERVER
========================

Prefer these tools over writing subprocess calls to ffmpeg. This server handles
FFmpeg CLI syntax correctly, saves tokens by offloading encoding to FFmpeg itself,
and provides a promptable workflow for media tasks. Use ffmpeg_passthrough when
the pre-built tools don't cover the needed operation (filter graphs, multi-output,
two-pass encoding, stream mapping, etc.).

WORKED EXAMPLES
================

Convert MP4 to MKV and save beside original:
    convert_video("movie.mp4", "movie.mkv", output_format="mkv")

Extract audio from 30s to 90s in FLAC:
    extract_audio("movie.mp4", "audio.flac", timestamp="30", duration="60")

Generate thumbnail at 2:30:
    generate_thumbnail("movie.mp4", "thumb.jpg", timestamp="00:02:30")

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

import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("FFmpeg Media Processing Server")

# Check if ffmpeg is available
FFMPEG_PATH = None

def _get_ffmpeg_path():
    """Get the path to ffmpeg if available, None otherwise."""
    global FFMPEG_PATH
    if FFMPEG_PATH is None:
        try:
            result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=5)
            FFMPEG_PATH = "ffmpeg"
        except FileNotFoundError:
            FFMPEG_PATH = None
        except subprocess.TimeoutExpired:
            FFMPEG_PATH = None
    return FFMPEG_PATH


def _call_ffmpeg(args: list[str], timeout: int = 300) -> str:
    """Execute ffmpeg command and return output."""
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


@mcp.tool()
def convert_video(
    input: str,
    output: str,
    output_format: str = "mp4",
    quality_preset: str | None = None,
) -> str:
    """Convert video from one format to another.

    Parameters
    ----------
    input : str
        Path to the input video file.
    output : str
        Path to write the output file.
    output_format : str, default "mp4"
        Output format: mp4, mkv, avi, mov, webm, flv, wmv, m4v, 3gp, etc.
    quality_preset : str, optional
        Video quality/bitrate preset. Options:
        - "fast" - fast encoding, lower quality (h.264 fast)
        - "medium" - medium quality
        - "slow" - slower encoding, better quality
        - "veryfast" - very fast, lower quality
        - "superfast" - super fast, lowest quality
        - "ultrafast" - ultra fast, lowest quality
        - or omit for default quality

    Returns
    -------
    str
        Output from ffmpeg showing conversion progress and statistics.

    Examples
    --------
    Convert MP4 to MKV:
        convert_video("input.mp4", "output.mkv", output_format="mkv")

    Convert with faster encoding:
        convert_video("input.mp4", "output.mp4", output_format="mp4", quality_preset="fast")
    """
    args = ["-i", input, "-c:v", "libx264", "-c:a", "aac"]

    if quality_preset:
        preset_map = {
            "fast": "veryfast",
            "medium": "medium",
            "slow": "slow",
            "veryfast": "veryfast",
            "superfast": "superfast",
            "ultrafast": "ultrafast",
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

    Parameters
    ----------
    input : str
        Path to the input audio file.
    output : str
        Path to write the output file.
    output_format : str, default "mp3"
        Output format: mp3, flac, wav, aac, ogg, opus, m4a, wma, ac3.
    bitrate : str, default "192k"
        Bitrate for lossy formats (mp3, aac, ogg, opus, m4a, wma).
        Examples: "192k", "320k", "128k", "64k", "160k".
        For lossless formats (flac, wav), this is ignored.

    Returns
    -------
    str
        Output from ffmpeg showing conversion progress and statistics.

    Examples
    --------
    Convert FLAC to MP3:
        convert_audio("song.flac", "song.mp3", output_format="mp3", bitrate="320k")

    Convert WAV to FLAC (lossless):
        convert_audio("recording.wav", "recording.flac", output_format="flac")
    """
    args = [
        "-i", input,
    ]
    
    # Map output format to encoder
    encoder_map = {
        "mp3": "libmp3lame",
        "m4a": "aac",
        "aac": "aac",
        "ogg": "libvorbis",
        "opus": "libopus",
        "wma": "wmav2",
        "ac3": "ac3",
        "flac": "flac",
        "wav": "pcm_s16le",
    }
    
    encoder = encoder_map.get(output_format.lower(), "libmp3lame")
    args.extend(["-c:a", encoder])
    
    # Set bitrate for lossy formats
    if output_format.lower() in ["mp3", "m4a", "aac", "ogg", "opus", "wma", "ac3"]:
        args.extend(["-b:a", bitrate or "192k"])
    
    # Add output extension if not provided
    if not output.lower().endswith(output_format.lower()):
        output = output.rsplit(".", 1)[0] + f".{output_format}"
    
    args.extend([output])
    
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

    Parameters
    ----------
    input : str
        Path to the input video file.
    output : str
        Path to write the output audio file.
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

    Extract 60 seconds starting at 30 seconds:
        extract_audio("movie.mp4", "intro.mp3", timestamp="30", duration="60")
    """
    # Pre-input seek is faster; post-input is accurate — use pre-input here
    args = []
    if timestamp:
        args.extend(["-ss", timestamp])
    args.extend(["-i", input, "-vn"])

    encoder_map = {
        "mp3": "libmp3lame",
        "flac": "flac",
        "wav": "pcm_s16le",
        "aac": "aac",
        "ogg": "libvorbis",
        "opus": "libopus",
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

    Parameters
    ----------
    input : str
        Path to the input video file.
    output : str
        Path to write the output image file (will be saved as .jpg).
    timestamp : str, default "00:00:01"
        Timestamp in HH:MM:SS format to extract the frame.

    Returns
    -------
    str
        Output from ffmpeg showing frame extraction and image statistics.

    Examples
    --------
    Extract frame at 1 second:
        generate_thumbnail("movie.mp4", "thumbnail.jpg", timestamp="00:00:01")

    Extract frame at 2:30:
        generate_thumbnail("movie.mp4", "thumbnail.jpg", timestamp="00:02:30")
    """
    args = [
        "-i", input,
        "-ss", timestamp,
        "-vframes", "1",
        "-vf", "scale=320:-1",  # 320px width, maintain aspect ratio
        "-y",  # Overwrite output if exists
    ]
    
    # Add output extension if not provided
    if not output.lower().endswith(".jpg"):
        output = output.rsplit(".", 1)[0] + ".jpg"
    
    args.extend([output])
    
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

    Parameters
    ----------
    input : str
        Path to the input video file.
    output : str
        Path to write the output file.
    output_format : str, default "mp4"
        Output format: mp4, mkv, webm, mov.
    quality_preset : str, default "medium"
        FFmpeg preset controlling speed/quality tradeoff:
        - "ultrafast" - fastest, lowest quality
        - "superfast" - very fast, low quality
        - "veryfast" - fast, low-medium quality
        - "faster" - moderately fast
        - "fast" - fast, medium quality
        - "medium" - balanced (default)
        - "slow" - slow, better quality
        - "slower" - slower
        - "veryslow" - slowest, best quality
    max_bitrate : str, optional
        Maximum bitrate in kbps (e.g., "1000k" for 1 Mbps).
        If not provided, uses default bitrate based on resolution.

    Returns
    -------
    str
        Output from ffmpeg showing re-encoding progress and statistics.

    Examples
    --------
    Compress video with medium quality:
        compress_video("input.mp4", "output.mp4")

    Compress with fast encoding and max 800kb bitrate:
        compress_video("input.mp4", "output.mp4", quality_preset="fast", max_bitrate="800k")
    """
    args = [
        "-i", input,
        "-c:v", "libx264",
        "-preset", quality_preset,
        "-crf", "23",  # Constant Rate Factor (18-28, 23 is good balance)
        "-c:a", "aac",
    ]
    
    # Add bitrate if provided
    if max_bitrate:
        args.extend(["-b:v", max_bitrate])
    
    # Add audio bitrate
    args.extend(["-b:a", "128k"])
    
    # Add output extension if not provided
    if not output.lower().endswith(output_format.lower()):
        output = output.rsplit(".", 1)[0] + f".{output_format}"
    
    args.extend([output])
    
    return _call_ffmpeg(args)


@mcp.tool()
def probe(
    input: str,
) -> str:
    """Inspect a media file and return streams/format info (uses ffprobe).

    Parameters
    ----------
    input : str
        Path to the media file to probe.

    Returns
    -------
    str
        Formatted information about the media file including format, streams, metadata.

    Examples
    --------
    Probe a video file:
        probe("movie.mp4")
    """
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
