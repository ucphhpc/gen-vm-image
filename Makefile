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

OWNER:=ucphhpc
PACKAGE_NAME=gen-vm-image
PACKAGE_NAME_FORMATTED=$(subst -,_,$(PACKAGE_NAME))
ARGS=

.PHONY: all
all: init install-dep install

.PHONY: venv
init: venv

.PHONY: clean
clean: distclean venv-clean
	rm -fr .env
	rm -fr .pytest_cache
	rm -fr tests/__pycache__

.PHONY: build
build: venv
	. $(VENV)/activate; gen-vm-image $(ARGS)

.PHONY: dist
dist: venv
	$(VENV)/python setup.py sdist bdist_wheel

.PHONY: distclean
distclean:
	rm -fr dist build $(PACKAGE_NAME).egg-info $(PACKAGE_NAME_FORMATTED).egg-info

.PHONY: maintainer-clean
maintainer-clean: clean
	@echo 'This command is intended for maintainers to use; it'
	@echo 'deletes files that may need special tools to rebuild.'

.PHONY: install
install: install-dep
	$(VENV)/pip install .

.PHONY: uninstall
uninstall: venv
	$(VENV)/pip uninstall -y gen-vm-image

.PHONY: install-dev
install-dev: venv
	$(VENV)/pip install -r requirements-dev.txt

.PHONY: uninstall-dev
uninstall-dev: venv
	$(VENV)/pip uninstall -r requirements-dev.txt

.PHONY: install-dep
install-dep: venv
	$(VENV)/pip install -r requirements.txt

.PHONY: uninstall-dep
uninstall-dep: venv
	$(VENV)/pip uninstall -r requirements.txt

.PHONY: installtest
installtest: install
	$(VENV)/pip install -r tests/requirements.txt

.PHONY: uninstalltest
uninstalltest: venv
	$(VENV)/pip uninstall -y -r tests/requirements.txt

.PHONY: test
test: installtest
	$(VENV)/pytest -s -v tests/

.PHONY: dockertest-clean
dockertest-clean:
	docker rmi -f $(OWNER)/gen-vm-image-tests

.PHONY: dockertest-build
dockertest-build:
# Use the docker image to test the installation
	docker build -f tests/Dockerfile -t $(OWNER)/gen-vm-image-tests .

.PHONY: dockertest-run
dockertest-run:
	docker run -it $(OWNER)/gen-vm-image-tests


include Makefile.venv
