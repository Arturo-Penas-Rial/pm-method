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
                     "recomendacion", "decision", "decidido_por", "fecha_decision", "estado", "notas", "costo", "cargo"],
        "valores": {"decision": ["", "aprobado", "rechazado", "diferido", "pedir-plan-excepcion", "pedir-mas-informacion"],
                    "cargo": ["", "presupuesto-cambio", "reserva-riesgo", "reserva-gestion", "plan-excepcion", "sin-costo"],
                    "estado": ["abierto", "en-evaluacion", "pendiente-decision", "aprobado", "rechazado", "diferido",
                               "implementado", "cerrado"]},
        "numericos": ["costo"],
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
                     "fecha_validacion", "responsable", "estado", "notas",
                     "criticidad", "certeza", "experimento", "criterio", "fecha_limite", "evidencia"],
        # criticidad: cuánto afecta al caso si resulta falso; certeza: cuánta evidencia hay hoy. Un supuesto de
        # criticidad alta y certeza baja es una hipótesis a validar antes de invertir (experimento + criterio + fecha).
        "valores": {"tipo": ["supuesto", "restriccion"], "validado": ["", "si", "no", "pendiente"],
                    "criticidad": ["", "alta", "media", "baja"], "certeza": ["", "alta", "media", "baja"],
                    "estado": ["abierto", "validado", "invalidado", "transferido", "cerrado"]},
        "abiertos": ["abierto"],
    },
    "lecciones": {
        "prefijo": "L", "estado_inicial": "registrada",
        "columnas": ["id", "fecha", "etapa", "categoria", "situacion", "efecto", "recomendacion", "prioridad",
                     "responsable_seguimiento", "estado", "notas", "origen", "etiquetas",
                     "impacto", "recurrencia", "aplicar_en", "accion", "verificar_en", "verificacion"],
        # origen: "<proyecto> · L-### · fecha" de una lección previa traída de otro proyecto (lecciones.py incorporar);
        # sus textos citan ids de ese proyecto, por eso REG-08 no revisa las filas con origen. etiquetas: "a;b" (búsqueda).
        # Ciclo (pm-lecciones-aprendidas, lecciones.py): registrada (identificada) → revisada (clasificada: impacto,
        # recurrencia, aplicar_en) → accionada-proyecto|accionada-organizacion (accion: ids o artefacto; verificar_en:
        # fecha para comprobar el efecto) → verificada (verificacion: fecha, resultado y evidencia) o descartada con motivo.
        "valores": {"prioridad": ["", "alta", "media", "baja"],
                    "impacto": ["", "alto", "medio", "bajo"], "recurrencia": ["", "alta", "media", "baja"],
                    "estado": ["registrada", "revisada", "accionada-proyecto", "accionada-organizacion", "verificada", "descartada"]},
        # columnas con varios valores separados por «;» (registro.py y sanidad REG-05 validan cada uno)
        "multivalor": {"aplicar_en": ["ideacion", "descubrimiento", "planificacion", "seguimiento"]},
        "abiertos": ["registrada", "revisada"],
    },
    "stakeholders": {
        "prefijo": "ST", "estado_inicial": None, "refs": {"estereotipo": "estereotipos"},
        "columnas": ["id", "nombre", "rol_organizacion", "rol_proyecto", "poder", "interes", "actitud",
                     "nivel_compromiso_actual", "nivel_compromiso_deseado", "expectativas", "canal", "frecuencia",
                     "responsable_relacion", "confidencial", "notas", "estereotipo", "correo", "usuario_chat"],
        "valores": {"poder": ["", "alto", "medio", "bajo"], "interes": ["", "alto", "medio", "bajo"],
                    "actitud": ["", "lider", "partidario", "neutral", "resistente", "desconocedor"],
                    "nivel_compromiso_actual": ["", "lider", "partidario", "neutral", "resistente", "desconocedor"],
                    "nivel_compromiso_deseado": ["", "lider", "partidario", "neutral", "resistente", "desconocedor"],
                    "confidencial": ["", "si", "no"]},
    },
    # ---- maestro de interesados (dueña pm-interesados). "opcional": se crean al primer uso, no en proyectos nuevos.
    "estereotipos": {
        "prefijo": "ET", "estado_inicial": "activo", "opcional": True,
        "columnas": ["id", "nombre", "descripcion", "cuadrante", "canal", "formato", "nivel_detalle", "frecuencia",
                     "idioma", "registro", "horario", "estilo_decision", "evitar", "estado", "notas"],
        "valores": {"cuadrante": ["", "gestionar-de-cerca", "mantener-satisfecho", "mantener-informado", "monitorear"],
                    "canal": ["", "correo", "slack", "teams", "reunion", "llamada", "tablero", "documento"],
                    "formato": ["", "conclusion-primero", "narrativa", "datos", "visual", "lista"],
                    "nivel_detalle": ["", "ejecutivo", "resumen", "detallado"],
                    "frecuencia": ["", "diaria", "semanal", "quincenal", "mensual", "trimestral", "por-hito", "a-demanda"],
                    "idioma": ["", "es", "en", "pt"],
                    "registro": ["", "formal", "neutral", "cercano"],
                    "estilo_decision": ["", "datos", "consenso", "rapido", "delegado"],
                    "estado": ["activo", "retirado"]},
        "abiertos": ["activo"],
        # catálogo: "activo" no es trabajo pendiente; estado.py contexto no lo cuenta entre los abiertos
        "catalogo": True,
    },
    "preferencias": {
        "prefijo": "PF", "estado_inicial": "propuesta", "opcional": True, "refs": {"stakeholder_id": "stakeholders"},
        "columnas": ["id", "fecha", "stakeholder_id", "dimension", "valor", "procedencia", "evidencia", "fuente",
                     "vigencia_hasta", "estado", "confirmado_por", "notas"],
        "valores": {"dimension": ["canal", "formato", "nivel_detalle", "frecuencia", "idioma", "registro", "horario",
                                  "estilo_decision", "evitar", "otro"],
                    "procedencia": ["declarado", "observado", "inferido"],
                    "estado": ["propuesta", "confirmada", "rechazada", "vencida"]},
        "abiertos": ["propuesta"],
    },
    "raci": {
        "prefijo": "RC", "estado_inicial": None, "opcional": True, "refs": {"stakeholder_id": "stakeholders"},
        "unico": ["elemento", "stakeholder_id"], "uno_por": {"rol": "A", "grupo": "elemento"},
        "columnas": ["id", "elemento", "tipo_elemento", "descripcion", "stakeholder_id", "rol", "notas"],
        "valores": {"rol": ["R", "A", "C", "I"],
                    "tipo_elemento": ["", "producto", "paquete", "actividad", "entregable", "requisito", "epica",
                                      "historia", "kr", "objetivo", "decision", "otro"]},
    },
    "envios": {
        "prefijo": "EN", "estado_inicial": "pendiente", "opcional": True, "refs": {"stakeholder_id": "stakeholders"},
        "columnas": ["id", "fecha", "stakeholder_id", "canal", "modo", "destino", "asunto", "proposito", "archivo", "estado",
                     "referencia", "confirmado_por", "notas"],
        "valores": {"canal": ["", "correo", "slack", "teams", "reunion", "llamada", "tablero", "documento"],
                    "proposito": ["", "comunicado", "informe", "recordatorio", "convocatoria", "puerta", "okr", "acta", "otro"],
                    "modo": ["", "mcp", "smtp", "slack-webhook", "teams-webhook", "eml", "manual"],
                    "estado": ["pendiente", "simulado", "enviado", "fallido", "cancelado"]},
        "abiertos": ["pendiente", "fallido"],
    },
    # personas de usuario (arquetipos que usan, piden o se benefician de las capacidades; no son interesados ni estereotipos
    # de comunicación). solicita/usa/beneficia: ids de requisitos, épicas, historias o productos de la WBS separados por «;»;
    # beneficios: B-##/DB-## del business case. Dueña pm-interesados (interesados.py personas).
    "personas": {
        "prefijo": "PU", "estado_inicial": "activa", "opcional": True, "refs": {"stakeholder_id": "stakeholders"},
        "columnas": ["id", "nombre", "descripcion", "objetivo", "dolores", "contexto_uso", "fuente", "evidencia", "stakeholder_id",
                     "solicita", "usa", "beneficia", "beneficios", "estado", "notas"],
        "valores": {"fuente": ["", "entrevista", "bmad-uj", "encuesta", "observacion", "documento", "supuesto"],
                    "estado": ["activa", "retirada"]},
        "abiertos": ["activa"],
        "catalogo": True,
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
    "open": ["abierto", "abierta"], "closed": ["cerrado"], "in-progress": ["en-curso", "en-accion"], "monitoring": ["en-seguimiento", "seguimiento"],
    "escalated": ["escalado"], "occurred": ["ocurrido"], "retired": ["retirado", "retirada"], "resolved": ["resuelto"],
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
    "registered": ["registrada"], "reviewed": ["revisada"], "verified": ["verificada"], "discarded": ["descartada"],
    "ideation": ["ideacion"], "discovery": ["descubrimiento"], "planning": ["planificacion"],
    "proposed": ["propuesta"], "confirmed": ["confirmada"], "expired": ["vencida"], "declared": ["declarado"], "observed": ["observado"],
    "inferred": ["inferido"], "active": ["activo", "activa"], "sent": ["enviado"],
    "interview": ["entrevista"], "survey": ["encuesta"], "observation": ["observacion"],
    "simulated": ["simulado"], "failed": ["fallido"], "pending": ["pendiente"],
    "email": ["correo"], "meeting": ["reunion"], "call": ["llamada"], "dashboard": ["tablero"], "document": ["documento"],
    "manage-closely": ["gestionar-de-cerca"], "keep-satisfied": ["mantener-satisfecho"], "keep-informed": ["mantener-informado"], "monitor": ["monitorear"],
    "bottom-line-up-front": ["conclusion-primero"], "narrative": ["narrativa"], "data": ["datos"], "visual": ["visual"], "list": ["lista"],
    "executive": ["ejecutivo"], "summary": ["resumen"], "detailed": ["detallado"], "daily": ["diaria"], "weekly": ["semanal"],
    "biweekly": ["quincenal"], "monthly": ["mensual"], "per-milestone": ["por-hito"], "on-demand": ["a-demanda"],
    "formal": ["formal"], "casual": ["cercano"], "consensus": ["consenso"], "fast": ["rapido"], "delegated": ["delegado"],
}

