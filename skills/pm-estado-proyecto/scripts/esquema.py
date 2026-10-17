#!/usr/bin/env python3
"""Esquema canónico del paquete pm-method: carpetas, registros CSV, prefijos, valores permitidos,
puertas y transiciones. Lo importan nuevo_proyecto.py, registro.py y estado.py.
Canonical schema shared by the scripts. The register guide (pm-registros/templates/guia-registros.md)
documents exactly these columns and values; change both together.
"""
import os, json, csv, datetime

# ---------------------------------------------------------------- carpetas
CARPETAS = [
    "00-direccion", "00-direccion/decisiones", "00-direccion/historial",
    "01-inicio",
    "02-planificacion", "02-planificacion/enfoques", "02-planificacion/productos",
    "02-planificacion/adquisiciones", "02-planificacion/visuales", "02-planificacion/especificacion",
    "03-control/registros", "03-control/paquetes-trabajo", "03-control/reportes", "03-control/reuniones", "03-control/fuentes",
    "04-cierre", "exportados",
]

# ---------------------------------------------------------------- registros
# columnas, prefijo de id, estado inicial, valores permitidos por columna (None = libre), columnas enteras
REGISTROS = {
    "riesgos": {
        "prefijo": "R", "estado_inicial": "abierto",
        "columnas": ["id", "fecha_identificacion", "autor", "categoria", "causa", "evento", "efecto", "tipo",
                     "probabilidad", "impacto", "puntuacion", "impacto_monetario", "valor_esperado", "proximidad",
                     "disparador", "respuesta", "acciones", "propietario", "ejecutor", "probabilidad_residual",
                     "impacto_residual", "estado", "fecha_revision", "notas"],
        "valores": {"tipo": ["amenaza", "oportunidad"],
                    "categoria": ["", "tecnico", "externo", "organizacional", "gestion", "comercial", "sostenibilidad", "otro"],
                    "proximidad": ["", "inminente", "corto-plazo", "mediano-plazo", "largo-plazo"],
                    "respuesta": ["", "evitar", "reducir", "transferir", "compartir", "aceptar", "contingencia",
                                  "escalar", "explotar", "mejorar"],
                    "estado": ["abierto", "en-seguimiento", "escalado", "ocurrido", "retirado", "cerrado"]},
        "enteros_1_5": ["probabilidad", "impacto", "probabilidad_residual", "impacto_residual"],
        "abiertos": ["abierto", "en-seguimiento", "escalado"],
    },
    "issues": {
        "prefijo": "I", "estado_inicial": "abierto",
        "columnas": ["id", "fecha", "autor", "tipo", "titulo", "descripcion", "prioridad", "severidad", "impacto",
                     "decision", "decidido_por", "responsable", "estado", "fecha_cierre", "notas"],
        "valores": {"tipo": ["solicitud-cambio", "fuera-especificacion", "problema-preocupacion", "evento-externo",
                             "oportunidad-negocio"],
                    "prioridad": ["", "urgente", "alta", "media", "baja"],
                    "severidad": ["", "critica", "mayor", "menor", "informativa"],
                    "estado": ["abierto", "en-evaluacion", "en-accion", "escalado", "pendiente-cambio", "resuelto", "cerrado"]},
        "abiertos": ["abierto", "en-evaluacion", "en-accion", "escalado", "pendiente-cambio"],
    },
    "cambios": {
        "prefijo": "C", "estado_inicial": "abierto",
        "columnas": ["id", "fecha", "solicitante", "titulo", "descripcion", "justificacion", "impacto_alcance",
                     "impacto_tiempo", "impacto_costo", "impacto_calidad", "impacto_riesgo", "impacto_beneficios",
                     "recomendacion", "decision", "decidido_por", "fecha_decision", "estado", "notas"],
        "valores": {"decision": ["", "aprobado", "rechazado", "diferido", "pedir-plan-excepcion", "pedir-mas-informacion"],
                    "estado": ["abierto", "en-evaluacion", "pendiente-decision", "aprobado", "rechazado", "diferido",
                               "implementado", "cerrado"]},
        "abiertos": ["abierto", "en-evaluacion", "pendiente-decision", "aprobado", "diferido"],
    },
    "decisiones": {
        "prefijo": "D", "estado_inicial": None,
        "columnas": ["id", "fecha", "decision", "contexto", "opciones_consideradas", "decidido_por", "nivel",
                     "artefactos_afectados", "revisar_en", "notas"],
        "valores": {"nivel": ["equipo", "product-owner", "gestor", "autoridad-cambio", "ejecutivo", "junta", "capa-negocio"]},
    },
    "supuestos": {
        "prefijo": "S", "estado_inicial": "abierto",
        "columnas": ["id", "fecha", "autor", "supuesto_o_restriccion", "tipo", "categoria", "validado",
                     "fecha_validacion", "responsable", "estado", "notas"],
        "valores": {"tipo": ["supuesto", "restriccion"], "validado": ["", "si", "no", "pendiente"],
                    "estado": ["abierto", "validado", "invalidado", "transferido", "cerrado"]},
        "abiertos": ["abierto"],
    },
    "lecciones": {
        "prefijo": "L", "estado_inicial": "registrada",
        "columnas": ["id", "fecha", "etapa", "categoria", "situacion", "efecto", "recomendacion", "prioridad",
                     "responsable_seguimiento", "estado", "notas"],
        "valores": {"prioridad": ["", "alta", "media", "baja"],
                    "estado": ["registrada", "revisada", "accionada-proyecto", "accionada-organizacion", "descartada"]},
        "abiertos": ["registrada", "revisada"],
    },
    "stakeholders": {
        "prefijo": "ST", "estado_inicial": None,
        "columnas": ["id", "nombre", "rol_organizacion", "rol_proyecto", "poder", "interes", "actitud",
                     "nivel_compromiso_actual", "nivel_compromiso_deseado", "expectativas", "canal", "frecuencia",
                     "responsable_relacion", "confidencial", "notas"],
        "valores": {"poder": ["", "alto", "medio", "bajo"], "interes": ["", "alto", "medio", "bajo"],
                    "actitud": ["", "lider", "partidario", "neutral", "resistente", "desconocedor"],
                    "nivel_compromiso_actual": ["", "lider", "partidario", "neutral", "resistente", "desconocedor"],
                    "nivel_compromiso_deseado": ["", "lider", "partidario", "neutral", "resistente", "desconocedor"],
                    "confidencial": ["", "si", "no"]},
    },
    "calidad": {
        "prefijo": "Q", "estado_inicial": "planificada",
        "columnas": ["id", "producto", "metodo_verificacion", "criterios", "responsable_productor", "revisores",
                     "aprobador", "fecha_prevista", "fecha_real", "resultado", "estado", "notas"],
        "valores": {"metodo_verificacion": ["", "revision", "prueba", "inspeccion", "demostracion", "auditoria"],
                    "resultado": ["", "aprobado", "aprobado-con-observaciones", "rechazado", "pendiente"],
                    "estado": ["planificada", "en-curso", "completada", "cancelada"]},
        "abiertos": ["planificada", "en-curso"],
    },
    "acciones": {
        "prefijo": "A", "estado_inicial": "abierta",
        "columnas": ["id", "fecha", "origen", "descripcion", "responsable", "fecha_compromiso", "prioridad",
                     "estado", "fecha_cierre", "notas"],
        "valores": {"prioridad": ["", "alta", "media", "baja"],
                    "estado": ["abierta", "en-curso", "completada", "cancelada"]},
        "abiertos": ["abierta", "en-curso"],
    },
}

