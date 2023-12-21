FROM python:3.11-alpine as build

# RUN mount cache for multi-arch: https://github.com/docker/buildx/issues/549#issuecomment-1788297892
ARG TARGETARCH
ARG TARGETVARIANT

# Install build dependencies
RUN apk add --no-cache build-base libffi-dev

WORKDIR /app

# Set up venv
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install poetry
RUN --mount=type=cache,id=pip-$TARGETARCH$TARGETVARIANT,sharing=locked,target=/root/.cache/pip pip3.11 install poetry

# Install dependencies
COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,id=pip-$TARGETARCH$TARGETVARIANT,sharing=locked,target=/root/.cache/pip poetry export -f requirements.txt | pip3.11 install -r /dev/stdin

# Build
COPY . .
RUN --mount=type=cache,id=pip-$TARGETARCH$TARGETVARIANT,sharing=locked,target=/root/.cache/pip poetry build && pip3.11 install dist/*.whl

# Uninstall them inside venv
RUN pip3.11 uninstall -y setuptools pip && \
    pip3.11 uninstall -y setuptools pip

FROM python:3.11-alpine as final

# Uninstall them for security purpose
RUN pip3.11 uninstall -y setuptools pip && \
    rm -rf /root/.cache/pip

# Copy venv
COPY --link --from=build /venv /venv
ENV PATH="/venv/bin:$PATH"

# Use dumb-init to handle signals
RUN apk add --no-cache dumb-init

# ffmpeg
COPY --link --from=mwader/static-ffmpeg:6.0 /ffmpeg /usr/local/bin/

# Create output directory
RUN mkdir -p /output && chown 1001:1001 /output
VOLUME [ "/output" ]

# Run as non-root user
USER 1001
WORKDIR /output

STOPSIGNAL SIGINT
ENTRYPOINT [ "dumb-init", "--", "/venv/bin/twspace_dl" ]
