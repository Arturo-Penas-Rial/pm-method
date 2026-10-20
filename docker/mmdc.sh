#!/bin/sh
# mmdc del contenedor de pm-method: agrega la configuración de Chromium de la imagen
# (/etc/pm-method/puppeteer.json) salvo que se pase otra con -p / --puppeteerConfigFile.
# --no-sandbox es necesario porque Docker, con su perfil seccomp por defecto, no permite el sandbox de Chromium;
# el aislamiento lo da el contenedor (usuario sin privilegios, sin capacidades, no-new-privileges).
REAL=/opt/node-tools/node_modules/.bin/mmdc
for a in "$@"; do
  case "$a" in
    -p|--puppeteerConfigFile|--puppeteerConfigFile=*) exec "$REAL" "$@" ;;
  esac
done
exec "$REAL" -p /etc/pm-method/puppeteer.json "$@"
