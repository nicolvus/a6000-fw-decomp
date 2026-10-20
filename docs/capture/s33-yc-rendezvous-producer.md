# S33 — productor de referencias YC y frontera Rendezvous (18-10-2026)

Continuación de [S32](s32-vd-callbacks-sync-ycout.md), exclusivamente estática.
`av-cam.bin`, base lógica `0x43541000`, SHA-256
`b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.
Proyecto `analysis/ghidra/silent-liro.gpr`, siempre `-readOnly -noanalysis`.
No se ejecutó firmware, no hubo cámara, modificaciones del binario ni guardado
del proyecto. Las definiciones temporales se revirtieron mediante transacción.

## Resultado

**VERIFICADO:** el productor inmediato es un conjunto de trabajos `Image` que
construyen un parámetro local de **0x104 bytes** y pasan a SyncYCout un puntero
a un `MemoryHandle`. Varias rutas obtienen ese handle mediante **AllocRendezvous**.
El bloque YC transmite **ID DMM y clave de asignación**, no una dirección raster
demostrada: su palabra `+4` procede del argumento solicitado a AllocRendezvous,
no de una dirección devuelta por el proveedor.

**PARCIAL:** esto cierra el productor de la referencia compartida, pero no el
productor físico que llena la memoria. No se ha recuperado el backend de la
llamada DMM importada, un pitch inequívoco ni una condición de fin DMA del YC.

Exports íntegros, con instrucciones, llamadas y xrefs:

- [`s33-initial.json`](../../analysis/ghidra/s33-initial.json) / `.c`: funciones objetivo.
- [`s33-callers.json`](../../analysis/ghidra/s33-callers.json) / `.c`: los doce productores completos.
- [`s33-memory.json`](../../analysis/ghidra/s33-memory.json),
  [`s33-protocol.json`](../../analysis/ghidra/s33-protocol.json): memoria y comandos DMM.
- [`s33-final.json`](../../analysis/ghidra/s33-final.json) /
  [`s33-final.c`](../../analysis/ghidra/s33-final.c): AllocShare completo y entrada HS correcta.
- `s33-scope`, `s33-workobjects`, `s33-execution`, `s33-adapters`, `s33-frontier`,
  `s33-boundaries`, `s33-queue`, `s33-input-helper`, `s33-apl`,
  `s33-secondary-flag`, `s33-dma`, `s33-mmio`, todos bajo
  `analysis/ghidra/`, en JSON y pseudocódigo `.c`.
- [`s33-audit.json`](../../analysis/ghidra/s33-audit.json): los 29 callsites,
  las trece instancias locales, sus asignaciones y hashes persistentes.

## VERIFICADO — contrato AllocShare, sin confundir identificador con dirección

`0x4390366c(dst,src,open,unit)` devuelve **estado**, no un puntero.
`0x43ae9674(src)` comprueba únicamente `s16(src+0) != -1`.
Después llama a `0x43902df8(u32(src+4),s16(src),open,reply,unit)`.
En éxito construye el siguiente objeto de 0x28 bytes:

| Offset | Contenido comprobado | Límite semántico |
|---|---|---|
| `+0` | ID de 16 bits devuelto en `reply+4` | Handle DMM, no dirección raster |
| `+2` | byte de `reply+8`, limitado a cuatro | Log `ERR_EXTENT_SIZE`; número de pares/extents |
| `+3` | 1 en éxito | Estado de referencia; no flag DMA |
| `+4` | copia de `src+4` | Clave de origen preservada, no un mapeo devuelto |
| `+8..+0x27` | hasta cuatro pares de palabras desde `reply+0x10` | No se han identificado como planos, pitch o pares físico/lógico |

`0x43902df8` borra una solicitud de `0x78` bytes, coloca comando **2**,
ID fuente, clave fuente, `open`, identificador **0x55**, longitud **0x70** y
unidad en los 16 bits altos de la cabecera. La pasa a `0x43561524`.
Valida estado de respuesta cero, comando **0x8002**, identificador **0x55** e
ID diferente de `0xffff`. Si `open==1`, exige además campos no nulos en
`reply+8` y `reply+0x10`; en éxito copia **0x70 bytes** al destino de respuesta.
Los errores distinguen `ERR_DMM_HANDLE`, `ERR_DMM_OPEN`, retorno y comando.
Los relojes opcionales que rodean la llamada miden duración del servicio;
no son espera de transferencia ni inspección de DMA.

En los dos callsites de `0x4379b44c`, `open=0`, `unit=5`.
Por tanto **esta ruta no pide abrir/mapping CPU** ni obliga a que haya un
primer extent no nulo. Copiar los pares no acredita que sean direcciones
efectivas, ni identifica tamaño/pitch. La palabra llevada a `YC+4` es
`handle+4`, mientras que `YC+8` es el nuevo ID corto.

**Frontera precisa:** `0x43561524` llama a
`*(*(base+0x14)+0x2e4)`, donde el slot `0x440205c0` contiene `0x43541000`.
El puntero de tabla inicial en `base+0x14` es `0x435410b4`; su entrada
`0x43541398` contiene **cero en el archivo**. Se necesita la resolución del
proveedor/importación en carga; cero no es un destino ejecutable válido.
Análogamente, `0x43561604` usa `tabla+0x308`, inicialmente cero en
`0x435413bc`. No se inventa una llamada a una implementación Dmm concreta.

### Comparación con S30

La consulta SDF `0x436519c0` acepta la misma pareja estructural
`u16(handle+0)` / `u32(handle+4)` y devuelve una lista de pares;
`0x43651694` cierra por ID. Ambos se reexportaron en `s33-memory`.
En [S30](s30-pipelines-capture-encode.md), `DmmCloseAndFree(0xdc180)`
pertenece a **libObj.so**, no a la base lógica de este blob.

**INFERENCIA:** es compatible con la misma familia de contratos DMM:
identificador, contexto/clave y operaciones de abrir/compartir/cerrar.
**NO_VERIFICADO:** identidad del buffer con los parámetros `0x1018/0x1032`
de EncodeStill, equivalencia de tipos C originales o llamada directa desde
esta cadena al PLT `0xdc180`. No son aristas demostradas.

## VERIFICADO — quién construye y escribe input

Barrido de bytes originales: **26 BL** a `0x4379b44c`, **1 BL** a
`0x43796954` y **2 BL** a `0x4379bb90`; todos contrastados con instrucciones
exportadas. No hay punteros absolutos pares/Thumb a esos tres destinos en el
barrido del exportador. Alcance: instrucciones BL/B.W alineadas a media
palabra y punteros absolutos; no garantiza ausencia de llamadas calculadas.

Cada una de las trece instancias de `input` de los doce llamadores recuperados
se inicializa con `0x43b03a5e`, que ejecuta `memset(input,0,0x104)`.
Cada llamador escribe explícitamente `input+0xc8=0` y después el puntero
primario `input+0x10`. **`input+0xd4` empieza en cero, pero puede cambiar**:
hay un escritor indirecto importante, `0x43814ea0`, llamado desde tres
productores. No basta buscar asignaciones directas en cada función padre.

**VERIFICADO — escritor secundario:** `0x43814ea0(P,...,input,...)` usa
el byte `cStack_83`, generado por `0x4387a1fc` en la respuesta auxiliar.
Si es cero, escribe `input+0xc8=0`. Si no lo es, escribe `input+0xc8=1`
y **`input+0xd4=P+0xbc`**. Instrucciones decisivas:
`0x43815192 STRB [r5,#0xc8]`, `0x4381519c STR [r5,#0xd4]`;
`r5=input` y `r4` ya contiene `P+0xbc` en ese último store.
Callsites del helper: **0x4355164a**, **0x435536be**, **0x435557de**.
`0x435525c0` además copia 0x104 bytes de `iStack_4a4` a `iStack_5a8`,
propagando también estos campos. Las otras nueve funciones no presentan
ese helper ni otro uso de la dirección del input fuera de constructor/publicación.
El valor efectivo del flag depende del resultado auxiliar; no se afirma que
la rama secundaria se active en todo modo ni todo frame.

En la tabla, `P=*image` se obtiene con `0x43ae75dc(image)`; este getter
devuelve simplemente la primera palabra del objeto `Image`.
Los nombres de locales son los del pseudocódigo exportado, no tipos Sony.

| Función productora | `input` local | Escritura de `input+0x10` | Calls a `0x4379b44c` |
|---|---|---|---|
| `0x43549380` | `uStack_2b4` | `P+0x1c` (`iVar15`) | `0x43549b48` |
| `0x43549e48` | `iStack_1c8` | `P+0x1c` | `0x4354a50a` |
| `0x4354b750` | `uStack_12c` | `P+0x1c` | `0x4354bc90` |
| `0x4354c0e0` | `uStack_138` | `P+0x1c`, dos construcciones | `0x4354c3fc`, `0x4354c5aa` |
| `0x4354c6d0` | `uStack_184` | `P+0x1c` (`iVar11`) | `0x4354ccb0`, `0x4354ccb8` |
| `0x4354cec0` | `uStack_290` | `P+0x1c` | `0x4354d662` |
| `0x4354d740` | `uStack_234` | `P+0x1c` | `0x4354e370` |
| `0x4354ea98` | `uStack_3e0` | `P+0x1c` (`iVar10`) | `0x4354f6c6`, `0x4354f6dc` |
| `0x4354fad8` | `uStack_198` | `P+0x1c` (`iVar12`) | `0x435502e0`, `0x435502e8` |
| `0x435503b0` | `uStack_4f0` | `P+0x44` | `0x435516fc`, `0x43551718`, `0x4355203c`, `0x43552054` |
| `0x435525c0` | `iStack_5a8`, `iStack_4a4` | primero `P+0x44`; también `P+0x1c` y `P+0x15c` según rama | `0x4355376a`, `0x43553776`, `0x43553792`, `0x4355413e`, `0x43554156` |
| `0x43554590` | `uStack_414` | `P+0x44` o `P+0x1c` según construcción | `0x4355588a`, `0x435558a6`, `0x43556060`, `0x43556078` |

**VERIFICADO — fuente de los handles:** `0x439035e0` registra
`MemoryHandle::AllocRendezvous`; usa `0x43902c2c` (comando **0x0c**,
respuesta **0x800c**) y forma el mismo objeto de 0x28 bytes. Escribe
`handle+4=argumento solicitado`, antes de copiar los extents.
Para `P+0x1c`, varias rutas pasan `P+0x18c` como clave; para `P+0x44`,
`P+0x194`. Ejemplos completos: `0x43549380`, `0x43549e48`,
`0x4354fad8`, `0x435503b0`, `0x435525c0`, `0x43554590`.
`0x4354c6d0` obtiene además `P+0x15c` con clave **0x293**.
No todos los trabajos reasignan el handle: algunas ramas reutilizan el
contenido que ya lleva `P`.

El handle secundario **`P+0xbc`** también se obtiene por AllocRendezvous:
en `0x435503b0`, `0x435525c0`, `0x43554590` sus llamadas usan claves
condicionales conservadas en los exports. No se confunde este handle con
el primario `P+0x1c/+0x44` ni con la bandera que habilita compartirlo.

**VERIFICADO — flag auxiliar de configuración:** `0x4387a1fc` llama a
`0x43b122fe(out)`, que escribe `out+0x59` mediante `0x43acb888`.
Ese byte llega a `cStack_83` y habilita el secundario en `0x43814ea0`.
`0x43acb888` devuelve el predicado `0x436bd404()!=0`;
`0x436bd404(unit)` lee el byte `0x43f922ef+unit`. `0x436bdbfc` lo
incrementa hasta dos tras operaciones de liberación/preparación DMM.
Es estado de software, sin espera de interrupción ni poll de fin de transferencia.

`0x43b2a2d0 → 0x43903118` registra **FreeRdv**, comando **0x0d** y
respuesta **0x800d**. El parámetro pasado a este comando y los valores de
secuencia no deben reinterpretarse como tamaños o contadores DMA sin
evidencia adicional. `0x43ae7542` invalida el handle y borra sus pares.

## VERIFICADO — origen del objeto y posición en la secuencia

`0x4380e358` / `0x4380e43c` seleccionan las funciones de trabajo mediante
slots originales (xrefs conservadas en `s33-scope`).
`0x43afb46a → 0x437de944` construye el callback de cinco palabras:
destino adaptador **0x43afb3bb** (slot `0x44020894`), ajuste cero y
función seleccionada en `+8`. `0x4380e2e8` conserva el callback en el
descriptor de trabajo.

`0x4380d708` toma un objeto del pool `0x43ee0048`, lo inicializa con
`0x4380d5b4` y aplica su callback de parámetros. `0x4380ca5c`, seleccionado
desde `0x4380e2a8` (slot `0x44025530→0x4380ca5d`), completa `P` a partir
del contexto de sincronización. Por ejemplo, escribe `P+0x1b4` desde
`context[2]+0x28` y en ramas específicas cambia la clave `P+0x18c`
a **0x2f0** o **0x2b1**. No es una dirección raster observada.

En `VD_Sequence`, la ruta concreta es:

1. `0x437916d4 → 0x43796954`.
2. Si hay descriptor de trabajo, `0x4380d708` obtiene `P` y
   `0x43796c6c → 0x4381bd4c` construye `Image`: `Image+0=P`, callback
   copiado a `Image+8`, estado en `+0x22/+0x23` y lista por categoría.
   `0x43b04730` llama al método `+0` del propietario con `Image`;
   esta llamada virtual conserva el límite de resolución del objeto efectivo.
3. `0x43796c7a → 0x4381bf38(0x43e9de14)` recorre trabajos de esa lista,
   con protección mediante llamadas `0x43560d38/0x43560d1c(0x1b)`.
4. `0x43b047d0 → 0x43b0478c(Image+8,Image)` resuelve el callback;
   `0x43afb3ba` pasa **Image** como argumento a la función seleccionada
   en `callback+8`. Ahí se construye `input` y se llama a `0x4379b44c`.
5. `0x43796c96 → 0x4379bb90(context)` envía los bloques de canal si
   `0x43ae916c()==0`.

Así, estos trabajos pueden preparar/publicar el bloque **dentro de
VD_Sequence**, antes de la fase Post/Drive ya descrita en S32. No son
necesariamente los callbacks registrados para VD_Post/VD_Drive. Las ramas
que cambian categoría se conservan en los exports: `0x437965ac` asigna listas
según categoría (0→`0x43e9de14`, 1→`0x43e9d810`, 2→`0x43e9d788`,
3→`0x43e9d71c`, otras→`0x43e9dd24`). No se afirma que todos los modos o
las 26 llamadas se ejecuten en el mismo VD.

El otro llamador directo de publicación es **HS_Sequence `0x43790b68`**,
callsite **0x4379123a**, condicionado por `0x43ae916c()!=0`.
Su entrada completa se exportó: `0x43791000` fue una consulta interior
exploratoria, con registros `unaff_`, y **no debe usarse como función completa**.

## PARCIAL — enum de formato

Se rastreó `input+0x38 ← P+0x1b4 ← context[2]+0x28`.
Se conserva el remapeo 0→2, 1→0, 2→1, 3→5, 4→3, 5→4.
Otro conversor, `0x43814d24` (log `EnumConverter.h`), agrupa 0/3/5→0,
1→1, 2→2, 4→3 para la entrada APL; tampoco aporta nombres de formatos.
No apareció una tabla que vincule esos seis valores con YUV422, planar,
submuestreo, orden de bytes o pitch. Por ello **PARCIAL**, sin nombre de
formato real asignado. Geometría y alineamientos no bastan para decidirlo.

## PARCIAL / NO_VERIFICADO — finalización física

**VERIFICADO:** AllocShare/AllocRendezvous verifican respuesta de un servicio
DMM; `src+0!=-1` valida un ID; `handle+2` cuenta extents y `handle+3`
controla estado de referencia. Ninguno prueba que el sensor haya terminado
de escribir el YC. La exclusión de listas con `0x1b` tampoco es fin DMA.
La finalización de un trabajo `Image` es una transición del planificador.

**VERIFICADO — avance hasta configuración de direcciones DMA:** el mismo
helper `0x43814ea0` pasa a `0x436be554` un registro que incluye ID/clave
del handle primario y **`P+0xc4`**, primera palabra del primer extent del
handle secundario `P+0xbc`. `0x436be554` contiene los logs
`sapl_SetDmaAddrTar`, `sapl_SetDmaAddrMEOut`, `sapl_SetDmaAddrOut` y
`sapl_SetDmaAddrParamBuff`; abre handles mediante `0x43903280` y, en
una rama, `0x43902df8(...,open=1,...,unit=10)`. Pasa palabras de extents a
`0x43a3a9b4(value,0x10,1)` y guarda valores preparados en
`0x43e77b7c+unit*0x38`. La traducción usa
`0x43560934/0x43560978`, que recorren pares de prefijos desde el slot
`0x44023cd0`: comparan los cuatro bits altos, preservan los 28 bajos y
validan que exista el prefijo. No se atribuye sin prueba un espacio físico
o CPU a la palabra anterior a la traducción.

La tabla original está en **0x43b90850**: pares
`0x80000000→0`, `0x90000000→0x10000000`,
`0xa0000000→0x20000000`, `0xb0000000→0x30000000`,
`0xc0000000→0x40000000`, `0xd0000000→0x50000000`, terminador
`0xffffffff/0xffffffff`. Con `(0x10,1)`, `0x43560934` busca la
columna derecha y devuelve el prefijo izquierdo más los 28 bits bajos.
El auditor contrasta estos pares directamente con el blob.

Después `0x43814ea0 → 0x436bdbfc` programa los valores preparados.
Por ejemplo, `0x436c0354` y `0x436c04e4` escriben respectivamente
offsets **0x20** y **0x50** de bancos MMIO **0xf3850400**, **0xf3950400**
o **0xf3a50400**, según unidad. Esto demuestra configuración de registros
en una rama vinculada a los handles de trabajo, más allá de transportar IDs.
No entrega valores numéricos de buffers en ejecución ni demuestra que los
píxeles estén ya disponibles. No se extiende esta asociación a todos los
canales/modos ni a una adquisición nueva del sensor.
La ruta concreta del secundario es `P+0xc4 → registro de solicitud+0x38
→ 0x43e77ba0+unit*0x38 → 0x436c041c`, que escribe el banco MMIO en
**+0x34**. La ruta de un ID primario abierto puede llegar a
`0x43e77bac+unit*0x38 → 0x436c06fc`, offset MMIO **+0xa4**.
Al final, `0x43acb2e8 → 0x436c019c` escribe sucesivamente **0 y 1** en
`0xf3850500/0xf3950500/0xf3a50500`. **INFERENCIA:** es una orden de
lanzamiento/rearme, compatible con el log `Apl_Kick`; su efecto físico y
el significado de cada registro no están demostrados por un manual de hardware.

Las comparaciones `0x4379caee/0x4379cafa` siguen siendo tiempo de ventana
según S32. No se les atribuye aquí transferencia física.

Se continuó además la rama de corrección `0x4354ea98 → 0x439416d4`
(`rcct_InitV`) / `0x4394171c` (`rcct_DistCorrectionV`), exportando sus
implementaciones inmediatas `0x43944678` / `0x43944af0` en `s33-boundaries`.
Es una rama de procesamiento distinta del mero intercambio AllocShare;
sus nombres no demuestran fin de adquisición del YC.

**NO_VERIFICADO:** un par señal/espera físico equivalente al SAFIN de
EncodeStill de S30, asociado inequívocamente al handle YC aquí publicado.
No se demuestra su ausencia universal: quedan backend DMM importado,
operaciones de procesamiento y callbacks dependientes de objetos/estado.
Tampoco se han observado integración electrónica, coherencia de caché,
propiedad exclusiva de los píxeles ni captura silenciosa completa.

## Validación y siguiente frontera

[`s33-audit.py`](../../analysis/ghidra/s33-audit.py) se ejecutó primero sin
`s33-final.json` (fallo esperado por evidencia ausente) y después con las
exportaciones: PASS de SHA, archivos persistentes, cobertura de las **29**
llamadas y **13** construcciones locales. Compara el proyecto con el manifiesto
S32, coincidente con los hashes observados al comienzo de S33; no se atribuye
a ese manifiesto un snapshot nuevo previo a la primera apertura de S33.
Cada exportación también contrasta todos los bytes cargados con el original
antes de escribir. Los logs `s33-*-headless.log` conservan las consultas;
se reutilizó sin modificar `s32-scripts/S32Export.java`, de ahí sus etiquetas
`S32` y nombres auxiliares `s32_candidate_` en resultados S33.

Ruff del auditor sin avisos nuevos; `ruff check src tests` mantiene los nueve
avisos preexistentes de cuatro tests ajenos. Mypy de `src` y del auditor PASS.
Mantenimiento del conocimiento completado en los cinco pasos; grafo estable
en 1376 entidades / 2633 relaciones. `pytest tests/knowledge -q`: **67 PASS**;
`ruff check scripts/knowledge tests/knowledge`: PASS.
No existe `.git` en este workspace: cambios sin commit; sin push.

**Próximo paso exacto:** resolver la importación de `base+0x14`, entrada
`+0x2e4` (DMM), y el lado que satisface las claves Rendezvous de `P+0x18c`
/ `P+0x194`, conservando la tupla clave/ID/secuencia. Correlacionar esa
asignación con configuración de escritura y callback físico de finalización.
Para RC, distinguir la finalización de corrección de la adquisición original.
El escritor secundario ya localizado es `0x43814ea0`; seguir su flag auxiliar
y el productor Rendezvous de `P+0xbc` antes de buscar otros escritores.

Las 118 consultas de función exportadas no tienen error de decompilación;
eso no prueba tipos ni completitud semántica. Dos consultas adicionales
resuelven contenedores completos: `0x43796740→0x4379671c` y
`0x436be62a→0x436be554`. Usar las entradas de los contenedores,
no las direcciones interiores como nuevas funciones.
