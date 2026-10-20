# S19-05 — ObjEffect, SDF y compatibilidad con Camera

Alcance: A6000 FW 3.21; análisis estático local, de solo lectura, sobre `libObj.so` SHA-256 `8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a`. Todas las direcciones son offsets ELF. Método principal: `llvm-objdump -d --triple=thumbv7-linux-gnueabi`. No se usó Ghidra, cámara ni firmware ejecutable.

## Veredicto

**S19-05: PARCIAL.** Hay evidencia positiva y completa de una operación SDF de la secuencia PbCap: la factory de `0x6013` crea el objeto correcto; su arranque exige holder/interfaz, conecta pines de infraestructura, reserva raster y SDS nuevos, envía la orden SDF y solo publica `PlayData` tras respuesta `0x111`. La finalización libera/cierra recursos según el estado. Sin embargo, no hay una arista estática que identifique ese holder, sus pines de infraestructura o su entrada SDF con `ObjCamera.out0 → ObjEffect.in0`. Por tanto no se verifican las precondiciones, DMM, geometría, formato ni vida útil del YC real de Camera frente a esta operación; **no se declara compatibilidad Camera→SDF→PbCap**.

## Ruta SDF efectivamente reconstruida

| Estado | Dirección, archivo, método | Hallazgo |
|---|---|---|
| **VERIFICADO** | `0x17b004..0x17b096`, `libObj.so`, `llvm-objdump` | La factoría compara `0x6013`, reserva `0xd4` B y llama al constructor `0x1761a8`. |
| **VERIFICADO** | `0x1761a8..0x176272`, `libObj.so`, `llvm-objdump` | El constructor instala su vptr, inicializa `+0x60..+0xac` para los descriptores de salida y crea el `ObjMsg(0x2001,0x1003)` almacenado en `+0xd0`. |
| **INFERENCIA** | `0x15fd50`, `libObj.so`, cadenas y layout contrastados con `0x1761a8` | Es el `BeginExecCommand` de `SequencePinDeliverExecWriteStillCmd`; el nombre exacto del slot virtual no se recuperó. |
| **VERIFICADO** | `0x15fd96..0x15fe88`, `libObj.so`, `llvm-objdump` | Requiere holder `this+0x14`, interfaz `this+0x8` y retorno no nulo del selector virtual 12; consulta selector 3 y conecta la infraestructura antes de saltar a la reserva normal. Ninguna de estas guardas inspecciona `unitType`. |
| **VERIFICADO** | `0x15f290..0x15f352`, `libObj.so`, `llvm-objdump` | `DataflowInfraCh::infraConnectPin` une dos extremos de infraestructura construidos localmente; la instrucción no identifica ningún `ObjCamera` ni descriptor Camera. |
| **VERIFICADO** | `0x15fa74..0x15fc94`, `libObj.so`, `llvm-objdump` | Crea `DmmCh(0x35)`, reserva primero `0x50b3f` y luego `0xe0b00`, prepara descriptores y remite `ObjMsg(0x3900,0x3000)` por la interfaz en `this+8`. Éstos son buffers de salida SDF, no prueba del buffer de entrada. |
| **VERIFICADO** | `0x15f9a0..0x15fa58`, `libObj.so`, `llvm-objdump` | La preparación de comando obtiene el CID virtual del holder, usa `ConvertCid`/`ConvertCmdMid` y adjunta una estructura `0x44` como parámetro `0xe001`; confirma que el SDF queda dirigido a un endpoint configurado por el holder. No decodifica la fuente YC. |
| **VERIFICADO** | `0x15f634..0x15f79c` y `0x15f928..0x15f956`, `libObj.so`, `llvm-objdump` | Ante completado/cleanup, desconecta infraestructura y cierra unidades de la rama normal (`+0x64`, `+0x7c`); con estado 1/2 despacha la continuación correspondiente. Esto es evidencia de gestión de salida, no de ownership de Camera. |
| **VERIFICADO** | `0x15ebfc..0x15f126`, `libObj.so`, `llvm-objdump` | Solo con resultado `0x111` forma `PlayData (0x2001,0x1003)`: selecciona el par normal o super-resolución, consulta dimensiones del holder, alinea canvas a 64×16 y publica raster/SDS, región, dimensiones, colorimetría y rango Y por el pin 7. |
| **VERIFICADO** | `0x15fac8`, `0x15fb1e`; `analysis/dmm-extent-sizes.json`, LLVM + extracción DMM previa | Salida normal: raster `unitType 0x50b3f`, extent `0xed`, `0x3fc000` B; SDS `unitType 0xe0b00`, extent `0xe4`, `0x800` B. La SDS es metadato/control, no píxeles. |

## Evaluación requerida: Camera contra la ruta SDF

| Requisito de compatibilidad | Estado | Evidencia o límite |
|---|---|---|
| Alcanzar la factory/ejecutar esta secuencia desde Camera | **NO_VERIFICADO** | La factory de `0x6013` y el método de arranque están reconstruidos, pero no hay caller/activación recuperada desde `ObjCamera` o la topología `0x0a`. |
| Holder `this+0x14`, interfaz `this+0x8`, selector 12 | **NO_VERIFICADO** para Camera | Son precondiciones reales de la secuencia, pero el contrato de Camera de S19-04 no materializa ese holder ni sus retornos. |
| Selección de pines SDF | **VERIFICADO** para PbCap / **NO_VERIFICADO** para Camera | `0x15f290` conecta extremos `DataflowInfra`, pero no expone `ObjCamera.out0` ni prueba que sea una entrada SDF. |
| Tipos DMM, handles, offsets y física de Camera | **NO_VERIFICADO** | SDF asigna sus propias salidas `0x50b3f` y `0xe0b00`; no lee ni valida un descriptor Camera en esta ruta. La ausencia de comparación no acredita aceptación del YC Camera. |
| Resolución/canvas | **VERIFICADO** para salida PbCap / **NO_VERIFICADO** para Camera | El selector 3 del holder produce clase y `0x15ebfc` alinea canvas; no hay identificación del selector/valor desde Camera. |
| Entrega a PbCap | **VERIFICADO** para salida SDF | Tras `0x111`, `0x15ebfc` emite PlayData con los buffers producidos. No demuestra que el raster proceda de Camera. |
| Vida útil | **VERIFICADO** parcialmente para recursos de la secuencia / **NO_VERIFICADO** para Camera | `0x15f634` desconecta y cierra las unidades de salida según el estado; no localiza el dueño ni el reciclaje del buffer fuente Camera, ni el liberador final tras FEA. |
| Compatibilidad completa Camera→SDF→PbCap | **NO_VERIFICADO** | Faltan identidad del holder, operación SDF que consuma Camera, contrato de entrada y ciclo de vida end-to-end. |

## Límites y descartes

- **DESCARTADO**: concluir compatibilidad porque `0x15fd50` no compara `unitType`. Ese método solo verifica disponibilidad del holder/SDF; la implementación virtual y la identidad de la entrada siguen fuera de la evidencia.
- **DESCARTADO**: tratar `0xe0b00`/`0x800` como raster de Camera. Es la SDS de salida de PbCap.
- **HIPOTESIS**: si un holder de la ruta `Camera.out0 → Effect.in0` implementase los selectores, pines y contrato SDF de esta secuencia, la ruta podría producir buffers PbCap. No hay evidencia estática de esa identidad ni de su ejecución.

SilentShutter no se declara funcional.
