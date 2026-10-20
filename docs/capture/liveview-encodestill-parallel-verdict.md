# Veredicto paralelo — Live View YC → EncodeStill (sesión 15)

Alcance: Sony A6000 fw 3.21, análisis estático exclusivamente. Sin hardware, sin flasheo, sin parches. Tres fuentes independientes, integradas aquí: investigador principal (Claude Sonnet 5, hilo principal), Rama A (subagente Claude Sonnet 5, razonamiento medio) y Rama B (Codex `gpt-5.6-terra`, razonamiento medio, `codex-cli 0.162.1`). Detalle de cada fuente y cruce completo en `analysis/liveview-encodestill-crosscheck.json`.

**No se afirma que SilentShutter funcione.** Este documento integra evidencia nueva; el veredicto de fondo (A > E > E2, sesión 14) no cambia.

## Incidente de proceso

Durante su primera ejecución, la Rama A intentó lanzar un segundo subagente (`general-purpose`), violando la restricción de «máximo un agente Claude» de esta sesión. Se detuvo con `TaskStop` antes de que produjera ningún entregable y se reinstruyó a la Rama A para ejecutar ella misma. La segunda ejecución cumplió la restricción y entregó evidencia real.

## 1. Quién investigó qué

- **Principal**: constructor real de `ObjCamera` (identidad del objeto 8 de la tabla, antes INFERENCIA, ahora VERIFICADA), firma completa de sus 9 pines, filas de topología `0x0a/0x07/0x2a`, exclusión de pin Camera/Player sobre `Effect.in0`.
- **Rama A**: estructura real de `EffectInternalMode` (un holder indirecto, no `this+0x14+4` como se aproximaba en sesión 14), getter/setter genéricos, el escritor `0x173158` y su tabla de mapeo `0x1025→modo`, re-decompilado del parser `REQ_DELIVER` con los modos que producen acción real, y confirmación independiente de las filas de topología y su `StsId`.
- **Rama B**: tamaños reales de los extents DMM (`0xed`, `0xe4`, `0x13d`), confirmación de que `0xe0b00` es solo la cabecera SDS (0x800 B exactos, nunca el raster), estructura de `RegionInfo` (0x40 B) en la preparación de `EncodeStill`, y el mecanismo `DmmShare`/`allocShare` con sus comprobaciones.

## 2. Qué descubrió cada uno (direcciones)

Ver tabla completa en `analysis/liveview-encodestill-crosscheck.json` → `hallazgos_nuevos_cruzados`. Resumen de lo más relevante:

| Hallazgo | Dirección ELF | Fuente | Estado |
|---|---|---|---|
| Constructor real de ObjCamera; 9 pines, todos de salida | `0x98c380` (wrapper `0x959bdc`), pines en `0x987dc6` | Principal | VERIFICADO |
| Getter/setter genéricos de estado | `0x14011c` / `0x140144` | Rama A | VERIFICADO |
| Escritor de EffectInternalMode y su tabla de mapeo | `0x173158` | Rama A | VERIFICADO |
| Modos con acción real: 1, 2, 3, 4, 5; resto solo log | `0x1e9880` | Rama A | VERIFICADO |
| Filas 0x0a/0x07/0x2a y StsId 0/0/6 | `0xcc4210 + id*0x20` | Principal y Rama A (independiente) | VERIFICADO |
| Tamaños de extent 0xed/0xe4/0x13d | `dmm.ko` ConfigData | Rama B | VERIFICADO |

## 3. Resultados comprobados entre ramas

El dato más sólido de esta sesión es que **Principal y Rama A llegaron, por caminos independientes, a la misma lectura de las filas de topología y del papel de `StsId`** en `TM::createLifeCycles` (ELF `0x4195c0`). No hubo contradicciones entre las tres fuentes. Los tamaños de extent de Rama B son consistentes con los tipos de unidad (`0x50b3f`/`0xe0b00`) que Principal y Rama A usan al describir la topología `0x2a`.

## 4. Modos de ObjEffect en EE y en PbCap

**PbCap**: el escritor `0x173158` lee el campo `0x1025` del propio mensaje `0x1011` entrante y fija el modo a `{2,3,4,5,7,0xe,0xf,0}` según una tabla; los valores `{2,3,4,5}` producen acción real (secuencia `SequencePinReqestDeliverSaveStillEditCmd`, `0x3900/0x6013`). El modo **1** (cola directa `0x3900/0x600d`) existe en el parser pero **su escritor no se localizó** en esta sesión.

**EE (Live View)**: **no se encontró ningún escritor de `EffectInternalMode` activado desde `ModelBootEE`**. Es consistente con que la lista de topologías de `ModelBootEE` (`{0xa,0x7}`, sesión 14) nunca incluye `0x2a`: si la salida nº1 de Effect hacia el Recorder no está conectada durante Live View, el modo interno de esa salida es irrelevante en ese momento — el bloqueo real sigue siendo la ausencia de un modelo que cree `0x2a` durante disparo/EE, no (solo) el valor del modo.

## 5. Qué YC entrega ObjCamera

