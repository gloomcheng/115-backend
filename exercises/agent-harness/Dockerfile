FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS test

COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY pytest.ini conftest.py main.py ./
COPY harness ./harness
COPY tests ./tests

CMD ["pytest", "-q"]

FROM base AS runtime

# The service runs as a user that owns nothing it does not need.
RUN useradd --create-home --uid 10001 appuser

COPY --chown=appuser:appuser main.py ./
COPY --chown=appuser:appuser harness ./harness

# The event log is the harness's memory. It lives on a volume, not in the
# image: an image is replaceable, a log is not.
ENV HARNESS_LOG=/var/lib/agent-harness/events.jsonl
RUN mkdir -p /var/lib/agent-harness && chown appuser:appuser /var/lib/agent-harness
VOLUME ["/var/lib/agent-harness"]

USER appuser

EXPOSE 8010

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8010/health')"

# HARNESS_SECRET is not baked into the image. It is given at run time.
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8010", "--proxy-headers", "--forwarded-allow-ips=*"]