# Umbrales de puntuación P×I (escala 1–5 × 1–5). Configurables en el enfoque de gestión del riesgo;
# estos son los valores por defecto del paquete y los usan registro.py, pm-riesgos y el tablero.
UMBRAL_RIESGO_ALTO = 15   # 15–25 alto
UMBRAL_RIESGO_MEDIO = 6   # 6–12 medio; 1–5 bajo

# ---------------------------------------------------------------- estado.json
VERSION_PAQUETE = "2.4.0"          # debe coincidir con .claude-plugin/plugin.json y compatibilidad.json
FASES = ["pre-proyecto", "inicio", "entrega", "cierre", "cerrado"]
PROCESOS = ["SU", "IP", "CS", "SB", "CP"]          # DP y MP son continuos (junta y equipos), no "estado actual"
DIMENSIONES_TOLERANCIA = ["tiempo", "costo", "alcance", "calidad", "beneficios", "riesgo", "sostenibilidad"]
NIVELES_TOLERANCIA = ["proyecto", "etapa"]          # las de paquete de trabajo viven en cada paquete
PUERTAS = ["autorizar-inicio", "autorizar-proyecto", "autorizar-etapa", "autorizar-plan-excepcion",
           "autorizar-cierre", "decision-ad-hoc"]
DECISIONES_PUERTA = ["aprobado", "condicionado", "rechazado", "pendiente"]
# presupuestos que fija la junta (montos en la moneda del proyecto): presupuesto de cambio, reserva de riesgo (contingencia),
# reserva de gestión y límite por cambio que puede aprobar la autoridad de cambio delegada (PRINCE2: issues y planes).
CLAVES_PRESUPUESTO = ["cambio", "riesgo", "gestion", "limite_autoridad_cambio"]
# cargos que consumen un presupuesto fijado por la junta (clave en `presupuestos`); lo usan sanidad (CAM-03) y registro.py
CARGO_PRESUPUESTO = {"presupuesto-cambio": "cambio", "reserva-riesgo": "riesgo"}
CAMBIO_VIGENTE = ("aprobado", "implementado", "cerrado")


