# Pruebas en vivo de pm-method · 2026-10-17 15:05

### multisesion (USD 1.96)

- OK    business case y PID registrados como artefactos
- OK    autorizar-proyecto y autorizar-etapa registradas
- OK    cada puerta tiene su fila en decisiones.csv
- OK    las puertas las registró pm-director (no el hilo principal ni otro agente)
- OK    tolerancias de etapa: costo 10 % y tiempo 2 semanas
- OK    PID y business case congelados en 00-direccion/historial/
- OK    tras /compact el orquestador sigue sabiendo la etapa
- OK    fin de etapa: pasa a SB con borrador del informe, o no inventa datos y los pide (sin informe inventado)
- OK    línea base del PRD registrada antes de la etapa de entrega
- OK    sanidad final sin ERROR
- OK    listas de verificación confirmadas para autorizar-proyecto y autorizar-etapa

| turno | pedido | turnos del modelo | USD | s |
|---|---|---|---|---|
| 1 | Armá el business case, el PID y el plan de la primera etapa de entrega | 19 | 0.75 | 191.7 |
| 2 | La junta (Marta Sosa, ejecutiva) aprobó hoy el proyecto (PID, business | 2 | 0.27 | 48.8 |
| 3 | /compact | 0 | 0.31 | 16.3 |
| 4 | ¿Cómo venimos y qué sigue? | 4 | 0.44 | 15.9 |
| 5 | Terminamos la etapa 2. Preparemos el límite de etapa y el informe de f | 8 | 0.19 | 27.0 |
