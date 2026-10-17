---
name: pm-comunicacion-stakeholders
description: "Matriz de comunicaciones y mensajes por audiencia. Usar: plan de comunicación, communication matrix, comunicado, status email, sprint review. No: actas→pm-reuniones; análisis o compromiso de interesados→pm-organizacion-roles."
version: 2.0.0
author: pm-method
license: MIT
metadata:
  pm-method:
    fase: transversal
    agente: pm-director
    procesos_prince2: [IP, DP, CS, SB, CP]
    practicas_prince2: [organizing, progress]
    tecnicas_pmbok: [análisis de requisitos de comunicación, matriz de involucramiento actual/deseado, métodos interactivo/empuje/atracción, poder-interés]
    artefactos: [matriz-comunicaciones, comunicado-por-audiencia, correo-seguimiento, stakeholders.csv, diario.md]
    idiomas: [es, en]
---

# Comunicación y stakeholders · Stakeholder communication

## Cuándo usar / When to use
- Construir o revisar la **matriz de comunicaciones** (anexo operativo del enfoque de comunicación): audiencia × mensaje × canal × frecuencia × emisor.
- Comunicar una decisión, desvío, hito, cambio o cierre a una audiencia concreta (dirección, equipo, cliente, proveedores) con el detalle adecuado.
- Seguir el **plan de compromiso de stakeholders**: brechas actual/deseado y ajustes de mensajes y canales.
- En ágil o híbrido, planificar la **revisión de iteración (sprint review) o demo** como evento de comunicación (su acta, vía `pm-reuniones`).
- EN: build the communications matrix; draft audience-specific updates (executive, team, customer, supplier).
- EN: follow up the stakeholder engagement plan; plan the sprint review as a communication event.

## Idioma
Responder en el idioma del usuario; cada fila de la matriz fija el idioma de su audiencia (p. ej. junta en español, proveedor en inglés). Términos EN la primera vez: communication management approach, communications matrix, stakeholder register, engagement plan.

## Conocimiento
- `references/guia.md` (esta skill): estereotipos §1, matriz §2, comunicado §3, plan de compromiso §4, sprint review §5, envíos §6, columnas §7, reglas y guardarraíles §8, traspaso a `pm-reuniones` §9.
- `pm-knowledge/references/prince2-principios-personas-procesos.md` §3.4, §5.2, §8.6 (comunicación bidireccional, la junta como canal).
- `pm-knowledge/references/prince2-practicas-riesgo-issues-progreso-productos.md` §4.c.3 (cadena de informes), §7.5 (highlight → versión ejecutiva), §7.3 (escalado verbal primero si es urgente).
- `pm-knowledge/references/pmbok8-dominios-procesos-adaptacion.md` §2.5 (interesados y comunicaciones).
- `pm-knowledge/references/pmbok8-artefactos-tecnicas-anexos.md` §3.5 (técnicas de comunicación), §4.2.2 y §5.3 (guardarraíles de IA).
- `pm-knowledge/references/plantillas-inicio-y-planes.md` §3.8 y §3.11 (plan de comunicaciones e involucramiento).

## Entradas requeridas
- `estado.json`: idioma, roles (incluido `product_owner`), `enfoque_entrega`, `agil.cadencia_iteracion_dias`, fase, etapa, `integraciones.chat`.
- Enfoque de comunicación `02-planificacion/enfoques/enfoque-comunicacion.md` (dueño `pm-enfoques-gestion`). Si no existe, matriz en borrador y pedir la versión mínima del enfoque.
- `03-control/registros/stakeholders.csv` (valores: `registro.py esquema stakeholders`; `confidencial=si` = circulación restringida) y `plan-compromiso-stakeholders` si existe. Si está vacío, `pm-organizacion-roles` o lista mínima (patrocinador, junta, equipo, cliente, proveedores).
- Para comunicar: la fila de `decisiones.csv`, el informe (highlight, excepción) o el acta confirmada de `pm-reuniones` en `03-control/reuniones/`.
- Opcional: chat o correo conectado (resuelto por `pm-integraciones`); sin él, texto listo para pegar.

