run-prod:
	docker-compose -f ./docker-compose.prod.yaml up --build
run-dev:
	docker-compose -f ./docker-compose.dev.yaml up --build
