# S19-10 — entrega SFRA → Linux: YC interno y JPEG DMM

Alcance: A6000 firmware 3.21, análisis estático local y de sólo lectura. Se
usó `llvm-objdump -d --triple=thumbv7-linux-gnueabi` sobre las bibliotecas
Linux. No se modificó binario alguno, no se usó cámara ni se declara
SilentShutter funcional.

## Resultado

**VERIFICADO:** SFRA es un nombre real del binario `av-cam.bin`, no una
abreviatura supuesta: las cadenas incluyen `ScalarInfraAsyncMain.cpp`,
`[SFRA][CMD] ***GET_JPEG***`, `SET_PATH` y `SfrJpegBuffer.h`. SFRA recibe YC
internamente por pines SFRS (`Send EEPin`/`Send RecPin`) y produce buffers
JPEG READY. La entrega recuperada al cliente Linux es el resultado comprimido,
no un descriptor/raster YC.

Ruta demostrada:

`YC interno por pin EE/Rec → SFRA/ScalarInfraAsyncMain → JPEG READY (unidad DMM)
→ ISS pubSfrGetJpeg → DataflowInfra/OSAL → handle u16 + tamaño redondeado
→ pubDmmOpenUnit → /dev/mem + mmap → puntero Linux → munmap/close/free`.

Por tanto, la formulación «entrega del YC de SFRA a Linux» queda corregida:
**NO_VERIFICADO** que SFRA entregue YC crudo a Linux; lo que sí entrega esta
ruta es JPEG asociado a una unidad DMM. No hay copia de píxeles demostrada en
ISS antes de su consumidor de streaming.

## Hallazgos

| Estado | Archivo, dirección, método | Hallazgo |
|---|---|---|
| VERIFICADO | `av-cam.bin`, strings (offsets `0x7a49fd..0x7a4bcd`, `0x7a8467`); `strings -a -t x` | El nombre SFRA y sus comandos `SET_PATH`/`GET_JPEG` existen. También existen `Send RecPin` y `Send EEPin`, y campos/errores YC. Esto acredita YC como entrada interna del bloque, no como ABI Linux. |
| VERIFICADO | `libInfraStreamingServer.so:0xcc58..0xccf0`; objdump Thumb | `pubSfrGetJpeg` prepara servicio `0x2009`, comando `0x100`, longitud `0x14` y cantidad 1; tras la respuesta toma `u16` en `+0x14` como handle, `u16` en `+0x16 << 7` como tamaño, y contador `+0x10`. |
| VERIFICADO | `libInfraStreamingServer.so:0xca28..0xcb98`; objdump Thumb | `pvtScalarInfraIF` inicializa payload de `0x170` B, obtiene ID OSAL, llama `DataflowInfraSender::SendASync`, espera `DataflowInfraReceiver::ReceiveASync` y copia `0x170` B de vuelta. Es transporte de control/respuesta, no mapeo de píxeles. |
| VERIFICADO | `libInfraStreamingServer.so:0x11e38`, `0x1230c..0x12476`; objdump Thumb y strings | `pubMmap` abre `/dev/mem`, pide `pubDmmOpenUnit(dmm_extent*, handle)`, alinea base/tamaño a página y llama `mmap`. El map es `MAP_SHARED` (flags 1) y RW (prot 2). Esto es mapeo explícito de la unidad DMM, no ashmem. |
| VERIFICADO | `libInfraStreamingServer.so:0x14568..0x14658`; objdump Thumb | `MmapLiveViewJpeg` pasa el handle u16 a `pubMmap`, conserva base, delta y tamaño, y devuelve `base_mmap + delta`; al reemplazar el frame anterior hace `pubMunmap` y `pubDmmFreeUnit`. |
| VERIFICADO | `libInfraStreamingServer.so:0x122f0..0x12308`; objdump Thumb | Los thunks distinguen `pubDmmCloseAndFreeUnit(handle)` (segundo arg. 2) y `pubDmmFreeUnit(handle)` (0). La vida del handle requiere una operación explícita; no se demuestra un refcount transferido a MPR. |
| VERIFICADO | `libScalarDaemon.so:0x11a080..0x11a15a`, `0x11a16c..0x11a264`; objdump Thumb | El endpoint CameraSequence usa `getPreviewBufferingFrame`, espera evento `0x1e08` y serializa tres vectores SDCom. No contiene una arista estática a SFRA, ISS o al mapeo DMM de Live View. |
| NO_VERIFICADO | `libObj.so`, `libScalarDaemon.so`, `libInfraStreamingServer.so`; `strings -a`, símbolos/imports | No aparece `ashmem` en las tres bibliotecas ni hay llamada mostrada a su API. El hecho de que el kernel OSS tenga ashmem no transforma este mapa `/dev/mem` en ashmem. |
| DESCARTADO | Contraste con `s19-camera-yc-real-contract.md` | El handle JPEG u16 y el tamaño en bloques de 128 B no prueban `unitType`, plano, stride, formato, colorimetría, dirección física del YC de `ObjCamera`, ni compatibilidad con su contrato abierto. |
| INFERENCIA | Secuencia y nombres locales | El buffer es prestado/transferido al consumidor ISS hasta `DmmFreeUnit`; es coherente con el cleanup observado, pero el propietario final, refcount y el instante seguro de lectura de otro consumidor no fueron recuperados. |

## Formato, momento y consumidor

El contrato de salida recuperado es `{handle:u16, blocks128:u16,
contador:u8}`; ISS convierte `blocks128` a una **cota** de bytes con `<< 7`.
No se recuperó el tamaño JPEG exacto, firma SOI/EOI, APP/EXIF, resolución,
ni el formato de un YC. Por tanto JPEG válido y cualquier formato YC de salida
siguen **NO_VERIFICADOS**.

La entrega ocurre después de que SFRA tenga un buffer JPEG READY y cuando el
cliente pide `GET_JPEG`; no se recuperó una entrega de YC en el instante de
recepción por pin ni una sincronización con S2/captura fija. El consumidor
Linux realmente demostrado es `InfraStreamingServerUser`/`ContentHandlerEEImpl`
(ISS, Live View), no `CameraSequence` ni SDCom. `CameraSequence` es una ruta
paralela: su `GetPreviewFrame` llega a ScalarDaemon y devuelve vectores/tickets,
pero no se enlazó estáticamente al GET_JPEG de ISS.

## Relación con ObjCamera

`docs/capture/s19-camera-yc-real-contract.md` sigue siendo correcto en su
límite: `ObjCamera.out0 → Effect.in0` no revela descriptor de memoria. Este
resultado añade que una ruta distinta transforma YC interno de SFRA en una
unidad comprimida DMM y la expone a ISS por `mmap`. No rellena ninguno de los
campos abiertos del contrato YC de ObjCamera y no autoriza a equiparar ambos
buffers.

## Veredicto

**PARCIAL.** SFRA, la solicitud Linux, el handle DMM, el `mmap` explícito, la
forma parcial de la respuesta y la liberación del cliente quedan verificados.
No se verifican entrega Linux de YC/raw, formato/dimensiones JPEG/YC, tamaño
exacto, cache coherency, vínculo con CameraSequence/SDCom o con ObjCamera,
propiedad final, S2/EFCS/MPR/DCF. SilentShutter no se declara funcional.

## Siguiente tarea

**S19-11 (b): comportamiento de modos 2–5 de ObjEffect con entrada Camera.**
Es la prioridad adicional no ejecutada que ataca directamente el bloqueo
persistente `Camera.out0 → holder/pines SDF`; la ruta SFRA/Linux demostró una
salida JPEG paralela, no el contrato YC de la captura convencional.
