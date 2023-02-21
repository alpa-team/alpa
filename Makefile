IMAGE_NAME=alpa-test

CONTAINER_ENGINE ?= $(shell command -v podman 2> /dev/null || echo docker)


build-image:
	$(CONTAINER_ENGINE) build --rm --tag $(IMAGE_NAME) -f Containerfile


enter-new-image: build-image
	$(CONTAINER_ENGINE) run -ti $(IMAGE_NAME) bash


enter-image:
	$(CONTAINER_ENGINE) run -ti $(IMAGE_NAME) bash


check-tests:
	poetry shell


check-install:
	$(CONTAINER_ENGINE) run -ti $(IMAGE_NAME) \
		bash -c "pip install .; alpa --help"


check: check-install check-tests


container-ckeck: build-image
	$(CONTAINER_ENGINE) run -ti $(IMAGE_NAME) make check
