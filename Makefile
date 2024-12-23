# Name of the Docker image
IMAGE_NAME=youtube-learning-assistant
# Name of the Docker container
CONTAINER_NAME=youtube-learning-assistant
# Docker network
NETWORK=host
# OVH host
REGSITRY_NAME= 'youtubelearningassistant'

.PHONY: build run stop clean

build:
	@docker build -t $(IMAGE_NAME) .

run: stop
	@docker run -d --rm -it -p 8501:8501/tcp $(IMAGE_NAME)

stop:
	@docker rm -f $(CONTAINER_NAME) || true

clean:
	@docker rmi -f $(IMAGE_NAME)

push:
	@docker tag $(IMAGE_NAME):latest $(REGSITRY_NAME).azurecr.io/$(CONTAINER_NAME):latest
	@docker push $(REGSITRY_NAME).azurecr.io/$(CONTAINER_NAME):latest
