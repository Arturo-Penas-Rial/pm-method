#!/usr/bin/env python3
"""Esquema canónico del paquete pm-method: carpetas, registros CSV, prefijos, valores permitidos,
puertas y transiciones. Lo importan nuevo_proyecto.py, registro.py y estado.py.
Canonical schema shared by the scripts. The register guide (pm-registros/templates/guia-registros.md)
documents exactly these columns and values; change both together.
"""
import os, json, csv, datetime, contextlib, errno, io, random, re, stat, sys, threading, time, unicodedata, uuid

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
                     "artefactos_afectados", "revisar_en", "notas", "reemplaza", "conviven"],
        # reemplaza: D-### que esta decisión deja sin efecto (nivel igual o superior; registro.py lo valida); conviven: D-###
        # que la persona decidió mantener vigentes a la vez. "Reemplazada por" se deriva (vigencia.py; sanidad DEC-05/DEC-06).
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
VERSION_PAQUETE = "2.6.0"          # debe coincidir con .claude-plugin/plugin.json y compatibilidad.json
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


# Nivel de autoridad de una persona (PRINCE2 manda; la RACI debe reflejarlo). Primero los roles de estado.json por nombre;
# después las palabras del rol escrito ("Gestor: Ana", rol_proyecto del maestro). Se toma el más alto que coincida. La
# junta es un órgano colectivo: ejecutivo, usuarios sénior y proveedores sénior tienen autoridad de nivel junta.
NIVEL_DE_ROL = {"ejecutivo": "junta", "usuario_senior": "junta", "proveedor_senior": "junta", "autoridad_cambio": "autoridad-cambio",
                "gestor_proyecto": "gestor", "product_owner": "product-owner", "jefes_equipo": "equipo", "aseguramiento": "equipo",
                "soporte": "equipo"}
PALABRAS_NIVEL = [                     # sobre el texto en minúsculas y sin acentos
    ("capa-negocio", r"capa de negocio|capa-negocio|corporativ|corporate|business layer"),
    ("junta", r"ejecutiv|executive|junta|board|usuari[oa] senior|senior user|proveedor(?:a)? senior|senior supplier"),
    ("autoridad-cambio", r"autoridad de cambio|change authority"),
    ("gestor", r"\bgestor(?:a)?\b|jef[ea] de proyecto|gerente de proyecto|director(?:a)? de proyecto|project manager"),
    ("product-owner", r"product owner|duen[oa] (?:del? )?producto"),
    ("equipo", r"jef[ea] de equipo|team manager|team lead|\bequipo\b|\bteam\b|desarrollador|developer|analista|aseguramiento|assurance|soporte"),
]
NIVELES_DECISION = REGISTROS["decisiones"]["valores"]["nivel"]   # orden de menor a mayor autoridad


def _plano(x):
    return unicodedata.normalize("NFKD", str(x or "")).encode("ascii", "ignore").decode().lower().strip()


def nivel_autoridad(e, texto, nombre=""):
    """(nivel, fuente) de quien firma `texto` ("<rol: nombre>" o el rol de un interesado) y se llama `nombre`; (None, "")
    si no se puede determinar. Fuente: 'estado.json.roles.<rol>' o 'texto del rol'."""
    plano, nom = _plano(texto), _plano(nombre)
    esta = lambda a, b: re.search(r"(?<![a-z0-9])" + re.escape(a) + r"(?![a-z0-9])", b)
    hall = []
    for rol, nivel in NIVEL_DE_ROL.items():
        v = (e.get("roles") or {}).get(rol)
        for n in (v if isinstance(v, list) else re.split(r"[;,]", v or "")):
            n = _plano(n)
            if len(n) >= 3 and (esta(n, plano) or (len(nom) >= 3 and esta(nom, n))): hall.append((nivel, f"estado.json.roles.{rol}"))
    for nivel, rx in PALABRAS_NIVEL:
        if re.search(rx, plano): hall.append((nivel, "texto del rol")); break
    if not hall: return None, ""
    return max(hall, key=lambda x: NIVELES_DECISION.index(x[0]))


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
    """Reescribe el CSV entero de forma atómica (mismo formato que csv.DictWriter: UTF-8, CRLF, columnas en orden).
    El llamador que lee, modifica y escribe debe hacerlo dentro de `bloqueo(proyecto)`."""
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(filas)
    escribir_atomico(p, buf.getvalue(), newline="")


