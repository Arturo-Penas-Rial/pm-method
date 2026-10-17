---
tipo: comunicado-por-audiencia
proyecto: "{{proyecto}}"
version: "0.1"
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
aprobado_por: ""
idioma: "{{idioma}}"
tema: "{{tema}}"
fuente: "{{fuente}}"
---

# Comunicado por audiencia · Audience update

> **BORRADOR generado con asistencia de IA / AI-assisted DRAFT.** Tres versiones del mismo hecho para tres audiencias. Fuente: {{fuente}} (id de decisión, issue, cambio o ruta del informe). Nada se envía sin confirmación de {{confirma}}.

**Tema / Topic:** {{tema}} · **Fecha / Date:** {{fecha}}
*Hecho que se comunica: decisión de puerta, excepción, hito, cambio aprobado, cierre.*

**Hecho en una frase / The fact in one sentence:** {{hecho}}
*Idéntico en las tres secciones; lo que cambia es el detalle y el pedido.*

**Fuente / Source:** {{fuente}}
*Id en decisiones.csv, issues.csv, cambios.csv o ruta en 03-control/reportes/.*

---

## 1. Ejecutivo · Dirección y patrocinador / Executive · Sponsor and board

**Para / To:** {{aud_ejecutivo}} · **Canal / Channel:** {{canal_ejecutivo}} · **Idioma / Language:** {{idioma_ejecutivo}}
*Según la matriz de comunicaciones.*

**Decisión que se pide o desvío que se informa / Decision needed or deviation reported:** {{decision_o_desvio}}
*Primera línea. Si no hay pedido, decirlo: "no se requiere decisión".*

**Fecha límite / Due:** {{fecha_limite_ejecutivo}}
*Qué pasa si no se decide a tiempo.*

**Contexto en tres líneas / Context in three lines:** {{contexto_ejecutivo}}
*Qué pasó, por qué importa para el business case, qué se hizo ya.*

**Estado contra tolerancias / Status against tolerances:** {{tolerancias_ejecutivo}}
*Semáforo por objetivo afectado, con fuente. Solo lo que necesita atención.*

**Opciones y recomendación / Options and recommendation:** {{opciones_ejecutivo}}
*Si aplica: letras, consecuencia en una línea cada una, recomendación con grado de confianza. Si no, "n/a".*

**Próximo punto de control / Next checkpoint:** {{proximo_ejecutivo}}

*Una pantalla como máximo; el detalle en anexos o enlaces a los registros.*

---

## 2. Equipo / Team

**Para / To:** {{aud_equipo}} · **Canal / Channel:** {{canal_equipo}} · **Idioma / Language:** {{idioma_equipo}}

**Qué cambia desde hoy / What changes from today:** {{que_cambia}}
*Prioridades, alcance, fechas, tolerancias de los paquetes de trabajo.*

**Bloqueos y quién los destraba / Blockers and who unblocks them:** {{bloqueos}}
*Lista corta con responsable y fecha; referenciar ids de issues.csv (`I-###`) o de acciones.csv (`A-###`).*

**Prioridades de la semana / This week's priorities:** {{prioridades}}
*Tres como máximo, en orden.*

**Qué no cambia / What does not change:** {{que_no_cambia}}
*Evita rumores: lo que sigue igual.*

**A quién preguntar / Who to ask:** {{a_quien_preguntar}}
*Gestor del proyecto o gestor de equipo; canal de retroalimentación.*

---

## 3. Cliente y usuarios / Customer and users

**Para / To:** {{aud_cliente}} · **Canal / Channel:** {{canal_cliente}} · **Idioma / Language:** {{idioma_cliente}}

**Qué recibe y cuándo / What they get and when:** {{hitos_cliente}}
*Hitos y entregas con fecha base y fecha actual; indicar si una fecha se movió y por qué, sin detalle interno no autorizado.*

**Riesgos que le afectan / Risks affecting them:** {{riesgos_cliente}}
*Solo los que cambian su operación o sus decisiones; qué se está haciendo al respecto.*

**Qué se le pide / What we need from them:** {{pedido_cliente}}
*Aceptaciones, datos, disponibilidad de usuarios para pruebas, con fecha.*

**Información sensible verificada / Sensitive information check:** {{verificacion_sensible}}
*Confirmar que no incluye costos internos, asuntos comerciales ni datos de terceros sin la autorización de la matriz.*

**Contacto / Contact:** {{contacto_cliente}}

---

## 4. Proveedores (si aplica) / Suppliers (if applicable)

**Para / To:** {{aud_proveedor}} · **Canal / Channel:** {{canal_proveedor}}

**Dependencias y fechas / Dependencies and dates:** {{dependencias_proveedor}}
*Qué necesitamos de ellos y cuándo; qué les damos nosotros y cuándo.*

**Aceptaciones y pagos / Acceptances and payments:** {{pagos_proveedor}}
*Productos aceptados, pendientes y los hitos de pago asociados, con referencia contractual.*

**Qué se le pide / What we need from them:** {{pedido_proveedor}}

---

## Confirmación de envío / Send confirmation

**Revisado por / Reviewed by:** {{revisado_por}} · **Enviar a / Send to:** {{destinatarios_confirmados}} · **Confirmado el / Confirmed on:** {{fecha_confirmacion}}
*Completar antes de enviar; anotar el envío en diario.md.*

## Lista de verificación / Checklist
- [ ] El hecho es el mismo en las tres secciones; solo cambian detalle y pedido.
- [ ] Ejecutivo: decisión o desvío en la primera línea, fecha límite, una pantalla.
- [ ] Equipo: bloqueos con responsable, prioridades ordenadas, qué no cambia, a quién preguntar.
- [ ] Cliente: hitos con fechas, riesgos que le afectan, pedido con fecha; verificación de información sensible hecha.
- [ ] Proveedores: dependencias, aceptaciones y pagos con referencia contractual.
- [ ] Fuente citada; cifras con origen; `[por confirmar]` donde falte dato.
- [ ] Confirmación de revisor y destinatarios antes de enviar.
