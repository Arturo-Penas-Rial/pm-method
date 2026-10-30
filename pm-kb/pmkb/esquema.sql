-- Esquema de pm-kb (PostgreSQL 16 o posterior; pgvector 0.6 o posterior). Idempotente: `pm-kb base crear` lo aplica
-- cada vez. Todo es derivado de la carpeta del proyecto y se reconstruye con `pm-kb indexar`. docs/PM-KB.md §6.
-- Lo ejecuta el dueño de la base (rol administrador del índice); el servicio lee como `pmkb_lector`, sujeto a RLS.

CREATE EXTENSION IF NOT EXISTS unaccent WITH SCHEMA public;
CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;

CREATE SCHEMA IF NOT EXISTS pmkb;

-- Español sin tildes con raíces (spanish_stem): "aprobación" = "aprobacion" = "aprobaciones".
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_ts_config c JOIN pg_namespace n ON n.oid = c.cfgnamespace
                 WHERE n.nspname = 'pmkb' AND c.cfgname = 'es') THEN
    CREATE TEXT SEARCH CONFIGURATION pmkb.es (COPY = pg_catalog.spanish);
    ALTER TEXT SEARCH CONFIGURATION pmkb.es
      ALTER MAPPING FOR hword, hword_part, word, asciiword, asciihword, hword_asciipart WITH public.unaccent, spanish_stem;
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS pmkb.meta (clave text PRIMARY KEY, valor text NOT NULL);

CREATE TABLE IF NOT EXISTS pmkb.indice (
  proyecto     text PRIMARY KEY,
  raiz         text,
  commit_git   text,
  indexado_en  timestamptz NOT NULL DEFAULT now(),
  unidades     int, documentos int, vigentes int,
  avgdl        double precision,
  version_kb   text,
  modelo       text,
  omitidos     jsonb
);
-- Esquema 3: carpeta de gestión (con estado.json) relativa a la raíz, para armar las acciones de `pm-kb enlaces`.
ALTER TABLE pmkb.indice ADD COLUMN IF NOT EXISTS gestion text;
-- Esquema 4: nombre del proyecto en estado.json (`proyecto`), para resolver los enlaces del tablero (<origen>/p/<nombre>/…).
ALTER TABLE pmkb.indice ADD COLUMN IF NOT EXISTS nombre text;

CREATE TABLE IF NOT EXISTS pmkb.documento (
  proyecto text, doc_id text, titulo text, tipo text, clave_pm text,
  version_vigente text, version_aprobada text, fuente_vigente text, fuente_aprobada text, versiones int,
  PRIMARY KEY (proyecto, doc_id)
);
-- Esquema 4: circulación del documento (restringida si alguna de sus versiones lo es) y de cada versión (la de su archivo).
ALTER TABLE pmkb.documento ADD COLUMN IF NOT EXISTS circulacion text NOT NULL DEFAULT 'equipo' CHECK (circulacion IN ('equipo', 'restringida'));

CREATE TABLE IF NOT EXISTS pmkb.version (
  proyecto text, doc_id text, version text, orden int, fecha text, estado text, aprobado_por text, decision_id text,
  fuente text, sha256_archivo text, sha256_texto text, origen text, copia boolean,
  PRIMARY KEY (proyecto, fuente)
);
ALTER TABLE pmkb.version ADD COLUMN IF NOT EXISTS circulacion text NOT NULL DEFAULT 'equipo' CHECK (circulacion IN ('equipo', 'restringida'));

CREATE TABLE IF NOT EXISTS pmkb.unidad (
  proyecto text, id text, doc_id text, version text, tipo text, registro text, titulo text, texto text,
  fuente text, rango text, seccion text, estado_doc text,
  vigente boolean NOT NULL, aprobada boolean NOT NULL, copia boolean NOT NULL DEFAULT false, duplicado_de text,
  circulacion text NOT NULL DEFAULT 'equipo' CHECK (circulacion IN ('equipo', 'restringida')),
  confianza text NOT NULL DEFAULT 'gestion' CHECK (confianza IN ('gestion', 'externo')),
  sha text, tambien_en text[],
  tsv tsvector GENERATED ALWAYS AS (
    setweight(to_tsvector('pmkb.es'::regconfig, coalesce(titulo, '')), 'A') ||
    setweight(to_tsvector('pmkb.es'::regconfig, coalesce(texto, '')), 'B')) STORED,
  dl int,
  PRIMARY KEY (proyecto, id)
);
CREATE INDEX IF NOT EXISTS unidad_tsv ON pmkb.unidad USING gin (tsv);
CREATE INDEX IF NOT EXISTS unidad_titulo_trgm ON pmkb.unidad USING gin (titulo gin_trgm_ops);
CREATE INDEX IF NOT EXISTS unidad_doc ON pmkb.unidad (proyecto, doc_id, version);

