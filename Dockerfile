FROM python:alpine as base

WORKDIR /output
VOLUME /output

FROM base as builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN apk add --no-cache gcc libffi-dev musl-dev
RUN pip install poetry
RUN python -m venv /venv

COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt | /venv/bin/pip install -r /dev/stdin

COPY . .
RUN poetry build && /venv/bin/pip install dist/*.whl

FROM base as final

RUN apk add --no-cache dumb-init ffmpeg
COPY --from=builder /venv /venv

ENTRYPOINT [ "/usr/bin/dumb-init", "--", "/venv/bin/twspace_dl"]
