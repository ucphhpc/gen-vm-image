.PHONY: help all clean build build-all maintainer-clean install-dep uninstall-dep
.PHONY: installtest uninstalltest test test-all

OWNER:=ucphhpc
PACKAGE_NAME=gen-vm-image
PACKAGE_NAME_FORMATTED=$(subst -,_,$(PACKAGE_NAME))
ARGS=

all: init install-dep install build

init: venv

clean:
	$(MAKE) distclean
	$(MAKE) venv-clean
	rm -fr .env
	rm -fr .pytest_cache
	rm -fr tests/__pycache__

build:
	. $(VENV)/activate; gen-vm-image $(ARGS)

dist:
	$(VENV)/python setup.py sdist bdist_wheel

distclean:
	rm -fr dist build $(PACKAGE_NAME).egg-info $(PACKAGE_NAME_FORMATTED).egg-info

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

uninstalltest:
	$(VENV)/pip uninstall -y -r tests/requirements.txt

installtest:
	$(VENV)/pip install -r tests/requirements.txt

test:
	$(VENV)/pytest -s -v tests/

dockertest-clean:
	docker rmi -f $(OWNER)/gen-vm-image-tests

dockertest-build:
# Use the docker image to test the installation
	docker build -f tests/Dockerfile -t $(OWNER)/gen-vm-image-tests .

dockertest-run:
	docker run -it $(OWNER)/gen-vm-image-tests


include Makefile.venv
