---
tipo: descripcion-producto
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Descripción de producto · Product description

> Borrador generado con asistencia de IA. / AI-assisted draft.

**Identificador / Identifier:** {{codigo_pbs}}
*Código del producto en la PBS (P-x.y); único dentro del plan.*

**Nombre / Name:** {{nombre}}
*Sustantivo que describe el producto terminado, no la actividad que lo crea.*

**Versión de la descripción / Description version:** {{version}}
*Se incrementa con cada cambio aprobado; los cambios posteriores a la línea base pasan por control de cambios.*

**Etapa / Stage:** {{etapa}}
*Etapa de gestión en la que se produce o se acepta.*

## 1. Propósito / Purpose
{{proposito}}
*Para qué sirve el producto, cómo y quién lo usará.*

## 2. Composición / Composition
{{composicion}}
*Partes o componentes que lo integran; en productos documentales, las secciones; en software, módulos o funciones.*

## 3. Formato / Format
{{formato}}
*Apariencia o estándar al que debe ajustarse, si existe (plantilla, norma, formato de archivo).*

## 4. Derivado de / Derived from
{{derivado_de}}
*Productos o fuentes de los que parte: diseño, producto comercial, sistema a reemplazar, requisito del business case.*

## 5. Especificaciones de calidad / Quality specifications
| ID | Especificación / Specification | Tipo / Type | Medida / Measure | Tolerancia de calidad / Quality tolerance |
|---|---|---|---|---|
| EC-01 | {{especificacion}} | funcional · no funcional | {{medida}} | {{tolerancia}} |
*Cuantitativas con número verificable; cualitativas acotadas con contexto (perfil de usuario, condiciones); separar funcionales (qué hace) de no funcionales (seguridad, rendimiento, usabilidad, sostenibilidad); tolerancia = rango aceptable.*

## 6. Enfoque de desarrollo y habilidades / Development approach and skills
{{enfoque_desarrollo}}
*Cómo se espera producirlo (interno, proveedor, compra), habilidades, instalaciones o equipos especiales.*

## 7. Métodos de calidad / Quality methods
| Método / Method | Qué verifica / What it checks | Habilidades requeridas / Skills required | Momento / When |
|---|---|---|---|
| inspección · prueba · demostración · análisis · revisión de calidad | {{que_verifica}} | {{habilidades}} | {{momento}} |
*Cada especificación de la sección 5 debe quedar cubierta por al menos un método; los métodos se presupuestan y se registran en calidad.csv al aprobar esta descripción.*

## 8. Responsabilidades / Responsibilities
**Productor / Producer:** {{productor}}
*Persona o equipo que crea el producto.*

**Revisor / Reviewer:** {{revisor}}
*Independiente del productor; verifica contra las especificaciones.*

**Autoridad de aceptación / Acceptance authority:** {{aprobador}}
*Quien declara el producto aceptado (usuario sénior o su delegado según el enfoque de calidad).*

## 9. Dependencias / Dependencies
{{dependencias}}
*Productos internos o externos que deben existir antes; coherentes con el diagrama de flujo de productos.*

## 10. Versión ágil (si aplica) / Agile version (if applicable)
**Épica o historias asociadas / Epic or stories:** {{historias}}
*IDs del backlog (PB-###) que detallan este producto; sus criterios de aceptación refinan las especificaciones de la sección 5.*

## 11. Fuentes y pendientes / Sources and open points
{{fuentes_pendientes}}
*Documentos y personas consultadas; campos [por confirmar].*

## Lista de verificación / Checklist
- [ ] Especificaciones medibles o acotadas, funcionales y no funcionales.
- [ ] Necesidades de operación, mantenimiento y sostenibilidad consideradas.
- [ ] Cada especificación tiene método de verificación y tolerancia.
- [ ] Revisor independiente del productor; autoridad de aceptación nombrada.
- [ ] Trazable a la descripción del producto del proyecto y a la PBS.
- [ ] Registrada en el registro de productos con su versión.
- [ ] Aprobación del usuario sénior pendiente (se registra como puerta o decisión).
