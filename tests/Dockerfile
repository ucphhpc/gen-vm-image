FROM rockylinux:9.1

ADD . /app

WORKDIR /app

RUN dnf install -y \
    make

# Install the dependencies
RUN tests/install-dependencies.sh

## Prepare the build
# Refresh the venv inside the directory
# to ensure that the venv links to python
# reflect the inside of the container and not the host
RUN make maintainer-clean
RUN make
RUN make installcheck

# Run the tests
CMD ["make", "check"]