# Ejercicio · E2E-3 · El compromiso de tus interesados y la cadena de tu informe

## Cómo funciona este ejercicio

- **Para qué sirve:** llevar el caso a un proyecto tuyo. Vas a mapear a cinco interesados, escribir qué les prometiste,
  comprobar si lo cumplís y seguir de dónde salen las cifras de tu último informe.
- **Cuándo se hace:** la parte A, al cierre de la clase 1, después de la demostración (10 minutos); la parte B, al
  cierre de la clase 2, después de la demostración (10 minutos). Si lo hacés por tu cuenta, calculá 20 minutos.
- **Qué hacés:** completás la hoja de trabajo con un proyecto propio, real o reciente, que tenga al menos cinco
  interesados y un informe de avance enviado en el último mes. Alcanza con papel o una planilla, y con lo que
  recuerdes. Si no tenés un proyecto, usá el escenario del caso: los datos de partida están en
  [Lo que necesitás saber](#lo-que-necesitás-saber).
- **Cómo te autoevaluás:** al final de cada parte hay una tabla de criterios. Marcá cuáles cumple tu hoja; un criterio
  sin cumplir es un hallazgo sobre tu proyecto, no un error del ejercicio.
- **Ejemplo resuelto:** al final está la hoja resuelta con el escenario del caso, y cada dato dice de qué paso de la
  guía sale. Miralo **después** de intentarlo, para comparar, no antes.

---

## Lo que necesitás saber

### El escenario del caso

Una cooperativa construye un portal de autoservicio para sus socios. Laura Méndez es la ejecutiva; Martín Suárez, el
gestor; Sofía Ramírez, usuaria sénior y product owner; Lucía Benítez, jefa de equipo del proveedor. El proyecto tiene
diez interesados en un maestro único, beneficios en el business case y OKR que los complementan. La clase 1 arma el
mapa y el plan de compromiso; la clase 2 arma el informe de aspectos destacados del 8/1 desde el dato y, el 5/2,
descubre que tres interesados están fuera de la frecuencia de contacto prometida.

**Datos de partida para la parte A** (si usás el caso). Cinco interesados del maestro, con poder, interés, compromiso
actual → deseado, y el canal y la frecuencia registrados al inicio:

| Interesado | Poder | Interés | Compromiso | Canal y frecuencia |
|---|---|---|---|---|
| Consejo directivo | alto | medio | partidario → líder | informe ejecutivo por correo, trimestral |
| Sindicato de operadores | medio | alto | resistente → neutral | taller presencial mensual |
| Socios usuarios piloto (panel de 40) | bajo | alto | desconocedor → partidario | encuesta y boletín mensual |
| Área de TI del núcleo operativo | alto | medio | neutral → partidario | reunión técnica semanal |
| Unidad de cumplimiento | alto | bajo | neutral → partidario | correo y revisión por hito |

- Los valores «medio» se ubican del lado alto de la matriz. Las valoraciones las revisó el gestor con Laura.
- En el taller del 19/11, el delegado sindical dijo: «Prefiero que las novedades nos lleguen por correo, en un resumen
  corto, cada dos semanas».
- Un criterio de éxito del business case: B-03, préstamos simples respondidos en menos de 48 horas hábiles, de 96 a 48
  horas al 30/6/2027; dueña Sofía Ramírez; tolerancia de beneficios −10 %; revisión posterior al cierre el 31/12/2027.

**Datos de partida para la parte B** (al 5/2):

- Frecuencia prometida y último contacto registrado: TI, semanal, 18/1 · Martín Suárez (checkpoint semanal), ninguno ·
  Lucía Benítez (frecuencia registrada «diaria», la daily del equipo), ninguno · Laura Méndez, quincenal, 15/1 ·
  Consejo directivo, trimestral, 15/1. Sin contacto propio, se cuenta desde el primer envío del proyecto, el 15/1.
- Cifras del informe de aspectos destacados del 8/1: SPI 0,933 · CPI 0,942 · EAC USD 131.676 (+6,2 %) · 26 de 68
  puntos terminados · O-1 0,11 y O-2 0,24 · 1 acción vencida (A-004). Fuentes disponibles: el corte de valor ganado
  guardado (`evm-2027-01-08.json`), el avance de BMAD (`avance-bmad.csv`), los OKR al corte (`okr.py`) y el resumen de
  registros (`registro.py resumen`).

### Conceptos mínimos

- **Poder e interés:** poder es la autoridad real (aprobar presupuestos, vetar decisiones); interés, cuánto se involucra
  o cuánto lo afecta el proyecto.
- **Cuadrantes:** poder alto e interés alto → gestionar de cerca; poder alto e interés bajo → mantener satisfecho; poder
  bajo e interés alto → mantener informado; los dos bajos → monitorear.
- **Compromiso:** desconocedor (0), resistente (1), neutral (2), partidario (3), líder (4). **Brecha** = deseado −
  actual (0 si ya está donde querés).
- **Preferencia declarada:** la que la persona pidió con sus palabras (con la cita); se distingue de la que supuso el
  equipo.
- **Beneficio frente a KR:** un beneficio del business case tiene dueño de medirlo, línea base, tolerancia y fecha de
  medición después del cierre; un KR (resultado clave de un OKR) es una meta de ciclo, a menudo aspiracional.
- **Cadencia de contacto:** la frecuencia prometida en días (diaria 1, semanal 7, quincenal 14, mensual 31, trimestral
  92). El máximo sin contacto es la frecuencia × 1,5, redondeado; en pm-method, la sanidad lo vigila con STK-12.
- **Cadena de reporte:** cada cifra del informe sale de una fuente y es la misma en el informe, el tablero y el correo.
- **Aprobación trazable:** se sabe quién aprobó cada mensaje antes de enviarlo y dónde quedó escrito.

---

## Hoja de trabajo · parte A · Mapa de interesados y brecha de compromiso (clase 1)

**A1. Cinco interesados.** Elegí los cinco con más poder o más afectados por el proyecto.

| Interesado | Poder (alto/bajo) | Interés (alto/bajo) | Cuadrante | Compromiso actual | Compromiso deseado | Brecha |
|---|---|---|---|---|---|---|
| | | | | | | |
| | | | | | | |
| | | | | | | |
| | | | | | | |
| | | | | | | |

**A2. Lo que le prometiste a cada uno.** Para los mismos cinco:

| Interesado | Canal prometido | Frecuencia prometida | ¿La pidió la persona o la decidiste vos? | ¿Dónde está escrita? |
|---|---|---|---|---|
| | | | | |
| | | | | |
| | | | | |
| | | | | |
| | | | | |

**A3. ¿Beneficio o KR?** Escribí un criterio de éxito de tu proyecto y marcá qué tiene.

> Criterio: ……………………………………………… · [ ] dueño de medirlo · [ ] línea base · [ ] tolerancia · [ ] fecha de
> medición después del cierre

### Autoevaluación de la parte A

| Criterio | Cumple si… |
|---|---|
| Una sola fuente | Los cinco interesados están en un único lugar (planilla, registro) y no repetidos con otros nombres. |
| Brecha explícita | Cada interesado con brecha > 0 tiene una acción con dueño y fecha. |
| Promesa trazable | Canal y frecuencia están escritos y sabés si los pidió la persona (declarado) o los supusiste. |
| Beneficio completo | El criterio de A3 tiene las cuatro marcas; si solo tiene una meta, es un KR, no un beneficio. |

---

## Hoja de trabajo · parte B · Cadencia de contacto y cadena de reporte (clase 2)

**B1. ¿Se cumplió la promesa?** Para los interesados de A2 con frecuencia diaria, semanal, quincenal, mensual o
trimestral. Máximo = frecuencia × 1,5, redondeado.

| Interesado | Frecuencia (días) | Máximo (días) | Último contacto registrado (fecha) | Días hasta hoy | ¿Fuera de cadencia? |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |

Si un contacto ocurrió pero no quedó registrado (una reunión sin acta, una llamada), anotalo aparte: para el control,
un contacto sin registro no existe.

**B2. La cadena de tu último informe.** Tomá cinco cifras de tu último informe de avance (o del correo que lo
acompañó) y buscá de dónde salen.

| Cifra tal como aparece | Fuente (archivo, sistema o planilla) | ¿Se copió a mano o sale de un cálculo? | ¿Coincide con el tablero o con el correo? |
|---|---|---|---|
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |

### Autoevaluación de la parte B

| Criterio | Cumple si… |
|---|---|
| Cadencia verificable | Para cada interesado sabés la fecha del último contacto sin preguntarle a nadie. |
| Sin descuidos | Ninguno supera su máximo; si alguno lo supera, anotaste qué contacto vas a hacer y cuándo. |
| Frecuencia real | Ninguna frecuencia es una ceremonia del equipo (daily, sprint review) cargada como compromiso con un interesado, salvo que lo sea. |
| Cadena íntegra | Las cinco cifras de B2 tienen fuente y coinciden en el informe, el tablero y el correo. |
| Aprobación trazable | Podés decir quién aprobó tu último informe antes de que saliera, y dónde quedó escrito. |

---

## Para ir más allá

- ¿Cuál de tus interesados con poder alto podría pasar de neutral a resistente sin que nadie lo note durante un mes?
- ¿Qué cifra de tu informe cambiaría si la copiaras de nuevo hoy, y quién se daría cuenta?

---

## Ejemplo resuelto (escenario del caso)

Cifras de la corrida de referencia ([salida-g3.md](../../guias/evidencia/salida-g3.md)); entre paréntesis, el paso de
la [guía E2E-3](../../guias/E2E-3-interesados-okr-avance.md) de donde sale cada dato.

**A1.** Valoraciones del paso 2 y cuadrantes del paso 3 (◇ = valor «medio», ubicado del lado alto).

| Interesado | Poder | Interés | Cuadrante | Actual | Deseado | Brecha al inicio |
|---|---|---|---|---|---|---|
| ST-002 Consejo directivo | alto | medio ◇ | gestionar de cerca | partidario | líder | 1 |
| ST-004 Sindicato de operadores | medio ◇ | alto | gestionar de cerca | resistente | neutral | 1 |
| ST-005 Socios usuarios piloto | bajo | alto | mantener informado | desconocedor | partidario | 3 |
| ST-006 Área de TI del núcleo | alto | medio ◇ | gestionar de cerca | neutral | partidario | 1 |
| ST-007 Unidad de cumplimiento | alto | bajo | mantener satisfecho | neutral | partidario | 1 |

Brecha total al inicio: 7 niveles (paso 2). Acciones del plan de compromiso con dueña y fecha: A-001, taller con el
sindicato (Sofía, 20/11); A-002, boletín al panel (Sofía, 1/12); A-003, informe ejecutivo trimestral al Consejo (Laura,
15/1) (paso 5). TI y cumplimiento no tienen acción propia en el plan del paso 5: la de TI llega en el paso 13 (A-005).

**A2.**

| Interesado | Canal | Frecuencia | ¿Pedida o decidida? | ¿Dónde está escrita? |
|---|---|---|---|---|
| ST-002 Consejo | informe ejecutivo por correo | trimestral | decidida por el proyecto, validada con Laura (paso 2) | maestro de interesados y matriz de comunicaciones (pasos 2 y 5) |
| ST-004 Sindicato | correo, resumen ejecutivo | quincenal | pedida por el delegado en el taller del 19/11: PF-006…PF-008, que reemplazan el taller mensual (paso 8) | `preferencias.csv`, con la cita; la matriz se actualiza a quincenal (paso 8) |
| ST-005 Socios piloto | encuesta y boletín | mensual | decidida por el proyecto (paso 2) | maestro y matriz (pasos 2 y 5) |
| ST-006 TI | reunión técnica | semanal | decidida por el proyecto (paso 2) | maestro y matriz (pasos 2 y 5) |
| ST-007 Cumplimiento | correo y revisión | por hito | decidida por el proyecto (paso 2) | maestro y matriz (pasos 2 y 5) |

Para comparar, Laura Méndez declaró su canal en una entrevista: correo (PF-001, «Prefiero que el avance me llegue por
correo, no por chat»); su frecuencia quincenal sale de la matriz de comunicaciones, no de una preferencia (paso 4).

**A3.** B-03, préstamos simples respondidos en menos de 48 horas: dueña Sofía Ramírez, línea base 96 horas,
tolerancia −10 % (≤ 52,8 horas), medición al 30/6/2027 y revisión posterior al cierre al 31/12/2027. Tiene las cuatro
marcas: es un beneficio. El KR que lo complementa es KR-2.1 (mantener la respuesta por debajo de 48 horas) (paso 6).

**B1, al 5/2** (paso 13).

| Interesado | Frecuencia | Máximo | Último contacto | Días | ¿Fuera? |
|---|---|---|---|---|---|
| ST-006 TI del núcleo | semanal (7) | 10 | 2027-01-18 | 18 | sí |
| ST-009 Martín Suárez | semanal (7) | 10 | ninguno (se cuenta desde el primer envío, 15/1) | 21 | sí |
| ST-010 Lucía Benítez | diaria (1) | 2 | ninguno (desde el 15/1) | 21 | sí |
| ST-001 Laura Méndez | quincenal (14) | 21 | 2027-01-15 | 21 | en el límite |
| ST-002 Consejo directivo | trimestral (92) | 138 | 2027-01-15 | 21 | no |

Contacto que ocurrió sin registro: el checkpoint semanal de Martín y Lucía. La frecuencia «diaria» de Lucía era la daily,
una ceremonia del equipo: se corrige a semanal (paso 13). Correcciones: reunión con TI el 5/2 (EN-008) y acción A-005;
checkpoint registrado (EN-009 y EN-010) (paso 13); resumen quincenal a Laura, el sindicato y Sofía el 5/2 (EN-011 a
EN-013) (paso 14). Al 19/2, ningún STK-12 y la brecha total en 3 niveles (paso 14).

**B2.** Cadena de reporte del informe de aspectos destacados del 8/1 (fuentes del paso 10; cifras de los pasos 9 y 10).

| Cifra | Fuente | ¿A mano o cálculo? | ¿Coincide? |
|---|---|---|---|
| SPI 0,933 · CPI 0,942 | `evm-2027-01-08.json` | cálculo (`evm.py`) | sí: informe, tarjetas y mensaje de Sofía |
| EAC USD 131.676 (+6,2 %) | `evm-2027-01-08.json` | cálculo | sí: informe y mensaje de Sofía; el comunicado base cita el 6,2 |
| 26 de 68 puntos (38,2 %) | `avance-bmad.csv` | cálculo (`bmad.py avance`) | sí |
| O-1 0,11 · O-2 0,24 | `okr.py … --corte 2027-01-08 --json` | cálculo | sí: informe, comunicado y mensaje ejecutivo |
| 1 acción vencida (A-004) | `registro.py resumen --corte 2027-01-08 --json` | cálculo | sí: informe y tarjetas |

Antes de enviar, la comprobación del paso 11 revisa las 12 cifras del comunicado y los borradores: ninguna sin respaldo
en el informe. Aprobación trazable: los borradores se aprueban como "Gestor: Martín Suárez", con un pedido de permiso
que resuelve una persona, y cada envío queda en `envios.csv` (EN-001 a EN-007) con quién lo aprobó (paso 11).
