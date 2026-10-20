# S18 — SDF y transformación YC

Alcance: Sony ILCE-6000 fw 3.21, análisis estático exclusivo. No se ejecutó firmware ni se conectó o modificó una cámara. Direcciones ELF; las direcciones Ghidra equivalentes tienen un sesgo de `+0x10000`.

Binarios examinados:

| Fichero | SHA-256 |
|---|---|
| `libObj.so` | `8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a` |
| `libmpr.so` | `9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30` |

## Hallazgos

| Estado | Hallazgo | Evidencia estática |
|---|---|---|
| VERIFICADO | La ruta PbCap asociada a `Sequence 0x6013` no entrega el raster original: `ObjEffect` crea dos unidades DMM, raster `0x50b3f` y SDS `0xe0b00`, las prepara para SDF resize/rotate (o la alternativa de super-resolución) y después produce el `PlayData`. | `libObj.so`: `0x15fa74`, `0x15f37c`, `0x15ebfc`; reconstrucciones `analysis/ghidra/libobj-effect-writestill-16fa74.json`, `...-16f37c.json`, `...-16ebfc.json`. |
| VERIFICADO | La unidad `0xe0b00` usada aquí tiene una extensión de `0x800` B y es el SDS, no los píxeles. El raster normal es `0x50b3f`/`0x3fc000` B. | Trazas estáticas previas reproducibles: `analysis/branch-codex-yc-memory.json`, `analysis/yc-pin-delivery-flow.json`; constructor del accesor SDS en `0x151b84`, llamado desde `0x16ebfc` con longitud `0x800`. |
| VERIFICADO | El SDS contiene metadatos YC estructurados además de los dos bytes que esta ruta reenvía a EncodeStill. El constructor/mapeador `YcSdsAcsr` inicializa `ImageSizeInfo`, `YcStateInfo` e `ImageOutTimInfo`; intenta además `RightImageSizeInfo` y `DisplayInfo`. | `libObj.so` `0x151b84` llama a `0x151860`; este último recupera esas entradas. Las importaciones dinámicas nombran `C_DataflowInfra_StdData_YC::{Get,Set}Entry_*`. |
| VERIFICADO | La interfaz disponible para `ImageSizeInfo` contempla unidad DMM (tipo, handle y data offset), canvas, área válida, área destino, tamaño de registro, `DataPlacement`, `DataScan`, `StripWidth` y `YcCompress`. La de `YcStateInfo` contempla `Colorimetry`, `YRange`, `ChromaPhase` y `Scanline`. | Tabla `.dynsym` de `libObj.so`, símbolos `C_DataflowInfra_Entry_ImageSizeInfo::*` y `C_DataflowInfra_Entry_YcStateInfo::*`; las cadenas/ABI se conservan en el binario no strip de símbolos dinámicos. |
| VERIFICADO | Al construir el `PlayData`, `0x16ebfc` pone raster `{handle,tipo,phys}` en `0x1032`, SDS `{handle,tipo,phys}` en `0x1018`, geometría sin alinear en `0x1019/0x101a`, y sólo extrae del SDS `colorimetry` y `YRange` para `0x1072/0x1073`. El canvas se alinea a 64x16. | Decompilado de `analysis/ghidra/libobj-effect-writestill-16ebfc.json`; accesores `0x16ebe8` y `0x16ebf2`; `align_up` `0x156ac8`. |
| VERIFICADO | `ObjStillRecorder::Execute` abre/cierra descriptores para sumar extensiones y entrega un `RegionInfo` a `MprIf::EncodeStill`; `FeaIf::EncodeStill` copia el `RegionInfo` y lo encola, retornando sin esperar al codificador. | `libObj.so` `0x90ad20`, `0x90b248`; `libmpr.so` `0x44f834`; `analysis/encodestill-yc-contract.json` y `analysis/yc-pin-delivery-flow.json`. |
| VERIFICADO | El árbol OSS incluye un acelerador `mach-cxd90014/cmpr.c`, pero es un compresor LZPART genérico: usa `CMPR_LZPART_MAGIC` (`LZPT`) y operaciones `deflate`; mapea buffers físicos fuente/destino/trabajo y hace `dma_sync_single_for_device`. | `analysis/session18/main/sony-oss-extracted/linux/arch/arm/mach-cxd90014/cmpr.c:107-158,192-356`; `include/mach/cmpr.h:50,111-112`. |
| NO_VERIFICADO | Que el acelerador CMPR, la sincronización DMA que efectúa, o la configuración de caché PL310 se empleen por SDF, ObjCamera, FEA o el pipeline de captura. No hay referencia desde `libObj.so`/`libmpr.so` a ese driver ni una unión estática con DMM/SDS. | El CMPR pertenece al kernel OSS; `libObj.so` depende de `libmpr.so` y otras bibliotecas de espacio de usuario, no del driver por nombre. La coincidencia de plataforma no prueba uso. |
| NO_VERIFICADO | El orden de componentes, número de planos, submuestreo, pitch/stride y offsets de planos del raster YC real. | `RegionInfo` no transporta tales campos. Los métodos disponibles en SDS prueban capacidad de describir metadatos, pero no prueban sus valores/serialización en el par PbCap ni el formato del raster. |
| NO_VERIFICADO | Que el YC nativo de `ObjCamera` sea compatible con el par raster+SDS producido por SDF, o que el camino 0x6013 se active para Live View. | La cadena demostrada corresponde a PbCap/Player. No se recuperó tipo DMM ni cadena de descriptor de Camera hasta SDF/EncodeStill. |
| DESCARTADO | Identificar CMPR como acelerador JPEG/ISP o deducir desde él el formato YC de esta ruta. | Su código identifica LZPART, no JPEG/YUV; además falta una arista estática hacia la tubería propietaria. |

## Consecuencia para el contrato YC

La evidencia fortalece la separación entre **raster DMM** y **SDS DMM**: el SDS es un bloque de control mapeado físicamente de `0x800` B, y `YcSdsAcsr` lo interpreta mediante `DataflowInfra`. Por tanto, copiar sólo un descriptor `{handle, unitType, phys}` o sólo colorimetría/rango no reconstruye el contrato completo del productor.

Esto no identifica un formato YC concreto. En particular, los nombres `YcCompress`, `ChromaPhase`, `Scanline`, `DataPlacement`, `DataScan` y `StripWidth` prueban que la ABI tiene sitios para esa clase de metadatos, no que esta instancia use un valor determinado ni que el raster sea YUV 4:2:0, 4:2:2 u otro formato.

## Límites y conclusión

El kernel OSS confirma mecanismos genéricos de memoria física, DMA y caché, pero no contiene DMM, SDF, FEA, MPR ni un driver de sensor/ISP enlazable estáticamente a esta ruta. No aporta una prueba sobre el formato YC real ni sobre la vida útil de un buffer de Live View. La transformación comprobada sigue siendo la de PbCap: SDF produce un par nuevo raster+SDS antes de que `ObjStillRecorder` lo entregue asíncronamente a FEA.

No hay evidencia estática que permita afirmar que SilentShutter funcione.
