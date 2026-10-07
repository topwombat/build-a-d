# syntax=docker/dockerfile:1
# Pinned container image for the SSBJ pipeline: Python 3.11, locked Python deps, OpenVSP 3.49.0
# built headless from source (NOSA 1.3). Build:  docker build -t ssbj .
# Run the Concorde case:  docker run --rm ssbj python -m ssbj run ssbj/validation/concorde/case.yaml
#
# Behind a TLS-intercepting proxy, pass its CA as a build secret (optional):
#   docker build --network host --build-arg HTTPS_PROXY=... \
#                --secret id=extra_ca,src=/path/to/proxy-ca.crt -t ssbj .
# trixie (GCC 14): OpenVSP 3.49 does not compile with bookworm GCC 12
FROM python:3.11.13-slim-trixie AS base

ENV DEBIAN_FRONTEND=noninteractive PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1 \
    PIP_CERT=/etc/ssl/certs/ca-certificates.crt REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
RUN --mount=type=secret,id=extra_ca,required=false \
    if [ -s /run/secrets/extra_ca ]; then \
        cp /run/secrets/extra_ca /usr/local/share/ca-certificates/extra_ca.crt && update-ca-certificates; \
    fi \
    && sed -i 's|http://deb.debian.org|https://deb.debian.org|g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update -q && apt-get install -y -q --no-install-recommends \
        build-essential cmake git swig ca-certificates \
        libxml2-dev libeigen3-dev libcminpack-dev libglm-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/ssbj
COPY requirements.lock .
RUN pip install -r requirements.lock

# OpenVSP (Python API only, no graphics). Bundled third-party libs; needs only a github.com clone.
COPY ssbj/docker/build_openvsp.sh /tmp/build_openvsp.sh
RUN SKIP_APT=1 SRC_ROOT=/opt/openvsp PYTHON=$(command -v python) bash /tmp/build_openvsp.sh \
    && rm -rf /opt/openvsp/build /opt/openvsp/OpenVSP/.git

COPY pyproject.toml .
COPY ssbj ssbj
COPY tests tests
RUN pip install --no-deps -e .

CMD ["python", "-m", "pytest", "-q"]
