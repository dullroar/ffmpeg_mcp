#!/usr/bin/env bash
# Run me when: I want to build the image and run the Docker checks for ffmpeg-mcp.
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
run_dir=$(mktemp -d "${TMPDIR:-/tmp}/ffmpeg-mcp-test.XXXXXXXX")
run_name=${run_dir##*/}
image="ffmpeg-mcp-test:${run_name##*.}"

cleanup() {
    docker image rm "$image" >/dev/null 2>&1 || true
    rmdir -- "$run_dir"
}
trap cleanup EXIT

docker build --tag "$image" "$repo_root"
docker run --rm --name "$run_name" --network none "$image" sh -ec '
    python -m unittest discover -s tests -v
    python scripts/check_context.py /app
'
