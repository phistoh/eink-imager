COMPOSE_DEV=docker/docker-compose.yml
COMPOSE_PROD=docker/docker-compose.prod.yml

dev:
	make init
	docker compose -f $(COMPOSE_DEV) up -d --build --force-recreate

up:
	make init
	docker compose -f $(COMPOSE_PROD) up -d

down:
	docker compose -f $(COMPOSE_DEV) down || true
	docker compose -f $(COMPOSE_PROD) down || true

init:
	mkdir -p data/{processed,failed,images}
	mkdir -p incoming
	touch data/metadata.db
	touch data/.initialized
	chown -R $(shell id -u):$(shell id -g) incoming data
