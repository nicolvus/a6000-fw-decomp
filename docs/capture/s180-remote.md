# S180 — `[REMOTE]`: el mando a distancia (sub-bloque de `[ACCY]`) — etiqueta nueva de la fw3.21

**32 trazas · 33 sitios (regla PIC estricta) · 16 funciones emisoras · 0 muertas · 0 gemelos.** Detalle: `analysis/s180_remote/remote.md` / `.json`.

## Qué es
`[REMOTE]` es el **subsistema de mando a distancia (control remoto por UART)** de la A6000 fw3.21: el sub-bloque `REMOTE` de `[ACCY]` que S136 ya había delimitado (**mismo rango `0x43c25b47`–`0x43c26319`, mismos 33 sitios, mismas 16 funciones** ⇒ **hipótesis del enunciado CONFIRMADA**). Lo implementa la clase RTTI **`AccyUmDeviceRemote`** (`0x43c26340`), 8.ª subclase de `AccyUmDeviceBase` (`0x43c2536d`); su vtable (`0x43fb9114`) son los 8 métodos virtuales del accesorio.
**La sigla SÍ tiene base textual**: `REMOTE` → `AccyUmDeviceRemote`. `ACCY` y `UM` **no** → se dejan sin desarrollar.

## Las 32 trazas (sitio y función en `remote.md`)
```
0x43c25b47 NotifyUartCommand...UART CMD:%C%C%C%C%C%C […]   0x43c25ba9 RecvCmd Unknown Category   0x43c25bdf EventKey Catwgory
0x43c25c26 RetrySendCmd...retry_up   0x43c25c59 RetrySendCmd Buffer err   0x43c25c88 SaveInfo...GF/SS/Freeze/Photo/Zoom/Tally
0x43c25cdb Zoom State Change To %d Speed   0x43c25d15 RestoreInfo...Savedata   0x43c25d4e ExecUartCommand
0x43c25d76 To Input KEY:%08X STATE:%08X INFO:%08X   0x43c25db5 SendCmd...CMD:%S retry   0x43c25de7 SendCmd Buffer Busy
0x43c25e21 TallyControlCmd...retry   0x43c25e54 CallForTransaction...Wait Tally Light   0x43c25ea9 NotifyApiRequest...Command/State
0x43c25ef9 NotifyApiRequest...Buffer Busy   0x43c25f3d NotifyApiRequest...Tally Light State   0x43c25f8b NotifyApiRequest...Not Support
0x43c25fdd AccyCmdClr   0x43c26000 RemoteClose...Spinal/GF/SS/Freeze/Photo/Zoom   0x43c26068 GUIDE FRAME OFF
0x43c260b0 START STOP OFF   0x43c260f7 PHOTO FREEZE OFF   0x43c26140 PHOTO REC OFF   0x43c26186 ZOOM OFF (2 sitios)
0x43c261c7 NotifyDetached   0x43c261ee NotifyUartTimedOut   0x43c26229 TimeoutNotify   0x43c26266 EventTimeout Tally Light TIMEOUT
0x43c262a0 NotifyUartResponse...Set Tally Light   0x43c262e2 Set Tally Light:%02X State   0x43c26319 NotifyAttached
```

## Hallazgos con dirección
- **NO es el patrón «prefijo + gemelo» de S177/S179**: el «núcleo» sin prefijo **no existe** como literal autónomo (**0/32** en A7S y A6300; las 6 coincidencias externas en la A6000 son literales de **otros sub-bloques `[ACCY]`**: `[HELLO]` comparte `RetrySendCmd...retry_up:%d`, `SendCmd Buffer Busy...` y `NotifyUartTimedOut...RetryCount:%d`; `[HOUSING]` comparte `RestoreInfo...Savedata:...`; `NotifyAttached`/`NotifyDetached` son genéricos repetidos) y **no hay doble emisión**: las 16 funciones **nunca** llaman al logger global `0x43902718`. Todo sale por un **logger propio del sub-bloque**, `0x435661e4`, con firma `(id_módulo=93, ?, nivel, fmt, …)` y niveles `1=ERR 2=WARN 3=DEBUG 4=INFO` (**33/33** coinciden con el nivel del prefijo; los 111 sitios `[ACCY]` usan `r0=93`). Los 15 sub-bloques de `[ACCY]` usan **14 loggers distintos** (misma plantilla).
- El prefijo es **`[ACCY][<NIVEL>][REMOTE]:<línea>:`** — el **nivel va dentro** (23 B `ERR`, 24 B `INFO`/`WARN`, 25 B `DEBUG`).
- **El primer `%d` es el nº de línea del fuente**: 32 líneas distintas entre **113 y 967** ⇒ un fichero de ~1000 líneas. **El nombre del fichero NO es identificable** (el bloque `[ACCY]` no referencia ningún nombre de fichero) → NO VERIFICADO.
- **Estructura de datos**: objeto `AccyUmDeviceRemote` con flags **GF `+0x3C`, SS `+0x3D`, Freeze `+0x3E`, Photo `+0x3F`, Tally `+0x40/+0x41/+0x42`, Zoom `+0x34/+0x38`, Spinal `+0x0C`**; estado serializado en **3 bytes** (`SaveInfo` `0x435664d0` / `RestoreInfo` `0x43566580`): byte0 = `GF|SS<<1|Freeze<<2|Photo<<3|Zoom<<4`, byte1 = Tally, byte2 = 0.
- **Tabla de 5 códigos de tecla** (`0x0A000009` GUIDE FRAME, `0x0A00000D` START STOP, `0x0A000008` PHOTO FREEZE, `0x0A00000C` PHOTO REC, `0x0A000011` ZOOM) y **3 tablas `tbb`** (categoría→carácter `0x435662f4`, comando→botón `0x43566638`, estado de tally→carácter `0x43566960`).
- **33/33 pares PIC verificados a mano**, 0 fallos, 0 reuso de registro; el escaneo local reproduce el mapa global con **0 discrepancias**; **0** punteros absolutos de 4 B (2 coincidencias de bytes en `.data` del A6300, no son punteros).

## Diferencial
| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[REMOTE]` / `[ACCY]` | **32** / **106** | **0** / **0** | **0** / **0** |
| núcleo como literal autónomo | 0/32 | **0/32** | **0/32** |
| clase `AccyUmDeviceRemote` | `0x43c26340` | `0x43c25aed` | `0x43d0ca6c` |
| vtable (8 métodos) | `0x43fb9114` | `0x43fb2e14` | `0x4416fd74` |
| `NotifyUartCommand` | `0x43566290` | `0x4356451c` | `0x4355ec30` |
| tabla de 5 códigos de tecla | `0x435667f0` | `0x43564874` | `0x4355f040` |

→ **Cambio de *logging*, no de código**: el mando remoto **existe igual** en los tres firmware (misma clase, misma vtable, mismo protocolo ASCII, misma tabla de teclas; `NotifyUartCommand` tiene la misma secuencia de instrucciones: `cmp #0x23` / `cmp #0x37` / `sub #0x30` / `cmp #5` / `tbb`). Lo propio de la fw3.21 de la A6000 son **las trazas**. *(Salvedad: la comparación mezcla versión y modelo.)*

## Línea del obturador: NEGATIVO ACOTADO
0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`. Lo único: `GUIDE FRAME` (guía de encuadre), `PHOTO REC` (grabación), `Zoom ... Speed` y los `Timeout` de UART. El «START STOP» del mando es una **tecla genérica** (`0x0A00000D`) entregada por `NotifyInput` `0x43565814`: **el módulo no ejecuta el disparo**. → **S51 (A/B/C = NO) se mantiene.**
