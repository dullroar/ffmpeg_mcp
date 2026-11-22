"""Test a media conversion through the MCP stdio entry point."""

import json
import subprocess
import sys
import tempfile
import unittest
import wave
from datetime import timedelta
from pathlib import Path

import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


SERVER = Path(__file__).resolve().parents[1] / "server.py"
SAMPLE_RATE = 8_000
FRAME_COUNT = 800


class StdioTest(unittest.TestCase):
    def test_convert_audio_to_flac(self):
        with tempfile.TemporaryDirectory(prefix="ffmpeg-mcp-stdio-") as directory:
            source = Path(directory) / "input.wav"
            output = Path(directory) / "output.flac"
            with wave.open(str(source), "wb") as audio:
                audio.setnchannels(1)
                audio.setsampwidth(2)
                audio.setframerate(SAMPLE_RATE)
                audio.writeframes(b"\0\0" * FRAME_COUNT)

            anyio.run(self.convert_audio, source, output)

            result = subprocess.run(
                [
                    "ffprobe", "-v", "error", "-select_streams", "a:0",
                    "-show_entries", "stream=codec_name,sample_rate,channels,duration_ts",
                    "-of", "json", str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(json.loads(result.stdout)["streams"], [{
                "codec_name": "flac",
                "sample_rate": str(SAMPLE_RATE),
                "channels": 1,
                "duration_ts": FRAME_COUNT,
            }])

    async def convert_audio(self, source: Path, output: Path):
        server = StdioServerParameters(command=sys.executable, args=[str(SERVER)])
        with anyio.fail_after(30):
            async with stdio_client(server) as (reader, writer):
                async with ClientSession(
                    reader, writer, read_timeout_seconds=timedelta(seconds=20)
                ) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    self.assertEqual({tool.name for tool in tools.tools}, {
                        "compress_video", "convert_audio", "convert_video",
                        "extract_audio", "ffmpeg_passthrough", "generate_thumbnail",
                        "probe",
                    })
                    result = await session.call_tool("convert_audio", {
                        "input": str(source),
                        "output": str(output),
                        "output_format": "flac",
                    })
                    self.assertFalse(result.isError, result.content)
                    self.assertTrue(output.is_file(), result.content)
