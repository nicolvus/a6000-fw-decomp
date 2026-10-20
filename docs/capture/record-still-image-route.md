# recordStillImage / GetFileImage — ruta real (sesión 9, P1)

Direcciones: Ghidra libObj = ELF + 0x10000 (ELF `0x920464` = Ghidra `0x930464`). Scripts: `scripts/libobj_dec.sh libObj.so out.json 0xADDRt`; exports `analysis/ghidra/libobj-rec-*.json`.

## Veredicto (corrige `sony-dcf-playback.md` y `silent-architecture-comparison.md`)
- VERIFICADO: `0x930464` (ObjStillRecorderImage::GetFileImage, traza módulo 0xac) **no llama a `WriteStill` ni a ninguna función DCF**. Su única llamada de grabación es `0x92c09c` (wrapper `MprIf::MakeWriteStillImage`, traza 0xb3), cuyo único llamador es ELF `0x920838` (dentro de esta función). Callers por BL de `0x91c09c` (ELF): solo `0x920838`.
- VERIFICADO: lo que produce es **un archivo JPEG completo en memoria** (EXIF + miniatura + principal), no un fichero en SD:
  - reserva un pool/DMM nuevo (`0xebabc` → `0xeff04` = handle `iVar2`), lo mapea con `0x92ffa8`;
  - `StillInfo` (0x6b0) lleva en `+0x48/+0x4c` el área de salida (base, tamaño); tras `MakeWriteStillImage` calcula `offset = *(out+4)` y `size = fin − offset`;
  - los guarda en el registro de imagen: `+0x30` handle (u16), `+0x34` offset, `+0x38` tamaño, `+0x3c` constante; estado `+8` = 2 (OK) o 3 (error) (`0x92ecf0`);
  - notifica el mensaje **0x3a48** al listener `param_1[0x13]` (vtable+0xc) y libera con `0x930174`.
- VERIFICADO: `0x930174(ctx, handle, ptr, size)` = desmapear (`0xeddbc(ptr,size)`) + liberar handle (`0xf24b4`); no escribe nada.
- VERIFICADO: `0x93677c(lista, clave)` = búsqueda en la lista enlazada `ctx[1]+8` del nodo cuyo tipo (`0x92ecf8` = `nodo+0xc`) iguala `clave = ctx[0x11]`; devuelve el registro de imagen (`nodo+8`).
- VERIFICADO: la entrada se invoca por tabla de métodos (registros de 0x1c B en ELF `.data.rel.ro` ~`0x1017240`: {fn, invocador común `0x91eab1`, …}); la fila de `GetFileImage` entra por el thunk ELF `0x920a79` (aparece dos veces). No hay BL/puntero directo a `0x920465`.
- INFERENCIA: es la ruta que sirve "dame el JPEG de esta imagen" (transferencia/Wi-Fi/visor), coherente con el nombre GetFileImage. El mensaje 0x3a48 y el consumidor de `+0x30..0x3c` NO están localizados.
- DESCARTADO: que `recordStillImage` → `0x930464` grabe en la SD. El vínculo con 0x1027/ScalarDaemon sigue NO VERIFICADO.

## Contrato real (registro de imagen, offsets del registro `iVar6`)
| off | uso |
|---|---|
| +0x10 | handle DMM (u16) de EXIF si `+0xc0`≠0 |
| +0x40/+0x44 | handle y offset de miniatura (solo si `+0x80==0xa0` y `+0x84==0x78`, 160×120) |
| +0x1dc | handle screennail/miniatura alternativa (si ≠0 prevalece) |
| +0x68 | → `StillInfo+0x?` (tamaño) ; `+0x9c/+0xa0` ancho/alto |
| +0xa4 | orientación 1→6, 2→3, 3→8 |
| +0xac | fecha (→ `0x92e19e`); `+0xc1`/`+0xc4` fecha EXIF 10 B |
| +0xbe | hay datos de imagen; +0xc0 EXIF presente; +0xc2 flag; +0x164 variante con `+0x240/+0x27c/+0x2a0` |
| +0xd0 | puntero a bloque de metadatos |
Los JPEG de entrada **ya están codificados** (handles DMM de principal, EXIF, miniatura). Caso B: las auxiliares llegan preparadas; esta ruta no las genera (NO VERIFICADO quién las crea).

