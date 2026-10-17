---
tipo: flujo-productos
proyecto: "{{proyecto}}"
version: "{{version}}"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
---

# Diagrama de flujo de productos · Product flow diagram

> Borrador generado con asistencia de IA. / AI-assisted draft.

**Nivel de plan / Plan level:** {{nivel_plan}}
*Proyecto o etapa N; usa los mismos códigos P-x.y que la PBS.*

## 1. Diagrama / Diagram
```mermaid
flowchart LR
    S((Inicio / Start)) --> P11["P-1.1 {{producto_1_1}}"]
    P11 --> P12["P-1.2 {{producto_1_2}}"]
    S --> P21["P-2.1 {{producto_2_1}}"]
    PX[("P-X externo {{producto_externo}}")] --> P12
    P12 --> P1["P-1 {{producto_1}}"]
    P21 --> P1
    P1 --> F((Fin / End: {{producto_proyecto}}))
    classDef etapa1 fill:#eef,stroke:#336;
    classDef etapa2 fill:#efe,stroke:#363;
    class P11,P21 etapa1;
    class P12,P1 etapa2;
```
*Un nodo Inicio y uno Fin; todos los productos de la PBS (finales, intermedios y externos); flecha = "necesario antes de"; clases de color por etapa de finalización. Si hay integración diagram-design o archify, pm-visuales puede producir la versión gráfica.*

## 2. Dependencias / Dependencies
| De / From | A / To | Tipo / Type | Control / Control | Paquete afectado / Affected work package | Riesgo asociado / Linked risk |
|---|---|---|---|---|---|
| {{origen}} | {{destino}} | interna · externa | total · parcial | W-{{codigo}} | R-{{id}} o "ninguno" |
*Una fila por flecha relevante; las externas (fuera del alcance o de otro proyecto) se documentan en la descripción del paquete y, cuando conviene, se registran como riesgo.*

## 3. Paralelismo y secuencia / Parallelism and sequence
{{paralelismo}}
*Qué productos pueden producirse a la vez y cuáles deben esperar; base para la secuenciación de actividades en pm-cronograma-estimacion.*

## 4. Productos por etapa / Products per stage
| Etapa / Stage | Productos que terminan / Products completed | Puerta / Gate |
|---|---|---|
| {{etapa}} | {{productos}} | autorizar-etapa |
*Permite a la junta ver cuándo empiezan a producirse resultados y cuándo medir beneficios.*

## 5. Fuentes y pendientes / Sources and open points
{{fuentes_pendientes}}
*Expertos de entrega y aceptación consultados; dependencias por confirmar.*

## Lista de verificación / Checklist
- [ ] Inicio y Fin presentes; sin productos sueltos.
- [ ] Todos los productos de la PBS aparecen una vez.
- [ ] Dependencias clasificadas (interna/externa) y copiadas al paquete de trabajo afectado.
- [ ] Dependencias externas evaluadas como riesgo.
- [ ] Nivel de detalle proporcional al costo y duración del plan.
- [ ] Coherente con las etapas definidas en el plan de proyecto.