# Alias en inglés aceptados al registrar (se guardan en el valor canónico en español).
ALIAS_EN = {
    "threat": ["amenaza"], "opportunity": ["oportunidad"],
    "open": ["abierto", "abierta"], "closed": ["cerrado"], "in-progress": ["en-curso", "en-accion"], "monitoring": ["en-seguimiento"],
    "escalated": ["escalado"], "occurred": ["ocurrido"], "retired": ["retirado"], "resolved": ["resuelto"],
    "done": ["completada"], "completed": ["completada"], "cancelled": ["cancelada"], "planned": ["planificada"],
    "high": ["alto", "alta"], "medium": ["medio", "media"], "low": ["bajo", "baja"], "urgent": ["urgente"],
    "critical": ["critica"], "major": ["mayor"], "minor": ["menor"], "informational": ["informativa"],
    "avoid": ["evitar"], "reduce": ["reducir"], "transfer": ["transferir"], "share": ["compartir"], "accept": ["aceptar"],
    "contingent": ["contingencia"], "escalate": ["escalar"], "exploit": ["explotar"], "enhance": ["mejorar"],
    "request-for-change": ["solicitud-cambio"], "change-request": ["solicitud-cambio"], "off-specification": ["fuera-especificacion"],
    "problem-concern": ["problema-preocupacion"], "problem": ["problema-preocupacion"], "external-event": ["evento-externo"],
    "business-opportunity": ["oportunidad-negocio"], "approved": ["aprobado"], "rejected": ["rechazado"], "deferred": ["diferido"],
    "team": ["equipo"], "manager": ["gestor"], "change-authority": ["autoridad-cambio"], "board": ["junta"], "executive": ["ejecutivo"], "business-layer": ["capa-negocio"],
    "assumption": ["supuesto"], "constraint": ["restriccion"], "yes": ["si"], "no": ["no"],
    "leading": ["lider"], "supportive": ["partidario"], "neutral": ["neutral"], "resistant": ["resistente"], "unaware": ["desconocedor"],
    "review": ["revision"], "test": ["prueba"], "inspection": ["inspeccion"], "demonstration": ["demostracion"], "audit": ["auditoria"],
    "registered": ["registrada"], "reviewed": ["revisada"],
}

