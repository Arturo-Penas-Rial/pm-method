# Entorno Docker opcional de pm-method: Linux aislado con Claude Code CLI, Python 3 y Node.js, más todas las
# dependencias opcionales que usan los scripts, las pruebas y los generadores de diagramas y diapositivas.
# Guía: docs/DOCKER.md.  Construir desde la raíz del repositorio:
#   docker build -f docker/Dockerfile -t pm-method:2.3.0 .
#
# Nada de credenciales en la imagen: la clave de API o el inicio de sesión se pasan al ejecutar
# (variables de entorno o volumen de configuración). Los secretos de construcción opcionales (un certificado de
# proxy corporativo) se montan con --secret y no quedan en ninguna capa.

# Imagen base oficial de Ubuntu 26.04 LTS, fijada por versión y por digest (índice multiplataforma).
# Digest tomado de docker-library/repo-info (repos/ubuntu/remote/26.04.md) el 2026-10-20.
ARG BASE_IMAGE=ubuntu:26.04@sha256:c098726dd9b9733f3e885f8de0ef375206a311b0a317eadc40d347b1115fb944

# ---------------------------------------------------------------------------------------------------------------
# base: paquetes del sistema que necesita la imagen final (también la usan las etapas de construcción)
# ---------------------------------------------------------------------------------------------------------------
FROM ${BASE_IMAGE} AS base
ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8
# Bibliotecas de Chromium headless shell (diagramas Mermaid y capturas), fuentes con tildes y emojis, tini como init.
RUN --mount=type=secret,id=ca_proxy,mode=0444 \
    set -eu; \
    CA=""; if [ -s /run/secrets/ca_proxy ]; then CA="-o Acquire::https::CAInfo=/run/secrets/ca_proxy"; fi; \
    apt-get $CA update; \
    apt-get $CA install -y --no-install-recommends \
        ca-certificates git less tini \
        python3 nodejs \
        libasound2t64 libatk-bridge2.0-0t64 libatk1.0-0t64 libatspi2.0-0t64 libcairo2 libcups2t64 libdbus-1-3 \
        libdrm2 libgbm1 libglib2.0-0t64 libnspr4 libnss3 libpango-1.0-0 libx11-6 libxcb1 libxcomposite1 \
        libxdamage1 libxext6 libxfixes3 libxkbcommon0 libxrandr2 \
        fonts-dejavu-core fonts-liberation fonts-noto-color-emoji; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*.deb /var/log/apt /var/log/dpkg.log

