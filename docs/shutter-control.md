# Interfaces de captura y obturador

Resultado vigente: [SilentShutter E015–E017](capture/silent-shutter-status.md):
factory y CamMgr resueltos, cola 0x30001, tipo 5, tabla LIRO de 220 comandos,
handler 0x40e3 que guarda modo. Off=0 y On=1 verificados. Falta el consumidor
físico del estado y demostrar final electrónico de foto completa.

## Resultado vigente E012/E013

Leer primero [EFCS y fin electrónico](capture/shutter-investigation.md) y
[protocolo de captura](capture-pipeline.md). EFCS, SilentShutter y su envío
OSAL tienen ahora rutas estáticas localizadas. La asociación 0x1008→procesador
TakePicture se verificó. Siguen abiertos consumidor OSAL, selección por modelo
y operaciones físicas. Categoría E, sin parche.

Las afirmaciones «sin xrefs» y «0x1008 pendiente» conservadas debajo son el
registro histórico anterior a E012/E013; ya no describen el resultado actual.

## Registro anterior a E012/E013

Actualización: [traza SilentShutter](silent-shutter-trace.md), E007–E009.
Se identificó un constructor de configuración con opciones On/Off en
CautionConfig.so. Las limitaciones siguientes sobre libObj siguen vigentes
hasta resolver sus referencias. Las direcciones ELF previas no incluyen la
base adicional 0x10000 de estas importaciones Ghidra.

E009 añade una xref de libObj a SetSilentShutterModeForLiro y una rutina
candidata de conversión de mensajes; todavía no identifica la operación física
de cierre. Las afirmaciones históricas de ausencia de xrefs siguientes se
refieren a la primera pasada, anterior a E009.

[VERIFICADO] `libObj.so`, SHA-256 `8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a`, contiene cadenas en offsets de archivo:

| Offset | Cadena |
|---|---|
| 0xbe22d0 | S_IMAGER_CURTAINMODE |
| 0xd5178c | pvt_SetSilentShutterMode |
| 0xd529b0 | pvt_ActionSetSilentShutterMode |
| 0xe072e8 | diagnóstico SetSilentShutterModeForLiro NON SUPPORTED |
| 0xe4ec7b | PARAMID_SILENT_SHUTTER_MODE |
| 0xe52aac | MSGID_SET_SILENT_SHUTTER_MODE_CMD |

Son datos/cadenas, no entradas de funciones identificadas. No hay xrefs resueltas ni prueba de alcanzabilidad, soporte por modelo o acción sobre cortinillas. `ShutterMute` puede referirse al sonido/interfaz y no establece silencio mecánico. Una ruta de rechazo genérica tampoco demuestra imposibilidad en A6000.

`libsencore.so` también contiene `S_IMAGER_CURTAINMODE`; pendiente resolver lectores, escritores y significado de valores. No se conoce registro del sensor ni comando físico de cierre.

[VERIFICADO] `libcamera.so`, SHA-256 `7bb156b3c68b802fcdeceb83037d770504c128d0b73a6708122d58589f80c013`, símbolo original `android::CameraHardwareDiadem::takePicture()` en VA ELF relativa `0x170c0`, 52 bytes. A `0x170e4` carga `0x1008`; a `0x170f0` salta a `SDComMsg_Basic` en `0x16d9c`. Hay llamada virtual condicional anterior; destino no resuelto. Esto verifica envío de una orden de alto nivel, no inicio físico de exposición.

[VERIFICADO] `libScalarDaemon.so`, SHA-256 `ca28cbf4c5c6402160ad80f6ad9f5e99052f42c3fabc382c557fcded18addc29`, `CommandProcessorCameraTakePicture::AsyncProcessor::execute`: símbolo `0x1080b5`, código Thumb `0x1080b4`, 528 bytes. En `0x108144` llama al PLT de `SystemEventIssuerCamera::captureStart`; en `0x10823c` a `onCaptureStart`. Dossier: `analysis/functions/dossiers.json`; desensamblados y símbolos en `analysis/`.

No se ha probado aún que el mensaje 0x1008 despache a ese procesador. Direcciones son relativas al ELF; ASLR y direcciones del dispositivo desconocidas. Etiquetas aproximadas del desensamblador para funciones locales no se consideran identidades demostradas.
