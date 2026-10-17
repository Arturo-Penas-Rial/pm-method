# Guía del orquestador · Orchestrator guide

Detalle de `pm-orquestador`. El SKILL.md cita cada sección por número.

## 1. Modos de ejecución
| Entorno | Cómo se activa | Quién conversa | Cómo se delega |
|---|---|---|---|
| Claude Code (plugin) | `/pm-method:pm-orquestador` en la sesión, o arrancar con `claude --agent pm-method:pm-orquestador` (opcional: el orquestador queda como agente principal de toda la sesión) | el orquestador, en el hilo principal | subagentes `pm-method:pm-inicio`, `pm-method:pm-planificacion`, `pm-method:pm-control`, `pm-method:pm-cierre`, `pm-method:pm-director` |
| Claude Code (manual) | `/pm-orquestador` | ídem | subagentes `pm-inicio` … `pm-director` en `~/.claude/agents/` |
| Hermes | `/pm-orquestador` | el orquestador | no hay subagentes con nombre: se cargan las skills de fase en el mismo hilo y los agentes se usan como persona (SOUL.md) |
Los subagentes no pueden preguntar al usuario (no tienen `AskUserQuestion`) ni delegar (`disallowedTools: Agent`); heredan
las herramientas y los MCP de la sesión.

## 2. Plantilla de encargo a un subagente
```
Proyecto: <ruta de la carpeta> · idioma: <es|en> · fase/proceso/etapa: <…>
Objetivo: <qué producir o actualizar>
Skills a usar: <pm-…> (invocarlas por demanda)
Datos ya confirmados por el usuario: <campo: valor; …>
Restricciones: no registrar puertas ni aprobaciones (solo pm-director); no escribir en sistemas externos;
  dejar productos en `en-revision`; con BMAD, solo lectura vía pm-bmad-puente.
Terminar con el bloque "## Retorno al orquestador / Return" (Hecho · Decisiones humanas requeridas ·
  Datos faltantes · Siguiente paso sugerido).
```
Para pm-director tras una decisión humana, agregar: `Decisión: <aprobado|condicionado|rechazado|pendiente> · Condiciones: <…>
· Decidió: <nombre> (<rol>) · Fecha: <AAAA-MM-DD>` y, si hay BMAD, qué especificaciones fijar como línea base.

## 3. Cómo presentar decisiones humanas
- Una pregunta por decisión, con 2–4 opciones y la consecuencia de cada una en una línea (tomada del retorno).
- Indicar el rol que decide y pedir nombre y rol de quien responde; si responde alguien sin el rol, no se registra.
- "Pedir más información" es una opción válida: no hay aprobación; se vuelve a delegar con lo que falta.
- Escrituras externas: mostrar destino y contenido exactos (vista previa) y pedir confirmación por lote.

## 4. Secuencias tipo
- **Arranque**: pm-inicio (SU) → 🔒 `autorizar-inicio` → pm-inicio + pm-planificacion (IP, PID, `plan-etapa-2`) → 🔒 `autorizar-proyecto` + `autorizar-etapa`.
- **Fin de etapa**: `limite-etapa` → pm-control (informe de fin de etapa, lecciones) + pm-planificacion (plan siguiente) → 🔒 `autorizar-etapa`.
- **Excepción**: pm-control (informe X-###) → 🔒 `decision-ad-hoc` → `limite-etapa --excepcion` → pm-planificacion (plan de excepción) → 🔒 `autorizar-plan-excepcion`.
- **Cierre**: `cierre [--prematuro]` → pm-cierre → 🔒 `autorizar-cierre`.
- **Con BMAD**: en IP, pm-planificacion usa `pm-bmad-puente` (inventario, requisitos, trazabilidad); antes de cada puerta, `bmad.py verificar`; tras la decisión, pm-director fija la línea base.
- **Reunión de la junta**: pm-control con `pm-reuniones` (acta, acciones A-###) → decisiones de la junta presentadas al humano para confirmar → pm-director registra.
- En cada 🔒: retorno del subagente → el orquestador pregunta al humano → pm-director registra.

## 5. Perfil ágil mínimo
Misma secuencia de puertas con productos livianos: brief ligero + visión, business case de una página, estructura con PO
(`estado.py rol product_owner=`), enfoques de una página, backlog priorizado en vez de PBS/WBS completa, release plan por
etapas, DoD/DoR, presupuesto por iteración, highlight corto con burn-up (SPEC §1.10.12).