def siguiente_id(reg, filas):
    pref = REGISTROS[reg]["prefijo"]; n = 0
    for f in filas:
        v = f.get("id", "")
        if v.startswith(pref + "-"):
            try: n = max(n, int(v.split("-", 1)[1]))
            except ValueError: pass
    return f"{pref}-{n + 1:03d}"


def asegurar_registro(proyecto, reg):
    """Crea el CSV si falta y agrega columnas nuevas del esquema al final (migración no destructiva).
    Solo toma el bloqueo del proyecto cuando hay que escribir (crear o migrar); la lectura no espera."""
    p = ruta_registro(proyecto, reg)
    esperado = REGISTROS[reg]["columnas"]
    if os.path.exists(p) and not [c for c in esperado if c not in leer_csv(p)[0]]: return p
    with bloqueo(proyecto):
        if not os.path.exists(p):
            os.makedirs(os.path.dirname(p), exist_ok=True)
            escribir_csv(p, esperado, []); return p
        cols, filas = leer_csv(p)
        faltan = [c for c in esperado if c not in cols]
        if faltan: escribir_csv(p, cols + faltan, filas)
    return p


def anotar_decision(proyecto, decision, decidido_por, nivel="junta", contexto="", artefactos="", notas="", fecha=None):
    with bloqueo(proyecto):    # reentrante: estado.py, puertas.py y bmad.py la llaman con el bloqueo ya tomado
        p = asegurar_registro(proyecto, "decisiones")
        cols, filas = leer_csv(p)
        fila = {c: "" for c in cols}
        fila.update({"id": siguiente_id("decisiones", filas), "fecha": fecha or datetime.date.today().isoformat(),
                     "decision": decision, "contexto": contexto, "decidido_por": decidido_por, "nivel": nivel,
                     "artefactos_afectados": artefactos, "notas": notas})
        if "reemplaza" in cols:    # versión nueva de un artefacto aprobado: reemplaza a la aprobación anterior (vigencia.py)
            import vigencia
            fila["reemplaza"] = vigencia.reemplazo_automatico(filas, decision, nivel, artefactos, fila["fecha"])
        filas.append(fila); escribir_csv(p, cols, filas)
    return fila["id"]


# ---------------------------------------------------------------- escrituras concurrentes (2.5.1)
# Un bloqueo por proyecto serializa toda lectura-modificación-escritura de estado.json, de los registros CSV y de los
# demás archivos de gobierno que se reescriben enteros; cada escritura es atómica (temporal en la misma carpeta +
# fsync + os.replace). Biblioteca estándar: fcntl.flock en POSIX y msvcrt.locking en Windows. docs/ARQUITECTURA.md §10.
DIR_BLOQUEO = ".pm-bloqueo"               # dentro de la carpeta del proyecto; su .gitignore ("*") la deja fuera de git
ARCHIVO_BLOQUEO = "bloqueo"
VAR_ESPERA = "PM_BLOQUEO_ESPERA"          # segundos de espera máxima (defecto ESPERA_BLOQUEO; 0 = un solo intento)
VAR_HEREDADO = "PM_BLOQUEO_HEREDADO"      # proyectos cuyo bloqueo tiene el proceso padre (subprocesos que este espera)
ESPERA_BLOQUEO = 30.0
_TOMADOS = {}                             # (carpeta real, hilo) → [archivo, profundidad]: reentrante en el mismo hilo
_SIN_SOPORTE = {getattr(errno, x) for x in ("ENOLCK", "EOPNOTSUPP", "ENOTSUP", "ENOSYS") if hasattr(errno, x)}

try:
    import fcntl
except ImportError:                       # Windows nativo
    fcntl = None
    import msvcrt


def espera_bloqueo():
    v = os.environ.get(VAR_ESPERA, "").strip()
    try: return max(0.0, float(v)) if v else ESPERA_BLOQUEO
    except ValueError: return ESPERA_BLOQUEO


