# Copyright (C) 2024  The gen-vm-image Project by the Science HPC Center at UCPH
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

.PHONY: help all clean build build-all maintainer-clean install-dep uninstall-dep
.PHONY: installtest uninstalltest test test-all

OWNER:=ucphhpc
PACKAGE_NAME=gen-vm-image
PACKAGE_NAME_FORMATTED=$(subst -,_,$(PACKAGE_NAME))
ARGS=

all: init install-dep install

init: venv

clean: distclean venv-clean
	rm -fr .env
	rm -fr .pytest_cache
	rm -fr tests/__pycache__

build: venv
	. $(VENV)/activate; gen-vm-image $(ARGS)

dist: venv
	$(VENV)/python setup.py sdist bdist_wheel

distclean:
	rm -fr dist build $(PACKAGE_NAME).egg-info $(PACKAGE_NAME_FORMATTED).egg-info

maintainer-clean: clean
	@echo 'This command is intended for maintainers to use; it'
	@echo 'deletes files that may need special tools to rebuild.'

install: install-dep
	$(VENV)/pip install .

uninstall: venv
	$(VENV)/pip uninstall -y gen-vm-image

install-dev: venv
	$(VENV)/pip install -r requirements-dev.txt

install-dep: venv
	$(VENV)/pip install -r requirements.txt

uninstall-dep: venv
	$(VENV)/pip uninstall -r requirements.txt

uninstalltest: venv
	$(VENV)/pip uninstall -y -r tests/requirements.txt

installtest: install
	$(VENV)/pip install -r tests/requirements.txt

test: installtest
	$(VENV)/pytest -s -v tests/

dockertest-clean:
	docker rmi -f $(OWNER)/gen-vm-image-tests

dockertest-build:
# Use the docker image to test the installation
	docker build -f tests/Dockerfile -t $(OWNER)/gen-vm-image-tests .

dockertest-run:
	docker run -it $(OWNER)/gen-vm-image-tests


include Makefile.venv