# ---------------------------------------------------------------------------------------------------------------
# herramientas-python: entorno virtual con dependencias fijadas por hash (docker/requirements.txt)
# ---------------------------------------------------------------------------------------------------------------
FROM base AS herramientas-python
RUN --mount=type=secret,id=ca_proxy,mode=0444 \
    set -eu; \
    CA=""; if [ -s /run/secrets/ca_proxy ]; then CA="-o Acquire::https::CAInfo=/run/secrets/ca_proxy"; fi; \
    apt-get $CA update; \
    apt-get $CA install -y --no-install-recommends python3-venv; \
    rm -rf /var/lib/apt/lists/*
COPY docker/requirements.txt /tmp/requirements.txt
RUN --mount=type=secret,id=ca_proxy,mode=0444 \
    set -eu; \
    if [ -s /run/secrets/ca_proxy ]; then export PIP_CERT=/run/secrets/ca_proxy; fi; \
    python3 -m venv /opt/venv; \
    /opt/venv/bin/pip install --no-cache-dir --disable-pip-version-check --require-hashes --only-binary=:all: \
        -r /tmp/requirements.txt; \
    /opt/venv/bin/pip uninstall -y pip; \
    find /opt/venv -name '__pycache__' -type d -prune -exec rm -rf {} +

# ---------------------------------------------------------------------------------------------------------------
# herramientas-node: Claude Code CLI, mermaid-cli, pptxgenjs y npm, instalados con npm ci (docker/node/)
# ---------------------------------------------------------------------------------------------------------------
FROM base AS herramientas-node
RUN --mount=type=secret,id=ca_proxy,mode=0444 \
    set -eu; \
    CA=""; if [ -s /run/secrets/ca_proxy ]; then CA="-o Acquire::https::CAInfo=/run/secrets/ca_proxy"; fi; \
    apt-get $CA update; \
    apt-get $CA install -y --no-install-recommends npm; \
    rm -rf /var/lib/apt/lists/*
WORKDIR /opt/node-tools
COPY docker/node/package.json docker/node/package-lock.json ./
# PUPPETEER_SKIP_DOWNLOAD: mermaid-cli usa el Chromium headless shell de Playwright (etapa navegadores).
RUN --mount=type=secret,id=ca_proxy,mode=0444 \
    set -eu; \
    if [ -s /run/secrets/ca_proxy ]; then export NODE_EXTRA_CA_CERTS=/run/secrets/ca_proxy; fi; \
    PUPPETEER_SKIP_DOWNLOAD=1 npm ci --omit=dev --no-audit --no-fund --cache /tmp/npm-cache; \
    rm -rf /tmp/npm-cache /root/.npm; \
    # El npm de Ubuntu no filtra las dependencias opcionales por libc: se quita el binario musl (glibc en Ubuntu).
    rm -rf node_modules/@anthropic-ai/claude-code-linux-*-musl; \
    ./node_modules/.bin/claude --version

# ---------------------------------------------------------------------------------------------------------------
# navegadores: Chromium headless shell de Playwright. Para usar una copia ya descargada de la MISMA revisión
# (redes sin acceso a la CDN de Playwright), reemplazar esta etapa con:
#   docker build --build-context navegadores=<carpeta con chromium_headless_shell-NNNN/> ...
# ---------------------------------------------------------------------------------------------------------------
FROM herramientas-python AS descarga-navegadores
RUN --mount=type=secret,id=ca_proxy,mode=0444 \
    set -eu; \
    if [ -s /run/secrets/ca_proxy ]; then export NODE_EXTRA_CA_CERTS=/run/secrets/ca_proxy; fi; \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright /opt/venv/bin/playwright install --only-shell chromium

FROM scratch AS navegadores
COPY --from=descarga-navegadores /ms-playwright/ /

# ---------------------------------------------------------------------------------------------------------------
# paquete: el plugin y los navegadores con permisos normalizados (legibles por todos, escribibles solo por root).
# Se hace en una etapa aparte para no duplicar capas en la imagen final.
# ---------------------------------------------------------------------------------------------------------------
FROM base AS paquete
COPY --from=navegadores / /opt/ms-playwright/
COPY . /opt/pm-method
COPY docker/puppeteer.json /etc/pm-method/puppeteer.json
RUN chmod -R a+rX,go-w /opt/pm-method /opt/ms-playwright /etc/pm-method

# ---------------------------------------------------------------------------------------------------------------
# final
# ---------------------------------------------------------------------------------------------------------------
FROM base AS final
ARG UID=1000
ARG GID=1000
ARG VERSION=2.3.0
LABEL org.opencontainers.image.title="pm-method" \
      org.opencontainers.image.description="Entorno aislado para usar y probar el plugin pm-method con Claude Code (Linux, Python 3, Node.js, Mermaid, Playwright)" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/Arturo-Penas-Rial/pm-method" \
      org.opencontainers.image.documentation="https://github.com/Arturo-Penas-Rial/pm-method/blob/main/docs/DOCKER.md" \
      org.opencontainers.image.base.name="ubuntu:26.04"

# Usuario sin privilegios (la imagen oficial trae "ubuntu" con UID 1000: se reemplaza por "pm").
RUN set -eu; \
    if id -u ubuntu >/dev/null 2>&1; then userdel --remove ubuntu; fi; \
    if getent group ubuntu >/dev/null; then groupdel ubuntu; fi; \
    groupadd --gid "${GID}" pm; \
    useradd --uid "${UID}" --gid "${GID}" --create-home --shell /bin/bash pm; \
    install -d -o pm -g pm -m 0700 /home/pm/.claude; \
    install -d -o pm -g pm -m 0755 /trabajo; \
    git config --system --add safe.directory /trabajo

COPY --from=herramientas-python /opt/venv /opt/venv
COPY --from=herramientas-node /opt/node-tools /opt/node-tools
COPY --from=paquete /opt/ms-playwright /opt/ms-playwright
COPY --from=paquete /etc/pm-method /etc/pm-method
COPY --chmod=0755 docker/mmdc.sh /usr/local/bin/mmdc
COPY --chmod=0755 docker/pm-pruebas.sh /usr/local/bin/pm-pruebas
COPY --from=paquete /opt/pm-method /opt/pm-method

# Enlace estable al Chromium headless shell y comprobación de que es un ejecutable ELF sin bibliotecas faltantes.
# (Sin chmod -R aquí: cambiar permisos en otra capa duplicaría cientos de MB.)
RUN set -eu; \
    shell="$(find /opt/ms-playwright -maxdepth 3 -type f \( -name headless_shell -o -name chrome-headless-shell \) | head -n 1)"; \
    test -n "$shell" || { echo "ERROR: no se encontró el Chromium headless shell de Playwright" >&2; exit 1; }; \
    ldd "$shell" > /tmp/ldd.txt 2>&1 || { echo "ERROR: $shell no es un ejecutable dinámico válido" >&2; exit 1; }; \
    if grep 'not found' /tmp/ldd.txt >&2; then exit 1; fi; \
    rm -f /tmp/ldd.txt; \
    ln -s "$shell" /usr/local/bin/chromium-headless-shell

ENV PATH=/usr/local/sbin:/usr/local/bin:/opt/venv/bin:/opt/node-tools/node_modules/.bin:/usr/sbin:/usr/bin:/sbin:/bin \
    HOME=/home/pm \
    PM_METHOD_DIR=/opt/pm-method \
    NODE_PATH=/opt/node-tools/node_modules \
    PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright \
    PUPPETEER_SKIP_DOWNLOAD=1 \
    CLAUDE_CONFIG_DIR=/home/pm/.claude \
    DISABLE_AUTOUPDATER=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPYCACHEPREFIX=/tmp/pycache \
    MPLCONFIGDIR=/tmp/matplotlib

USER pm
WORKDIR /trabajo
HEALTHCHECK --interval=5m --timeout=30s --start-period=10s --retries=3 \
    CMD claude --version >/dev/null && python3 -c "import yaml, docx, openpyxl" || exit 1
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["bash"]
