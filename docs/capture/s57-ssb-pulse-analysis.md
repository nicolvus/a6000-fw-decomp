# S57-B — Pulso SSB: productores, orden y consecuencias (20-10-2026)

> **Aviso D4 (25-10-2026):** [S58](s58-conclusions.md) retira la lectura del umbral `0x1000` como condición de exposición: pertenece a SetRead/AGC (SetExposure A7S `0x436f4168`, SetRead `0x436f4a94`).

**Resultado:** SSB es un *strobe* de un bit (ID1 bit 3) que el firmware emite **siempre justo después de preparar una actualización de exposición y antes de `Execute(1)`**; no aparece en `Execute(0)`, ni en el fin de exposición, ni en cambios de modo sin SetExposure. Clasificación: **operación de sincronización/aplicación probable (INFERENCIA, confianza media)**; *no* se demuestra finalización de exposición. Pruebas: `tests/test_s57_imx210_exposure.py::{SsbProducers,Id1Emulation}`; matriz S57-05…14.

## 1. Productores (VERIFICADO: índice de llamadas Capstone + REA `procedure_callers`)
`0x43ad9116` (fachada de `[O+0x268]=1`, log «SSBRK_ON») tiene 5 llamadores. REA da el 5.º como `0x43b1af3a` porque su función contiene el bloque `0x438c86b0`; los bytes confirman `0x438c883c`.

| Llamador | Contexto (cadenas del firmware) | Secuencia de llamadas (orden de direcciones) |
|---|---|---|
| `0x438c7a0a` en `0x438c7800` | arranque de captura: `ReadExecuteBase`, `PGA ON`, `SHD ON`, `28Limit ON`, `LongObMode`, `SnrCtrlMode`, `opb_out`, `CamCore/DFE Start` | SetMode → **Execute** → SetExposure → **SSB** → SetRead → **Execute** |
| `0x438c8326` en `0x438c828c` (StartExposure) | paso del secuenciador de exposición | SetExposure → SetRead → **SSB** → Execute(1) si `[cap+0x4b9c]==0`; si no, solo `Execute(0)` |
| `0x438c883c` en `0x438c86b0` | `ExposureTimerStart!(first)` / `ExposureTimerEnd!` | ShutMode:=1; SetExposure → SetRead → **SSB** → Execute(1) (paso 0); luego `msg 0x107` a Darwin con `[cap+0x56c]` y `[cap+0x570]` |
| `0x438cc5ce` en `0x438cc4b4` | `PrelightDebug: ImagerDriveMode`, `dmm Err` | consulta de modo (`0x436d61a4`) → **SSB** (sin SetExposure en esa función) |
| `0x43ae936c` en `0x43ae935a` | helper de `0x4381106c` (CAMERA_MAIN_SYNC, «StrtExps») | **SSB** → SetExposure (arg = `shd,svd,spl,sint,ShutMode`) |

Todos los productores con SetExposure piden SSB **inmediatamente antes o después** de él. `0x4381106c` (por VD, planificador CAMERA_MAIN_SYNC) llama al helper en cada actualización de exposición.

## 2. Orden temporal reconstruido (VERIFICADO por desensamblado + emulación)
```
SetExposure  → registros sombra 3..8 (svd/shd/spl), 0x100/0x101 (ShutMode 2), ID1 bits 2,4,6,7
SetRead      → registros de lectura (no ID1)
SSB          → [O+0x268]=1                                   (solo una bandera)
Execute(1)   → 0x436d79c4 → 7b34 → 8040 → 0x436d7c08 (aplica el pulso a A/B) → 7c58 → 7c94 → 7db4 → 7cb0 → 7cf0 → 92d0 → 8244 → 8064
               → lista de 119 (SyncMode 2, un único lote) → espera de bandera P2S (0x436d5bcc) → 8 inmediatos (modo 0)
```
Las dos entradas de ID1 van **en el mismo lote** (`A|0x08` primero, `B` después). En el hilo de bytes (emulación de formateador y commit reales) quedan en bloques distintos: `81 05 81 00 00 0c cc` y `81 2f 81 00 01 c4 20 …`: la escritura `0xCC` y la `0xC4` están separadas por 5 bytes de cabecera del bloque siguiente; **escribirlas seguidas en el buffer no implica dos transiciones separadas en el pin**: el intervalo real lo fija el hardware P2S (no observado).

## 3. Comparación con otros pulsos
Escaneo de operaciones de bit (`analysis/s57/bitops.json`, 52 registros): el bit 3 de ID1 lo escribe **solo** `0x436d7c08`. Los demás pares «poner/quitar bit» son ramas excluyentes: SetExposure por ShutMode, `0x436d7b34` (ID0 bit1, 0x127, 0x126, 0x128) según `[O+0x267]` (SLEEP_ON). No hay otro reset/latch/confirmación con patrón de pulso en la región imager. Una coincidencia de patrón no prueba equivalencia funcional.

## 4. Diferencial A7S (IMX235)
En A7S la petición `[O+0x3d7]` **no la solicitan llamadores externos**: la genera `SetExposure` A7S (`0x436f4a94`): `=1` cuando el parámetro u16 `arg+2` supera `0x1000` (con el valor ajustado), `=0` si no (`0x436f4b10–0x436f4b48`). El consumidor (`0x436f459c`) activa el bit `0x10` del byte `+4` de un registro y borra la petición. A7S no admite ShutMode 2. Por tanto el *strobe* existe en ambos modelos pero con **condición y bit distintos**: en A6000 lo decide el flujo de captura; en A7S la magnitud del parámetro. No hay equivalencia demostrada; ShutMode/pulso en modos Silent 0x4e/0x4f no se emularon (el formateador A7S no está emulado).

## 5. Qué NO se concluye
* SSB **no** es «segunda cortina electrónica»: se emite al *iniciar* captura/exposición y no en `ExposureTimerEnd!` (`0x438c893a`: sin SetExposure/SSB/Execute).
* No es un reset de sensor demostrado: ID1 conserva el resto de bits y el pulso dura un lote.
* Su nombre «SSBRK» no se descifra con el firmware.

## 6. Límites
Llamadas indirectas (vtable, punteros a función) no cubiertas por el índice; `0x438cc4b4` (prelight) no se siguió hasta su `Execute` (`0x438cc8b0` en otra función). Duración real y efecto en el sensor: NO VERIFICADO (requiere traza CIS0).