-- Estadísticas de BM25 por proyecto (documentos que contienen cada lexema, solo unidades vigentes).
CREATE TABLE IF NOT EXISTS pmkb.lexema (proyecto text, lexema text, ndoc int, PRIMARY KEY (proyecto, lexema));

CREATE TABLE IF NOT EXISTS pmkb.arista (proyecto text, origen text, destino text, tipo text, fuente text, rango text);
CREATE INDEX IF NOT EXISTS arista_origen ON pmkb.arista (proyecto, origen);
CREATE INDEX IF NOT EXISTS arista_destino ON pmkb.arista (proyecto, destino);

-- Historia de filas y del estado (de .bitacora.jsonl, ya sin valores de interesados ni filas confidenciales).
CREATE TABLE IF NOT EXISTS pmkb.historia (
  proyecto text, id text, n int, fecha text, operacion text, script text, por text, registro text, detalle jsonb
);
CREATE INDEX IF NOT EXISTS historia_id ON pmkb.historia (proyecto, id);

-- Ubicaciones por id estable (esquema 3; docs/PM-KB.md §5.1): dónde está hoy cada fila de registro (id), cada artefacto
-- de estado.json (clave) y cada documento sin clave (doc_id, también el anterior a un movimiento). Se reemplaza en cada
-- indexación; `desde` se conserva mientras la ruta no cambie. estado: vigente | movida (artefacto encontrado fuera de la
-- ruta de estado.json, por huella o por nombre) | no-encontrada | externa (especificación de BMAD).
CREATE TABLE IF NOT EXISTS pmkb.ubicacion (
  proyecto text NOT NULL, ref text NOT NULL,
  tipo text NOT NULL CHECK (tipo IN ('fila', 'artefacto', 'documento')),
  ruta text NOT NULL DEFAULT '', rango text NOT NULL DEFAULT '', sha256 text NOT NULL DEFAULT '',
  desde timestamptz NOT NULL DEFAULT now(),
  doc_id text NOT NULL DEFAULT '', declarada text NOT NULL DEFAULT '',
  estado text NOT NULL DEFAULT 'vigente' CHECK (estado IN ('vigente', 'movida', 'no-encontrada', 'externa')),
  encontrada_por text NOT NULL DEFAULT '',
  circulacion text NOT NULL DEFAULT 'equipo' CHECK (circulacion IN ('equipo', 'restringida')),
  detalle jsonb,
  PRIMARY KEY (proyecto, ref)
);
CREATE INDEX IF NOT EXISTS ubicacion_doc ON pmkb.ubicacion (proyecto, doc_id);

-- Movimientos detectados al indexar (comparando con la indexación anterior): se acumulan, no se reemplazan.
-- motivo: id (fila en otro archivo) | clave (estado.json declara otra ruta) | huella (mismo sha256 en otra ruta) | nombre.
CREATE TABLE IF NOT EXISTS pmkb.movimiento (
  proyecto text NOT NULL, ref text NOT NULL, tipo text NOT NULL,
  ruta_anterior text NOT NULL, ruta_nueva text NOT NULL, sha256 text NOT NULL DEFAULT '',
  detectado timestamptz NOT NULL DEFAULT now(), motivo text NOT NULL,
  circulacion text NOT NULL DEFAULT 'equipo' CHECK (circulacion IN ('equipo', 'restringida'))
);
CREATE INDEX IF NOT EXISTS movimiento_ref ON pmkb.movimiento (proyecto, ref, detectado);

