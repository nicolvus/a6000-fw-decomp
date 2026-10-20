# S17 — FEA: callback, vida del raster y cierre hacia DCF

Alcance: firmware ILCE-6000 3.21, análisis estático de `libmpr.so`, `libObj.so`
y `dmm.ko`. Direcciones ELF. No se probó hardware ni se afirma que exista una
fotografía electrónica funcional.

## Respuesta a las once preguntas

| # | Resultado | Clasificación y evidencia |
|---|---|---|
| 1 | La API de registro es `MprIf::SetCallbackFunc`, `libmpr.so:0x71f7b8`; pasa `(eventId, fn, targetId, context)` a `FeaIf` por `0x450418`. No se recuperó el llamador/registro concreto de `CBID_ENCODE_STILL` en `libObj.so`. | **VERIFICADO** API/destino; **NO VERIFICADO** sitio concreto. |
| 2 | `StillConverter` es el receptor semántico candidato: cadenas locales `Receive CBID_ENCODE_STILL`, `StillConverter::PARAMID_CB_ENCODE_STILL` y `EncodeJpgCmp`. No hay xref de código que una el registro con ese método. `ObjStillRecorder` no quedó probado como receptor directo. | **INFERENCIA fuerte**; receptor real **NO VERIFICADO**. |
| 3 | El identificador en la familia callback es `0xc0000004`: literal en `libmpr.so:0x759748`, comparado por código MPR de prueba junto a las rutas de still. El despachador acepta el intervalo `0xc0000001..0xc0000091`. Falta la asociación simbólica directa literal→nombre `CBID_ENCODE_STILL`; por tanto, el valor de nombre se conserva como inferencia fuerte, no hecho final. | **INFERENCIA fuerte** (valor); rango **VERIFICADO** (`0x45030a..0x450318`). |
| 4 | `ObjStillRecorder::Execute` construye `EncodeStillParam` y llama `MprCtrl::EncodeStill` (`libObj.so:0x90b14c..0x90b18a`). El retorno `0` de FEA sólo confirma encolado. No se localizó una espera ni una respuesta `ObjStillRecorder` ligada al callback. | **VERIFICADO** llamada/semántica de retorno; respuesta posterior **NO VERIFICADO**. |
| 5 | No hay punto estático recuperado que marque la última lectura de raster. `FeaIf::EncodeStill` copia sólo el descriptor `RegionInfo` (0x40 B) y metadatos a pila/cola, después entrega por vtable `+0x20`, `libmpr.so:0x44f864..0x44f8d8`. | **VERIFICADO** que el retorno no marca lectura completa; instante exacto **NO VERIFICADO**. |
| 6 | No se identificó la función que libera las unidades fuente de ObjEffect (`0x50b3f`/`0xe0b00`) tras EncodeStill. `DmmClose` no lo hace: sólo reduce `unit+0x2a1`, `dmm.ko:0xa430..0xa458`. | **VERIFICADO** para `DmmClose`; liberador original **NO VERIFICADO**. |
| 7 | Tampoco se identificó el liberador de la copia SDF. `libObj.so` contiene `SequencePinRequestDeliverStillEditBase::FreeRecMem()` y `DmmCh::freeSdsAndYc`, pero esta sesión no demuestra su alcance sobre la copia que llega a EncodeStill. | **VERIFICADO** presencia de símbolos/cadenas; atribución a la copia SDF **NO VERIFICADO**. |
| 8 | No. El callback demuestra entrega de una notificación, no una barrera de DMA, caché, ni liberación DMM. Es una condición conservadora razonable mantener el raster hasta `CBID_ENCODE_STILL`, pero la garantía de reciclaje no está recuperada. | **INFERENCIA** para retener hasta callback; garantía **NO VERIFICADO**. |
| 9 | Al no haber slot, `FeaIf::EncodeStill` llama `AsyncApiDone(...,9)`, notifica internamente y retorna `9` (`0x44f84e..0x44f862`). Se halló la cadena `ConvertJpg Canceled` y liberaciones de memorias del convertidor, pero no una ruta de cancelación enlazada a esta solicitud ni sus efectos sobre buffers ObjEffect. | Error inmediato **VERIFICADO**; cancelación/asíncrono posterior **NO VERIFICADO**. |
| 10 | No hay camino estático comprobado desde completitud de `EncodeStill` a `WriteStill` y confirmación MPR. `FeaIf::WriteStill` existe (`0x44f784`) y su propio envío es asíncrono; `FeaCore::WriteStill` prepara la operación (`0x440794`), pero no se recuperó una arista desde `StillConverter::EncodeJpgCmp`/callback al recorder. | Tramos aislados **VERIFICADOS**; cadena completa **NO VERIFICADA**. |
| 11 | Para aparecer en reproducción no basta crear JPEG: debe completar el flujo MPR de `WriteStill`/MMgr con `entryId` y datos de ruta, y actualizar el catálogo DCF. El firmware contiene esas estructuras y mensajes de `WriteStillCmp`; CIPA DC-009 define DCF 2.0. La secuencia concreta desde EncodeStill no está unida estáticamente. | Requisito arquitectónico **INFERENCIA fuerte**; implementación concreta **NO VERIFICADA**. |

