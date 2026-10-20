# S16 — FEA `EncodeStill`: encolado, callback y vida de buffers

Alcance: análisis estático A6000 3.21. Direcciones ELF; desensamblado Thumb real con `llvm-objdump`.

## Cadena recuperada

| Tramo | Estado | Evidencia |
|---|---|---|
| `ObjStillRecorder::Execute` prepara `EncodeStillParam` y llama a `MprCtrl::EncodeStill`. | **VERIFICADO** | `libObj.so:0x90b14c..0x90b18a`; `bl 0x8fe6f8`. |
| `MprIf::EncodeStill(EncodeStillParam*)` registra y salta al `FeaIf` configurado. | **VERIFICADO** | `libmpr.so:0x71cf58..0x71cf72`: carga `this->m_feaIf`, pasa el parámetro y hace tail-call indirecta por PLT. |
| `FeaIf::EncodeStill` comprueba/reserva una ranura del objeto `this+4`, copia el payload y llama una vtable de envío. | **VERIFICADO** | `libmpr.so:0x44f834..0x44f8da`. |
| El retorno correcto de `FeaIf::EncodeStill` significa "solicitud encolada", no "JPEG terminado". | **VERIFICADO** | Éxito: `0x44f8ca..0x44f8d8` llama `vtable+0x20`; `0x44f8da` devuelve `r4=0`. No hay espera ni lectura de resultado. |
| El componente semánticamente identificado que recibe `CBID_ENCODE_STILL` es `StillConverter`. | **INFERENCIA fuerte** | Cadenas reales de `libObj.so`: `Receive CBID_ENCODE_STILL`, `StillConverter::PARAMID_CB_ENCODE_STILL`, `send StillConverter::MSGID_CONVERT_JPG_CMP`. No se recuperó todavía la entrada que registra el callback ni el objeto `this` concreto. |
| `MprIfCallbackPoint` despacha el callback registrado y después notifica por código de evento. | **VERIFICADO** | `libmpr.so:0x4502e8..0x450322`; invoca puntero de callback en `0x450308`; si el ID está en intervalo, llama al notificador `0x449ed8`. |
| Que ese despacho concreto sea `CBID_ENCODE_STILL` en todas las rutas no está enlazado por xref recuperada. | **NO VERIFICADO** | Falta recuperar registro de callback y valor numérico del CBID. |

## Bytes y desensamblado decisivos

### `MprIf::EncodeStill`

`libmpr.so:0x71cf58`:

```asm
71cf60: c903          ldm     r1, {r0, r1}
71cf62: 69a2          ldr     r2, [r4, #0x18]
71cf64: 69e3          ldr     r3, [r4, #0x1c]
71cf66: f601 e696     blx     MprIfLog::EncodeStill@plt
71cf6a: 6828          ldr     r0, [r5]
71cf6c: 4621          mov     r1, r4
71cf72: f600 b787     b.w     FeaIf::EncodeStill@plt
```

### `FeaIf::EncodeStill`

Bytes iniciales reales:

```text
44f834: f0 b5 05 46 a1 b0 0c 46 29 49 00 af fa f7 a0 fa
```

Éxito y error:

```asm
44f844: 6868          ldr     r0, [r5, #0x4]
44f848: 6803          ldr     r3, [r0]
44f84a: 699b          ldr     r3, [r3, #0x18] ; reservar/validar slot
44f84c: 4798          blx     r3
44f84e: b948          cbnz    r0, 0x44f864 ; éxito

; fallo de reserva:
44f850: 4824          ldr     r0, [pc, #0x90] ; 0x4000007c
44f852: 2109          movs    r1, #9
44f854: f4ce eb04     blx     MprIfLog::AsyncApiDone@plt
44f860: 2009          movs    r0, #9
44f862: e03b          b       retorno

; éxito: copia 0x40 B RegionInfo desde *param:
44f864..44f880: cuatro bloques ldm/stm de 16 B
44f884..44f88c: memcpy de fecha, 10 B
44f890..44f8c4: copia tamaños, meta y JpgInfo
44f8ca: 6868          ldr     r0, [r5, #0x4]
44f8d0: 4904          ldr     r1, [pc, #0x10] ; 0x4000007c
44f8d4: 6a1d          ldr     r5, [r3, #0x20] ; vtable + 0x20
44f8d6: 2304          movs    r3, #4
44f8d8: 47a8          blx     r5             ; envío
44f8da: 4620          mov     r0, r4         ; r4 = 0
```

## Propiedad y liberación

| Pregunta | Resultado | Estado |
|---|---|---|
| ¿`DmmClose` libera el raster? | No; reduce `open` (`unit+0x2a1`). | **VERIFICADO**: `dmm.ko:0xa34c`, tramo `0xa430..0xa458`. |
| ¿El recorder toma `DmmShare` de entradas YC/dec? | No en la preparación recuperada; abre/cierra para sumar extents. | **VERIFICADO**: `libObj.so:0x90ad20` y preparación de `Execute`. |
| ¿Qué protege `allocShare`? | Tras validar serial, estado y tipo esperado, incrementa `unit+0x2a0`. | **VERIFICADO**: `dmm.ko:0x9c68..0x9d44`. |
| ¿Puede el `allocShare` impedir reciclaje de un anillo Camera/EE? | No demostrado. | **NO VERIFICADO**. |
| ¿Cuándo libera ObjEffect `0x50b3f`/`0xe0b00` tras EncodeStill? | No recuperado. | **NO VERIFICADO**. |
| ¿Es prudente mantener la copia PbCap hasta `CBID_ENCODE_STILL`? | Sí, pero es una condición de seguridad inferida, no una prueba de implementación. | **INFERENCIA**. |
| ¿Hay cancelación/error FEA identificada? | Error inmediato si no hay slot: retorno `9`; no se recuperó una ruta de cancelación específica de EncodeStill ni una liberación posterior asociada. | **VERIFICADO** para error 9; **NO VERIFICADO** para cancelación/liberación. |

## Veredicto

El parámetro pasa por referencia de handles/phys en `RegionInfo`; FEA copia la estructura descriptiva, no el raster. Por tanto, el retorno `0` de `FeaIf::EncodeStill` solo certifica envío exitoso de una solicitud. No prueba que FEA ya haya leído el YC ni que sea seguro liberar o reciclar la unidad.

El candidato de consumidor de completitud es `StillConverter`, respaldado por las cadenas de callback presentes en `libObj.so`. Falta una xref estática directa que una el registro de callback, el valor numérico `CBID_ENCODE_STILL`, el objeto `StillConverter` y la liberación de los buffers ObjEffect.

## Comandos ejecutados

```sh
llvm-objdump -d --triple=thumbv7-none-eabi \
  --start-address=0x90b0d0 --stop-address=0x90b1c8 libObj.so

llvm-objdump -d --triple=thumbv7-none-eabi \
  --start-address=0x71cf58 --stop-address=0x71cfb4 libmpr.so

llvm-objdump -d --triple=thumbv7-none-eabi \
  --start-address=0x44f834 --stop-address=0x44f8e8 libmpr.so

llvm-objdump -d --triple=thumbv7-none-eabi \
  --start-address=0x4502e8 --stop-address=0x450324 libmpr.so

xxd -g1 -s $((0x44f834)) -l 180 libmpr.so
strings -td libObj.so | rg 'Receive CBID_ENCODE_STILL|CBID_ENCODE_STILL|StillConverter'
```
