# S402 — Mapeo de diferencias A7S vs A6000 a pruebas físicas (P1–P8)

> Hito de la **línea del obturador electrónico** (Agente C, sesión S402).
> Basado en `s401-a7s-silent-control-path.md`. Para cada diferencia, se indica cuál prueba de `physical-test-plan.md` la confirmaría o refutaría, y se proponen pruebas nuevas donde faltan.

---

## Tabla de mapeo

| # | Diferencia | Prueba(s) física(s) que la confirmarían/refutarían | Qué resultado confirmaría A7S vs A6000 |
|---|---|---|---|
| 1 | **Handler LIRO 0x40e3 ausente en A7S** | **P6** (service shell lectura MCU Darwin) | Si service shell permite leer RAM Darwin y se ve que A7S procesa Silent sin handler LIRO 0x40e3 → confirma vía alternativa (CAIF directo). |
| 2 | **libObj.so rechaza ForLiro en ambos** | **Ninguna** (capa user, no física) | No testeable físicamente; es decisión de firmware user-space. |
| 3 | **Darwin `no_silent` (bit 0x20) solo en A7S** | **P5** (analizador lógico bus CAIF/Darwin) — **CRÍTICA** | **P5**: Medir `pkt[+0x12]` en bus CAIF durante foto Silent A7S vs mecánica A7S vs A6000. Si A7S Silent muestra bit 0x20 y A6000 no → confirma diferencia Darwin. |
| 4 | **Darwin rama sin mecanismo + reposición coherente (A7S) vs tipo 0 sin reposición (A6000)** | **P3** (forzar `G+0x808=1` con disparo) + **P7** (imagen hélice/LED flicker) | **P3**: Si forzar tipo 2 en A6000 produce foto silenciosa (P7) → A6000 acepta rama sin mecanismo. Si además reposición acciona cortinas (sonido doble) → tipo 0 incompleto vs A7S. |
| 5 | **CAIF bit 0x20: A7S Sí (inferido) / A6000 No** | **P5** (analizador lógico) — **CRÍTICA** | **P5**: Capturar paquete CAIF evento 1 en A7S Silent y A6000. Verificar bit `0x20` en `pkt[+0x12]`. |
| 6 | **Sensor IMX235 vs IMX210 (APIs extra en A7S)** | **P7** (imagen hélice/LED flicker a 1/1000s+) | **P7**: Comparar rolling shutter / bandas flicker en Silent A7S vs A6000 (si se logra activar). Si A7S muestra lectura global/parcial electrónica y A6000 no → diferencia sensor/driver. |
| 7 | **API imager extra en A7S (StabilizationTime, FrameSize, Mode)** | **P6** (service shell leer MCU) + **P7** | **P6**: Si service shell expone registros IMX235 de estabilización → confirma API real. **P7**: Comportamiento de exposición en modos extra. |
| 8 | **LiroSeq CheckSet* ausente en ambos** | **Ninguna** (capa validación, no física) | No testeable físicamente; ausencia en ambos = no discriminante. |

---

## Análisis por prueba física (P1–P8)

### P1 — Observación pasiva `G+0x808` (selector tipo mecanismo)
- **Relevancia**: Baja para diferencias A7S/A6000. `G+0x808` es variable Darwin A6000; A7S usa `S+0xd0.b5` (`no_silent`).
- **Confirmaría**: Qué ajuste menú mueve selector en A6000 (base para P2–P4).
- **No discrimina** A7S vs A6000 directamente.

### P2 — Forzar `G+0x808=1` sin disparar
- **Relevancia**: Media. Prueba si selector tipo 2 es aceptado por Darwin A6000.
- **Confirmaría**: Darwin A6000 acepta tipo 2 (cambia `G+0x784` a 2).
- **Refutaría**: Si no cambia → selector no se ejecuta fuera de captura o se regenera.

### P3 — Forzar `G+0x808=1` **con disparo remoto** (CRÍTICA para Diferencia 4)
- **Relevancia**: **ALTA**. Prueba directa de si tipo 2 en A6000 produce exposición electrónica.
- **Confirmaría A7S-like**: Tipo 2 + disparo → foto silenciosa (P7) + **sin sonido de cortinas** + **sin reposición con bobinas**.
- **Confirmaría diferencia 4**: Si hay sonido de reposición (doble click) → A6000 tipo 0 **no** replica reposición coherente de A7S Silent.
- **Métricas**: `done <bytes>`, tipo leído antes/después, **P7 obligatoria**.