## Procedimiento
### A. Matriz de comunicaciones
1. Leer `stakeholders.csv` y `estado.json.roles`; agrupar en estereotipos y definir el mensaje que importa a cada uno (`references/guia.md` §1).
2. Completar `templates/matriz-comunicaciones.md`: una fila por audiencia × mensaje con canal, frecuencia, emisor, idioma, retroalimentación, regla extraordinaria y autorización de información sensible; prioridad poder × interés; cobertura de todo el registro; coherencia con el enfoque (guía §2).
3. **PUERTA HUMANA.** Guardar en `02-planificacion/matriz-comunicaciones.md` (`en-revision`); el ejecutivo aprueba y se registra con `estado.py aprobar matriz-comunicaciones` (dentro del PID, `pm-director`). Luego actualizar `canal` y `frecuencia` en `stakeholders.csv` (guía §2).

### B. Comunicado por audiencia
4. Identificar el hecho y su fuente (id de registro, informe o acta de `pm-reuniones`).
5. Redactar con `templates/comunicado-por-audiencia.md`: ejecutivo (decisión primero, pedido con fecha límite), equipo (cambios, bloqueos, prioridades) y cliente (hitos, riesgos, qué se le pide); proveedores si la matriz lo exige (guía §3).
6. **PUERTA HUMANA.** Guardar en `03-control/reportes/AAAA-MM-DD-comunicado-<tema>.md` como borrador; lo confirma el gestor (el ejecutivo si va a la capa de negocio o al exterior).
7. **Enviar** solo vía `pm-integraciones`, con vista previa y confirmación explícita; anotar el envío en `diario.md` (guía §6). Correos de seguimiento de acciones con `templates/correo-seguimiento.md`, solo desde un acta confirmada de `pm-reuniones` o un comunicado aprobado.

### C. Seguimiento del plan de compromiso
8. Cada período (o en límite de etapa): comparar compromiso actual vs. deseado, revisar acciones de comunicación vencidas y señales de actas, y proponer ajustes de mensaje, canal o frecuencia en la matriz (guía §4). Interesados nuevos o reanálisis → `pm-organizacion-roles`.

### D. Revisión de iteración o demo (ágil e híbrido)
9. Agendarla en la matriz; preparar invitados y agenda (incremento terminado, burn-up, Must en riesgo); durante, solo lo terminado. El acta, acciones y decisiones los produce `pm-reuniones`; la aceptación demostrada va a `pm-calidad`; intercambios del PO a `pm-issues-cambios` (guía §5). Comunicado al patrocinador si cambió el pronóstico de Must.

### E. Reuniones y transcripciones
10. Pedidos de acta, minuta, transcripción, acciones de reunión o clima de equipo → **`pm-reuniones`** (plantilla `<pm-reuniones>/templates/acta-reunion.md`). Esta skill solo usa el acta confirmada como fuente (guía §9).
11. **Cerrar** con artefactos y estado, envíos pendientes de confirmación y siguiente paso; si corre como subagente, bloque de retorno (SPEC §1.11).

## Reglas del método
1. [PRINCE2] Etapas por defecto; en ágil o híbrido la revisión de iteración es un evento de la matriz dentro de la etapa, sin eliminar puertas.
2. [PRINCE2] Un desvío fuera de tolerancia no se suaviza con un comunicado: se escala por excepción vía `pm-issues-cambios` y `pm-director`.
3. [PRINCE2] Nada aprobado sin acto humano registrado; un comunicado o un acta no convierten un comentario en aprobación.
4. [PRINCE2] Comunicación bidireccional: cada comunicado define cómo vuelve la retroalimentación; la matriz incluye canales de escucha.
5. [PRINCE2] La junta es el canal con la capa de negocio: las notificaciones de inicio, autorización y cierre las firma el ejecutivo.
6. [PRINCE2] Excepciones urgentes: verbal inmediato y luego el informe escrito; el comunicado no sustituye al informe de excepción.
7. [PRINCE2] La matriz se revisa en cada límite de etapa y cuando cambian los influenciadores.
8. [PMBOK→Organizing/IP] Técnicas: requisitos de comunicación, matriz actual/deseado, poder × interés, método interactivo/empuje/atracción; declarar supuestos.
9. [PMBOK→Progress/DP] El comunicado ejecutivo pide decisiones con fecha límite, en una pantalla.
10. [PMBOK→Organizing/CS] Privacidad: valoraciones de interesados solo en circulación restringida (`confidencial=si`); nunca en comunicados amplios.
11. [Plantillas] Dueños únicos (SPEC §1.10.11): el enfoque es de `pm-enfoques-gestion`, la matriz de esta skill; actas y transcripciones de `pm-reuniones`.
12. [Plantillas] Cada interesado en al menos una fila; cada fila con audiencia, información, canal, frecuencia y emisor; versión mínima para proyectos pequeños.
13. Transparencia de IA: borrador, `[por confirmar]`, cada cifra con su fuente. Idioma por audiencia.
14. Escrituras externas (correo, chat, tracker) solo vía `pm-integraciones` con vista previa y confirmación explícita.

