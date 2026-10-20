# S17 — Codex C: Sequence `0x6013`, SDF y contrato YC

Alcance: firmware A6000 3.21, análisis estático. Direcciones son ELF salvo que se indique Ghidra VA (= ELF + `0x10000`). No se ejecutó firmware ni hardware.

## Corrección de direccionamiento

La dirección que en Ghidra aparece como `0x1861a8` corresponde a **ELF `0x1761a8`**, no a ELF `0x1861a8`. La instrucción de la factoría es `0x17b08e: bl 0x1761a8`; el desensamblado de `0x1761a8` comienza `bl SequenceBase::SequenceBase`, instala el vptr y retorna el objeto. **VERIFICADO**.

## Cadena demostrada

`0x17b004` compara `0x6013` en `0x17b01e..0x17b024`, reserva `0xd4` en `0x17b086..0x17b08c` y llama al constructor en `0x17b08e`. El constructor `0x1761a8` llama a `SequenceBase::C2` (`0x1761b0`), escribe el vptr en `[this]` (`0x1761c8`), inicializa `this+0x6c` y `this+0x78` a `0xffff`, y el resto de los pares handle/física a cero (`0x176206..0x176250`). El puntero de vtable almacenado es `ELF 0x0db3cc` (la carga PIC en `0x1761ac..0x1761c8` resuelve la base `0x0db3c4` y suma 8). **VERIFICADO** para el valor instalado; nombre RTTI de la clase, **NO VERIFICADO**.

El método de arranque recuperado es `ELF 0x15fd50` (texto de diagnóstico: `SequencePinDeliverExecWriteStillCmd`). Es compatible con ese layout: usa `+0x60/+0x78` para los resultados normales y `+0x90/+0xa8` para super-resolución, exactamente los offsets inicializados por el constructor. Esto identifica el `BeginExecCommand` de la familia con evidencia de layout y cadenas, pero la relación slot-de-vtable→nombre `BeginExecCommand` no quedó reconstruida por símbolo C++; se clasifica **INFERENCIA fuerte**.

## Condiciones de entrada reales

Antes de iniciar SDF, `0x15fd50` impone tres guardas:

1. `ldr r5,[r4,#0x14]; cbnz r5,0x15fdd2` (`0x15fd96..0x15fd98`): estado/holder de entrada no nulo.
2. `ldr r6,[r4,#0x8]; cbnz r6,0x15fe18` (`0x15fdd2..0x15fdd4`): interfaz de SDF/VDF no nula.
3. llamada virtual de ese holder con selector `12` (`movs r1,#12; ldr r3,[vtable,#0x3c]; blx r3`, `0x15fe18..0x15fe20`) debe devolver no-cero; se guarda en `this+0xc0` y si es cero falla (`0x15fe22..0x15fe60`).

Después consulta el selector 3 del mismo holder (`0x15fe62..0x15fe6a`) para elegir el flag de super-resolución (`this+0xc4`) y conecta los pines en `0x15f290`; solo entonces salta a `0x15fa74`. **VERIFICADO**. No hay comparación de `unitType` de Camera ni de formato YC en este Begin: la validación visible es disponibilidad del holder/infraestructura y retorno de su selector 12. **VERIFICADO para ausencia dentro de `0x15fd50`; NO VERIFICADO en la implementación virtual del holder o SDF.**

## SDF, geometría y PlayData

En la vía normal `0x15fa74`, `DmmCh::allocNew` recibe `this+0x60` y el tipo `0x50b3f`, luego `this+0x78` y `0xe0b00`; prepara el descriptor SDS con handle `+0x7c`, física `+0x88`, longitud de allocation y el descriptor raster con handle `+0x64`, tipo `0x50b3f` (`0x15fa74`, decompilado). Construye `ObjMsg(0x3900,0x3000)` y lo entrega por la interfaz de `this+8`; al éxito fija estado `+0x58=1`. **VERIFICADO**.

La geometría proviene del selector virtual 3 del holder: `0x15fa74` llama `holder->vtable[0x3c](holder,3)` y `0x15e1f8`; alinea ancho a 64 y alto a 16 mediante `0x156ac8`, pero conserva ancho/alto sin alinear para región. El mapeo recuperado de clase de tamaño es `0→640×360`, `1→640×480`, `2→1920×1080`. **VERIFICADO**. No son dimensiones inferidas desde el sensor.

`0x15f37c` es la alternativa: reserva raster tipo `0x243` y SDS `0xe0b00`; no prueba que `0x243` sea un formato YC concreto. `0x15f290` conecta los canales de datos para SDF/VDF; `0x15f634` ejecuta la desconexión/cierre posterior y la espera del flujo. **VERIFICADO para control de canales y allocations; NO VERIFICADO el formato de píxel.**

