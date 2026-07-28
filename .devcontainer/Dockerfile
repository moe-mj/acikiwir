FROM mcr.microsoft.com/devcontainers/javascript-node:22

USER root

RUN apt update && apt install -y python3 python3-pip curl git

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

USER node