## Artefactos y plantillas
| Artefacto | Plantilla | Ruta de salida | estado.json |
|---|---|---|---|
| Matriz de comunicaciones | `templates/matriz-comunicaciones.md` | `02-planificacion/matriz-comunicaciones.md` | `matriz-comunicaciones` |
| Comunicado por audiencia | `templates/comunicado-por-audiencia.md` | `03-control/reportes/AAAA-MM-DD-comunicado-<tema>.md` | — |
| Correo de seguimiento | `templates/correo-seguimiento.md` | `03-control/reportes/AAAA-MM-DD-correo-<tema>.md` | — |
| Canal y frecuencia por interesado | `registro.py actualizar stakeholders` | `03-control/registros/stakeholders.csv` | — |
| Envíos realizados | fila en el diario | `03-control/registros/diario.md` | — |
| Acta (también de sprint review) | `<pm-reuniones>/templates/acta-reunion.md` vía `pm-reuniones` | `03-control/reuniones/` | — |

Columnas de `stakeholders.csv` y `acciones.csv` con su traducción: `references/guia.md` §7.

## Calidad
- [ ] Matriz: todo el registro cubierto; cinco columnas por fila; regla extraordinaria; autorización de información sensible; coherente con el enfoque.
- [ ] En ágil/híbrido, sprint review como evento recurrente.
- [ ] Comunicado ejecutivo: decisión o desvío primero, pedido con fecha, una pantalla.
- [ ] Equipo: bloqueos y prioridades; cliente: hitos, riesgos, pedido; sin costos internos no autorizados.
- [ ] Filas `confidencial=si` fuera de comunicados amplios; idioma por audiencia.
- [ ] Nada enviado sin confirmación; envíos en `diario.md`.
- [ ] Ninguna acta producida aquí: derivada a `pm-reuniones`.

## Escalamiento y excepciones
- Pronóstico fuera de tolerancia conocido al redactar → issue en `pm-issues-cambios` y aviso a `pm-control`/`pm-director`; no redactar un mensaje tranquilizador.
- Comunicación externa con información sensible sin autorización definida en la matriz → ejecutivo.
- Pedido de evaluar a una persona a partir de reuniones → rechazar; el análisis agregado con consentimiento es de `pm-reuniones`.
- Interesados nuevos o cambio de influenciadores → `pm-organizacion-roles`.
- Como subagente (pm-director u otro): aprobación de la matriz y confirmación de envíos se devuelven como "decisiones humanas requeridas" en el bloque de retorno (SPEC §1.11).

## Ejemplos de invocación
- "Armá la matriz de comunicaciones del proyecto Faro con la junta, el equipo, el cliente y los dos proveedores."
- "Comunicá a la dirección, al equipo y al cliente que la etapa 2 se aprobó con condiciones."
- EN: "Draft the weekly update for the sponsor: decisions needed first, then risks; post it to Teams after I review it."
- EN: "Plan the sprint 5 review with the product owner and key users."
- No activa: "Acá está la transcripción del comité de hoy; sacame el acta y las acciones" → `pm-reuniones`.

## EN summary
Owns the operational communications matrix (annex of the communication approach owned by pm-enfoques-gestion), audience-specific updates (executive, team, customer, supplier) with the decision first, and the follow-up of the stakeholder engagement plan.
In agile/hybrid the sprint review is a communication event; its minutes, actions and decisions come from pm-reuniones, which also owns transcripts and team-climate analysis.
Outbound messages go only through pm-integraciones after preview and explicit confirmation, and are logged in diario.md.
