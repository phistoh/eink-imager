FROM python:3.11-slim

WORKDIR /app

# install dependencies first (for caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# copy source code
COPY . .

# default command overridden in docker-compose
CMD ["python", "-m", "app.web"]