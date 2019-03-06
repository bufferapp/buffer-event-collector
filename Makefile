IMAGE_NAME:=bufferapp/events-collector:0.5.0
AWS_SECRET = -v $(HOME)/.aws:/root/.aws

.DEFAULT_GOAL := run

.PHONY: run
run: build
	docker run $(AWS_SECRET) -p 50051:50051 --rm $(IMAGE_NAME)

.PHONY: build
build:
	 docker build . -t $(IMAGE_NAME)

.PHONY: push
push: build
	 docker push $(IMAGE_NAME)

.PHONY: dev
dev: build
	docker run -it $(AWS_SECRET) --net=host --rm -v $(PWD):/usr/src/app $(IMAGE_NAME) /bin/bash

.PHONY: compile
compile:
	docker run -it --rm -v $(PWD):/usr/src/app $(IMAGE_NAME) \
	/bin/bash -c "python -m grpc_tools.protoc \
		--proto_path pb/ \
		--python_out . \
		--grpc_python_out . \
		pb/buda/*/*.proto"

.PHONY: clean
clean:
	sudo rm -rf buda/

.PHONY: deploy
deploy: build push
	kubectl apply -f kubernetes/ -n data