# Umbrales de puntuación P×I (escala 1–5 × 1–5). Configurables en el enfoque de gestión del riesgo;
# estos son los valores por defecto del paquete y los usan registro.py, pm-riesgos y el tablero.
UMBRAL_RIESGO_ALTO = 15   # 15–25 alto
UMBRAL_RIESGO_MEDIO = 6   # 6–12 medio; 1–5 bajo

# ---------------------------------------------------------------- estado.json
VERSION_PAQUETE = "2.1.0"          # debe coincidir con .claude-plugin/plugin.json y compatibilidad.json
FASES = ["pre-proyecto", "inicio", "entrega", "cierre", "cerrado"]
PROCESOS = ["SU", "IP", "CS", "SB", "CP"]          # DP y MP son continuos (junta y equipos), no "estado actual"
DIMENSIONES_TOLERANCIA = ["tiempo", "costo", "alcance", "calidad", "beneficios", "riesgo", "sostenibilidad"]
NIVELES_TOLERANCIA = ["proyecto", "etapa"]          # las de paquete de trabajo viven en cada paquete
PUERTAS = ["autorizar-inicio", "autorizar-proyecto", "autorizar-etapa", "autorizar-plan-excepcion",
           "autorizar-cierre", "decision-ad-hoc"]
DECISIONES_PUERTA = ["aprobado", "condicionado", "rechazado", "pendiente"]
ESTADOS_ARTEFACTO = ["borrador", "en-revision", "aprobado", "obsoleto"]


def estado_inicial(nombre, idioma="es", enfoque="predictivo", ejecutivo="", gestor=""):
    hoy = datetime.date.today().isoformat()
    return {
        "proyecto": nombre, "idioma": idioma, "metodo": "prince2-por-etapas", "version_paquete": VERSION_PAQUETE,
        "enfoque_entrega": enfoque, "fase": "pre-proyecto", "proceso_actual": "SU",
        "etapa_actual": {"numero": 0, "nombre": "pre-proyecto" if idioma == "es" else "pre-project",
                         "inicio": hoy, "fin_previsto": ""},
        "proyecto_autorizado": False,
        "excepcion_abierta": "",
        "tolerancias": {n: {k: "" for k in DIMENSIONES_TOLERANCIA} for n in NIVELES_TOLERANCIA},
        "roles": {"ejecutivo": ejecutivo, "usuario_senior": [], "proveedor_senior": [], "gestor_proyecto": gestor,
                  "aseguramiento": [], "soporte": "", "autoridad_cambio": "", "product_owner": "", "jefes_equipo": []},
        "agil": {"cadencia_iteracion_dias": "", "velocidad_referencia": "", "tracker_backlog": ""},
        "umbrales_riesgo": {"alto": UMBRAL_RIESGO_ALTO, "medio": UMBRAL_RIESGO_MEDIO},
        "artefactos": {}, "puertas": [],
        "integraciones": {"tracker": "ninguno", "chat": "ninguno", "docs": "ninguno", "reuniones": "manual", "okr": "archivo",
                          "diagramas": "mermaid", "cronograma": "cpm", "export": "scripts", "especificacion": "ninguna"},
        "creado": hoy, "actualizado": hoy, "version_estado": 1,
    }


# valores conocidos de estado.json.integraciones (los usan estado.py integracion y sanidad INT-01)
VALORES_INTEGRACION = {"tracker": {"ninguno", "jira", "linear", "github", "azure-devops"}, "chat": {"ninguno", "slack", "teams"},
    "docs": {"ninguno", "confluence", "notion", "sharepoint"}, "reuniones": {"manual", "archivo", "granola", "fireflies", "zoom", "minutes", "teams"},
    "okr": {"archivo", "tability"}, "especificacion": {"ninguna", "bmad"},
    "diagramas": {"mermaid", "diagram-design", "archify", "visual-explainer", "drawio"}, "cronograma": {"cpm", "mspdi"},
    "export": {"scripts", "skills-office"}}

