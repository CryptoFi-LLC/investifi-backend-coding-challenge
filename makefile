# This command only works if a container is running
bash:
	docker compose -f ./docker/config/docker-compose.yaml run investifi-backend-coding-challenge bash

destroy:
	docker system prune -a --volumes

run:
	docker compose -f ./docker/config/docker-compose.yaml up --build

stop:
	docker compose -f ./docker/config/docker-compose.yaml down -v --remove-orphans

run-testsuite:
	docker compose -f ./docker/config/docker-compose.yaml run investifi-backend-coding-challenge python -m pytest