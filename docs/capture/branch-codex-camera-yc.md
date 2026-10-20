# Rama B — YC de Camera, DMM/SDS y estabilidad

Alcance: Sony A6000 fw 3.21, análisis estático. Todas las direcciones son ELF; la VA de Ghidra es ELF + `0x10000`. No se conectó ni alteró hardware y los binarios se leyeron solamente.

## Veredicto

**NO VERIFICADO:** el `unitType` que entrega directamente `ObjCamera` durante EE/Live View. La topología de BootEE crea solo `{0x0a,0x07}`: `Camera(8).out0 -> Effect(9).in0 -> Renderer`; no existe una topología YC `Camera -> StillRecorder` recuperada. Por tanto, no es válido afirmar que el handle de un frame EE sea directamente una entrada de `EncodeStill`.

**VERIFICADO:** el productor que alimenta el pin YC del recorder en PbCap es `ObjEffect` salida 1 (topología `0x2a`, fila `libObj.so:0xcc4750`; creación `0x6135dc`). No reenvía el frame tal cual: reserva un par DMM nuevo, lo rellena por SDF y publica `PlayData`.

**INFERENCIA:** un frame EE puede convertirse en entrada válida si se ejecuta esa conversión nativa y se conserva el par producido hasta la finalización. La compatibilidad del buffer original de Camera permanece **NO VERIFICADA**: no se recuperaron su tipo, SDS, formato ni política de reciclaje.

## Productor y unidades PbCap verificadas

| Papel | unitType / extent | Tamaño | Evidencia | Estado |
|---|---:|---:|---|---|
| Raster `decBufferInfo` normal | `0x50b3f` / `0xed` | `0x3fc000` | `ObjEffect 0x15fa74` reserva en `this+0x60`; `0x15ebfc` publica `{handle +0x64, tipo 0x50b3f, phys +0x70}` en `0x1032`; ConfigData | VERIFICADO |
| Descriptor SDS `ycBufferInfo` | `0xe0b00` / `0xe4` | `0x800` | `0x15fa74` reserva en `this+0x78`; `0x15ebfc` publica `{handle +0x7c, tipo 0xe0b00, phys +0x88}` en `0x1018`; ConfigData | VERIFICADO |
| Raster alternativo super-resolución | `0x243` | no recuperado | `ObjEffect 0x15f37c` llama a la reserva con literal `0x243`; `0x15ebfc` lo selecciona si `+0xc4 != 0` | VERIFICADO valor; NO VERIFICADO semántica |
| Raster 640×480 | `0x220b2e` / `0x13d` | `0x96000` | helper `0x1704e4`; ConfigData | VERIFICADO |

La lectura de `ConfigData` es reproducible en [dmm-extent-sizes.json](../../analysis/dmm-extent-sizes.json): los registros de extent contienen `id` en `+0x08` y tamaño en `+0x0c`, coherente con las copias de `dmm_ext_tbl_Init` en `dmm.ko:0xedb4..0xedcc` y `0xd5bc..0xd5d8`.

`0xe0b00` no es un frame YC completo: su único extent mide exactamente `0x800`. Es el descriptor/cabecera SDS que acompaña al raster `0x50b3f` o `0x243`. Queda **DESCARTADO** identificar `0xe0b00` como el formato o el búfer de píxeles del visor.

## Cabecera SDS (`YcSdsAcsr`, 0x800 B)

`0x15ebfc` crea un accesador sobre `ycBufferInfo` con longitud `0x800`. El constructor `0x151b84` escribe, de forma verificable, `handle` en `+0x04` (u16), `unitType` en `+0x08`, dirección física en `+0x0c` y longitud de acceso en `+0x10`. Los accesadores `0x16ebe8` y `0x16ebf2` leen respectivamente colorimetría de `+0x14c` y rango Y de `+0x14d`; `0x15ebfc` los transfiere a `PlayData` `0x1072` y `0x1073`.

El resto de la estructura —en particular direcciones de planos, offsets, orden de componentes, submuestreo y stride— es **NO VERIFICADO**. La relación SDS→raster es observable en el par de descriptores publicado, pero la semántica interna del enlace es **NO VERIFICADA**.

## Geometría, formato y SDF

`ObjEffect 0x15fa74` calcula canvas `{align_up(w,64), align_up(h,16)}` por `0x156ac8` y región real `{w,h}`. `0x15ebfc` los publica como `0x1036` y `0x1038`; las mismas dimensiones se guardan en SDS como `0x1019`/`0x101a`. Esto es **VERIFICADO**.

