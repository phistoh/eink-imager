FROM python:3.11-slim

ARG UID=1000
ARG GID=100
ARG USER=einker

WORKDIR /app

# install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# copy source code
COPY . .

# create folders
RUN mkdir -p \
/app/incoming \
/app/data/processed \
/app/data/failed \
/app/data/images
# fix permissions
RUN useradd -m -u ${UID} ${USER} \
&& chown -R ${UID}:${GID} /app

USER ${USER}

HEALTHCHECK --interval=30s \
	--timeout=3s \
	--start-period=10s \
	--retries=3 \
	CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"

CMD ["python", "-m", "einker.web"]
