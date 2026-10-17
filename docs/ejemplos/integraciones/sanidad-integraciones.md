---
tipo: informe-sanidad
fecha: 2026-10-17
estado: borrador
---

# Sanidad del proyecto · Health check — Portal de autoservicio para socios

0 ERROR · 2 AVISO · 6 INFO

| Severidad | Código | Hallazgo | Cómo corregir |
|---|---|---|---|
| AVISO | ESP-13 | Traspaso a BMAD sin confirmar: 02-planificacion/especificacion/handoff-bmad-2026-10-17-prioridades.md. | Cuando el equipo BMAD lo aplique: marcar estado: aplicado en el documento, bmad.py verificar y nueva línea base. |
| AVISO | INS-05 | Las descripciones de las 68 skills visibles suman ≈19035 caracteres; el listado de Claude Code usa ≈1 % del contexto y puede recortarlas. | En settings.json: "skillListingBudgetFraction": 0.02, o marcar skills poco usadas como "name-only" en skillOverrides (no aplica a skills de plugins). |
| INFO | INS-03 | Skill externa 'archify' (archify) instalada: invocar como 'archify' · proyecto (<repo>/.claude/skills) · <repo>/.claude/skills/archify/SKILL.md |  |
| INFO | INS-03 | archify: no se encontró Chrome/Chromium; su verificación en navegador (browser-check) quedará omitida. | Instalar Chrome o definir ARCHIFY_CHROME=<ejecutable>. |
| INFO | INS-03 | Skill externa 'visual-explainer' (visual-explainer) instalada: invocar como 'visual-explainer' · proyecto (<repo>/.claude/skills) · <repo>/.claude/skills/visual-explainer/SKILL.md |  |
| INFO | INS-03 | Skill externa 'docx' (skills-office) instalada: invocar como 'anthropic-skills:docx' · claude.ai (skills sincronizadas) · ~/.claude/skills/synced/<id>/docx/SKILL.md |  |
| INFO | INS-03 | Skill externa 'xlsx' (skills-office) instalada: invocar como 'anthropic-skills:xlsx' · claude.ai (skills sincronizadas) · ~/.claude/skills/synced/<id>/xlsx/SKILL.md |  |
| INFO | INS-03 | Skill externa 'pptx' (skills-office) instalada: invocar como 'anthropic-skills:pptx' · claude.ai (skills sincronizadas) · ~/.claude/skills/synced/<id>/pptx/SKILL.md |  |
