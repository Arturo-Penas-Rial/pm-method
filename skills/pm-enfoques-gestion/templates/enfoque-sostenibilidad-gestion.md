---
tipo: enfoque-sostenibilidad-gestion
proyecto: "{{proyecto}}"
version: 0.1
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Enfoque de sostenibilidad: controles de gestión · Sustainability management controls — {{proyecto}}

> Controles, revisiones y responsables que aseguran que el proyecto cumple las metas de sostenibilidad fijadas en el caso de negocio (`00-direccion/enfoque-sostenibilidad.md`). Si ese documento ya cubre los controles, este se reduce a una referencia. Lo prepara el gestor; lo aprueba el ejecutivo. / Operational controls for sustainability targets.

**Versión mínima / Minimal version:** {{version_minima}}
*`sí`: tabla de metas con indicador, umbral y responsable, revisada en cada fin de etapa.*

## 1. Referencia a metas / Reference to targets

{{referencia_metas}}
*Enlace a las metas ambientales, sociales y económicas aprobadas en el caso de negocio; no redefinirlas aquí.*

## 2. Indicadores y tolerancias / Indicators and tolerances

| Meta / Target | Indicador / Indicator | Línea base / Baseline | Objetivo / Goal | Tolerancia / Tolerance | Fuente del dato / Data source | Responsable / Owner |
|---|---|---|---|---|---|---|
| {{meta1}} | {{ind1}} | {{base1}} | {{obj1}} | {{tol1}} | {{fuente1}} | {{resp1}} |
| {{meta2}} | {{ind2}} | {{base2}} | {{obj2}} | {{tol2}} | {{fuente2}} | {{resp2}} |

*La tolerancia de sostenibilidad se suma a las seis tolerancias clásicas y se registra con `estado.py tolerancia --nivel proyecto sostenibilidad=...` (y por etapa, si la junta la fija al autorizar la etapa).*

## 3. Controles en el ciclo de vida / Lifecycle controls

| Momento / When | Control / Control | Quién / Who |
|---|---|---|
| Descripciones de producto | Criterios de calidad incluyen requisitos de sostenibilidad | {{ctrl_producto}} |
| Adquisiciones | Criterios de selección ponderan sostenibilidad | {{ctrl_adquisiciones}} |
| Highlight report | Indicadores informados contra tolerancia | {{ctrl_highlight}} |
| Fin de etapa | Revisión de cumplimiento y previsión | {{ctrl_fin_etapa}} |
| Cierre | Evaluación final y traspaso de metas a operaciones | {{ctrl_cierre}} |

## 4. Gestión de desvíos / Deviation handling

{{desvios}}
*Un desvío previsto fuera de tolerancia de sostenibilidad se trata como cualquier excepción: informe de excepción a la junta.*

## Lista de verificación / Checklist
- [ ] Cada meta tiene indicador, fuente de dato y responsable.
- [ ] Tolerancia de sostenibilidad registrada en `estado.json`.
- [ ] Controles integrados en descripciones de producto, adquisiciones e informes.
- [ ] Aprobado por el ejecutivo.
