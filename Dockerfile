FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg git \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home app

WORKDIR /app
COPY requirements.txt ./
# server.py uses the FastMCP API from MCP 1.x.
RUN python -m pip install --no-cache-dir -r requirements.txt 'mcp<2'
COPY . .

USER app
# Prepare the shim cache for the pinned library. The test run has no network.
RUN python -c "import sys; sys.path.insert(0, 'scripts'); import check_context as c; spec, commit = c.pinned(); c.ensure_environment(spec, commit)"
CMD ["python", "server.py"]
