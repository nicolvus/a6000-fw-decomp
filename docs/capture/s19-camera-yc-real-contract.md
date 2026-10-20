# S19-04 — contrato YC real de ObjCamera

Alcance: A6000 FW 3.21, análisis estático local y de solo lectura de `libObj.so` (SHA-256 `8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a`). Direcciones: offsets ELF. Método principal: `llvm-objdump -d --triple=thumbv7-linux-gnueabi`. No se usó cámara ni se modificó ningún binario.

## Resultado

**S19-04: PARCIAL.** Se verificó que la construcción de `ObjCamera` no crea ni abre una superficie DMM/`AvbbcPhycMem`; crea nueve pines de salida y auxiliares de eventos/recursos. La superficie DMM concreta que sí se puede reconstruir sigue perteneciendo a `ObjEffect`/PbCap. No hay arista estática Camera.out0 → esa asignación, por lo que no es lícito promover su descriptor como el YC real de Live View.

| Campo solicitado para Camera.out0 | Estado | Evidencia/límite |
|---|---|---|
| productor/topología | **VERIFICADO** | Constructor `0x98c380`; fila `0x0a` de `0xcc4210`: ObjId 8 Camera.out0 → ObjId 9 Effect.in0. |
| nueve salidas | **VERIFICADO** | Auxiliar `0x987dc6` construye nueve `MWF::ObjPin` con dirección de salida; posiciones `this+0x58..0x78`. |
| unitType | **NO_VERIFICADO** | Ninguna llamada `DmmCh::allocNew/allocShare/open/getUnitInfo` en el constructor ni una arista Camera.out0 hacia una de ellas. |
| handle DMM y offset | **NO_VERIFICADO** | No se materializa descriptor DMM ni `DmmAccessPLA::GetUnitHandle*` atribuible a Camera. |
| memoria física | **NO_VERIFICADO** | `AvbbcPhycMem::GetLogAddr` aparece en otras rutas; no hay llamada desde Camera. Además, `GetLogAddr` nombra dirección lógica, no demuestra dirección física/DMA. |
| geometría, formato, stride y planos | **NO_VERIFICADO** | Camera no carga esos campos; la geometría/formatos no se derivaron de IMX210. |
| colorimetría | **NO_VERIFICADO** | La SDS de Effect expone colorimetría/rango Y, pero no está enlazada al payload Camera. |
| ownership/reciclaje | **NO_VERIFICADO** | No se encontró `allocShare/open/close/free/freeSdsAndYc` en una ruta atribuible a Camera.out0. |

## Evidencia directa

| Estado | Dirección, archivo, método | Hallazgo |
|---|---|---|
| **VERIFICADO** | `libObj.so:0x959bdc..0x959bf0`, `llvm-objdump` | `ObjCamera_Create` reserva `0x20c` y llama al constructor `0x98c380`. |
| **VERIFICADO** | `libObj.so:0x98c380..0x98c4d8`, `llvm-objdump` | El constructor inicializa estado, locks, hilo/recursos y llama auxiliares `0x987788`, `0x987d6c`, `0x987dc6`, `0x9880a4`; en este intervalo no hay llamada a DMM ni `AvbbcPhycMem`. |
| **VERIFICADO** | `libObj.so:0x987dc6..0x987fb0`, `llvm-objdump` | Se reservan nueve objetos `MWF::ObjPin` de `0x40` B, se almacenan en `this+0x58..0x78`, y cada constructor recibe dirección `1` (salida). |
| **VERIFICADO** | `libObj.so:0xcc4210 + 0x0a*0x20`, lectura de `.rodata` previamente contrastada y trazado de pines | Topología `0x0a`: Camera.out0 → Effect.in0. Esto prueba conectividad declarada, no el contrato de memoria del mensaje. |
| **VERIFICADO** | `libObj.so:0x15fa74..0x15fc94`, `llvm-objdump` | Ruta de Effect/PbCap construye `DmmCh(0x35)` y ejecuta dos `allocNew`; después prepara `ObjMsg(0x3900,0x3000)`. Es una superficie propietaria DMM verificable, pero no un caller de `ObjCamera`. |
| **VERIFICADO** | `analysis/dmm-extent-sizes.json`; `libObj.so:0x15fac8`, `0x15fb1e` | Las dos reservas PbCap conocidas son raster `unitType 0x50b3f`, extent `0xed`, `0x3fc000` B, y SDS `unitType 0xe0b00`, extent `0xe4`, `0x800` B. La SDS es control, no raster. |
| **VERIFICADO** | `libObj.so` PLT/relocaciones, `readelf -Wr` y `llvm-objdump` | Las APIs disponibles incluyen `DmmCh::{allocNew,allocShare,open,close,free,freeSdsAndYc,getUnitInfo}` y `DmmAccessPLA::{GetExtAdrs*,GetExtSize*,GetExtCount*,GetUnitHandle*}`. Su presencia no identifica el descriptor Camera. |
| **DESCARTADO** | Comparación de rutas anterior, método estático | Inferir dimensión/tamaño YC Camera desde registros IMX210. No existe cadena sensor-registro → descriptor Camera. |
| **DESCARTADO** | `0x15fa74..0x15fc94`, método estático | Etiquetar `0xe0b00`/`0x800` como raster YC: es la cabecera SDS de la ruta Effect/PbCap. |
| **INFERENCIA** | Separación de callers anterior | Si Camera.out0 llegase a alimentar la conversión PbCap, Effect podría crear un par DMM posterior; eso no prueba que el frame de Camera posea esos unitTypes ni que sea compatible. |

## Límite técnico y siguiente paso

La relación verificable llega a `Camera.out0 → Effect.in0`. Falta localizar el método de Effect que consume ese pin durante Live View y, dentro de esa misma cadena, un descriptor real pasado a `DmmCh` o `DmmAccessPLA`. Hasta entonces los valores de unitType, handle, offset, dirección física, geometría, formato, stride, planos, colorimetría, ownership y reciclaje del YC de Camera son **NO_VERIFICADOS**.

SilentShutter no se declara funcional.
