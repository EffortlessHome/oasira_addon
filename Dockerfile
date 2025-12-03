# Simple version - requires dashboard to be pre-built
FROM ghcr.io/home-assistant/aarch64-base:latest

RUN apk add --no-cache python3 py3-pip

COPY run.py /run.py
RUN chmod +x /run.py

COPY run.sh /run.sh
RUN chmod +x /run.sh

COPY cert.pem /root/.cloudflared/cert.pem
COPY cert.pem /cert.pem

# Copy requirements and install Python packages
COPY requirements.txt /requirements.txt

# Create and use a virtual environment for Python packages
RUN python3 -m venv /venv \
    && . /venv/bin/activate \
    && pip install --no-cache-dir -r /requirements.txt \
    && pip install --no-cache-dir aiohttp websockets==12.0 Brotli

ENV PATH="/venv/bin:$PATH"

CMD ["/run.sh"]
