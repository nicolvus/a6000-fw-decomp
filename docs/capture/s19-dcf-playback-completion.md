# S19-08 — MPR/DCF: escritura y catálogo de reproducción

Análisis estático de A6000 fw 3.21; se inspeccionó `libmpr.so` en modo solo lectura con `llvm-nm -D`, `strings -t x` y `llvm-objdump -d --triple=thumbv7-linux-gnueabi`. Las direcciones son VA ELF. No se ejecutó firmware ni se conectó cámara.

## Resultado

**PARCIAL.** La ruta alcanza la API asíncrona `FeaIf::WriteStill` y existe una abstracción MPR que delega `WriteAndFlush` a un gestor de medio. También existen APIs DCF síncronas de pre-registro, consulta por directorio/número y reproducción/miniaturas. Esto demuestra capacidades separadas, pero no una arista estática que pruebe que una escritura concreta complete el alta DCF ni que invalide/actualice el catálogo que consume reproducción.

| Estado distinto | Evidencia | Límite |
|---|---|---|
| JPEG válido | `StillInfo` transporta `mainData`, EXIF, thumbnail y screennail; el constructor de imagen prepara esas áreas. | No se validó el JPEG final ni la lectura completa de píxeles tras `EncodeStill`.
| Escritura en SD | `MprFileIfCore::WriteAndFlush` valida handle/buffer/out-count y despacha por vtable del gestor de medio. | No se identificó el gestor concreto, la ruta SD montada, ni un call-site desde el escritor de still.
| Registro DCF | `MprIf::PreRegisterDcfContentSync` y `GetEntryIdFromDirectoryFileNumberSync` son APIs reales. | No se demostró que `WriteStill` las llame, ni el commit/rollback de un registro de esta fotografía.
| Visible en reproducción | APIs de conteo, directorios, `ReadThumbnail`, `PlayThumbnail` y `EnterThumbnailPb` existen. | No se siguió un consumidor del `ObjMsg 0x3500/0x3002` ni una invalidación/recarga de catálogo causada por WriteStill.

## Cadena recuperada

1. **VERIFICADO — `libmpr.so:0x44f834`, método: objdump.** `FeaIf::EncodeStill` copia el descriptor de `RegionInfo` y lo entrega de forma asíncrona; su retorno no espera JPEG ni escritura. El receptor concreto permanece **NO_VERIFICADO** (S19-06).
2. **VERIFICADO — `libObj.so:0x908afc`, método: evidencia estática previa corroborada.** `RecordStill` prepara `WriteStillParam` y llama a `MprCtrl::WriteStill` (`0x8fe0a0`), que alcanza MPR. El wrapper construye la solicitud, pero no acredita que el writer la complete.
3. **VERIFICADO — `libmpr.so:0x44f784`, método: objdump.** `FeaIf::WriteStill` valida `WriteStillParam`, sólo admite uno o dos elementos, empaqueta 0x90 bytes y los entrega por llamada virtual. Es una admisión/encolado, no una confirmación de archivo, DCF o reproducción.
4. **VERIFICADO — `libmpr.so:0x4507b6` (entrada interna FeaCore, identificada por el flujo de `0x44f784` y evidencia previa), método: objdump/Ghidra previo corroborado.** La implementación comprueba estado, writer disponible, identificador de grabación no nulo y línea activa. `WriteStillParam+0x18` es identificador de grabación, no handle DMM.
5. **VERIFICADO — `libmpr.so:0x38b064` y `0x37af44`, método: evidencia de desensamblado previa.** La construcción de still lee las áreas `mainReserve`, `mainData`, `thumJpg` y `screenNail`; reserva espacio EXIF/miniatura y rechaza reserva insuficiente. `WriteDcfMemory` coloca EXIF y miniatura antes del JPEG. Esto no verifica que el resultado llegue al medio.
6. **VERIFICADO — `libmpr.so:0x726138`, método: objdump.** `MprFileIfCore::WriteAndFlush(handle, buffer, size, outCount)` exige sus tres punteros, inicializa `*outCount=0`, encuentra el `MMgr` dueño y llama su slot virtual `+0x290`; propaga el resultado. La confirmación es la que devuelva el gestor, no la del wrapper.