-- Tablero del proyecto (esquema 4; docs/PM-KB.md §11.1): el pm-tablero/1 que genera el núcleo de pm-method
-- (`tablero.py generar --json`), publicado al indexar, en `vigilar`, con `pm-kb tablero` o con «actualizar ahora». Se
-- reemplaza en cada publicación; `version` sube cuando cambia el contenido. Una fila por circulación: `equipo` (sin las
-- tarjetas cuya fuente es restringida) y, solo si difiere, `restringida` (completa). `detalle`: datos de la ficha de cada
-- puerta (decisión, condiciones, verificación) leídos de estado.json.
CREATE TABLE IF NOT EXISTS pmkb.tablero (
  proyecto text NOT NULL,
  circulacion text NOT NULL DEFAULT 'equipo' CHECK (circulacion IN ('equipo', 'restringida')),
  formato text NOT NULL, huella text NOT NULL, sha256 text NOT NULL, corte text NOT NULL DEFAULT '', n_bitacora int,
  version int NOT NULL DEFAULT 1,
  generado_en timestamptz NOT NULL DEFAULT now(),
  origen text NOT NULL DEFAULT '' CHECK (origen IN ('', 'indexar', 'vigilar', 'tablero', 'web')),
  por text NOT NULL DEFAULT '',
  detalle jsonb,
  datos jsonb NOT NULL,
  PRIMARY KEY (proyecto, circulacion)
);

-- Instantáneas congeladas (03-control/reportes/tableros/<id>.json, inmutables, escritas por pm-method): el historial del
-- tablero. Se reemplazan en cada publicación (la carpeta es la fuente); mismas dos filas por circulación que el tablero.
CREATE TABLE IF NOT EXISTS pmkb.instantanea (
  proyecto text NOT NULL, id text NOT NULL,
  circulacion text NOT NULL DEFAULT 'equipo' CHECK (circulacion IN ('equipo', 'restringida')),
  orden int NOT NULL, fecha text NOT NULL DEFAULT '', tipo text NOT NULL DEFAULT '', etiqueta text NOT NULL DEFAULT '',
  puerta text NOT NULL DEFAULT '', etapa int, decision text NOT NULL DEFAULT '', decision_id text NOT NULL DEFAULT '',
  por text NOT NULL DEFAULT '', corte text NOT NULL DEFAULT '',
  archivo text NOT NULL, html text NOT NULL DEFAULT '', sha256 text NOT NULL, en_bitacora boolean,
  datos jsonb NOT NULL,
  PRIMARY KEY (proyecto, id, circulacion)
);
CREATE INDEX IF NOT EXISTS instantanea_orden ON pmkb.instantanea (proyecto, orden);

-- Vectores (opcionales): sin dimensión fija para admitir cualquier modelo; búsqueda exacta por coseno.
CREATE TABLE IF NOT EXISTS pmkb.vector (proyecto text, unidad_id text, modelo text, emb vector, PRIMARY KEY (proyecto, unidad_id, modelo));
CREATE TABLE IF NOT EXISTS pmkb.cache_vector (sha text, modelo text, emb vector, PRIMARY KEY (sha, modelo));

-- Acceso: un token por persona (solo se guarda su sha256), proyectos permitidos ('*' = todos), circulación y vencimiento.
CREATE TABLE IF NOT EXISTS pmkb.acceso (
  token_sha  text PRIMARY KEY,
  persona    text NOT NULL,
  proyectos  text NOT NULL,
  restringida boolean NOT NULL DEFAULT false,
  creado     timestamptz NOT NULL DEFAULT now(),
  revocado   timestamptz
);
-- Vencimiento: `pm-kb token crear` lo fija siempre (--dias, 90 por defecto); NULL solo en tokens emitidos sin él.
ALTER TABLE pmkb.acceso ADD COLUMN IF NOT EXISTS vence timestamptz;

-- Enlaces compartidos (esquema 4; docs/PM-KB.md §11.7), separados de los tokens personales: un proyecto y un tablero
-- (`actual` en vivo o el id de una instantánea), filtrado por actor si se pidió (`actor`: ST-### o nombre, tal como lo
-- resolvió el núcleo; `actor_nombre` para mostrar), con circulación restringida solo si se pidió. `id` es público (para
-- listar y revocar); del token solo se guarda el sha256. Vencimiento obligatorio, 90 días como máximo (la línea de
-- comandos pone 7 por defecto). `usos` y `ultimo_uso`: canjes del enlace (cada apertura que crea una sesión).
CREATE TABLE IF NOT EXISTS pmkb.enlace (
  id           text PRIMARY KEY CHECK (id ~ '^e-[0-9a-f]{8}$'),
  token_sha    text NOT NULL UNIQUE,
  proyecto     text NOT NULL,
  alcance      text NOT NULL DEFAULT 'actual'
               CHECK (alcance = 'actual' OR alcance ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9][a-z0-9-]{0,80}$'),
  actor        text NOT NULL DEFAULT '',
  actor_nombre text NOT NULL DEFAULT '',
  restringida  boolean NOT NULL DEFAULT false,
  para         text NOT NULL DEFAULT '',
  creado       timestamptz NOT NULL DEFAULT now(),
  creado_por   text NOT NULL DEFAULT '',
  vence        timestamptz NOT NULL,
  revocado     timestamptz,
  usos         int NOT NULL DEFAULT 0,
  ultimo_uso   timestamptz,
  CONSTRAINT enlace_vence_maximo CHECK (vence <= creado + interval '90 days')
);
CREATE INDEX IF NOT EXISTS enlace_proyecto ON pmkb.enlace (proyecto);

