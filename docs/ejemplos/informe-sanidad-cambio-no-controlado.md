---
tipo: informe-sanidad
fecha: 2026-10-17
estado: borrador
---

# Sanidad del proyecto · Health check — Portal de autoservicio para socios

2 ERROR · 3 AVISO · 1 INFO

| Severidad | Código | Hallazgo | Cómo corregir |
|---|---|---|---|
| ERROR | ESP-03 | Requisitos sin cobertura (ni historia ni paquete de la WBS): FR-5. | Planificarlos (pm-planificacion-por-productos / pm-agil-hibrido) o retirarlos mediante control de cambios. |
| ERROR | ESP-10 | Cambio no controlado: bmad-prd difiere de la línea base v1.0 (ids FR-5) y ningún issue/cambio abierto lo cita. | pm-issues-cambios: registrar solicitud-cambio (o declarar elaboración progresiva y fijar nueva línea base). |
| AVISO | ESP-07 | Versión de BMAD version-no-visible (probadas: v4 · v6.11–v6.12). | Correr scripts/probar_paquete.py del paquete y revisar el inventario. |
| AVISO | ESP-14 | requisitos-bmad.csv no coincide con el PRD vigente (desactualizado o editado). | bmad.py requisitos (es derivado: no se edita). |
| AVISO | INS-05 | Las descripciones de las 50 skills visibles suman ≈13787 caracteres; el listado de Claude Code usa ≈1 % del contexto y puede recortarlas. | En settings.json: "skillListingBudgetFraction": 0.02, o marcar skills poco usadas como "name-only" en skillOverrides (no aplica a skills de plugins). |
| INFO | ESP-02 | El índice de especificación está desactualizado (se reconstruye solo al consultarlo). | especificacion.py indice o sanidad.py --reparar. |
