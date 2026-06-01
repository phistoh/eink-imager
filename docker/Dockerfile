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

ENTRYPOINT ["/entrypoint.sh"]

CMD ["python", "-m", "einker.web"]
