FROM rockylinux:9.1

ADD . /app

WORKDIR /app

RUN dnf install -y \
    make

## Prepare the build
# Refresh the venv inside the directory
# to ensure that the venv links to python
# reflect the inside of the container and not the host
RUN make maintainer-clean

RUN make
# Install the check
RUN make installcheck
# Run the tests
RUN make check