def _intentar(fh):
    """Un intento sin espera; True si se obtuvo el bloqueo."""
    try:
        if fcntl: fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        else: fh.seek(0); msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
        return True
    except OSError as x:
        if x.errno in _SIN_SOPORTE: raise
        return False


def _soltar(fh):
    if fh is None: return
    try:
        if fcntl: fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        else: fh.seek(0); msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
    except OSError:
        pass
    finally:
        fh.close()


def _heredados():
    try: return set(json.loads(os.environ.get(VAR_HEREDADO) or "[]"))
    except ValueError: return set()


@contextlib.contextmanager
def bloqueo(proyecto, espera=None, nuevo=False):
    """Bloqueo exclusivo de escritura del proyecto, con espera máxima (PM_BLOQUEO_ESPERA, 30 s por defecto).
    Reentrante en el mismo hilo y heredado por los subprocesos que el titular lanza y espera (p. ej. sanidad.py desde
    puertas.py). Sin estado.json (carpeta que no es un proyecto) no bloquea, salvo `nuevo=True` (nuevo_proyecto.py).
    Si no se obtiene a tiempo: SystemExit con mensaje bilingüe y nada modificado. Exclusive per-project write lock."""
    d = os.path.realpath(proyecto)
    clave = (d, threading.get_ident())
    if clave in _TOMADOS:
        _TOMADOS[clave][1] += 1
        try: yield
        finally: _TOMADOS[clave][1] -= 1
        return
    if d in _heredados() or not os.path.isdir(d) or not (nuevo or os.path.isfile(os.path.join(d, "estado.json"))):
        yield; return
    carpeta = os.path.join(d, DIR_BLOQUEO); ruta = os.path.join(carpeta, ARCHIVO_BLOQUEO)
    try:
        os.makedirs(carpeta, exist_ok=True)
        if not os.path.exists(os.path.join(carpeta, ".gitignore")):
            try:
                with open(os.path.join(carpeta, ".gitignore"), "x", encoding="utf-8") as g:
                    g.write("# pm-method: bloqueo de escrituras concurrentes (no versionar) / write lock (do not commit)\n*\n")
            except FileExistsError: pass
        fh = open(ruta, "a+b")
    except OSError as x:
        raise SystemExit(f"No se pudo crear el archivo de bloqueo {ruta}: {x}. Comprobar los permisos de escritura de la carpeta del proyecto.\n"
                         f"Could not create the lock file {ruta}: {x}. Check write permissions on the project folder.")
    limite = espera_bloqueo() if espera is None else max(0.0, float(espera))
    fin = time.monotonic() + limite
    try:
        while not _intentar(fh):
            resta = fin - time.monotonic()
            if resta <= 0:
                fh.close()
                raise SystemExit(f"Otro proceso está modificando el proyecto {proyecto} y no liberó el bloqueo en {limite:g} s ({ruta}); "
                                 f"no se modificó nada. Reintentar en unos segundos: el sistema operativo libera el bloqueo cuando ese "
                                 f"proceso termina (no hace falta borrar el archivo). Espera ajustable con {VAR_ESPERA}=<segundos>.\n"
                                 f"Another process is modifying project {proyecto} and did not release the lock within {limite:g} s ({ruta}); "
                                 f"nothing was changed. Retry in a few seconds: the operating system releases the lock when that process "
                                 f"ends (no need to delete the file). Adjust the wait with {VAR_ESPERA}=<seconds>.")
            time.sleep(min(resta, 0.02 + random.random() * 0.06))
    except OSError as x:                  # sistema de archivos sin bloqueos (algunos montajes de red): sigue sin bloqueo
        fh.close(); fh = None
        print(f"AVISO: el sistema de archivos de {d} no admite bloqueos ({x}); la escritura sigue siendo atómica, pero sin "
              f"exclusión entre procesos. / WARNING: no file locking on this file system; writes stay atomic but are not serialized.",
              file=sys.stderr)
    _TOMADOS[clave] = [fh, 1]
    previo = os.environ.get(VAR_HEREDADO)
    os.environ[VAR_HEREDADO] = json.dumps(sorted(_heredados() | {d}))
    try:
        yield
    finally:
        del _TOMADOS[clave]
        if previo is None: os.environ.pop(VAR_HEREDADO, None)
        else: os.environ[VAR_HEREDADO] = previo
        _soltar(fh)


