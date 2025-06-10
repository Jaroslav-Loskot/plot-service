APP_NAME=plot-service
DOCKER_TAG=plot-service:latest

build:
	docker build -t $(DOCKER_TAG) .

run:
	docker run -p 8000:8000 --rm $(DOCKER_TAG)

run-detached:
	docker run -d -p 8000:8000 --name $(APP_NAME) $(DOCKER_TAG)

stop:
	docker stop $(APP_NAME) || true
	docker rm $(APP_NAME) || true

logs:
	docker logs -f $(APP_NAME)

compose-up:
	docker compose up --build

compose-down:
	docker compose down

test-help:
	curl http://localhost:8000/help | jq

test-health:
	curl http://localhost:8000/health