-- Sesiones web (personales y de enlaces compartidos): la cookie lleva un id de sesión aleatorio, nunca el token; aquí
-- solo su sha256. Una sesión personal depende de su token (`acceso`) y una compartida de su enlace: revocar o vencer el
-- token o el enlace la corta en la petición siguiente. `vence` nunca supera el del token o el del enlace.
CREATE TABLE IF NOT EXISTS pmkb.sesion (
  sid_sha   text PRIMARY KEY,
  token_sha text REFERENCES pmkb.acceso (token_sha) ON DELETE CASCADE,
  enlace    text REFERENCES pmkb.enlace (id) ON DELETE CASCADE,
  creada    timestamptz NOT NULL DEFAULT now(),
  vence     timestamptz NOT NULL,
  CONSTRAINT sesion_de_uno CHECK ((token_sha IS NULL) <> (enlace IS NULL))
);
CREATE INDEX IF NOT EXISTS sesion_enlace ON pmkb.sesion (enlace);
CREATE INDEX IF NOT EXISTS sesion_token ON pmkb.sesion (token_sha);

-- Visibilidad por fila: proyectos y circulación que el servicio fija por transacción según el token.
CREATE OR REPLACE FUNCTION pmkb.visible(p text, circ text DEFAULT 'equipo') RETURNS boolean
LANGUAGE sql STABLE AS $$
  SELECT (coalesce(current_setting('pmkb.proyectos', true), '') = '*'
          OR p = ANY (string_to_array(coalesce(current_setting('pmkb.proyectos', true), ''), ',')))
     AND (circ = 'equipo' OR coalesce(current_setting('pmkb.restringida', true), 'no') = 'si')
$$;

-- Identidad de un token sin dar lectura a la tabla de accesos (descarta revocados y vencidos).
DROP FUNCTION IF EXISTS pmkb.identidad(text);
CREATE FUNCTION pmkb.identidad(sha text) RETURNS TABLE (persona text, proyectos text, restringida boolean, vence timestamptz)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = pmkb, pg_temp AS $$
  SELECT a.persona, a.proyectos, a.restringida, a.vence FROM pmkb.acceso a
   WHERE a.token_sha = sha AND a.revocado IS NULL AND (a.vence IS NULL OR a.vence > now())
$$;
REVOKE ALL ON FUNCTION pmkb.identidad(text) FROM PUBLIC;

-- Sesiones web sin dar lectura a las tablas de tokens, enlaces ni sesiones (el lector solo ejecuta estas funciones).
-- abrir_sesion: un token personal vigente abre una sesión de hasta `horas` (1–12), sin pasar del vencimiento del token.
DROP FUNCTION IF EXISTS pmkb.abrir_sesion(text, text, int);
CREATE FUNCTION pmkb.abrir_sesion(p_token_sha text, p_sid_sha text, p_horas int) RETURNS timestamptz
LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path = pmkb, pg_temp AS $$
DECLARE v timestamptz;
BEGIN
  DELETE FROM pmkb.sesion s WHERE s.vence < now();
  SELECT least(a.vence, now() + make_interval(hours => least(greatest(p_horas, 1), 12))) INTO v
    FROM pmkb.acceso a WHERE a.token_sha = p_token_sha AND a.revocado IS NULL AND (a.vence IS NULL OR a.vence > now());
  IF NOT FOUND THEN
    RETURN NULL;
  END IF;
  INSERT INTO pmkb.sesion (sid_sha, token_sha, vence) VALUES (p_sid_sha, p_token_sha, v);
  RETURN v;
END $$;