**VERIFICADO**: ObjCamera es un productor puro — sus 9 pines (6 YC, STILL_DATA, SOUND, CAMERA_STATUS) son todos de salida; no tiene pin de entrada. Su salida YC #0 alimenta en exclusiva el pin de entrada #0 de Effect (topología `0x0a`), en exclusión mutua con Player sobre ese mismo pin (fila `0x4`, mismo destino).

**NO VERIFICADO**: el `unitType`/formato/geometría del YC que Camera entrega por esa salida. Ninguna de las tres fuentes lo recuperó esta sesión.

## 6. ¿Compatible con SDF/EncodeStill?

**NO DEMOSTRADO**, igual que en sesión 14. La única cadena YC→EncodeStill verificada (PbCap) pasa por un par de unidades DMM **fabricadas por ObjEffect** (`0x50b3f` + `0xe0b00`, ahora con tamaños exactos: `0x3fc000` B y `0x800` B) tras una conversión SDF explícita (resize/rotate o super-resolución). No hay evidencia de que el buffer crudo de Camera pueda entrar directamente sin ese paso de conversión.

## 7. ¿Pueden coexistir las topologías?

**INFERENCIA, reforzada por doble verificación independiente**: `0x0a` (entrada de Effect), `0x07` y `0x2a` (sus dos salidas) usan recursos de pin distintos y `StsId` distintos (0, 0, 6); no se halló, en `TM::createLifeCycles`, ningún chequeo que impida activar `0x2a` mientras `0x0a`/`0x07` están activas. **No verificado** si ObjEffect, en su propia lógica de pines (fuera del TopologyManager), impone una exclusión adicional.

## 8. ¿El frame permanece válido hasta terminar la codificación?

**NO VERIFICADO**, sin cambios respecto a sesión 14: el recorder no retiene las unidades de entrada; la Rama B confirma que `DmmShare`/`allocShare` es el único mecanismo de retención por refcount conocido, pero no se demostró que las unidades de EE lo respeten. El consumidor real de `CBID_ENCODE_STILL` y el momento de liberación de `0x50b3f`/`0xe0b00` siguen sin identificarse.

## 9. ¿Sigue viva la arquitectura E?

**Ni viable ni descartada.** A (LIRO nativa) sigue siendo la única ruta demostrada de extremo a extremo. E acumula más piezas verificadas esta sesión (identidad de Camera, estructura real de `EffectInternalMode`, tamaños de extent), pero los tres bloqueos centrales de sesión 14 persisten intactos:

1. Ningún modelo de disparo conocido crea la topología `0x2a` (búsqueda de esta sesión, 318 sitios de llamada a `createTopology`/`destroyTopology`, no exhaustiva por tiempo — declarado NO VERIFICADO, no DESCARTADO).
2. No se localizó qué modo de Effect atendería `REQ_DELIVER` con entrada de Camera durante EE (de hecho, ni siquiera se encontró que Effect entre en un modo relevante durante EE).
3. El `unitType`/formato del YC de Camera/EE sigue sin recuperarse.

## 10. Siguiente bloqueo técnico

Localizar el escritor de `EffectInternalMode = 1` (la única vía de cola directa `0x3900/0x600d`, distinta de la secuencia `0x6013` de PbCap) y determinar si existe algún camino — mensaje, modelo, o configuración dinámica de topología — que conecte la salida nº1 de Effect con el Recorder mientras la entrada nº0 recibe de **Camera** (no de Player). Sin eso, la arquitectura E sigue sin un punto de entrada demostrado en modo disparo.

## Clasificación global de esta sesión

| Afirmación | Estado |
|---|---|
| Identidad objeto 8 = ObjCamera | VERIFICADO (subida desde INFERENCIA fuerte) |
| ObjCamera sin pines de entrada | VERIFICADO |
| Estructura real de EffectInternalMode (holder indirecto) | VERIFICADO |
| Escritor 0x173158 y mapeo 0x1025→modo | VERIFICADO |
| Modos con acción real: 1,2,3,4,5 | VERIFICADO |
| Relación EffectInternalMode↔EE | NO VERIFICADO |
| Tamaños de extent 0xed/0xe4/0x13d | VERIFICADO |
| 0xe0b00 = solo cabecera SDS, no raster | VERIFICADO |
| Coexistencia de 0x0a/0x07/0x2a a nivel de TopologyManager | INFERENCIA (doble verificación independiente) |
| YC de Live View compatible con EncodeStill | NO DEMOSTRADO |
| Modelo de disparo con 0x2a | NO VERIFICADO |
| Arquitectura E viable | NI VIABLE NI DESCARTADA |

## Modelos y ajustes realmente usados

- Investigador principal: Claude Sonnet 5 (sesión interactiva), sin cambio de modelo ni esfuerzo.
- Rama A: subagente Claude, modelo `sonnet` (Sonnet 5), esfuerzo `medium`, confirmado por la propia ejecución (dos invocaciones: la primera incumplió la restricción de no delegar y se descartó sin entregables; la segunda cumplió y entregó).
- Rama B: Codex `codex-cli 0.162.1`, modelo `gpt-5.6-terra`, `model_reasoning_effort=medium`, confirmado por una llamada de prueba previa ("OK", 10 031 tokens) y por la ejecución real que generó los tres entregables.