## Evidencia decisiva

### Envío y callback

`MprIf::EncodeStill` (`0x71cf58`) hace tail-call a `FeaIf::EncodeStill`
(`0x44f834`). Ésta reserva el slot con vtable `+0x18`; si falla, retorna 9.
En éxito copia `RegionInfo` y campos asociados (`0x44f864..0x44f8c4`) y ejecuta
la vtable `+0x20` (`0x44f8ca..0x44f8d8`). No espera una lectura ni un JPEG.

`FeaIf::MprIfCallbackPoint` (`0x4502e8`) llama primero la función de callback
recibida indirectamente (`0x450308`) y, para un ID dentro del intervalo
`0xc0000001..0xc0000091`, llama después al notificador (`0x450314..0x450318`).
Esto prueba orden de despacho/notificación, no qué recurso deja de usar FEA.

La única evidencia numérica localizada asociada a esta familia en el código MPR
es el literal `0xc0000004` en `0x759748`; está consumido por código de prueba
MPR (`0x75963c..0x75964c`). No se lo promociona a vínculo simbólico probado.

### DMM

`dmm_unit_ctrl_Share` (`dmm.ko:0x9c68`) valida índice, serial, estado/tipo y
comparación de propietario; sólo entonces incrementa `unit+0x2a0` en
`0x9d1c..0x9d44`. `dmm_unit_ctrl_Close` decrementa `unit+0x2a1` en
`0xa430..0xa458`. No se encontró aquí una prueba de que un anillo de Camera/EE
respete `alloc`, ni una operación de caché/DMA que haga el callback una barrera.

## Implicación para Codex C (SDF/YC)

El raster no puede considerarse reciclable en el retorno `0` de EncodeStill.
La regla segura provisional es retener original y copia SDF hasta recibir
`CBID_ENCODE_STILL`, pero sigue siendo **INFERENCIA**, no contrato recuperado:
se requiere localizar la función de callback y la liberación DMM/ObjEffect.

## Contexto externo delimitado

El portal de Sony para ILCE-6000 publica paquetes GPL, incluido un
`linux-kernel.tar.gz`; no se usó como evidencia de la implementación propietaria
de FEA/DMM. CIPA lista `DC-009-2010`, *Design rule for Camera File system: DCF
Version 2.0*, confirmado en 2020: valida el marco DCF, no la ruta interna Sony.

Fuentes: [Sony OSS ILCE-6000](https://oss.sony.net/Products/Linux/DI/ILCE-6000.html),
[CIPA DC-009](https://www.cipa.jp/e/std/std-sec.html).

