COMPOSE_DEV=docker-compose.yml
COMPOSE_PROD=docker-compose.prod.yml

dev:
	make init
	docker compose up -d --build -f $(COMPOSE_DEV)

up:
	make init
	docker compose up -d -f $(COMPOSE_PROD)

down:
	$(COMPOSE_DEV) down || true
	$(COMPOSE_PROD) down || true

init:
	mkdir -p data/{incoming,processed,failed,images}
	touch data/metadata.db
	touch data/.initialized
	chown -R $(shell id -u):$(shell id -g) data
