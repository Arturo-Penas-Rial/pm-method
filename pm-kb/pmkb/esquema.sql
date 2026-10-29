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

CREATE TABLE IF NOT EXISTS pmkb.documento (
  proyecto text, doc_id text, titulo text, tipo text, clave_pm text,
  version_vigente text, version_aprobada text, fuente_vigente text, fuente_aprobada text, versiones int,
  PRIMARY KEY (proyecto, doc_id)
);

CREATE TABLE IF NOT EXISTS pmkb.version (
  proyecto text, doc_id text, version text, orden int, fecha text, estado text, aprobado_por text, decision_id text,
  fuente text, sha256_archivo text, sha256_texto text, origen text, copia boolean,
  PRIMARY KEY (proyecto, fuente)
);

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

-- Vectores (opcionales): sin dimensión fija para admitir cualquier modelo; búsqueda exacta por coseno.
CREATE TABLE IF NOT EXISTS pmkb.vector (proyecto text, unidad_id text, modelo text, emb vector, PRIMARY KEY (proyecto, unidad_id, modelo));
CREATE TABLE IF NOT EXISTS pmkb.cache_vector (sha text, modelo text, emb vector, PRIMARY KEY (sha, modelo));

-- Acceso: un token por persona (solo se guarda su sha256), proyectos permitidos ('*' = todos) y circulación.
CREATE TABLE IF NOT EXISTS pmkb.acceso (
  token_sha  text PRIMARY KEY,
  persona    text NOT NULL,
  proyectos  text NOT NULL,
  restringida boolean NOT NULL DEFAULT false,
  creado     timestamptz NOT NULL DEFAULT now(),
  revocado   timestamptz
);

-- Visibilidad por fila: proyectos y circulación que el servicio fija por transacción según el token.
CREATE OR REPLACE FUNCTION pmkb.visible(p text, circ text DEFAULT 'equipo') RETURNS boolean
LANGUAGE sql STABLE AS $$
  SELECT (coalesce(current_setting('pmkb.proyectos', true), '') = '*'
          OR p = ANY (string_to_array(coalesce(current_setting('pmkb.proyectos', true), ''), ',')))
     AND (circ = 'equipo' OR coalesce(current_setting('pmkb.restringida', true), 'no') = 'si')
$$;

-- Identidad de un token sin dar lectura a la tabla de accesos.
CREATE OR REPLACE FUNCTION pmkb.identidad(sha text) RETURNS TABLE (persona text, proyectos text, restringida boolean)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = pmkb, pg_temp AS $$
  SELECT a.persona, a.proyectos, a.restringida FROM pmkb.acceso a WHERE a.token_sha = sha AND a.revocado IS NULL
$$;
REVOKE ALL ON FUNCTION pmkb.identidad(text) FROM PUBLIC;

ALTER TABLE pmkb.indice ENABLE ROW LEVEL SECURITY;
ALTER TABLE pmkb.documento ENABLE ROW LEVEL SECURITY;
ALTER TABLE pmkb.version ENABLE ROW LEVEL SECURITY;
ALTER TABLE pmkb.unidad ENABLE ROW LEVEL SECURITY;
ALTER TABLE pmkb.lexema ENABLE ROW LEVEL SECURITY;
ALTER TABLE pmkb.arista ENABLE ROW LEVEL SECURITY;
ALTER TABLE pmkb.historia ENABLE ROW LEVEL SECURITY;
ALTER TABLE pmkb.vector ENABLE ROW LEVEL SECURITY;
ALTER TABLE pmkb.acceso ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS leer ON pmkb.indice;     CREATE POLICY leer ON pmkb.indice     FOR SELECT USING (pmkb.visible(proyecto));
DROP POLICY IF EXISTS leer ON pmkb.documento;  CREATE POLICY leer ON pmkb.documento  FOR SELECT USING (pmkb.visible(proyecto));
DROP POLICY IF EXISTS leer ON pmkb.version;    CREATE POLICY leer ON pmkb.version    FOR SELECT USING (pmkb.visible(proyecto));
DROP POLICY IF EXISTS leer ON pmkb.unidad;     CREATE POLICY leer ON pmkb.unidad     FOR SELECT USING (pmkb.visible(proyecto, circulacion));
DROP POLICY IF EXISTS leer ON pmkb.lexema;     CREATE POLICY leer ON pmkb.lexema     FOR SELECT USING (pmkb.visible(proyecto));
DROP POLICY IF EXISTS leer ON pmkb.arista;     CREATE POLICY leer ON pmkb.arista     FOR SELECT USING (pmkb.visible(proyecto));
DROP POLICY IF EXISTS leer ON pmkb.historia;   CREATE POLICY leer ON pmkb.historia   FOR SELECT USING (pmkb.visible(proyecto));
DROP POLICY IF EXISTS leer ON pmkb.vector;     CREATE POLICY leer ON pmkb.vector     FOR SELECT USING (pmkb.visible(proyecto));
-- pmkb.acceso: sin política para el lector (solo el dueño la ve; el lector usa pmkb.identidad).

-- Rol de lectura del servicio (lo crea `pm-kb base crear` o la imagen pm-kb-db): solo SELECT, sujeto a RLS.
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'pmkb_lector') THEN
    GRANT USAGE ON SCHEMA pmkb TO pmkb_lector;
    GRANT SELECT ON pmkb.meta, pmkb.indice, pmkb.documento, pmkb.version, pmkb.unidad, pmkb.lexema, pmkb.arista,
                    pmkb.historia, pmkb.vector TO pmkb_lector;
    REVOKE ALL ON pmkb.acceso, pmkb.cache_vector FROM pmkb_lector;
    GRANT EXECUTE ON FUNCTION pmkb.visible(text, text), pmkb.identidad(text) TO pmkb_lector;
  END IF;
END $$;

INSERT INTO pmkb.meta (clave, valor) VALUES ('esquema', '1')
  ON CONFLICT (clave) DO UPDATE SET valor = EXCLUDED.valor;