## Consecuencia para el diseño
`MakeWriteStillImage` = útil como **constructor de EXIF/contenedor JPEG** (ya soluciona EXIF + miniatura si le damos principal + miniatura codificados), pero **no** persiste en SD. Para guardar hay que seguir hasta `RecordStill 0x908afc → WriteStill` (ruta 0x1006) o encontrar otro consumidor del archivo en memoria. Arquitectura C pierde la ventaja "escritura incluida"; sigue siendo candidata solo si el consumidor de `+0x30..0x3c` acaba en DCF (NO VERIFICADO).

## Sesión 10: destino de GetFileImage y relación real con 0x1027

- VERIFICADO: el listener `param_1[0x13]` (`this+0x4c`) se crea en el constructor ELF `0x920c8c` (Ghidra `0x930c8c`) como `MWF::EventSender`, enlazado a un `EventReceiver` propio (`+0x50`, `GenerateEventId(0x145)`) y un `EventHandlerWrapper` (`+0x54`). El destino de respuesta es `this+0x58`, argumento del constructor. El objeto lo instancia `ObjConverter` en ELF `0x926eaa` (lo guarda en `parent+0x12c`, su sumidero es `parent+0x18`).
- VERIFICADO: `0x3a48` NO es específico de GetFileImage; es el `MWF::ObjMsg` de respuesta genérico que emiten muchos manejadores del módulo (≥30 `movw #0x3a48` en 0x91c…0x924…). Su consumidor es el solicitante del comando, no un grabador.
- VERIFICADO: la respuesta `ELF 0x921788` (traza 0xad) empaqueta handle/offset/tamaño (JPEG `0x1c` B, miniatura/EXIF/screennail `0x10` B) con `0x935870` y los devuelve al solicitante por `+0x58`. Campos del registro: `+0x30/+0x60/+0x70` = {u16 handle, u32 offset, u32 size}.
- VERIFICADO: solo si `this+0x5c` (= `MprCtrl::IsNetworkWriteTestMode`, que lee un dato EEP vía `BackupLib::GetEepDataEjhPv`) es distinto de 0, `ELF 0x921658` genera `%c%c%c%c%04d.JPG` y `ELF 0x9214d0` escribe el archivo con E/S cruda en `/dev/ms/` (log "Write Image"). No pasa por MPR/DCF.
- VERIFICADO (cadenas): ObjConverter lo usan `NetUpMain`/UPLDR ("deliverRequest to ObjConverter", `ExportInfoToObjConv`).
- CLASIFICACIÓN de GetFileImage: **TRANSFERENCIA** (export/subida), con volcado de depuración opcional a la SD. No es almacenamiento DCF.
- VERIFICADO: GetFileImage se invoca por la tabla de métodos con IDs locales `0x2000000x` (entrada `0x20000008`), no por `0x1027`.
- VERIFICADO: `0x1027` lo recibe ObjStillRecorder en `ELF 0x919ca0` (callback de estado 0x1002/0x3000/0x3001): lee el ticket `0x131f/0x1320`, fija `this+0x128 = 4`, inicia el anillo de buffers de `this+0xdc` (`0x91efb0`) y responde `0x3500` con ambos ítems.
- VERIFICADO: `RecordStill::Execute` (ELF `0x90b248`) lee `+0x128`: modos 0 y 4 ponen `param[0]=1` en la `WriteStillImageParam` (0xbc B); solo el modo 0 pone `[0x1d]=1`; los modos 2..6 ponen `[0x16]=1`. Es decir, recordStillImage reutiliza el mismo grabador nativo con un modo distinto.
- NO VERIFICADO: cómo obtiene Execute la imagen fuente en modo 4 (el ticket solo se devuelve; la fuente pasa por el anillo `+0xdc`) y si llega a `MprCtrl::WriteStill`.
- Otro llamador de `MakeWriteStillImage`: `ELF 0x93b8e8` (InfraStillPool, traza 0xb0), envoltorio mínimo; sus llamadores NO se han rastreado.

## Corrección sesión 11
- DESCARTADO (sesión 10): "0x1027 → ObjStillRecorder modo 4 → RecordStill::Execute reutiliza el grabador con imagen externa". `0x1027` solo arma el grabador y devuelve el ticket; `+0xDC` es `ObjStillRecorderMediaMgr`, no un anillo de imágenes. La imagen de `Execute` viene del Pool (RegisterImage). Ver `objstillrecorder-mode4.md`.
- VERIFICADO: la composición de `MakeWriteStillImage` (que GetFileImage usa para transferencia) es también el paso interno de `InfraStillPool::RegisterImage` (ELF `0x9328b4`), así que su salida (StillInfo 0x6B0) sí alimenta la grabación nativa, pero a través del Pool.
