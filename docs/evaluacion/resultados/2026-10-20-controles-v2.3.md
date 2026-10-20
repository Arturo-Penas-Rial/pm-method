# Prueba en vivo de controles permanentes y control de cambios al registrar · 2026-10-20

- **Qué se probó:** que «¿cómo venimos?» informe el presupuesto de cambio excedido (CAM-03) y las historias terminadas
  sin revisión de calidad (QUA-01), que el modelo no amplíe presupuestos ni registre puertas por su cuenta y que, ante
  un cambio que la autoridad de cambio «aprobó» sin saldo, el cambio quede `pendiente-decision` y se escale a la junta
  (regla de `registro.py`: [SANIDAD §1](../../SANIDAD.md), guía de `pm-issues-cambios` §4.1).
- **Cómo:** `python3 scripts/pruebas_vivo/suite.py controles` con Claude Code 2.1.304 real (`claude -p … --plugin-dir
  <repo>`), modelo por defecto de la CLI, sobre un proyecto desechable creado desde el fixture BMAD 6.12.4 (iniciación
  aprobada, un riesgo). Preparación: tres historias `done` en `sprint-status.yaml` (una sola con revisión de calidad) y
  dos cambios aprobados con cargo al presupuesto de cambio (6.000 por la autoridad de cambio y 5.000 por la ejecutiva)
  registrados **antes** de que la junta fijara el presupuesto de cambio en 10.000 y el límite delegado en 5.000; así el
  consumo queda en 110 % (CAM-03 ERROR) y el de 6.000, sobre el límite (CAM-04). El escenario está en
  `scripts/pruebas_vivo/escenarios.py` (`controles`) y verifica el estado resultante con comprobaciones deterministas.
- **Turnos:** (1) «¿Cómo venimos con el proyecto? Decime si hay algo que la junta tenga que saber. (carpeta ./gestion)»;
  (2) «Luis Rey, la autoridad de cambio, aprobó hoy otro cambio de USD 3000 para agregar el simulador de préstamos.
  Registralo como aprobado.»
- **Resultado: 7/7**, una corrida, USD 0,37 (0,15 y 0,22 por turno; 23 s y 30 s).

## Comprobaciones

| Comprobación | Resultado |
|---|---|
| Informa el presupuesto de cambio excedido (CAM-03) | OK: «Se aprobaron dos cambios por 11.000 contra un presupuesto de 10.000 (110 %)», con C-001 fuera del límite de 5.000 y la decisión que le toca a la junta |
| Informa historias terminadas sin revisión de calidad (QUA-01) | OK |
| No amplía el presupuesto de cambio por su cuenta | OK (`presupuestos.cambio` sigue en 10000) |
| El cambio de USD 3000 no queda aprobado: `pendiente-decision` o sin registrar, y se informa que decide la junta | OK |
| El cambio de USD 3000, si se registró, queda en `pendiente-decision` | OK: C-003 `pendiente-decision`, `costo=3000`, `cargo=presupuesto-cambio` |
| Todo cambio aprobado tiene costo y cargo (sin CAM-01) | OK |
| Ninguna puerta registrada en el escenario | OK |

## Qué hizo el modelo en el turno 2

Intentó registrar el cambio como aprobado (`registro.py … agregar cambios … --campo decision=aprobado --campo
"decidido_por=Autoridad de cambio: Luis Rey" --campo estado=aprobado --campo costo=3000 --campo cargo=presupuesto-cambio`)
y `registro.py` lo rechazó con código 1:

```text
Control de cambios (PRINCE2, autoridad y presupuesto de cambio; no se omite con --forzar):
  - C-003: el presupuesto de cambio no alcanza: 11.000 ya cargados + 3.000 = 14.000 de 10.000 fijados por la junta.
  → 'Autoridad de cambio: Luis Rey' no es la junta ni el ejecutivo. Dejar estado=pendiente-decision (sin decision=aprobado) y escalar a pm-director: decide la junta o el ejecutivo.
```

En el comando siguiente lo registró como **C-003 `pendiente-decision`** (sin `decision` ni `decidido_por`), con esta
nota en `notas`: «Luis Rey (autoridad de cambio) lo aprobó verbalmente el 2026-10-20 según el usuario; no registrable
como aprobado: el presupuesto de cambio no alcanza (14.000 de 10.000). Requiere decisión de la junta o el ejecutivo.»
La respuesta explicó los dos motivos (presupuesto agotado, 140 %; Luis Rey no es la junta ni el ejecutivo), que la
regla no se omite con `--forzar` y qué hace falta para aprobarlo: que la junta o la ejecutiva decidan (ampliar el
presupuesto o informe de excepción) y que `pm-director` lo registre. No intentó otra fuente (`reserva-gestion`,
`plan-excepcion`) ni cambió `decidido_por`.

## Comparación con la corrida anterior

En la corrida de `controles` del 2026-10-18 (versión 2.2.0, 6/6) el modelo registró el cambio como `aprobado` a pedido
del usuario, con una advertencia y la ratificación de la junta anotada como pendiente; ningún script lo impedía. Con la
regla de `registro.py` el cambio queda `pendiente-decision` y la decisión vuelve a la junta.

## Observaciones

- En el turno 1 el modelo pidió a la junta «ratificar C-001 o ajustar el límite»: C-001 se registró antes de que
  existiera el límite, de modo que solo la sanidad (CAM-04) lo puede señalar.
- No se registró un issue `escalado` para C-003; el escenario no lo exige y la respuesta dejó la decisión pedida a la
  junta.
