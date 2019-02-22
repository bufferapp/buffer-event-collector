IMAGE_NAME:=bufferapp/events-collector:0.4.0

.PHONY: all
all: run

.PHONY: run
run:
	docker run --env-file .env -p 50051:50051 --rm $(IMAGE_NAME)

.PHONY: build
build:
	 docker build . -t $(IMAGE_NAME)

.PHONY: push
push:
	 docker push $(IMAGE_NAME)

.PHONY: dev
dev:
	docker run -it -e ENV=dev --env-file .env -p 50051:50051 --rm -v `pwd`:/usr/src/app $(IMAGE_NAME) /bin/bash

.PHONY: deploy
deploy: build push
	kubectl apply -f kubernetes/ -n data