def escribir_atomico(ruta, texto, newline=None, encoding="utf-8"):
    """Escribe `texto` en `ruta` de forma atómica: temporal oculto en la misma carpeta, flush + fsync y os.replace.
    `newline` y `encoding` se aplican igual que en open(ruta, "w", ...), así los bytes son los de antes; conserva los
    permisos del archivo existente. Si el proceso se interrumpe, el archivo anterior queda intacto."""
    destino = os.path.realpath(ruta)
    carpeta = os.path.dirname(destino)
    gobernado = _gobernado(ruta)          # estado.json, registro o propuesta: la escritura se anota en la bitácora (2.6.0)
    previo = _leer_bytes(destino) if gobernado else None
    try: modo = stat.S_IMODE(os.stat(destino).st_mode)
    except FileNotFoundError: modo = None
    tmp = os.path.join(carpeta, f".{os.path.basename(destino)}.{os.getpid()}.{uuid.uuid4().hex[:8]}.tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o666)
    try:
        with open(fd, "w", encoding=encoding, newline=newline) as f:
            f.write(texto); f.flush(); os.fsync(f.fileno())
        if modo is not None:
            try: os.chmod(tmp, modo)
            except OSError: pass
        for intento in range(40):
            try: os.replace(tmp, destino); break
            except PermissionError:       # Windows: un lector tiene el archivo abierto; reintentar
                if os.name != "nt" or intento == 39: raise
                time.sleep(0.05)
    except BaseException:
        try: os.unlink(tmp)
        except OSError: pass
        raise
    if os.name != "nt":
        try:
            dfd = os.open(carpeta, os.O_RDONLY)
            try: os.fsync(dfd)
            finally: os.close(dfd)
        except OSError: pass
    if gobernado: anotar_bitacora(gobernado[0], gobernado[1], previo, _leer_bytes(destino))


def escribir_json(ruta, datos):
    """JSON con el formato de siempre (ensure_ascii=False, indent=2, sin salto final), escrito de forma atómica."""
    escribir_atomico(ruta, json.dumps(datos, ensure_ascii=False, indent=2))


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


# ---------------------------------------------------------------- bitácora de escrituras (2.6.0)
# Toda escritura de estado.json, de un registro CSV o de una propuesta (03-control/propuestas/P-###.json) que pasa por
# escribir_atomico (escribir_csv, escribir_json, anotar_decision: estado.py, registro.py, puertas.py, interesados.py…)
# agrega una línea JSON a <proyecto>/.bitacora.jsonl, solo anexado y bajo el bloqueo del proyecto: número, fecha y hora,
# script, operación, archivo, ids y campos cambiados (antes → después, sin valores de interesados ni de filas
# confidencial=si), --por si lo hay, huellas sha256 del archivo antes y después, y huella de la línea anterior (cadena).
# Una reescritura sin cambios no se anota. Sin deshacer: una decisión se corrige con una fila nueva (SPEC §1.10.16).
import hashlib as _hashlib
ARCHIVO_BITACORA = ".bitacora.jsonl"
DIR_PROPUESTAS = os.path.join("03-control", "propuestas")
BITACORA_SIN_VALORES = ("stakeholders", "estereotipos", "preferencias", "envios", "personas")   # solo nombres de campo
TOPE_VALOR_BITACORA = 160
_CONTEXTO_BITACORA = {}


def contexto_bitacora(**kw):
    """Datos de la escritura en curso que el script conoce mejor que sys.argv (operacion, por, propuesta, propuesto_por).
    Un valor None los quita."""
    for k, v in kw.items():
        if v is None: _CONTEXTO_BITACORA.pop(k, None)
        else: _CONTEXTO_BITACORA[k] = v


def _contexto_argv(argv=None):
    """script = nombre del archivo; operacion = primer argumento posicional (subcomando); por = valor de --por."""
    argv = list(sys.argv if argv is None else argv)
    script = os.path.basename(argv[0]) if argv else ""
    op = por = ""; i = 1
    while i < len(argv):
        x = argv[i]
        if x.startswith("--"):
            k, igual, v = x.partition("=")
            if not igual and k in ("--proyecto", "--ruta", "--por") and i + 1 < len(argv): v = argv[i + 1]; i += 1
            if k == "--por": por = v
        elif not op and not x.startswith("-"): op = x
        i += 1
    return {"script": script, "operacion": op, "por": por}


def _sha(b): return _hashlib.sha256(b).hexdigest()


def _leer_bytes(p):
    try:
        with open(p, "rb") as fh: return fh.read()
    except (FileNotFoundError, IsADirectoryError, NotADirectoryError): return None


def _gobernado(ruta):
    """(carpeta del proyecto, ruta relativa) si `ruta` es estado.json, un registro o una propuesta de un proyecto."""
    r = os.path.abspath(ruta); base = os.path.basename(r); d = os.path.dirname(r)
    if base == "estado.json": return d, base
    padre, abuelo = os.path.basename(d), os.path.dirname(d)
    if os.path.basename(abuelo) != "03-control": return None
    if not ((padre == "registros" and base.endswith(".csv") and base[:-4] in REGISTROS)
            or (padre == "propuestas" and re.fullmatch(r"P-\d+\.json", base))): return None
    raiz = os.path.dirname(abuelo)
    return (raiz, f"03-control/{padre}/{base}") if os.path.isfile(os.path.join(raiz, "estado.json")) else None


def _corto_b(v):
    v = " ".join(str(v or "").split())
    return v if len(v) <= TOPE_VALOR_BITACORA else v[:TOPE_VALOR_BITACORA - 1] + "…"


def _cambios_csv(reg, antes, despues):
    def filas(b):
        if not b: return [], {}
        rd = csv.DictReader(io.StringIO(b.decode("utf-8-sig", errors="replace"), newline=""))
        fs = list(rd)
        return list(rd.fieldnames or []), {(f.get("id") or f"#{i}"): f for i, f in enumerate(fs, 1)}
    ca, fa = filas(antes); cd, fd = filas(despues)
    oculto = lambda f: reg in BITACORA_SIN_VALORES or (f.get("confidencial") or "").strip().lower() == "si"
    out = {"registro": reg}; cambios = {}
    for k, f in fd.items():
        a = fa.get(k, {})
        dif = [c for c in cd if c != "id" and (f.get(c) or "") != (a.get(c) or "")]
        if dif: cambios[k] = dif if oculto(f) or oculto(a) else {c: [_corto_b(a.get(c)), _corto_b(f.get(c))] for c in dif}
    altas = [k for k in fd if k not in fa]; bajas = [k for k in fa if k not in fd]
    out["ids"] = [k for k in fd if k in cambios or k in altas] + bajas
    if altas: out["altas"] = altas
    if bajas: out["bajas"] = bajas
    if cambios: out["cambios"] = cambios
    if antes is None: out["creado"] = True
    elif [c for c in cd if c not in ca]: out["columnas_nuevas"] = [c for c in cd if c not in ca]
    return out


def _claves_json(antes, despues):
    def carga(b):
        try: d = json.loads(b.decode("utf-8")) if b else {}
        except ValueError: d = {}
        return d if isinstance(d, dict) else {}
    a, d = carga(antes), carga(despues); claves = []
    for k in list(d) + [k for k in a if k not in d]:
        va, vd = a.get(k), d.get(k)
        if va == vd: continue
        if isinstance(va, dict) and isinstance(vd, dict):
            claves += [f"{k}.{s}" for s in list(vd) + [s for s in va if s not in vd] if va.get(s) != vd.get(s)]
        else: claves.append(k)
    return claves


def _ultima_linea(ruta):
    """Última línea de la bitácora (bytes, sin el salto) leyendo desde el final; None si no hay."""
    try:
        with open(ruta, "rb") as fh:
            fh.seek(0, 2); pos = fh.tell(); bloque = b""
            while pos > 0:
                paso = min(65536, pos); pos -= paso; fh.seek(pos); bloque = fh.read(paso) + bloque
                cuerpo = bloque.rstrip(b"\n")
                if b"\n" in cuerpo: return cuerpo.rsplit(b"\n", 1)[1]
            return bloque.rstrip(b"\n") or None
    except FileNotFoundError:
        return None


def anotar_bitacora(proyecto, rel, antes, despues):
    """Agrega la línea de una escritura ya hecha (bytes antes y después). No falla la escritura: si no puede anotar,
    avisa por stderr (el hueco lo detecta después la sanidad, BIT-02)."""
    if despues is None or antes == despues: return
    try:
        ctx = _contexto_argv(); ctx.update(_CONTEXTO_BITACORA)
        linea = {"n": 0, "fecha": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                 "script": ctx.get("script", ""), "operacion": ctx.get("operacion", ""), "archivo": rel}
        if rel.startswith("03-control/registros/"): linea.update(_cambios_csv(os.path.basename(rel)[:-4], antes, despues))
        elif rel == "estado.json": linea["claves"] = _claves_json(antes, despues)
        else:
            try: pr = json.loads(despues.decode("utf-8"))
            except ValueError: pr = {}
            linea.update({"propuesta_estado": pr.get("estado", ""), "registro": pr.get("registro", ""), "ids": [x for x in [pr.get("objetivo") or (pr.get("resolucion") or {}).get("id")] if x]})
        for k in ("por", "propuesta", "propuesto_por"):
            if ctx.get(k): linea[k] = ctx[k]
        linea["antes"] = _sha(antes) if antes is not None else ""
        linea["despues"] = _sha(despues)
        _anexar_linea(proyecto, linea)
    except Exception as x:
        print(f"AVISO: no se pudo anotar la escritura de {rel} en {ARCHIVO_BITACORA} ({x}); la sanidad lo mostrará como BIT-02. / "
              f"WARNING: could not append this write to the write log.", file=sys.stderr)


def _anexar_linea(proyecto, linea):
    """Numera, encadena (huella de la línea anterior) y agrega `linea` bajo el bloqueo del proyecto."""
    with bloqueo(proyecto):
        ruta = os.path.join(proyecto, ARCHIVO_BITACORA)
        ultima = _ultima_linea(ruta)
        try: linea["n"] = int(json.loads(ultima.decode("utf-8")).get("n")) + 1 if ultima else 1
        except (ValueError, TypeError, AttributeError):
            linea["n"] = (_leer_bytes(ruta) or b"").count(b"\n") + 1
        linea["previa"] = _sha(ultima) if ultima else ""
        with open(ruta, "ab") as fh:
            fh.write((json.dumps(linea, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8"))
            fh.flush(); os.fsync(fh.fileno())
    return linea["n"]


def reconocer_bitacora(proyecto, rel, por, motivo):
    """Anota que una persona revisó un cambio hecho fuera de los scripts en `rel` (merge de git, corrección manual):
    la línea `reconocer` lleva la huella anotada antes y la actual, y cierra los avisos BIT-02 anteriores de ese archivo.
    No restaura ni deshace nada. Devuelve el número de línea, o None si el archivo ya coincide con la bitácora."""
    lineas = [d for d in (_json_o_none(x) for x in leer_bitacora(proyecto)) if d and d.get("archivo") == rel]
    actual = _leer_bytes(os.path.join(proyecto, rel))
    previo = lineas[-1].get("despues", "") if lineas else ""
    hoy = _sha(actual) if actual is not None else ""
    if hoy == previo and not _pendientes_bitacora(proyecto, rel): return None
    linea = {"n": 0, "fecha": datetime.datetime.now().astimezone().isoformat(timespec="seconds"), "script": _contexto_argv()["script"],
             "operacion": "reconocer", "archivo": rel, "por": por, "motivo": motivo, "antes": previo, "despues": hoy}
    return _anexar_linea(proyecto, linea)


def _json_o_none(raw):
    try:
        d = json.loads(raw.decode("utf-8"))
        return d if isinstance(d, dict) else None
    except ValueError:
        return None


def _pendientes_bitacora(proyecto, rel):
    return [m for c, m in verificar_bitacora(proyecto)[1] if c == "BIT-02" and m.startswith(rel + " ")]


def leer_bitacora(proyecto):
    """Líneas crudas de la bitácora (bytes, sin el salto final), en orden."""
    crudo = _leer_bytes(os.path.join(proyecto, ARCHIVO_BITACORA)) or b""
    partes = crudo.split(b"\n")
    if partes and partes[-1] == b"": partes.pop()
    return partes


def verificar_bitacora(proyecto, idioma="es"):
    """Comprueba la cadena (BIT-01: línea ilegible, número fuera de orden o huella de la anterior distinta) y la
    continuidad de cada archivo (BIT-02: la escritura siguiente partió de otra versión, o el archivo actual no es el
    que dejó la última escritura anotada = cambio fuera de los scripts). Devuelve (lineas, [(codigo, mensaje)])."""
    T = lambda es, en: t(idioma, es, en)
    crudo = _leer_bytes(os.path.join(proyecto, ARCHIVO_BITACORA))
    if crudo is None: return [], []
    partes = leer_bitacora(proyecto); lineas, problemas = [], []; previa = None
    if crudo and not crudo.endswith(b"\n"):
        problemas.append(("BIT-01", T(f"{ARCHIVO_BITACORA}: la última línea está incompleta (escritura interrumpida o edición manual).",
                                      f"{ARCHIVO_BITACORA}: the last line is incomplete.")))
    for i, raw in enumerate(partes, 1):
        try:
            d = json.loads(raw.decode("utf-8"))
            if not isinstance(d, dict): raise ValueError
        except ValueError:
            problemas.append(("BIT-01", T(f"{ARCHIVO_BITACORA} línea {i}: ilegible.", f"{ARCHIVO_BITACORA} line {i}: unreadable.")))
            previa = raw; continue
        if d.get("previa", "") != (_sha(previa) if previa is not None else ""):
            problemas.append(("BIT-01", T(f"{ARCHIVO_BITACORA} línea {i}: la huella de la línea anterior no coincide (se editó, borró o insertó una línea antes).",
                                          f"{ARCHIVO_BITACORA} line {i}: the previous-line hash does not match (a line was edited, removed or inserted).")))
        if d.get("n") != i:
            problemas.append(("BIT-01", T(f"{ARCHIVO_BITACORA} línea {i}: número {d.get('n')} fuera de orden.", f"{ARCHIVO_BITACORA} line {i}: number {d.get('n')} out of sequence.")))
        lineas.append(d); previa = raw
    ultima = {}; huecos = {}                 # archivo → avisos de huecos aún no reconocidos
    for d in lineas:
        a = d.get("archivo") or ""
        if d.get("operacion") == "reconocer": huecos.pop(a, None)
        elif a in ultima and d.get("antes", "") != ultima[a][1]:
            huecos.setdefault(a, []).append(("BIT-02", T(f"{a} cambió fuera de los scripts entre las líneas {ultima[a][0]} y {d.get('n')} de la bitácora (la escritura {d.get('n')} partió de otra versión).",
                                                         f"{a} changed outside the scripts between write-log lines {ultima[a][0]} and {d.get('n')}.")))
        ultima[a] = (d.get("n"), d.get("despues", ""))
    for a in sorted(huecos): problemas += huecos[a]
    for a, (n, h) in sorted(ultima.items()):
        actual = _leer_bytes(os.path.join(proyecto, a))
        if actual is None:
            if h: problemas.append(("BIT-02", T(f"{a} ya no existe; la última escritura anotada es la línea {n} de la bitácora.", f"{a} no longer exists; last logged write is line {n}.")))
        elif _sha(actual) != h:
            problemas.append(("BIT-02", T(f"{a} se modificó fuera de los scripts después de la línea {n} de la bitácora (su huella actual no es la que dejó la última escritura anotada).",
                                          f"{a} was modified outside the scripts after write-log line {n} (its current hash is not the one the last logged write left).")))
    return lineas, problemas
