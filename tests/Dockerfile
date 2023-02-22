FROM rockylinux:9.1

RUN dnf install -y \
    make 

# Install test dependencies
RUN dnf install -y \
    qemu-img \
    qemu-kvm \
    genisoimage \
    /usr/bin/virt-sysprep

RUN dnf install -y --enablerepo devel \
    cloud-utils

RUN ln -s /usr/libexec/qemu-kvm /usr/bin/qemu-kvm

ADD tests /app/tests
WORKDIR /app

ADD Makefile /app/
ADD Makefile.venv /app/
ADD src /app/src
ADD requirements.txt /app/
ADD architecture.yml /app/
ADD build-images.py /app/
ADD configure-image.py /app/

## Prepare the build
# Refresh the venv inside the directory
# to ensure that the venv links to python
# reflect the inside of the container and not the host
RUN make maintainer-clean
RUN make
RUN make installcheck

# Run the tests
CMD ["make", "check"]