## DCF, numeración, EXIF y derivados

- **VERIFICADO — `libmpr.so:0x71eafc`, método: objdump.** `MprIf::PreRegisterDcfContentSync` llama una operación interna síncrona con `T_LTM`, `DcfObjInfo`, números de directorio/archivo y salidas; prueba un mecanismo DCF de pre-registro, no su uso desde `WriteStill`.
- **VERIFICADO — `libmpr.so:0x71eb70`, método: objdump.** `GetEntryIdFromDirectoryFileNumberSync` consulta un `EntryId` por números de directorio/archivo y tipo/condición de contenido. Junto con las cadenas `\\DCIM\\%3ldMSDCF\\DSC0%04ld.JPG`, prueba que MPR modela la numeración DCF, no cuál número asigna esta captura ni que el archivo exista.
- **VERIFICADO — `libmpr.so:0x38b064`/`0x37af44`, método: evidencia previa; y `0x3b2f60`, método: evidencia previa.** EXIF, thumbnail y screennail son áreas diferenciadas. Para EXIF nuevo, la rama normal exige miniatura; screennail de tamaño cero tiene rama consumidora. **NO_VERIFICADO:** etiquetas EXIF mínimas, JPEG válido del thumbnail, y presencia de screennail para aceptación extremo a extremo.
- **DESCARTADO — método: contraste de flujo.** Tener un JPEG principal válido, un retorno cero de `EncodeStill`, o una cadena `DSC0%04ld.JPG` no demuestra escritura SD, registro DCF ni visibilidad en reproducción.

## Confirmación, errores y cancelación

**VERIFICADO — `libmpr.so:0x44f6a4`, método: objdump.** Existe `FeaIf::FlushWriteStill`, que empaqueta una operación de 0x0c bytes y la entrega por la misma interfaz asíncrona. Su retorno inmediato se fija a cero después de la entrega; no se observó espera por respuesta ni relación demostrada con `MprFileIfCore::WriteAndFlush`.

**VERIFICADO — `libmpr.so:0x726138`, método: objdump.** El wrapper de archivo puede devolver error por argumento nulo o por el gestor. **NO_VERIFICADO:** códigos de error del writer DCF, orden entre flush/close/registro, `fsync`/`fdatasync` por still, borrado del archivo parcial, liberación DMM o compensación de pre-registro.

**NO_VERIFICADO.** No apareció un `CancelWriteStill` exportado ni una arista desde los `Cancel*` exportados al estado de esta operación. La cancelación de reproducción/miniaturas no debe atribuirse a grabación.

## Catálogo de reproducción

**VERIFICADO — símbolos exportados, método: `llvm-nm -D`.** `GetContentsCountSync`, `GetDcfDirectoryCount`, `GetDcfDirectoryName`, `GetDcfFileInfo`, `GetDcfObjectInfo`, `ReadThumbnail`, `PlayThumbnail` y `EnterThumbnailPb` están implementados en MPR. Son evidencia de una capa de catálogo/reproducción que consulta DCF.

**NO_VERIFICADO.** No se localizó el DCFStillWriter nominal como símbolo exportado, su tabla virtual concreta, ni una llamada que conecte `WriteStill` con `RegisterDCFContent`/`PreRegisterDcfContentSync`, `GetContentsCount*` o el receptor final de `0x3500/0x3002`. Por ello tampoco se verifica una fotografía visible en reproducción.

## Veredicto

No declarar SilentShutter funcional. La cadena conocida llega a una admisión asíncrona de escritura y MPR posee primitivas independientes de archivo, DCF y reproducción; falta la arista de finalización que una las cuatro condiciones. Siguiente tarea propuesta: identificar la implementación/vtable que recibe el paquete de 0x90 B de `FeaIf::WriteStill`, y desde allí rastrear pre-registro, escritura/flush, resultado, rollback y publicación de `EntryId`.
