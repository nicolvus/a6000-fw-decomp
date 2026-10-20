# S19-09 — CameraSequence → SDCom → ScalarDaemon

Alcance: firmware A6000 3.21 local, análisis estático. No se modificó un
binario, no se abrió Ghidra ni se usó una cámara. `llvm-objdump -d
--triple=thumbv7-linux-gnueabi` se usó sobre el lado Thumb de
`libScalarDaemon.so`; `libcameraseq.so` contiene A32 (símbolos de función con
dirección par), por lo que su lectura fiable se hizo con el triple ARMv7.

## Cadena recuperada

| Clasificación | Evidencia local | Resultado |
| --- | --- | --- |
| VERIFICADO | `libcameraex_jni.so`, símbolos JNI `JNICamSeqContext` y UND `scalar::CameraSequenceIF_open` | JNI usa la implementación nativa exportada por `libcameraseq.so`; no se observó un puente Binder en este tramo. |
| VERIFICADO | `libcameraseq.so:0x8214`, `0x85f0`, `0x8638`; método: objdump ARMv7 | `CameraSequenceDiadem::startPreviewSequence` construye parámetros SDCom y envía el mensaje `0x124` al objeto `CameraSeqUtil` almacenado en `this+8`. El resultado se prueba antes de marcar el estado local de preview. |
| VERIFICADO | `libcameraseq.so:0x90a4..0x9120`; método: objdump ARMv7 | `getPreviewSequenceFrames(n, ...)` toma mutex, crea un parámetro entero ID 5 con `n` y envía SDCom `0x127`. Copia tres vectores de la respuesta y construye un `DeviceMemoryDiadem` por elemento en `0x9308/0x9390`. |
| VERIFICADO | `libScalarDaemon.so`, exports `CommandProcessorCamseq*` y `SystemEventIssuerCameraSequence::*`; método: `llvm-nm -D -C`, objdump Thumb | ScalarDaemon implementa procesadores separados Start/Stop/Update/GetPreviewInfo/GetPreviewFrame/SetRawCapture/StoreImage y emite/consume eventos CameraSequence. Es el extremo nativo del protocolo SDCom. |
| VERIFICADO | `libScalarDaemon.so:0x11cd0c..0x11cf00`; método: objdump Thumb | El procesador StartPreview exige un `SDJob`, valida el parámetro `0x3001`, registra evento `0x1e06`, interpreta vectores y devuelve un código por SDCom. Por tanto el inicio no es una llamada directa al productor de JPEG. |
| VERIFICADO | `libcameraseq.so:0x9f08..0xa2d8`; método: objdump ARMv7 | `DeviceMemoryDiadem::createBuffer` crea un objeto de 0x20 B, guarda ticket/tipo y un par de dos enteros. `release()` envía SDCom `0x3` con parámetro entero ID 4 cuyo valor es el ticket (`0xa290..0xa2d0`). |
| VERIFICADO | `libcameraseq.so:0xbca4..0xbd6c`; método: objdump ARMv7 | `readBuffer(dst,len,off)` consulta propiedades 1 y 2, valida longitud/offset, llama `CameraSeqUtil::mapSharedMemory`, hace `memcpy(dst, mapped+off, len)` y desmonta. Esto prueba una copia de bytes desde memoria compartida, no una decodificación JPEG. |
| VERIFICADO | `libcameraseq.so:0xb868..0xbbf4`; método: objdump ARMv7 | Las escrituras usan el mismo mapeo de memoria compartida; la implementación también puede mapear descriptor de archivo para la sobrecarga entre buffers. El backend observado es SDCom más mapeo compartido, no Binder. |

La ruta reconstruida, con sus límites, es:

`Java CameraSequence → JNI/JNICamSeqContext → CameraSequenceDiadem → CameraSeqUtil::sendSDComMsg → libsdcom.so → ScalarDaemon CommandProcessorCamseq* → SystemEventIssuerCameraSequence / eventos → respuesta SDCom → DeviceMemoryDiadem(ticket, propiedades) → mapSharedMemory → readBuffer → release SDCom 0x3`.

## Preview de 640×480, formato y propiedad

- **VERIFICADO** — `libcameraseq.so:0x8268` carga el valor por defecto 640
  durante `startPreviewSequence`; las opciones locales incluyen las cadenas
  `PREVIEW_FRAME_WIDTH`, `PREVIEW_FRAME_HEIGHT`, `PREVIEW_FRAME_FORMAT` y
  `PREVIEW_FRAME_MAX_NUM`. El componente permite que la opción cambie esos
  valores.
- **NO_VERIFICADO** — no se recuperó un literal 480 asociado de forma
  inequívoca al mismo request, ni el identificador numérico del formato para
  640×480. La afirmación pública de un preview JPEG de 640×480 es sólo
  contexto de provenance: no sustituye la evidencia local.
- **NO_VERIFICADO** — no se halló comprobación de firma JPEG (`FF D8`) ni
  decodificador JPEG en `DeviceMemoryDiadem::readBuffer`; ésta sólo copia un
  rango de bytes. Tampoco hay arista estática desde `GetPreviewFrame` al
  encoder JPEG, sensor/ISP o `ObjStillRecorder`.
- **INFERENCIA** — el ticket es un token de préstamo del recurso remoto:
  aparece al crear el `DeviceMemoryDiadem` y vuelve al daemon sólo mediante
  `release()`. Esto delimita una responsabilidad de devolución, pero no prueba
  el conteo de referencias, el propietario último ni qué ocurre ante fallo,
  abandono o `stopPreviewSequence`.
- **DESCARTADO** — tratar un `DeviceBuffer`/`DeviceMemory` como evidencia de
  raster YC, de JPEG válido o de captura Silent. El contrato local observado
  es opaco: ticket, tamaño/propiedades y bytes mapeados.

## Precondiciones y relación con S2/MPR

- **VERIFICADO** — StartPreview tiene precondiciones de job, parámetro válido
  `0x3001` y evento de espera `0x1e06` en
  `libScalarDaemon.so:0x11cd0c..0x11ce3a`.
- **VERIFICADO** — StopPreview no equivale a liberar cada buffer: envía SDCom
  `0x125` y posteriormente `0x12b` con valor 300
  (`libcameraseq.so:0x7e28..0x7ed0`); el release individual es el mensaje
  `0x3` de `DeviceMemoryDiadem::release`.
- **NO_VERIFICADO** — una arista desde S2, el dominio LIRO convencional, o
  cualquier condición Silent/EFCS hacia CameraSequence. `CameraSequence` no
  debe confundirse con `takePicture()` convencional.
- **NO_VERIFICADO** — conexión a MPR: no hay arista estática entre los tickets
  DeviceMemory/SDCom y `MprIf::EncodeStill`, `WriteStill`, DCF o el productor
  JPEG. Por ello no se puede derivar una cadena de captura/guardado ni la
  funcionalidad de SilentShutter.

## Siguiente tarea propuesta

**S19-10 (a): entrega del YC de SFRA al cliente Linux.** Este análisis cerró
el consumidor Android hasta el préstamo SDCom, pero deja opaco el productor
que asigna tickets, dimensiones/formato y backing compartido. Seguir la
entrega SFRA→cliente Linux ataca directamente ese bloqueo y puede separar
preview codificado de YC/raster sin asumir equivalencia de sensor.

## Veredicto

**PARCIAL.** La frontera CameraSequence/SDCom y el ciclo mínimo
ticket→lectura→release quedan demostrados localmente. Formato, 640×480 real,
productor JPEG/YC, ownership completo, S2, MPR y SilentShutter siguen sin
verificación. No se declara SilentShutter funcional.
