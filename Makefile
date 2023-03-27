CONTAINER_ENGINE ?= $(shell command -v podman 2> /dev/null || echo docker)
CONTAINER_TEST_NAME ?= alpa-conf_test_image
ALPA_BIND_DIR ?= /alpa-conf/alpa-conf_bind


build-image:
	$(CONTAINER_ENGINE) build -f ./Containerfile . -t $(CONTAINER_TEST_NAME)


enter-image:
	$(CONTAINER_ENGINE) run -v .:$(ALPA_BIND_DIR):Z -v .:$(ALPA_BIND_DIR):Z --rm -it $(CONTAINER_TEST_NAME) /bin/bash


test-in-container:
	$(CONTAINER_ENGINE) run -v .:$(ALPA_BIND_DIR):Z --rm -it $(CONTAINER_TEST_NAME) /bin/bash -c \
		"cd alpa-conf_copied && \
		 poetry run pytest -vvv ../alpa-conf_bind/test/"
