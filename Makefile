IMAGE_NAME=alpa-test

CONTAINER_ENGINE ?= $(shell command -v podman 2> /dev/null || echo docker)


# regenerate new image when needed
build-image:
	$(CONTAINER_ENGINE) build --rm --tag $(IMAGE_NAME) -f Containerfile


enter-image:
	$(CONTAINER_ENGINE) run -v .:/alpa/alpa_bind:Z -ti $(IMAGE_NAME) bash


check-tests:
	$(CONTAINER_ENGINE) run -ti $(IMAGE_NAME) bash -c "poetry run pytest -vvv test/"


check-install:
	$(CONTAINER_ENGINE) run -ti $(IMAGE_NAME) \
		bash -c "pip install . && alpa --help"


check: check-install check-tests


ci-check-install: build-image check-install


ci-check-tests: build-image check-tests
