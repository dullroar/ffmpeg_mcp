FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home app

WORKDIR /app
COPY requirements.txt ./
# server.py uses the FastMCP API from MCP 1.x.
RUN python -m pip install --no-cache-dir -r requirements.txt 'mcp<2'
COPY . .

USER app
CMD ["python", "server.py"]
