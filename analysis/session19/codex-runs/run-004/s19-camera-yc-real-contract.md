# S19-04 — contrato YC real de ObjCamera (copia de ejecución)

Fuente canónica: `docs/capture/s19-camera-yc-real-contract.md`. A6000 FW 3.21, análisis estático local y de solo lectura de `libObj.so` (SHA-256 `8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a`). Direcciones: offsets ELF. Método: `llvm-objdump -d --triple=thumbv7-linux-gnueabi`.

**S19-04: PARCIAL.** La construcción de `ObjCamera` no crea ni abre una superficie DMM/`AvbbcPhycMem`; crea nueve pines de salida y auxiliares. La superficie DMM concreta reconstruible pertenece a `ObjEffect`/PbCap. No existe arista estática Camera.out0 → esa asignación; no se puede promover su descriptor como YC Live View de Camera.

| Campo Camera.out0 | Estado |
|---|---|
| productor/topología | **VERIFICADO**: `0x98c380`; fila `0x0a`: ObjId 8 Camera.out0 → ObjId 9 Effect.in0. |
| nueve salidas | **VERIFICADO**: `0x987dc6`, `this+0x58..0x78`. |
| unitType, handle, offset, memoria física, geometría, formato, stride, planos, colorimetría, ownership, reciclaje | **NO_VERIFICADO**: no hay llamada/cadena Camera atribuible a DMM o Avbbc. |

| Estado | Dirección, archivo, método | Hallazgo |
|---|---|---|
| **VERIFICADO** | `libObj.so:0x959bdc..0x959bf0`, `llvm-objdump` | `ObjCamera_Create` reserva `0x20c` y llama `0x98c380`. |
| **VERIFICADO** | `libObj.so:0x98c380..0x98c4d8`, `llvm-objdump` | Constructor sin llamadas DMM/DmmAccessPLA/AvbbcPhycMem. |
| **VERIFICADO** | `libObj.so:0x987dc6..0x987fb0`, `llvm-objdump` | Nueve `MWF::ObjPin` de salida. |
| **VERIFICADO** | `libObj.so:0x15fa74..0x15fc94`, `llvm-objdump` | Effect/PbCap construye `DmmCh(0x35)`, dos `allocNew` y `ObjMsg(0x3900,0x3000)`; no es caller de Camera. |
| **VERIFICADO** | `0x15fac8; 0x15fb1e`, más `analysis/dmm-extent-sizes.json` | Par PbCap: raster `0x50b3f`/`0xed`/`0x3fc000`; SDS `0xe0b00`/`0xe4`/`0x800`. SDS no es raster. |
| **DESCARTADO** | Ruta estática | Inferir geometría/tamaño Camera desde IMX210. |
| **INFERENCIA** | Rutas separadas | Effect podría crear un par posterior compatible, pero ni alcanzabilidad ni identidad con Camera se probaron. |

SilentShutter no se declara funcional.