Tras la finalización que llega con resultado `0x111`, `0x15ebfc` construye el `ObjMsg(0x2001,0x1003)` PlayData. Publica raster como parámetro `0x1032`, canvas `0x1036`, región `0x1038`, SDS/YC como `0x1018`, dimensiones YC como `0x1019/0x101a`, colorimetría y rango como `0x1072/0x1073`, y envía por el pin 7 (`0x15ebfc`). **VERIFICADO**. El texto recuperado de la clase menciona `stateSdfResizeRotateComp`; por tanto `CMD_ID_SDF_RESIZE_ROTATE_CMP`/estado SDF-completo es el evento que habilita esta fase. **INFERENCIA fuerte**: la transición exacta del dispatcher a la llamada `0x15ebfc` no fue reconstruida como arista directa.

## Respuestas solicitadas

| # | Respuesta | Estado |
|---:|---|---|
| 1 | Vptr real instalado por el constructor: `ELF 0x0db3cc`; constructor ELF `0x1761a8` (Ghidra `0x1861a8`). | VERIFICADO |
| 2 | `0x15fd50`, `SequencePinDeliverExecWriteStillCmd`, es el BeginExecCommand por layout y cadena; slot exacto no resuelto. | INFERENCIA fuerte |
| 3 | De `this+0x14`: requiere holder y obtiene selector 12 y geometría por selector 3. | VERIFICADO |
| 4 | La secuencia SDF PbCap encaja con el objeto `0xd4` de `0x6013` (mismo layout/strings), pero no hay arista factoría→slot virtual recuperada. | INFERENCIA fuerte |
| 5 | Puede aceptar Camera solo si Camera→Effect materializa el holder/contrato que satisfaga esas guardas; no hay prueba de ello. | NO VERIFICADO |
| 6 | No compara unitType en `0x15fd50`; sí reserva sus propios tipos de salida `0x50b3f`+`0xe0b00` o `0x243`+`0xe0b00`. | VERIFICADO / límite señalado |
| 7 | Selector 3 del holder determina clase/tamaño; se alinea canvas a 64×16 y región queda sin alinear. | VERIFICADO |
| 8 | SDF recibe descriptor raster DMM y descriptor SDS DMM recién asignados, más canvas/región y `ObjMsg(0x3900,0x3000)`; no recibe una cabecera SDS como píxeles. | VERIFICADO |
| 9 | Produce raster DMM dedicado y SDS de 0x800 B, publicados como PlayData. | VERIFICADO |
| 10 | `CMD_ID_SDF_RESIZE_ROTATE_CMP`/estado `stateSdfResizeRotateComp` es el completado identificado; arista exacta al callback, pendiente. | INFERENCIA fuerte |
| 11 | Sólo tras resultado `0x111`: `0x15ebfc` crea y emite PlayData. | VERIFICADO |
| 12 | Necesita dos unidades DMM de salida: raster y SDS; normal `0x50b3f`+`0xe0b00`, alternativa `0x243`+`0xe0b00`. | VERIFICADO |
| 13 | No: el productor real Camera no fue seguido hasta un descriptor, por lo que su unitType sigue desconocido. | NO VERIFICADO |
| 14 | Hay conversión nativa PbCap→raster dedicado vía SDF; Camera-YC→esa ruta no está demostrada. | VERIFICADO / NO VERIFICADO |

## Separación de conceptos

- **Raster DMM:** `0x50b3f`, extent `0xed`, `0x3fc000` B; alternativa auxiliar conocida `0x220b2e`, extent `0x13d`, `0x96000` B. Tamaño no define formato/pitch/planos.
- **Cabecera SDS:** `0xe0b00`, extent `0xe4`, exactamente `0x800` B; contiene descriptor/metadatos YC, no píxeles.
- **Descriptor/handle:** el PlayData transporta `unitType`, handle y dirección física; no equivale al contenido del raster.
- **Geometría:** selector 3, canvas alineado y región son campos distintos; no se deriva de IMX210.
- **Reutilización:** Recorder abre/cierra para extents y no demuestra `DmmShare` ni política de reciclaje del productor; retener hasta `CBID_ENCODE_STILL` es sólo una inferencia de seguridad.

Conclusión: existe una ruta estática PbCap que construye PlayData compatible, pero no una prueba de que Camera suministre el tipo/descriptor requerido ni de que SDF acepte su YC original. Esto no demuestra SilentShutter.