Después de preparar los dos descriptores, `0x15fa74` emite `ObjMsg(0x3900,0x3000)` (resize/rotate SDF); `0x15f37c` es el camino de super-resolución. Así existe una operación nativa entre el origen de Effect y estas clases DMM: **VERIFICADO**. No constituye evidencia de que SDF acepte cualquier clase DMM: para el tipo real de Camera/EE es **NO VERIFICADO**.

`0x220b2e` tiene `0x96000 / (640×480) = 2` B/píxel, consistente con YC 4:2:2 empaquetado; orden de bytes, pitch y layout de planos son **INFERENCIA**, no una especificación recuperada. `0x50b3f` mide `0x3fc000`, 30 720 B por encima de `1920×1080×2`; tampoco permite deducir stride o planos.

## Contrato de EncodeStill

`ObjStillRecorder::Execute` (`0x90b248`) prepara el contrato en `0x90ad20`: toma `decBufferInfo` y `ycBufferInfo`, abre cada handle DMM, suma los extents y lo cierra. Construye `RegionInfo` de 0x40 B:

| Offset | Contenido | Estado |
|---:|---|---|
| `0x00..0x20` | `dec`: tipo, handle, física, offset 0, tamaño; fondo, layout, canvas y región | VERIFICADO |
| `0x24..0x34` | `yc`: tipo, handle, física, offset 0, tamaño | VERIFICADO |
| `0x38`, `0x3c` | rango Y y colorimetría | VERIFICADO |

La preparación valida presencia de ambos descriptores, que `DmmOpen` funcione, colorimetría `0..3` y rango Y `0..1`. No valida formato de píxel, stride, submuestreo, tamaño mínimo frente al canvas ni compatibilidad entre dos handles. Todo ello se sostiene en `0x90ad20` y en la copia literal de 16 palabras de `FeaIf::EncodeStill`, `libmpr.so:0x44f834`. Por tanto, la falta de validación no demuestra compatibilidad.

El receptor final recuperado es `FeaIf::EncodeStill` (`0x44f834`): reserva/valida una ranura por `this+4` vtable `+0x18`, copia `RegionInfo`, fecha, tamaños, metadatos y `JpgInfo`, y envía la cola por vtable `+0x20`. El retorno inmediato es `0`; el callback recuperado es `CBID_ENCODE_STILL`. **VERIFICADO:** la llamada es asíncrona. **NO VERIFICADO:** qué componente exacto consume la cola y cuándo comienza a leer cada byte.

## Propiedad, DmmShare y liberación

El recorder no adquiere una referencia de asignación sobre los buffers de entrada: en `0x90ad20` hace `DmmOpen`/`DmmClose` para los tamaños y no hace `DmmShare` ni `DmmFree` de `yc`/`dec`. `DmmClose` no libera: `dmm_unit_ctrl_Close` (`dmm.ko:0xa34c`, `0xa430..0xa458`) decrementa `open` en `unit+0x2a1`. **VERIFICADO.**

`DmmShare` en `dmm.ko:0x9c68` comprueba serial del handle (`0x9cb8..0x9cc4`), estado 1–3 (`0x9cd8..0x9ce8`) y tipo esperado (`unit+0x298`, `0x9cfc..0x9d08`), y sólo entonces incrementa `alloc` (`unit+0x2a0`, `0x9d1c..0x9d44`). `ObjScalar` usa `DmmCh::allocShare` mediante PLT ELF `0xdf49c` antes de guardar descriptores de cliente (`0x3eed34`): precedente **VERIFICADO** de retención por refcount.

Ese patrón protege frente a un `DmmFree` que respete `alloc`; no prueba que un anillo EE no recicle el contenido de una unidad por otra política. Para EE, esa garantía es **NO VERIFICADA**. La liberación segura sólo después de `CBID_ENCODE_STILL` es una **INFERENCIA** prudente: el retorno de `FeaIf` es demasiado temprano y no se recuperó una señal anterior de fin de lectura. Tampoco se recuperó la función/momento que libera el par `0x50b3f`/`0xe0b00` después del callback: **NO VERIFICADO**.

## Resultado para integración

1. No pasar el handle EE original directamente a `EncodeStill`: su tipo y contrato SDS no están recuperados, y su vida útil no está asegurada.
2. La ruta probada es crear el par raster + SDS de ObjEffect, completar SDF resize/rotate/super-resolución y publicar ambos descriptores en el `PlayData` del recorder.
3. Si se pretende retener una unidad ajena, `allocShare` debe recibir el tipo esperado y un handle vigente; aun así hay que demostrar que el productor EE honra el refcount. No basta con que el handle sea u16.
4. El productor debe conservar/cerrar la vida de ambos buffers hasta el callback `CBID_ENCODE_STILL`; `DmmClose` no sustituye esta retención.
