# syntax=docker/dockerfile:1

FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --prefix=/install -r requirements.txt


FROM python:3.13-slim AS runtime

# R6-01: release provenance (passed by compose / build-rc; never hardcode SHA).
ARG APP_VERSION=1.0.0
ARG GIT_COMMIT=unknown
ARG GIT_BRANCH=unknown
ARG BUILD_TIME=unknown
ARG GIT_TREE_STATE=unknown

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/install/bin:${PATH}" \
    PYTHONPATH="/install/lib/python3.13/site-packages" \
    APP_VERSION=${APP_VERSION} \
    GIT_COMMIT=${GIT_COMMIT} \
    GIT_BRANCH=${GIT_BRANCH} \
    BUILD_TIME=${BUILD_TIME} \
    GIT_TREE_STATE=${GIT_TREE_STATE}

LABEL org.opencontainers.image.title="ecmp-backend" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.revision="${GIT_COMMIT}" \
      org.opencontainers.image.created="${BUILD_TIME}" \
      ecmp.git.branch="${GIT_BRANCH}" \
      ecmp.git.tree_state="${GIT_TREE_STATE}"

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system --gid 10001 ecmp \
    && useradd --system --uid 10001 --gid ecmp --home-dir /app --shell /usr/sbin/nologin ecmp

COPY --from=builder /install /install
COPY --chown=ecmp:ecmp . .

RUN chmod +x /app/docker-entrypoint.sh \
    && chown -R ecmp:ecmp /app

USER ecmp

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=40s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/ready || exit 1

ENTRYPOINT ["/app/docker-entrypoint.sh"]
