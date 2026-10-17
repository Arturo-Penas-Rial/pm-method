---
tipo: "{{tipo}}"  # aceptacion-<producto> (producto intermedio o de etapa) | registro-aceptacion (solo el producto del proyecto)
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Registro de aceptación de producto · Product acceptance record — {{producto}}

> Borrador generado con apoyo de IA; la aceptación solo es válida con el acto explícito de la autoridad nombrada en la sección 5. / AI-assisted draft; acceptance is valid only with the explicit act of the authority named in section 5.

## 1. Producto / Product

**Producto y versión / Product and version:** {{producto}} v{{version_producto}}
*Id y nombre del producto (o "producto del proyecto" si es la aceptación final). Producto intermedio → clave `aceptacion-<producto>` y ruta `03-control/reportes/AAAA-MM-DD-aceptacion-<producto>.md`; producto del proyecto → clave `registro-aceptacion` y ruta `04-cierre/registro-aceptacion.md`.*

**Descripción de producto / Product description:** {{ruta_descripcion}}
*Ruta de la descripción aprobada con los criterios de aceptación y la autoridad de aceptación.*

**Paquete de trabajo / Work package:** {{id_paquete}}
*WP-nnn de origen; vacío si es la aceptación del producto del proyecto.*

**Productor / Producer:** {{productor}}
*Equipo o proveedor que lo desarrolló.*

**Tipo de aceptación / Acceptance type:** {{tipo_aceptacion}}
*de proyecto (junta o delegado en nombre del usuario) · contractual (proveedor → cliente según contrato) · de operación (quien lo mantendrá). En contexto comercial, la contractual precede a la de proyecto.*

## 2. Evidencia 1: información de control / Evidence 1: project control information

| Actividad (Q-nnn) / Activity | Método / Method | Fecha real / Actual date | Resultado / Result | Acciones cerradas / Actions closed | Evidencia / Evidence |
|---|---|---|---|---|---|
| {{q_1}} | {{metodo_1}} | {{fecha_real_1}} | {{resultado_1}} | {{acciones_1}} | {{evidencia_1}} |

*Todas las actividades de calidad del producto en calidad.csv; todas con resultado aprobado y acciones cerradas. Si alguna falta, el producto no está listo para aceptación.*

## 3. Evidencia 2: revisión independiente contra expectativas y criterios / Evidence 2: independent review against expectations and criteria

| Criterio de aceptación / Acceptance criterion | Prioridad / Priority | Cumple / Met | Cómo se verificó / How verified | Verificado por / Verified by |
|---|---|---|---|---|
| {{criterio_1}} | {{prioridad_1}} | {{cumple_1}} | {{verificacion_1}} | {{verificador_1}} |

*Criterios copiados de la descripción de producto (o del producto del proyecto); verificación hecha por alguien independiente del productor, idealmente del lado del usuario.*

## 4. Desviaciones y concesiones / Deviations and concessions

**Criterios no cumplidos / Criteria not met:** {{criterios_no_cumplidos}}
*Lista; cada uno debe tener un off-specification (I-nnn).*

**Concesiones aprobadas / Approved concessions:** {{concesiones}}
*Id de la decisión (D-nnn) de la junta o autoridad de cambio que aceptó el producto incompleto, con alcance de la concesión.*

**Condiciones de aceptación / Acceptance conditions:** {{condiciones}}
*Acciones pendientes que la autoridad exige, con responsable y fecha; se trasladan a recomendaciones de seguimiento si quedan abiertas al cierre.*

## 5. Acto de aceptación / Acceptance act

| Campo / Field | Valor / Value |
|---|---|
| Autoridad de aceptación (según descripción) / Acceptance authority (per description) | {{autoridad}} |
| Nombre de quien acepta / Name of acceptor | {{acepta_nombre}} |
| Rol / Role | {{acepta_rol}} |
| Decisión / Decision | {{decision}} |
| Fecha / Date | {{fecha_aceptacion}} |
| Registro en decisiones.csv / Decision log entry | {{id_decision}} |
| Medio / Means | {{medio}} |

*Decisión: aceptado · aceptado con condiciones · rechazado. Medio: firma, correo, acta de reunión, confirmación en herramienta. Sin esta sección completa, el estado del producto sigue siendo "aprobado", no "aceptado".*

## 6. Transferencia / Handover

**Propietario tras la aceptación / Owner after acceptance:** {{propietario}}
*Área o persona que opera y mantiene el producto desde ahora.*

**Elementos entregados / Items handed over:** {{elementos_entregados}}
*Producto, documentación, accesos, manuales, datos, garantías.*

**Actualización del registro de productos / Product register update:** {{actualizacion_registro_productos}}
*Fecha y versión registradas en el product status account.*

## Lista de verificación / Checklist
- [ ] Todas las actividades de calidad del producto con resultado aprobado y acciones cerradas.
- [ ] Revisión independiente contra cada criterio de aceptación, por alguien distinto del productor.
- [ ] Criterios no cumplidos con off-specification y, si se acepta igual, concesión registrada.
- [ ] Autoridad de aceptación coincide con la descripción de producto o con la delegación documentada.
- [ ] Nombre, rol, decisión, fecha y fila D-nnn completos.
- [ ] En contexto comercial: aceptación contractual registrada antes que la de proyecto.
- [ ] Propietario posterior y elementos entregados identificados.
- [ ] Contenido generado marcado como borrador; datos sin fuente como `[por confirmar]`.