### P4 — Forzar tipo directamente `G+0x784=2` con disparo
- **Relevancia**: Media-Alta. Salta selector `G+0x808` y prueba si Darwin ejecuta tipo 2.
- **Confirmaría**: Darwin A6000 ejecuta rama tipo 2 (equivalente a A7S Silent en exposición).
- **Riesgo**: Reinicio (medio-alto). Solo tras P2/P3 limpios.

### P5 — Traza pasiva bus CAIF/Darwin (analizador lógico) — **CRÍTICA para Diferencias 3 y 5**
- **Relevancia**: **MÁXIMA**. Única forma de **ver** el bit `0x20` en `pkt[+0x12]` y confirmar predicado `no_silent` en Darwin.
- **Metodología**: Analizador lógico en `GPIO_9`/P4C (CN4900) y `MSS_SO_DWN` durante:
  - (a) Foto mecánica A7S
  - (b) Foto Silent A7S
  - (c) Foto mecánica A6000
  - (d) Foto EFCS A6000
- **Qué medir**: ID mensaje CAIF, `pkt[+0x12]` bits, polaridad/flanco `P4C←0`, relación con `P4C←0`.
- **Éxito**: Distinguir si host A7S cambia `pkt[+0x12]` bit 0x20 en Silent y Darwin A7S responde omitiendo P4D/P4E.
- **Requiere**: Abrir cámara (valorar aparte).

### P6 — Service shell lectura MCU Darwin / RAM captura
- **Relevancia**: Media-Alta. Para verificar estado interno Darwin (`S+0xd0.b5` `no_silent`, `S+0x153` fase) y estructura captura A6000 (`captura+0x804` equivalente).
- **Confirmaría**: Si `captura+0x804` (o equivalente A6000) cambia con menú Silent/EFCS.
- **Riesgo**: Service mode; backup NVRAM obligatorio.

### P7 — Prueba objetiva obturación electrónica (imagen) — **CRÍTICA para Diferencias 4, 6, 7**
- **Relevancia**: **MÁXIMA**. Criterio medible vs oído.
- **Metodología**: Fotografiar (a) hélice/ventilador girando o patrón barras en movimiento, (b) LED flicker 1/1000s+, en:
  - Mecánico
  - EFCS (si disponible)
  - Silent A7S (referencia)
  - A6000 tipo 0 forzado (P3/P4)
- **Éxito**: Diferencia reproducible rolling shutter / bandas flicker entre configuraciones.
- **Guarda**: RAW/JPEG con nombre y hash.

### P8 — `+0x210=1` «disparo múltiple» (EFCS)
- **Relevancia**: Baja para Silent. Relacionado con EFCS (cortina delantera electrónica), no Silent completo.
- **Confirmaría**: Significado de `+0x210` (EFCS vs ráfaga).
- **No discrimina** Silent electrónico completo.

---

## Pruebas nuevas propuestas (solo redacción)

### P9 — Traza pasiva línea serie LIRO → IMX210/IMX235 (I2C/SPI sensor)
- **Objetivo**: Ver registros reales programados en sensor durante exposición Silent A7S vs A6000 tipo 0.
- **Metodología**: Analizador lógico en bus de control sensor (pines IMX210/IMX235 serial interface) durante captura.
- **Confirmaría**: Qué registros `SetExposure`/`SetRead`/`SetMode` programa cada driver en modo Silent/electrónico.
- **Refutaría**: Si A6000 IMX210 programa mismos registros que A7S IMX235 → driver capaz, falta activación.
- **Riesgo**: Requiere acceso físico a pines sensor (flex PCB); **muy invasivo**.

### P10 — Forzar campo `captura+0x804` equivalente A6000 a valor 2 (Silent) + disparo
- **Objetivo**: Probar si A6000 `av-cam.bin` tiene la condición `*(captura+0x804)==2` para poner bit CAIF 0x20 (como A6300).
- **Metodología**: Identificar offset equivalente en A6000 (estructura captura), escribir 2 vía `dd`/`/dev/mem`, disparar remoto, medir P7 + bus CAIF (P5).
- **Confirmaría**: Si A6000 pone bit 0x20 en CAIF al forzar campo → faltaría solo origen del campo (UI→campo).
- **Refutaría**: Si no pone bit → construcción CAIF A6000 **no tiene** la rama Silent (hardcoded absence).

