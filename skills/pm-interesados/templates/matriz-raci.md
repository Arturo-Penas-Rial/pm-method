---
tipo: matriz-raci
proyecto: "{{proyecto}}"
version: 0.1
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Matriz de asignación de responsabilidades (RACI) · Responsibility assignment matrix — {{proyecto}}

> Intersección entre productos, paquetes de trabajo, decisiones o actividades y los roles del proyecto, con el tipo de participación de cada uno. Técnica de apoyo (su uso o sustitución no es adaptación del método). / Who does what for each product, work package, decision or activity.

**Fuente de datos / Data source:** `03-control/registros/raci.csv` (una fila por elemento × interesado: `elemento`, `tipo_elemento`, `stakeholder_id`, `rol`). La sección 2 se genera con `interesados.py raci --markdown` y la sección 3 la calcula el mismo script (un A por elemento, al menos un R, referencias existentes en el maestro y en la especificación, OKR o WBS). No editar la matriz a mano: corregir `raci.csv` con `registro.py`.
*Las columnas son interesados del maestro (`stakeholders.csv`): personas, roles o grupos registrados. Las filas pueden ser productos o paquetes de la WBS, requisitos, épicas o historias (vía la fachada de especificación), KR u objetivos de `okr.csv`, decisiones `D-###` o entregables.*

**Nivel de las filas / Row level:** {{nivel_filas}}
*`producto`, `paquete de trabajo`, `actividad del proceso` o `decisión`. Proporcional al tamaño: en versión mínima, por entregable con tres a seis columnas.*

**Alcance / Scope:** {{alcance}}
*Etapa de inicio, etapa N, proyecto completo, o interfaz con una organización externa.*

## 1. Leyenda / Key

| Código / Code | Significado / Meaning | Regla / Rule |
|---|---|---|
| R | Responsable: ejecuta / Responsible: does the work | Al menos uno por fila |
| A | Rinde cuentas: único dueño / Accountable: single owner | Exactamente uno por fila; no se comparte |
| C | Consultado: aporte requerido / Consulted: input required | Comunicación bidireccional |
| I | Informado / Informed | Comunicación unidireccional |
| S | Firma o acepta / Sign-off (opcional) | {{uso_s}} |

*La leyenda es obligatoria. Añadir códigos extendidos solo si se usan.*

## 2. Matriz / Matrix

| Fila / Row | {{rol_1}} | {{rol_2}} | {{rol_3}} | {{rol_4}} | {{rol_5}} | {{rol_6}} |
|---|---|---|---|---|---|---|
| {{fila_1}} | {{f1_r1}} | {{f1_r2}} | {{f1_r3}} | {{f1_r4}} | {{f1_r5}} | {{f1_r6}} |
| {{fila_2}} | {{f2_r1}} | {{f2_r2}} | {{f2_r3}} | {{f2_r4}} | {{f2_r5}} | {{f2_r6}} |
| {{fila_3}} | {{f3_r1}} | {{f3_r2}} | {{f3_r3}} | {{f3_r4}} | {{f3_r5}} | {{f3_r6}} |
| {{fila_4}} | {{f4_r1}} | {{f4_r2}} | {{f4_r3}} | {{f4_r4}} | {{f4_r5}} | {{f4_r6}} |

*Columnas: roles (no personas) del proyecto y, cuando ejecutan paquetes, proveedores externos. Filas: productos de la PBS, paquetes de trabajo, decisiones clave (aprobar plan de etapa, aceptar producto) o actividades del proceso. Referenciar el id de producto o paquete.*

## 3. Validación / Validation

| Verificación / Check | Resultado / Result | Filas o columnas afectadas / Rows or columns affected |
|---|---|---|
| Exactamente una A por fila | {{val_una_a}} | {{val_una_a_detalle}} |
| Al menos una R por fila | {{val_una_r}} | {{val_una_r_detalle}} |
| Ninguna columna vacía (rol fantasma) | {{val_col_vacia}} | {{val_col_vacia_detalle}} |
| Ninguna fila vacía (producto huérfano) | {{val_fila_vacia}} | {{val_fila_vacia_detalle}} |
| Concentración: ningún rol con A en más del 40 % de las filas | {{val_concentracion}} | {{val_concentracion_detalle}} |
| Sobre-consulta: ninguna fila con más de tres C | {{val_sobreconsulta}} | {{val_sobreconsulta_detalle}} |
| Coherencia con descripciones de rol y tolerancias | {{val_coherencia}} | {{val_coherencia_detalle}} |

*Umbrales del 40 % y de tres C son valores de referencia configurables. Toda alerta se resuelve o se acepta explícitamente.*

## 4. Decisiones sobre interfaces / Interface decisions

{{interfaces}}
*Cuando una fila cruza organizaciones (cliente–proveedor, programa–proyecto): quién acepta técnicamente, quién firma comercialmente, y que no sean la misma persona salvo decisión explícita.*

## 5. Revisión / Review

**Validado con / Validated with:** {{validado_con}}
*Gerentes funcionales que ceden recursos, gestores de equipo, proveedor. La RACI se valida con los involucrados, no se impone.*

**Se actualiza cuando / Updated when:** {{actualizacion}}
*Nuevos paquetes, reasignaciones, cambio de proveedor; es uno de los artefactos más estables.*

## Lista de verificación / Checklist
- [ ] Leyenda presente y solo con códigos usados.
- [ ] Nivel de filas proporcional al proyecto y declarado.
- [ ] Exactamente una A y al menos una R por fila.
- [ ] Sin columnas ni filas vacías.
- [ ] Alertas de concentración y sobre-consulta revisadas.
- [ ] Proveedores como columnas cuando ejecutan paquetes.
- [ ] Coherente con descripciones de rol, tolerancias y plan de recursos.
- [ ] Validada con los involucrados; estado `borrador` hasta entonces.
