# Vida útil del buffer YC durante `EncodeStill` — sesión 14

> **Corrección S30:** FeaIf encola, pero MprAcsr espera `WaitEvent(-1)` en
> `0x8febd0`. La respuesta real `0x4000007c` lleva 12 bytes y el retorno del
> worker del encoder está resuelto hasta `0x71c8a8` y la señalización de
> `0xad38e8`. Execute continúa a Pool después de esa espera y su epílogo
> cierra/libera los handles `0x1018/0x1032`. Se retiran «no se localizó
> WaitEvent» y la inferencia de que Execute prosigue tras el mero encolado.
> Persisten las preguntas sobre caché y reciclaje del productor. [S30](s30-pipelines-capture-encode.md).

Alcance: estático. ELF (Ghidra = ELF + 0x10000). Decompilados: `analysis/ghidra/libmpr-feaif-encodestill.json`, `libobj-effect-*.json`, `libmpr-encodestill-onmemory-impl.json`; desensamblado de `kmod/dmm.ko`.

## Resultado

`EncodeStill` es **asíncrono** para quien llama y el recorder **no retiene** el YC de entrada. La unidad sobrevive solo mientras su **productor** mantenga la asignación DMM. Cuándo termina FEA de leer el buffer no está determinado estáticamente; la señal de fin es el callback `CBID_ENCODE_STILL`.

## Cadena (VERIFICADO salvo marca)

`ObjStillRecorder::Execute 0x90b248` → prep `0x90ad20` → `MprCtrl::EncodeStill 0x8fe6f8` → `MprIf::EncodeStill` → `MprIfLog::EncodeStill` (volcado) → `FeaIf::EncodeStill 0x44f834` (libmpr).

`FeaIf::EncodeStill`: reserva/valida un slot con `this+4` vtable `+0x18` (si falla → error 9), empaqueta RegionInfo (16 palabras), fecha (10 B), tamaños, `StillMetaAreaInfo` (24 B) y `JpgInfo`, y los **envía con `vtable+0x20` (id de comando, buffer, 4)**. A continuación `return 0` sin esperar respuesta. Por tanto la función vuelve **tras encolar**, no tras codificar.

Fin de operación: `[MprAcsr] eventId : [CBID_ENCODE_STILL]` y `[StillConverter] Receive CBID_ENCODE_STILL` (secuencia `StillConverter`: `AllocMemoryForEncodeStill` → `GetEncodeStillParam` → `PARAMID_CB_ENCODE_STILL`). INFERENCIA: Execute continúa (Pool, `RecordStill`) al recibir ese callback; no se localizó un `WaitEvent` bloqueante sobre EncodeStill.

Dónde corre el codificador: `FeaCore` de libmpr **no exporta `EncodeStill`** (sí `WriteStill`, `MakeWriteStillImage`, `PlayStillSingleByAddress`). libmpr contiene el controlador `StillEncoderDrv`/`StillEncoderIf[0..2]` con eventos `<Evt<StillEncoder(Encode) OK/NG` y `mb_cbFromStillEnc`: INFERENCIA de que FEA delega en él (motor SDF). NO VERIFICADO el destino de `this+4`.

## Respuestas

| Pregunta | Resultado | Estado |
|---|---|---|
| ¿Síncrona o asíncrona? | Asíncrona (encola y devuelve 0; fin por `CBID_ENCODE_STILL`) | VERIFICADO retorno; INFERENCIA fin |
| ¿Cuándo se copia/referencia la memoria YC? | Nunca por el recorder: pasa `{handle,unitType,phys}` (RegionInfo) y FEA los usa | VERIFICADO |
| ¿Cuándo empieza FEA a leer? | NO VERIFICADO (tras desencolar) | NO VERIFICADO |
| Señal de fin de lectura | `CBID_ENCODE_STILL` (callback del codificador) | VERIFICADO el nombre |
| ¿Cuándo es seguro liberar? | Tras `CBID_ENCODE_STILL` | INFERENCIA |
| ¿Qué función conserva las referencias? | Ninguna del recorder. `0x90ad20` hace `DmmOpen`+`DmmClose` solo para sumar extents; `DmmShare`/`DmmFree`/`CloseAndFree` aparecen en `0x90a810`, `0x90b248`, `0x90c088`, `0x911f68`, `0x912c04` sobre las **áreas de salida/Pool**. La unidad de entrada vive por la asignación del productor (ObjEffect: `DmmAllocate` en `0x15fa74/0x15f37c`) | VERIFICADO |
| ¿Qué hace `DmmClose`? | Decrementa el contador `open` (`+0x2a1`) de la unidad; **no libera** | VERIFICADO (`dmm_unit_ctrl_Close`) |
| ¿Qué hace `DmmFree`? | Decrementa `alloc` (`+0x2a0`) si >1; con `alloc`≤1 libera extents; si `rdv`≠0 pasa a estado 4 (liberación diferida) | VERIFICADO (`dmm_unit_ctrl_Free`) |
| ¿Refcount/pinning/copia? | Refcount por unidad: `alloc` (compartible con `DmmShare`/`DmmCh::allocShare`) y `open`. Copia: ObjEffect crea unidades dedicadas | VERIFICADO |
| ¿Timeout? | `FeaIf` no impone timeout (solo encola). Timeouts de DMM existen en las llamadas de alloc (`-1` = infinito en `0xebc0c`) | VERIFICADO parcial |
| ¿Execute bloquea hasta que el encoder acaba? | No en `FeaIf`; el fin llega por callback | INFERENCIA |

## Mecanismos existentes que mantienen un YC estable (priorizar sobre inventar)

1. **Copia dedicada de ObjEffect** (SDF resize/rotate a unidades `0x50b3f`/`0xe0b00`) — usada por PbCap. Estable hasta que ObjEffect la libere (momento NO VERIFICADO; existe `FreeRecMem` en el camino StillEdit).
2. **`DmmAccess::DmmShare` / `DmmCh::allocShare`**: toma una asignación compartida (+1 `alloc`). ObjScalar lo usa para retener handles de cliente (`0xdf49c`); el recorder lo usa sobre sus áreas de salida. Garantiza que un `Free` del productor no libere la unidad, **si el productor libera por `Free` (refcount) y no por reciclaje propio de su anillo**.
3. **LIRO `ycc_freeze` / `sds_ycc_freeze`** (SeqStillCap): congelado de buffers de captura; no aplica al visor.

## Riesgo para un YC de Live View

El anillo de EE es reciclado por el pipeline de la cámara (`PinSend` libera con `FUN_43b63566(handle,-1,-1)` tras enviar; sesión 13). Pasar ese handle a `EncodeStill` sin `DmmShare` ni copia puede dejar al motor leyendo un buffer reutilizado. NO VERIFICADO si las unidades EE respetan el refcount `alloc` o se reutilizan sin pasar por `Free`.

## NO VERIFICADO

Destino de `this+4` (FEA), instante exacto de lectura y de liberación de `0x50b3f/0xe0b00`, coherencia de caché CPU↔motor, manejo de error si la unidad desaparece durante la codificación.
