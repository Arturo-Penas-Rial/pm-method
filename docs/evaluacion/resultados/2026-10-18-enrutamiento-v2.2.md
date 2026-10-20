# Pruebas en vivo de enrutamiento · pm-method 2.2.0 · 2026-10-18

- **Qué se probó:** las 14 frases de `docs/evaluacion/frases-enrutamiento.tsv` que esperan alguna de las skills cuya
  descripción cambió en 2.2.0 (`pm-interesados` nueva, `pm-organizacion-roles`, `pm-comunicacion-stakeholders`,
  `pm-integraciones`, `pm-okr`) más la frase 66 (`pm-riesgos`, pedido nuevo de riesgos candidatos).
- **Cómo:** `scripts/pruebas_vivo/suite.py enrutamiento` con Claude Code 2.1.302 real (`claude -p … --plugin-dir <repo>`),
  modelo por defecto de la CLI, sobre un proyecto desechable creado desde el fixture BMAD 6.12.4. Se compara la primera
  skill elegida; la sesión se corta apenas elige (por eso no queda registrado el costo de cada corrida).
- **Corridas:** frase de humo (id 40) y luego las otras 13, el 18/10/2026.
- **Resultado: 14/14 OK.**

| id | Frase | Esperada | Elegida | Veredicto |
|---|---|---|---|---|
| 40 | Draft the stakeholder engagement plan | pm-interesados | pm-interesados | OK |
| 1 | Armemos el análisis de interesados con poder e interés | pm-interesados | pm-interesados | OK |
| 2 | Quiero un plan de comunicación para la junta y los usuarios | pm-comunicacion-stakeholders | pm-comunicacion-stakeholders | OK |
| 12 | Definamos los OKR del proyecto para el próximo semestre | pm-okr | pm-okr | OK |
| 16 | Traé los tickets abiertos de Jira del sprint actual | pm-integraciones | pm-integraciones | OK |
| 17 | Publicá el resumen semanal en el canal de Teams | pm-integraciones | pm-integraciones | OK |
| 46 | Score our key results for Q4 | pm-okr | pm-okr | OK |
| 51 | Mandale un correo a los stakeholders con el estado | pm-comunicacion-stakeholders | pm-comunicacion-stakeholders | OK |
| 61 | Armá la RACI de las épicas con un solo aprobador por elemento | pm-interesados | pm-interesados | OK |
| 62 | ¿Cómo prefiere Laura que le comuniquemos el avance? | pm-interesados | pm-interesados | OK |
| 63 | Proponé las preferencias de comunicación de cada participante a partir | pm-interesados | pm-interesados | OK |
| 64 | Send the approved status update to the steering committee by email | pm-comunicacion-stakeholders | pm-comunicacion-stakeholders | OK |
| 65 | Registrá el check-in del KR-1.1 de esta semana con confianza 7 | pm-okr | pm-okr | OK |
| 66 | Detectá riesgos candidatos en el brief de BMAD, las actas y los ticket | pm-riesgos | pm-riesgos | OK |

Observaciones:
- Las frases 1 y 40, que hasta 2.1 iban a `pm-organizacion-roles`, llegan ahora a `pm-interesados`: el traspaso de
  dueño del tema funciona en vivo.
- Frases en español e inglés enrutan igual (40, 46, 64).
- Pendiente: `suite.py todo` (guardarraíles e idioma) y los controles permanentes en una conversación real.
