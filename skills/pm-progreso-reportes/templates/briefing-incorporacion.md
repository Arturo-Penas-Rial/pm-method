---
tipo: briefing-incorporacion
proyecto: "{{proyecto}}"
fecha: "{{corte}}"
para: "{{para}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
fuentes: "estado.json; 03-control/registros/*.csv; 03-control/reportes/evm-*.json; puertas.py verificar; estado.py radar"
---

# Briefing de incorporación · Onboarding briefing — {{proyecto}}

*{{intro}}*

<!-- Lo llena `estado.py --proyecto <dir> briefing [--para ST-###] [--corte AAAA-MM-DD]`: cada sección sale de una fuente
     con su id o su archivo; el texto lo revisa el gestor antes de distribuirlo. A lo sumo dos páginas: las tablas se
     recortan con "… y N más" y el detalle queda en los registros citados. -->

## 1. Contexto · Context

{{contexto}}

## 2. Su rol y responsabilidades · Your role and responsibilities

{{rol}}

## 3. Decisiones clave · Key decisions

{{decisiones}}

## 4. Riesgos, issues y cambios · Risks, issues and changes

{{riesgos}}

## 5. Desempeño contra tolerancias · Performance against tolerances

{{desempeno}}

## 6. Artefactos aprobados · Approved artifacts

{{artefactos}}

## 7. Próxima puerta · Next gate

{{puerta}}

## 8. Próximos pasos · Next steps

{{pasos}}
