.PHONY: help all clean build build-all maintainer-clean install-dep uninstall-dep
.PHONY: installcheck uninstallcheck test test-all

OWNER:=ucphhpc
TAG:=edge
PACKAGE_TIMEOUT:=60
ALL_IMAGES:=base-sif

all: venv install-dep init help

# Inspired by https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help:
	@echo "sif-images"
	@echo "========================="
	@echo "Replace % with a image directory name (e.g., make build/sif-image)"
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

init:
	. $(VENV)/activate; python3 init-images.py

clean:
	rm -fr .env
	rm -fr .pytest_cache
	rm -fr tests/__pycache__

build/%:


build-all: $(foreach i,$(ALL_IMAGES),build/$(i))

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