-- canjear: el token de un enlace vigente abre una sesión de hasta `horas` (1–12), sin pasar del vencimiento del enlace,
-- y registra el uso. Sin filas: inválido, vencido o revocado.
DROP FUNCTION IF EXISTS pmkb.canjear(text, text, int);
CREATE FUNCTION pmkb.canjear(p_token_sha text, p_sid_sha text, p_horas int)
RETURNS TABLE (id text, proyecto text, alcance text, actor text, actor_nombre text, restringida boolean, vence timestamptz, enlace_vence timestamptz)
LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path = pmkb, pg_temp AS $$
DECLARE e pmkb.enlace%ROWTYPE; v timestamptz;
BEGIN
  DELETE FROM pmkb.sesion s WHERE s.vence < now();
  SELECT * INTO e FROM pmkb.enlace x WHERE x.token_sha = p_token_sha AND x.revocado IS NULL AND x.vence > now() FOR UPDATE;
  IF NOT FOUND THEN
    RETURN;
  END IF;
  UPDATE pmkb.enlace x SET usos = x.usos + 1, ultimo_uso = now() WHERE x.id = e.id;
  v := least(e.vence, now() + make_interval(hours => least(greatest(p_horas, 1), 12)));
  INSERT INTO pmkb.sesion (sid_sha, enlace, vence) VALUES (p_sid_sha, e.id, v);
  RETURN QUERY SELECT e.id, e.proyecto, e.alcance, e.actor, e.actor_nombre, e.restringida, v, e.vence;
END $$;

-- sesion_identidad: quién es la sesión de una cookie (descarta sesiones vencidas y las de tokens o enlaces revocados o
-- vencidos). `clave`: identificador no secreto para límites de uso (sha256 del sha del token, o el id del enlace).
DROP FUNCTION IF EXISTS pmkb.sesion_identidad(text);
CREATE FUNCTION pmkb.sesion_identidad(p_sid_sha text)
RETURNS TABLE (tipo text, persona text, proyectos text, restringida boolean, vence timestamptz, clave text,
               enlace text, alcance text, actor text, actor_nombre text, enlace_vence timestamptz)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = pmkb, pg_temp AS $$
  SELECT 'persona', a.persona, a.proyectos, a.restringida, least(s.vence, a.vence), encode(sha256(convert_to(a.token_sha, 'UTF8')), 'hex'),
         NULL::text, NULL::text, NULL::text, NULL::text, NULL::timestamptz
    FROM pmkb.sesion s JOIN pmkb.acceso a ON a.token_sha = s.token_sha
   WHERE s.sid_sha = p_sid_sha AND s.vence > now() AND a.revocado IS NULL AND (a.vence IS NULL OR a.vence > now())
  UNION ALL
  SELECT 'enlace', 'enlace ' || e.id, e.proyecto, e.restringida, least(s.vence, e.vence), e.id,
         e.id, e.alcance, e.actor, e.actor_nombre, e.vence
    FROM pmkb.sesion s JOIN pmkb.enlace e ON e.id = s.enlace
   WHERE s.sid_sha = p_sid_sha AND s.vence > now() AND e.revocado IS NULL AND e.vence > now()
$$;

-- cerrar_sesion: `/salir` borra la sesión de la cookie.
DROP FUNCTION IF EXISTS pmkb.cerrar_sesion(text);
CREATE FUNCTION pmkb.cerrar_sesion(p_sid_sha text) RETURNS void
LANGUAGE sql VOLATILE SECURITY DEFINER SET search_path = pmkb, pg_temp AS $$
  DELETE FROM pmkb.sesion s WHERE s.sid_sha = p_sid_sha
$$;
REVOKE ALL ON FUNCTION pmkb.abrir_sesion(text, text, int), pmkb.canjear(text, text, int), pmkb.sesion_identidad(text),
                       pmkb.cerrar_sesion(text) FROM PUBLIC;

