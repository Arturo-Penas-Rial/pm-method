---
tipo: descripcion-rol
proyecto: "{{proyecto}}"
version: 0.1
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Descripción de rol · Role description — {{rol}} — {{proyecto}}

> Qué puede aprobar, de qué responde y ante quién rinde cuentas una persona en este proyecto. Es un rol del proyecto, no el cargo que la persona tiene fuera de él. Las prepara el gestor; las confirma el ejecutivo. / Authority, responsibilities and reporting line of a project role; confirmed by the executive.

## 1. Identificación / Identification

**Rol / Role:** {{rol}} ({{rol_en}})
*Nombre del rol del método (ejecutivo, usuario sénior, proveedor sénior, gestor de proyecto, gestor de equipo, aseguramiento, soporte, autoridad de cambio) o rol añadido con su relación al método.*

**Persona / Person:** {{persona}} · **Organización y cargo / Organisation and position:** {{organizacion_cargo}}
*Nombre real solo si se proporcionó; aclarar la diferencia entre el título de puesto y el rol en el proyecto.*

**Dedicación / Allocation:** {{dedicacion}} · **Vigencia / Period:** {{vigencia}}
*Completa o parcial (horas o porcentaje); etapas en las que el rol existe.*

**Combinado con / Combined with:** {{combinado_con}}
*Otros roles que la misma persona asume y cómo se mantiene un único punto de rendición de cuentas. Combinaciones prohibidas: ejecutivo + gestor; aseguramiento + gestor/equipo/soporte; desaconsejada: usuario sénior + proveedor sénior.*

**Rinde cuentas ante / Accountable to:** {{rinde_cuentas_ante}}
*Capa de negocio (ejecutivo), junta (gestor), gestor (gestores de equipo), miembro de la junta correspondiente (aseguramiento).*

## 2. Propósito del rol en este proyecto / Purpose of the role in this project

{{proposito}}
*Qué interés representa (negocio, usuario, proveedor) o qué servicio presta; en dos o tres líneas.*

## 3. Autoridad / Authority

| Puede aprobar o decidir / Can approve or decide | Límite / Limit | Escala a / Escalates to |
|---|---|---|
| {{aut_1}} | {{aut_1_limite}} | {{aut_1_escala}} |
| {{aut_2}} | {{aut_2_limite}} | {{aut_2_escala}} |
| {{aut_3}} | {{aut_3_limite}} | {{aut_3_escala}} |

*Cifras o criterios (monto, porcentaje de tolerancia, tipo de decisión). Coherente con `estado.json.tolerancias`, con los controles del PID y con el enfoque de issues y cambio.*

## 4. Responsabilidades / Responsibilities

**Del método / Method responsibilities:** {{responsabilidades_metodo}}
*Las responsabilidades base del rol según el método (por ejemplo, el usuario sénior especifica beneficios y los confirma tras el cierre; el proveedor sénior responde por la integridad técnica).*

**Específicas de este proyecto / Project-specific responsibilities:** {{responsabilidades_proyecto}}
*Lo que este proyecto añade: productos concretos que acepta, contratos que supervisa, comunidades que representa.*

**Sostenibilidad, seguridad y bienestar / Sustainability, safety and wellbeing:** {{responsabilidades_sostenibilidad}}
*Qué le toca a este rol en metas de sostenibilidad, seguridad y bienestar del equipo, incluida la gestión posterior al cierre si aplica.*

**Aseguramiento o comunicación asociados / Associated assurance or communication:** {{aseguramiento_comunicacion}}
*Qué aseguramiento le corresponde (si es miembro de la junta) y con quién se comunica según el enfoque de comunicación.*

## 5. Competencias y disponibilidad / Competencies and availability

**Competencias requeridas / Required competencies:** {{competencias}}
*Experiencia, conocimiento del dominio, credibilidad en el ecosistema, habilidades de liderazgo o técnicas.*

**Brecha y cómo se cubre / Gap and how it is covered:** {{brecha}}
*Si la persona no cubre alguna competencia o no tiene disponibilidad: formación, apoyo, delegación parcial; registrar riesgo si afecta tolerancias.*

## 6. Relaciones clave / Key relationships

{{relaciones}}
*Con quién trabaja más: otros roles de la junta, gerentes funcionales, proveedor, PMO, comunidad de usuarios.*

## 7. Revisión / Review

**Se revisa en / Reviewed at:** {{revision}}
*Cada fin de etapa, cambio de tolerancia o cambio de persona.*

**Aceptación de la persona / Acceptance by the person:** {{aceptacion}}
*Evidencia de que la persona conoce y acepta el rol (correo, acta); sin aceptación, el rol sigue `[por confirmar]`.*

## Lista de verificación / Checklist
- [ ] Rol del método identificado (o rol añadido con relación explícita).
- [ ] Autoridades con límite numérico o criterio y ruta de escalado.
- [ ] Responsabilidades del método y específicas sin solapamientos ni vacíos respecto a otros roles.
- [ ] Sostenibilidad, seguridad y bienestar incluidos.
- [ ] Combinaciones de roles declaradas y permitidas; punto único de rendición de cuentas explicado.
- [ ] Rinde cuentas ante el nivel correcto.
- [ ] Competencias y brechas evaluadas; riesgo registrado si corresponde.
- [ ] Aceptación de la persona y confirmación del ejecutivo previstas; estado `borrador` hasta entonces.