### P11 — Comparar secuencia Darwin completa: A7S Silent vs A6000 tipo 0 (registro a registro)
- **Objetivo**: Verificar si A6000 tipo 0 omite **solo** P4D/P4E/ADC o también otras escrituras de control (p. ej. `0x42668234`/`0x42668238` en darwin-state-machine.md).
- **Metodología**: P5 (analizador lógico) + registro completo de todas las escrituras Darwin durante captura.
- **Confirmaría**: Diferencias exactas en control de cortinas/power/timers.

### P12 — Test de consistencia reposición: forzar tipo 0/2 en A6000 y medir estado cortinas tras aborto
- **Objetivo**: Verificar Diferencia 4 (reposición coherente).
- **Metodología**: Forzar tipo 0/2 (P3/P4), iniciar captura, abortar (soltar botón / timeout), medir posición cortinas (P5/P9) o sonido doble.
- **Confirmaría**: Si A6000 tipo 0 **no** acciona bobinas en aborto → mecanismo queda en estado desconocido (riesgo físico).

---

## Priorización para ejecución

| Orden | Prueba | Diferencias que cierra | Riesgo | Info/riesgo |
|---|---|---|---|---|
| 1 | **P5** (bus CAIF) | 3, 5 | Bajo (solo lectura, pero abre cámara) | **Más información por riesgo**: ve bit 0x20 y predicado Darwin en vivo |
| 2 | **P1** (obs. `G+0x808`) | Base para P2–P4 | Bajo | Prerrequisito |
| 3 | **P7** (imagen hélice/LED) | 4, 6, 7 | Bajo | **Criterio objetivo** silencioso vs mecánico |
| 4 | **P2** (forzar `G+0x808=1` sin disparo) | 4 | Bajo-Medio | Valida selector |
| 5 | **P3** (forzar `G+0x808=1` + disparo) | 4 | Medio | **Prueba funcional completa** |
| 6 | **P6** (service shell) | 1, 3, 7 | Medio | Estado interno Darwin/captura |
| 7 | **P4** (forzar `G+0x784=2` + disparo) | 4 | Medio-Alto | Solo si P2/P3 limpios |
| 8 | **P10** (forzar campo captura+0x804) | 5 | Medio | Prueba directa construcción CAIF |
| 9 | **P9** (bus sensor) | 6, 7 | Muy alto | Solo si P5/P7 indican camino viable |
| 10 | **P8** (`+0x210`) | EFCS | Medio | Separado de Silent |
| 11 | **P11** (secuencia Darwin completa) | 3, 4 | Bajo (si P5 hecho) | Análisis post-P5 |
| 12 | **P12** (reposición aborto) | 4 | Medio | Seguridad mecanismo |

---

## Notas de implementación

- **P5 es la prueba única** que puede confirmar/refutar las Diferencias 3 y 5 (bit CAIF 0x20 y predicado Darwin `no_silent`) de forma directa. Sin P5, toda la cadena CAIF→Darwin queda en **INFERENCIA**.
- **P7 es obligatoria** en cualquier prueba con disparo (P3, P4, P10) para tener criterio objetivo de "silencioso".
- **P10** es la prueba más directa para verificar si `av-cam.bin` A6000 tiene la **capacidad latente** de poner bit 0x20 (como A6300) y solo le falta el origen del valor.
- Las pruebas nuevas (P9–P12) **no se ejecutan** sin autorización expresa y plan de seguridad; se documentan aquí para completitud.

---

## Actualización de etiquetas en S401

| Diferencia | Etiqueta actual | Tras P5 + P3 + P7 limpias |
|---|---|---|
| 3 (Darwin no_silent) | VERIFICADO (estático) | **VERIFICADO (físico)** si P5 ve bit 0x20 y omisión P4D/P4E |
| 5 (CAIF bit 0x20) | INFERENCIA (A7S) | **VERIFICADO** si P5 ve bit 0x20 en A7S Silent y no en A6000 |
| 4 (reposición coherente) | VERIFICADO (estático) | **VERIFICADO (físico)** si P3/P12 muestra doble click en A6000 tipo 0 |
| 6 (sensor APIs) | VERIFICADO (estático) | **VERIFICADO (físico)** si P7/P9 muestra comportamiento electrónico real |

---

## Referencias

- `docs/capture/s401-a7s-silent-control-path.md` (diferencias detalladas)
- `docs/capture/physical-test-plan.md` (P1–P8 originales)
- `docs/capture/s53-darwin-a7s-a6000-comparison.md`, `s54-mechanism-type-zero.md`, `darwin-state-machine.md`, `silent-caif-transport.md`
- `analysis/ghidra/a6300-caif-silent-payload.json`, `a6000-caif-event-dispatch.json`