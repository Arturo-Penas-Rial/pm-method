---
tipo: entrevista-interesado
proyecto: "{{proyecto}}"
version: 0.1
fecha: "{{fecha}}"
autor: "{{autor}}"
estado: borrador
idioma: "{{idioma}}"
confidencial: si
interesado: "{{stakeholder_id}}"
---

# Entrevista de interesado · Stakeholder interview — {{stakeholder_id}} {{nombre}}

> Guion breve (20–30 min) para conocer las expectativas del interesado y **cómo prefiere que el proyecto se comunique con él**. Lo que la persona declara se registra como preferencia `declarado` con la cita textual; nada se aplica hasta que el gestor lo confirma (`interesados.py confirmar`). **Circulación restringida.** / Short interview to capture expectations and communication preferences; declared answers become `declarado` preferences with a verbatim quote.

**Aviso a la persona / Notice to the person (leer al inicio):** {{aviso}}
*Explicar para qué se usan las respuestas (adaptar la comunicación del proyecto), quién las verá, que puede pedir verlas, corregirlas o retirarlas en cualquier momento y que no se evalúan emociones ni personalidad. Registrar si acepta.*

**Acepta que se registren sus preferencias / Agrees to record preferences:** {{acepta}}  *(si / no)*

## 1. Rol y expectativas / Role and expectations
| Pregunta / Question | Respuesta (texto literal cuando sea posible) / Answer |
|---|---|
| ¿Qué espera que el proyecto logre para usted o su área? | {{expectativa}} |
| ¿Qué decisiones del proyecto necesita tomar, aprobar o puede vetar? | {{decisiones}} |
| ¿Qué le preocupa o podría hacerle frenar el proyecto? | {{preocupaciones}} |
| ¿Cuánto tiempo puede dedicarle y en qué momentos? | {{dedicacion}} |

*Poder e interés se valoran después, por el gestor, con fuente: no se le preguntan a la persona en esos términos.*

## 2. Preferencias de comunicación / Communication preferences
| Dimensión / Dimension | Pregunta / Question | Respuesta literal / Verbatim | Valor normalizado / Value |
|---|---|---|---|
| canal | ¿Por dónde prefiere recibir novedades: correo, Slack, Teams, reunión, llamada, tablero? | {{r_canal}} | {{v_canal}} |
| formato | ¿Prefiere la conclusión primero, los datos, algo visual, una lista o el contexto completo? | {{r_formato}} | {{v_formato}} |
| nivel_detalle | ¿Resumen ejecutivo de una página, un resumen o el detalle completo? | {{r_nivel}} | {{v_nivel}} |
| frecuencia | ¿Con qué frecuencia: semanal, quincenal, mensual, solo en hitos, solo si hay desvíos? | {{r_frecuencia}} | {{v_frecuencia}} |
| idioma | ¿En qué idioma? | {{r_idioma}} | {{v_idioma}} |
| registro | ¿Formal o cercano? | {{r_registro}} | {{v_registro}} |
| horario | ¿Hay días u horarios mejores para recibir o tratar temas del proyecto? | {{r_horario}} | {{v_horario}} |
| estilo_decision | Para decidir, ¿qué necesita: datos, consenso, una recomendación clara, delegarlo? | {{r_decision}} | {{v_decision}} |
| evitar | ¿Hay algo que prefiera no recibir o en lo que no quiere estar en copia? | {{r_evitar}} | {{v_evitar}} |

*Valores normalizados: los del esquema (`registro.py --proyecto <dir> esquema estereotipos`). Una respuesta ambigua queda sin valor normalizado y se repregunta.*

## 3. Registro / Recording
```bash
# una fila por respuesta con valor normalizado (estado: propuesta)
python3 <pm-estado-proyecto>/scripts/registro.py --proyecto <dir> agregar preferencias --campo stakeholder_id={{stakeholder_id}} \
  --campo dimension=canal --campo valor=correo --campo procedencia=declarado --campo evidencia="«…cita…»" --campo fuente=01-inicio/entrevistas/{{archivo}}
# el gestor confirma con la persona y registra quién confirmó
python3 <pm-interesados>/scripts/interesados.py --proyecto <dir> confirmar PF-… --por "Gestor: Nombre"
```

## Lista de verificación / Checklist
- [ ] Aviso leído y aceptación registrada; sin preguntas sobre salud, creencias ni otros datos sensibles.
- [ ] Respuestas literales cuando fue posible; nada inferido se registra como `declarado`.
- [ ] Cada preferencia con dimensión, valor normalizado, evidencia y fuente.
- [ ] Preferencias confirmadas por el gestor y con vigencia (por defecto 180 días).
- [ ] Documento guardado como restringido (`confidencial: si`).
