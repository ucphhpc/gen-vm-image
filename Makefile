.PHONY: help all clean build build-all maintainer-clean install-dep uninstall-dep
.PHONY: installcheck uninstallcheck test test-all

OWNER:=ucphhpc
TAG:=edge
PACKAGE_TIMEOUT:=60
IMAGE=sif-compute-base

all: venv install-dep init

init:
	. $(VENV)/activate; python3 init-images.py

clean:
	rm -fr .env
	rm -fr .pytest_cache
	rm -fr tests/__pycache__

build:
	

maintainer-clean:
	@echo 'This command is intended for maintainers to use; it'
	@echo 'deletes files that may need special tools to rebuild.'
	$(MAKE) venv-clean
	$(MAKE) clean

install-dev:
	$(VENV)/pip install -r requirements-dev.txt

install-dep:
	$(VENV)/pip install -r requirements.txt

uninstall-dep:
	$(VENV)/pip uninstall -r requirements.txt

include Makefile.venv