"""Proyecto mínimo de prueba para pm-kb: versiones, exclusiones, relaciones, circulación y fuentes externas."""
import json
from pathlib import Path

PLAN_V1 = "---\ntipo: plan\nversion: 1.0\nestado: aprobado\n---\n# Plan de comunicaciones\n\n## Cadencia\n\nReunión mensual con la junta.\n"
PLAN_V2 = PLAN_V1.replace("version: 1.0\nestado: aprobado", "version: 2.0\nestado: en-revision").replace(
    "Reunión mensual con la junta.", "Reunión quincenal con la junta y boletín semanal.") + "\n## Canales\n\nCorreo y Teams.\n"
BC_V10 = "# Business case\n\n## Opciones\n\nOpción 2: portal propio con VAN 272.569.\n"
BC_V11 = BC_V10 + "\n## Revisión por R-001\n\nLa demora del padrón atrasa el beneficio B-02 un trimestre.\n"


def crear(raiz):
    r = Path(raiz)
    g = r / "gestion"
    for d in ("00-direccion/historial", "02-planificacion", "03-control/registros", "03-control/reuniones",
              "03-control/comunicaciones/2027-01-10-aviso", "docs"):
        (g / d).mkdir(parents=True, exist_ok=True)
    estado = {"proyecto": "Prueba KB", "fase": "entrega", "proceso_actual": "CS", "idioma": "es",
              "etapa_actual": {"numero": 2, "nombre": "Release 1", "inicio": "2026-11-27", "fin_previsto": "2027-03-05"},
              "artefactos": {
                  "business-case": {"ruta": "00-direccion/business-case.md", "version": "1.1", "estado": "aprobado",
                                    "aprobado_por": "Ejecutiva: Laura Méndez", "fecha": "2027-01-12"},
                  "plan-comunicaciones": {"ruta": "02-planificacion/plan-comunicaciones.md", "version": "2.0", "estado": "en-revision"}},
              "integraciones": {"chat": "slack"}}
    (g / "estado.json").write_text(json.dumps(estado, ensure_ascii=False, indent=1), encoding="utf-8")
    (g / "00-direccion/business-case.md").write_text(BC_V11, encoding="utf-8")
    (g / "00-direccion/historial/business-case-v1.0.md").write_text(BC_V10, encoding="utf-8")
    (g / "00-direccion/historial/business-case-v1.1.md").write_text(BC_V11, encoding="utf-8")
    (g / "02-planificacion/plan-comunicaciones.md").write_text(PLAN_V2, encoding="utf-8")
    (g / "00-direccion/historial/plan-comunicaciones-v1.0.md").write_text(PLAN_V1, encoding="utf-8")
    reg = g / "03-control/registros"
    (reg / "riesgos.csv").write_text(
        "id,evento,causa,respuesta,propietario,estado,notas\n"
        "R-001,Demora en la integración con el padrón,Entorno de pruebas sin datos,reducir,Diego Ferreira,abierto,ver D-002 y A-001\n"
        "R-002,Resistencia de los operadores a la bandeja única,Cambio de hábito,reducir,Ana Pereira,abierto,\n", encoding="utf-8")
    (reg / "decisiones.csv").write_text(
        "id,fecha,decision,decidido_por,nivel,artefactos_afectados,reemplaza\n"
        "D-001,2026-11-27,aprobado business-case v1.0,Ejecutiva: Laura Méndez,junta,00-direccion/business-case.md,\n"
        "D-002,2027-01-12,aprobado business-case v1.1,Ejecutiva: Laura Méndez,junta,00-direccion/business-case.md,D-001\n"
        "D-003,2026-11-30,aprobado plan-comunicaciones v1.0,Gestor: Martín Suárez,gestor,02-planificacion/plan-comunicaciones.md,\n", encoding="utf-8")
    (reg / "acciones.csv").write_text("id,descripcion,origen,responsable,estado\nA-001,Pedir datos de prueba al padrón,R-001,Lucía Benítez,abierta\n", encoding="utf-8")
    (reg / "stakeholders.csv").write_text(
        "id,nombre,rol_organizacion,poder,interes,actitud,confidencial,notas,correo,usuario_chat\n"
        "ST-001,Laura Méndez,Ejecutiva,alto,alto,lider,no,apoya el proyecto,laura@ejemplo.org,@laura\n"
        "ST-002,Sindicato de operadores,Representación,alto,alto,resistente,si,teme por la carga de trabajo,sindicato@ejemplo.org,\n", encoding="utf-8")
    (reg / "preferencias.csv").write_text("id,stakeholder_id,dimension,valor\nPF-001,ST-001,horario,llamadas antes de las 9\n", encoding="utf-8")
    (g / "03-control/comunicaciones/2027-01-10-aviso/mensaje-01.md").write_text("# Aviso a Laura\n\nHola Laura, te escribo por R-001.\n", encoding="utf-8")
    (g / "03-control/reuniones/ronda.vtt").write_text(
        "WEBVTT\n\n00:00:01.000 --> 00:00:05.000\nDiego: el padrón no nos da datos de prueba\n\n"
        "00:00:06.000 --> 00:00:09.000\nAna: los operadores no quieren la bandeja\n", encoding="utf-8")
    (g / "docs/salarios.md").write_text("---\ncirculacion: restringida\n---\n# Negociación\n\nSalarios del equipo del proveedor.\n", encoding="utf-8")
    (g / "docs/informe_v1.md").write_text("# Informe de calidad\n\nNueve defectos abiertos.\n", encoding="utf-8")
    (g / "docs/informe_v2.md").write_text("# Informe de calidad\n\nTres defectos abiertos tras la corrección.\n", encoding="utf-8")
    (g / "docs/2027-01-10-tablero.md").write_text("# Tablero\n\nAvance 40 %.\n", encoding="utf-8")
    (g / "docs/2027-02-10-tablero.md").write_text("# Tablero\n\nAvance 55 %.\n", encoding="utf-8")
    (g / "docs/borrador-privado.md").write_text("# Notas privadas\n\nNo indexar.\n", encoding="utf-8")
    (r / ".pmkbignore").write_text("# carpetas o archivos que no se indexan\ngestion/docs/borrador-privado.md\n", encoding="utf-8")
    (g / ".bitacora.jsonl").write_text(json.dumps({"n": 1, "fecha": "2027-01-12T10:00:00", "script": "registro.py", "operacion": "actualizar",
                                                   "registro": "riesgos", "ids": ["R-001"], "cambios": {"R-001": {"estado": ["identificado", "abierto"]}},
                                                   "por": "Gestor: Martín Suárez"}) + "\n", encoding="utf-8")
    return r
