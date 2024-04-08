.PHONY: help all clean build build-all maintainer-clean install-dep uninstall-dep
.PHONY: installcheck uninstallcheck test test-all

OWNER:=ucphhpc
TAG:=edge
PACKAGE_TIMEOUT:=60
IMAGE=saga-base
IMAGE_PATH=image/$(IMAGE).qcow2
IMAGE_OWNER=qemu
QEMU_SOCKET_PATH=/tmp/qemu-monitor-socket
# https://qemu-project.gitlab.io/qemu/system/qemu-cpu-models.html
QEMU_CPU_MODEL=AuthenticAMD
ARGS=

all: venv install-dep install build configure

clean:
	rm -fr .env
	rm -fr .pytest_cache
	rm -fr tests/__pycache__

build:
	. $(VENV)/activate; gen-vm-image --image-output-path $(IMAGE_PATH) --image-owner $(IMAGE_OWNER) $(ARGS)

configure:
	. $(VENV)/activate; configure-vm-image --image-input-path $(IMAGE_PATH) ---image-qemu-socket-path $(QEMU_SOCKET_PATH) $(ARGS)

maintainer-clean:
	@echo 'This command is intended for maintainers to use; it'
	@echo 'deletes files that may need special tools to rebuild.'
	$(MAKE) venv-clean
	$(MAKE) clean

install:
	$(VENV)/pip install .

uninstall:
	$(VENV)/pip uninstall -y gen-vm-image

install-dev:
	$(VENV)/pip install -r requirements-dev.txt

install-dep:
	$(VENV)/pip install -r requirements.txt

uninstall-dep:
	$(VENV)/pip uninstall -r requirements.txt

uninstallcheck:
	$(VENV)/pip uninstall -y -r tests/requirements.txt

installcheck:
	$(VENV)/pip install -r tests/requirements.txt

check:

dockercheck-clean:
	docker rmi -f ucphhpc/gen-vm-image-tests

dockercheck-build:
# Use the docker image to test the installation
	docker build -f tests/Dockerfile -t ucphhpc/gen-vm-image-tests .

dockercheck-run:
	docker run -it ucphhpc/gen-vm-image-tests


include Makefile.venv