FROM python:3.11-slim

ARG UID=1000
ARG GID=100
ARG USER=einker

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN useradd -m -u ${UID} -U ${USER}

COPY --chown=${USER}:${USER} . .
COPY --chmod=755 docker/entrypoint.sh /entrypoint.sh

USER ${USER}

HEALTHCHECK --interval=30s \
	--timeout=3s \
	--start-period=10s \
	--retries=3 \
	CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"

ENTRYPOINT ["/entrypoint.sh"]

CMD ["python", "-m", "einker.web"]