def migrar(e):
    """Actualiza estado.json de versiones anteriores del paquete sin perder datos."""
    tol = e.get("tolerancias", {})
    if tol and all(isinstance(v, str) for v in tol.values()):
        e["tolerancias"] = {"proyecto": {k: tol.get(k, "") for k in DIMENSIONES_TOLERANCIA},
                            "etapa": {k: "" for k in DIMENSIONES_TOLERANCIA}}
    for n in NIVELES_TOLERANCIA:
        e.setdefault("tolerancias", {}).setdefault(n, {k: "" for k in DIMENSIONES_TOLERANCIA})
    e.setdefault("roles", {}).setdefault("product_owner", "")
    e["roles"].setdefault("jefes_equipo", [])
    e.setdefault("agil", {"cadencia_iteracion_dias": "", "velocidad_referencia": "", "tracker_backlog": ""})
    e.setdefault("proyecto_autorizado", any(p.get("tipo") == "autorizar-proyecto" and p.get("decision") in ("aprobado", "condicionado") for p in e.get("puertas", [])))
    e.setdefault("excepcion_abierta", "")
    e.setdefault("umbrales_riesgo", {"alto": UMBRAL_RIESGO_ALTO, "medio": UMBRAL_RIESGO_MEDIO})
    for k, v in {"tracker": "ninguno", "chat": "ninguno", "docs": "ninguno", "reuniones": "manual", "okr": "archivo",
                 "diagramas": "mermaid", "cronograma": "cpm", "export": "scripts", "especificacion": "ninguna"}.items():
        e.setdefault("integraciones", {}).setdefault(k, v)
    if e["integraciones"].get("cronograma") in ("mermaid", "utf8proj"): e["integraciones"]["cronograma"] = "cpm"
    if e.get("fase") == "planificacion": e["fase"] = "inicio"
    if e.get("fase") == "ejecucion": e["fase"] = "entrega"     # v1 → v2: nombre PRINCE2 (etapas de entrega)
    return e


# ---------------------------------------------------------------- utilidades CSV
def ruta_registro(proyecto, reg):
    return os.path.join(proyecto, "03-control", "registros", f"{reg}.csv")


def leer_csv(p):
    with open(p, newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        filas = list(rd); cols = list(rd.fieldnames or [])
    return cols, filas


def escribir_csv(p, cols, filas):
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(filas)


def siguiente_id(reg, filas):
    pref = REGISTROS[reg]["prefijo"]; n = 0
    for f in filas:
        v = f.get("id", "")
        if v.startswith(pref + "-"):
            try: n = max(n, int(v.split("-", 1)[1]))
            except ValueError: pass
    return f"{pref}-{n + 1:03d}"


def asegurar_registro(proyecto, reg):
    """Crea el CSV si falta y agrega columnas nuevas del esquema al final (migración no destructiva)."""
    p = ruta_registro(proyecto, reg)
    esperado = REGISTROS[reg]["columnas"]
    if not os.path.exists(p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        escribir_csv(p, esperado, []); return p
    cols, filas = leer_csv(p)
    faltan = [c for c in esperado if c not in cols]
    if faltan: escribir_csv(p, cols + faltan, filas)
    return p


def anotar_decision(proyecto, decision, decidido_por, nivel="junta", contexto="", artefactos="", notas="", fecha=None):
    p = asegurar_registro(proyecto, "decisiones")
    cols, filas = leer_csv(p)
    fila = {c: "" for c in cols}
    fila.update({"id": siguiente_id("decisiones", filas), "fecha": fecha or datetime.date.today().isoformat(),
                 "decision": decision, "contexto": contexto, "decidido_por": decidido_por, "nivel": nivel,
                 "artefactos_afectados": artefactos, "notas": notas})
    filas.append(fila); escribir_csv(p, cols, filas)
    return fila["id"]


def t(idioma, es, en):
    """Mensaje según idioma del proyecto."""
    return en if idioma == "en" else es


def cargar_estado(proyecto):
    f = os.path.join(proyecto, "estado.json")
    if not os.path.exists(f):
        raise SystemExit("No existe estado.json; ejecutar nuevo_proyecto.py / estado.json not found; run nuevo_proyecto.py")
    return migrar(json.load(open(f, encoding="utf-8")))


def idioma_de(proyecto):
    try: return json.load(open(os.path.join(proyecto, "estado.json"), encoding="utf-8")).get("idioma", "es")
    except Exception: return "es"
