# S16 — YC de ObjCamera, contrato SDF/PbCap y límite estático

Alcance: firmware Sony A6000 3.21, análisis estático local exclusivamente. Direcciones son offsets ELF; en `libObj.so` y `libmpr.so`, offset de archivo = vaddr para `.text`/`.rodata`.

Binarios comprobados:

- `firmware/extracted/fw321/.../lib/libObj.so`
  SHA-256 `8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a`
- `.../lib/libmpr.so`
  SHA-256 `9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30`
- `.../kmod/dmm.ko`

## B1 — YC de Camera

| Hallazgo | Estado | Evidencia |
|---|---|---|
| `ObjCamera` es solamente el extremo de objeto/pines; no se recuperó en su constructor una asignación DMM, handle, dirección física, geometría ni formato del frame YC. | **VERIFICADO / NO VERIFICADO** | Constructor real `libObj.so:0x98c380`; topología `0x0a`, tabla `0xcc4210 + 0x0a*0x20`: Camera(objeto 8).out0 → Effect(objeto 9).in0. |
| El YC Camera#0 llega a `Effect.in0`; Camera no puede recibir `YcPinReqDeliver`. | **VERIFICADO** | Constructor crea nueve pines, todos salida; no existe pin de entrada Camera. |
| No hay evidencia estática de un puente desde ese YC Camera#0 al productor PbCap ni a `ObjStillRecorder`. | **NO VERIFICADO** | La única topología aún recuperada hacia recorder es `0x2a`: `Effect.out1 → Recorder.in0`, StsId 6. No se recuperó una activación que combine `0x0a` y `0x2a` para EE. |
| El `unitType`, handle DMM, física, tamaño, SDS, stride, orden Y/C y submuestreo del YC emitido por Camera#0 siguen desconocidos. | **NO VERIFICADO** | No se encontró escritura/lectura de esos campos atribuible a `ObjCamera` ni a la ruta Camera#0→Effect.in0. |
| No se pueden trasladar al YC Camera las dimensiones de registros de IMX210. | **DESCARTADO** | No existe una cadena estática sensor-register → descriptor YC Camera; los registros de sensor no describen por sí mismos raster, stride ni SDS del frame de pipeline. |
| La ruta SFRA/LIRO de pines EE/Rec es una infraestructura distinta; no prueba que sea el payload de `ObjCamera.out0`. | **DESCARTADO como identificación de Camera#0** | `docs/capture/sfra-electronic-frame-source.md` documenta `PinSend` LIRO `0x439abbfe`, mensaje `0x2009/0xb012` y liberación `FUN_43b63566(handle,-1,-1)`, pero no se recuperó un puente a la topología ObjCamera/Effect. |

Conclusión B1: el productor real detrás de `ObjCamera.out0` no está identificado estáticamente. Es incorrecto presentar un tipo DMM, formato YC, geometría o política de reciclaje como si fueran propiedades demostradas de Camera.

## B2 — Contraste con PbCap y SDF

### Unidades PbCap verificadas

| Unidad | Extent | Tamaño | Rol demostrado | Estado |
|---|---:|---:|---|---|
| `0x50b3f` | `0xed` | `0x3fc000` | raster/`decBufferInfo` dedicado de ObjEffect | **VERIFICADO** |
| `0xe0b00` | `0xe4` | `0x800` | cabecera/descripción SDS `YcSdsAcsr`; no raster | **VERIFICADO** |
| `0x220b2e` | `0x13d` | `0x96000` | raster auxiliar de 640×480 por helper de Effect | **VERIFICADO** para tamaño; layout no recuperado |

`ObjEffect` reserva el par PbCap en `libObj.so:0x15fa74`:

- raster `0x50b3f`;
- SDS `0xe0b00`;
- operación posterior `ObjMsg(0x3900, 0x3000)` de SDF resize/rotate;
- alternativa de super-resolución en `0x15f37c`.

El constructor de `PlayData` es `0x15ebfc`: publica `decBufferInfo` y `ycBufferInfo`; la SDS se abre con longitud `0x800`. El accesor `YcSdsAcsr` recupera colorimetría/rango Y en `+0x14c/+0x14d`, pero no se recuperó código que interprete bytes del raster como plano Y/C, packed 4:2:2, NV12, stride o pitches.

Por ello:

1. Que `0x96000 / (640*480) = 2` es consistente con 2 bytes/píxel, pero es solo **INFERENCIA**, no prueba de 4:2:2 ni de orden de bytes.
2. `0x3fc000` tampoco demuestra formato, stride ni área útil.
3. La ausencia de validación de formato en `ObjStillRecorder::Execute` no convierte cualquier DMM en entrada compatible.
4. La infraestructura SDF demostrada acepta el par construido por ObjEffect; que acepte el tipo desconocido del YC Camera/EE es **NO VERIFICADO**.

La conversión posible es una **HIPÓTESIS condicionada**: Camera→Effect debe producir, mediante una ruta SDF realmente alcanzable, un par nuevo `{raster compatible, SDS válida}` equivalente al PbCap. No hay prueba de que el frame Camera original pueda entrar directamente a `EncodeStill`.

## Evidencia de comandos

```sh
readelf -S libObj.so | rg '\.(text|rodata|data|rel.ro)'
readelf -S libmpr.so | rg '\.(text|rodata|data|rel.ro)'
llvm-objdump -d --triple=thumbv7-none-eabi \
  --start-address=0x90b0d0 --stop-address=0x90b1c8 libObj.so
strings -td libObj.so | rg -i 'SDS_YCC|STL_YCC|YcSdsAcsr|Receive CBID'
cat analysis/dmm-extent-sizes.json
```

No se realizó análisis dinámico, acceso a cámara, escritura de firmware ni inferencia funcional de SilentShutter.
