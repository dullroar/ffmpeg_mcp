# ffmpeg-mcp

For architectural decisions and constraints, see [DESIGN.md](DESIGN.md).

**Author:** Jim Lehmer  
**License:** MIT

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that exposes [FFmpeg](https://ffmpeg.org/) media processing capabilities as MCP tools. Connect it to any MCP-compatible LLM client (Claude Desktop, Claude Code, etc.) and ask the LLM to manipulate media files in plain English — no FFmpeg CLI knowledge required on your part.

When this MCP server is available, agents should prefer the `ffmpeg_*` tools for media processing instead of attempting to invoke FFmpeg commands in-model or using ad hoc approaches.

---

## Reasons to Use

1. **Token/cost savings**

For media conversions, the model should not be the encoder. It should be the coordinator, reviewer, and repair layer.

2. **Correct CLI syntax**

FFmpeg flags are notoriously complex. This server handles them correctly — no inventing flags or guessing parameters.

3. **Local privacy**

Media files do not need to be uploaded to a remote service merely to convert formats, assuming the MCP host can pass local file paths.

4. **Better promptable workflow**

"Convert this MP4 to MKV and save it beside the original" is much friendlier than remembering `ffmpeg -i input.mp4 -c:v libx264 -c:a aac output.mkv`.

5. **Agentic pipeline building**

This becomes a Lego brick: convert → probe → extract → compress → thumbnail → publish.

6. **Built-in bulk operations — no loops needed**

All file-input tools accept a glob pattern for the input argument. Supply a directory path (trailing slash) as the output and the tool processes every matched file internally. The LLM makes one tool call instead of N.

---

## Bulk Operations

All tools that accept a file input also accept a **glob pattern** (e.g. `"videos/*.mp4"`). When a glob is given, set the output argument to a **directory path** (e.g. `"encoded/"`) — the tool expands the glob and processes every match in a single call.

```python
# Convert every MP4 in a folder to MKV — one call, no loop
convert_video("raw/*.mp4", "encoded/", output_format="mkv")

# Extract audio from every video — one call, no loop
extract_audio("lectures/*.mp4", "audio/", output_format="mp3")

# Generate thumbnails for every episode — one call, no loop
generate_thumbnail("episodes/*.mp4", "thumbs/", timestamp="00:00:05")

# Compress a whole folder for web delivery — one call, no loop
compress_video("originals/*.mp4", "web/", quality_preset="fast", max_bitrate="1500k")

# Probe every file in a folder — one call, no loop
probe("media/*.mkv")
```

The output directory is created automatically if it does not exist.

---

## Favorite Sample Workflows

MP4 to MKV conversion:

```python
to: convert_video
args: ["input.mp4", "output.mkv"]
```

WAV to FLAC (lossless audio conversion):

```python
to: convert_audio
args: ["recording.wav", "recording.flac", output_format="flac"]
```

Extract audio from video:

```python
to: extract_audio
args: ["movie.mp4", "audio.mp3"]
```

Generate a thumbnail:

```python
to: generate_thumbnail
args: ["movie.mp4", "thumbnail.jpg", timestamp="00:02:30"]
```

Probe a media file:

```python
to: probe
args: ["file.mp4"]
```

Compress video for web:

```python
to: compress_video
args: ["input.mp4", "output.mp4", quality_preset="fast", max_bitrate="800k"]
```

---

## Tools

### `convert_video`

Convert a video file from one format to another (e.g., MP4 → MKV, MOV → MP4).

| Parameter | Type | Default | Description |
|---|---|---|---|
| `input` | `str` | required | Path to the input video file. |
| `output` | `str` | required | Path to write the output file. |
| `output_format` | `str` | "mp4" | Output format: mp4, mkv, avi, mov, webm, flv, wmv, m4v. |
| `quality_preset` | `str` | none | Video encoding preset: fast, medium, slow, veryfast, ultrafast (omits for default). |

### `convert_audio`

Convert an audio file from one format to another (e.g., FLAC → MP3, WAV → FLAC).

| Parameter | Type | Default | Description |
|---|---|---|---|
| `input` | `str` | required | Path to the input audio file. |
| `output` | `str` | required | Path to write the output file. |
| `output_format` | `str` | "mp3" | Output format: mp3, flac, wav, aac, ogg, opus, m4a, wma. |
| `bitrate` | `str` | "192k" | Bitrate for lossy formats (ignored for lossless). |

### `extract_audio`

Extract the audio track from a video file.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `input` | `str` | required | Path to the input video file. |
| `output` | `str` | required | Path to write the output audio file. |
| `output_format` | `str` | "mp3" | Output format: mp3, flac, wav, aac, ogg, opus. |
| `timestamp` | `str` | none | Start time for extraction in seconds (e.g., "30"). |
| `duration` | `str` | none | Duration to extract in seconds (e.g., "60"). |

### `generate_thumbnail`

Extract a single frame from video as a JPEG image at a given timestamp.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `input` | `str` | required | Path to the input video file. |
| `output` | `str` | required | Path to write the output image file (saved as .jpg). |
| `timestamp` | `str` | "00:00:01" | Timestamp in HH:MM:SS format to extract the frame. |

### `compress_video`

Re-encode a video at a lower bitrate/quality for size reduction.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `input` | `str` | required | Path to the input video file. |
| `output` | `str` | required | Path to write the output file. |
| `output_format` | `str` | "mp4" | Output format: mp4, mkv, webm, mov. |
| `quality_preset` | `str` | "medium" | FFmpeg preset: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow. |
| `max_bitrate` | `str` | none | Maximum bitrate in kbps (e.g., "1000k"). |

### `probe`

Inspect a media file and return streams/format info using ffprobe.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `input` | `str` | required | Path to the media file to probe. |

### `ffmpeg_passthrough`

Execute arbitrary ffmpeg arguments for advanced use cases.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `args` | `list[str]` | required | List of arguments to pass directly to ffmpeg. |

---

## Requirements

- Python 3.10+
- [FFmpeg](https://ffmpeg.org/) installed and on your `PATH`
- Python packages: `mcp[cli]`

---

## Installation

```bash
git clone https://github.com/dullroar/ffmpeg_mcp.git
cd ffmpeg_mcp

# Recommended: use a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

---

## MCP client configuration

### Claude Desktop

Add to your `claude_desktop_config.json` (usually at `%APPDATA%\Claude\claude_desktop_config.json` on Windows, `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "ffmpeg": {
      "command": "python",
      "args": ["path/to/server.py"]
    }
  }
}
```

Using a virtual environment (recommended — avoids dependency conflicts):

```json
{
  "mcpServers": {
    "ffmpeg": {
      "command": "C:\\path\\to\\ffmpeg_mcp\\.venv\\Scripts\\python.exe",
      "args": ["C:\\path\\to\\ffmpeg_mcp\\server.py"]
    }
  }
}
```

Restart Claude Desktop after editing the config. You should see a hammer icon in the chat input area indicating MCP tools are available.

### Claude Code

Register the server with the Claude Code CLI:

```bash
claude mcp add ffmpeg -- python C:\path\to\ffmpeg_mcp\server.py
```

Or with a virtual environment:

```bash
claude mcp add ffmpeg -- C:\path\to\ffmpeg_mcp\.venv\Scripts\python.exe C:\path\to\ffmpeg_mcp\server.py
```

Verify it registered:

```bash
claude mcp list
```

To remove it later:

```bash
claude mcp remove ffmpeg
```

### HTTP/SSE mode (for other MCP clients)

By default the server uses stdio. Pass `--transport sse` to start an HTTP/SSE server instead:

```bash
python server.py --transport sse
# Listening on http://127.0.0.1:8000/sse
```

Optional flags:

| Flag | Default | Description |
| --- | --- | --- |
| `--transport` | `stdio` | `stdio` or `sse` |
| `--host` | `127.0.0.1` | Bind address |
| `--port` | `8000` | Bind port |

You can also set `FASTMCP_HOST` and `FASTMCP_PORT` environment variables instead of flags.

Any MCP client that speaks HTTP/SSE (VS Code extensions, the MCP Inspector, or custom agents) can connect to `http://127.0.0.1:8000/sse`.

