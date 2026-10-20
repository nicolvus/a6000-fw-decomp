# S19-06 — receptor de completitud `CBID_ENCODE_STILL`

## Veredicto

**PARCIAL.** Se verificó el conducto real de registro y distribución genérica: `MprCtrl::Init` registra un callback MPR; `FeaIf::MprIfCallbackPoint` lo invoca y, para IDs `0xc0000001..0xc0000091`, emite además la notificación interna. `EventSwitcher` distribuye entradas por `targetId` y `eventId`. No se recuperó la entrada que asocia `0xc0000004` con el objeto/método de `StillConverter`; por tanto el receptor final sigue **NO_VERIFICADO**.

| Hallazgo | Estado | Evidencia estática |
|---|---|---|
| Registro global de callback MPR | **VERIFICADO** | `libmprctrl.so:0x11b96..0x11ba2` llama a `MprIf::SetCallbackFunc(fn,target,context)` tras crear/inicializar MprIf. `libmprctrl.so` es el único importador de ambas sobrecargas. Método: `llvm-nm -D`, relocaciones y `llvm-objdump`. |
| API con identificador de media | **VERIFICADO** | `libmpr.so:0x71f7b8..0x71f7e8` reordena `(mediaId,fn,target,context)` y llama a FEA `0x450418`; el destino rechaza `mediaId==0` antes de delegar. Método: `llvm-objdump`. |
| Despacho de callback | **VERIFICADO** | `libmpr.so:0x4502e8..0x450308` resuelve e invoca el callback; `0x45030a..0x450318` acepta exactamente el rango inclusivo `0xc0000001..0xc0000091` y notifica. Método: `llvm-objdump`. |
| Distribución hacia receptores | **VERIFICADO** | `libmprctrl.so:0x1c88a..0x1c90c` recorre `EventSwitcher`; compara `targetId` (o comodín 0) y `eventId`, luego llama la entrada. `AddCallbackFunc` copia `count*0x10` bytes (`0x1c792..0x1c7e2`). Método: `llvm-objdump`. |
| `0xc0000004 == CBID_ENCODE_STILL` | **INFERENCIA fuerte** | Literal presente en `libmpr.so` (incluido offset/VA `0x759748`); cadenas de `libObj.so` nombran `CBID_ENCODE_STILL` y `StillConverter::PARAMID_CB_ENCODE_STILL`. No hay asociación código/literal/nombre recuperada. |
| `StillConverter` es receptor final | **NO_VERIFICADO** | Las cadenas `Receive CBID_ENCODE_STILL`, `EncodeJpgCmp`, `ConvertJpg Canceled` y liberación de memoria existen en `libObj.so`, pero no se halló el `AddCallbackFunc` cuya tabla contenga el ID candidato ni una arista registro→instancia. |
| Éxito de `EncodeStill` significa finalización | **DESCARTADO** | `libmpr.so:0x44f84c..0x44f8da`: reserva slot por vtable `+0x18`; ante fallo devuelve `9`; copia el descriptor y entrega por vtable `+0x20`, luego devuelve `0`. No espera callback, lectura ni JPEG. |
| Copia de píxeles por FEA | **NO_VERIFICADO** | `0x44f864..0x44f880` copia solo 16 palabras (`0x40` B) de `RegionInfo`; los píxeles no aparecen en la copia. Esto prueba copia de descriptor, no copia ni retención del raster. |
| Última lectura de píxeles | **NO_VERIFICADO** | El dispatcher de callback no constituye barrera de DMA/caché ni expone una marca de lectura. Retener hasta callback es sólo una **INFERENCIA** conservadora. |
| Cancelación ligada a EncodeStill | **NO_VERIFICADO** | Se observan `CancelPlayStill*` y la cadena `ConvertJpg Canceled`, pero no una arista desde una cancelación a esta solicitud ni su efecto sobre el raster. |
| Liberación de fuente/copia | **NO_VERIFICADO** | `MprIf::ReleaseMemSubArea` existe (`0x71cef4`), pero no se enlazó a esta operación. Tampoco se enlazaron `FreeJpgCnvMemInfo`/`FreeCnvMsg` de StillConverter al descriptor de entrada. `DmmClose` no puede asumirse como liberador de la fuente. |

## Implicación de vida útil

El retorno `0` de `EncodeStill` certifica solamente que FEA aceptó/encoló una solicitud. No certifica codificación, lectura completa, cancelación, escritura ni liberación. La relación `StillConverter`↔`CBID_ENCODE_STILL` sigue siendo una hipótesis de arquitectura respaldada por cadenas, no una arista estática demostrada. SilentShutter no se declara funcional.

## Método reproducible

```sh
llvm-nm -D --demangle libmpr.so
llvm-readelf -rW libmprctrl.so
llvm-objdump -d --triple=thumbv7-linux-gnueabi \
  --start-address=0x44f834 --stop-address=0x44f8e8 libmpr.so
llvm-objdump -d --triple=thumbv7-linux-gnueabi \
  --start-address=0x4502e8 --stop-address=0x450324 libmpr.so
llvm-objdump -d --triple=thumbv7-linux-gnueabi \
  --start-address=0x11b8c --stop-address=0x11bae libmprctrl.so
llvm-objdump -d --triple=thumbv7-linux-gnueabi \
  --start-address=0x1c792 --stop-address=0x1c90c libmprctrl.so
```
