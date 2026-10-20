# S57-F — SyncMode del P2S, VD y aplicación de registros (20-10-2026)

**Resultado:** `SyncMode` es un valor que el firmware escribe **tal cual** en el registro `0xfc088800` del bloque P2S; solo el modo 2 usa el *handshake* de banderas OSAL y el disparo `1,0,1` en `0xfc088808`. `Execute` envía el lote de 119 registros en modo 2, **llama a una espera de banderas P2S** (`0x436d5bcc`) y solo después envía los 8 registros inmediatos. Qué evento activa esas banderas y si la espera bloquea hasta el fin real de la transmisión **no se resolvió** (la API de banderas es OSAL indirecta); la aplicación «en el próximo VD» sigue siendo **INFERENCIA**: ninguna referencia a VD en esa ruta. Pruebas: `tests/test_s57_imx210_exposure.py::P2SSync`; script `analysis/s57/sync_modes.py`; matriz S57-29…32.

## F.1 SyncMode (VERIFICADO, emulación del código real, 4 modos)
| cfg[0] | Escritura en `0xfc088800` | Banderas OSAL (grupo `0x18`) | `0xfc088808` |
|---|---|---|---|
| 0 | 0 | — | 1 (arranque directo) |
| 1 | 1 | — | 1 |
| **2** | **2** | apertura: `clr`(0x20), `set`(0x10); commit: `wait`(0x10), `clr`(0x10), `set`(0x20) | 1, **0, 1** tras el commit |
| 3 | 3 | — | 1 |
La apertura `0x436d5b74` solo acepta el modo 2 (en otro caso registra «`P2S : Unsupported SyncMode.`») y copia 5 B de configuración a `P+0xa8`. Las banderas `0x10`/`0x20` del grupo `0x18` funcionan como estado del driver («inactivo»/«iniciado»): la apertura limpia 0x20 y pone 0x10; el commit espera 0x10, lo limpia y pone 0x20; la espera de `Execute` (`0x436d5bcc`, máscara `[P+8]\|[P+0xc]` = 0x30) no se puede evaluar sin la semántica OSAL de la llamada indirecta y de la IRQ del P2S (registrada con `0x436d594c`): **no se afirma que bloquee hasta el fin eléctrico**. **El valor `2` del registro de bloque es lo que el hardware interpreta**; su significado no se lee del firmware.

## F.2 Orden en Execute (VERIFICADO, desensamblado)
`0x436d839c`: preparar registros (SetMode-fill, `7b34`, `7c08` pulso, `7cf0`…) → `0x436d75f8(lista 119, modo 2)` → `0x436d5bcc` (espera bandera) → `0x436d75f8(lista 8, modo 0)` → rotar historial de drive_mode (`[0x178]←[0x174]←[0x170]`) → refresco de parámetros de lectura (`0x43ad9a78/9ab2`). `Execute(0)` (`0x436d6a34`) solo reinicia el P2S (`0x43ad8d76`) y vuelve: no envía registros.
Consecuencia: **todo el lote de exposición (ID3–8, ID1, 0x100/0x101) viaja en una única transacción síncrona**; el pulso SSB queda dentro de ella (ver [SSB](s57-ssb-pulse-analysis.md)).

## F.3 VD y estado del sensor
* `SIFSyncCode` (log de `Execute`, `[vtable+0xac]`) es el código de sincronía del **receptor SIF**: `0x435440a0` («SIF SetSyncCode : Serial/Parallel Synccode Not Selected») programa patrones de sincronía de 10 bit (`0x3FF`, `0xFF00`, …). No hay vínculo demostrado entre ese código y `SyncMode` del P2S: **no se convierte «se aplica en el próximo VD» en hecho**.
* El planificador por VD es CAMERA_MAIN_SYNC `0x43792a0c` (7 KB): «`VD_Pre: start delayed %dV => %dV %dus`», «`overflow %dV`», «`HS3: process margin warning %dus`». Existe un margen de proceso por VD y se avisa cuando la exposición se retrasa uno o más VD, lo que sugiere **aplicación en frontera de VD**, pero el cuerpo del planificador no se analizó (frontera).
* Aplicación inmediata/frontera de fotograma/de línea/durante lectura: sin evidencia para distinguirlas con el firmware solo. La combinación `VD_Pre` + contador de pasos del host ([informe C](s57-exposure-timing-origin.md)) apunta a frontera de VD para el **inicio** del secuenciador.

## F.4 Segunda cortina electrónica (búsqueda de un fin de integración)
Se buscó una secuencia que termine electrónicamente la integración:
1. En `ExposureTimerEnd!` (`0x438c893a`) el host no reescribe ningún registro del sensor ni emite SSB/Execute.
2. `Execute(0)` no transmite datos.
3. No hay en el lote de 119 registros un registro cuyo único cambio ocurra al final de la exposición: lo que cambia entre foto y reposo son los de modo (SetMode) y ShutMode.
4. Lectura programada/transferencia de filas: la lectura completa de 24 MP dura ≈66,8 ms (4176 líneas, [`imx210-video-readout.md`](imx210-video-readout.md)); si el sensor cerrara la integración de cada fila en su lectura, la distorsión de obturador de persiana sería de ese orden — INFERENCIA, no comprobada.
Resultado: **no hay evidencia** de que el firmware gestione el fin de integración por registros; tampoco evidencia en contra. El comportamiento podría estar en el sensor (temporización interna con svd/shd/spl), en XPI o en Darwin.

## F.5 Límites
Sin hardware: el bloque P2S, la IRQ que activa la bandera y los instantes reales no se observan. Falta seguir `0x436d594c` (callback registrada) y la tabla OSAL (`[[GOT 0x16dc]+0x14]+0x9c…0xa8`) hasta quien activa la bandera tras la transmisión.