def monto(v):
    """Monto de un registro o de `presupuestos` como número (None si está vacío o no es número)."""
    try: return float(str(v or "").strip().replace(",", "."))
    except ValueError: return None


def es_junta(e, quien):
    """¿`decidido_por` es la junta o el ejecutivo? Se reconoce por "ejecutiv", "junta", "board", "executive" o el nombre
    del ejecutivo de `estado.json.roles` (criterio común de sanidad CAM-04/CAM-05 y de registro.py)."""
    q = (quien or "").lower(); ej = (e.get("roles", {}).get("ejecutivo") or "").lower()
    return any(x in q for x in ("ejecutiv", "junta", "board", "executive")) or (bool(ej) and ej in q)


def cambio_vigente(f):
    """Un cambio cuenta contra los presupuestos si está aprobado, implementado o cerrado, o tiene decision=aprobado."""
    return f.get("estado") in CAMBIO_VIGENTE or f.get("decision") == "aprobado"


def consumo_cambios(filas, excluir=None):
    """Consumo por cargo (presupuesto-cambio, reserva-riesgo) de los cambios vigentes, sin el id `excluir`."""
    consumo = {c: 0.0 for c in CARGO_PRESUPUESTO}
    for f in filas:
        if f.get("id") == excluir or not cambio_vigente(f): continue
        c = monto(f.get("costo"))
        if c is not None and f.get("cargo") in consumo: consumo[f["cargo"]] += c
    return consumo
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
        "presupuestos": {k: "" for k in CLAVES_PRESUPUESTO},
        "artefactos": {}, "puertas": [],
        "integraciones": {"tracker": "ninguno", "chat": "ninguno", "docs": "ninguno", "reuniones": "manual", "okr": "archivo",
                          "diagramas": "mermaid", "cronograma": "cpm", "export": "scripts", "especificacion": "ninguna",
                          "correo": "ninguno"},
        "creado": hoy, "actualizado": hoy, "version_estado": 1,
    }


# valores conocidos de estado.json.integraciones (los usan estado.py integracion y sanidad INT-01)
VALORES_INTEGRACION = {"tracker": {"ninguno", "jira", "linear", "github", "azure-devops"}, "chat": {"ninguno", "slack", "teams"},
    "correo": {"ninguno", "smtp", "gmail", "outlook", "eml"},
    "docs": {"ninguno", "confluence", "notion", "sharepoint"}, "reuniones": {"manual", "archivo", "granola", "fireflies", "zoom", "minutes", "teams"},
    "okr": {"archivo", "tability", "perdoo"}, "especificacion": {"ninguna", "bmad"},
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
    for k in CLAVES_PRESUPUESTO: e.setdefault("presupuestos", {}).setdefault(k, "")
    for k, v in {"tracker": "ninguno", "chat": "ninguno", "docs": "ninguno", "reuniones": "manual", "okr": "archivo",
                 "diagramas": "mermaid", "cronograma": "cpm", "export": "scripts", "especificacion": "ninguna",
                 "correo": "ninguno"}.items():
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
