IMAGE_NAME=alpa-test

CONTAINER_ENGINE ?= $(shell command -v podman 2> /dev/null || echo docker)


build-image:
	$(CONTAINER_ENGINE) build --rm --tag $(IMAGE_NAME) -f Containerfile


enter-image:
	$(CONTAINER_ENGINE) run -v .:/alpa/alpa_bind:Z -ti $(IMAGE_NAME) bash


check-tests:
	poetry shell && pytest -vvv test/


check-install:
	$(CONTAINER_ENGINE) run -ti $(IMAGE_NAME) \
		bash -c "pip install . && alpa --help"


check: check-install check-tests


container-check: build-image
	$(CONTAINER_ENGINE) run -ti $(IMAGE_NAME) make check
