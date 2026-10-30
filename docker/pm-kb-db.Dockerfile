# PostgreSQL segregado de pm-kb (perfil "kb" de docker/compose.yaml): solo la base del índice, en su propio contenedor,
# volumen y red interna sin salida ni puertos publicados. PostgreSQL y pgvector de los repositorios oficiales de Ubuntu.
# Guía: docs/INSTALACION-DOCKER.md §8 y docs/PM-KB.md §7. Construir desde la raíz del repositorio:
#   docker build -f docker/pm-kb-db.Dockerfile -t pm-kb-db:2.7.0 .
# Contraseñas: solo como secretos de Docker (/run/secrets/pmkb_admin_clave y pmkb_lector_clave); nunca en la imagen.

# Misma base que docker/Dockerfile (Ubuntu 26.04 LTS fijada por digest; ver docs/DOCKER.md §6 para actualizarla).
ARG BASE_IMAGE=ubuntu:26.04@sha256:c098726dd9b9733f3e885f8de0ef375206a311b0a317eadc40d347b1115fb944
FROM ${BASE_IMAGE}
ENV DEBIAN_FRONTEND=noninteractive LANG=C.UTF-8 LC_ALL=C.UTF-8
RUN --mount=type=secret,id=ca_proxy,mode=0444 \
    set -eu; \
    CA=""; if [ -s /run/secrets/ca_proxy ]; then CA="-o Acquire::https::CAInfo=/run/secrets/ca_proxy"; fi; \
    apt-get $CA update; \
    apt-get $CA install -y --no-install-recommends postgresql-common tini; \
    sed -i -E 's/^#?[[:space:]]*create_main_cluster[[:space:]]*=.*/create_main_cluster = false/' /etc/postgresql-common/createcluster.conf; \
    V="$(apt-cache policy postgresql | awk '/Candidate:/ {print $2}' | cut -d+ -f1)"; \
    apt-get $CA install -y --no-install-recommends "postgresql-$V" "postgresql-$V-pgvector"; \
    test -f "/usr/share/postgresql/$V/extension/vector.control"; \
    mkdir -p /var/lib/postgresql/data && chown postgres:postgres /var/lib/postgresql/data && chmod 700 /var/lib/postgresql/data; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*.deb /var/log/apt /var/log/dpkg.log
COPY --chmod=0755 pm-kb/db/pg.sh /usr/local/bin/pm-kb-pg
USER postgres
ENV PGDATA=/var/lib/postgresql/data
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=6 \
    CMD /usr/lib/postgresql/*/bin/pg_isready -h /tmp -d pmkb -q || exit 1
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/pm-kb-pg", "docker"]