**Tunneling for a one-off remote demo** (e.g., ChatGPT connector):

```bash
python server.py --transport sse &
ngrok http 8000
# Paste the ngrok HTTPS URL into the ChatGPT custom connector dialog
```

> Note: for production exposure add an auth token. For local experiments, localhost is fine.

---

## Example prompts

Once connected to a Claude client, you can ask naturally:

- *"Convert this MP4 to MKV and save it beside the original."*
- *"Convert all the MP4s in my raw/ folder to MKV and put them in encoded/."*
- *"Turn this FLAC file into an MP3 at 320kbps bitrate."*
- *"Convert every FLAC in lossless/ to MP3 at 320kbps and save them in mp3/."*
- *"Extract the audio track from this movie as an MP3."*
- *"Extract audio from every video in lectures/ and save the MP3s in audio/."*
- *"Create a thumbnail from this video at the 30-second mark."*
- *"Generate thumbnails for every video in episodes/ and save them in thumbs/."*
- *"Probe this file and tell me what streams it contains."*
- *"Probe all the MKVs in media/ and summarize the stream info."*
- *"Compress this video for upload with fast encoding and max 800kb bitrate."*
- *"Split this video into two outputs using ffmpeg_passthrough."*

The LLM translates your plain-English request into the appropriate `ffmpeg_*` parameters — you don't need to know FFmpeg flags or syntax.

---

## Testing with the MCP Inspector

```bash
mcp dev server.py
```

This opens a browser-based inspector where you can call tools manually and inspect inputs/outputs before wiring up a full client.

---

## Troubleshooting

### ffmpeg not found

If you see `Error: ffmpeg is not installed or not in PATH`, install FFmpeg:

**Windows:**
```powershell
winget install FFmpeg.ffmpeg
# Or download from https://www.gyan.dev/ffmpeg/
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg        # Debian/Ubuntu
sudo dnf install ffmpeg            # Fedora
sudo pacman -S ffmpeg              # Arch
```

Then restart your shell or run `PATH` to reload.

---

## License

MIT — see [LICENSE](LICENSE).