ALTER TABLE pmkb.indice ENABLE ROW LEVEL SECURITY;
ALTER TABLE pmkb.documento ENABLE ROW LEVEL SECURITY;
ALTER TABLE pmkb.version ENABLE ROW LEVEL SECURITY;
ALTER TABLE pmkb.unidad ENABLE ROW LEVEL SECURITY;
ALTER TABLE pmkb.lexema ENABLE ROW LEVEL SECURITY;
ALTER TABLE pmkb.arista ENABLE ROW LEVEL SECURITY;
ALTER TABLE pmkb.historia ENABLE ROW LEVEL SECURITY;
ALTER TABLE pmkb.vector ENABLE ROW LEVEL SECURITY;
ALTER TABLE pmkb.ubicacion ENABLE ROW LEVEL SECURITY;
ALTER TABLE pmkb.movimiento ENABLE ROW LEVEL SECURITY;
ALTER TABLE pmkb.tablero ENABLE ROW LEVEL SECURITY;
ALTER TABLE pmkb.instantanea ENABLE ROW LEVEL SECURITY;
ALTER TABLE pmkb.acceso ENABLE ROW LEVEL SECURITY;
ALTER TABLE pmkb.enlace ENABLE ROW LEVEL SECURITY;
ALTER TABLE pmkb.sesion ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS leer ON pmkb.indice;     CREATE POLICY leer ON pmkb.indice     FOR SELECT USING (pmkb.visible(proyecto));
DROP POLICY IF EXISTS leer ON pmkb.documento;  CREATE POLICY leer ON pmkb.documento  FOR SELECT USING (pmkb.visible(proyecto, circulacion));
DROP POLICY IF EXISTS leer ON pmkb.version;    CREATE POLICY leer ON pmkb.version    FOR SELECT USING (pmkb.visible(proyecto, circulacion));
DROP POLICY IF EXISTS leer ON pmkb.unidad;     CREATE POLICY leer ON pmkb.unidad     FOR SELECT USING (pmkb.visible(proyecto, circulacion));
DROP POLICY IF EXISTS leer ON pmkb.lexema;     CREATE POLICY leer ON pmkb.lexema     FOR SELECT USING (pmkb.visible(proyecto));
DROP POLICY IF EXISTS leer ON pmkb.arista;     CREATE POLICY leer ON pmkb.arista     FOR SELECT USING (pmkb.visible(proyecto));
DROP POLICY IF EXISTS leer ON pmkb.historia;   CREATE POLICY leer ON pmkb.historia   FOR SELECT USING (pmkb.visible(proyecto));
DROP POLICY IF EXISTS leer ON pmkb.vector;     CREATE POLICY leer ON pmkb.vector     FOR SELECT USING (pmkb.visible(proyecto));
DROP POLICY IF EXISTS leer ON pmkb.ubicacion;  CREATE POLICY leer ON pmkb.ubicacion  FOR SELECT USING (pmkb.visible(proyecto, circulacion));
DROP POLICY IF EXISTS leer ON pmkb.movimiento; CREATE POLICY leer ON pmkb.movimiento FOR SELECT USING (pmkb.visible(proyecto, circulacion));
DROP POLICY IF EXISTS leer ON pmkb.tablero;    CREATE POLICY leer ON pmkb.tablero    FOR SELECT USING (pmkb.visible(proyecto, circulacion));
DROP POLICY IF EXISTS leer ON pmkb.instantanea; CREATE POLICY leer ON pmkb.instantanea FOR SELECT USING (pmkb.visible(proyecto, circulacion));
-- pmkb.acceso, pmkb.enlace y pmkb.sesion: sin política para el lector (solo el dueño las ve; el lector usa pmkb.identidad,
-- pmkb.abrir_sesion, pmkb.canjear, pmkb.sesion_identidad y pmkb.cerrar_sesion).

-- Rol de lectura del servicio (lo crea `pm-kb base crear` o la imagen pm-kb-db): solo SELECT, sujeto a RLS.
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'pmkb_lector') THEN
    GRANT USAGE ON SCHEMA pmkb TO pmkb_lector;
    GRANT SELECT ON pmkb.meta, pmkb.indice, pmkb.documento, pmkb.version, pmkb.unidad, pmkb.lexema, pmkb.arista,
                    pmkb.historia, pmkb.vector, pmkb.ubicacion, pmkb.movimiento, pmkb.tablero, pmkb.instantanea TO pmkb_lector;
    REVOKE ALL ON pmkb.acceso, pmkb.enlace, pmkb.sesion, pmkb.cache_vector FROM pmkb_lector;
    GRANT EXECUTE ON FUNCTION pmkb.visible(text, text), pmkb.identidad(text), pmkb.abrir_sesion(text, text, int),
                              pmkb.canjear(text, text, int), pmkb.sesion_identidad(text), pmkb.cerrar_sesion(text) TO pmkb_lector;
  END IF;
END $$;

-- Versión del esquema (indexador.ESQUEMA). 2 → 3: tablas ubicacion y movimiento, y la columna indice.gestion. 3 → 4:
-- tablas tablero e instantanea, columnas indice.nombre y circulacion de documento y version (con sus políticas), enlaces
-- compartidos (enlace) y sesiones web (sesion) con sus funciones. Se migra
-- aplicando este archivo (`pm-kb base crear`), sin tocar el índice ni los tokens.
INSERT INTO pmkb.meta (clave, valor) VALUES ('esquema', '4')
  ON CONFLICT (clave) DO UPDATE SET valor = EXCLUDED.valor;
