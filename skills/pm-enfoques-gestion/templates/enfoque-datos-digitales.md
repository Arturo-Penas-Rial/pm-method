---
tipo: enfoque-datos-digitales
proyecto: "{{proyecto}}"
version: 0.1
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Enfoque de gestión de datos y tecnología digital · Digital and data management approach — {{proyecto}}

> Qué tecnología se usa para gestionar el proyecto y para el trabajo especializado, cómo se gobiernan los datos del proyecto y cómo se usa la IA de forma responsable. Lo prepara el gestor con soporte del proyecto; lo aprueba el ejecutivo. / Technology, data governance and responsible AI use for the project.

**Versión mínima / Minimal version:** {{version_minima}}
*`sí`: lista de herramientas, dónde vive la fuente de verdad, quién tiene acceso, y las reglas de uso de IA (sección 6).*

## 1. Tecnología para gestionar el proyecto / Project management technology

| Uso / Use | Herramienta / Tool | Dueño / Owner | Fuente de verdad / Source of truth |
|---|---|---|---|
| Registros y estado | {{herr_registros}} | {{dueno_registros}} | Carpeta del proyecto (`estado.json`, `03-control/registros/`) |
| Cronograma | {{herr_cronograma}} | {{dueno_cronograma}} | {{fuente_cronograma}} |
| Tracker de trabajo | {{herr_tracker}} | {{dueno_tracker}} | {{fuente_tracker}} |
| Documentos | {{herr_documentos}} | {{dueno_documentos}} | {{fuente_documentos}} |
| Comunicación | {{herr_comunicacion}} | {{dueno_comunicacion}} | {{fuente_comunicacion}} |
| Agentes de IA | Claude Code / Hermes con pm-method | {{dueno_ia}} | Carpeta del proyecto |

*Cuando dos herramientas contienen el mismo dato, declarar cuál manda y cómo se sincronizan.*

### 1.1 Integraciones conectadas (capacidades MCP) / Connected integrations (MCP capabilities)
*El paquete no trae conectores predefinidos. Listar solo los MCP que el usuario conectó en la sesión (`pm-integraciones` los detecta y `estado.py integracion ...` los registra en `estado.json.integraciones`). Describir capacidades, no productos obligatorios. Si no hay ninguno: "ninguna; alternativa interna (CSV, Mermaid, scripts)".*

| Capacidad / Capability | Sistema conectado / Connected system | Lectura / Read | Escritura (con confirmación) / Write (confirmed) | Instantánea en / Snapshot at | Dueño / Owner |
|---|---|---|---|---|---|
| {{cap1}} | {{cap1_sistema}} | {{cap1_lectura}} | {{cap1_escritura}} | `03-control/fuentes/` | {{cap1_dueno}} |
| {{cap2}} | {{cap2_sistema}} | {{cap2_lectura}} | {{cap2_escritura}} | `03-control/fuentes/` | {{cap2_dueno}} |

*Capacidades típicas: leer/crear issues del tracker, leer/escribir páginas de documentación, publicar mensajes en chat, leer transcripciones, leer eventos de calendario, leer OKR. Reglas: lectura libre; escritura externa solo con vista previa y confirmación explícita; los datos externos entran como instantáneas fechadas y nunca reemplazan a los registros de gobierno; quién puede conectar o desconectar un MCP (sección 5).*

## 2. Tecnología para el trabajo especializado / Specialist technology

{{tecnologia_especialista}}
*Herramientas que usan los equipos para producir los productos (diseño, desarrollo, ingeniería) y cómo se integran con el control del proyecto.*

## 3. Gestión de datos / Data management

| Pregunta / Question | Respuesta / Answer |
|---|---|
| ¿Qué datos produce y consume el proyecto? / Data in and out | {{datos_alcance}} |
| ¿Quién es el custodio de cada conjunto? / Custodian | {{custodio}} |
| ¿Clasificación (pública, interna, confidencial, personal)? / Classification | {{clasificacion}} |
| ¿Requisitos de privacidad y normativa aplicable? / Privacy and regulation | {{privacidad}} |
| ¿Quién accede y con qué permisos? / Access | {{acceso}} |
| ¿Cómo se asegura la calidad del dato? / Data quality | {{calidad_dato}} |
| ¿Copias de seguridad y retención? / Backup and retention | {{retencion}} |
| ¿Qué se hace con los datos al cierre? / Disposal at closure | {{cierre_datos}} |

*Si hay datos personales, consultar con el área legal antes de aprobar el enfoque.*

## 4. Tableros y audiencias / Dashboards and audiences

{{tableros}}
*Qué tableros existen (avance, riesgos, acciones por actor), para quién, con qué frecuencia se actualizan y desde qué fuente. Ver `pm-visuales`.*

## 5. Seguridad / Security

{{seguridad}}
*Autenticación, gestión de secretos y tokens de integraciones, quién puede conectar herramientas externas.*

## 6. Uso responsable de IA / Responsible AI use

| Regla / Rule | Aplicación en el proyecto / Project application |
|---|---|
| Todo contenido generado por IA se marca como borrador hasta revisión humana | {{ia_borrador}} |
| Ninguna aprobación ni decisión de gobernanza la toma un agente | {{ia_decisiones}} |
| Las cifras generadas citan su fuente; lo no confirmado se marca `[por confirmar]` | {{ia_fuentes}} |
| No se envían datos confidenciales o personales a servicios no autorizados | {{ia_datos}} |
| Escrituras externas (tracker, correo, chat) solo con confirmación explícita | {{ia_escrituras}} |
| Análisis de reuniones solo agregado y con consentimiento; sin perfilado individual | {{ia_reuniones}} |
| Revisión periódica de sesgos y errores en salidas recurrentes | {{ia_revision}} |

*Estas reglas son las mismas que aplican los agentes de pm-method; adaptarlas a la política de IA de la organización.*

## 7. Roles / Roles

{{roles}}
*Quién administra herramientas, quién otorga accesos, quién revisa el cumplimiento de este enfoque.*

## Lista de verificación / Checklist
- [ ] Fuente de verdad declarada para cada tipo de dato.
- [ ] Integraciones conectadas listadas como capacidades (o "ninguna"), con regla de escritura confirmada e instantáneas fechadas.
- [ ] Clasificación y custodio por conjunto de datos.
- [ ] Privacidad y normativa revisadas cuando hay datos personales.
- [ ] Reglas de IA adoptadas y comunicadas al equipo.
- [ ] Disposición de datos al cierre definida.
- [ ] Aprobado por el ejecutivo y registrado en `decisiones.csv`.
