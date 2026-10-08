FROM node:24-bookworm-slim@sha256:d6aa754f16b3197301076f047b5def2f02ea1dbbc2ca920407d46d7ec7f87b20
RUN apt-get update && apt-get install --yes --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && npm install --global @openai/codex@0.154.0 && npm cache clean --force \
    && mkdir -p /home/node/.codex /work \
    && chown -R node:node /home/node/.codex /work
ENV CODEX_HOME=/home/node/.codex
USER node
WORKDIR /work
ENTRYPOINT ["codex"]
