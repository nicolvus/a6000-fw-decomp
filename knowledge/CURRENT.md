# Estado actual — léeme primero

## S176 — dos lectores más del state IMX210 (22-10-2026)

REA/bytes clasifican `0x4386140a` como load del state pointer seguido por lectura de `state+0xac` en `0x43861410`; si el byte es cero, la cola usa default 6. `0x438693ec` carga el mismo pointer y el bloque lee bytes `+0x30..+0x37`, copiando ceros/defaults a un objeto distinto apuntado por `r6`. No hay store a state ni a gates `+3/+6` en esos dos procedimientos. **Límite local:** campos estáticos cero no determinan runtime, y no se concluye ausencia global. [S176](../docs/capture/s176-imager-state-readers.md), reproducción `analysis/s176_imager_state_readers/state_readers.json` (3 tests).

**Siguiente:** clasificar el próximo xref no resuelto del state pointer con REA typed refs y bytes; considerar el árbol de referencias de la tabla `0x43ff3200` como investigación separada, porque xrefs exactas al vector/GOT base no fueron observadas.

## S163 — tercer lector del estado (22-10-2026)

`FUN_438d939c` lee `state+0x1c` (halfword) y `+0x1e` (byte); defaults 3/4 si los campos valen cero. Construye un mensaje y almacena resultados a otros globals, no a estado/gates dentro de este cuerpo. **Notificación es INFERENCIA; runtime no probado.** [S163](../docs/capture/s163-imager-state-event-reader.md), JSON/3 tests en `analysis/s163_imager_state_event_reader/`. Commit publicado `ff5bbb98`.

**Siguiente:** seguir un xref aún no clasificado hacia `0x43f72d02`, especialmente si hay store tipado; mantener “no demostrado” en lugar de inferir ausencia.

## S162 — lectores de `state+0x1c` (22-10-2026)

`FUN_438d9318`/`FUN_438d936c` cargan el state pointer y leen un halfword en `+0x1c`; cada resultado se escribe a `0x43f7c702` o `0x43f7c704`, no al objeto/gates. La lectura es VERIFICADA; “notificación” es INFERENCIA, alcanzabilidad runtime NO_VERIFICADA. [S162](../docs/capture/s162-imager-state-event-readers.md), `analysis/s162_imager_state_event_readers/event_readers.json` (3 tests). Commit publicado: `8f17819a`.

**Siguiente:** otro xref pendiente; comprobar si es puntero/GOT, field read o writer tipado antes de atribuirlo a gates.

## S161 — otro spill del state pointer (22-10-2026)

En `FUN_4384b268`, `0x4384cb06` carga `0x43f72d02` desde GOT y `0x4384cb0a` almacena el puntero en `[sp+0x20]`; el edge al objeto es de valor, el WRITE efectivo es stack. El cuerpo lee otros campos, no gates `+3/+6`. [S161](../docs/capture/s161-imager-state-spill.md), `analysis/s161_imager_state_spill/state_spill.json` (3 tests). Límite local. Commit publicado: `0a26c130`.

**Siguiente:** escoger otro xref restante y clasificar si es acceso de memoria efectivo o propagación de puntero; no convertirlo en conclusión global.

## S160 — writer local de `state+0` (22-10-2026)

`FUN_4383abec` carga el state pointer vía GOT y `0x4383ac90` ejecuta `strb r3,[r2]`, edge REA WRITE a `0x43f72d02+0`; en la ruta que alcanza el store el contador expira y el byte se pone a cero. No escribe gates `+3/+6`, y la condición de los callers no acredita ejecución runtime. [S160](../docs/capture/s160-state-open-flag.md), JSON y 3 tests en `analysis/s160_state_open_flag_writer/`. Commit publicado: `0a7daba9`.

**Siguiente:** clasificar xrefs restantes; buscar escritura estructurada/copias hacia `+3/+6`, sin inferir ausencia global.

## S159 — spill del puntero de estado en `0x4386001c` (22-10-2026)

`FUN_4385fff0` carga el objeto vía GOT; `0x4386001c` es `str r3,[sp,#0x1c]` (spill), no write a estado. Este cuerpo lee `+0/+0x1c/+0xa2`, stores van a otros destinos; no gates `+3/+6` localmente. [S159](../docs/capture/s159-imager-state-spill.md), reproducción `analysis/s159_imager_state_ref/state_spill.json` (3 tests); no prueba ausencia global. Commit publicado: `98262cd6`.

**Siguiente:** otro xref restante a `0x43f72d02`; distinguir el edge de valor del acceso al contenido y priorizar instrucciones de escritura/copia.

## S158 — `0x4385b268` guarda el puntero de estado en stack (22-10-2026)

`FUN_4385b234` lee GOT `0x4401f990→0x43f72d02`; el xref `0x4385b268` es `str r3,[sp,#0x20]`, un spill, no acceso de escritura a la base. El cuerpo lee `+0x26/+0x28/+0x29`, escribe a otros objetos, y no toca gates `+3/+6` localmente. [S158](../docs/capture/s158-imager-state-ref.md), `analysis/s158_imager_state_ref/state_accessor.json` (3 tests). Sin conclusión global. Commit publicado: `3affd7cc`.

**Siguiente:** clasificar otro xref restante; priorizar candidato que use store/copy sobre puntero estado, no otro spill, mediante typed references y bytes.

## S157 — lector de snapshot del estado (22-10-2026)

`0x43859954` lee el GOT slot `0x4401f990` y obtiene el puntero `0x43f72d02`; `FUN_43859944` lee `+5`, condicional `+0xf`, vuelca/copía a buffer y escribe un global distinto. No hay stores `+3/+6` en este cuerpo. **Límite local**, no ausencia global. [S157](../docs/capture/s157-imager-state-snapshot.md), JSON/3 tests `analysis/s157_imager_state_snapshot/`. Commit publicado: `6d8680c8`.

**Siguiente:** clasificar otro xref a base del estado, especialmente candidatos no cubiertos en S153–S157; seguir stores y alias por evidencia directa.

## S155 — tres referencias más al estado de gates (22-10-2026)

REA/bytes: `0x43857f90` y `0x43857fb0` cargan el byte `+0` y devuelven predicados; `0x43858134` carga el puntero GOT pero solo lee campos `+4` y `+0x1c`, almacenando en otros objetos. No se observa write a gates `+3/+6` **en estos cuerpos**. No es ausencia global. [S155](../docs/capture/s155-imager-state-readers.md), reproducción `analysis/s155_imager_state_readers/state_readers.json` (3 tests). Commit publicado: `d0888afd`.

**Siguiente:** elegir un xref restante a `0x43f72d02` (p. ej. `0x43859954`/`0x4385b268`) y clasificar su dataflow/store por evidencia, uno o un grupo acotado.

## S154 — referencia del estado desde `0x438363e6` (22-10-2026)

`FUN_438363cc` en `0x438363e6` carga el valor del slot `0x4401f990` (`0x43f72d02`); el edge al objeto es DATA y el READ efectivo es al GOT slot. Este procedimiento lee otros campos +0x38..+0x3b y no escribe +3/+6; sus stores van a otros objetos/buffers. **Acotado a esta función**; no prueba ausencia de otros writers. [S154](../docs/capture/s154-imager-state-ref.md), JSON y 3 tests en `analysis/s154_imager_state_ref/`. Commit publicado: `9030811f`.

**Siguiente:** revisar otro xref a la base del estado para detectar copias estructuradas o stores a +3/+6 con evidencia positiva; no inferir ausencia por la lista de xrefs.

## S153 — gates lectores del volcado del gap (22-10-2026)

REA/bytes verifican los gates en `FUN_43858338`: `[obj+3]&2` y `[obj+6]&0x20` habilitan líneas del dumper; los xrefs directos a esos bytes son lecturas y los bytes BSS iniciales están a cero. **Escritor/valor runtime NO_VERIFICADOS**; no prueba ausencia global ni ejecución en una foto. [Informe](../docs/capture/s153-imager-dump-gates.md), `analysis/s153_imager_dump_gates/dump_gates.json` (3 tests). Commit publicado: `7ce7f329`.

**Siguiente:** seguir refs al bloque de estado `0x43f72d02` buscando copias estructuradas a +3/+6, distinguiendo base-pointer stores de inicialización `+0/+2`; si no se resuelve, mover a otra ruta estática independiente. No hacer pruebas físicas.

## S152 — lectura diagnóstica de un byte del gap G (22-10-2026)

Las celdas de S150 son campos `addr` de dos tablas `{u16 id,u16 size,u32 addr}`: A[32] y B[6] = `{0x0030,1,0x43eb0850}`. `FUN_43858338` dirige al raw copier `FUN_43b09c7a`, que lee `addr+size−1` hacia abajo y copia a buffer; con size=1, lectura exacta del byte gap. **No escribe el byte.** Dos gates dependen de flags con valor runtime desconocido, así que alcanzabilidad es PARCIAL. [S152](../docs/capture/s152-imager-gap-descriptor-read.md); `analysis/s152_imager_descriptor_reads/descriptor_reads.json` (3 tests). Commit publicado: `024bb46f`.

**Siguiente:** identificar escritores de los bits gates de `0x43f72d05`/`0x43f72d08` o demostrar cómo se inicializan dinámicamente; mantener la distinción entre ruta de volcado y exposición. S51 sigue A/B/C=NO.

## S150 — xrefs de los huecos +8/+9 y pista de descriptor (22-10-2026)

REA devolvió `[]` para las ocho direcciones exactas de los huecos de fila; el control positivo muestra xrefs al inicio de una fila. Una búsqueda completa de bytes encuentra dos celdas que empiezan con literal `0x43eb0850` (el hueco +8/+9 de la tercera fila), pero no se ha identificado su consumidor ni formato: **no afirmar lectura/escritura efectiva**. Bytes estructurados en `analysis/s150_imager_row_gaps/gap_refs.json`; [informe](../docs/capture/s150-imager-row-gaps.md), 3 tests. El resultado vacío no prueba ausencia de escritores por alias/argumento. Commit publicado: `feb767e5`.

**Siguiente:** resolver quién consulta las dos celdas `0x4400812c` y `0x4400b27c` y cómo se interpreta su primer campo; confirmar si se usa como puntero a `0x43eb0850` antes de atribuir acceso a gap.

## S149 — cierre parcial de helpers de filas G (22-10-2026)

Se verificó el cierre del loop por instrucciones: el writer `0x4383c9dc` **itera cuatro veces** (contador 4, stride `0x10`, back-edge), no solo una; stores por fila en `0,4,6,0xa,0xc,0xe`. Los cuatro helpers auditados no escriben `+0x2c..+0x6b` ni el hueco +8/+9. **Limitado** a estos cuerpos/gates, no excluye otros writers. Evidencias y test reproducible: [S149](../docs/capture/s149-imager-row-helpers.md), `analysis/s149_imager_row_helpers/row_helper_stores.json` (3 tests). S51 sin cambios. Commit publicado: `c4193a2a`.

**Siguiente:** decidir una pregunta IMX210 independiente para cerrar el consumidor de filas/valores modo; buscar escritores alternos de `+0x34/+0x35` con evidencia positiva, sin asumir que el silencio de estos helpers es ausencia global.

## S147 — escritor parcial de filas G (22-10-2026)

**VERIFICADO:** `0x437b5f00` forma `G+0x224` y prepara la llamada a `0x4383bf2c`; éste llama a `0x4383c9dc`, cuyo loop usa stride `0x10` durante cuatro iteraciones y escribe offsets relativos `0,4,6,0xa,0xc,0xe` en cada fila desde `+0x2c`. No escribe `+8/+9` **en ese loop**. REA evidence/páginas y bytes: [S147](../docs/capture/s147-imager-g-rows.md), `analysis/s147_imager_g_rows/g_rows.json` (3 tests). Commit publicado: `ffdba84b`.

**PARCIAL:** los otros xrefs a G son paso de puntero o loads; consumidores indirectos/efectos restantes, otros escritores, modo fotográfico y semántica física no se cerraron. No cambia S51.

**Siguiente:** seguir `FUN_4383bfd4`, `FUN_4383c818` y `FUN_43b08786` para identificar stores a `+0x34/+0x35` o campos restantes por evidencia positiva; después revisar consumidores de lectura. No atribuir significados eléctricos.

## S146 — límite de seeding REA y offset corregido (22-10-2026)

REA acepta `file-offset:` solo para resolver un procedimiento ya existente; no ofrece creación/seeding de función en el proveedor activo. `0x43843a44` mapea a `0x302a44` pero pseudocode falla por `no procedure`; `0x437b617e` corresponde a `0x27517e` (el offset `0x27617e` fue error de coordenada y mapea a otra VA). **La cobertura limitada no prueba ausencia.** [Informe](../docs/capture/s146-rea-seed-limit.md), reproducción `analysis/s146_rea_seed_capability/rea_seed_capability.json` (3 tests). Commit publicado: `0a865472`.

**S145 se conserva** como observación de bytes; su sugerencia de sembrar se reemplaza por recorrido estático reproducible. Siguiente: delimitar código Thumb mediante `read_bytes` REA y contrastar stores/gates sin afirmar CFG completo; si no cierra, pasar a otra pregunta IMX210 independiente.

## S145 — staging en hueco de análisis (22-10-2026)

**PARCIAL:** REA reconoce `FUN_43843a38` (`0x43843a38..0x43843a3f`), pero `0x43843a44` y la rutina que empieza en `0x437b617e` están fuera de procedimientos analizados. Los bytes originales verifican el prólogo Thumb candidato y `BL 0x43843a44` en `0x437b61d2`. Evidencia y reproducción: [S145](../docs/capture/s145-imager-code-gap.md), `analysis/s145_imager_unanalyzed_code/code_gap.json` (3 tests). Esto **no prueba ejecución ni ausencia**. Commit publicado: `a0955258`.

**Siguiente exacto:** en REA sembrar solo entradas Thumb observadas `0x437b617e` y `0x43843a44`; recuperar `procedure_info` y refs salientes; después seguir referencias a tablas/callbacks del caller.

## S142 — referencias directas al struct S (22-10-2026)

**VERIFICADO:** REA `xrefs(S=0x43eb35d0)` devuelve `0x437b56b4` (inicialización que limpia 0x148 bytes) y `0x437b59ce` (lee `u16 S+0xda`, lo consume en `0x4383c638`). Bytes Thumb del GOT/lectura/thunk corroborados y reproducibles en `analysis/s142_imager_s_init/s_accesses.json`; 3 tests. Commit publicado: `bf199b15`.

**PARCIAL:** el memset inicializa `S[0]=0` pero no identifica escritor posterior ni valor por modo. Las xrefs directas no incluyen necesariamente rutinas que reciben S como argumento; no se toma el listado como prueba de ausencia. [Informe](../docs/capture/s142-imager-s-init.md). S51 intacto.

**Siguiente:** trazar con REA funciones que reciben `S` como argumento, empezando por la entrada al staging `0x43843a44`; primero hallar coordenada de función admisible, después seguir stores y gates de `S[0]`.

## S141 — selección de fila IMX210, origen sin cerrar (21-10-2026)

**PARCIAL:** REA `0x43b0893c` + bytes Thumb verifican `S[0]` como selector, fila en `S+4+16·S[0]` y copia de 16 bytes a `S+0xc4`; `0x43849fb8` consume esa fila al construir exposición. **NO_VERIFICADO:** quién escribe `S[0]`, condiciones de staging y origen G+`0x224`; REA no reconoció `0x43843a44`, consulta vacía no prueba ausencia. Evidencias y reproducción: [S141](../docs/capture/s141-imager-row-copy.md), `analysis/s141_imager_row_trace/row_trace.json`; 3 tests. Commit publicado: `47147952`.

**Siguiente:** obtener una dirección Thumb que REA admita para el código referido como `0x43843a44` y seguir evidencia positiva del store a `S[0]` / copia G→S. No nueva Ghidra. No semántica física ni cambio de S51.

## S140 — vector de registros IMX210 y bancos de filas (21-10-2026)

**VERIFICADO:** REA leyó 119 punteros en `0x43fe995c`, terminador cero en `0x43fe9b38`; cada registro empieza `{u16 ID little-endian, byte +2, byte +3}`. El vector completo está en `analysis/s140_imager_regmap/imager_regmap.json` y se reproduce con `analysis/s140_imager_regmap/extract_regmap.py` (3 tests). Commit publicado: `6f064d93`.

**PARCIAL:** los rangos S `0x43eb35d0` y G+`0x224` `0x43eb07fc` son cero en el blob. El código selecciona fila mediante `S[0]` desde `S+4+16·índice` y la copia a `S+0xc4`; no se ha determinado la asignación modo→fila ni su contenido runtime o significado físico. **S51 A/B/C=NO se mantiene.** [Informe](../docs/capture/s140-imager-register-map.md).

**Siguiente:** seguir con REA los stores a `S[0]` y la copia desde G+`0x224` hacia S en la ruta `0x43843a44`; bytes/instrucciones originales requeridos. Identificadores S138/S139 están ocupados por trabajo no relacionado/in progreso; evitar sus archivos.

Resumen operativo breve. Para el historial completo de decisiones, ver `knowledge/PROGRESS.md`.
Para restricciones del proyecto (sin firmware ejecutado, sin flasheo) ver `docs/STATE.md`; el usuario
ha instruido explícitamente subir cada hito terminado a `origin/main`.

[Plan de pruebas físicas pendientes](../docs/capture/physical-test-plan.md) (P1–P8, ninguna ejecutada; requieren tu autorización).

**Sesión actual (21-10-2026)**: línea de RE general por módulos de trazas + línea del obturador
electrónico. Lo último: **S137** (`[CTRLCORE]`), **S136** (`[ACCY]`), **S135** (control positivo:
el A6300 tiene `ElecShutter/` y la A6000/A7S **no**), **S134** (la relación `shut`→`svd` es
aritmética, no tabulada), **S133** (`[MOUNT_DEBUG]`), **S132** (`[CLK_CTRL]`), **S131** (`[VPH_API]`),
**S130** (los 20 módulos "nuevos"), **S129** (`[CAMERA_MAIN_IM]`), **S128** (mapa de etiquetado de la
fw3.21), **S127** (`[CAMERA_MAIN_LC]`), **S126** (`[CAMERA_MAIN]`), **S125** (`[IMAGING_REL]`/
`[IMAGING]`). **S51 A=NO, B=NO, C=NO** (sin cambios). Catálogo: 69 hitos en
[docs/capture/linea-general-re.md](../docs/capture/linea-general-re.md). Sesiones: [README](../README.md).

## S109 — el módulo `[CDIAG]` (270 trazas): el banco de diagnóstico del códec (21-10-2026, línea de RE general)

**VERIFICADO (22 tests, `tests/test_s109_cdiag.py`):** 270 tokens `[CDIAG]` (`0x43c3b0d4`–`0x43c3e86a`): 255 cadenas que empiezan por `[CDIAG]` y 15 `[ERR][CDIAG]`. Estructura: **7 escenarios** (HD REC/DEC, SD REC/DEC, JPEG ENC/DEC/ENCDEC) × **8 operaciones** (`DbgDiagAvc` `0x43c3b6df`, `CmpData` `0x43c3b72a`, `RunCodec` `0x43c3c123`, `RelMemArea` `0x43c3b768`, `SetMemArea` `0x43c3b7ec`, `SetData` `0x43c3c162`, `ConfirmDoneCodec`, `SetDiagMode` `0x43c3bf5c`), **27 firmas `CDIAGER …`**, **16 clases** (RTTI: `8CdCtrlIf` `0x43c3b67e` … `13CdUtilSysvMsg` `0x43c3e8ab`) y **2 ficheros** (`cdCtrlIf.cpp` `0x43c3b1a8`, `cdCtrlCore.cpp` `0x43c3b86c`). **Tabla de registro de clases** en `0x43fda6a0`: 16 pares `{vtable base común 0x43fd04f8, puntero al nombre RTTI}` (en la A7S, `0x43fdb6ec`) → es una tabla de **resolución clase→nombre**, no de vtables por clase. 118 funciones (`0x435a127a`–`0x435a50b6`), 295 sitios de referencia; **226/255** cadenas referenciadas y **29 muertas** (ni PIC ni puntero absoluto). Transporte por **OSAL**: `osal_rcv_msg` `0x43561260`, `osal_snd_msg` `0x4356120c`, `osal_free_msg` `0x435612ec`, `osal_try_valloc_msg` `0x435612d0`; el núcleo de la tarea (`0x435a1318`) llega a `osal_rcv_msg` vía `0x435a9f4c` (bl en `0x435a9f68`); escritor `0x435ab880` (310 llamadas), nivel `0xbe`, id `0xbad`.

**Diferencial A7S fw3.20**: 270 tokens, **270 cadenas comunes y 0 exclusivas** en ningún sentido, mismas 16 clases, 2 ficheros y 27 firmas → módulo **idéntico**. El A6300 fw2.01 tiene 310 tokens = 270 + **40 de 4K** (`[CTRL4KREC]`, `CdCtrl4KDec/Rec`, `CdExt*`, `CodecDiagLog`).

**Negativo verificado**: 0 menciones de `shutter`/`silent`/`imager`/`sensor`/`dmm` en las 270 trazas → sin efecto sobre S51.

[Informe](../analysis/s109_cdiag/cdiag.md) · [doc](../docs/capture/s109-cdiag.md). Siguiente: formato de `MSG_SENS_COMMAND`/`DIAGINFO`; codificación numérica de `cmd`/`mode`/`func`; emisor de los comandos `SENS_*`; fichero fuente de las clases de códec (no embebido).

## S116 — el módulo `[SFRS]` (117 trazas) de control por *pins* (21-10-2026, línea de RE general)

**VERIFICADO (23 tests, `tests/test_s116_sfrs.py`):** 117 cadenas `[SFRS]` en `0x43ce7661`–`0x43ceb8c4`; **131 puntos de emisión PIC** (`ldr rX,[pc,#imm]` + `add rX,pc`) y **52 funciones**, todas dentro de `0x439a0000`–`0x439c0000` (módulo compacto y localizado), **0** cadenas sin referencia. Sub-bloques: SUPERSTABLEMOVIE 37, MOTIONSHOTVIDEO 25, EFFECTMOVIEREC 23, PINSEND 12, SET_PATH_STATUS 9, SA 6, RC_AIC_TRIGGER 3, MULTIPLEXTRIGGER 2. Contenido: `SETPIN`/`GETPIN`/`PINSEND` con `file=%s line=%d`, `ReqYccAsap`, `YccOut`, `SendExecTrigger`, `CtSetAicParam`, `RC_CALLBACK`. Evidencia de código: `SETPIN` `cmp r1,#1` en `0x439aada4` (línea 58 en `0x439aadc0`), `GETPIN` `cmp` en `0x439aae3c` (línea 56: `movs r2,#0x38` en `0x439aae4c`), cola de `EXECUTE_PIN_SEND` en `0x439b1f4c`–`0x439b1f6c` (lee `[r4,#0x3f4..0x3ff]`, escribe `[r4,#0x410]=1` y `[r4,#0x40c]`, traza `0x43ceb80d`).

**Diferencial A7S fw3.20**: la A7S tiene **151** cadenas `[SFRS]`: **117 comunes, 0 exclusivas de la A6000 y 34 exclusivas de la A7S** → el módulo de la A6000 es un **subconjunto** del de la A7S.

**Observación**: 40 de las 52 funciones no imprimen `file=%s`, así que no se les puede asignar fichero fuente; de las 24 clases `.cpp` citadas solo 12 se localizan en el código.

[Informe](../analysis/s116_sfrs/sfrs.md) · [doc](../docs/capture/s116-sfrs.md). Siguiente: significado de SFRS, AIC, RC, VFX, IIB y PINSEND; si `line=%d` corresponde al `.cpp` de `file=%s` (falta la tabla de líneas); semántica de los tres modos de grabación.

## S117 — `[AUGI]`: la cabecera de 32 B del códec (21-10-2026, línea de RE general)

**VERIFICADO (27 tests, `tests/test_s117_augi.py`):** 75 apariciones de `[AUGI]` → **26 cadenas** con el prefijo `[AUGI]` y **49** con `[CodecIF][AUGI]…`; dos *clusters* de cadenas: los **impresores de estructura** (`0x43c6a909`–`0x43c6b517`, con los nombres de campo `length`, `num_AUs`, `PTS`, `DTS`, `nextHRDBuffer`, `nextPTS`, `size_SPS`, `size_PPS`, `PictureType`, `seq_parameter_set_id`) y el **volcado de depuración** `[AUGI] campo = %d` (`0x43cd993d`–`0x43cd9c8d`). **No es un subsistema de trazas**: es el nombre de una **cabecera de bloque de códec**, y las clases que la manipulan están nombradas en el binario: `DecExAugiConverter` `0x43c6a8db`, `DecInAudioAugiConverter` `0x43c6acc5`, `DecInVideoAugiConverter` `0x43c6b02e`, `EncExAugiConverter` `0x43c6b554`, más la entrada de API `StrmEngEncCIIf::CodecEventCreateVAUGI` `0x43c66fbf`. 86 puntos de emisión y **0** cadenas sin referencia; los impresores ocupan 4 funciones contiguas `0x436150ce`–`0x436163c0` y el dumper `0x4391ca90`. **La sigla no aparece expandida en ningún byte** (no se inventa su significado) y no se afirma qué cuenta `length`.

**Diferencial A7S fw3.20**: **idéntico** — mismas 75 apariciones y mismas 26 cadenas.

[Informe](../analysis/s117_augi/augi.md) · [doc](../docs/capture/s117-augi.md). Siguiente: qué cuenta exactamente `length`; el layout binario de la cabecera; el emisor de `CodecEventCreateVAUGI`.

## S118 — el módulo `[SFRA]` (100 trazas) de la infraestructura escalar (21-10-2026, línea de RE general)

**VERIFICADO (22 tests, `tests/test_s118_sfra.py`):** 100 trazas `[SFRA]` en `0x43ce5a16`–`0x43ce7723` (100 textos distintos), 11 sub-bloques (`[CMD]`, `[CMP]`, `[BUF]`, `[RATECONTROL]`, `[RC]`, `[NOTIFY]`, `[ERROR]`/`[ERR]`, `[WARNING]`, `[SFR_ERR_NOTREADY]`), 11 ficheros fuente (`ScalarInfraAsyncMain.cpp`, `SfrJpegBuffer.h`, 7× `ScalarInfraSequence*.cpp`, `SfrYc.cpp`, `DrvCallRc.cpp`) y 47 funciones. **`SFR` = `NS_SCALAR_INFRA` verificado por los nombres de clase C++** de la zona `[SFR]`, no por conjetura. **17 comandos** con los **ids decodificados de los bytes** en los predicados `0x43b63xxx` (tipo de mensaje en `+0x02`, sub-comando en `+0x0f`): `0x0100`/`0x10` GET_INFO, `/0x20` GET_JPEG, `/0x22` SET_JPEG_PARAM, `/0x30` GET_SA_RESULT, `/0x32` SET_SA_NOTIFY, `/0x42` LiveView SET_JPEG, `0x8110` SET_PATH(CLOSE), `0x8120` SET_PATH(OPEN), `0x9010` GET_INFO_CMP; despachador de finalizaciones `0x439a1640` con `TBB` de 5 bytes en `0x439a1654`; núcleo `ScalarInfraAsyncMain` `0x439a1864`.

**Diferencial A7S fw3.20**: **100/100 mensajes idénticos** y en el mismo orden (mismo conjunto, mismos sitios y funciones) → módulo **idéntico**, solo cambia su posición en el blob (`0x7a4a16` en la A6000 frente a `0x7998c4` en la A7S). El A6300 fw2.01 tiene **108** trazas: las 100 de la A6000 más 8 con nomenclatura antigua (`CMD_JPEG`, `CMD_LIVEVIEW`, `SET_PATH_CMP(JPEG CLOSE)`, `LiveViewStageIdle::exec openReq/closeReq`…).

[Informe](../analysis/s118_sfra/sfra.md) · [doc](../docs/capture/s118-sfra.md). Siguiente: la correspondencia de los 5 casos del `TBB` con los nombres `[CMP]`; 5 ids de sub-comando sin traza propia; el papel de `RC`/`VFX`/`IIB`.

## S124 — el bloque de parámetros de exposición/lectura por `drive_mode` (imager) (21-10-2026, línea de RE general)

**VERIFICADO (7 tests, `tests/test_s124_exposure_params.py`):** de dónde salen los campos de la traza `[CAM_IMAGER]: SetExps : [PrevDrv][NowDrv][NextDrv][svd][shd][spl][shut]` (`0x43c93cc2`), leída de la función que la emite (`FUN_436d6f70`, localizada por sus sitios PIC `0x436d7242`/`0x436d7280`): `PrevDrv` = u16 [r1+4], `NowDrv` = u16 [r1+0], `NextDrv` = u16 [r1+6] y **`shut` = byte [r1+9]**; `svd`/`shd`/`spl` = tres u32 del **contexto de captura** en +0x178/+0x174/+0x170 (lecturas en `0x436d725c`, `0x436d726a`, `0x436d7274`).

**Diferencial A6000 fw3.21 vs A7S fw3.20**: el **conjunto de parámetros es el mismo** (`shut`, `svd`, `shd`, `spl`, `sint`, `gs`, `epdsel`): las 5 trazas de `[CAMERA_MAIN_SYNC]` que lo revelan coinciden texto a texto (`ZAF img_id:%04X, shut:%d, svd:%d, shd:%d, spl:%d, epdsel:%d` `0x43ca3356`/`0x43ca8e9b`, `Imager param error shut:%d…` `0x43cb11d2`/`0x43cb2bcd`, `Imager svd error…` `0x43cb1217`/`0x43cb2bfe`, `shut:%d, svd:%d, shd:%d, spl:%d, sint:%d, gs:%d` `0x43cb1253`/`0x43cb2c26`, `vfc%d[%d] shut%d->%d…` `0x43ca3a50`/`0x43ca936f`). Lo que **sí** cambia en la fw3.21: (a) el vocabulario de trazas (`SetExps`/`SetExpsZ`/`SetRead`/`Execute` con el drive mode **anterior** frente a `Exposure.`/`Change ImagerMode.` de la A7S, `0x43c9c942`/`0x43c9c8d9`); (b) el **layout del contexto** (la rama de modo `0x11` usa `r0+0xfc` en la A6000 frente a `r0+0x13c` en la A7S); (c) una traza **nueva** `[CAMERA_MAIN_LC]: zaf_now_shut_cycle=%d` `0x43ca7836` (la A7S no la tiene) y la retirada de `b8_shutter_limit` `0x43c9f01c` (solo A7S).

**Para la línea del obturador**: `shut` convive con `shutter mute on/off` `0x43c8253b` (el silenciador del obturador **mecánico**), `shutCycleCount` `0x43cbee6b` y `uc_shut_idx_num` `0x43cc326d` → es el **índice/contador de obturación** del modo de lectura, **no** un selector de mecanismo. La fw3.21 **no** introduce ningún parámetro de obturador electrónico (el DFE/IMX210 sigue por P2S/DFE0 y CISIF, S56). **Sin efecto en S51 (A/B/C = NO).**

[Informe](../analysis/s124_exposure_params/exposure_params.md) · [doc](../docs/capture/s124-exposure-params.md). Siguiente: la **tabla de valores por `drive_mode`** (sin ella no puede afirmarse que ningún modo concreto difiera entre A6000 y A7S); el significado de `sint` y `gs`; si `zaf_now_shut_cycle` cuenta obturaciones mecánicas o electrónicas.

## S120 — `[IDT_OPD]`: la segunda instancia del módulo IDT (21-10-2026, línea de RE general)

**VERIFICADO (97 tests, `tests/test_s120_idt_opd.py`):** 274 apariciones del token `[IDT_OPD]` → **273** cadenas que empiezan por él (la 274.ª es anidada: `' $(,0[IDT_OPD]: CCinitParam addr null'`) y 274 textos distintos, en `0x43cf11f9`–`0x43cf5810`. **Los 274 mensajes van seguidos, byte a byte y separados por NUL, de su gemelo `[IDT]`** → el etiquetado es la única diferencia. **`IDT_OPD` no es una sigla inventada**: es un **recurso del `SyncResMgr`** (`RESOURCE_IDT_OPD` `0x43c9c461`, presente también en la A7S en el offset `0x761b67`) y unos **comandos** (`IDT_OPD_TOP_Sync_OPDAcquire` `0x43c9c2fc`, `IDT_OPD_TOP_Sync_SetFOPD`): la fw3.21 de la A6000 es la **única de las tres** que etiqueta con `[IDT_OPD]`. 165 funciones (`0x439dde84`–`0x439fcf9c`, ~127 KB de código) y **271 de las 274** cadenas con referencia confirmada (3 sin referencia: `0x43cf150f`, `0x43cf1557`, `0x43cf274a`). Estructuras verificadas: bloque IE (`0x439e80c8`, 19 campos, `tar_num`+0x00 … `backImgData`+0x78), bloque MAP (`0x439ee7e8`, 18 campos, `miniraw`+0x0c … `out_opd_ec`+0x4c) y 18 punteros de volcado en `0x43f41b30`/`0x43f41cbc`/`0x43f418a8`. Relaciones: `KickFOPD` desde `[IMAGING_CAP]` (`0x43cadd2d`), miniRAW hacia `[CAMERA_MAIN_LC]` (`0x43c9c8ba`), IDT en **HS3@CPU0** (`0x43ca12f6`); el driver del imager (S115) **no nombra** el IDT.

**Diferencial**: A7S fw3.20 y A6300 fw2.01 tienen **0** trazas `[IDT_OPD]` (306 y 382 `[IDT]`); **270 de los 274** mensajes son comunes texto a texto, 4 son sólo de la A6000 (reformulaciones de `Sync rate`, `det:xs:`, `test`, `test2`) y 36 son sólo de la A7S (16 del tipo `PBL … ERROR. R0./W0./W1./W2.`).

**Corrección de una herramienta del repo**: el subagente encontró que la *kill analysis* de `analysis/s106_imaging_cap/scan_pic_refs_v2.py` **estaba inerte** (`md.detail` apagado → `ins.operands` lanzaba `CsError` → nunca mataba nada; además `op.reg & 0xF` confunde r1 con r3 en Capstone). **Ya corregido**: ahora coincide con la regla estricta en el conjunto de cadenas y en los sitios verificados a mano (`[SFRA]` 118, `[AIP]` 37, `[TRK]` 288) y solo elimina los sitios falsos.

[Informe](../analysis/s120_idt_opd/idt_opd.md) · [doc](../docs/capture/s120-idt-opd.md). Siguiente: qué distingue la instancia OPD de la IDT normal; el layout del bloque LC y del array `waku`; el tamaño en bytes de cada mapa; el significado de `tar_num`, `isSpectRef`, `msain0/1`, `msaout`, `kido_th`, `sel_hist/sel_sum`.

## S126 — `[CAMERA_MAIN]`: el módulo raíz de la cámara (21-10-2026, línea de RE general)

**VERIFICADO (7 tests, `tests/test_s126_camera_main.py`):** 135 trazas `[CAMERA_MAIN]` en `0x43c9c57b`–`0x43ccae46`, **48 funciones** emisoras (regla estricta) y **148 ficheros fuente** embebidos en la zona. Es el contenedor de la capa de **coordinación** (AF y calibración, seguimiento, keymap, carga de parámetros), la que no pertenece a ningún submódulo especializado. Contenido: `calibration_fc_pos:%d getFcPos(suc_ref_index_target):%d` `0x43c9c57b`, `Calibration start` `0x43c9c6d5`, `FOCUS MODE is not AF-A` `0x43c9cd19`, `Scanless NG because of Face AF` `0x43c9cd3f`, `this lens is not permitted` `0x43c9ce07`, `SCANLESS OK! %d ympc %d csum %d cpeak %d defocus %d` `0x43c9ce8f`, `waku area is %d` `0x43c9d53f`, `keymap size is under 0 [%d]` `0x438d16b0` y `>>### LoadNum %x, Ch %x` `0x4378a68c` (51 trazas: la que más emite). **Puente con el ZPD** (S75): `NOT_DETECT from ZPD MODULE in spite of ZpdPreEnable. lc_HybridAF.cpp %d` `0x43c9d07e`. Ficheros fuente de la zona: `CamResource.cpp`, `CamSyncResource.cpp`, `SyncTask.cpp`, `ClockControl.cpp`, `SystemDelay.cpp`, `init_cam_SetCamParam_main.cpp`, `ImagingMain.cpp`, `InfraImaging.cpp`, `CS_imaging.cpp`, `lc_AF_Scan.cpp`, `lc_HybridAF.cpp`, `RCWrapper.cpp`, `DualRecResManager.cpp`, `StageResourceStack.cpp`, `CaptureUtilityCommon/RC/Debug/ExifMkNote.cpp`, `Spinal.cpp`… → el núcleo es un **gestor de recursos** con tareas de sincronización, control de reloj y planificador de secuencias.

**Diferencial**: la etiqueta `[CAMERA_MAIN]:` es **nueva en la fw3.21 de la A6000**: A7S fw3.20 y A6300 fw2.01 tienen **0** trazas con ese prefijo, pero **92** y **121** de los mensajes existen allí **sin etiqueta** → misma política de etiquetado por submódulo que en S106 (`[IMAGING_CAP]`), S119 (`[APL]` dentro de `[CAMERA_SA]`) y S120 (`[IDT_OPD]`).

[Informe](../analysis/s126_camera_main/camera_main.md) · [doc](../docs/capture/s126-camera-main.md). Siguiente: subdivisión de los 82 mensajes "sin etiqueta"; qué fichero fuente corresponde a cada función; significado de `waku`, `ympc`, `csum`, `cpeak`, `LoadNum`/`Ch`.

## S122 — el módulo `[CAMERA_MAIN_TC]` (127 trazas) de tiempo y giroscopio (21-10-2026, línea de RE general)

**VERIFICADO (40 tests, `tests/test_s122_camera_main_tc.py`):** 127 tokens `[CAMERA_MAIN_TC]` (127 textos distintos) en **6 tramos** entre `0x43ca7fd7` y `0x43ccb350`; **123 vivas** y 4 muertas; **256 sitios PIC** en **41 funciones** (regla estricta). Reparto por contenido: **GYRO/CALIB 32**, **DIST 13**, **APL/ApolloSA 47**, **SMART ZOOM 16**, **DDT 18**, JudgeBdroRslt 1. **17 publicadores** con prólogo uniforme `push {r3}` y primer `bl` a `osal_try_valloc_msg` `0x435612d0` (publicación por cola OSAL, con `memset` `0x439c5a04` y `osal_free_msg` `0x435612ec`). **Despachador `ApolloSA_Main` `0x438730b0`**: `tbb` de rango en `0x4387333e` (tabla `dfe805f005050914140d0f0d`) y `tbh` de 9 casos en `0x4387348e`, con el caso 3 convergiendo en `0x438735d8`; desde él salen los **6 clientes de `[APL]`** (S119), cada uno con un único llamador (`0x43873378`, `0x438733e6`, `0x43873418`, `0x4387343a`, `0x438734e8`, `0x4387352c`). Dos llamadores del módulo: la panorámica (`bl 0x438730b0` en `0x437f1324`, con `cmp r7,#2` en `0x437f12f6` y el error `0x43cacf9c`) y `0x438bdeac`.

**Diferencial**: la etiqueta es **nueva en la fw3.21 de la A6000**: A7S fw3.20 y A6300 fw2.01 tienen **0** apariciones del token, con **126/127** textos interiores literales y 123 sitios (frente a los 256 de la A6000).

**No toca la línea del obturador**: 0 apariciones de `shut`, `silent`, `electro`, `mech`, `sensor`, `exposure`, `drive`, `readout`, `jpeg`, `movie`, `bracket`, `sweep`, `interval` en sus 127 trazas → **S51 A/B/C = NO se mantiene**.

[Informe](../analysis/s122_camera_main_tc/camera_main_tc.md) · [doc](../docs/capture/s122-camera-main-tc.md). Siguiente: por qué se pierden sitios en la A7S/A6300 (idx 2, 32, 108); llamadas por puntero a `0x438786c4`/`0x43879204`/`0x438792dc`/`0x4387938e`; significado de TC/DDT/DIST/ARC/Gmv/Lmv; el pipeline interno de calibración, DIST, DDT y SMART ZOOM.

## S128 — el mapa de etiquetado de la fw3.21 (21-10-2026, línea de RE general)

**VERIFICADO (6 tests, `tests/test_s128_label_map.py`):** comparación **texto a texto** de los 98 prefijos de módulo con ≥ 8 cadenas entre la A6000 fw3.21 y la A7S fw3.20: **58 IGUAL** (la A7S usa el mismo prefijo y los textos coinciden), **18 RENOMBRADO** (la A7S **no** usa ese prefijo pero los textos coinciden: la fw3.21 **añadió la etiqueta**), 2 PARCIAL y 20 NUEVO/PROPIO. Los 18 renombrados: `[CAMERA_MAIN_YC]` (958/968), `[IMAGING_CAP]` (678/697), `[CAMERA_MAIN_SYNC]` (412/428), `[CAMERA_SA]` (228/231), `[CAMERA_MAIN]` (97/134), `[CAMERA_MAIN_TC]` (122/125), `[IMAGING]` (115/120), `[MOUNT_ERROR]` (78/80).

**Conclusión transversal**: la fw3.21 de la A6000 **no reescribe el firmware: reescribe el logging** — confirma, de forma transversal, lo medido hito a hito (S106 `[IMAGING_CAP]`, S119 `[APL]` dentro de `[CAMERA_SA]`, S120 `[IDT_OPD]`, S122 `[CAMERA_MAIN_TC]`, S126 `[CAMERA_MAIN]`). El único módulo con **cambio de contenido real y grande** es `[CAM_IMAGER]` (179/371 = 0.48; S124) y `[SFRS]` va al revés (117 en la A6000 frente a 151 en la A7S, S116).

[Informe](../analysis/s128_label_map/label_map.md) · [doc](../docs/capture/s128-label-map.md). Siguiente: comprobar uno por uno los 20 "NUEVO/PROPIO" (contenido nuevo o etiqueta distinta en la A7S).

## S123 — el módulo `[CAMERA_MAIN_CC]` (49 trazas) de control de captura (21-10-2026, línea de RE general)

**VERIFICADO (32 tests, `tests/test_s123_camera_main_cc.py`):** 49 apariciones del token `[CAMERA_MAIN_CC]` en 6 tramos contiguos de `.rodata` (control de captura 21 `0x43ca54c8`–`0x43ca5e30`, LUT 12 `0x43ca5f0a`–`0x43ca6158`, IE 8 `0x43ca6470`–`0x43ca6600`, miniRaw 2, MakerNote-playraw 2, CamCore-3DLUT 4 `0x43cb4cd3`–`0x43cb4d62`); **47/49** referenciadas (regla estricta, 1 sitio cada una) en **29 funciones** emisoras; las 2 huérfanas (`GetKDZMode()` `0x43ca5bb7`, `SetMovDevelopParam()` `0x43ca5d31`) tienen un par "ancho" demostrado como **falso positivo**. **Máquina de estados de 10 etapas** (cada método vivo delega en una función de etapa que escribe estado en `obj+0xb` y sub-paso en `obj+0xa`): `ExtractCaptureData`→`CaptureInit`→`SetReadImageParam`→`SetNRParam`→`SetOPDParam`→`AfterOPDAfterNR`→`SetDevelopParam`→`SetDualRecParam`→`SetDevDetectDevelopParam`→`WriteExifMakernote`. **Identidad de captura** (precisa S96): `CapMode`@`0x1c0`, `ExposureID`@`0x1b8`, `ContID`@`0x1bc`, `BDROSeq`@`0x6ec`, `BDRObase`@`0x6f4`, `FrameID`@`0x701`. **Clase `CC`**: nombres verificados en los bytes (`CcEncryptedTagData` `0x43ca9242`, `CcEncryptedFtTagData` `0x43ca9259`, `ImageParam_Capture` `0x43ca9802`; las direcciones `0x43ff8ee4`/`0x43ff8f24` son tablas de punteros/vptrs). **Grafo entrante**: 37 llamadas desde 22 funciones (`Stage_SACC.cpp` → `SetSACCParam`/`WriteSACCMakerNote`, `Stage_OPD.cpp` → `SetOPDParam`/`AfterOPDAfterNR`, `Stage_MARBLE.cpp`, `Stage_Orientation.cpp`, `CaptureUtilityModuleAPI.cpp`), **0 llamadas directas** a `[CAM_DMM]`/`[CAM_IMAGER]`/`[CAMERA_MAIN_YC]`: el enlace es por **tabla de parámetros compartida** `0x43ae9226` (ids `0x9408`/`0x9409`/`0x9410`).

**Diferencial**: A7S fw3.20 y A6300 fw2.01 tienen **0** cadenas con el prefijo (ninguno de los dos modelos tiene familia `[CAMERA_MAIN_*]`), con **47/49** mensajes idénticos sin etiqueta → coherente con el mapa de etiquetado de S128.

[Informe](../analysis/s123_camera_main_cc/camera_main_cc.md) · [doc](../docs/capture/s123-camera-main-cc.md). Siguiente: fichero(s) fuente que implementan la clase `CC`; significado de la sigla; rangos reales de `CapMode`/`ContID`/`BDROSeq`/`FrameID`; `drive_mode`↔`CapMode`; flujo completo de la LUT 3D.

## S130 — los 20 módulos "nuevos" del mapa de etiquetado (21-10-2026, línea de RE general)

**VERIFICADO (7 tests, `tests/test_s130_new_modules.py`):** buscando el **núcleo** de cada mensaje (el texto tras `"[PREFIX]: "`) como subcadena en la A7S fw3.20 y el A6300 fw2.01, de los 20 módulos que S128 clasificó como `NUEVO/PROPIO` solo **2 son un cambio de etiqueta** (`[IDT_OPD]`: 270 de 273 núcleos presentes en la A7S, todos bajo `[IDT]`; `[DFE]`: 11/11, 10 sin etiqueta y 1 con `[DFE]`), **1 es parcial** (`[JPEG]`: 4/17) y **17 tienen contenido que no está en los otros dos firmwares** (`[MOUNT_DEBUG]` 2/132, `[CAMERA_MAIN_LC]` 1/72, `[SAD]` 3/44, `[TP_R]` 2/18, `[ILLUMI]` 1/34 y `[ACCY]`, `[VPH_API]`, `[CLK_CTRL]`, `[CAM_UTIL_ADJ]`, `[CAM_UTIL_SENS]`, `[CAMERA_IS]`, `[DEPTH]`, `[JOG]`, `[ADC_DEBUG]`, `[LIF_DEBUG]`, `[PANDA]`, `[CAMERA_MAIN_FC]` con 0). Los tokens `ACCY`, `VPH_API`, `CLK_CTRL`, `CAMERA_MAIN_LC`, `MOUNT_DEBUG`, `ILLUMI` y `PANDA` **no aparecen ni una vez** en la A7S ni en el A6300.

**Detalle para la línea del obturador**: el módulo `[VPH_API]` (106 trazas, la API de cámara) incluye una **API de silenciador de obturador nueva en la fw3.21**: `<shutter_mute_param>` `0x43ce3634`, `<shutter_mute_param_sub>` `0x43ce3b5a`, `>shutter_mute<` `0x43ce3de4`, `>shutter_mute_status<o/f:%d` `0x43ce3dfc` (4 apariciones de `shutter_mute*` en la A6000, **0** en la A7S y el A6300), mientras que la traza del silenciador en sí (`shutter mute on/off`, `[SFRS][PINSEND]`, S118) **sí** está en los tres firmwares → la fw3.21 **añade el parámetro de API**, no el mecanismo (y el silenciador es del obturador **mecánico**).

**Advertencia**: la comparación mezcla **versión y modelo**; no hay una fw anterior de la A6000 en el repositorio, así que no se puede separar «nuevo en la fw3.21» de «propio de este modelo».

[Informe](../analysis/s130_new_modules/new_modules.md) · [doc](../docs/capture/s130-new-modules.md). Siguiente: qué son `[ACCY]`, `[VPH_API]`, `[CLK_CTRL]`, `[DEPTH]`, `[PANDA]` (sin desarrollar siglas); quién consume la API nueva de silenciador.

## S127 — el módulo `[CAMERA_MAIN_LC]` (72 trazas): AF, ZPD y DM AF (21-10-2026, línea de RE general)

**VERIFICADO (22 tests, `tests/test_s127_camera_main_lc.py`):** 72 cadenas `[CAMERA_MAIN_LC]` entre `0x43c9c6f6` y `0x43ca7e0b`; **78 sitios PIC** (regla estricta) en **37 funciones** y **1 cadena muerta** (`0x43c9c779`). **Corrección de la premisa del hito**: el módulo **no calibra la lente** — es la capa de **AF + ZPD + DM AF** (`Camera::LC` probado por RTTI; sigla **sin desarrollar**). Puente con el ZPD (S75): `LC_GetZpdResultInfo` (cadena `0x43ca78c8`, **función** `0x437c1e48`, prólogo `0xb5f7`), con gate `ldrb.w [rX,#0xc0]` + `tst.w #2` + `beq`, 10 lecturas de campo y 10 trazas; `full_count` es el primer argumento. Reparto real 32/40 (37/41 sitios) en 13 sub-bloques.

**Diferencial**: A7S fw3.20 y A6300 fw2.01 con **0** prefijos y **0/72** mensajes interiores coincidentes → material **propio de la A6000 fw3.21** (con la salvedad versión/modelo de S130 §4).

**Sin efecto en S51** (A/B/C = NO).

[Informe](../analysis/s127_camera_main_lc/camera_main_lc.md) · [doc](../docs/capture/s127-camera-main-lc.md). Siguiente: el layout completo del resultado ZPD; qué consume `LC_GetZpdResultInfo`; el significado de `lc_Movie_DM_AF_Util_*`.

## S131 — `[VPH_API]`: la API de parámetros del subsistema VPH (21-10-2026, línea de RE general)

**VERIFICADO (7 tests, `tests/test_s131_vph_api.py`):** 106 trazas `[VPH_API]` contiguas `0x43ce32e7`–`0x43ce3dfc` con **sintaxis de API explícita**: 49 entradas `<nombre>` (p. ej. `[VPH_API]<mode>` `0x43ce32e7`), 42 variantes `_sub` (`<mode_sub>` `0x43ce3781`), 11 salidas `>nombre<` (`>mode_status<` `0x43ce3d0e`) y 4 `=x=` (`=v_command_comp=` `0x43ce374b`) → **60 familias de parámetros** del subsistema de display (OSD, panel, salida de línea, muteos, ayudas de encuadre, línea de vídeo). Las emiten **48 manejadores** (uno por parámetro, una sola traza cada uno) en dos bloques: `0x4395aab8`–`0x4395b5f4` (39) y `0x4395e1b8`–`0x4395e34c` (9), de 52 a 160 B cada uno.

**Línea del obturador**: la API incluye el **silenciador del obturador** con 4 trazas (`<shutter_mute_param>` `0x43ce3634`, `<shutter_mute_param_sub>` `0x43ce3b5a`, `>shutter_mute<` `0x43ce3de4`, `>shutter_mute_status<o/f:%d` `0x43ce3dfc`): las 4 cadenas `shutter_mute*` **no existen** en la A7S fw3.20 ni en el A6300 fw2.01, mientras que la traza `shutter mute on/off` (`[SFRS][PINSEND]`, S118) **sí** está en los tres → la fw3.21 **añade el parámetro de API**, no el mecanismo (es el obturador **mecánico**, como `yuv_mute` y `chroma_mute`). **Sin efecto en S51.**

**Diferencial**: A7S fw3.20 y A6300 fw2.01 con **0** trazas `[VPH_API]` y 24 apariciones del token `VPH`, frente a las **106** trazas y **134** apariciones de la A6000 fw3.21 → el subsistema VPH es mucho mayor en esta fw; no solo se etiqueta (S128), es que la API completa no está en ellos.

[Informe](../analysis/s131_vph_api/vph_api.md) · [doc](../docs/capture/s131-vph-api.md). Siguiente: cómo se referencia la tabla de manejadores y quién la invoca; qué hacen `laxo`, `diceic_arb`, `line_fchr`, `set_eomainsub_inverse`; qué hace exactamente `shutter_mute_param` y quién lo consume.

## S129 — el módulo `[CAMERA_MAIN_IM]` (42 trazas) de control térmico (21-10-2026, línea de RE general)

**VERIFICADO (21 tests, `tests/test_s129_camera_main_im.py`):** 42 cadenas `[CAMERA_MAIN_IM]:` (40 contiguas `0x43ca6b32`–`0x43ca71e7` y 2 sueltas `0x43cb5fc1`/`0x43cb5ffa`); **43 sitios PIC** (regla estricta) en **10 funciones** (`0x43547362`, `0x437b8774` (22), `0x437b8e1c`, `0x437b8ed4`, `0x437b8fb0`, `0x437b9064`, `0x437b915c`, `0x437b91e8`, `0x437b93c0`, `0x4386bbec`); **0 cadenas sin referencia** y una con doble referencia (`0x43ca70f6`, `ImStartMovThermal set_timer:%x`, desde `0x437b90fe` y `0x437b9268`). **Despachador** `0x437b8384`: id u16 de `[ctx+0x10]` → 24 pares en `0x43befc32` (bytes `000a0000100a1000110a1100120a1200`), defecto `0xa00` (`0x437b8404`), `0xa20`→`0x437b9064`, `0xa21`→`0x437b915c`. Contenido: térmico del imager (`movie thermal diffTemp < 0`, `paramA%f paramB%f diff:%d`, `envOld:%d env':%d boot:%d`, `ImStartMovThermal set_timer:%x`). Enlaces: con el driver del imager (S115) en `0x437b877a bl 0x436d6118` / `0x437b8780 bl 0x436d648c` (slot `0x6c`), `vldr s14,[sp,#0x34]` ×`0x42c80000` (100.0f); con el bloque de parámetros por `drive_mode` (S124) en `ldrb` `0x437b87f6`/`0x437b87fe` (+6/+4) e intervalos `×0x186a0` en `0x437b8f42`/`0x437b90e4`/`0x437b924e`.

**Negativo verificado (importante)**: el módulo **no expone el obturador** — las únicas apariciones de `shut` en sus 42 trazas son la subcadena de `shutdownTh` en `0x43ca6ca8` y `0x43ca6d3f` (texto de `[CAM_IMAGER]`), y no hay `svd`/`shd`/`spl`/`sint`/`gs`/`epdsel` → **sin efecto en S51**.

**Diferencial**: 0 prefijos en la A7S y el A6300 con **34/42** y **33/42** textos interiores idénticos → módulo **RENOMBRADO** (el mecanismo térmico ya existía con otro etiquetado; la fw3.21 añade instrumentación).

[Informe](../analysis/s129_camera_main_im/camera_main_im.md) · [doc](../docs/capture/s129-camera-main-im.md). Siguiente: por qué `0x437b8774` no tiene ningún `bl` ni puntero de 32 bits en toda la imagen; el slot `0x6c` ↔ `GetImagerTemperature(float*)` `0x43c936a3` (inferido, no está en la vtable); los 24 ids del despachador.

## S134 — la aritmética de los parámetros del imager (21-10-2026, línea de RE general)

**VERIFICADO (8 tests, `tests/test_s134_imager_params.py`):** en la función validadora `0x4381106c` (prologo `push.w {r4-r8, sb, sl, lr}`) del módulo `[CAMERA_MAIN_SYNC]`, la relación **`shut`→`svd` es aritmética y no tabulada**: `svd_esperado = (svd == 9 ? 1 : shut) * svr_num − 1` con `svr_num` = u8 en `[estado+0x14e]`, o `= (svd == 9 ? 1 : shut) / VdNum − 1` cuando `VdNum` (u16 en `[estado+0xcc]`) > 1, con la división sin signo en `0x4355faf0` (tipo `__aeabi_uidiv`). El desbordamiento (bit 15 tras `uxth`) dispara `Imager param error shut:%d, svr_num:%d, VdNum:%d` `0x43cb11d2` (sitio `0x4381110e`) e `Imager svd error. shut:%d, svd:%d -> %d` `0x43cb1217` (sitio `0x43811162`); el volcado completo es `shut:%d, svd:%d, shd:%d, spl:%d, sint:%d, gs:%d` `0x43cb1253` (sitio `0x438111d4`). **Procedencia de los seis parámetros**: `shd` = `[estado+0x24]` (u32), `svd` = u16 bajo de `[estado+0x28]`, `spl` = u16 **alto de la misma palabra** (`svd` y `spl` van empaquetados), `sint` = u8 de `[estado+0x2c]`, `gs` = **flag binario** (1 si el `svd` del contexto vale 9, si no 0: `cmp r3,#9` + `subs r3,#8` / `movs r3,#0`), `shut` = `[ctx_sync+0x1f8]`. El estado se obtiene con un **accesor de singleton** `0x4378f9b4` → global `0x43e99208` (cero en el blob).

**Conclusión para S124**: **descarta** la hipótesis de una «tabla de valores por `drive_mode`» para `svd`; el peso de `shut` está en la fórmula. El bloque de modo que S124 vio leer (`[r1+0]`, `[r1+4]`, `[r1+6]`, `[r1+9]`) **sigue sin localizar**. `shut` sigue siendo el índice/contador de obturación, no un selector de mecanismo → **sin efecto en S51**.

[Informe](../analysis/s134_imager_params/imager_params.md) · [doc](../docs/capture/s134-imager-params.md). Siguiente: qué son `svr_num` y `VdNum` y quién los escribe; por qué `svd == 9` es un centinela; si la A7S fw3.20 usa la misma fórmula.

## S125 — `[IMAGING_REL]` y `[IMAGING]`: el liberador de recursos y el motor de panorama (21-10-2026, línea de RE general)

**VERIFICADO (38 tests, `tests/test_s125_imaging_rel.py`):** **"REL" = RELease, y está en el RTTI** (nombre mangled `N6Camera11ReleaseLock9RelLockS1E` en `0x43ca5489`; `RelLockBase` `0x43ca54bb`, `RelLockS2` `0x43cb4b75`), no es una sigla inventada. **`[IMAGING_REL]`**: 31 cadenas `0x43c9c520`–`0x43cb4bc4`, 30 referenciadas, **34 sitios** en **26 funciones**; es el gestor `RelMgr` `0x4379d114`–`0x4379e600` con despachador `REL_EVT` `0x4379d83a` (`subs r2,r3,#1` + `cmp r2,#0x26` + `tbh` → ids `0x01`–`0x27`) y el bloque `CapIdTblMgr`/`RelQueue`/`RelLock` `0x4381c30c`–`0x4381d150`; fichero fuente **`Spinal.cpp`** `0x43c9c54f`; el programa es el **LIRO** (S105). Una cadena **muerta**: `0x43c9c520` (`Spinal) osal_free_timer`), también muerta en la A7S. **`[IMAGING]`**: 120 cadenas `0x43c9b47c`–`0x43cc6c99`, 82 referenciadas, **608 sitios** en **346 funciones**; 3 genéricas (`FATAL! %s:%d` literal en `0x43c9b487`, **443 sitios**; `FATAL! %s:%d [0x%x]` `0x43c9f6d9`, 29; `%s:%d \n` `0x43cabafb`, 1) = el macro de todo el subsistema de captura, y 117 específicas del **motor de panorama/stitch** (`still_cnt_panoramaSweep.cpp` 62 sitios, `still_seq_panoramaStitch.cpp` 25, `still_cnt_panoramaStitch.cpp` 15, `still_seq_enc.cpp` 12, `src/stitch/ddl_stitch.cpp`…), con direcciones que coinciden con la cadena de S105 y con el motor de secciones de S114 (que no emite mensajes específicos).

**Diferencial**: A7S fw3.20 y A6300 fw2.01 con **0** trazas etiquetadas. `[IMAGING]`: **115/120** comunes texto a texto y **5 nuevas** de la fw3.21 (4 `[PanoramaSweepEnd]…` + `[seq_panoramaParallelStitch][OK] StitchProc ALL OK`); `[IMAGING_REL]`: 30/31 en la A7S (1 nueva: `(%d,%d,%d)` `0x43ca3887` en `SyncTask.cpp`) y 22/31 en el A6300 (que sí tiene `Camera::ReleaseLock`). Las 38 cadenas sin referencia de `[IMAGING]` **ya estaban muertas en la A7S**.

**Sin efecto en S51**: ninguno de los dos módulos menciona `shutter`/`silent`/`EFCS` ni mecanismo de obturación.

[Informe](../analysis/s125_imaging_rel/imaging_rel.md) · [doc](../docs/capture/s125-imaging-rel.md). Siguiente: significado de `irp/cidx/rp/wp/wpd/dm` e `InnerRP`; ids concretos de `REL_EVT`; por qué la fw3.21 etiqueta con `[IMAGING]:` el `FATAL!` genérico de toda la captura.

## S135 — el subsistema `ElecShutter` del A6300 como control positivo (21-10-2026, línea de RE general + línea del obturador)

**VERIFICADO (25 tests, `tests/test_s135_elec_shutter.py`):** barrido literal de una batería de términos de obturador electrónico en los tres `av-cam.bin`. El **A6300 fw2.01 sí tiene** un subsistema de obturador electrónico: `ElecShutter/EC_ElecShutter_Main.cpp` `0x43dcfa41`, `ElecShutter/EC_NonlinearElecShutter_MechShutterTable.cpp` `0x43dcfa65` (seguida de la tabla de códigos de velocidad no lineal `0x43dcfa9e`: `00 01 03 04 05 06 08 09 0a 0b 0d 0e 0f 10 12 13 14 16 17 18 19 1b 1c 1d 1e 1f 21 22`), los ajustes `SET Silent Shutter Type: %d` `0x43dc4f43`, `LiroSeq ParamCheckErr@%s[SilentShutterMode]…` `0x43dc9a14`, `[shutterType]` `0x43dca61f`, `[front_eshutter]` `0x43dc821d` y `CheckSetSilentShutterMode` `0x43dca9ad`, `CheckSetShutterType` `0x43dcb09c`, `CheckSetFrontEshutter` `0x43dca84a`; además el motor `EC` (`job_EC_move_iris error:[%x]` `0x43dcf97d`, `CapRawDSLR::ECShare is NULL![%d]` `0x43dcf9cd`, `EC::ISO Range Error…` `0x43dcf9ee`, `EC::CapISO Error…` `0x43dcfa1c`). La **A6000 fw3.21 y la A7S fw3.20 tienen 0** de todo eso (`efcs`/`EFCS`, `electronic`, `curtain`, `mechanical`, `flicker` y `silent` en minúsculas: 0 en los tres). La única coincidencia de la A7S es el diagnóstico `SET Silent Shutter Type: %d` `0x43ca4b6b` (ya documentado en `work/claude/a7s_silent_execution_trace.md`, convertidor `0x4379ec04`).

**La ausencia en la A6000 es selectiva**: sí tiene el motor de exposición `EC` (`EC::EcTagData` `0x43ca91ce`, `EC::EcEncryptedTagData` `0x43ca9227`, `EC::EcAmcTagData` `0x43ca931b`, `api_EC_GetApolloLapNum()` `0x43caa193`); lo que falta es **exactamente** la sub-rama `ElecShutter/`. Sus 15 apariciones de `shutter`/`Shutter` son del **obturador mecánico** (silenciador `VDF::ShutterMuteOffExecutor` `0x43c851d8`, `[SFRS][PINSEND] shutter mute thru` `0x43ce956e`, `[VPH_API]<shutter_mute_param>` `0x43ce3634`) y del disparo táctil (`[CAMERA_MAIN_FC]: ReplyForTouchShutter` `0x43ca6a85`).

**Lectura**: es un **control positivo** — cuando un firmware de Sony trae obturador electrónico en esta capa deja huellas inequívocas, y la A6000 fw3.21 no tiene ninguna → su HAL **no implementa** un subsistema de obturador electrónico. Refuerza la conclusión vigente de **S51 (A/B/C = NO)** y complementa a S101 (allí el selector de tipo de mecanismo `0x4379316a` tenía valor 0 por defecto y sin escritor; aquí se ve que tampoco existe el módulo que lo interpretaría). **Límite**: la ausencia estática no demuestra incapacidad del hardware, solo la no implementación en el HAL (la prueba física P0–P8 sigue pendiente).

[Informe](../analysis/s135_elec_shutter/elec_shutter_scan.md) · [doc](../docs/capture/s135-elec-shutter.md). Siguiente: si el módulo `ElecShutter` del A6300 se ejecuta; si la política EFCS de la A6000 en `libObj.so` (E012) es el mismo concepto (capas distintas, no enlazado); si una fw anterior de la A6000 lo tuvo.

## S133 — el módulo `[MOUNT_DEBUG]` (132 trazas) de diagnóstico de la montura (21-10-2026, línea de RE general)

**VERIFICADO (42 tests, `tests/test_s133_mount_debug.py`):** 132 cadenas `[MOUNT_DEBUG]` entre `0x43c9648d` y `0x43c9a10f`, **148 sitios PIC** (regla estricta) en **65 funciones** y **9 sinks**; con `[MOUNT_ERROR]` (80), `[MOUNT_INFO]` (6) y `[MOUNT_WARNING]` (5) son **223 trazas `[MOUNT_*]`**. En la A7S fw3.20 y el A6300 fw2.01: **0** cadenas con esos prefijos y **0/132** mensajes interiores idénticos → material **propio de la A6000 fw3.21**; pero el mecanismo de captura (`/mnt/Mount_ms_log_%03d.dat`) y el módulo Eclipse son **preexistentes** en las tres cámaras → lo nuevo es la *instrumentación*, no la función. El subagente comprobó además la sensibilidad de los tests (cambiar una dirección o el `push {r3}` de `0x436e03b0` hace fallar 5 pruebas).

**Negativo acotado**: ninguna traza del módulo menciona obturador, sensor, apertura, actuador ni autofoco → **sin efecto en S51**.

[Informe](../analysis/s133_mount_debug/mount_debug.md) · [doc](../docs/capture/s133-mount-debug.md). Siguiente: atribución de módulo de los puentes `0x4377e0e8` y `0x437d24c8`; el consumidor de `osal_snd_msg`; la semántica de los códigos `CS_*`/`PowerSeq` y de los estados 0-2.

## S137 — `[CTRLCORE]`: la sub-etiqueta del núcleo de control de códec (21-10-2026, línea de RE general)

**VERIFICADO (54 tests, `tests/test_s137_ctrlcore.py`):** 55 cadenas con el token `[CTRLCORE]` entre `0x43c3b82d` y `0x43cdb492`, **74 sitios PIC** (regla estricta) en **16 funciones** emisoras, **74/74 recalculados de forma independiente** por `analysis/s137_ctrlcore/verify_sites.py` (`ldr` del mismo registro → literal → `destino = W + add + 4`). **Corrección de la premisa del hito**: `[CTRLCORE]` **no es un módulo de primer nivel**, es una **sub-etiqueta de segundo nivel** (como `[APL]` dentro de `[CAMERA_SA]`, S119): `[CDIAG][CTRLCORE]` (51, clase `CdCtrlCore`), `[MCSENS][CTRLCORE]` (1, `McSensCtrlCore`) y `[AMSENS][CTRLCORE]` (3, `AmSensCtrlCore`). Capas: `CdCtrlIf` despacha y `*CtrlCore` ejecuta, con `ExecCmd` (comandos `MSG_SENS_COMMAND` `0x435a1424`), `ExecSensCmd` (`0x435a15e8`) y `ExecSensComp` (`0x435a17e8`); ficheros `cdCtrlCore.cpp` `0x43c3b86c`, `mcSensCtrlCore.cpp` `0x43c73689`, `amSensCtrlCore.cpp` `0x43cdb45a`, `mcAvCtrlCore.cpp` `0x43c454e8`.

**Diferencial**: A7S fw3.20 con **55/55** cadenas idénticas (mismas operaciones y ficheros); A6300 fw2.01 con **90** = las 55 comunes + 14 `[CDIAG][CTRLCORE] … 4K` + 21 `[CDEXT][CTRLCORE]` (`CdExtCtrlCore` **no existe** en la A6000).

**Negativo acotado**: ninguna de las 55 cadenas menciona obturador, disparo, cortinilla ni lectura del sensor → **sin efecto en S51**.

[Informe](../analysis/s137_ctrlcore/ctrlcore.md) · [doc](../docs/capture/s137-ctrlcore.md). Siguiente: nombre de `0x439b4244` (registro de mensaje/clase); los ids `0x32`/`0x33` de `ExecSensCmd`; la entrada indirecta a `ExecSensCmd`/`ExecSensComp`.

## S132 — el módulo `[CLK_CTRL]` (66 trazas): el control de reloj (21-10-2026, línea de RE general)

**VERIFICADO (180 tests, `tests/test_s132_clk_ctrl.py`):** `[CLK_CTRL]` es el **etiquetado de un subsistema ya existente**, no un módulo nuevo: el gestor de control de reloj **ClkCtrl** de la A6000, expuesto como **14 funciones DDL** (`ddl_clkctrl_*`), con **tarea propia**, **máquina de estados**, **arbitraje** (abrir/cerrar el reloj, bloquear/desbloquear la señal de sync) e **intercambio maestro/esclavo**. Las **66 trazas** viven en `0x43c3a1df`–`0x43c3b09c`; con la regla estricta: **62/66 referenciadas**, **85 sitios de emisión** en **36 funciones**, todas en el cluster de código `0x4359ee24`–`0x435a1150`; **4 cadenas sin referencia** (`0x43c3a2a6`, `0x43c3afc0`, `0x43c3afe4`, `0x43c3b007`), verificadas sin referencia PIC (mapa global de 17 525 destinos) **ni** puntero absoluto de 4 B → texto muerto. Cadillas verificadas: `CALL CB3` `0x43c3acae`, `ClkCtrl` `0x43c3aef0`, `[CAMERA_MAIN]: init_cam_clkctrl CLKTYPE=%x, sysv_delay=%dus` `0x43ca3be5`, `ddl_clkctrl_set_sync_signal err = %d` `0x43c3aea5`; despachador DDL `0x435a0880` (prólogo `0xb570`).

**Diferencial**: la etiqueta es **nueva en la fw3.21 de la A6000** (66 apariciones; **0** en la A7S fw3.20 y el A6300 fw2.01) y **los 66 núcleos de mensaje no existen** en los otros dos, pero los tres comparten **la misma tabla de 14 nombres de API DDL** y los mismos mensajes de inicialización → **lo nuevo es la instrumentación (trazas + traza de la llamada DDL), no la funcionalidad** (26 apariciones de `ddl_clkctrl_` en la A6000 frente a 14 en la A7S y 15 en el A6300).

**Para la línea del obturador**: el módulo fija (a) el **tipo de reloj** `CLKTYPE` (24P/25P/30P/50I/50P/60I/60P) y (b) el **retardo de sincronía vertical** `sysv_delay` (µs). No fija frecuencias en Hz ni divisores de obturación y ninguna de sus 66 trazas menciona obturador: gobierna la **duración del frame** y, por tanto, el presupuesto temporal de exposición y lectura, de forma **indirecta** → **sin efecto en S51**.

[Informe](../analysis/s132_clk_ctrl/clk_ctrl.md) · [doc](../docs/capture/s132-clk-ctrl.md). Siguiente: qué ajustes exactos hace `sysv_delay` sobre el presupuesto de exposición; la relación entre `CLKTYPE` y `change_vfc`/`subVFC` (presentes solo en la A6000).

## S136 — el módulo `[ACCY]` (106 trazas) de accesorios (21-10-2026, línea de RE general)

**VERIFICADO (16 tests, `tests/test_s136_accy.py`):** 106 cadenas `[ACCY]` en el bloque contiguo `0x43c24cac`–`0x43c26319`, **111 sitios PIC** (regla estricta) en **61 funciones** (`0x43562a08`–`0x43566f20`), las 106 referenciadas (0 muertas), en **15 sub-bloques** `[ACCY][nivel][sub]`: HW1, Main 9, MAIN 4, SENSER 3, UART 13, UTILITY 2, FACTORY 7, HOUSING 5, AVOUT 2, AVR 2, BASE 7, HELLO 16, JIRO 2, NULL 1, REMOTE 32. **9 clases RTTI `AccyUm*`** intercaladas (`0x43c2536d`–`0x43c26340`) con tabla `type_info` en `0x43fd7c8c`–`0x43fd7dbc`: `AccyUmDeviceBase` + 7 derivadas (`WaterHousing`, `AvOut`, `Avr`, `Hello`, `Jiro`, `Null`, `Remote`); `AccyUmKeyStatusMgr` sin clase base. Taxonomía (`FACTORY` `0x435646a4`): ID `0`=AvOut, `1`=JIRO1.5, `4`=HELLO, `5`=LANC-AVR, resto `UNSUPPORTED`; máscara `0x80`=Remote, `0x40`=WaterHousing. Transporte: UART propio (`AccyUartOpen` `0x43563bf8`, `Close` `0x43563de8`, `Send` `0x43563ef4`) + OSAL (`0x435612d0`/`0x4356120c`/`0x435612ec`); GID emisor `0x008F0139` (`0x43562284`); `NotifyInput` `0x43565814` entrega `{KeyCode,ID,State,INFO}`.

**Corrección de la premisa (hallazgo)**: `[ACCY]` = **0** trazas en la A7S fw3.20 y el A6300 fw2.01 y **0/106** textos presentes allí, **pero el módulo sí existe** en ambos: las mismas 9 clases `AccyUm*` (bloque RTTI `0x43c25a23`–`0x43c25afc` en la A7S y `0x43d0c9a2`–`0x43d0ca7d` en el A6300) están presentes **sin trazas**, con tabla de nombres de comando (`accy`, `edr`, `SendCommand`…) y dos clases `AccyMi*` que la A6000 no tiene → lo propio de la fw3.21 de la A6000 es el **logging**, no el módulo.

**Para la línea del obturador**: 0/106 trazas mencionan obturador, flash, lente, montura o batería; el **disparador remoto aparece solo como tecla del mando** (`START STOP OFF` `0x43c260b0` → `KEY:0x0A00000D` en el pool `0x43566cfc`), entregada como evento genérico por `NotifyInput` → **no decide ni ejecuta el disparo**. La montura (S66) es un subsistema **distinto** (otro UART, otro protocolo) → **sin efecto en S51**.

[Informe](../analysis/s136_accy/accy.md) · [doc](../docs/capture/s136-accy.md). Siguiente: significado de `ACCY`/`UM`/`Spinal`/`GF`/`SS`/`Tally`/`JIRO`/`AVR`/`LANC`/`AISATSU`; la tabla de teclas `0x0A0000xx` → acción; la cola OSAL destino (`0x007A0020`); el papel de las clases `AccyMi*`.

## S139 — el módulo `[ENCSEQCTRL]` (46 trazas): el control de secuencias de codificación (21-10-2026, línea de RE general)

**VERIFICADO (35 tests, `tests/test_s139_encseqctrl.py`):** 46 cadenas `[ENCSEQCTRL]` en `0x43c4bce5`–`0x43c4c796`, **46/46 referenciadas**, **96 sitios PIC** (regla estricta, **96/96 reconfirmados** de forma independiente) en **32 funciones** (`0x435d6ad0`–`0x435d90ac`), 0 muertas. La clase es **`McAvcEncSeqCtrl`** (RTTI `0x43c4320f`), con fichero **`seqCtrl/mcAvcEncSeqCtrl.cpp`** `0x43c4bd0f` y componente **`Avbb-MovieCodec_131H`** `0x43c41227`; id de log `0x0e` en las 82 llamadas al logger. **18 ids de mensaje** `0x8101`–`0x8112` (`tbh` en `0x435d8d50`, despachador `ProcAvcMsg` `0x435d8d38`): 12 con nombre (`OPEN_COMP`…`GET_ES_NOTIFY`) y 6 sin nombre. Estado = u32 en **`obj+0x15B84`** (getter `0x43a5d2da`, setter `0x435d715c`, 17 llamadores; estados vistos 0,1,2,3,4,6,7,8,10,11). Tabla **O/U Crank** de 57×8 B en `0x43b93bf4`; **35 nº de línea** del `.cpp` recuperados (89–2237). Relaciones: S132 solo temporal (razona en **VFC**, 0 menciones de `CLKTYPE`); S137 por la interfaz `mcAvCtrlIf/mcAvCtrlCore` y el evento `AVSC_CID_MPRNTFY_ENC_SA_CONFIRM_EVENT` `0x43c4c332`; S106 indirecta vía `[SYNCENCSTART]` (`0x43620dd0`–`0x43621298`); S114 y S115 sin relación (0 llamadas cruzadas).

**Diferencial**: A7S fw3.20 **idéntico** (46/46 textos, 96 sitios, 32 funciones y la tabla `tbh` de `ProcAvcMsg` **byte a byte igual**: `0x435d69e0` frente a `0x435d8d50`); A6300 fw2.01 = **superset** (50 cadenas, 100 sitios, 34 funciones; 45 comunes y 5 nuevas: `quickRestartVfc`, `ouCrankStopVfc`, `Remain/gopNum`, `EnsRestartTime(VFC)`, `Audio Buffer Overflow…`).

**Negativo acotado**: 0 apariciones de `shut`/`silent`/`electro`/`mech`/`sensor`/`imager`/`expos`/`drive`/`readout`/`bracket`/`sweep`/`flicker`/`curtain` en sus 46 trazas → **sin efecto en S51**.

[Informe](../analysis/s139_encseqctrl/encseqctrl.md) · [doc](../docs/capture/s139-encseqctrl.md). Siguiente: qué es exactamente `VFC`; la semántica de la tabla O/U Crank; los 6 ids de mensaje sin nombre; quién crea el objeto de la clase (0 punteros absolutos de 4 B).

## S138 — el módulo `[CAMERA_MAIN_FC]` (9 trazas): el glue hacia `Camera::FC` (22-10-2026, línea de RE general)

**VERIFICADO (53 tests, `tests/test_s138_camera_main_fc.py`):** 9 cadenas `[CAMERA_MAIN_FC]:` en `0x43ca6944`–`0x43ca6aec` (**0** en la A7S fw3.20 y el A6300 fw2.01), **13 sitios PIC** (regla estricta, **recalculados a mano 13/13** por `verify_sites.py`) en **7 funciones** del bloque `0x437b7200`–`0x437b821e`, con logger propio en `0x437b7158` (11 llamadas). Contenido: `Eye data is invalid, but lc flag is true.` (dos flags del contexto, `[ctx+0xde]` y `[ctx+0xdf]`, deben valer 1), `OSAL_ERROR: osal_alloc_timer`/`osal_set_timer`/`osal_free_timer` (`0x437b74a4` alta/activación, `0x437b7778` baja), `APP MODE ERROR: face_on, obj_on` (`0x437b7844`: error si `[ctx+0x49c]` y `[ctx+0x49e]` están ambos activos), `OSAL_ERROR: BatteryInfo` (`0x437b7d6c`) y las tres de disparo táctil (`ReplyForTouchShutter ERROR - NULL cb_func`, `SetRequestReplyForTouchShutter ERROR - multiple request`/`- NULL cb_func`).

**La sigla `FC` tiene base textual** (no inventada): es el *namespace* C++ `Camera::FC` (**45** apariciones de `Camera::FC::` y **101** de `FC/` en **los tres** firmwares) con el árbol `FC/**/*.cpp` (99 ficheros) → la biblioteca es común a las tres cámaras; lo propio de la A6000 fw3.21 es el *logging* del *glue* `CAMERA_MAIN`→`Camera::FC`.

**Negativo bien acotado**: el módulo **no participa en la cadena de disparo táctil** documentada (`0x4379d838`, `0x4379e6a8`, `0x4379eba0`→`0x3011`, `0x43809ed8`, `0x437df640`, `0x437df338`, `0x437eabfc`, `0x437e4de4`): ninguna de esas funciones llama a la zona del módulo ni a `Camera::FC`. El módulo **sí** tiene su **propia** API de respuesta al disparo táctil (`ReplyForTouchShutter`/`SetRequestReplyForTouchShutter`), cableada por `wrapper/Face.cpp` → **camino distinto**, lo que evita un falso positivo de correlación.

[Informe](../analysis/s138_camera_main_fc/camera_main_fc.md) · [doc](../docs/capture/s138-camera-main-fc.md). Siguiente: quién invoca la API de respuesta al disparo táctil del módulo y qué la connects con la cadena `0x3011`; el significado de `[ctx+0xde]`/`[ctx+0xdf]` (flags de `lc`).

## S143 — el módulo `[CAM_UTIL_ADJ]` (22 trazas): la utilidad de ajuste de la cámara (22-10-2026, línea de RE general)

**VERIFICADO (30 tests, `tests/test_s143_cam_util_adj.py`):** 22 cadenas `[CAM_UTIL_ADJ]` en el bloque contiguo `0x43ccdcee`–`0x43cce0f2`; **22/22 referenciadas**, **22 sitios** (1 por cadena) en **3 funciones** (regla estricta canónica, aritmética `ldr`/`add` verificada a mano): `0x439007b0`–`0x439008ac` (Table Write/Read, 6 trazas), `0x43900a24`–`0x43900bde` (`cam_adjcmd_handle_cb()`, 13) y `0x43900c44`–`0x43900d30` (`tsk_cam_adjctrl`, 3). Tabla de despacho en `0x440121f8`: idx 1 → `0x439007b0`; idx 0 y 2 → stub `0x43b2a0b8` (**1 de 3 operaciones implementada**); puntero del callback `0x43900a25` registrado en `0x4401f7a4`. **Tabla de comandos «Sens»** (`{cmd,size,str}` de 12 B) en `0x43fe858c`: **51 entradas** `0x0400015d`–`0x0400018f`, con `Sens:AdjCmd CAIF` `0x04020180`, `Sens:RAM Write` `0x04000188`, `Sens:RAM Read` `0x04020189`, `Sens:AdjCmd DwnCamera` `0x0400018a`.

**Diferencial (hallazgo de fondo)**: la **etiqueta** es propia de la A6000 fw3.21 (token 22 / **0** / **0**; interiores **0/22** en A7S y **0/22** en A6300; tampoco existen allí `[CAM_UTIL_SENS]`, `[CAM_UTIL]`, `[CAMERA_ADJ]`), **pero la capa de comandos «Sens» es común a los tres**: 27 cadenas `Sens:*` idénticas y **51 entradas con los mismos cmd y size** (única diferencia de texto: cmd `0x04000167` = `Reserved` vs `POFF return`) → lo nuevo en la A6000 es la **instrumentación**, no la función.

**Para la línea del obturador**: el módulo **no toca** obturación, iris, ISO ni lectura de sensor; los únicos destinos de llamada de las 3 funciones son el log `0x43900728`, OSAL `0x43561260`/`0x435612ec`, `[CAM_UTIL_SENS]` `0x439023b8`, `0x4390092c`/`0x439009f0`/`0x439009c8`/`0x439009c1c` y memcpy/memset → es una **vía genérica de escritura de calibración en la RAM del sensor**, no el punto de materialización de un Silent/EFCS → **sin efecto en S51**.

**Colateral reutilizable**: la convención **vaddr = 0x43541000 + offset** también vale para la A7S fw3.20 y el A6300 fw2.01 (verificado con los punteros de la tabla `Sens`) → confirmado con otro par de blobs.

[Informe](../analysis/s140_cam_util_adj/cam_util_adj.md) · [doc](../docs/capture/s140-cam-util-adj.md). Siguiente: qué `Module ID` corresponde a iris/ISO/shutter/WB; los ids OSAL `0x008f013a` y la plantilla `0x43c04d70`; los índices 0 y 2 de la tabla de despacho; el módulo `[CAMERA_ADJ]`.

## S144 — el módulo `[CAM_UTIL_SENS]` (21 trazas): la interfaz de ajuste hacia el sensor (22-10-2026, línea de RE general)

**VERIFICADO (22 tests, `tests/test_s144_cam_util_sens.py`):** 21 cadenas `[CAM_UTIL_SENS]` en `0x43cce1ea`–`0x43cce66b` (bloque `0x43cce1ea`–`0x43cce6ad`, con 3 cadenas `[CAM_UTIL]` intercaladas en `0x43cce282`–`0x43cce2f3`); **21/21 referenciadas**, **39 sitios** (regla estricta) en **5 funciones**: `0x439012d0` (CB de BKID), `0x43901d50` (Debug IM ASync Open, con camino sync en `0x43901ef8`), `0x43902168` (SET FILE NUM), `0x439023b8` (UTIL MS Mgr Call CB) y `0x43902418` (Debug IM Sync Open). Globales: plantilla/parámetros `0x43f062c8`, «MountSTAT» `0x43fa29f0`, «Flg» `0x43fa2d23`, puntero al callback del gestor MS `0x43f062d4`, tabla de objetos `0x4401eee4`. **Ids OSAL compartidos con `[CAM_UTIL_ADJ]`** (S143): log `0x008f0139`, comando `0x008f013a`, id de módulo `0xb5`; **dependencia cruzada verificada**: ADJ→SENS `0x43900c9c`, SENS→ADJ/`[CAMERA_ADJ]` `0x439012fa` (Mount) y `0x43901302` (UnMount) → son **el mismo par**. El CB de BKID tiene **0 `bl`** y se registra por puntero absoluto `0x439012d1` en `0x44022d84`.

**Pieza transversal**: **17 llamadas** a `0x43901d50` desde `[CAMERA_MAIN_LC]`, `[IMAGING_CAP]`, `[CAMERA_MAIN_TC]`, `[CAMERA_MAIN_YC]`, `[IDT]`/`[IDT_OPD]` → `cam_util_debug_file_write` es la pieza que **vuelca imagen (RAW/YC) en la memoria del sensor**: un sumidero de depuración transversal, no un módulo de captura.

**Diferencial**: la etiqueta es **propia de la fw3.21** (21/0/0; interiores 0/21 y 0/21), **pero la funcionalidad ya existía en los tres** (`cam_util_debug_file_write` 3/2/2, `MemAreaMSDebug` 4/4/10, `Sens:` 27/27/27) → lo nuevo es la **instrumentación**, no la función.

**Negativo acotado**: 0 coincidencias de `shut`/`iris`/`iso`/`exposure`/`silent`/`elec`/`efcs`/`fps` en las 21 trazas ni en las 47 cadenas de la banda `0x43901000`–`0x43902610`; destinos de llamada solo OSAL, thunks y memcpy → **sin efecto en S51**.

[Informe](../analysis/s144_cam_util_sens/cam_util_sens.md) · [doc](../docs/capture/s144-cam-util-sens.md). Siguiente: siglas «IM»/«MS» (sin expansión en los bytes); semántica de `BKID`/`SWFLG`/`MODEFLG`/`MountSTAT`/`FsysMode`; naturaleza de la tabla de `0x44022d84`; el canal exacto hacia el driver.

## S148 — el módulo `[DEPTH]` (16 trazas): el medidor de profundidad (22-10-2026, línea de RE general)

**VERIFICADO (25 tests, `tests/test_s148_depth.py`):** 16 cadenas `[DEPTH]` en `0x43c249ec`–`0x43c24c73` (11 `INFO`, 2 `DEBUG`, 3 `WARN`); **0** en la A7S fw3.20 y el A6300 fw2.01; **17 sitios de emisión** (regla estricta, **verificados a mano** los 17) en **11 funciones** (`0x43541b00` `update`, `0x4356228c` `enableDummyRecv`, `0x435622d4` Rsp, `0x4356230c` `getMsg`, `0x43562354` `notifyOff`, `0x435623bc` `notifyOn`, `0x43562424` `getLiro`, `0x43562454` `update`, `0x43562634` GET, `0x43562660` NOTIFY, `0x435626d4` despachador); 0 cadenas sin referencia y ningún puntero absoluto de 4 B.

**No es un módulo nuevo**: la clase **`DepthGaugeMain`** (RTTI `14DepthGaugeMain` `0x43c24b85`, `type_info` `0x43fd7c84`, vtable `0x43fb8f50`) está **en los tres firmware** (1/1/1) y se registra con el nombre **`depth`** (`0x43c24b46`) en `0x435ab6f0`; **tabla de 6 comandos** de 12 B en `0x43fd7c30` (`update`, `getLiro`, `getMsg`, `notifyOn`, `notifyOff`, `enableDummyRecv`); GID **`0x018b04dc`**; ids de notificación 1=GET / 2=NOTIFY_ON / 3=NOTIFY_OFF (`0x435626d4`); `valueDepth` acotado a **0xFA0 = 4000** (`0x43541b04`) → la fw3.21 de la A6000 **añade solo el logging** (patrón S130/S132/S136).

**Consumidor real (aportación)**: `CS_ExifMakerNote.cpp` (`0x43cc56dc`) → `getMsg` en `0x438b900a` → tag Exif **0x5001** = racional `(valueDepth*10 : 1000)` (`0x438b90a8`) y **0x5002** = estado (`0`/`1`/`0x80`/`0x81`, `0x438b90b8`); segundo consumidor: `[ACCY]` → `update` en `0x43564dc0`/`0x43564ed2`. La "profundidad" sale a la **EXIF** de la foto.

**Negativo acotado**: 0/16 menciones de obturador/sensor/exposición/enfoque/lectura/distancia (`shut`, `shutter`, `silent`, `electro`, `mech`, `sensor`, `exposure`, `readout`, `focus`, `af`, `dist`, `iso`, `aperture`, `iris`, `zpd`, `imager`, `drv`, `drive` = 0 cada uno) y los **26 destinos de llamada** del módulo no salen de él (cero llamadas a `[CAM_IMAGER]`, `[CAMERA_MAIN*]`, `[IDT_OPD]`, `[VPH_API]`/`[VDF]`) → **S51 A/B/C = NO intacto**.

[Informe](../analysis/s148_depth/depth.md) · [doc](../docs/capture/s148-depth.md). Siguiente: qué magnitud física mide `valueDepth` (0..4000) y qué significa `status`; el receptor final del GID fuera de `av-cam.bin`; por qué `[ACCY]` publica `update` con `status=2`; el sentido de `0x80`/`0x81` en el MakerNote.

## S151 — el módulo `[PANDA]` (10 trazas): el gestor de mensajes del drive de iris (22-10-2026, línea de RE general)

**VERIFICADO (26 tests, `tests/test_s151_panda.py`):** 10 cadenas `[PANDA]` contiguas `0x43c9a599`–`0x43c9a7c8` (`Panda_SendMessage: <canal> osal_valloc_msg error!`, 5 canales Pre1/Pre2/Post1/Post2/Async); **10/10 referenciadas**, **15 sitios** (regla estricta) en **4 funciones** (`F1_init` `0x437073cc` con 5, `F4_pre` `0x43707f8c` con 4, `F5_post` `0x437081b8` con 4, `F6_async` `0x437083e4` con 2) y logger privado `0x43707324` (10 llamadas: 7 `bl` + 3 `b.w`). Mecánica: **7 colas OSAL** (`0x00f900bc`, `0x00f90078`, `0x00f900d5`, `0x00f90191`, `0x00f90184`, `0x00f90520`, `0x00f90521`), **5 buffers de 0x40 B** con GID `0x00740017` (tabla global `0x4401eee4`), envío por thunk `0x43561228`, errores por GID de log `0x008f0139` (id `0x16`, mensaje 0x9a B); lo inicializa `void Camera::Lens::Initialize(UPM_BOOT_FACTOR*)` `0x43721624` (`bl` en `0x4372163e`).

**Base textual de "Panda"**: el nombre de función `Panda_SendMessage` (10/0/0) y los **parámetros de iris** `uc_PandaADErrorOpen` `0x43c99267` / `uc_PandaADErrorClose` `0x43c9927b` (**1/1/1** en los tres firmware; tabla `0x43febe04`/`0x43febe14`). **0 RTTI, 0 ficheros y 0 cadena independiente `PANDA`** → **`[PANDA]` no es un módulo de logging registrado** (al contrario que `[LENS_MOUNT]`); la sigla se deja **sin desarrollar**.

**Diferencial**: token **10/0/0** y 0/10 textos interiores, **pero el código existe en los tres firmware** (los 7 ids de cola aparecen 1 vez en cada blob; `F1_init` equivalente en `0x43729910` (A7S) y `0x437648d0` (A6300), mismo prólogo y misma secuencia de `bl` salvo las del reporter: F1 19 vs 14, F4 7 vs 6, F5 5 vs 4; la familia de loggers `push {r3}; movs r2,#0x9a` da 43/0/0) → **lo nuevo es el logging, no la función**.

**Negativo acotado**: 0/10 menciones de obturador, sensor, exposición o tiempos; los 47 `bl` del código PANDA van solo a thunks OSAL, helpers propios y `[CAM_UTIL]`; el único vínculo físico es el **drive del iris** → **sin efecto en S51**.

[Informe](../analysis/s151_panda/panda.md) · [doc](../docs/capture/s151-panda.md). Siguiente: qué significan Pre/Post/Async; los ids de cola `0x00f9xxxx`; el GID `0x00740017`; el id de log `0x16`; el papel de `0x00910042`; el receptor final del log.

## S156 — el módulo `[TP_R]` (18 trazas): el reporter de un framework de mensajes (22-10-2026, línea de RE general)

**VERIFICADO (19 tests, `tests/test_s156_tp_r.py`):** 18 cadenas `[TP_R]` en la A6000 fw3.21 entre `0x43c80f23` y `0x43c812f3`: **14 vivas** (20 sitios PIC en 8 funciones emisoras) + **4 muertas**; además **3** con la etiqueta antigua `[TP R]`, todas muertas → 21 cadenas con el token. Funciones: `0x4366c388`/`0x4366c568`/`0x4366c624` (errores OSAL), `boot_exit_tp` `0x4366c6e8`, bucle de recepción `0x4366c840`, `0x4366c978`, despachador `0x4366ca92`, `boot_init_tp` `0x4366caf4` (llamados desde `0x43a464dc` id 135 y `0x43a4670c` id 134). Módulo: código `0x4366c2a4`–`0x4366cd38` (18 funciones); **tabla de comandos DDL** `0x43fe3f28` (`start`, `set_mode`, `print_xy`, `dds_on`, `dds_off`) registrada con el nombre **`tp`** en `0x4366cae8`; colas OSAL: log `0x008f0139`, eventos `0x005c011c`, control `0x01010227`.

**Confirma S151**: el reporter `0x4366c300` (`push {r3}` … `movs r2,#0x9a` → `osal_try_valloc_msg` → `vsnprintf` → `osal_snd_msg`) es **miembro de la familia**; recuentos estricto 43/0/0 (reproduce S151) y laxo 561/0/2 → el conteo con regla estricta es el canónico.

**Corrección de S130 (falso positivo)**: los 2 "textos comunes" entre `[TP_R]` y `[DMMYSIOCOM]` son las **plantillas OSAL** `ERR. osal_snd_msg…`/`ERR. osal_free_msg…`; en la A7S están en `0x43c73764`/`0x43c73792` (ref. `0x4362cc7a`) y en el A6300 en `0x43d7296b`/`0x43d72999`, mientras que en la A6000 ese módulo sigue intacto en `0x43c72e7d`/`0x43c72eab` (ref. `0x43628a5e`/`0x43628a80`) → **código distinto**: falso positivo textual (el texto es genérico de OSAL).

**Diferencial**: A7S 3 cadenas `[TP R]` y A6300 4, **0 vivas**; la tabla de comandos y el registro `tp` existen en los tres (`0x43fe3f28` / `0x43fe54d0` / `0x441a59c0`) → el módulo ya existía **silencioso** y la fw3.21 **añade 15 trazas**.

**Negativo acotado**: la única coincidencia del barrido es `read` en `[TP_R]: ERR. read size error` (tamaño leído por una llamada OSAL) → **sin efecto en S51**.

[Informe](../analysis/s156_tp_r/tp_r.md) · [doc](../docs/capture/s156-tp-r.md). Siguiente: siglas "TP" y "DDS" (sin desarrollar); `<Water>` y `ex_status`/`ex_info`; el consumidor de los eventos de la cola `0x005c011c`; los nombres exactos de `0x43561244`/`0x4356127c`/`0x435613b0`.

## S164 — el módulo `[CAMERA_IS]` (17 trazas): la capa de estabilización de imagen de la cámara (22-10-2026, línea de RE general)

**VERIFICADO (18 tests, `tests/test_s164_camera_is.py`):** 17 cadenas `[CAMERA_IS]` en la A6000 fw3.21 entre `0x43c98da6` y `0x43c9a426` (sub-etiquetas: `MOUNT` 5, `DIST` 5, `EIS` 4, `AS` 3); **0** en la A7S fw3.20 y el A6300 fw2.01. **21 sitios** de emisión (regla estricta) en **13 funciones** emisoras, con los **17 pares PIC verificados a mano (17/17)** → **validación cruzada del mapa de S70**: S164 añade las **5 trazas** que S70 no listaba (`0x43c98dde`, `0x43c98e80`, `0x43c98ebc`, `0x43c9a352`, `0x43c9a3e3`) y la **13.ª función** `0x4371e4cc` (máquina de estados del estabilizador "AS").

**Qué es (VERIFICADO)**: **la capa que aplica la estabilización**. Coordina el recurso RC de estabilización (`rcct_SetStblzPower` `0x439417c8`, `rcct_SetStblzGridH` `0x43941814`, rejilla redondeada a múltiplo de 8 en `0x43702db0`/`0x43702db6`), **lee el giroscopio por ADC** (`GyroAD[p],GyroAD[y], %d, %d` `0x43c9a324`, emitido en `0x437046a4` con los valores de `0x4370665c`), aplica la **corrección de distorsión** (`pos -= (coef·(pos−centro))>>10` en `0x436ea594`/`0x436ea596`, centro/coef en los globales `0x43f61884`/`0x43f61886`), y se sincroniza con la **montura** (se registra como cliente del servicio literal `LENS_MOUNT` `0x43c9a39c`; callbacks `IS_LensMountExpStartCB` `0x436ea2d0` e `IS_LensMountPanoramaGyroCB` `0x43705d64`, códigos `0xF0`/`0xF1`, y envío al objetivo por el canal de no-comandos `SendingLensNonCommand` `0x436e1254`) y con la **secuencia de exposición** (`[CAMERA_MAIN_SYNC]`: `0x43702dac` llamada desde `0x4354a97c` en `0x4354a678`; `0x43704d90` desde `0x4354e51c` en `0x4354d740`). Escribe `/mnt/FILE_IS_%04x.dat` `0x43c9a535` (contador `u16` global `0x43f65d3c`).

**Diferencial**: la etiqueta y la **capa de cámara** del IS (giroscopio propio, matemática de distorsión, callbacks con la montura, cola del estabilizador "AS") **solo existen en la A6000 fw3.21**; pero la **infraestructura del driver RC** es **común a los tres** (`rcct_SetStblzPower` **2/1/1**, `rcct_SetStblzGridH` **2/1/1**, `WrapRcctSetStblz*.cpp` 4/4/4, `/mnt/FILE_IS_%04x.dat` **1/1/1**, `EIS_RC1V_SetPower` 2/2/2) → la diferencia está en la *capa de cámara*, no en el driver.

**Negativo verificado**: 0/17 trazas mencionan obturador, lectura del sensor, *rolling shutter*, tiempo de exposición o solapamiento EIS/obturador → **sin efecto en S51**.

**Colateral con valor para la línea del obturador**: la A6000 fw3.21 tiene **0 apariciones** de `rolling` y de `readout` (igual la A7S fw3.20), mientras que el **A6300 fw2.01 tiene 1**: `position num in rolling is strange %d` (`0x43d9fe03`), junto a `position num in vd is strange %d` (`0x43d9fde2`) → el concepto de *rolling shutter* **existe en el A6300 y no en la A6000/A7S** (y la cadena `vd`/VD del visor aparece en el A6300 pero no en la A6000). Refuerza que el A6300 es el cuerpo con más funciones de lectura, pero **no cambia S51** (A/B/C = NO): la ausencia estática de una cadena no demuestra incapacidad del hardware.

[Informe](../analysis/s164_camera_is/camera_is.md) · [doc](../docs/capture/s164-camera-is.md). Siguiente: fichero fuente propio del módulo (no embebido); significado de `upm_get_hcrn_ura` y de las sub-capas `AS`/`DIST`; el significado físico de `SetStblzGridH` y el camino RC→imager; el formato binario de `/mnt/FILE_IS_%04x.dat`; las 4 funciones sin llamadores `bl` directos (¿tabla de callbacks?).

## S165 — el módulo `[JOG]` (14 trazas): el subsistema de la rueda de control (22-10-2026, línea de RE general)

**VERIFICADO (tests del hito + comprobaciones a mano):** 14 cadenas `[JOG]` en la A6000 fw3.21 entre `0x43c40eb4` y `0x43c411bd` (contiguas en `.rodata`); **0** en la A7S fw3.20 y el A6300 fw2.01; `deg/sec` **1/0/0**. **14/14 referenciadas**, **24 sitios** (regla estricta) en **12 funciones**, **0 cadenas muertas**; los **34 pares PIC** de la zona `0x435ae400`–`0x435afb00` (24 de `[JOG]` + 10 de `__PRETTY_FUNCTION__`) se verificaron **a mano 34/34**, comprobando que el registro no se reescribe entre el `ldr` y el `add` (kill analysis con `movs/adds Rd,#imm` → `Rd = (h>>8)&7`).

**Qué es**: **la fuente de eventos de la rueda de control**. Sondea `JogFg`/`JogTpu`/`JogVGrip` con temporizador OSAL, traduce el movimiento a un `key_code` de cámara + delta en grados (`JogKey::SendKeyEvent` `0x435af9d0`) y emite un evento de 12 B (`JogMain::SendEvent` `0x435aeb18`) a la **cola de eventos de cámara (id `0x106`)**. Tabla de key codes `0x43fdab20` (`0x11`–`0x17`); montaje en `JogMain::Init` `0x435ae6b6`.

**Diferencial**: las clases RTTI `JogDev` (2/1/1), `JogFg` (3/1/1), `JogTpu` (3/1/1) y `JogVGrip` (**3/1/0**) están **en los tres firmware** → el subsistema ya existía; lo propio de la fw3.21 es la **instrumentación** `[JOG]` y la clase `JogKey` (**5/0/0**). **Matiz propio del A6300**: sustituye `JogVGrip` por **`JogCaif`** (**0/0/1**) → en el A6300 la rueda se toma por la interfaz CAIF en vez de por la empuñadura vertical.

**Colateral**: el módulo hermano `[ILLUMI]` (sensor de luz ambiente; clases `IllumiDev`/`IllumiAd`/`IllumiCam`/`IllumiRPR0400` en las tres fw) emite en la A6000 una traza **gemela** `[ILLUMI]<Send Event> key_code = 0x%x,Level:%d` `0x43c40798` → mismo patrón de emisión por `key_code`; `ILLUMI]` es **34/0/0**.

**Negativo acotado**: 0 coincidencias de `shutter`/`capture`/`exposure`/`sensor`/`read`/`frame` en las 14 trazas ni en las 10 `__PRETTY_FUNCTION__`; los únicos temporizadores son de **sondeo de la rueda** → **sin efecto en S51**.

[Informe](../analysis/s165_jog/jog.md) · [doc](../docs/capture/s165-jog.md). Siguiente: ficheros fuente (no embebidos); siglas `Fg`/`Tpu` (sin base textual); significado de los key codes `0x11`–`0x17`; la cola OSAL concreta (recurso `0x011b02aa`); las ranuras 0/3/4/5 de las vtables `Jog*`.

## S166 — el módulo `[ADC_DEBUG]` (14 trazas): el volcado del ADC del driver LIRO (22-10-2026, línea de RE general)

**VERIFICADO (tests del hito + comprobaciones a mano):** 14 cadenas `[ADC_DEBUG]` en la A6000 fw3.21 entre `0x43ce50dd` y `0x43ce5273` (bloque contiguo, paso 0x20 B); **0** en la A7S fw3.20 y el A6300 fw2.01. **14/14 referenciadas**, **15 sitios** (regla estricta; `few arg` se emite en 2 sitios) en **2 funciones** — `0x4398eb20` (handler ADJ `get_da`) y `0x4398ec7c` (handler ADJ `get_d`) — con los **15 pares PIC verificados a mano 15/15**.

**Qué es**: **no es un módulo autónomo**, es la capa de volcado de valores crudos que la fw3.21 añadió a los *handlers* de los comandos de fábrica (`ADJ`) del **driver LIRO del ADC**. El ADC tiene **2 unidades × 12 canales** (array en RAM `0x43f84b80`, índice `= unidad*12 + canal`; registro de HW `0xf2406014` + `0x1000`/unidad + `4`/canal, leído por `0x4398ee14`; rango validado con `cmp r2,#0xb` `0x4398e6b8` y `cmp r1,#1` `0x4398e6b2`); base HW `0xf2406000` (u0) / `0xf2407000` (u1); handle de servicio `0x720018` (**LIRO_ADC**) y **11 clientes**; ids de mensaje `0xfff0` (1 canal) / `0xfff1` (12 canales) / `0xfff2` (escribir 12).

**Diferencial**: el driver ya existía en los tres firmware (`TSK_ADC` **1/1/1**, `get_d` **1/1/1**, `get_da` **1/1/1**, `set_da` **2/2/2**, `CNF_ADC_CH_EVF_TEMP` **1/1/1**, las tres plantillas `ADC_GET_DATA…`/`ADC_SET_DATA_ALL…` **1/1/1**, base HW `0xf2406000` **5/5/5**); los handlers equivalentes (`0x4397c860`/`0x4397c89c` en la A7S, `0x43a23480`/`0x43a234bc` en el A6300) son **estructuralmente idénticos pero no imprimen nada**. Lo propio de la fw3.21: la capa `[ADC_DEBUG]`, las **etiquetas de comando** `ADJ_CMD_LIRO_DRIVERS_ADC_*` (**5/0/0**) y trazas internas del driver (`sem=%x`, `reg_sync err=%d`, `Backup Read Error!`, **1/0/0** cada una) → **instrumentación, no función**.

**Corrección de una lectura posible de S164**: el «acceso ADC» del giroscopio de `[CAMERA_IS]` **NO** es el servicio LIRO ADC — la región del estabilizador hace **0** y **1** llamadas al helper genérico `0x43561228` y **ninguna** con el handle `0x720018`; el lector de `GyroAD` lee una **tabla de constantes** en `0x43bdc0a6`. Dos mecanismos distintos que comparten la palabra "ADC".

**Aportación a la línea del obturador (verificada)**: el ADC participa en la **sincronización temporal de la secuencia HS** (`HS_Main` `0x4378fef4` → `SendToADCTask` `0x4378d3b4`; espera con `ADC flg timeout %dV #%d, %04x` `0x43ca30fd`) y en la **medida de jitter** (`int_ADC_Handler #%d jitter NG %d->%d, jitter:%dusec` `0x43ca241e`, umbral `cmp.w r8,#0x320`), pero **ningún canal está ligado a la decisión mecánico/electrónico**: el único canal con nombre simbólico es `CNF_ADC_CH_EVF_TEMP` (temperatura del EVF) y el **A6300 fw2.01, que sí implementa `ElecShutter/` (S135), tiene el MISMO ADC LIRO y no añade ningún canal ni traza de obturador electrónico** → **S51 sigue A=NO, B=NO, C=NO**.

[Informe](../analysis/s166_adc_debug/adc_debug.md) · [doc](../docs/capture/s166-adc-debug.md). Siguiente: asignación canal→sensor (los ids de configuración se leen en runtime, `0xf9034d`/`0xf90413`/`0xf90414`); fichero fuente y clase RTTI del driver LIRO ADC (no embebidos); el canal `CNF_ADC_CH_EVF_TEMP` y las siglas `CNF`/`EVF_TEMP`.

## S168 — control positivo del *rolling shutter* del A6300: la cadena es **muerta** (22-10-2026, línea de RE general)

**VERIFICADO (16 tests, `tests/test_s168_a6300_rolling.py`):** la cadena `position num in rolling is strange %d` del **A6300 fw2.01** (`0x43d9fe03`) **no la referencia NINGÚN código**: **0 referencias PIC** (regla estricta canónica), **0 punteros absolutos de 4 B**, **0 pares `movw`/`movt`**, y **0** por el **método inverso independiente** (`add_addr = destino − W − 4`). La cadena tampoco aparece en ningún otro fichero del paquete del A6300 (solo en `av-cam.bin`).

**Control de contraste**: en la banda `0x43d9fd80`–`0x43d9fe80` hay **5** cadenas y **4 están referenciadas** (`[BL]Wait_BL_ASYNC_RCV (%+hd)` `0x43d9fdc5`; `position num in vd is strange %d` `0x43d9fde2`; `this vsync command has another command` `0x43d9fe29`; `ASYNC BL COMMAND BANISH ! Mount_FcZm_BLComm.cpp %d` `0x43d9fe50`) → el discriminante funciona y **exactamente una —la del *rolling*— está muerta**. El código vivo es `0x4372914c`: **cálculo de ancho en bits del número de posición del VD** con control de rango (`r1 = 1 << n`; `cmp r3,#0xfe`; si no cabe, traza y fuerza 8 bits), referencia en `ldr 0x43729164` (pool `0x43729174` = `0x00676c78`) + `add 0x43729166`.

**Método (reutilizable)**: tres herramientas parametrizadas en `analysis/s168_a6300_rolling/` — `scan_refs.py` (réplica de la regla estricta con *blob* y *base* como parámetros), `find_ref.py` (**método inverso independiente**) y `alive_map.py` (mapa vivo/muerto de una banda de `.rodata`). Controles validados: A6000 `Get ADC CNF_ADC_CH_EVF_TEMP Val:0x%x(%d)` `0x43c7751a` → 1 referencia (`ldr 0x43636ce2` + `add 0x43636ce6`); A6300 `0x43d9fde2` → 1 (`ldr 0x43729164` + `add 0x43729166`).

**Corrección que impone sobre S164**: el colateral de la revisión de S164 («el concepto de *rolling shutter* **existe en el A6300**») **queda matizado**: la cadena existe pero **está muerta** → no prueba el concepto en ese firmware. Lo que **sigue en pie** es el dato bruto (la cadena está en el A6300 y no en la A6000/A7S) y que las 36/37/40 apariciones de `roll` en las tres son casi todas `Controller`/`Scroll` (RTTI), no el concepto. **No cambia S51** (A=NO, B=NO, C=NO) ni S135 (control positivo del `ElecShutter/` en el HAL del A6300, **independiente** de esta cadena); de hecho **debilita** un argumento potencial.

**Excepciones de `roll` que NO son *rolling shutter***: `SetDistRoll` `0x43c7b1f3` (**1/1/1**, comando de la API RC), `SetRoll` `0x43c7fc61` (**1/1/1**, comando RC) y `RollAD,%d,%d,%d,%d,%d,%d,%d,%d` `0x43c9ae2e` (**1/0/0**, propio de la fw3.21 de la A6000; imprime 9 valores AD de un global en `0x437212b8`). Análisis de esa familia: hito **S169**.

[Informe](../analysis/s168_a6300_rolling/rolling.md) · [doc](../docs/capture/s168-a6300-rolling.md). Siguiente: `GetImagerStabilizationTime` del A6300 (`0x43d9ce7f`, viva pero no analizada); qué comandos RC son `SetRoll`/`SetDistRoll`; el global de los 9 valores AD de `RollAD`.

## S169 — control positivo del obturador electrónico: la API de **drive** del A6300 (22-10-2026, línea de RE general)

**VERIFICADO (32 tests, `tests/test_s169_drive_api.py`):** el **A6300 fw2.01** tiene una **capa de validación de parámetros de cámara** (`LiroSeq`) con **201 propiedades** `CheckSet*` y **370 comprobaciones** `LiroSeq ParamCheckErr@%s[campo] cur:%d req:%d`. Entre ellas, los **parámetros de obturador** (nombre de campo + offset en el bloque de parámetros + sitio del `add`):

| propiedad | campo | offset | sitio |
|---|---|---|---|
| `CheckSetShutDrive` | **`sc_ShutDrive`** | `+0x1dd` | `0x438c51c0` |
| `CheckSetShutDriveMode` | **`uc_ShutDriveMode`** | `+0x1dc` | `0x438c6842` |
| `CheckSetFrontEshutter` | **`front_eshutter`** | `+0x23c` | `0x438c6e1e` |
| `CheckSetSilentShutterMode` | **`SilentShutterMode`** | `+0x264` | `0x438c81da` |
| `CheckSetShutterType` | **`shutterType`** | `+0x268` | `0x438c8b52` |
| `CheckSetShutLowLimit` | `ul_ShutLowLimit` | `+0x248` | `0x438c7ba4` |
| `CheckSetIrisDrive` / `CheckSetIrisDriveMode` | `sc_IrisDrive` / `uc_IrisDriveMode` | `+0x1d1` / `+0x1d0` | `0x438c55a2` / `0x438c680e` |
| `CheckSetManualExposureDrive` | `sc_ExposureDrive` | `+0x1ac` | `0x438c5d14` |

**La A6000 fw3.21 y la A7S fw3.20 tienen 0 de todo eso**: `CheckSet*` **0/0/201**, `ParamCheckErr` **0/0/370**, `sc_ShutDrive` **0/0/1**, `front_eshutter` **0/0/1**, `SilentShutterMode` **0/0/2**, `shutterType` **0/0/1** → **no falta la traza, falta el parámetro**: la fw3.21 de la A6000 **no expone ningún parámetro de obturador electrónico**.

**Patrón verificado a mano** (3 casos): `ldrsb.w r2,[r0,#0x1dd]` (valor actual) vs `ldrsb.w r3,[r4,#8]` (solicitado) → si difieren, `ldr`+`add` al mensaje y a la etiqueta y `b.w 0x43986518` (traza). Los **201 nombres están vivos** (1 referencia PIC cada uno) y se despachan desde la región contigua `0x438c4ade`–`0x438c8c76` (390 sitios), **en el orden del bloque de parámetros**.

**Matiz**: la A6000 **sí** tiene el módulo LiroSeq (2 trazas: `[CAMERA_MAIN]: LiroSequencerMovieFileFormat : %d` `0x43ca3b3a`, `[CAMERA_MAIN]: LiroSequencer cannot read IRIS_DIAL_POS ::: %d` `0x43ccadbf`) y **sí** tiene `drive_mode` (el del imager de S134, 10 apariciones) → no le falta el subsistema, le falta **esta capa de validación de parámetros**.

**Salvedad** (S130 §4): la comparación mezcla versión de firmware y modelo (el A6300 es de otra generación de plataforma, LIRO/CXD).

**Efecto en S51: NINGUNO — S51 sigue A=NO, B=NO, C=NO.** El hallazgo dice que la fw3.21 de la A6000 no expone parámetros de obturador electrónico, no que su hardware sea incapaz; la ausencia estática no demuestra incapacidad del hardware y sigue faltando la prueba física.

[Informe](../analysis/s169_drive_api/drive_api.md) · [doc](../docs/capture/s169-drive-api-a6300.md). Herramientas reutilizables: `scan_all_refs.py` (mapa global PIC de un blob parametrizado: A6300 **20 001** destinos, A7S **16 638**, A6000 17 525 ya existente) y `pair_checkset.py` (**387** pares propiedad↔campo con offset y sitio). Siguiente: qué valores toman `shutterType`/`SilentShutterMode`/`front_eshutter` en runtime y quién los escribe; la ruta de `sc_ShutDrive` hasta el driver del obturador.

## S167 — el módulo `[SAD]` (44 trazas): el diagnóstico de la biblioteca «SA» (22-10-2026, línea de RE general)

**VERIFICADO (124 tests: 106 del hito + 18 de verificación independiente):** 45 apariciones del token `[SAD]` en la A6000 fw3.21 entre `0x43ce546b` y `0x43ce59d1` (44 con mensaje + el token suelto `[SAD] ` `0x43ce56b3`); **0** en la A7S fw3.20 y el A6300 fw2.01. **49 sitios** (regla estricta) en **5 funciones** emisoras: `0x43998578` (gestión de handle de unidad, 3), `0x4399d464` (validador de cabecera **Cdc**SaPrg), `0x4399d528` (**Nml**SaPrg), `0x4399d618` (**Rsd**SaPrg) y el **despachador de volcado `0x439a119c`** (43); **0 cadenas sin referencia**. Los **49 pares PIC verificados a mano (49/49)** y la reimplementación del escáner del subagente reproduce el mapa canónico del repo (`analysis/s106_imaging_cap/pic_refs_strict_global.json`, 17 525 destinos) con **0 discrepancias**.

**Qué es**: el **módulo de diagnóstico del subsistema «SA»** (acelerador escalar): vuelca el estado de configuración (`CFG_STATE`), el estado y los datos de la **FIFO de JPEG** (`JpgNrm` `0x43ce5724`, `JpgSrt` `0x43ce5738`, `JpgNrmIndex` `0x43ce5762`, `JpgSrtIndex` `0x43ce577b`), los **tiempos de cálculo** (`CALCTIME`), las **cabeceras de programa SA** (`SaProgHdr`, validadores Cdc/Nml/Rsd con error `0x0d` y el byte «una sola vez» `0x43e211c8`) y la gestión de **handles de unidad/DMM** (`0x43f85932` 32 u16, `0x43f84bfe` 255 u16 → **`[CAM_DMM]`**, S113). Canal de log **propio** `0x439a10f0` (id OSAL `0x93`), frente al logger global `0x435ab880` de `[SFRA]`/`[SFRS]`.

**La sigla NO tiene base textual → sin desarrollar**: `SAD` = 45 apariciones = solo las 45 trazas; `SAD_`/`_SAD`/`Sad[A-Za-z]` = 0; los 11 `SaD` son del subsistema de **audio** (`SaDriverBase` `0x43cde8f1`, `SaDriverZoomNr` `0x43cdda06`); 0 nombres de fichero con `sad`/`SaD`; **0** apariciones de `[SAD]` en los **148 `.so`** de la fw3.21. **No** se propone «SA Debug» ni «Scene Auto Detection»: no tienen respaldo en los bytes.

**Diferencial**: la **biblioteca SA es común a los tres firmware** (`ScalarInfraSequenceSa` **10/10/10**, `ScalarInfraSequenceSa.cpp` **1/1/1**, `ScalarInfraSequenceSaStage.cpp` **1/1/1**, `SaStageAutoexec_sadone` **1/1/1**, `SA_JPEG_DEC` **1/1/1**; versiones SA0/SA1/SA5/ZMA0/ZMA1 en `0x43ce5402`–`0x43ce5445`) → lo propio de la fw3.21 es la **instrumentación** (`[SAD]` 45/0/0, `SaProgHdr` **2/0/0**).

**Negativo acotado**: 0 de `shutter`/`silent`/`obtur`/`expos`/`imager`/`sensor`/`readout`/`drive`/`brack`/`sweep`/`interval`/`still`/`movie`/`focus`/`aperture`/`iso` en las 45 cadenas; las 4 apariciones de `Jpg` son **índices de la FIFO** → **sin efecto en S51** (A/B/C = NO).

**Corrección aceptada del subagente (verificada por el agente principal)**: el puntero embebido `"PEG_DEC"` en `0x43ce5644` **no existe**; el `ldr r3,[pc,#0x3e4]` de `0x439a11ac` resuelve al pool `0x439a1594` (`W=0x344494`) y, con el `add r3,pc` de `0x439a11b4`, el destino es `0x43ce564c` = **`[SAD] DbgPrt CmdRcv`**. `"PEG_DEC"` es una **cadena muerta** (0 referencias PIC, 0 punteros de 4 B). También se corrigió la afirmación «bloque contiguo»: son **3 bloques** (3 + 3 + 39).

[Informe](../analysis/s167_sad/sad.md) · [doc](../docs/capture/s167-sad.md). Siguiente: `0x43998578` no tiene llamador `bl` ni puntero absoluto de 4 B → se invoca por puntero; sentido de `DdsDataAdd`/`SelCode`/`ZmCfg` vs `SaCfg`; los ids `0x9548`/`0x93`/`0xa1` sin decodificar; semántica de los 6 subcomandos y quién envía `0x9548`.

## S171 — la API del imager y el canal «SteadyShot» del objetivo (22-10-2026, línea de RE general)

**VERIFICADO (20 tests, `tests/test_s171_imager_api.py`):** tres diferencias de **superficie de API** entre el A6300 fw2.01 y la A6000 fw3.21 / A7S fw3.20:

| elemento | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| nombres de API del imager (`Get/Set*Imager*`) | **4** | **4** | **7** |
| → `GetImagerStabilizationTime` | 0 | 0 | **1** |
| → `SetImagerFrameSize` (traza `SetImagerFrameSize[%d]` `0x43daccdd`) | 0 | 0 | **1** |
| → `SetImagerMode` (firma C++ `0x43daf786`) | 0 | 0 | **1** |
| clase `Camera::Sync::SyncUtilityUpm` | **0** | **0** | **3** |
| tipo `Camera::Imager::IMAGER_DRIVEMODE` | **0** | **0** | **2** |
| `SteadyShot` (cualquier grafía) | **0** | **0** | **11** |
| `SteadyShotInfo` (canal del objetivo) | **0** | **0** | **7** |
| `Mount_DividedInfo` (módulo que lo contiene) | 5 | 3 | 5 |

Los cuatro nombres comunes: `GetImagerDriveMode`, `GetImagerTemperature`, `GetImagerTemperatureAD` y `GetPrelightImagerDriveMode` (el `drive_mode` del imager de **S134**).

**`GetImagerStabilizationTime` (solo A6300)**: cadena `GetImagerStabilizationTime Request Error` `0x43d9ce7f`, **viva** con **1** sitio PIC (`ldr 0x43718d02`, pool `0x43718d14` = `0x00684177`, `add r0,pc` `0x43718d04` → logger `0x43986518`). El manejador (`0x43718cd8`) **suma** los `count` bytes de una tabla en `base + 3·índice + 0x25a` (count en `+0x258`) y devuelve `(suma + 2) & 0xFF`; con la tabla vacía avisa («Request Error») y devuelve 0. **NO VERIFICADO**: qué magnitud devuelve (el nombre viene de la tabla de API, no del código), qué es la tabla de `+0x25a` y quién la escribe.

**Canal «SteadyShot» del objetivo (solo A6300)**: las 7 apariciones de `SteadyShotInfo` están en el **driver de la montura (BL)**: el objetivo manda su información de estabilización y el cuerpo la recibe en dos callbacks (`CallBack_SteadyShotInfo_Com_1st` `0x43da460a` y `_Com_2nd` `0x43da46aa`, entre otras, con sitios `0x4374eb60`–`0x4374ed6c`), con `Mount_DividedInfo_SteadyShotInfo.cpp` como fichero. Las otras 4 apariciones de `SteadyShot` son propiedades de la capa `LiroSeq` de **S169**: `CheckSetFrameLockOnSteadyShot` `0x43dc5494`, `CheckSetSteadyShotAdvancedStill` `0x43dca7b7`, `CheckSetS1SteadyShotMode` `0x43dca8b5`, `CheckSetSteadyShotAdvancedMovie` `0x43dcabd7`.

**Matiz**: el módulo `Mount_DividedInfo` **existe en los tres** (5/3/5) → lo exclusivo del A6300 es la **variante `SteadyShotInfo`**, no el driver de la montura. Y la A6000 **no** carece de estabilización (tiene el subsistema IS/EIS de **S164**): lo que le falta es **este canal del objetivo** y la entrada de API `GetImagerStabilizationTime`.

**Salvedad** (S130 §4): la comparación mezcla versión de firmware y modelo.

**Efecto en S51: NINGUNO — S51 sigue A=NO, B=NO, C=NO.** Son diferencias de **firmware**; la ausencia estática de una API no demuestra incapacidad del hardware.

[Informe](../analysis/s171_imager_api/imager_api.md) · [doc](../docs/capture/s171-imager-api.md). Siguiente: qué magnitud devuelve `GetImagerStabilizationTime`; el formato del paquete `SteadyShotInfo`; si la clase `SyncUtilityUpm` tiene más métodos con nombre.

## S172 — el módulo `ElecShutter` del A6300: qué hace realmente (22-10-2026, línea de RE general)

**VERIFICADO (15 tests, `tests/test_s172_elec_shutter_a6300.py`):** **S135** localizó el subsistema `ElecShutter/` del A6300 por sus **nombres de fichero** (`ElecShutter/EC_ElecShutter_Main.cpp` `0x43dcfa41`, `ElecShutter/EC_NonlinearElecShutter_MechShutterTable.cpp` `0x43dcfa65`) y sus ajustes, **sin decodificar el comportamiento**. Este hito **localiza el código** (los nombres son cadenas `__FILE__` de un `EC_ASSERT %s:%d` `0x43db1a4d`) y **caracteriza las dos funciones**:

1. **`EC_ElecShutter_Main.cpp`** (función `0x4391d67c`; sitio `0x4391d6a2`): lee un **u16** de una tabla global (`ldr r3,[pc,#0x38]` → puntero; `ldr r3,[r3,r2]`; `ldrh r3,[r3]`) y devuelve un **código de modo de obturador**: `0x80` → **3**, `0x100` → **4**; otro valor → `EC_ASSERT` con línea **0x421** (1057) y devuelve 3.
2. **`EC_NonlinearElecShutter_MechShutterTable.cpp`** (sitios `0x4391dd50` y `0x4391ddb0`): la **equivalencia no lineal entre velocidad electrónica y mecánica**:
   * **interpolación por tramos**: lee una fila con `ldr.w r3,[r2,r6,lsl #2]` (**32 bits por fila**), compara con el valor pedido e interpola con escalas **10000** (`0x2710`) y **1000** (`0x3e8`), helper aritmético `0x435586f8` y setters `0x4391da74`/`0x4391da9c`; `EC_ASSERT` línea **0x23c** (572);
   * **búsqueda en punto fijo 16.16**: escala `0x8000` y **15 bits fraccionarios** (`mov.w r3,#0x8000`; `movs r2,#0xf`), valor = `(r3 + r0*2) << r2`; `EC_ASSERT` línea **0x24f** (591).

**Corrección a S135**: los **128 bytes** que S135 identificó como «tabla de índices de velocidad de obturación» en `0x43dcfa9e` **no tienen ninguna referencia de código** (ni PIC —no están en `pic_refs_strict_a6300.json`— ni puntero absoluto de 4 B) y forman una tabla byte→byte **no decreciente** (`54 54`, `60 60`, `66 66`, `6a 6a`, `6e 6e`, `71 71`, `74 74`, `77 77`, `7b 7b`, `7d 7d`, `7f 7f`), más compatible con una tabla de **caracteres imprimibles**. La tabla real se indexa **por fila con 32 bits por entrada**. **Lo que S135 acertó** (existencia del módulo `ElecShutter/`, sus ficheros y sus ajustes) **se mantiene**.

**Colateral**: `EC_ASSERT` **0/1/1** y `EC_ERR_PRINT` **0/0/5** (A6000/A7S/A6300) → el motor EC de la A6000 **no instrumenta sus aserciones**, otra diferencia de *logging* coherente con S128/S130.

**Salvedad** (S130 §4): el A6300 es de otra generación de plataforma (LIRO/CXD).

**Efecto en S51: NINGUNO — S51 sigue A=NO, B=NO, C=NO.** La ausencia del módulo en la fw3.21 de la A6000 no demuestra incapacidad del hardware; sigue faltando la prueba física.

[Informe](../analysis/s172_elec_shutter_a6300/elec_shutter_a6300.md) · [doc](../docs/capture/s172-elec-shutter-a6300.md). Siguiente: qué significan los códigos 3 y 4; la base de datos de la tabla (índice de fila) y quién la escribe; la ruta hasta el driver del obturador.

## S173 — `[CAM_UTIL]` (10) y `[CAMERA_ADJ]` (3): las utilidades compartidas (22-10-2026, línea de RE general)

**VERIFICADO (21 tests, `tests/test_s173_cam_util_labels.py`):** las etiquetas **`[CAM_UTIL]`** (10 cadenas) y **`[CAMERA_ADJ]`** (3) **no son un módulo propio**: son el rótulo de **utilidades compartidas** por la familia `CAM_UTIL` (`[CAM_UTIL_ADJ]` de S143 y `[CAM_UTIL_SENS]` de S144) y por el gestor de memoria **DMM** de `[CAMERA_MAIN]`. `[CAM_UTIL]` **10/0/0** y `[CAMERA_ADJ]` **3/0/0** (A6000/A7S/A6300).

Las **13 cadenas están vivas** (0 muertas) con **16 sitios** (regla estricta) en **13 funciones**: 5 en la zona **DMM** (`0x437e3c92`–`0x437e446e`: `MemPool Free Err`, `Dmm Open/Close Err hdl`) y 8 en la zona **`CAM_UTIL`** (`0x43900234`–`0x43904092`): `AV DDS Alloc/Snd Msg Err`, `Utility Adjust Ctrl` / `Utility MS Mount Start` / `Utility MS UnMount Start` (fallos de reserva OSAL), `EvtDrvnTsk) Send Err` / `Print Max` / `Task tid` (driver de eventos) y el **contador de fallos de `osal_try_valloc_msg`** con reintento (si el bit 0 del byte de estado `[r6,#0xfc]` está activo, traza el error y lo limpia con `bic r3,r3,#1`). Son **funciones que S143 y S144 no cubrían** porque emiten con otra etiqueta.

**Coherencia con S144**: la inicialización `0x4390178e` limpia una tabla de **17 entradas** (`cmp r2,#0x11`) y **22 registros** de 0x18 B (`0x198/0x18`) y escribe el **id de módulo `0xb5`** (`movs r2,#0xb5`) y un contador **5** (`subs r2,#0xb0`) → el **mismo `0xb5`** que S144 identificó como compartido por `[CAM_UTIL_ADJ]` y `[CAM_UTIL_SENS]`.

**Diferencial**: las etiquetas son **propias de la fw3.21** de la A6000 (0/0 en A7S y A6300), pero los **nombres** que avisan (`DmmMemPool`, `AV DDS`, `Utility MS`, `EvtDrvnTsk`) describen **utilidades preexistentes** del framework → otra vez el patrón «se reescribe el logging» (S128/S130).

**Negativo acotado**: 0 menciones de obturador, disparo, sensor, exposición o tiempos → **sin efecto en S51** (A/B/C = NO).

[Informe](../analysis/s173_cam_util_labels/cam_util_labels.md) · [doc](../docs/capture/s173-cam-util-labels.md). Siguiente: qué es «AV DDS» y «Utility MS» (siglas sin desarrollar); la tabla de 17 entradas y los 22 registros de `0x4390178e`; el byte de estado `+0xfc` y su bit 0; por qué la A6000 usa dos etiquetas para el mismo subsistema.

## S174 — el API de mensajes «…ForLiro» del `libObj.so`: 216/221/240 nombres, 0/0/6 soportados (22-10-2026, línea de RE general)

**VERIFICADO (17 tests, `tests/test_s174_forliro_api.py`):** el conversor de mensajes `CamMsgConv` de la capa *camera-user* (`libObj.so`) conoce **216 / 221 / 240** nombres de mensaje `…ForLiro` (A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01) y **soporta 0 / 0 / 6**:

| firmware | nombres `…ForLiro` | en mensajes de **SOPORTE** | en mensajes de **RECHAZO** |
|---|---|---|---|
| A6000 fw3.21 | **216** | **0** | 216 |
| A7S fw3.20 | **221** | **0** | 221 |
| A6300 fw2.01 | **240** | **6** | 234 |

Los 6 del A6300: `SetApertureSTFForLiro`, `SetAutoDualRecModeForLiro`, `SetExpandFocusAfModeForLiro`, `SetMountAdapterFocusTypeForLiro`, `SetPowerStatusForLiro` y `SetVolpfModeForLiro` — **ninguno del obturador**. El A6300 añade **25** nombres `…ForLiro` (incluido **`SetShutterTypeForLiro`**, 0/0/1) y la A6000 añade **1** (`SetStepzoomModeForLiro`); la A7S añade 5 respecto de la A6000.

**Advertencia metodológica (lo más importante del hito)**: en la A6000 y la A7S, **los 216 y 221 nombres `…ForLiro` aparecen TODOS dentro de mensajes de RECHAZO** (`… <Nombre> NON SUPPORTED MsgID[0x%04x]…`; el de soporte es `… <Nombre> SUPPORTED MsgID…`). La clasificación es **exacta** (el nombre va seguido literalmente de ` NON SUPPORTED MsgID` / ` SUPPORTED MsgID`), no por proximidad. → **La presencia del nombre NO prueba soporte**: `SetSilentShutterModeForLiro`, `SetShutDriveForLiro`, `SetShutDriveModeForLiro`, `SetShutLowLimitForLiro`, `SetFrontEShutterModeForLiro`, `SetIrisDriveForLiro`, `SetDriveModeForLiro` y `SetMovieAutoSlowshutModeForLiro` **están** en el `libObj.so` de la A6000 **y están rechazados**.

**Coherencia con S169**: el mensaje (capa *camera-user*, `libObj.so`) y el parámetro (capa LiroSeq de `av-cam.bin`) **concuerdan** — solo el A6300 tiene el mensaje `SetShutterTypeForLiro` **y** el campo `shutterType` (+`sc_ShutDrive`, `front_eshutter`, `SilentShutterMode`).

**Regla que deja este hito**: **la presencia de una cadena no prueba una funcionalidad**. Tres casos ya en el repo: la cadena del *rolling shutter* del A6300 **muerta** (S168), el bloque de 128 bytes de `0x43dcfa9e` **sin referencias** (S172) y ahora los nombres `…ForLiro` de la A6000 **todos rechazados**. Antes de afirmar que una cámara «tiene» algo por el nombre de su cadena, hay que comprobar que el nombre **se usa**.

**Efecto en S51: NINGUNO — S51 sigue A=NO, B=NO, C=NO.** El `libObj.so` es una capa de *mensajería*, no una implementación; la ausencia estática no demuestra incapacidad del hardware.

[Informe](../analysis/s174_forliro_api/forliro_api.md) · [doc](../docs/capture/s174-forliro-api.md). Siguiente: por qué el `CamMsgConv` de la A6000 y la A7S no soporta ninguno (¿otra ruta de conversión?); qué ganan exactamente los 6 del A6300; si los mensajes rechazados se envían por otra vía (tabla `MsgID` → manejador).

## S175 — el módulo `[LIF_DEBUG]` (13 trazas): el diagnóstico del sensor de luz de la cámara (22-10-2026, línea de RE general)

**VERIFICADO (11 tests, `tests/test_s175_lif_debug.py`):** `[LIF_DEBUG]` es la traza de diagnóstico del **subsistema de sensor de luz de la cámara** (`CAM LIF SENSER`): su inicialización, el registro/desregistro de los *callbacks* de **backup** (`BK`, con `BKID`) y las **copias «shadow»** entre el estado de *backup* y el «shadow». Es el **último** de los 17 módulos «de contenido nuevo» de S130.

13 cadenas en `0x43cfb032`–`0x43cfb224`; **13/0/0** (A6000/A7S/A6300). **14 sitios** (regla estricta) en **3 funciones contiguas** (`0x43a1c9d8` con 8, `0x43a1cb0c` con 1, `0x43a1cb3c` con 5), **0 muertas**, con **logger propio de id `0x125`** (`0x43a1c92c`: mensaje OSAL de `0x9a` B → `osal_try_valloc_msg` `0x435612d0`, `vsnprintf` `0x439c5a04`, `osal_send_msg` `0x43561244`), igual que `[TP_R]` (S156) y `[SAD]` (S167).

**Mecánica**: copia de seguridad **bidireccional** entre el estado «shadow» y el «BK», de **2** elementos (`cmp r7,#2` en `0x43a1caa2`; `cmp r4,#2` en `0x43a1cb9c`), con `bl 0x435614d0` / `bl 0x435614ec` por elemento y `bl 0x435613e8` al cerrar. Contenido: `[BKID]`, `[DataSize]`, `[Count]`, `[HandleValue]`, `[HandlerValue]`, `[Erro]`.

**Los dos nombres de función aparecen SOLO dentro de las trazas**: `cam_lif_senser_copy_bk2shadow` `0x43cfb14d` y `cam_lif_senser_copy_shadow2bk` `0x43cfb18a` (**0** apariciones como símbolo independiente) → son **texto literal**, no símbolos del enlazador.

**Diferencial**: el **subsistema existe en los tres firmware** (`LIF` **64/43/81**, `BKID` **28/23/22**, `SENSER` **12/7/8**) → lo propio de la fw3.21 de la A6000 es la **etiqueta** y los dos nombres escritos como texto: otra vez «se reescribe el logging, no el firmware».

**Negativo acotado**: 0 menciones de obturador, disparo, lectura del sensor, exposición o tiempos → **sin efecto en S51** (A/B/C = NO).

[Informe](../analysis/s175_lif_debug/lif_debug.md) · [doc](../docs/capture/s175-lif-debug.md). Siguiente: qué es el «BK» (backup) y quién registra los *callbacks*; por qué solo 2 elementos; los ids `0x125`/`0x93`/`0xa1` y los helpers `0x435613e8`/`0x435614d0`/`0x435614ec`.

## S170 — el módulo `[ILLUMI]` (34 trazas): el subsistema de iluminación (22-10-2026, línea de RE general)

**VERIFICADO (30 tests, `tests/test_s170_illumi.py`):** 34 cadenas `[ILLUMI]` en la A6000 fw3.21 entre `0x43c40570` y `0x43c40ddc` (bloque contiguo); **0** en la A7S fw3.20 y el A6300 fw2.01. **52 sitios** (regla estricta) en **25 funciones** emisoras, **0 cadenas muertas**, con los **52 pares PIC verificados a mano (52/52)** y sin reuso de registro.

**Corrige la inferencia de S130/S165**: el **subsistema de iluminación es COMÚN a las tres fw** — las cuatro clases RTTI `IllumiDev`, `IllumiAd`, `IllumiCam`, `IllumiRPR0400` existen en las tres con la misma jerarquía, y el acceso al chip es el mismo: `ReadDevice` con dirección `0x39` y registros `0x46` (GetAD) / `0x41` (PollingDevice) en `0x435adffe`/`0x435ae060` (A6000), `0x435afee0`/`0x435affd0` (A7S) y `0x435b0cd0`/`0x435b0dc0` (A6300), con los mismos ids OSAL (`0x520250` bus del dispositivo, `0x720018` ADC LIRO, `0x7a0020` cola de eventos) y los mismos *backup ids* (`0x133003c`/`0x133003d`). Lo **propio de la fw3.21 de la A6000 es la instrumentación**: las 34 trazas `[ILLUMI]` y las **20** cadenas `__PRETTY_FUNCTION__` (`IllumiDiag`, `IllumiGain`, `IllumiLevel`, `IllumiAd`, `IllumiCam`, `IllumiRPR0400`), **0** en la A7S y el A6300.

**Coherencia**: el **id de módulo de traza es `0x133`** (307) — primer argumento de todas las llamadas de log (`movw r0,#0x133`, p. ej. `0x435acdf2`) — y es el prefijo de sus ids OSAL/backup (`0x133003c`, `0x133003d`, `0x13303ba` cola sync de `IllumiDiag`, `0x13303be` de `IllumiCam`). Mismo patrón que el id `0xb5` de la familia `CAM_UTIL` (S173) y el `0x93` de `[TP_R]` (S156).

**Negativo acotado**: 0 de `shutter`/`curtain`/`expos`/`iso`/`apert`/`frame`/`capture`/`photo`/`sensor`/`compens` en las 34 trazas; los 2 `read` son `ReadDevice`/`Backup_read` (**registros del chip de luz**, no del sensor de imagen) y los 5 `sync` son colas OSAL síncronas. El «gain» es la **ganancia del amplificador del sensor de luz** (seleccionada con dos GPIO en `SetGainMode` `0x435aca80`), no la ganancia de imagen → **sin efecto en S51** (A/B/C = NO).

[Informe](../analysis/s170_illumi/illumi.md) · [doc](../docs/capture/s170-illumi.md). Siguiente: qué magnitud física mide el chip `RPR0400` y cómo se usa su lectura (auto-ganancia, filtrado, corrección); la semántica de los 6 subcomandos ADJ de `IllumiDiag`; por qué el módulo emite un evento `key_code` (mismo patrón que `[JOG]`, S165).

## S178 — censo de cobertura de la línea de módulos (22-10-2026, línea de RE general)

**VERIFICADO (8 tests, `tests/test_s178_census.py`):** censo completo de las etiquetas `[XXX]` de la A6000 fw3.21: **372** distintas (techo), **52** con hito de decodificación en el catálogo y **320 pendientes**; **93** son **exclusivas de la A6000** (0 en A7S y 0 en A6300).

**Hallazgo de versionado de plataforma**: la familia **`[STK]`** (`[STK]`, `[STK_AUTO_SAL]`, `[STK_COLOR_SIM]`, `[STK_C_SIM]`, `[STK_TOUCH_SIM]`, `[STK_T_SIM]`) y **`[OSD]`** existen en la A6000 y en la A7S fw3.20 y **desaparecen por completo en el A6300 fw2.01** → son funciones de la **plataforma antigua** (E-mount / pre-LIRO) que la nueva plataforma no arrastra. Es un control de **plataforma**, no de modelo: la A7S (2016) comparte plataforma con la A6000; el A6300 (2019) es de otra.

**Otros datos**: `[VDF]` tiene **81 apariciones más** en la A6000 (243) que en la A7S y el A6300 (162). Pendientes más grandes: `[SDF]` 477, `[ERR]` 288, `[VDF]` 243, `[ERROR]` 213, `[BL]` 154, `[VEF]` 149, `[STK]` 76, `[TD]` 73, `[VIDENCSTAT]` 70, `[FACE]` 70, `[RC]` 69, `[DEBUG]` 67, `[GOLFSHOT]` 65, `[WSX]` 59, `[INFO]` 58, `[RE]` 54, `[INT_ERROR]` 53, `[ENCOUCSTAT]` 49, `[CONFIG]` 47, `[BT]` 44, `[CAM_FUNC_MGR]` 43, `[PNL]` 41, `[SAN]` 35, `[AUDPINEDTR]` 34, `[CAM_SCALAR]` 34, `[REMOTE]` 32.

**Salvedad del propio censo**: el patrón de extracción captura también fragmentos de formato (`[D0]`–`[D7]`, `[IN1]`, `[IN2]`, `[NULL]`, `[SIZE]`, `[STAT]`, `[HW]`) → **372 es un techo**, no el número exacto de módulos.

**Efecto en S51: NINGUNO — S51 sigue A=NO, B=NO, C=NO.** El censo es de cobertura, no de contenido.

[Informe](../analysis/s178_census/census.md) · [doc](../docs/capture/s178-census.md). Siguiente: elegir las siguientes etiquetas por **valor** (las que hablan de disparo, lectura del sensor o tiempos: `[VDF]`, `[RC]`, `[EIS]`, `[STABILIZER]`, `[ZPD]`) y no solo por tamaño.

## S177 — el módulo `[CAM_FUNC_MGR]` (43 trazas): el gestor de funciones de cámara (22-10-2026, línea de RE general)

**VERIFICADO (31 tests / 1024 subtests, `tests/test_s177_cam_func_mgr.py`):** 43 cadenas `[CAM_FUNC_MGR]` en la A6000 fw3.21 entre `0x43ca12af` y `0x43cb02f1`; **0** en la A7S fw3.20 y el A6300 fw2.01. **57 sitios** (regla estricta; coincide 57=57 con el mapa global) en **25 funciones**, con los **57/57 pares PIC verificados a mano**; **1 cadena muerta**: `Pseudo AF Stop %d` `0x43cb02f1`.

**Qué es**: la etiqueta de traza del namespace C++ **`Camera::Function`** (RTTI `N6Camera8Function…`, **18 clases idénticas en las tres fw**): un **gestor/despachador de funciones de cámara** que enruta peticiones/respuestas entre 4 clientes (`CamUser`, `CameraBackGround`, `Release`, `CamMain`) y las traduce al bus inter-LSI mediante el puente **`LRBridge`**.

**Tabla de 65 funciones** en `0x43ff17b8` (paso 12 B): `{const char *origin; const char *name; u32 id;}` — comprobado directamente: `[0] "UNKNOWN" id=0`, `[1] "REQ_MOVIE" id=1`, `[2] "REQ_MOVIE_REC" id=2`, `[3] "REQ_STILL_EE" id=3`, `[4] "REQ_PB" id=4`; `origin` vale 0 en el fichero (se inicializa en runtime, `0x43787d88`).

**Despachador `0x43805930`** (`Function/LRBridge.cpp`): tipo de mensaje u16 en `[msg+2]`, `sub.w r2,r3,#0x3000` (`0x4380599a`), `cmp r2,#0x30` (`0x4380599e`) y **`tbb` de 49 entradas** (`0x438059a2`) → **tipos de bus `0x3000`–`0x3030`**. Los **12 `type_id`** del puente salen de las comparaciones en `0x43805ec0`–`0x43806126` (`REQ_APP_SND`, `APP`, `APP_CMP`, `REQ_V2ND_SND`, `V2ND`, `V2ND_CMP`, `REQ_VSYNC_CUST_SND`, `VSYNC_CUST`, `VSYNC_CUST_CMP`, `REQ_FSPSUM_SND`, `FSPSUM`, `FSPSUM_CMP`); cada rama se habilita con un bit de máscara en `[obj+0x41]`; campos impresos: `type_id` (`[msg+0]`), `from_lsi` (`[msg+1]`), `req_seq_id` (u16 en `[msg+2]`).

**Firma mecánica del rewrite de logging (verificada a mano)**: las **43/43** cadenas tienen **gemelo exacto en `vaddr+16`** — el prefijo `"[CAM_FUNC_MGR]: "` ocupa exactamente **16 B** y se antepone al literal original, que **queda intacto**: no se reescribe la cadena, se antepone una copia.

**Es cambio de logging, no de código**: los **textos interiores** están presentes **43/43** en la A7S y **42/43** en el A6300 (la A7S solo tiene la traza *vieja* en `0x437ac63e` → `bl 0x438f7114`; el A6300 en `0x437f621e` → `bl 0x43986518`), y la **tabla de 65 funciones no existe en el A6300** (`REPLY_` **0**, `MSG_NONE` **0**, `FUNC <= ` **0**; en la A6000 27 / 1 / 4).

**Negativo acotado**: 0 de `shutter`/`silent`/`curtain`/`electro`/`mech`/`expos`/`iso`/`apert`/`sensor`/`shut`/`svd`/`frame` en las 43 trazas. Gestiona órdenes de alto nivel (`REQ_CAPTURE_START/END`, `REQ_AF_START/STOP`, `REQ_AE_START/STOP`…) pero **no baja al nivel del obturador**; el `unretract` `0x43cb027c` es del obturador **mecánico** → **sin efecto en S51** (A/B/C = NO).

[Informe](../analysis/s177_cam_func_mgr/cam_func_mgr.md) · [doc](../docs/capture/s177-cam-func-mgr.md). Siguiente: la relación entre el `id` de la tabla de 65 funciones y los tipos de bus `0x3000`–`0x3030` (dos espacios de ids distintos); la lista de LSIs; la semántica de `APP`/`V2ND`/`FSPSUM`/`VSYNC_CUST`.

## S179 — el módulo `[CAM_SCALAR]` (34 trazas): la capa HAPI de imagen de la cámara (22-10-2026, línea de RE general)

**VERIFICADO (38 tests, `tests/test_s179_cam_scalar.py`):** 34 cadenas `[CAM_SCALAR]` en la A6000 fw3.21 entre `0x43cb045a` y `0x43cc679a` (33 en un bloque + 1 aislada); token **34/0/0**. **47 sitios** (regla estricta) en **14 funciones**; de las 34 cadenas, **31** están en el mapa global y **vivas**, y **3 están muertas** (`0x43cb0aa5`, `0x43cb0abe`, `0x43cb0ae3`, con sus gemelos `+14` también muertos); **0 punteros absolutos** de 4 B. **94/94 pares PIC verificados a mano** (47 nuevos + 47 gemelos), 0 fallos y **0 discrepancias** contra el mapa canónico (17 525 destinos).

**Segunda confirmación de la firma del rewrite de logging**: **34/34** cadenas tienen **gemelo exacto en `+14`** — el prefijo `"[CAM_SCALAR]: "` ocupa **14 B** antepuesto y el literal original **queda intacto y referenciado** por el logger global `0x43902718`; la fw3.21 **duplica** la traza (nueva con logger de módulo `0x4380a5d0`, **id de módulo 5**, **nivel 6**, flag 1, + la vieja). Es el mismo mecanismo que en **S177** (prefijo de 16 B) → **el prefijo no tiene longitud fija: se ajusta al nombre del módulo**.

**Qué es**: la **capa HAPI de imagen** de la cámara: despachador `0x4380a688` con `tbh` de **23 entradas** (base `0x4380a72c`) → `MSG_ID` **0x5001–0x5017**; `SetSpecialSequence` `0x4380c344` valida `ExposureCount`=1, `RecordCount`≤5 y `CapMode`=`CAP_SINGLE`; handles DMM `YCC_FULL`/`RAW_FULL`; ficheros `HAPI_Filter_TBOX.cpp` `0x43cb07b7` (línea 99), `CS_Command.cpp` `0x43cb0b85` (línea 112) e `ImageParamCapture_SyncBranch.cpp` `0x43cc6779`.

**Hipótesis del enunciado REFUTADA**: **no** es la capa del acelerador escalar «SA» — **0 llamadas** al rango `NS_SCALAR_INFRA` (`0x43990000`–`0x439c0000`, donde viven `[SAD]`/`[SFRA]`/`[SFRS]`) y **0** referencias a `sa_func_*`; todas las cadenas `SCALAR`/`Scalar` de la A6000 (88 + 261) son de `NS_SCALAR_INFRA`. La sigla **se deja sin desarrollar** (`CAM_SCALAR` = 34 apariciones = 34 trazas; `CamScalar`/`cam_scalar` = 0).

**Es ETIQUETADO, no contenido nuevo (refina a S128)**: los **núcleos** sin prefijo están presentes **34/34** en la A7S y **34/34** en el A6300 (mismo código: A6000 `0x4380a688`, A7S `0x4382d49c`, A6300 `0x438c8dxx`; mismos ficheros y mismos 29 nombres `req_*`/`Start_*`/`Check*`). Los cambios **propios del A6300**: `%s: Develop(RAW->YC) fail.`, `%s: invalid parameter on simple develop.` y `req_image_clone` → `req_yc_image_parse`.

**Negativo acotado**: 0 de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`shut`/`svd`/`shd`/`spl`/`frame`/`imager`/`drive`/`brack`/`sweep`/`still`/`movie`/`focus`/`iso`/`apert`/`sync`/`vsync`/`scan`; el único `expos` es `ExposureCount` → **sin efecto en S51** (A/B/C = NO).

[Informe](../analysis/s179_cam_scalar/cam_scalar.md) · [doc](../docs/capture/s179-cam-scalar.md). Siguiente: por qué quedaron 3 literales muertos; la equivalencia `MSG_ID`↔petición para los 6 ids con destino por defecto (`0x4380ae0e`) o «imagen inválida» (`0x4380adf8`); la lista completa de `CapMode`; el criterio de reparto `[CAM_SCALAR]` vs `[IMAGING_CAP]`/`[IMAGING]`.

## S180 — el módulo `[REMOTE]` (32 trazas): el mando a distancia por UART (22-10-2026, línea de RE general)

**VERIFICADO (50 tests, `tests/test_s180_remote.py`):** 32 cadenas con el token `[REMOTE]` en la A6000 fw3.21 (rango `0x43c25b47`–`0x43c26319`); token **32 / 0 / 0** (A6000/A7S/A6300). **33 sitios** PIC (regla estricta, reproducidos por el agente principal) en **16 funciones**, **0 cadenas muertas**; los **33/33 pares** verificados a mano (0 fallos, 0 reuso de registro) y el escaneo local reproduce el mapa canónico con **0 discrepancias**. El mapa global contiene **32** destinos con `[REMOTE]`, y una de ellos (`[ACCY][INFO][REMOTE]:%d:ZOOM OFF  KEY:%08X…` `0x43c26186`) se referencia **dos** veces (`0x43566c8e`, `0x43566cb0`) → 33 sitios sobre 32 cadenas.

**Precisión estructural (verificada por el agente principal)**: las 32 cadenas **no son cadenas propias**, son **subcadenas** de cadenas con el formato **`[ACCY][<NIVEL>][REMOTE]:%d:<mensaje>`**, y **la referencia PIC apunta al INICIO de la cadena completa** (p. ej. `0x43c25b47` = `[ACCY][INFO][REMOTE]:%d:NotifyUartCommand…`), no a la posición de `[REMOTE]`. Repartición de niveles por el prefijo: **INFO 24, ERR 3, DEBUG 3, WARN 2** → **el nivel va en la propia cadena** y el logger `0x435661e4` recibe `(id_módulo=93, ?, nivel, fmt, …)`; por eso el mapa global no lista las que empiezan por `[REMOTE]` (empiezan por `[ACCY][…]`): no es contradicción, es la misma regla.

**Qué es**: el **subsistema de MANDO A DISTANCIA (control remoto por UART)**, y es **exactamente** el sub-bloque `REMOTE` de `[ACCY]` que S136 ya había delimitado (mismo rango, mismos 33 sitios, mismas 16 funciones) → **no es un módulo nuevo**. Lo implementa la clase RTTI **`AccyUmDeviceRemote`** (`0x43c26340`, `type_info` `0x43fd7dbc`, vtable `0x43fb9114` con los 8 métodos virtuales del accesorio) → **`REMOTE` sí tiene base textual**; `ACCY`/`UM` se dejan sin desarrollar.

**Estructura de datos (verificada)**: objeto con flags `+0x3C` GF, `+0x3D` SS, `+0x3E` Freeze, `+0x3F` Photo, `+0x40/+41/+42` Tally, `+0x34/+0x38` Zoom, `+0x0C` Spinal; estado serializado en **3 bytes** (`SaveInfo` `0x435664d0` / `RestoreInfo` `0x43566580`); tabla de **5 códigos de tecla** (`0x0A000009`/`0D`/`08`/`0C`/`11`) y **3 tablas `tbb`** (`0x435662f4`, `0x43566638`, `0x43566960`).

**Cambio de logging, no de código**: **no** hay gemelo «prefijo + original» (a diferencia de S177/S179): el núcleo autónomo `[REMOTE]` está **0/32** en la A7S y el A6300 (las 6 coincidencias en la A6000 son literales de otros sub-bloques `[ACCY]`: `[HELLO]` y `[HOUSING]`) y **no hay doble emisión** (el logger global `0x43902718` no aparece en ninguna de las 16 funciones). Pero **el código del mando existe en los tres**: misma clase RTTI (`0x43c25aed`/`0x43d0ca6c`), misma vtable de 8 métodos (`0x43fb2e14`/`0x4416fd74`), misma tabla de 5 códigos de tecla (`0x43564874`/`0x4355f040`) y `NotifyUartCommand` con la **misma secuencia de instrucciones** (`cmp #0x23`/`cmp #0x37`/`sub #0x30`/`cmp #5`/`tbb`).

**Negativo acotado**: 0 de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`. Lo único: `GUIDE FRAME`, `PHOTO REC`, `Zoom…Speed` y timeouts de UART; el «START STOP» (`0x0A00000D`) es una **tecla genérica** entregada por `NotifyInput` `0x43565814` → el módulo **no ejecuta el disparo** → **sin efecto en S51** (A/B/C = NO).

[Informe](../analysis/s180_remote/remote.md) · [doc](../docs/capture/s180-remote.md). Siguiente: qué hace la tabla `0x0A0000xx` (en particular `0x0A00000D`); la cola OSAL de `NotifyInput` (`0x007A0020`); por qué solo la A6000 fw3.21 trae trazas `[ACCY]`; la categoría UART `'F'` solo del A6300.

## S121 — el módulo `[AIP]` (37 trazas): la interfaz de audio con el escalado (21-10-2026, línea de RE general)

**VERIFICADO (97 tests, `tests/test_s121_aip.py`):** 37 cadenas `[AIP]` en `0x43cdd844`–`0x43cdec50`; **16 funciones** y 6 sub-bloques RTTI: `SaWrapper` (8), `SaBackUpCtrl` (12), `SaDriverBase` (4), `LPS` (11), `SaDriverZoomNr` (1), `SetFader` (1). **Callbacks `Ack`/`Comp`/`Err` en tres capas**: SA (`0x43926d1c`/`0x43926de8`, con los predicados `[r1,#1]==0x14`/`0x13`), LPS (`0x4392b16c`/`0x4392b254`) y driver; los errores llevan `errCode`+`errState` (SA) o `ErrCode`+`ErrStatus` (LPS). **Tabla de backup**: **350 entradas de 12 B** en `0x43bd1964` con `{id = 0x10c0000 + n, offset, size}`; `WriteShadow2BakcupArea` vuelca `0x10c` B (`mov.w r0,#0x10c` en `0x4392ab78`) y `SetAudioNrType` publica el **bit 3** de `bkId = 0x10e0000`. Comandos hacia el escalar en `0x4392ac30` (`Cmd`/`Func` + `Zma`/`Ext`/`Mbx`) y `0x4392acb4` (`Cmd`/`Func`/`Unq`). Buffers LPS `0x82`/`0x83`/`0x85` con longitudes `0x2c`/`0x28`/`0x14`; `SetFader` (`0x4355ae98`) divide por 100/20/otro según `[r0,#0x78]`.

**Quién lo usa**: el **ADF** (S81): `[ADF][INIT]AUDIOIP INIT COMP` `0x43c26411`, tipos `AUDIO_IP_CONFIG_TYPE_*` `0x43c264fa`–`0x43c2659e` y comandos `SetAip0/1`, `GetSa0/1`, `SetSa`, `SetFader`, `SetZoomNr`. **No** es el «SA» de S108 (`Camera::SaFuncDrv`, `sa_func_*`): ninguna de las 37 trazas lo menciona.

**Diferencial**: A7S fw3.20 tiene **las mismas 37**; el A6300 fw2.01 tiene **63** = 37 + 26 (25 `[AIP][ZNR_EE]*` y `SetInstanceNumberExec Err %d`).

**Aporte metodológico (rectificó todo el repo)**: el subagente cuantificó los falsos positivos de cada regla de emparejamiento PIC (estricta 37/37 reales; kill analysis 60 pares = 37 verdaderos + **23 falsos**) y el caso concreto donde falla (`0x4355bcb2` resuelve a `0x43ceb58b`, no a `0x43cde863`, cuyo sitio real es `0x4392ab04`). Con la calibración de S118 (`[SFRA]`: 118 reales = 118 con la regla estricta, 166 con kill analysis, 186 con la ancha) se declaró **regla canónica estricta** y se rectificaron S106, S110, S113 y S115.

[Informe](../analysis/s121_aip/aip.md) · [doc](../docs/capture/s121-aip.md). Siguiente: significado de AIP/SA/LPS/ANR/ZNR/Zma/Ext/Mbx; formato de la cola `AudioIpCmdQueue`; contenido de las 350 entradas del backup.

## S119 — `[APL]`: la apertura/cierre de SA y HW, dentro de `[CAMERA_SA]` (21-10-2026, línea de RE general)

**VERIFICADO (47 tests, `tests/test_s119_apl.py`):** las **42 apariciones de `[APL]` no son un módulo propio**: las 42 están **dentro** de cadenas que empiezan por `"[CAMERA_SA]: "` (13 bytes), p. ej. `[CAMERA_SA]: [APL] HW Open Err %d` `0x43cebde1`, `[CAMERA_SA]: [APL] SA Open Err` `0x43cebe03`, `[CAMERA_SA]: [APL] Calloc InputPrm Err` `0x43cebe46` → **`[APL]` es una etiqueta de segundo nivel dentro de `[CAMERA_SA]`** y la entrada "APL 42" del mapa de módulos de S79 es una sub-etiqueta. 5 funciones emisoras (`0x439cea30` Open 7 trazas, `0x439cebe4` Close 9, `0x439cedd0` Free&Close 4, `0x439ceeb8` Open+ejecución 20, `0x439cf3b8` SA open/close 2) con **42/42 referencias PIC 1:1** bajo la regla estricta; las 5 equivalentes de la A7S en `0x439bcd80`, `0x439bcea0`, `0x439bcfc8`, `0x439bd05c`, `0x439bd3a4`. API: `ExecuteOpenMSG` `0x439d143c`, `ExecuteCloseMSG` `0x439d133c`, `ExecuteCalcStartMSG` `0x439d185c`, `CallocCamSaParam` `0x439d0f58` (la traza la llama *InputPrm*), `GetMemInfo` `0x439d1bd0`, `GetExecUnit` `0x439d168c` (la traza dice *GetZimaNo*); los `unit_hndl` son **handles del DMM** (S113: open `0x43903280`, close `0x43903414`, free `0x43902fbc`).

**Consumidor único**: `[CAMERA_MAIN_TC]` ("ApolloSA"), **un solo llamador** por función (`0x438765ca`, `0x43876650`, `0x438766da`, `0x43876714`, `0x43876a82`); ni `[IMAGING_CAP]` (S106) ni `CamCore` (S107) lo llaman.

**Diferencial A7S fw3.20**: los 42 textos coinciden uno a uno, pero allí **empiezan por `[APL]`** (`[APL] HW Open Err %d` `0x43ce1588`) → la fw3.21 de la A6000 **antepone la etiqueta de módulo** `[CAMERA_SA]: `. El A6300 fw2.01 tiene las mismas 42.

**Aporte metodológico (tercera calibración)**: la regla "ancha" da **67** pares para 42 cadenas reales → 25 falsos positivos comprobados desensamblando. Con S118 (`[SFRA]` 118) y S121 (`[AIP]` 37) son **tres** módulos donde la regla **estricta** coincide exactamente con la verificación a mano.

[Informe](../analysis/s119_apl/apl.md) · [doc](../docs/capture/s119-apl.md). Siguiente: el módulo `[CAMERA_MAIN_TC]` ("ApolloSA"), su consumidor, que sigue sin hito propio; layout de `InputPrm`; por qué la traza dice *GetZimaNo* si la función es `GetExecUnit`; los códigos de error (2, 6, 8, 0xff).

## S111 — el módulo `[TRK]` (215 cadenas) de tracking y detección (21-10-2026, línea de RE general)

**VERIFICADO (17 tests, `tests/test_s111_trk.py`):** 216 apariciones del literal `[TRK` → **215 cadenas** (214 que empiezan por `[TRK` + 1 anidada: `[TRK]: [TRK] cb_func == NULL`) → **207 textos distintos** (8 repetidos en dos direcciones cada uno) en `0x43cebceb`–`0x43cfe31c`, con **288 sitios de referencia** y **47 funciones** (283 strict + 5 relaxed). Sub-bloques: **STK** 76 trazas (saliency, touch, simulación de color y de toque), **BT** 44, **EDTSA** 19, **PMV** 16, **IRO2G** 13, **DETSA** 9, VAE/VAT/VOT 3 cada uno, más las familias STK_AUTO_SAL / STK_COLOR_SIM / STK_TOUCH_SIM. El código del módulo vive en `0x43a30000`–`0x43a39000` (284 sitios, 43 funciones) y los 4 restantes son *wrappers* de sesión en `0x439c0000`–`0x439d0000`; las zonas `sa_stubs` (ZIT), `fc` y `apl_osal` tienen 0 sitios. El firmware embebido incluye **99 ficheros `FC/*.cpp`** (`0x43cef12a`–`0x43cf707a`).

**Diferencial A7S fw3.20**: la A7S tiene **las mismas 215 cadenas y los mismos 207 textos** (listas `only_a6000`/`only_a7s` vacías) y los mismos recuentos (288 sitios, 47 funciones) → **módulo idéntico**, solo cambia su posición en el blob (`0x43ce1492`–`0x43cee615`).

**Nota metodológica**: el subagente usó la regla estricta (*nearest-ldr*, `MAX_GAP=0x40`); con la regla canónica del repo (todos los `ldr` del registro en 4 KB, aceptando solo destinos en el inicio de una cadena) las 215 cadenas dan **214 referenciadas y 657 sitios**. Además se **`ancho el rango de cadenas válidas** de `scan_pic_refs.py` (estaba fijo a `0x43c90000`–`0x43cd0000` y excluía la zona de `[TRK]`, lo que daba 0 referencias)**: ahora acepta `LO HI RUTA_SALIDA` y cubre toda la imagen.

[Informe](../analysis/s111_trk/trk.md) · [doc](../docs/capture/s111-trk.md). Siguiente: límites de las funciones `0x43a376d8`/`0x437a37734`; semántica de los 2 sitios *relaxed*; correspondencia 1:1 de los 99 ficheros `FC/*.cpp` con funciones.

## S115 — `[CAM_IMAGER]`: el driver del imager de la cámara (21-10-2026, línea de RE general)

**VERIFICADO (9 tests, `tests/test_s115_cam_imager.py`):** 371 trazas `[CAM_IMAGER]` (79 del módulo ZIT, ya de S80 → **292 del driver**) en **94 funciones** (`0x43543568`–`0x436dbd66`). **P2S**: dos canales (**DFE0**, **DFE1**), datos **por páginas** (`P2SData[Page:%01x]` `0x43c931d6`), `P2STransferSize` `0x43c931b2`, `P2SFormatter` `0x43c932ac`, `P2S CheckAddrOrder: ORDER ERROR !` `0x43c9327c`, `P2SWaitTransComp` `0x43c93180`, `P2S : Unsupported SyncMode.` `0x43c93156` → es el camino que S56 ("transporte de registros del IMX210, P2S/DFE0") siguió en la línea del obturador. **Interrupciones**: `int_p2s_handler` (+`_dfe0`/`_dfe1`), `int_timer_handler` y el temporizador por canal (`Imager TimerSetFunc/TimerStart Error!! [CH:%02x, err:%02x]`). **SIF** (11 trazas): `SetSyncCode` distingue **sync code en serie** (`0x43c94e55`) o **en paralelo** (`0x43c94e92`), más `SetSIFMode`, `SetSIFSigsel`, `SetDitherSet`, `SetDataEnableParam`, `ReadSIFScodeCnt`, `SyncCodeDetNum`, `SIF AD_MODE`. **`ImagerCommon`** (16): API "macro" hacia el **CISIF** (`Update_IIFINSEL`, `SetCISIFRequest`, `GetCISIFSyncCodeRequest`, `MacroPowerOn/SaveOn/OffRequest`, `Update_CISIFConnectParam`, `Update_MacroRxEnable`), 8 de ellas con `do not use CH_1` → **un solo canal**. **`SubLVDS`** (9): PowerOn/PowerSave/ChangeParam/GetReceiverEnable por bloque, con `SUBLCNTL_DFE1 does not exist on Regulus`.

**Punto de contacto con la línea del obturador**: la exposición y la lectura se programan **por `drive_mode`**: `SetExps : [PrevDrv][NowDrv][NextDrv][svd][shd][spl][shut]` `0x43c93cc2` (**campo `shut`**), `SetExpsZ` `0x43c939b5` (`svrz`, `shrz`, `splz`, `epd`, `epdsel`), `SetRead` `0x43c93fcb` (`AGainCont_EC`, `AGainCont`, `AGainDrv`), `SetReadZ` `0x43c93d67`, `Execute : […][SSBRK_ON][SLEEP_ON]` `0x43c94076`, `Execute. […][SSBRK_ON][SIFSyncCode]` `0x43c940d7`, `Execute0/1` `0x43c93ae2`/`0x43c9413a` (`ssb`, `read`, `svr`), `SetMode […][ntpal]` `0x43c93b2f`. El campo **`shut`** y el **SSB** son los puntos que conectan con S56–S58 (ID1/SSB).

**Diferencial A7S fw3.20**: 0 trazas con el prefijo, pero el mismo driver (P2S, SubLVDS, ImagerCommon, SIF, NTPAL, SSBRK) existe **sin etiqueta** y con menos instrumentación: `SetExps`, `Execute0` y `AGainCont` tienen **0** apariciones en la A7S.

**NO VERIFICADO**: el significado de `svd`, `shd`, `spl`, **`shut`**, `epd`, `epdsel`, `ssb`, `read`, `svr`, `ntpal` (el firmware no expande las siglas) y si `shut` difiere entre A6000 y A7S. Nada de esto **modifica** S51 (A/B/C = NO): no hay ningún mensaje de obturador electrónico.

[Informe](../analysis/s115_cam_imager/imager_driver.md) · [doc](../docs/capture/s115-cam-imager.md). Siguiente: decodificar la tabla de parámetros por `drive_mode` (69 modos, S96) y el significado de `shut`.

## S112 — el módulo `[CAMERA_MAIN_SYNC]` (429 trazas) de sincronización de recursos (21-10-2026, línea de RE general)

**VERIFICADO (12 tests, `tests/test_s112_camera_main_sync.py`):** 429 cadenas `[CAMERA_MAIN_SYNC]` en `0x43c9b409`–`0x43cb5616` (tras reextraerlas: el borrador del subagente apuntaba **un byte después** del inicio real y no cortaba el texto en el NUL). Contenido: **`SyncResMgr`** (55 trazas: `Lock`/`Unlock`/`Free`/`Get` sobre `CAMDEV(0|1)`, RC y APL), volcado de registros `[CAM0]`/`[DDT]`/`[APL0]`, `DFS`/`DVS` (11+5), `Sync_Kick_IDT`/`RCH`/`RCV`, `HS_Sequence` (5) e `int_HS timing`; 101 sub-bloques distintos (160 sin etiqueta, `SyncResMgr` 55, `APL_ERR` 17, `jpeg` 13, `DFS` 11, `Sequence_Movie` 9). **Mapa función→traza completo** (regla estricta): 425 cadenas referenciadas, 489 sitios (las que más emiten: `0x4354d740` 57, `0x43728dec` 44, `0x43812848` 40, `0x43812f34` 35, `0x437298e8` 32, `0x4379bb90` 29).

**Diferencial A7S fw3.20** (verificado byte a byte, ignorando especificadores de formato): 0 trazas con el prefijo y **418/429** mensajes comunes; los **11** exclusivos de la A6000 son `CamOutV` `0x43ca2de1`, `CamV` `0x43ca35b6`, `CONNETCT_COMP err` `0x43ca3fe7`, `DISCONNETCT err` `0x43ca4045`, `SuperSlowMotion[Buffering] error` `0x43cb0ded`, `Sync_Kick_IDT: overflow` (2), `Sync_Cam_Setting: DIST_RSLT_NG …` `0x43cb10f7`, `Sync_Kick_RCH: overflow` (2) y `EC::CapISO Error` `0x43cb55dd`.

[Informe](../analysis/s112_camera_main_sync/camera_main_sync.md) · [doc](../docs/capture/s112-camera-main-sync.md). Siguiente: significado de `Sync_Kick_IDT/RCH/RCV` y del contador `%d/8V`.

## S114 — el motor de secciones de la captura: 17 ids ↔ 17 etapas (21-10-2026, línea de RE general)

**VERIFICADO (9 tests, `tests/test_s114_sections.py`):** cierra la pregunta abierta de S106. **15 de las 17 secciones** de la tabla `{id u32, manejador u32}` de `0x43ff8fb4` quedan **nombradas**: `0x01` = **Prelight** (nuevo: el manejador `0x437eb144` llama a `0x437eb07c`, que registra `CapturePrelight_Selector.cpp`) y las 14 restantes por su propio `*_Selector.cpp` (`0x02` Exposure, `0x03` Read, `0x04` AfterRead, `0x05` DevEntry, `0x07` CorrectRaw, `0x08` OpdBeforeNR, `0x09` Develop, `0x0a` Marble, `0x0b` FeatureEffect, `0x0c` AfterEffect, `0x0d` Encode, `0x0e` AfterEnc, `0x0f` SortJpeg, `0x10` DevExit). **`0x00` (`0x437eabfc`) y `0x06` (`0x437eaa5c`) no tienen nombre** en el firmware: `0x00` es un selector puro de perfil (2 llamadas: `0x43ae75dc` obtener contexto, `0x43ae76ca` fijar modo) que elige un registro de 20 B según el modo; `0x06` tiene la misma forma que `0x01` pero sin llamar al selector de Prelight. Además **5 de los 16 nombres los registra código fuera de la tabla** (`SequenceFilter` en 5 funciones con 14 registros; `CapturePrelight` en 2; `CaptureDevelop`+`CaptureMarble` en una compartida) → existen **selectores auxiliares** que no son secciones.

**Método**: referencia PIC de la cadena → prólogo Thumb → si el sitio cae dentro del manejador, ese es el selector; si no, sus llamadas `bl` (capstone) → `0x01` llama al selector de Prelight.

[Informe](../analysis/s114_sections/section_engine.md) · [doc](../docs/capture/s114-section-engine.md). Siguiente: significado de `0x00` y `0x06`; la tabla de 20 B por sección; la relación entre secciones (`SectionQueueManager.cpp` `0x43caaf62`, `SectionEndFunc.cpp` `0x43caea54`).

## S113 — `[CAM_DMM]`: el gestor de memoria dinámico de la cámara (21-10-2026, línea de RE general)

**VERIFICADO (11 tests, `tests/test_s113_cam_dmm.py`):** 54 trazas `[CAM_DMM]` (todas de error) `0x43cce6ae`–`0x43ccf1c3`, con la implementación en **25 funciones contiguas** `0x439011d8`–`0x43903d5c`. **11 operaciones**: `AllocNew` (4), `AllocNewRdv` (4, *rendezvous*, confirmado por `MemoryHandle::AllocRendezvous` `0x43cceb4c`), `AllocShare` (4), `Free` (2), `FreeRdv` (2), `Open` (3), `Close` (2), 4 `MemoryHandle::*` (5) y las asíncronas `AsyncAllocNew` (9, función `0x439037c0`), `AsyncAllocRule` (7, `0x43903b80`), `LoadExtraMap` (7, `0x43903d5c`). **4 clases de error** del DMM: `ERR_DMM_RET_CODE` (10), `ERR_DMM_DIFFERENT_COMP` (10, con `msg_id`/`my_id` → la unidad pertenece a otro componente), `ERR_DMM_HANDLE` (4), `ERR_DMM_OPEN` (5); y **4 de capa OSAL** en las asíncronas (`ERR_OSAL_MSGQ`, `ERR_OSAL_HANDLE`, `ERR_OSAL_UIPC`, `rcv Invalid Src!`) → la frontera **DMM↔OSAL** del firmware es real (S38). El userland `DmmAccess` de `libmprctrl.so` (S37: `DmmAllocateNEWAndOpen_body`, `DmmShare`, `DmmCloseORFree_body`, `GetUnitHandleFromDmmAlloc`, `GetDMMRetMsg`) es **cliente** de este servidor, no una reimplementación.

**Diferencial A7S fw3.20**: 0 trazas con el prefijo; **50 de las 54** tienen mensaje equivalente sin etiqueta; las 4 restantes son `AllocNew`, que en la A7S se registraba como `AllocNew(DMM_OPTION_NOUNIT_WARN): ERR_DMM_RET_CODE!: %x` (`0x43cb4f99`) y que la fw3.21 sustituyó por cuatro mensajes detallados.

[Informe](../analysis/s113_cam_dmm/dmm_module.md) · [doc](../docs/capture/s113-cam-dmm.md). Siguiente: valores numéricos de `ERR_DMM_*`/`ERR_OSAL_*`; formato del mensaje OSAL asíncrono; tabla de reglas de `AsyncAllocRule`.

## S108 — el módulo `[CAMERA_SA]` (231 trazas) del acelerador escalar (21-10-2026, línea de RE general)

**VERIFICADO (4 tests, `tests/test_s108_camera_sa.py`):** 231 trazas `[CAMERA_SA]` en `0x43cc5286`–`0x43cef0d8`: la capa de cámara que reporta errores y estado del acelerador escalar (`Camera::SaFuncDrv`, S84), en 13 sub-bloques —APL (27), gestión de memoria (20), errores `GetAddr` (35), alineación de parámetros (29), paso de mensajes/mailbox (18), parámetros DUALREC (14), cierre de handles (20), referencias `sa_func_*` (8), errores especiales (4) y códigos `SA_FUNCDRV_E_OSAL/RSLTCODE/ERRCODE` (3)— más 51 de contenido mixto. **8 de las 19 familias `sa_func_*`** de S84 tienen traza directa aquí (`BDEX_exit`, `BFNR_release`, `BOKS`, `LFNR`, `KKNR`, `NFLASH`, `YKNR`, `DUALREC_BAYER`).

**Diferencial**: la A7S fw3.20 y el A6300 fw2.01 tienen **0** trazas con la etiqueta y los **231/231** mensajes **idénticos sin ella** → la fw3.21 solo añade el prefijo de módulo.

**Correcciones de la revisión** (agente principal): el borrador ponía "Parámetros Inválidos: 17" y omitía la categoría "Otros" (las 13 filas sumaban 195, no 231); daba `ExlHelper`/`MonPowersave` por presentes en `[CAMERA_SA]` (no lo están: son de `[CAMCORE]`, S107); y afirmaba que el A6300 tenía más trazas (tiene las mismas 231, sin etiqueta).

[Informe](../analysis/s108_camera_sa/camera_sa.md) · [doc](../docs/capture/s108-camera-sa.md). Siguiente: atribución función→traza (el esquema PIC de S110 permite hacerla) y el formato binario del mailbox del SA.

## S110 — `Camera::YC`: el motor de imagen de la A6000 (21-10-2026, línea de RE general)

**VERIFICADO (15 tests, `tests/test_s110_camera_main_yc.py`):** `[CAMERA_MAIN_YC]` = **970 trazas** `0x43ca88f6`–`0x43ccd469` en 4 bloques. **API de 8 funciones**: `api_YC_InitCap` `0x437cf5f0`, `api_YC_SetCapBoks` `0x437d8c88`, `api_YC_SetCapStar` `0x437cfe94`, `api_YC_SetCapTbox` `0x437d88e4`, `api_YC_SetSaCamDsp` `0x437ce0cc`/`0x437d77a8`/`0x437d8940`, `api_YC_SetVdPreParam` `0x437d0768`/`0x437d5608`/`0x437d9a04`, `api_YC_LfnrSetParam` `0x437d8bd4`, `api_YC_DEV_SetCoodinate` `0x437d9d1c`. **12 jobs**: `job_YC_Initialize` `0x438aa574`, `job_YC_ModeManager` `0x4389f29e`, `job_YC_SetParam` (15 sitios), `job_YC_SetParamOn` `0x438b7c48`, `job_YC_SetParamOff` `0x438b7ba4`, `job_YC_SetParamPrelight` `0x4389b80c`, `job_YC_SetPreParam` `0x4388bb54`, `job_YC_SetSaCamDspParam` `0x4388b2c4`, `job_YC_CalcParam` (14 sitios), `job_YC_SetCapBoks` `0x4387f4b0`, `job_YC_SetCapStar` `0x438aec84`, `job_YC_GetTagPointer` (19 sitios). **141 sub-módulos etiquetados**: `SHD` 219, `ITP` 90, `YAP` 79, `DCV` 42, `OLC` 37, `NR` 36, `CLP` 29, `MARBLE` 24, `KKNR` 22, `PFR` 19 (las siglas **no están expandidas** en el firmware). **Mapa función→traza**: 968 cadenas en **304 funciones** (1 756 pares), **958** referenciadas (kill analysis) y **2 cadenas muertas** confirmadas (ni PIC ni puntero absoluto). **119 ficheros fuente** embebidos en la zona: `Sequence_Common.cpp` `0x43cb14a1`, `Sequence_Movie.cpp` `0x43cb31f1`, `yc_clp_common.cpp` `0x43cb81ac`, `init_cam_SetCamParam.cpp` `0x43cb40b8`, `SyncLoader.cpp` `0x43cb397a`, `CS_ExifMakerNote.cpp` `0x43cc56dc`, `ddl_stitch.cpp` `0x43cc6964`… **Comprobación cruzada con S78** (Ghidra): la atribución PIC da `job_apc_main_stl` → `0x438b3ea8` y `job_apc_main_mov` → `0x438b5810`, las mismas direcciones de S78.

**Diferencial A7S fw3.20**: 0 cadenas con el prefijo (los mismos mensajes existen sin etiqueta) y, comparando el texto sin prefijo, **969 de las 970** cadenas de la A6000 existen también en la A7S; la única traza nueva de la fw3.21 es `HD_SWEEP_HOLD  =%x` (`0x43cbc27c`).

**Corrección de método (arrastrada a S106):** el escáner PIC emparejaba cada `add rX,pc` con el `ldr` más cercano del registro y se detenía en el primer destino válido; como el registro se reutiliza, atribtaba mal algunas referencias. Corregido (se prueban todos los `ldr` del registro en 4 KB y solo se aceptan destinos que caen en el inicio de una cadena): S106 pasa de 694/697 a **696/697** (de 3 cadenas muertas a **1**, `0x43ca9b12`).

[Informe](../analysis/s110_camera_main_yc/yc_engine.md) · [doc](../docs/capture/s110-camera-main-yc.md). Siguiente: significado de las siglas (SHD, ITP, DCV, OLC, CLP, PFR…); tabla de despacho de jobs (no localizada); enlace por código entre `api_YC_SetCapBoks/Star/Tbox` y las etapas `Stage_BOKS/STAR/TBOX`; sentido de `HD_SWEEP_HOLD`.

## S107 — `Camera::CamCore` y la pila de recursos `ResourceStack` (21-10-2026, línea de RE general)

**VERIFICADO (9 tests, `tests/test_s107_camcore.py`):** 37 trazas `[CAMCORE]` en la fw3.21 de la A6000 (`0x43c905ca`→`0x43cebcb2`) y **0** en la A7S fw3.20. RTTI: `N6Camera7CamCore8RdcImageE` `0x43c906b6` y `N6Camera7CamCore13SplitRdcImageE` `0x43cb0b94`. Contenido: SGC (`GetFlowType: No SgcTable` `0x43c905ca`), RDC/PFR (memoria PFR `0x43c90846`/`0x43c9088e`, `PFR in width[%d] > 596` `0x43c90ca3`), AIF (`AIF%d out[%d] > memsize[%d]` `0x43c90a96`, `pbl_aif_set_func` `0x43c90abd`, extents 1 o 2), `MemoryPool has no space.` `0x43c908e7`, `ResourceBase::Release was called without acquire` `0x43c90ec5`, `ExlHelper` (5 cadenas `0x43c90f98`–`0x43c91074`), *setter* de DMA (6 cadenas `0x43c910a4`–`0x43c91160`), `MonPowersave` `0x43c90f07` y corrección de defectos (`Acl::CAMHEAD_Z1C::setDefectPt` `0x43cebcb2`). **Las siglas (SGC, RDC, PFR, AIF, Exl) NO están expandidas en el firmware**: cualquier desarrollo es hipótesis.

**Pila `ResourceStack`**: 4 mensajes dentro del bloque `[IMAGING_CAP]` (`0x43ca10d1` `ResourceStack)CamCore Release Error!`, `0x43ca110d` `rcct_Release err RC`, `0x43ca11c2` `Dfe Release Error!`, `0x43ca120f` `ResStack) GetMemIndex Err handle`) → la pila de recursos de CamCore la consume el gestor de captura still (S106).

**Corrección de la revisión** (agente principal): el borrador daba por no verificada la presencia de `ExlHelper` (5) y `MonPowersave` (1) en la A7S — **existen** en ambos blobs, sin etiqueta; la fw3.21 solo **añade la etiqueta** `[CAMCORE]:`/`[IMAGING_CAP]:`. También se corrigieron los sitios de referencia de las trazas `sa_func_DUALREC_*` (los reales: `0x437ed95e`, `0x437ee4ae`, `0x437ee716`, `0x437eeb34`, `0x437ee84e`).

[Informe](../analysis/s107_camcore/camcore_resources.md) · [doc](../docs/capture/s107-camcore-resources.md). Siguiente: significado de SGC/RDC/PFR/AIF/Exl; formato interno de la ResourceStack; por qué 2 de las 5 cadenas `ExlHelper` no tienen referencia PIC.

## S106 — `IMAGING_CAP`: el gestor de captura still de la A6000 (21-10-2026, línea de RE general)

**VERIFICADO (18 tests, `tests/test_s106_imaging_cap.py`):** `[IMAGING_CAP]` = **697 trazas** `0x43c9b335`–`0x43ccab72` en 11 bloques; es el **gestor de captura still** (no el pipeline de vídeo, no el obturador). En el mismo bloque de cadenas el firmware lleva **83 nombres de fichero fuente** (`0x43ca8e14`–`0x43cb0cbe`): 16 `*_Selector.cpp`, 10 `CaptureUtility*.cpp`, 9 manejadores, 6 `RawMemManager*.cpp`, 8 `Stage_*.cpp`, `CaptureManager*.cpp`, `SectionController.cpp`, `CaifCom_Control.cpp`, `NotifyController.cpp`, `ImageParamCapture*.cpp`… → así se reconstruye la arquitectura real. **Motor de secciones**: tabla de **17 entradas** `{id u32, manejador u32}` en `0x43ff8fb4`; el despachador `FUN_437e534c` copia `0x88` B y busca el id entre 17; cada manejador devuelve un bloque de **20 B (5 u32)** con los parámetros de la sección, elegido según el modo de captura; 14 de los 17 referencian su `Capture<Etapa>_Selector.cpp` (`Exposure`, `Read`, `AfterRead`, `DevEntry`, `CorrectRaw`, `OpdBeforeNR`, `Develop`, `Marble`, `FeatureEffect`, `AfterEffect`, `Encode`, `AfterEnc`, `SortJpeg`, `DevExit`); los ids `0x00`, `0x01`, `0x06` no lo hacen y `CapturePrelight`/`SequenceFilter` se referencian fuera de la tabla → asignación id↔etapa completa NO VERIFICADA. **CapMgr**: eventos `LastDetectionEnd` `0x43ca9caa`, `NotifySyncStart` `0x43ca9cf2`, `StartRawSequence` `0x43ca9dc7`, `EndRawSequence` `0x43ca9e81`, `CaptureEnd` `0x43ca9d55`, `CheckLastDet` `0x43ca9dfd`, `CaptureCancel_PowerOffDetect` `0x43ca9d85`; el despachador `FUN_437ddf4c` salta con una tabla de 16 entradas en `0x43bc4e08`. **CAIF**: `CAP_REQ`/`CAP_REQ_CLR`/`CAP_SETTING`/`CAP_START`/`CAP_DATA`/`CAP_V_COM` con dirección `[EN->CA]`/`[CA->EN]`/`[CA->AVIP]` (`0x43cca4fb`–`0x43cca8c3`); `CAP_*` son nombres de mensaje del protocolo, no estados internos. **CamCore**: 8 modos de adquisición (`MODE_CAP`, `MODE_CAP_DRP`, `MODE_CAP_PREREVIEW`, `MODE_CAP_SNR`, `MODE_CAP_SNR_PREREVIEW`, `MODE_SNR_BUS_THROUGH`, `MODE_SNR_BUS_THROUGH_PREREVIEW`, `MODE_CDET`). **Memoria**: `ImageParam_Capture_Base` AddRef/Release/ALL Released (`0x43ca9842`–`0x43ca99d0`), `RawMemManager` (MemPool/MemBuffer/MemRuleLib/UnitTypeLib), `GetMem_*`/`ShareMem_StlRaw8`/`UseRaw_DualRec`/`FreeRaw_DualRec`, DMM (`SetDmmInfo) FATAL! overwrite` `0x43ca9bd1`. **Método**: las cadenas no se apuntan con punteros absolutos, sino con el esquema PIC `destino = literal_del_pool + (add rX,pc + 4)` (verificado con `0x437284da`→`0x43c9b335` y `0x437f5b4a`→`0x43cad93c`): **690 de las 697** cadenas referenciadas (regla canónica *estricta*); las **7** restantes (los cuatro `DistV_RC`/`DistH_RC`, `0x43ca9b12` `ShareMem_StlRaw8 Err…`, `0x43cc7d5c` `%s: ContrastPlus error` y `0x43cc839c` `Rch_Rcv_Zima_Base Err…`) no tienen referencia alguna (ni PIC ni puntero absoluto) → cadenas muertas. *(La «corrección» de S110, 694→696, se apoyaba en una regla que inventa referencias; la kill analysis tampoco es exacta. La regla canónica es la estricta, validada a mano en `[SFRA]` y `[AIP]`. Metodología: `analysis/s106_imaging_cap/pic_xref_methodology.md`.)* **Diferencial A7S fw3.20**: 0 cadenas con el prefijo `[IMAGING_CAP]`; los mismos mensajes existen **sin etiqueta** (`CapMgr) LastDetectionEnd…` `0x43cae3b3`, `SectionCtrl) Fatal!…` `0x43caefd1`) → la fw3.21 **añade la etiqueta**; los 16 `*_Selector.cpp` están en A6000, A7S y A6300.

**Negativo verificado:** 0 apariciones de `shutter`/`silent`/`EFCS`/`curtain`/`mechan` en las 697 trazas → el gestor de captura no registra nada del obturador. **Sin efecto en S51 (A/B/C = NO).**

[Informe](../analysis/s106_imaging_cap/imaging_cap_architecture.md) · [doc](../docs/capture/s106-imaging-cap.md). Siguiente: ids de sección sin nombre (`0x00`, `0x01`, `0x06`); significado de los 20 B por sección; formatos binarios de CAIF y `MSG_ID_SDF_*`.

## S105 — panorámica/barrido, bracketing e intervalo (21-10-2026, línea de RE general)

**VERIFICADO (305 tests, `tests/test_s105_panorama.py`):** `CaptureManager::CaptureStart` (`0x437df646`) discrimina el modo con un **campo de 2 bits** del contexto de captura `0x43e9b548`; en el valor 2 pide la petición **`0x301f`** (`movw r0,#0x301f` en `0x437df7a2`; error `[IMAGING_CAP]: !!! Can't send Panorama cmd` `0x43caa019`). Cadena: `Stage_InitializeSweepAndSpoolBranch` (`0x437f0838`) → `Stage_Panorama::PanoramaSweepStart` (`0x43549020`) → `PanoramaSweepStart` (`0x437e6b3c`, abre/cierra el encoder JPEG por trama) → `UpdateSweepCanvas` (`0x437e751c`, `seq_brcEncode()`) → `PanoramaSweepEnd` (`0x437e6e78`, `cmp_execStitchPreProcess()` + `cmp_checkFillResidual()`) → `seq_panoramaClippingDecode` (`0x43780eb4`) → `PanoramaStitch` (`0x438bcef8`: `seq_initStitch`/`seq_panoramaParallelStitch`/`seq_endStitch`) → `PanoramaResize`/`PanoramaResizeEncode`. El stitch es **por tiras** (`PanoramaStripSequence::StripInfo` `0x438f4bcc` consume `PreProcessResult::Strip[]` `0x43ccd5fa`); el **número de capturas no está en el firmware** (lo decide el userland). **Bracketing**: en el firmware solo `lc_BracketAF.cpp` (`0x43ca79ba`) → 2 métodos de `Camera::LC` (`0x437c74b6`, `0x437c7554`); el bracketing de EV/WB lo orquesta `libObj.so`. **Intervalo**: `GetCaptureIntervalResource` (`0x437df338`), semáforo OSAL `CAPTURE_INTERVAL` (`0x43caa2b1`–`0x43caa3f8`) y control por PTM (`[SDF] interval(PTM) %ld` `0x43c7a1a5`, límite 900000 → `[SDF_ERR] interval_ptm over 10[sec]` `0x43c7a1be`).

**NO VERIFICADO:** N de capturas, acrónimo CCNR, unidad del timer OSAL y del PTM, valor concreto del campo de 2 bits, clase LC del bracketing, ids `0x3005`/`0x301f`, algoritmo de `exec_tanzaku`.

[Informe](../analysis/s105_panorama/panorama_bracket_interval.md) · [doc](../docs/capture/s105-panorama-bracket-interval.md). Siguiente: el número de capturas (userland) y el significado del campo de 2 bits del contexto.

## S102 — menú principal (botón MENU): carga y apertura (21-10-2026, línea de RE general)

[S102](../docs/capture/s102-menu-principal.md): `libObj.so` → `viewUnified2.so` (registro de ~150 vistas; índices = `Vn` del log real) → `viewUnified3..8`; vistas BASE_MENU/GLOBAL_MENU/SETTINGMENUX/FNMENU; `DefRootView::ActionOpen*` es el árbitro de arranque, no la tecla MENU. Abierto: evento base de MENU y la vista de disparo que abre BASE_MENU (requiere log de RAM tras pulsar MENU). Anexos: APK por función y decompilación de apps (solo local).

## S101 — selector del tipo de mecanismo y consumidores de campos de ajuste (21-10-2026; etiquetado S70/S71/S72 en commits)

[Conclusiones S101](../docs/capture/s101-conclusions.md) — resumen consolidado; los apartados siguientes son el detalle.

### Recorrido de los 12 puntos abiertos

**VERIFICADO (3 tests, `tests/test_s101_pending.py`):** el bloque de 12 u16 `+0xdd0` lo escribe `0x437b1048` (bytes de estado de captura); la copia en bloque `0x438acc24`/`0x4389efc2` es de un bloque de parámetros con **mapa idéntico en A6000 y A7S** (no la estructura de captura desplazada): **S52 sigue vigente** (rectificado, había una afirmación errónea en la primera versión de S71); `0x437881a8` es el `bl` de init de arranque y `0x43802614` el comando `0x402e`; `Backup 0x3e0005` solo lo leen 2 sitios (cadena de 0x18 B). Los 12 puntos están cerrados (2, 8, 9, 11 como bloqueados/no resolubles; 10 con el grafo de menciones `analysis/s101_shutter_type/graph/module_graph.md`; 12 cubierto por S98/S100). **S51 se mantiene.**
[Informe](../analysis/s101_shutter_type/pending/report.md). **Selector de tipo:** A7S `cap+0x78c = 0x4379ec04(...)` y tipo 2 ⟸ byte `[X+0x7a]≠0` (opción Silent, inferencia) ⇒ `cap+0x748=1`; **A6000 sí tiene selector** (`0x4379316a`, `tbb` sobre `[G+0x808]&7`: 1→tipo 2, 2..6→tipo 1, resto 0 en `cap+0x784`) pero **no** el camino por el byte `+0x7a` ni escribe la bandera. `G=0x43e9b548` (instantánea de S64), campo `0x43e9bd50` (RAM `0x83e9bd50`) vale 0 en la imagen ⇒ tipo 0 por defecto; sin escritor PIC. **Experimento pendiente (requiere tu autorización y backup de NVRAM):** escribir 1 en `0x83e9bd50` y comprobar tipo (`0x83e9bccc`→2) y obturador. Barrido PIC completo: **ningún escritor directo de `G+0x805..0x80e`** (solo lectores `0x43790ac6/654/ee6`, `0x437904a8`, `0x43793106/60`); lo rellena una ruta por puntero (candidato: constructor de petición `0x43868a30`). Ver P1 de [docs/capture/physical-test-plan.md](../docs/capture/physical-test-plan.md). Detalle en `analysis/s101_shutter_type/pending/report.md`.

### Consumidores de `+0x238`/`+0x280` y byte de tipo de Darwin (detalle)

**VERIFICADO (3 tests, `tests/test_s101_block238.py`):** comando `0x40e3` (`0x43fffc60`) → handler `0x438032d5` → `+0x238`; `+0x280` por `0x43802614`. Las 62 referencias PC-relativas al bloque están todas en `0x43802000–0x43805000`; los accesores `0x43804de8` (40 llamadores) y `0x43804c38` (6) no van seguidos de ningún acceso a `0x234/0x238/0x23c/0x280`. **INFERENCIA fuerte:** ambos campos son solo escritura en `av-cam.bin` (explica S64). El parser CAIF de Darwin A6000 ya está resuelto en S53 (descarta el bit `0x20`). **NO VERIFICADO:** lectura vía puntero guardado en global o desde otro binario. S51 se mantiene.
[Informe](../analysis/s101_shutter_type/block238/block238_consumers.md). **Ampliación:** el puntero de los accesores tampoco llega a esos campos (19 destinos revisados). Darwin: `[0x20000050+ch]` solo tiene lectores (`0x1b080/0x1b096/0x1b0b2`), ningún escritor por código ni literal en el pool, y el arranque no hace carga de datos → INFERENCIA: lo rellena el host BIONZ por mensaje (NO VERIFICADO cuál). **Cierre S70:** A6000, A7S y A6300 tienen la misma estructura (3 lectores, 0 escritores del tipo) y el `__scatterload` de Darwin solo inicializa `0x20002a00+`: el bloque de tipos viene del cargador `0x0–0x41ff` (fuera de la actualización) o del host. La diferencia A6000/A7S está en el valor suministrado o en el bit `0x20` (S53). Vía host→Darwin revisada (tabla de 13 mensajes `0x27c68`; ninguna copia llega a `0x20000050–67`, ni con literales sesgados). Siguiente: traza pasiva autorizada de la RAM de Darwin o volcado del cargador; no hay más vía estática.

## S64 — prueba en cámara de SilentShutter (20-10-2026)

- Modo normal por telnet/adb (Tweak, 192.168.1.29): mismo bloque de ajustes; `+0x238`=1 forzado con 3 disparos ⇒ obturador sigue mecánico y la copia `0x83ed4ff0` no cambia; el espejo vuelve a 0 tras un disparo si no se fuerza. Disparo remoto requiere app propia con `CameraEx` (pendiente). Detalle en `docs/capture/s64-silent-ram-nvram-test.md`.
- Cierre de pruebas en cámara (20-10-2026): ningún campo probado (Silent `+0x238`, copia, instantánea `0x43e9b548`, vecinos, override drive_mode, `D+0x78`/`+0x34`) cambió el obturador; solo espejo `+0x210`=1 dio sonido de «disparo múltiple» (4/4, un JPEG por petición; significado NO VERIFICADO). Electrónico total: NO demostrado.
- Disparo remoto (`tools/remote-shutter/`, `CameraEx` sin preview, HTTP :8080) y matriz de 6 disparos con `+0x238`=1/2 y copia de trabajo: **todos sonaron igual** (oído del usuario); bloque alternativo no activo (`ctx+0x57c`=0). Sin obturador electrónico en modo de aplicaciones. Ver `docs/capture/s64-silent-ram-nvram-test.md`.
**VERIFICADO:** escribir `1` en `0x83edf8bc` (service mode, `dd`/dev/mem) y restaurar; NVRAM `flash` sin cambios y RAM 4 MB sin cambios atribuibles al modo (control en otra dirección da los mismos artefactos). Estático: `0x43804610` reinicializa el bloque (`+0x238`/`+0x280`=0) leyendo un byte de backup; ningún lector/escritor de backup ligado a `+0x238`. Sin consumidor de captura. S51 se mantiene.

[Detalle](../docs/capture/s64-silent-ram-nvram-test.md). Siguiente: llamadora `0x437881a8` (¿cuándo se inicializa?), handler hermano `0x43802614`, trazar `+0x280` en el objeto de trabajo.

## S62 — PMCA: inyección de código, service shell y `modelName` (20-10-2026)

**VERIFICADO (fuente + firmware):** `updatershell` inyecta un fdat propio (cramfs con `/bodylib/libupdaterbody.so`, header de 0x30 B por modelo, cifrado de plataforma, guard CRC + modelo/región/versión **sin firma**; familia CXD90014) que el updater ejecuta y que expone un shell USB `0x23` (`SHEL`/`PULL`/`PUSH`/`RMEM`/`BK*`). `serviceshell` (senser, HASP) da terminal + backup `0x603` + ficheros/memoria. `bk w 0x003e0005` no es una dirección ni un offset: es el id BK4 `subsistema 0x3e | índice 5` = `modelName` (16 B, attr `0x01`), escrito en el almacén `/setting` (`nflasha2`) vía `BKWR` o `0x603/2`; el preset de fábrica `CX77500_ALLLANG.bin` la trae como `ILCE-6000` + 7 NUL (`tests/test_s62_backup_modelname.py` 5/5). **NO VERIFICADO:** el efecto «shell mode» al escribir `ILCE-6001`; esa cadena no existe en el firmware 3.21 (solo `ILCE-6000` en presets), así que no es un match literal de tabla. S51 A=NO/B=NO/C=NO.

[Documento](../docs/capture/s62-pmca-injection.md) · [matriz](../analysis/s62-evidence-matrix.json). Siguiente: lectores de `Backup_read` para `0x3e0005` (REA) o traza pasiva autorizada.

## S68 — gestión de batería, energía y carga (NP-FW50) (21-10-2026)

**VERIFICADO (7 tests, `tests/test_s68_battery.py`):** resultado **negativo**: el `av-cam.bin` de A6000 **no contiene modelo del pack NP-FW50** (0 hits de `NP-FW`/`NPFW`/`FW50`, sin tensión/corriente/ciclos/SOC). Sí hay: nivel de batería vía UPM (`Set UPM Battery Level` `0x43ca2dfd`, función `0x4378f364`, lee 8 B de un dispositivo), códigos de estado hacia un MCU (`ACV_BATT_Snd` `0x43c8f95e`, `BATT_AUTH_Snd` `0x43c8f96b`, `BATT_STATE1..3_Snd`, `BATT_TYPE1/2_Snd`, `Box_Temperature_Snd` `0x43c8f9fc`, `ACV Error Voltage` `0x43c8f83b`), **carga del flash** y no de la batería (`SB_CHARGE` `0x43cb4c23`, `CamStrbChargeOn/Off`, `uc_ChargeCommand` `0x43ccd8c2`, `uc_ChargeStatus` `0x43ccd8ef`, `uc_ChargeEnable` `0x43ccd939`, `uc_ChargeForceOff` `0x43ccd96c`, `b_SBChargeReq` `0x43ccdc76`), power save del imager (`MacroPowerSaveOn/OffRequest`, `SubLVDS PowerSaveOn/Off`, `MonPowersave`) y coordinación lente↔voltaje (`Wait E-MountLens ReduceVoltage Wait(%d ms` `0x43cc7aa4`, `CaptureCancel_PowerOffDetect()` `0x43ca9d85`). La A7S (fw3.20) conserva el bloque de estado (`ACV_BATT_Snd` `0x43c983f6`, `ACV Error Voltage` `0x43c982d3`) pero **no** tiene `BatteryInfo` ni los `[IRLight]/[VideoLight] Battery Info`.

**Corrección de la revisión (21-10-2026):** el informe inicial del subagente afirmaba que la A7S carecía de `ACV Error Voltage` y `ACV_BATT_Snd`; es falso y está corregido en `analysis/s68_power/battery_power.md` y fijado por test.

**NO VERIFICADO:** modelo del pack (está en otro binario); destino de los códigos `BATT_*_Snd`; carga por USB/MTP/PD y por base (no hay modelo en el firmware); perfiles de consumo y apagado automático por batería.

**Sin efecto en la línea SilentShutter:** fin electrónico NO VERIFICADO; **S51 A=NO/B=NO/C=NO** se mantiene.

[Conclusiones](../docs/capture/s68-battery-power.md) · [informe](../analysis/s68_power/battery_power.md). Siguiente: el modelo del pack está fuera de `av-cam.bin` (userland o MCU); el bloque de "carga" es del flash; el destino de `ACV_BATT_Snd`.

## S78 — parámetros `apc_*` del motor de imagen YC (21-10-2026)

**VERIFICADO (6 tests, `tests/test_s78_apc.py`):** el motor de imagen `Camera::YC` (logs `[CAMERA_MAIN_YC]: YAP:`) calcula sus parámetros con un espacio de nombres jerárquico `apc_<módulo>.<parámetro>`: **50 parámetros** en **7 módulos**, entre `0x43cc44cb` y `0x43cc4fe4` — `apc_lpf` (2), `apc_mask` (6), `apc_yld` (9), `apc_acm` (4), `apc_zoukou` (18), `apc_coring` (8), `apc_gain` (3). El nombre va **embebido en la cadena de formato** del log (p. ej. `'[CAMERA_MAIN_YC]: YAP:\tapc_lpf.vaplpf\t=%x'` `0x43cc44b4`): no hay tabla de nombres aparte. Cada módulo lo calcula un job distinto (por el prefijo de log referenciado): `apc_lpf`→`0x438b0f80`, `apc_mask`→`0x438b1058`, `apc_yld`→`0x438b11f0`, `apc_acm`→`0x438b177c`, `apc_zoukou`→`0x438b2070`, `apc_coring`→`0x438b2ac4` (`void Camera::YC::job_apc_coring_stl(...)` `0x43cc513d`), `apc_gain`→`0x438b3570` (`void Camera::YC::job_apc_gain_stl(...)` `0x43cc40df`); más los jobs globales `job_apc_main_stl` (`0x438b3ea8`) y `job_apc_main_mov` (`0x438b5810`). El cálculo depende de la **secuencia BDRO** (`bdro_sequence error` `0x43cc4d37`), del **ISO** (`aus_X_ISO` `0x43cc4d68`) y del **efecto de imagen** (`picture_effect` `0x43cc4d8c`); la ganancia se sincroniza entre captura y preview (`AgcContStdBase`/`AgcContBlend` `0x43cc4428`/`0x43cc446e`).

**NO VERIFICADO:** significado exacto de `acmpm`/`acmpp`; dónde se materializan los 50 parámetros (probablemente `Camera::YC::T_AdjRam`, vista en `sjob_GetDetectArea` `0x438ea230`); tabla de valores por modo de captura; comparación con A7S.

[Conclusiones](../analysis/s78_apc/yc_apc_params.md). Siguiente: emparejar cada parámetro con el bloque de RAM donde se almacena y con la función SA que lo consume.

## S79 — mapa de módulos del firmware por prefijos de log (21-10-2026)

**VERIFICADO (5 tests, `tests/test_s79_modules.py`):** el firmware numera sus trazas con un prefijo `[MÓDULO]`; extrayendo todos los prefijos de las cadenas del blob se obtiene la tabla de módulos: **348 prefijos distintos en A6000 (fw3.21)** y **277 en A7S (fw3.20)**. `CAMERA_MAIN` se descompone en **8 submódulos** (VERIFICADO por nº de trazas y rango): `CAMERA_MAIN_YC` (970, motor de imagen: `api_YC_*`/`job_YC_*`), `CAMERA_MAIN_SYNC` (429, `SyncResMgr::Lock/Unlock/Free`, `CAMDEV(0|1)`), `CAMERA_MAIN` (135), `CAMERA_MAIN_TC` (127, **giro**: `GyroStitScl`, `LmtGyroVect`, `calib_r_ave` → enlaza con S70/EIS), `CAMERA_MAIN_LC` (72, **calibración de lente**: `lc_Movie_DM_AF_Util_getMiniRawAddr`… → enlaza con S75/ZPD), `CAMERA_MAIN_CC` (49, **control de captura**: `ExtractCaptureData/CaptureInit/SetReadImageParam/SetNRParam` con `CapMode/ExposureID/ContID/BDROSeq` → enlaza con S78), `CAMERA_MAIN_IM` (42, **térmico/ambiente**: `movie thermal diffTemp`, `environmentalTemp`) y `CAMERA_MAIN_FC` (9, **datos de ojo**: `Eye data is invalid, but lc flag is true`). Familias mayores: `ADF` (1231), `IMAGING_CAP` (697), `SDF` (477), `CAM_IMAGER` (371), `IDT` (298), `IDT_OPD` (274), `CDIAG` (270), `VDF` (243), `CAMERA_SA` (231), `TRK` (216), `VEF` (149), `MOUNT_DEBUG/ERROR` (132/80), `SFRS/SFRA` (117/100), `VPH_API` (106), `ACCY` (106), `DBGCMD` (102), `STK` (76), `FACE` (70), `VIDENCSTAT` (70), `CLK_CTRL` (66), `GOLFSHOT` (65), `WSX` (59), `CTRLCORE` (55), `CAM_DMM` (54), `SAD` (45), `CAM_FUNC_MGR` (43), `APL` (42), `PNL` (41). **Diferencial**: 83 prefijos exclusivos de A6000 (los `CAMERA_MAIN_*`, `CAMERA_IS`, `CAMERA_ADJ`, `CAMERA_DETECT_FC`, `CAMERA_DEVICE`, `ACCY`, `ADC_DEBUG`, `AVOUT`, `ADR`, `AVR`, `BKID`, `CAMCORE`…) y 12 exclusivos de A7S (`APL_PARM`, `APL_ESR`, `APL_ADDR`, `APL_REF`, `APL_SIZE`, `APL_TAR`, `APL_UPDT`, `NLAP`, `PIN`, `PINCOUNT`, `TCUB`, `CDCTCUBENCTABLE`).

**NO VERIFICADO:** qué significan las siglas `ADF`, `IDT`, `VDF`, `VEF`, `SFRS`/`SFRA`, `WSX`, `GOLFSHOT`, `ACCY`, `AUGI`, `SAD`, `APL`; correspondencia prefijo↔tarea real del OSAL; renombrados posibles entre fw3.20 y fw3.21.

[Conclusiones](../analysis/s79_modules/module_map.md) · [tabla JSON](../analysis/s79_modules/module_map.json).

## S80 — ZIT: corrección de defectos del sensor (DDC) (21-10-2026)

**VERIFICADO (9 tests, `tests/test_s80_zit.py`):** el imager (`Camera::Imager`) lleva un motor de **corrección de defectos** con 118 trazas `ZIT`/`Zit` (75 en la A7S fw3.20). Clases RTTI: `N6Camera6Imager12ZitMemBufferE` (`0x43cf768e`), `N6Camera6Imager18ZitZphDefectBufferE` (`0x43cf81a1`), `N6Camera6Imager21ZitZphLineTableBufferE` (`0x43cf96ef`). Trabaja sobre **cuatro áreas de memoria** (`ZIT:: shadowAddr adj:%x usr:%x slow:%x mend:%x` `0x43cf7706`): **adj** (ajuste de fábrica), **usr** (usuario), **slow** (long exposure) y **mend** (parche), con los defectos organizados en **bancos por "read mode"** (`<read:%d bank:%d>` `0x43cf7771`). **Puente con el motor de imagen**: `Camera::Imager::ZitSaFunctionDriver` con `ZIT_SaOpen`/`ZIT_SaStart`/`ZIT_SaClose` (`0x43cfa2a7`–`0x43cfa2ee`; firma `ZIT_SaClose()` `0x43cfa312`), handles DMM limitados (`dmmHandleList is Full` `0x43cf9cd3`) y **MMU propio** (`CloseFreeZitMMUParam` `0x43cfa210`). **Siete operaciones se ejecutan en el SA**: `Merge` (`0x43a13be8`), `ConvThin` (`0x43a194c4`), `ConvUnity` (`0x43a19908`), `ConvZ1C` (`0x43a19c58`), `Det` (`0x43a1a364`, con `DetectInfo [ch1..ch4]` y `RAWInfo [AVE/MIN/MAX]`), `Hist` (`0x43a1a834`) y `ZphSA` (`0x43a1aafc`), más `ZitSA_ConvDdc` (`0x43a139c8`). Registro de defectos: `SetZitLog_DetectSequencePre/MassiveDefectDetectNum/DefectLvAndPos/DefectPosNum` (`0x43cf7e5f`–`0x43cf7f2e`). Búferes "Zph": `ZitZphDefectBuffer::reCalcOffset/copyBuff/convertBackupSaveformat`, `ZphAdj_Merge_Req`, `ZphAdj_Det_Req`, `ZphDetSA`. Variantes: **long exposure** (`buildLongExpCapData_DDC`, merge `adj`+`usr`, `convDdcByCpu`) y **vídeo** (`MovieAdj_SpreadDefectsOverSharedPixels`). Drivers de nivel superior: `ZitDdcDriver` (`0x4386bbee`) y `ZitZ1cDriver` (`0x437b93c0`), ambos en `CAMERA_MAIN_IM`.

**NO VERIFICADO:** qué significan las siglas ZIT y Zph; qué es un "read mode"/banco y cuántos hay; formato binario y origen de fábrica de los datos de defecto; enlace exacto con ZPD (S75); algoritmos del SA que ejecutan las conversiones.

[Conclusiones](../analysis/s80_zit/zit_defect_correction.md).

## S71 — subsistema de detección de caras y objetos (FC/FRC) (21-10-2026)

**VERIFICADO (20 tests, `tests/test_s71_frc.py`):** el subsistema `Camera::FC` del `av-cam.bin` tiene **99 ficheros `FC/…`** embebidos, **idénticos en A6000 fw3.21 y A7S fw3.20** (0 diferencias), repartidos en `Alg` (`fc_alg_frc`, `smoothing`, `remove_overlap`, `target_selecting`, `tracking`, `tracking_obj(_color)`, `tracking_face_object`, `pre_fdt`, `attribute`, `extract_color`, `blink`, `exif_face_data`, `exif_makernote`, `normalize`, `object`, `pmv`, `select_key`, `track_init`, `touch`), `Seq` (`mon_face`, `mon_object`, `mon_frame`, `attribute`, `oneshot`, `pmv`, `re_init`, `touch`, `track_init`, `prc`, `rec_face`, `vae` + `fc_data_*`), `Drv` (`frc`, `bt`, `edt`, `fat`, `fdt`, `vat`, `detsa`, `iro`, `iro2g`, `pmv`, `stk`, `prc`, `vae`), `SaFuncDrv` (`fc_sa_frc2_drv`, `fc_sa_frc2_mmu`, `recog_sa_drv`), `Feature` (17), `Api` (9), `Lib` (7) y `Misc` (3). **Puente con el acelerador Scalar (SA)**: recursos en Core2/Core3 (`AcquireRes … Core2 user[0]` `0x43cf094a`, `Core3 user[1]` `0x43cf0981`, `RES_SA_FOR_FRC2` `0x43cf09b8`), búferes propios `s_sa_temp_icon_mem`/`s_sa_param_mem` (`0x43cf0bd8`/`0x43cf0bc3`), MMU (`MakeMmu …` `0x43cf0c11`), ciclo de cálculo (`ddl_saCalcCancel` `0x43cf0afb`, `int_fact=NOT_FINISH` `0x43cf0ad4`, `alloc size:%d, expected:%d` `0x43cf0b39`) e iconos de cara (`FRC: Init FaceIcon` `0x43cf0d6c`, `FaceIconInfo::Alloc() handle:%d` `0x43cf0db8`). Módulo `[FACE]` (70 trazas) con estados INIT/BASE/MON/IMME/ATTR/STOP. Módulo `[TRK]` (216 trazas) con **seis detectores**: DETSA (Core2), EDTSA (Core3, entrega cara/ángulo/nodo/rangos HSV), IRO2G (Core2), PMV (Core3, vectores de movimiento), STK (Core2, saliencia y similitud toque/color) y BT (fg/bg areas + mapas bayesianos). Algoritmo FRC: reordena IDs por `record_rank` y gobierna la creación de iconos por prioridad; además **parpadeo** (`fc_alg_blink.cpp`), Pre-FDT (African/Scene/Bunri/Hist/contraluz), alternancia cara↔objeto en el tracking, panorámica/retoque y **MakerNote de caras**.

**Corrección de la revisión (21-10-2026):** el borrador del subagente tenía direcciones en espacio de ficheros (`0x8060839`), nombres de búfer inexistentes (`s_temp_icon_mem`/`s_param_mem`), "SA (Secure Area)" (es el **acelerador Scalar**: SFRA = *ScalarA-ScalarInfra*, `sa_dfdet.bin` = detección de caras en el Scalar), semántica inventada para BT/FAT/IRO/PMV/STK y un **diferencial A7S falso** (los ficheros `FC/` son los mismos 99 en ambas cámaras).

**NO VERIFICADO:** siglas FDT/VAT/PRC/VAE/VOT; formato binario de los mensajes al Scalar; reparto Core2/Core3; algoritmos del SA para FRC; relación con `analysis/s63_af/` (otro agente) más allá de `fc_feature_touch_for_scanaf.cpp` y `fc_alg_pre_fdt.cpp`.

[Conclusiones](../analysis/s71_frc/frc_subsystem.md) · [tabla JSON](../analysis/s71_frc/frc_subsystem.json).

## S81 — ADF: el framework de arranque, MSGQ, MMGR y comandos DBGCMD (21-10-2026)

**VERIFICADO (9 tests, `tests/test_s81_adf.py`):** `ADF` es el **módulo más grande del firmware por número de trazas**: **1220** cadenas `[ADF]` en A6000 fw3.21 (1269 en A7S fw3.20) en `0x43c26366`–`0x43c37a62`, con sub-niveles raíz 934, `[DBGCMD]` 102, `[ERR]` 70, `[SYSND]` 27, `[ADJ]` 24, `[SAN]` 23, `[OUT]` 15, `[ADF]` 11, `[SYS]` 3, `[INIT]` 2, `[DEBUG]` 2, `[GS]` 2, `[AFNR]` 2, `[FACE]` 2, `[CH_SRC]` 1. **Arranque**: `[ADF]BootInit` `0x43c26366` → `InitWaitVsync SelectCompo` `0x43c26375` (espera de vsync y selección de componentes) → `[ADF][INIT]AVIO INIT COMP` `0x43c263f6` y `[ADF][INIT]AUDIOIP INIT COMP` `0x43c26411` → `[ADF]BootExit` `0x43c263c9`, con **reenvío de mensajes** (`INIT Resend MsgqNum` `0x43c263d8`, `Resend header cateId/msgId/msgLength/version` `0x43c2642f`, `Resend to Adf src/reply` `0x43c2648f`). **Configuración del IP de audio** (enlace con S69): `AUDIO_IP_CONFIG_TYPE_VGS` `0x43c264fa`, `_PR` `0x43c26518`, `_MF` `0x43c26535`, `_BANDI_BASEDON_CONS` `0x43c26552`, `_CONS` `0x43c2657f`, `_BANDI` `0x43c2659e`. **Gestor de memoria (MMGR)**: `MMGR COMM INFO` `0x43c265ce` con `indexNo, unitType, handle, allocNum, openNum` `0x43c265e3` y `AdfMemMgrCtrl::SetMemMgrCommResult` `0x43c26652`. **Colas de mensajes (MSGQ)**: `MSGQ Set:srcId %08X ,msgId %08X` `0x43c26788`, `MSGQ Get:msgId %08X` `0x43c267d5`, `SendImmediateComp msgId/replyId` `0x43c268a8`, `ClearAllComp` `0x43c2691c`, y el grupo `MSGQ_GID_HOTSHOE_INFRA1` `0x43c266e6` (colas del flash hotshoe). **102 comandos de depuración** (`[ADF][DBGCMD]`, `0x43c2a443`–`0x43c2b315`): `System` (ClearExecTime/ClearMSGQ/CountMSGQ/SetMSG/GetMSGQ/BootExit/GetMemMgrComm), **medida del tiempo de ejecución de la CPU2 a 60 Hz y 48 Hz** (`CPU2 ExecTime 60Hz max m/s` `0x43c2a465`, `48Hz` `0x43c2a4ca`), `Input`/`InputPro` (SetInput, SetRecLevel, SetAgcLink, SetManualGainLink, SetChSource…), `Output`/`OutputPro` (SetOutput, DetectJack, SetHdmiFormat, SetAntiClipping, SetHpMonitor, SetHpOut, SetAdjI2sMute), `Proc` (**fases lineales del arranque**: SetLinearPhase, SetDec0/1, SetAip0/1, GetSa0/1, GetPin0/1, SetMb, SetSa; y ruta de audio/zoom: SetPath, SetMixRatio, SetFader, SetZoomNr, ZOOM[0..2]), `SystemSound` (SetTable/SetPath/Request/SetVol/SetNotify/RequestPin) y **`SoundAnalyzer` con el disparo de golf** (`StartGolfShot` `0x43c2b143`, `StopGolfShot`, `AnalyzeGolfShot`, `SetSoundAnalyze`).

**NO VERIFICADO:** significado de `ADF`/`MMGR`/`Compo`/`AIP`/`MB`/`SA` en este contexto (salvo `AIP` = Audio IP); formato del mensaje (cabecera `cateId/msgId/msgLength/version` + `srcId`/`replyId`) y tabla de destinos; lista completa de grupos `MSGQ_GID_*`; qué hacen `ADF][ADJ]`, `[SAN]`, `[SYSND]`, `[GS]`, `[AFNR]`, `[FACE]`, `[CH_SRC]`; cómo se invocan los comandos DBGCMD.

[Conclusiones](../analysis/s81_adf/adf_framework.md).

## S83 — los módulos "menores" del firmware, decodificados (21-10-2026)

**VERIFICADO (10 tests, `tests/test_s83_modules.py`):** decodificación por evidencia (nombres de función y campos de estado) de los módulos de tamaño medio que S79 dejó sin descripción: **`[ACCY]`** (106) = **accesorios por UART** (`NotifyAttachedUart` `0x43c24cca`, `NotifyDetached` `0x43c24d1e`, `NotifyUartCommand` `0x43c24d41`, `[HW]:AD=%d, ID=%d` `0x43c24cac`; mismo hardware que el grupo `MSGQ_GID_HOTSHOE_INFRA1` de ADF, S81); **`[CAM_FUNC_MGR]`** (43) = **gestor de funciones de captura** (`SyncProcMargin[usec] HS0..HS3@CPU2/CPU0(IDT)/CPU3(RCH)` `0x43ca12f6`, `SetCapMode:Invalid CapMode` `0x43caf036`, `receive[..] before comp[..] (QUEUEING)` `0x43caf077`); **`[ENCOUCSTAT]`** (49) = **errores del codificador AVC** (`AVC_ENC_VIDEO_ERR_STATE/MEMORY/PARAM/INDEX` `0x43c50693`–`0x43c50730`); **`[VIDENCSTAT]`** (70) = **estado del encoder de vídeo** (`Pts = 0x%08x EndFlug` `0x43cd680b`, `augi,paddingAreaLength` `0x43cd6861`, `Use 2nd Latest Index` `0x43cd68af`); **`[ENCSEQCTRL]`** (46) = **secuenciador de encoding** con tabla de frame rate/sampling rate (`[O/U Crank] Table[%d] fR sR` `0x43c4bd2b`) y máquina de estados (`[state]0x%x -> 0x%x` `0x43c4bda2`); **`[SAD]`** (45) = **programas del motor de imagen** con cabecera (`CdcSaPrg/NmlSaPrg/RsdSaPrg Hdr Err` `0x43ce55bc`–`0x43ce55fa`); **`[PNL]`** (41) = **panel/display** con configuración por callbacks y backup (`Backup_read() b_id` `0x43c76155`, `cmd_set_conf_cb_NULL` `0x43c761bd`; enlaza con `ADJ_CMD`, S73); **`[AUGI]`** (75 token / 26 cadenas con prefijo) = **formato de bloque con cabecera** (`length`, `Reserved2`, `end_flag`, `PS_flag`, `EP_flag` `0x43cd9968`–`0x43cd99f4`); **`[WSX]`** (59) = servicio de **búsqueda en fichero "BSFS"** (`BSFS INIT: TG: %x` `0x43ce41bd`, `BSFS SEARCH LOOP ERROR` `0x43ce41fe`).

**NO VERIFICADO:** siglas BSFS/AUGI/SAD/WSX/ENCOUCSTAT; qué son los programas `Cdc/Nml/Rsd` del SA; los 4 sub-valores de `CapMode`; la tabla "O/U Crank" completa; formato exacto de la cabecera AUGI; módulos aún sin decodificar (`IDT`, `VDF`, `VEF`, `CLK_CTRL`, `SFRS`/`SFRA`, `GOLFSHOT`, `SAN`, `GS`, `CH_SRC`, `AFNR`).

[Conclusiones](../analysis/s83_modules/minor_modules.md).

## S84 — el API del motor de imagen (SA): catálogo de `sa_func_*` (21-10-2026)

**VERIFICADO (11 tests, `tests/test_s84_sa_api.py`):** la superficie del driver `Camera::SaFuncDrv` tiene una forma uniforme — `Camera::SaFuncDrv::SA_FUNCDRV_ERR Camera::SaFuncDrv::sa_func_<X>_<op>(__uint8_t, __uint16_t, Camera::SaFuncDrv::<X>_START_PARAM*)` = (unidad, código de función, parámetros) —, con **19 familias**: `BFNR` (init con `SaFuncDrvCmn*` + `BFNR_PARAM*`, acquire/start/release), `BOKS` (init/init_CONTROL/GetAddr/start/release/exit), `CONTP`, `DECOMP`, `DUALREC_BAYER`/`DUALREC_CLEARVID`, `GOLFSHOT` (con **dos sobrecargas de `start`**: `SSP_START_PARAM*`+`SSP_START_MBX*` y `BGEST_START_PARAM*`+`SA_MBX_0123*`), `KKNR`, `LFNR`, `NFLASH` (flash: `flash_add`/`amb_add`/`int_add`/`rc_line_ofs`), `PreDCV`, `SFTFCS` (`preinit(__uint16_t)` + mailbox `cha_mbx0/1/2`), `SPICA` (con fases **PRE/MAPPING/POST**), `STAR`, `TBOX`, `YKNR`, `BDEX`, y en la A7S además `MOTIONSHOT` y `NLAP`. Códigos de error: `SA_FUNCDRV_E_OSAL`, `SA_FUNCDRV_E_RSLTCODE`, `SA_FUNCDRV_E_ERRCODE`. Quien las invoca en la captura es el módulo `IMAGING_CAP` (697 trazas) y el propio driver con prefijo `[CAMERA_SA]` (231 trazas). 92 cadenas contienen `sa_func_` en la A6000 (109 en la A7S).

**Diferencial (VERIFICADO):** la fw3.21 de A6000 **elimina por completo** `NLAP` (0 ocurrencias; la A7S tiene 13, con `[YC][NLAP]isNLAP:true, iso_cont=0x%04x` `0x43cbbf71`) y `sa_func_MOTIONSHOT_*` (0 ocurrencias; la A7S los llama desde `IMAGING_CAP` `0x43cc403e`/`0x43cc4063` y tiene la firma `0x43ce3448`). Lo que permanece en la A6000 es `MOTIONSHOTVIDEO`, del módulo **SFRS** (otra cosa: vídeo de movimiento).

**NO VERIFICADO:** significado de las siglas de cada familia; estructura de los `<X>_START_PARAM`; qué algoritmo del SA corresponde a cada familia; detalle de las fases PRE/MAPPING/POST de SPICA; por qué la A6000 conserva SFRS/MOTIONSHOTVIDEO.

[Conclusiones](../analysis/s84_sa_api/sa_api_catalogue.md).

## S72 — wireless y transferencia remota (WLAN / PlayMem / "Camera on Demand") (21-10-2026)

**VERIFICADO (16 tests, `tests/test_s72_wlan.py`):** pila wireless del userland fw3.21 (`firmware/extracted/fw321/.../nflasha15_unpacked_unpacked/lib`, 157 `.so`): **`libWlanAdjust.so`** (60 492 B) = ajuste del radio (`WlanAdjust_Init/Res/Sus`, 11 `wpa_ctrl_*`, `wlanLoadFirmware`, `wlanSetSsid/TxCh/TxMode/TxRate/TxPower` + `wlanGet*`, `wlanStartTx/StopTx`, `m_fixed_psk`, `SetMacAddress`); **`libWlanControlCommon.so`** (23 840 B) = control del puerto (`initializePort/finalizePort`, `setPortToStartWlan/StopWlan`, `installWlanDrivers`, 25 × "BMI" = bus del chip, GPIO de energía); **`libWlanResource.so`** (63 656 B) = recurso/hilo (`WlanResourceMainThread`, `GetMacAddress(WlanResource::ST_MSG_SYNC_REQ*)`, DFS, colas `OSAL_MSGQ_GID_WLAN_RSRC_DBG`/`_TEST`); **`libGOConnectionManager.so`** (106 016 B) = **P2P con rol Group Owner**: máquina de estados **Idle→Init→Auth→Wait→ChgKey→AuthConn→Finalizing→Stop** (`startGO/stopGO`, `authPush`, `changeKey`), `GOConnectionManagerCmdMgr` (`ProcIdleToAuthReq`, `ProcWaitAuthReqToChgKey`, `ProcIssueFatalError`…) y `NetServiceWrapper` con los comandos **WPS** (`StartWpsCmd`, `CancelWpsCmd`, `InputPin`, `AuthPush`, `ChangeKey`) y eventos (`SendReqWpsEvtPush/ShowPin/InputPin`, `SendWpsCompleteEvt`); **`libInfraDlnaControl.so`** (525 892 B) = **DLNA/UPnP** (`dc_statetbl`, `dc_evtTbl`, 9 *callers* `m_lid_*`, `sendMsgToControlpoint/MediaServer/ContentHandler`); **`CameraOnDemandSaver.so`** (20 084 B) = guardado "on demand" en `/dev/ms1`, **`/mnt/dcim/100msdcf`** y **`/setting/psd.bin`** (hilo `cam_ondemand_saver_thread`, auto-numeración `%04d_%02X`); **`libHapiLib.so`** (89 628 B) = API de la app. **`netconf/` es un directorio** con 4 configuraciones: `bss.conf` (`manufacturer=Sony Corporation`, `model_name=SonyImagingDevice`, `device_name=WCM-Sample-Device`, `device_type=1-0050F204-1`, `config_methods=physical_display virtual_push_button`, `uuid=12345678-9abc-def0-1234-56789abcdef0`, `ctrl_interface=/tmp_network/run/wpa_supplicant`), `p2p.conf` (`p2p_go_intent=10`, `max_num_sta=1`, `p2p_ssid_postfix=-WCM`, `device_type=4-0050F204-1`, `config_methods=virtual_push_button physical_display keypad`), `dhcpd.conf` (subred `10.0.0.0/16`, rango `10.0.1.1-254`) y `pump.conf` (cliente DHCP en `ath0`/`ath1`).

**Hallazgo nuevo (VERIFICADO):** el `psd.bin` que escribe `CameraOnDemandSaver.so` es **el mismo fichero** que S75 identificó como origen "from body" de los datos **ZPD** de calibración del sensor → el "Camera on Demand" escribe en el almacén de ajustes de la cámara.

**Correcciones de la revisión (21-10-2026):** (a) `getMacAddress` no existe → el símbolo real es `GetMacAddress(WlanResource::ST_MSG_SYNC_REQ*)`; (b) las colas son `OSAL_MSGQ_GID_WLAN_RSRC_DBG` y `…_TEST` (no `…_API`); (c) **`libgps_rsrc.so` SÍ está en el firmware de la A6000** (109 384 B), el borrador afirmaba lo contrario; (d) la cadena GO está **más desarrollada en la A6000** (106 016 B vs 64 580 B; mismo esquema de 348 símbolos, 0 diferencias), no en la A7S; (e) `netconf` no es idéntico: 3 de 4 ficheros coinciden por SHA-256 y solo difiere `dhcpd.conf`; (f) la biblioteca HAPI se llama `libHapiLib.so`, no `libInfraHapiLib.so`.

**NO VERIFICADO:** cómo se enlazan `libGOConnectionManager` y `CameraOnDemandSaver`; por qué la fw3.21 duplica el tamaño de las bibliotecas WLAN; contenido y destino del `psd.bin` escrito; los 10 símbolos de DLNA exclusivos de la A6000.

[Conclusiones](../analysis/s72_wlan/wlan_playmem.md) · [tabla JSON](../analysis/s72_wlan/wlan_playmem.json).

## S85 — `CLK_CTRL` (control de reloj) y `VPH_API` (API del vídeo del visor) (21-10-2026)

**VERIFICADO (11 tests, `tests/test_s85_clk_vph.py`):** dos módulos **nuevos en la fw3.21 de A6000** (0 trazas en la A7S fw3.20). **`[CLK_CTRL]`** (66 trazas, `0x43c3a1df`–`0x43c3b09c`): control de reloj y de la señal de sincronización del visor, con 12 llamadas `ddl_clkctrl_*` (`open/close_clk`, `open/close_dly`, `set_sync_signal`, `set_sync_initial_signal`, `lock/unlock_sync_signal`, `set_sysv_delay[_changing]`, `set_sysv_initial_delay`, `get_clk_chg_enable`), máquina de estados `STATE_INIT1(InitDelay)` → `STATE_NORMAL(InitSignal)` → `STATE_LOCK` (+ `STATE_CHANGE_CLK`, `STATE_CHANGE_CLK_LOCKING`), **gestión por subsistema** (`open/close subsytem = 0x%04x`, `Busy!! 0x%04x already opened`, `lock_sync_signal subsystem = %x`), cambios de reloj y retardo (`CHANGE_CLK dly … clk … change_vfc=0x%x`, `ClkChgExec`, `DelayChgExec`) con **dos VFC** (`m_vfc.main=0x%0x, m_vfc.sub=0x%0x` `0x43c3ac2f`), y arquitectura **maestro/esclavo** (`Receive Message from Master` `0x43c3abd0`, `Send Message to Slave` `0x43c3ac86`, `Send HTP at` `0x43c3aae7`) que además se coordina con VPH (`vph stat:%d,mode:%d` `0x43c3aa69`). **`[VPH_API]`** (106 trazas, `0x43ce32e7`–`0x43ce3dfc`): vocabulario de **comandos** del procesado de vídeo del visor — ruta (`<mode>`, `<line_out>`, `<panel_out>`, `<dualpanel_out>`, `<update_yuv>`, `<mix_mode>`, `<force_out>`), OSD (`<osd_on>`, `<osdarea_on>`, `<osdarea>`, `<update_osd>`), **marco de cara** (`<faceframe_on>`, `<update_faceframe>`, `<faceframe_color>`), timecode, mute (`<yuv_mute>`, `<yuv_mute_param>`, `<yuv_mute_immediately>`, `<chroma_mute>`, `<shutter_mute_param>`), línea (`<line_closedcaption>`, `<line_macrovision>`, `<line_vbidwss>`, `<line_sync_setup>`, `<line_fchr>`, `<line_hdmi_still_range>`), panel (`<panel_brightness>`, `<panel_cabc>`, `<panel_depth>`, `<panel_reverse>`, `<panel_ysetup>`, `<set_panel_osd_luminance>`), ayudas (`<pictureeffect>`, `<ylevel_caution>`, `<zebra>`, `<peaking>`, `<gridline>`, `<histogram>`, `<testpattern>`, `<diceic_arb>`) y corrección (`<parallax_adjust>`, `<set_extblackframe>`, `<set_color_temperature>`) — **cada uno con su gemelo `_sub`** (los dos canales) — más 11 salidas de estado (`>hw_status<`, `>mode_status<`, `>histogram_result<`, `>yuv_delay<`, `>osdmix_size_panel/line<`, `>black_frame<`, `>panel_brightness_status<`, `>shutter_mute<`).

**Enlace con S71 (VERIFICADO):** el visor dibuja el marco de la cara detectada (`<faceframe_on>`, `<update_faceframe>`, `<faceframe_color>`).

**NO VERIFICADO:** significado de `laxo`, `diceic_arb`, `ylevel_caution`, `vbidwss`, `fchr`, `extblackframe`, `eomainsub`, `htp`; correspondencia exacta de los canales línea/panel; quién es el "master"; si VPH_API es un contrato con hardware externo o con el módulo VDF (S79); por qué la fw3.21 introduce ambos módulos.

[Conclusiones](../analysis/s85_clk_vph/clk_ctrl_vph_api.md).

## S86 — el subsistema del visor: `VDF` y `VEF` (21-10-2026)

**VERIFICADO (14 tests, `tests/test_s86_vdf_vef.py`):** **`[VDF]`** (243 trazas, `0x43c813fc`+) es un framework C++ completo del display (~200 clases RTTI `N3VDF*`): núcleo (`VDF::SubsystemMain::Main()` `0x43c8221b`, `SubsystemFactory::ExecCmd` `0x43c83b7f`), framework de mensajes (`MsgAccessor`/`MsgIterator`/`WaitQueue`), **cmds del sistema** (`PinConnect`/`PinSend`/`PinGet`/`PinDisconnect`/`Trigger`/`Receive`/`Sysv`/`Debug`/`CipaModeOut`), **cmds de display** (`SetPanelOut` `0x43c8714a`, `SetPanelBrightness` `0x43c86eea`, `SetPanelColorTemperature` `0x43c86886`, `SetParallax` `0x43c86e1c`, `SetDetectExtEvf` `0x43c862b9`, `SetOsdAlpha` `0x43c866ef`, `GetPanelBrightness` `0x43c86209`), **cmds de entrada** (`UpdateYuv` `0x43c888ef`, `SetOsdArea`, `SetYuvLayout`, `SetYuvMute`, `SetShutterMute`, `SetHdTrimming`, `UpdateFaceFramePin` `0x43c887e9`), **cmds de servicio** (`SetZebra` `0x43c8ad68`, `SetPeaking`, `SetHistogram`, `SetFaceFrame`, `SetEvfParallax`, `SetLiveDemo`, `SetPanelZoom`, `SetTimeCode`), **rutas de imagen** (`SetPath` `0x43c89fca`, `ThroughTransfer`, `ResizeTransfer`, `4K…`), memoria (`YuvIndexDoubleBuffer`, `YuvIndexQfhdMemoryManager`, `VfxRgba8888ToYuv422`) y dispositivos (`EoLineDevice`/`EoPanelDevice`/`LRMixDevice`, `MirrorSubsystemSynchronizer` `0x43c84c0c`). **Puente con VPH** (S85): `VphSetZebraCall` `0x43c87294`, `VphSetPeakingCall` `0x43c872f9`, `VphSetPanelDepthCall` `0x43c870e0`, `VphUpdateYuvFunction` `0x43c85017`, `DrvCallVphLatestCmdHolder` `0x43c8305e`; trazas `[VDF] CallVphUpdateYuv size_x/size_y` `0x43c82fd7` y `vph_set_yuv_mute_immediately ON/OFF sel=%d` `0x43c83004`. **Enlace con ADF** (S81): `VDF::VdfToAdfYcDataSender` `0x43c86165` (envía los datos YC al ADF) y persistencia en el **bus SSBI** del display (`ssbi_read/write` `0x43c814f0`/`0x43c81547`, `Backup_read(BKID_UPM_BOOT_CIPA_FLAG)` `0x43c82329`). **Enlace con CLK_CTRL** (S85): `CheckUpdateYuvTiming(VDF_PRM_SUBSYSTEM_CLKCTRL_INFO)` `0x43c847d1`, `HtpVfcMainPerformanceCounter` `0x43c855f1`. **Enlace con las caras** (S71): `VdfInputCmdUpdateFaceFramePin` `0x43c887e9`, `VdfFaceFrameUtility::UpdateFaceFrameNormal` `0x43c8c014`, `VdfSrvcCmdSetFaceFrameCommonDesign` `0x43c8a998`. **`[VEF]`** (149 trazas) = el visor electrónico: **espejo** con el panel (`reply_osal_id/mirror_osal_id` `0x43c8c36e`), modos **3D/2D/INIT** (`0x43c8d5cf`–`0x43c8d62f`), **multicast** de infraestructura para pausarlo (`Receive InfraMulticast PauseNotify` `0x43c8d10d`), **down-conversion** de la señal a **PAL/NTSC** (`DOWNCON: PAL 50i50p` `0x43c8d394`, `NTSC 30p24p` `0x43c8d403`), cancelación de efectos **sincronizada con el VFC** (`VFC Sync!!!` `0x43c8dc56`) y toma del bloque de trabajo YC del datarec (`free DMM_UNITTYPE_DATEREC_WORK_YC` `0x43c8da6b`).

**NO VERIFICADO:** qué es el modo "3D" del visor; formato de los mensajes VDF (`VDF_MSG_INFO`, `CATE_ID`, `MSG_ID`, `TRIGGER_TYPE`); implementación del espejo EVF↔panel; efectos de vídeo más allá de la cancelación; si este VDF es el mismo que el citado en S16–S18.

[Conclusiones](../analysis/s86_vdf_vef/vdf_vef_viewfinder.md).

## S77 — Creative Style y balance de blancos (21-10-2026)

**VERIFICADO (10 tests, `tests/test_s77_pp.py`):** en el `av-cam.bin` hay **dos tablas de nombres de estilo creativo**: `0x43ca6702`–`0x43ca676d` (**13** entradas: Vivid, Neutral, Portrait, Landscape, Clear, Deep, Light, Sunset, Nightview, Autumnleaves, **Real**, Sepia, Standard) y `0x43ca678b`–`0x43ca67f0` (**12**, las mismas sin `Real`); la **A7S fw3.20 tiene las mismas dos tablas** (`0x43cb540e`…, `0x43cc5ab8`…) → el juego de estilos no cambia entre fw3.20 y fw3.21. **El bloque `wb_*`** (`wb_b_data=%02X` `0x43c76c26`, `wb_data_tmp=%02X` `0x43c76c36`, `wb_r_data=%02X` `0x43c76c48`, `wb_g_data=%02X` `0x43c76c6b`, `wb_w_data=%02X` `0x43c76dca`/`0x43c76e21`, `wb_mask=%02X` `0x43c76dbb`/`0x43c76e13`) está **dentro del bloque de ajuste de panel `ADJ_CMD`** (S73) → es la **calibración de WB del display**, no el WB fotográfico. **Resultado negativo verificado:** en `av-cam.bin` hay **0 apariciones** de `CreativeStyle`, `PictureProfile`, `Highlight`, `Saturation`, `Sharpness`, `ColorTone` y `wb_shift` → el control del estilo/WB fotográfico vive solo en el userland. **`wrapperCreativeStyle.so`** (8 420 B): `WrapperCreativeStyle::getCreativeStyle/setCreativeStyle/convertProcessValueIdToValue/convertValueToProcessValueId/isInhOn`, `CmnViewProcessDataMgr::getInstance`, `stella::8BitArray<unsigned int>`; ruta de compilación embebida `…/build/141H/141H.DSLR.DM_UUD3.reco.LATEST.diadem.set/Guiengine_131H/` (modelo interno **141H** = ILCE-6000, motor GUI **Diadem**). **`wrapperWhiteBalance.so`** (15 556 B): `WrapperWhiteBalance::getWhiteBalance`, `setWhiteBalance(…, int, int, int)` (tres enteros: WB + compensación), `resetAdjustmentValue`, `isInhOn`, persistencia vía `WrapperSettingUtil::readBackup/writeBackup` → `BackupManager::Bkup_Read_Setting_Attr`, y aplicación vía `ViewBase::requestModelExecute`/`getModelInfo` con `ParamBase`/`PrmNumber`/`ParamList`.

**Correcciones de la revisión (21-10-2026):** la "tabla de Picture Profile" del borrador (offset `0xaa8d50`) es **código Thumb**, no datos; los nombres de parámetro `Highlight`/`Saturation`/`Sharpness` y `CreativeStyle`/`PictureProfile` **no existen** en el firmware; y los presets de WB (`Auto`, `Daylight`…) **no aparecen** en ninguna cadena del binario (el test lo fija como negativo).

**NO VERIFICADO:** qué tabla de estilos usa el código y qué significa la entrada `Real`; los valores por estilo (no están en el firmware ni en estas .so); los enumerados `WRAPPER_CREATIVE_STYLE`/`WRAPPER_WHITE_BALANCE`; el mapeo PP1..PP6/Off; los presets fotográficos de WB; los rangos de la compensación.

[Conclusiones](../analysis/s77_pp/picture_profile_creative_style.md) · [tabla JSON](../analysis/s77_pp/picture_profile_creative_style.json).

## S88 — GOLFSHOT (disparo de golf por sonido) y MOTIONSHOT (21-10-2026)

**VERIFICADO (9 tests, `tests/test_s88_shotmodes.py`):** el modo de golf shot dispara sincronizado con el **sonido del golpe**: 72 cadenas contienen `GOLFSHOT` en la A6000 (también 72 en la A7S), pero en la **A6000 la etiqueta va anidada** dentro de `[IMAGING_RSRC]:`, `[IMAGING_CAP]:` y `[CAMERA_MAIN_SYNC]:` (`[IMAGING_RSRC]: [GOLFSHOT]SA_LPF Exec[%02d]…` `0x43ca492f`), mientras que en la **A7S es prefijo principal** (65 cadenas que empiezan por `[GOLFSHOT]`, 0 en A6000) → la fw3.21 **reorganizó la traza**, no la función. El **módulo `[SAN]`** (5 cadenas) da los comandos: `[SAN]StartGolfShot` `0x43c2c72e`, `[SAN]StopGolfShot` `0x43c2c77a`, `[SAN]AnalyzeGolfShot` `0x43c2c792`, `[SAN]SetSoundAnalyze` `0x43c2c7dd` y `[SAN] CLAP DETECT SCORE = %d (%d[deg]) DIFF = %d` `0x43ce2f27` → **detecta el golpe por el sonido, con puntuación, ángulo (grados) y diferencia**; los mismos están como comandos de depuración del ADF (S81: `SoundAnalyzer StartGolfShot` `0x43c2b143`…). El motor de imagen ejecuta **tres fases SA**: `SA_LPF` `0x43ca492f`, `SA_BGEST` `0x43ca4984` (la estimación de fondo **decodifica un JPEG**: `Seq._BgestPre: JPEG_DEC OPEN OFF` `0x43cb1ba1`) y `SA_SSP` `0x43ca49d5`; el **"ALOCK"** enumera sus búferes (`BG_INPUT_IMAGE` `0x43cb1915`, `BG_IMAGE` `0x43cb1952`, `BG_MASK_IMAGE` `0x43cb1988`, `INPUT_IMAGE` `0x43cb19c3`, `INPUT_LPF_IMAGE` `0x43cb1a00`, `ALPHA_IMAGE` `0x43cb1a3d`, `KEY_ALPHA_LPF_IMAGE` `0x43cb1a76`, `SSP_IMAGE` `0x43cb1abb`, `PRE_KEY_SSP_IMAGE` `0x43cb1af6`); y el instante del disparo se calcula en **unidades de VFC** (`vfc2indx: Shot Timing Transform Error` `0x43ca4a8a`, `shot_time_vfc error!` `0x43cb18a9`, `vfc %x vfcSub %x` `0x43c36d0a` → conecta con los dos VFC de `CLK_CTRL`, S85). API del SA: `sa_func_GOLFSHOT_start` con dos sobrecargas (`SSP_START_PARAM*`+`SSP_START_MBX*` `0x43cedc91`; `BGEST_START_PARAM*`+`SA_MBX_0123*` `0x43cedff6`) y `sa_func_GOLFSHOT_release` `0x43cedf67`. **MOTIONSHOT: eliminado por completo en la A6000 fw3.21** (0 apariciones de `sa_func_MOTIONSHOT`; la A7S tiene 5) — lo que queda es `MOTIONSHOTVIDEO` (24 cadenas), del módulo **SFRS** (vídeo en movimiento), que no es lo mismo.

**Corrección de la revisión:** el borrador citaba **etiquetas de Ghidra** (`s__GOLFSHOT__…`) en vez de las cadenas reales, yreatribuía el prefijo de módulo.

**NO VERIFICADO:** qué es exactamente "ALOCK" y cómo se combinan los búferes; la unidad de `vfc2indx`; el significado de `deg`; si el `JPEG_DEC` de BGEST es el decodificador del proyecto; por qué la fw3.21 elimina MOTIONSHOT.

[Conclusiones](../analysis/s88_shotmodes/golfshot_motionshot.md) · [JSON](../analysis/s88_shotmodes/golfshot_motionshot.json).

## S89 — el módulo `IDT`/`IDT_OPD`: mapas del imager, FOPD e IDTSA (21-10-2026)

**VERIFICADO (11 tests, `tests/test_s89_idt.py`):** el módulo `IDT` (297 cadenas que empiezan por `[IDT]`) y `IDT_OPD` (273) es **el mismo código con dos prefijos**: cada mensaje aparece dos veces, contiguas (`4cmap.adrs Err:%X` en `0x43cf2c2e` y `0x43cf2c4b`; igual para `histmap` `0x43cf2c64`/`0x43cf2c83`, `summap` `0x43cf2c9e`/`0x43cf2cbc`, `shade_map` `0x43cf2bf0`/`0x43cf2c11`, `imgmap` `0x43cf1e45`/`0x43cf1e63`, `refmap` `0x43cf1eb5`/`0x43cf1ed3`, `backImgData` `0x43cf1e03`/`0x43cf1e26`, `miniRAW` `0x43cf40e0`/`0x43cf4100`, `msain0/1` `0x43cf463d`/`0x43cf4663`, `msaout` `0x43cf4689`/`0x43cf469e`, `p_backImgData` `0x43cf46ff`/`0x43cf471b`). **Los mapas que entrega al imager**: `backImgData`, `imgmap`, `refmap`, `shade_map`, `4cmap`, `histmap`, `summap`, `miniRAW`, `msain0/1`, `msaout`, más `ie_in/ie_out`, `lc_in/lc_out`, `mapRC_in`, `p_img_map` y `out_opd_cc/out_opd_ec`. El **miniRAW** lo consume directamente el AF híbrido: `[CAMERA_MAIN_LC]: [LC] Movie DM AF cannot get miniRAW Stored memhandle` `0x43c9c8ba` (→ S75/S71). **FOPD** (42 trazas): cuatro canales (`FOPD_AIF_R0/W0/W1/W2_ERROR` `0x43c91547`–`0x43c915a7`), lanzado desde la captura (`KickFOPD error` `0x43cadd2d`/`0x43cadd60`) y repartido por el `SyncResMgr` (`[IDT]r0:… [FOPD]r0:… [PRC]r0…` `0x43ca2939`). **Split/IDTSA** (52 trazas con "Split"): `GetIDTSA Unknown aspect` `0x43cf3306`/`0x43cf332c`, `calc SplitIDTSA error` `0x43cf34d4`/`0x43cf3508`, `IDTSA Invalid Ch select` `0x43cf3538`/`0x43cf3562`, `Illegal FRM mode for IDTSA` `0x43cf5147`, más `Split Movie Cannot use AIF/Insel`, `Fatal Not Copiled for Split Cap` → **captura partida** (2 frames) del AF por desplazamiento. **Regiones de detección** que el IDT calcula para el subsistema de caras: `kido_th[%d].up/dn` `0x43cf2962`/`0x43cf2983`, `ratio_wak[%d].up/dn/rgt/lft` `0x43cf29de`–`0x43cf2aa6`, `sel_hist`/`sel_sum`/`sel_wak`/`sel_waku`, `idealWidth/idealHeight` (mismo tipo de estructura que `box af_island_*` del módulo `[STK]`, S71). Además `VATR` (36 trazas, resultados `det`/`gle`, `0x43cf3ec8`) y `NSX_OPD` (`FRM set SGC unknown` `0x43c915c7`, `FRM start unknown` `0x43c915e9`, `IDT AIF illegal address`).

**NO VERIFICADO:** qué distingue las variantes `[IDT]` y `[IDT_OPD]`; el significado de `kido_th`, `ratio_wak`, `waku`, `gle`; formato y tamaño de cada mapa; qué es FOPD exactamente; cómo se calculan las coordenadas del modo Split; qué es `NSX`/`SGC`.

[Conclusiones](../analysis/s89_idt/idt_opd_maps.md).

## S82 — AutoFraming y las etapas de control del pipeline (21-10-2026)

**VERIFICADO (8 tests, `tests/test_s82_autoframing.py`):** el **encuadre automático** son **tres etapas** del pipeline: `Stage_AutoFraming.cpp` `0x43cc71a3`, `Stage_AutoFraming_ResizeRotate` `0x43cc71b9` y `Stage_AutoFraming_Branch` `0x43cc71d8` — **las mismas tres existen en la A7S fw3.20** (`0x43cc26ac`/`0x43cc26c2`/`0x43cc26e1`). El log clave es `[IMAGING_CAP]: Debug) ResizeRotate Framing size force set: offset[%d,%d] size[%d,%d] rotate[%d]` (`0x43cc7143`; A7S `0x43cc265b`): el encuadre se **impone** con offset, tamaño y **ángulo de rotación**, y antes se **valida** (`ImageAreaResize.us_Size_X/Y` `0x43cc6e5f`/`0x43cc6eaa`; el lienzo debe contener el área `canvas_size.ul_SizeX(%d) < ImageAreaResize.us_Frame_X(%d)` `0x43cc6ef5`/`0x43cc6f79`; y alineación `Align Error … us_Frame_X/us_Frame_Y/us_Size_X/us_Size_Y` `0x43cc6ffd`–`0x43cc70f2`). Las **ocho etapas de control/comunicación** (iguales en A7S): `Stage_CaComm.cpp` `0x43cc7b9c`, `Stage_CameraHAPI.cpp` `0x43cc7bad`, `Stage_Notify.cpp` `0x43caccd6`, `Stage_WaitControl.cpp` `0x43cad784`, `Stage_SACC`/`Stage_SACC.cpp` `0x43c9ee6c`/`0x43c9f18a`, `Stage_Common.cpp` `0x43cac363`, `Stage_DevLater.cpp` `0x43cac51b`, `Stage_DualRec.cpp` `0x43cac9f8`. Relación con el motor de imagen (INFERENCIA por proximidad en rodata): `CaComm`→`CONTP` (`sa_func_CONTP_acquire error` `0x43cc7bfa`), `DualRec`→`DUALREC_BAYER`/`DUALREC_CLEARVID` (`0x43cac9c1`/`0x43cac867`), `SACC`→`NFLASH` (flash) (`sa_func_NFLASH_start error` `0x43c9ef73`); **en AutoFraming no hay ninguna llamada `sa_func_*`**: el encuadre se aplica con parámetros de imagen propios.

**Corrección de la revisión (21-10-2026):** `Stage_WaitControl.cpp` está en `0x43cad784` (en `0x43cad6fd` está `Stage_RchRcv_ResizeTrim`); el error estaba también en el informe de S76 y **se ha corregido allí** (con test). Y es **falso** que en la A7S el AutoFraming esté "disperso o ausente": tiene las mismas tres etapas y el mismo log.

**NO VERIFICADO:** cómo se calcula el encuadre (qué dato lo origina) y qué es la "rotación" que se impone; su relación con los `apc_*` (S78); qué intercambian `CaComm` y `CameraHAPI` con la app; qué es exactamente "SACC".

[Conclusiones](../analysis/s82_autoframing/autoframing_stages.md) · [JSON](../analysis/s82_autoframing/autoframing_stages.json).

## S91 — submódulos del framework ADF: ADJ, SYSND, GS, FACE, AFNR, CH_SRC (21-10-2026)

**VERIFICADO (8 tests, `tests/test_s91_adf_submods.py`):** se cierran los submódulos que S81 dejó abiertos. **`[ADF][ADJ]`** (24 trazas) = el ajuste del **sensor de audio** (`AdfSenserCtrl::SetParamSet{MicMode 0x43c26dc1, RecLevel 0x43c26df4, ChSource 0x43c26e28, InputType 0x43c26e5c, RecLevelMode 0x43c26e91, HpMonitor 0x43c26ec9, InputTrim 0x43c26efe, LowCut 0x43c26f33}`) → es la **implementación** de los comandos de depuración `[ADF][DBGCMD] InputPro Set*` de S81 (enlace con S69). **`[ADF][SYSND]`** (27) = el **sonido del sistema** (pitido) con compensación de retardo por **60/50 Hz** (`m_StartTransDelay60` `0x43c279a4`, `m_StartTransDelay50` `0x43c279f9`, `m_dummySetOutputSysndDelay` `0x43c27941`, `PS ON` `0x43c278f0`) → el retardo se ajusta al estándar de TV de la región (mismo eje que el `DOWNCON` PAL/NTSC del visor, S86). **`[ADF][GS]`** (2) = arranque de un "path" de proceso (`START PROC PATH ERR` `0x43c327d3`, `START STATE ERR state : %x` `0x43c327f2`). **`[ADF][FACE]`** (2) = el ADF **arranca y detiene la detección de caras** (`StartExecFace` `0x43c32a3b`, `StopExecFace` `0x43c32a54`) → puente explícito ADF↔S71. **`[ADF][AFNR]`** (2) = proceso de **reducción de ruido del AF** (`StartExecAfnr:%x` `0x43c32990`, `StopExecAfnr` `0x43c329ac`). **`[ADF][CH_SRC]`** (1) = arranque del **micrófono AVIO** con FIFO (`AvioMicStateStart fifoErr %x` `0x43c2e99a`).

**NO VERIFICADO:** qué es "GS"; el parámetro de modo de AFNR; los 24 mensajes completos de ADJ; la relación exacta de los retardos 60/50 Hz con el estándar de TV.

[Conclusiones](../analysis/s91_adf/adf_submodules.md).

## S87 — almacenamiento, sistema de archivos y tarjeta (21-10-2026)

**VERIFICADO (9 tests, `tests/test_s87_storage.py`):** en `av-cam.bin` el **medio externo** es un recurso sincronizado de `CAMERA_MAIN_SYNC` (`ExternalStorageStart/Acquire/Release() Error` `0x43cb3148`/`0x43cb317f`/`0x43cb31b8`; A7S `0x43cb4372`), la ruta de la foto RAW es **`DCIM/100MSDCF/DSC%05d.ARW`** (`0x43cac566`; A7S `0x43cb022b`, más el ejemplo literal `DCIM/100MSDCF/DSC00001.ARW` `0x4401ea7f`) y **`/setting/psd.bin`** (`0x43ccf2b6`) es **novedad fw3.21** (0 apariciones en la A7S → coherente con S75 y S72). **Negativo verificado**: en `av-cam.bin` hay **0 apariciones** de `exFAT`/`EXFAT`/`FAT32`/`CLIP_` → el sistema de archivos está **en el userland**: **`libInfraFsys.so`** (375 524 B; **51 × "EXFAT"**, 8 × "FAT32"; estructuras **BPB** `BPB_Media`, `BPB_TotSec16/32`, `block size/start (org|adj)` y atributos `FSYS_ATTRIB_{ALL,ARCHIVE,DIRECTORY,HIDDEN,NONE,READONLY,SYSTEM,VOLUME}`; fechas con **desplazamiento UTC** y precisión de 10 ms), **`libObj.so`** (17.4 MB; **13 × "CLIP_"**; el modelo de contenido con `contentType`, `entryCondition`, `p_entryIdList`, `mainJpg`, `thumJpg`, `screenNail`, `exifSrcArea`, `lensModel`, `publicMakerNote`/`secretMakerNote` y, para el espacio, **`forcastUseSizeOnDstDisc`** (previsión del tamaño de la próxima captura), `remainSizeOnDstDisc`, `isExistUnsupportedContent`, `dubbingProhibitionFactor`) y **`libmpr.so`** (10.3 MB; el **índice**: `category folder`, `date num`, `entry num`, `last date folder`, `playlist num/folder/category folder`, `total mark num`, `creationTime`, `thumbPictFileModTime`, `aviFileModTime` y `seekPoint … packLength` → el índice apunta a posiciones dentro de los packs).

**Correcciones de la revisión:** las direcciones del borrador eran **offsets de fichero** (`0x772148`…) y no direcciones del binario; `CLIP_` **no está** en `av-cam.bin` sino en `libObj.so`/`libmpr.so`; y la implementación exFAT/FAT32 **sí** existe, en `libInfraFsys.so` (con BPB y atributos FSYS).

**NO VERIFICADO:** MBR/particiones y formateo; el máximo de imágenes por carpeta y la regla "reducir/divide"; la codificación de prefijos más allá de `DSC%05d.ARW`; el formato binario de `Index/`/`SceneInfo`/`DCF`; los contenedores de vídeo en tarjeta.

[Conclusiones](../analysis/s87_storage/storage_filesystem.md) · [JSON](../analysis/s87_storage/storage_filesystem.json).

## S93 — el bus de mensajes OSAL del userland (21-10-2026)

**VERIFICADO (6 tests, `tests/test_s93_osal_bus.py`):** el lado Linux de la cámara se organiza en **microservicios** que se hablan por colas OSAL, con dos niveles: **GID** (grupo, 16 nombres) y **LID** (cola, 13 nombres). Grupos: `AIRPLANE_MODE_SCALAR_API`/`_TEST` (libInfraAirplaneMode), `APP_VIEW_SCALAR`/`INFRA_VDF`/`CAMERA_RAW_DEVELOP`/`NET_BACKUP_SERVER` (libObj), **`DETECT_FACE`**/`DMM_CTRL`/`SADRIVER` (libBizFw), **`GPS_GET`** (libmpr), `NETSERVICE_SCALAR_API`/`SYNC_EMU`/`TEST` (libNetService), **`TASK_ADC`** (libRsrcHotshoe), `WLAN_RSRC_DBG`/`_TEST` (libWlanResource). Colas: `AIRPLANE_MODE_API`, `DLNACONTROL_CP`/`_MAIN`/`_MEDIASVR` (libInfraDlnaControl), `GPS_GET` (libmpr), **`MDNS_CONTROL_MAIN`** (libInfraMDnsControl), `NETFUNCTIONMGR_MAIN` (libInfraNetFunctionManager), `NETSERVICE_ASYNC_REQ`/`SYNC_REQ` (libNetService), `NET_BACKUP_SERVER_INFRA_NET_SERVICE_CMP` (libObj), `R_HOTSHOE_API` (libRsrcHotshoe), **`WEBAPI_MAIN`** (libInfraWebApi), `WLAN_RSRC_API` (libWlanResource).

**Lo que revela (VERIFICADO):** el "firmware de negocio" `libBizFw.so` es quien **orquesta la detección de caras** (`OSAL_MSGQ_GID_DETECT_FACE`) y el driver del escalar; la **A6000 incluye soporte de GPS en el firmware** (`libgps_rsrc.so` + `OSAL_MSGQ_GID_GPS_GET` en libmpr) aunque no tenga GPS de hardware (código heredado de la A7S); y la cámara **se anuncia por mDNS y expone una API web** (`libInfraMDnsControl.so`, `libInfraWebApi.so`).

**NO VERIFICADO:** los mensajes concretos de cada cola; qué sirven `CAMERA_RAW_DEVELOP` y `NET_BACKUP_SERVER`; si el bus OSAL del userland es el mismo que el ADF del firmware; el protocolo de la API web.

[Conclusiones](../analysis/s93_osal_bus/osal_message_bus.md).

## S90 — reproducción de vídeo: PlayArranger, VFC y VDISP (21-10-2026)

**VERIFICADO (23 tests, `tests/test_s90_playback.py`):** el subsistema de reproducción de vídeo del `av-cam.bin` se articula en **tres ejes**: (1) los **organizadores de reproducción** (`20AbstractPlayArranger` `0x43c43c7c`, `12PlayArranger` `0x43c43c93`, `19PlayArrangerAdapter` `0x43c43cd2`, `16NullPlayArranger` `0x43c43d00`, `20VideoArrangerAdapter` `0x43c43cbb`, `22VideoReserveCmdCreator` `0x43c43ca2`); (2) el **programador de VFC** (contador de campos de vídeo: `20AbstractVFCCmdIssuer` `0x43c43dea`, `12VFCCmdIssuer` `0x43c43e01`, `12VFCScheduler` `0x43c43e95`, `12VFCSchedulerCore` `0x43c43ea4`, `14VFCScheCmdList` `0x43c43e3a`, `16VFCReScheCmdList` `0x43c43e4b`, `24VideoFieldCounterFactory` `0x43c43e1f`) que **programa los comandos al reloj de vídeo** (mismo reloj que `CLK_CTRL`, S85); y (3) el **estado de reproducción** (`10MPlayState` `0x43c43ecf`, `MPlay` `0x43c66542`) con la traza ` bid=MPLAY cid=%#hx flg=%d dvfc=%#x ivfc=%#x edge=%#hx` (`0x43c660e0`) y `Issue VFCCmd to MPLAY.` (`0x43c7291e`). El **visor de vídeo** (VDISP) tiene **cuatro modos de salida**: `VDISP24p` (`0x43c4811f`), `VDISP30p25p` (`0x43c481c2`, `SeqCtrl,PcpSet`), `VDISP60i50i` (`0x43c48341`) y `VDISP60p50p` (`0x43c4856a`), cada uno con su lógica de descarte de cubos TCUB (`[DiscardTcub] [cnt:t/b/p][%d] tc[%d][0x%02x%02x…]`) y su `GetPlayState(): DISP_PLAY_UNKOWN is NOERR` → el **mismo eje de down-conversion PAL/NTSC** que S86. Además, la reproducción consume el bloque `AUGI` (`16DecAugiConverter` `0x43c43d2a`, `20NullDecAugiConverter` `0x43c43d13`, `21DecTcubEventRequester` `0x43c43ce8`) y la tabla de secuencia VP (`24AbstractVpTableSequencer` `0x43c43d3d`, `16VpTableSequencer` `0x43c43d58`, `6VPInfo` `0x43c43d6b`, `10VPInfoCore` `0x43c43d73`, `21AbstractTblMsgHandler` `0x43c43d94`, `13TblMsgHandler` `0x43c43dac`).

**Revisión:** verificado por muestreo (15/15 nombres de clase en sus direcciones + las cadenas `bid=MPLAY`, `Issue VFCCmd to MPLAY.` y los cuatro modos VDISP): el informe del subagente era correcto, sin correcciones.

**NO VERIFICADO:** la semántica exacta de `cid`/`flg`/`dvfc`/`ivfc`/`edge` en la cabecera MPLAY; qué son los "cubos TCUB" que se descartan; la relación entre `VPInfo` y el `AUGI` de S83; el punto de reanudación (`18ResumePointChanger` `0x43c43f04`) y la reserva (`18ReserveCmdRegister` `0x43c43f47`).

[Conclusiones](../analysis/s90_playback/playback.md) · [JSON](../analysis/s90_playback/playback.json).

## S95 — los ficheros que la cámara lee y escribe (21-10-2026)

**VERIFICADO (7 tests, `tests/test_s95_files.py`):** el firmware de la A6000 usa **43 rutas de fichero** en cuatro zonas: **`/usr/sabin/`** (27), **`/mnt/`** (11), **`/setting/`** (1) y **`/usr/dfe/`, `/etc/`, `/usr/share/`** (4). **Parámetros de procesado**: **22 ficheros SPICA** con la nomenclatura `spica_musashi_<modo>_<canal>_tap_step<N>.bin` (`<modo>` ∈ still, mov, mov_4k, mov_interlace, dualrec, dualrec_4k; `<canal>` ∈ **C**/**Y**; dos pasos) — confirma y precisa lo que S76 apuntaba: el procesado SPICA toma sus parámetros de ficheros externos, con variantes por modo de captura (incluida la grabación dual BAYER+CLEARVID de S82); además `star_kernel_param.bin` (`0x43cc3d1a`, el kernel STAR de S84) y las **tablas de PSF** de la deconvolución `dcv_psf_table_{still,movie,movie_4k,dualrec}.bin` (`0x43cb9a34`–`0x43cba9ea`, para `Stage_Decomp`/`Stage_LoadDeconvPsfTbl` de S76). **La cámara escribe sus propias trazas en el disco RAM**: `/mnt/FILE_IS_%04x.dat` (IS/EIS, S70), `/mnt/FILE_TC_COMMON_%04x.dat` (giro, S70), `/mnt/lc_mslog_%04x.dat` (calibración de lente/ZPD, S75), `/mnt/Mount_ms_log_%03d.dat` (montura, S66), `/mnt/cc_ms_log%04x.dat` (control de captura, S82), `/mnt/detect_ms_log%04x.dat` (detección, S71), `/mnt/YC_FILE%04x.dat`, `/mnt/log.bin` y `/mnt/%s.%4d%02d%02d_%02d%02d%02d.dat` (con **fecha y hora** en el nombre) → **estos ficheros deben estar en los volcados de RAM de la cámara** (`analysis/camera-dumps/`, S64/S65) y son una fuente primaria para contrastar los hitos sin más instrumentación. Otros: `/usr/dfe/dfe.bin` (`0x43cd1b94`, la imagen del DFE), `/setting/psd.bin` (`0x43ccf2b6`, 0 en A7S), `/etc/localtime`, `/usr/share/zoneinfo`, `/usr/share/locale`.

**NO VERIFICADO:** el formato binario de los `spica_musashi_*` y de las tablas PSF; qué es "musashi"; el formato de `/mnt/*.dat`; si esas trazas sobreviven en el volcado de RAM; por qué 4K y dualrec tienen parameter sets propios.

[Conclusiones](../analysis/s95_files/file_inventory.md) · [JSON](../analysis/s95_files/file_inventory.json).

## S92 — la base de datos de medios: SceneInfo, MovieFile e índice (21-10-2026)

**VERIFICADO (10 tests, `tests/test_s92_mediadb.py`):** el modelo de medios de la cámara tiene su parte de **userland** (`libmpr.so`, `libObj.so`, `libInfraFsys.so` — ver S87) y su parte de **firmware** en `av-cam.bin`: el **secuenciador LIRO** (`[CAMERA_MAIN]: LiroSequencerMovieFileFormat : %d` `0x43ca3b3a`, que además lee la **posición del dial de diafragma**: `LiroSequencer cannot read IRIS_DIAL_POS` `0x43ccadbf`) y la **nomenclatura de escena** `Scene%02d.txt` (`0x43ccb21b`). En el userland, la interfaz `MprIf` (1525 apariciones en `libmpr.so`) gestiona el contenido: `PreRegisterDcfContentSync` (8), `GetHighlightSceneInfo` (2), `SceneInfo` (10) y, en `libObj.so`, `SceneInfo`/`HighlightScene` (5). La ruta de la foto sigue siendo `DCIM/100MSDCF/DSC%05d.ARW` (`0x43cac566`).

**Revisión:** verificado por muestreo (todas las cadenas citadas en sus direcciones) — el informe del subagente era correcto, sin correcciones; se añade el dato de `IRIS_DIAL_POS`.

**NO VERIFICADO:** el contenido de los `Scene%02d.txt` y dónde se almacenan exactamente; la relación con la especificación **DCF** (`xDCF`/`D2FxDCF` en el blob); cómo se relacionan `MovieFileFormat` y la nomenclatura de clips de la tarjeta; el formato del índice en disco (`Index/`).

[Conclusiones](../analysis/s92_mediadb/media_database.md) · [JSON](../analysis/s92_mediadb/media_database.json).

## S94 — la API HAPI de la app remota (21-10-2026)

**VERIFICADO (6 tests, `tests/test_s94_hapi.py`):** `libHapiLib.so` (89 628 B en A6000; 77 380 B en A7S) es la biblioteca de la **API de la app remota** (HAPI). Estructura (símbolos mangled verificados): `HapiLibMain` (singleton, `getInstance`, `mainLoop`, `interrupt`, `getTargetQId`), `Cam::CamService` (`getInstance`, `run`, `interrupt`, `processReq(REQ_MSGE)`, `processComp(COMP_MSGE)`, `processCaptureEvent(EVT_MSGE)`) y `Sdf::SdfService` (`run`, `interrupt`). Tipos de mensaje: **`REQ_MSGE`** (29 apariciones), **`EVT_MSGE`** (3), **`COMP_MSGE`** (53), `SDF_MSG_SENDE` (6), `MAIN_MSG_RECVE` (4) y la categoría **`CATEID_HAPI`** (1) con `CATEID_SDF_ACK/COMP/NEXT`. La API de cámara propiamente dicha son **139 símbolos `Camera::CamApi*`** (`CamApiBase::apiFactory`, `stmDepositYc`, `stmDepositRaw`, `stmInquire`, `stmWithdraw`, `checkOneTicket`/`checkThreeRawTickets`, `convertErrorCode`, `freeImageInstance`/`freeExif`/`freeStdYc`, `setHapiCommon`) → la app puede **depositar YC o RAW, pedir/info/tirar de tickets y recibir eventos de captura**. Del lado de la cámara, la etapa `Stage_CameraHAPI.cpp` (`0x43cc7bad`) es el punto de entrada (S82).

**NO VERIFICADO:** los IDs numéricos de `msg_id` (qué acción corresponde a cada uno); el mapeo exacto cola OSAL ↔ `Stage_CameraHAPI`.

[Conclusiones](../analysis/s94_hapi/hapi_api.md) · [JSON](../analysis/s94_hapi/hapi_api.json).

## S96 — modos de captura: `drive_mode`, `CapMode` y la tabla 69 → 14 ShdMode (21-10-2026)

**VERIFICADO (7 tests, `tests/test_s96_modes.py`):** hay **dos niveles de "modo"**. El **`drive_mode`** es el modo del **imager** (0..0x44 = **69 valores**): lo usan `SetExposure`/`Execute`/`SetRead`/`GetModeParam` (`[CAM_IMAGER]: Invalid SetExposure Error!! [drive_mode:%2d]` `0x43c9397a`, `Invalid Execute` `0x43c93a6c`, `Invalid SetRead` `0x43c93d30`, `GetTransModeState DriveMode Error!! [src_drive_mode:%02x] [dest_drive_mode:%02x]` `0x43c94a9f`, `Invalid GetModeParam` `0x43c94aff`), sincroniza con el resto del sistema (`SIFSyncCode`, `GetPrelightImagerDriveMode` `0x43cae26b`) y **condiciona el tamaño de lectura** (`getDriveModeSizeRatio` `0x43cae2b7`); y el **patrón de ojos** depende de él (`[DFECore]: eyePtn:%d is unusable in driveMode:%d.` `0x43c92bde`). El **`CapMode`** (con `ExposureID`, `ContID`, `FrameID` y `BDROSeq`) es el modo de la **captura**, en `CAMERA_MAIN_CC`: `ExtractCaptureData()` `0x43ca54c8`, `CaptureInit()` `0x43ca552b`, `SetReadImageParam()` `0x43ca55a9`, `SetNRParam()` `0x43ca5627`, `SetOPDParam()` `0x43ca56a5`. El cruce modo→sombreado es la tabla `tbb` de **69 bytes** en `0x438ef418` que usa `SHD::GetShdMode` (`0x438ef40e`, `cmp r3,#0x44` + `tbb [pc,r3]`) y que reduce los 69 modos a **14 ShdMode** (S66). Modos nombrados en el firmware: foto (`SDF_RECMODE_STILL_REC` `0x43c7effb`), vídeo (`REQ_MOVIE_REC` `0x43ca13be`), ráfaga (`BURST_CNT` `0x43cb4bfe`), panorámica (`MSG_ID_SDF_PANORAMA_CCNR_ENCODE` `0x43c781e4`), barrido (`PanoramaSweepStart` `0x43cab054`), bracketing (`lc_BracketAF.cpp` `0x43ca79ba`), intervalo (`[SDF] interval(PTM) %ld` `0x43c7a1a5`) y golf (S88).

**NO VERIFICADO:** la tabla de 69 `drive_mode` con nombre (no está en el blob); el rango de `CapMode`/`ContID`; cómo se calcula `BDROSeq`; la equivalencia `drive_mode` ↔ `CapMode`.

[Conclusiones](../analysis/s96_modes/capture_modes.md).

## S97 — sincronización audio/vídeo del codificador (21-10-2026)

**VERIFICADO (12 tests, `tests/test_s97_encsync.py`):** los módulos que coordinan audio, vídeo y el codificador AVC en la A6000 fw3.21: **`[ENCMODEMGR]`** (21 trazas, `0x43c4ac73`) = `McAvcEncModeMgr` (`15McAvcEncModeMgr` `0x43c431fb`), que gestiona el modo de encoding y la **secuencia de comandos** (`RecordCodecIfCmd: CmdCode/CmdTime/ExecTime/CurrentRefTime`, `ComQue CANNOT Exec!`, y los `CMD_ID_*`: `ACT_ENC`, `GET_REF_TIMER`, `INIT_ES_API_PARAM`, `INACT_CHIP`, `ALLOC_USER_DATA_AREA`, `BEGIN_ENC`, `SET_SEQ_PARAM`, `TERM_ENC`, `STILL_ENC`, `APPLY_USER_DATA_GOP/PIC`, `MUTE_AUDIO_CAPTURE`, `INIT_RC_BUFFER`, `SET_RC_WTPT`, `SET_ENC_READ_POINTER`; métodos `ProcVsyncPre/Post`, `ProcMsg(MSG_MC_AVC_ENC*)`, `EnqueueCodecIfCmd`); **`[ENCAUDOUCR]`** (9, `0x43c4b444`) = escritura del bloque **AUGI** con el audio (`IsOuCrank/Sampling/FrameRate/ImagingRate`, `TermEnc(vfc24/vfc32/cnt): NormalTerm/OuCrankTerm/GopNum`, `Begin Enc: StartAdr/BuffAdr/BuffSize`, `AUGI(AVCODEC-AVSC) OverFlowFile:`, `WriteAugi : AUGI FLAG END`, `[AUDIO INFO] Pts = 0x%08x EndFlug = 0x%02x, Num Au = %x`); **`[ENCAUDSYNC]`** (17, `0x43c526d3`) = sincronización por **semáforos** (`McSyncEncStart::SetEncStartTimeForThumbnail`, `MC[%d] comes later/earlier`); **`[ENCOUCUDMG]`** (7, `0x43c522fb`) = desbordamiento/alineación de datos de usuario; **`[VIDENCCTRL]`** (13, `0x43cd6070`) = control del encoder con 22 apariciones de `MSGID_AVC_ENC_VIDEO_*`; más los ya decodificados `[VIDENCSTAT]` (70) y `[ENCOUCSTAT]` (49).

**Corrección de la revisión (21-10-2026):** (a) el borrador daba **offsets de fichero** (`0x70a444`…) → convertidos a direcciones del binario (`0x43c4b444`, `0x43c4ac73`, `0x43c631fb`, `0x43c522fb`); (b) es **falso** que estos módulos sean exclusivos de la A6000: la A7S fw3.20 tiene **el mismo conjunto y los mismos recuentos** (`ENCMODEMGR` 21, `ENCAUDSYNC` 17, `ENCAUDOUCR` 9, `ENCOUCUDMG` 7, `VIDENCCTRL` 13, `VIDENCSTAT` 70) y los mismos símbolos; la única diferencia es que la A7S tiene **5 trazas de error más** en `[ENCOUCSTAT]` (54 frente a 49).

**NO VERIFICADO:** el formato exacto de los mensajes `MSG_MC_AVC_ENC*`; el formato del bloque AUGI en la tarjeta; cómo se eligen los parámetros de sincronización.

[Conclusiones](../analysis/s97_encsync/encoder_sync.md) · [JSON](../analysis/s97_encsync/encoder_sync.json).

## S99 — la arquitectura del userland: las capas de `libObj.so` (21-10-2026)

**VERIFICADO (6 tests, `tests/test_s99_userland.py`):** `libObj.so`, la mayor biblioteca del userland (17 436 172 B en A6000; 16 184 848 B en A7S), contiene **2507 símbolos mangled en 167 namespaces** (la A7S: 2538 en 168) → el userland de la A6000 es **prácticamente el mismo** que el de la A7S. Reparto por capas: **`MprIf`** (318, medios: contenidos, carpetas por fecha, playlists — S87/S92), **`MWF`** (241, núcleo de mensajes: `MWF::ObjMsgList`/`ObjMsg`/`ObjMsgEntry`/`RsrcAcsr`), **`ux`** (227, gráficos: `ux::core::GraphicsImage`, `GraphicsSystem::setOSDGainParam`, `TextLayout::registerFontFaceFile`), **`AVBIZ`** (138, *universo de aplicaciones*: `AVBIZ::UNIVERSE::UActiveObject` con `onStarting`/`onStopping`/`SendMsgToApp`/`eventProcessing`, `UBbSuspend`/`UBbResume`, `SelectorProxy`, `ULog_u16x5`/`ULog_u8x10`), **`OBJAVBBCBASECLASS`** (128, el puente de imagen Obj→AVBBC, S16–S30), **`MprCtrl`** (58), **GUI** (`ViewBase` 53, `LayoutableWidgetBase` 45, `AppWidgetBase` 27, `DefRootView` 22, `CmnViewMenuData` 23) y el **toolkit `GEN_*`** (`GridList` 45, `Calendar` 34, `Button` 29, `Label` 24, `Balloon` 22, `EditBox` 20), **`C_DataflowInfra_*`** (44, pipeline de datos), **`InputService`** (36), **`UFW`** (34, recursos: `DfsWrapper`, `MsgReceiver::RcvMsg/PostMsg`, `RsrcWrapper::AcquireSingle/ReleaseAll`), **`NetCommonLibrary_*`** (25) y **`GCM_*`** (24), más `ScalarView` (17), `HighlightManager` (19) y `GlobalAccessor` (18).

**Lo que revela (VERIFICADO + INFERENCIA):** el userland es **capas** — `MWF` (mensajes) + `UFW` (recursos) como base, `MprIf`/`MprCtrl` para medios, `ux`+`GEN_*`+`ViewBase` para la **interfaz**, `AVBIZ::UNIVERSE` como **gestor de aplicaciones** con mensajería asíncrona, `OBJAVBBCBASECLASS`+`C_DataflowInfra_*` para la **imagen**, `NetCommonLibrary`+`GCM` para la **red**. `UFW::RsrcWrapper::AcquireSingle/ReleaseAll` es el **arbitraje de recursos** del lado Linux (coherente con el `SyncResMgr` del firmware, S81) y el "escalar" aparece en ambos lados (`ScalarView`, cola `SADRIVER`, S93). **La A6000 tiene 10 símbolos menos de red** (`NetCommonLibrary_`: 25 frente a 35), coherente con S72.

**NO VERIFICADO:** qué separa `MprIf` de `MprCtrl` y `MWF` de `UFW`; los 167 namespaces completos; cómo se registran las apps del `UNIVERSE`.

[Conclusiones](../analysis/s99_userland/userland_architecture.md).

## S98 — `libBizFw.so`: el orquestador userland y el puente con el ADF (21-10-2026)

**VERIFICADO (9 tests, `tests/test_s98_bizfw.py`):** `libBizFw.so` (**332 600 B**, *stripped*) es la biblioteca que **une el userland con el firmware**: usa tres colas OSAL (`OSAL_MSGQ_GID_DETECT_FACE`, `OSAL_MSGQ_GID_DMM_CTRL`, `OSAL_MSGQ_GID_SADRIVER`), define **9 categorías** de mensaje (`CATEID_PIN/RENDERER/DISPLAY/SYSTEMSOUND/AUDIOPROCESSOR/MIC/MIXER/SPEAKER/EFFECT`), **1 identificador** (`MSG_ID_VDF_SRVC_SET_YC_REC_CONTROL`, el control de grabación YC dirigido al servicio del visor) y **11 peticiones** con respuesta (`REQ_DEPOSITE`, `REQ_DEPOSIT_MULTIE`, `REQ_DESTRUCTE`, `REQ_INQUIREE`, `REQ_OVERWRITEE`, `REQ_PARSEE`, `REQ_PEEKE`, `REQ_POKEE`, `REQ_RAW_PARSEE`, `REQ_SHAREE`, `REQ_WITHDRAWE` → el ciclo de vida de un objeto: depositar, consultar, compartir, releer, destruir), más la clase de estado `StmCh`. **El puente es la clase `OBJAVBBCBASECLASS::AdfCh`**: sus métodos repiten **exactamente** el vocabulario de los comandos de depuración del ADF del firmware (S81) — `PrcSetPath` ↔ `Prc SetPath`, `SysSetTable`/`SysRequest`/`SysSetPath` ↔ `Sys …`, `InSetInput`/`InSetIVoice`/`InSetLowCut`/`InSetWindNr` ↔ `In …`, `PrcSetFader` ↔ `Prc SetFader`, `OutSetOutput`/`OutSetSpSwap`/`OutSetVolume` ↔ `Out …` → **la numeración de prefijos (`Prc`/`Sys`/`In`/`InPro`/`Out`) es el contrato entre userland y firmware**. El userland envía mensajes a **diez destinos**: `ADF`, `DETECT`, `DMM`, `HAPI`, `HDMI`, `SA`, `SDF`, `SDI`, `VDF`, `VEF`. En el firmware, el escalar tiene **125 nombres de clase RTTI `NS_SCALAR_INFRA*`** (p. ej. `N15NS_SCALAR_INFRA21ScalarInfraSequenceIfE` `0x43ce59d2`). El vocabulario es **idéntico en la A7S fw3.20** → código compartido.

**Corrección de la revisión (21-10-2026):** las trazas `PrcSetPath to ADF` y `Snd Msg to ADF` **no están en `av-cam.bin`** (0 hits) sino en `libBizFw.so`: es el **userland** quien envía al ADF (el subagente las atribuye al firmware). El test lo fija.

**NO VERIFICADO:** el formato binario de los mensajes ADF y la tabla de equivalencia con las 11 peticiones; qué distingue el canal `SA` de `SADRIVER`; el mapeo de `MSG_ID_VDF_SRVC_SET_YC_REC_CONTROL` al servicio del visor.

[Conclusiones](../analysis/s98_bizfw/bizfw_bridge.md) · [JSON](../analysis/s98_bizfw/bizfw_bridge.json).

## S100 — el contrato de comandos del ADF (firmware) ↔ `AdfCh` (userland) (21-10-2026)

**VERIFICADO (7 tests, `tests/test_s100_adf_contract.py`):** el firmware expone su control interno como **90 comandos `[ADF][DBGCMD]`** agrupados en familias: `Input` 16 (`SetInput`, `SetInputContinue2/3/4`, `SetExtType`, `SetRefLevel`, `SetZoomLink`, `SetLowCut`, `SetUnderWater`, `SetRecLevel`, `SetReverseLR`, `SetAdjThrough`, `GetShoe*`/`SetShoeOnComp`), `InputPro` 8 (`SetIntMicSens`, `SetInputType`, `SetInputTrim`, `SetChSource`, `SetRecLevelMode`, `SetAgcLink`, `SetManualGainLink`, `SetRecLevelLimitter`), `Output` 9 (`SetOutput`, `SetOutputContinue2/3/4`, `DetectJack`, `SetHdmiFormat`, `SetAntiClipping`, `SetSpSwap`), `OutputPro` 3, `System` 12, `SystemSound` 7, `Proc` 19 (las **fases lineales del arranque**: `SetLinearPhase`, `LinearPhase{SetDec0/1,SetAip0/1,GetSa0/1,GetPin0/1,Nomatch0/1,SetMb,SetSa,MemPrint}Print`, `SetPath`, `SetMixRatio`, `SetFader`, `SetZoomNr`), `SoundAnalyzer` 4 (golf, S88) y `CPU2` 4 (la **medida del tiempo de ejecución** a 60/48 Hz, S81). El userland (`libBizFw.so`) implementa la clase **`OBJAVBBCBASECLASS::AdfCh`** con **35 métodos** (`Prc` 8, `Sys` 4, `In` 8, `InPro` 7, `Out` 8) y **cada uno tiene su comando gemelo en el firmware con la familia traducida** (`PrcSetPath`↔`Proc SetPath`, `SysSetTable`↔`SystemSound SetTable`, `InSetInput`↔`Input SetInput`, `InProSetAgcLink`↔`InputPro SetAgcLink`, `OutSetOutput`↔`Output SetOutput`, `OutProSetHpMonitor`↔`OutputPro SetHpMonitor`) → **la numeración de prefijos y verbos ES el contrato userland↔firmware**. Excepciones: cuatro métodos solo en userland (`PrcSetPeakDetect`, `PrcSetAudioOutpinMute`, `OutSetVolume`, `SysSetVolume`) y un comando solo en firmware (`InputPro SetManualGainLink`); el userland no puede invocar los comandos de inspección (`LinearPhase*`, `CPU2 ExecTime`, `SoundAnalyzer*`, `ClearMSGQ`, `CountMSGQ`, `GetMSGQ`).

**NO VERIFICADO:** el formato binario de cada comando y su equivalencia con las 11 peticiones `REQ_*` (S98); qué hace el submódulo `Prc`; la semántica de `PrcSetPeakDetect`.

[Conclusiones](../analysis/s100_adf_contract/adf_command_contract.md).

## S104 — prefijos de traza exclusivos de la A6000 (21-10-2026)

**VERIFICADO (6 tests, `tests/test_s104_prefixes.py`):** seis prefijos de `analysis/s79_modules/module_map.json` que la A7S fw3.20 **no** tiene. `ADC_DEBUG` (14 cadenas, `0x43ce50dd`→`0x43ce5273`): ADC de **12 canales** del LIRO, tarea `TSK_ADC` y `boot_exit_adcliro`, mensaje OSAL de 0x20 B con cabecera `0xfff1` (`0x4398eb22`). `AVR` (2, `0x43c25502`→`0x43c25528`): **accesorio** LANC-AVR del módulo `ACCY` (`LANC-AVR Attached` `0x43c252b4`, handlers GPIO `0x43565680`/`0x435656d4`). `ADR` (1, `0x43cce3fa`): **campo** de dirección de una apertura IM dentro de un mensaje de `0x43901d50`, no un módulo. `BKID` (4, `0x43cce1ea`→`0x43cfb1a8`): *backup ID* (`BKID_SDF_QTBL_C` `0x43c77aeb`, `Backup_read(BKID_*)`). `AVOUT` (2, `0x43c2549e`→`0x43c254c6`): accesorio **AvOut** de `ACCY` (`AvOut Attached` `0x43c25260`). `CAMCORE` (37, `0x43c905ca`→`0x43cebcb2`): la librería **`Camera::CamCore`** (SGC, RDC/PFR, AIF/DMA, recursos, `ExlHelper`; RTTI `N6Camera7CamCore8RdcImageE` `0x43c906b6`).

**Corrección de S73:** hay **cinco** cadenas `ADJ ADC`, no cuatro; `GET_DATA` (`0x43ce4fc7`) no está referenciada.

## S103 — el subsistema SDF: la capa de dataflow de imagen still (21-10-2026)

**VERIFICADO (51 tests, `tests/test_s103_sdf.py`):** `[SDF]` = **477 trazas** (`0x43c7785b`→`0x43c806f9`) y **15 `[SDF_ERR]`** (`0x43c7a145`→`0x43c7eb78`). SDF es el **ejecutor de trabajos** de imagen still: el gestor de captura (`IMAGING_CAP`, S106) le envía **33 `MSG_ID_SDF_*`** distintos (`paint_image`, `copy_image`, `resize_rotate`, `resize_rotate_lowspeed`, `encode_jpeg`, `decode_jpeg`, `encode_jpeg_rec`, `decode_jpeg_rss`, `encode_jpeg_with_work`, `redeye`, `beauty_effect`, `image_effect`, `image_mix`, `split_encode`, `split_resize`, `develop_resize`, `develop_resize_apl`, `scn_encode`, `scn_encode_with_thm`, `ccnr_encode`, `ccnr_encode_with_mode`, `ccnr_resize`, `panorama_ccnr_encode`, `thm_copy`, `thm_encode`, `jpeg_sort`, `dist_encode`, `dist_resize`, `dist_resize_no_tanz`, `face_resize`, `set_date_image_param`, `set_date_image_param_dual`, `ptm_count`), todos en `0x43c78000`→`0x43c78350`. Los errores son casi todos de **PTM** (`bigger_value.ptm_32==PTM_SECOND_ZONE`, `smaller_value.ptm_32==PTM_FIRST_ZONE`, `interval PTM`, `check stop PTM`) → el temporizador de imagen (`PTM`, `MSG_ID_SDF_PTM_COUNT`). Funciones: `FUN_43638308` (init; pasa `0x43c77857` = la cadena `"sdf"`), `FUN_435ab6f0` (dispatcher), `FUN_4363c730` (factoría de trabajos JPEG), `FUN_4363ca28` (ejecutor), `FUN_43639c78` (manejador de mensajes). En userland, `OBJAVBBCBASECLASS::SdfCh::{resizeRotate,paintImage,copyImage}` (`libObj.so`). La A7S fw3.20 tiene el mismo módulo con **479** trazas (`0x43c7a1eb`→`0x43c83082`).

**NO VERIFICADO:** el significado del acrónimo (la hipótesis *Still DataFlow* encaja con `DataflowInfraErrorCode` en la primera traza, pero no hay evidencia textual); el formato de los mensajes `MSG_ID_SDF_*`; las dos trazas de diferencia con la A7S.

## S69 — subsistema de audio de la A6000 (línea general) (21-10-2026)

**VERIFICADO (9 tests, `tests/test_s69_audio.py`):** el audio del `av-cam.bin` A6000 es un *IP* más del driver de sensor: arranque `AUDIOIP INIT COMP` (`0x43c26411`) con configs VGS/PR/MF/CONS/BANDI; micrófono (`AdfSenserCtrl::SetParamSetMicMode` `0x43c26dc1`, `Abb::SetMicConfig` `0x43cddad4`, `AbbMicSensAdjustCtrl::SetStatus` `0x43cddd49`); niveles (`SetParamSetRecLevel` `0x43c26df4`, `SetParamSetRecMode` `0x43c26e91`, `15AbbRecLevelCtrl` `0x43cdddf3`, `RecLevel SetRecLevel` `0x43929fa4`); WNR y cancelación de voz (`WindStage:%d, MagDataRsv:%d` `0x43cddea7`, `MAGIC SetNwnr`, `New WNR ON/OFF`, `PremiumCloserVoice`, `MyvoiceCanceling`, `iVoice` `0x43cddeec`–`0x43cddf9a`); códecs `XAVCS_LPCM` `0x43c6909d`, `MP4_LPCM` `0x43c690c8`, `AAC` `0x43c690f1`; diagnóstico (`targetAudioFormat` `0x43c5c68e`, `audioChannelNum` `0x43c5c6b1`, `audioMuteRec` `0x43c5ca62`); enlace con vídeo (`ProcBuffMgrWrAudioPin` `0x43c28d29`, `AVBB_SCN_START/STOP_AUDIO`); backup de sonido (`9AudioIpIf` `0x43cdd82e`, `Sa SaChangeBackup` `0x43cddfbc`). **A7S (fw3.20) tiene códec externo** (`15AbbExtCodecCtrl` `0x43cd582e`, `ConvChSsau2AudioIpCh` `0x43c2f48a`) que la A6000 (fw3.21) **no tiene**; el resto del audio es prácticamente idéntico (235 vs 237 cadenas).

**NO VERIFICADO:** frecuencia de muestreo/bits/canales; "reduce voltage" del micrófono; muxer de audio en el contenedor; coeficientes del DSP de WNR; ganancia/calibración del micrófono; semántica de VGS/PR/MF/CONS/BANDI.

**Sin efecto en la línea SilentShutter:** fin electrónico NO VERIFICADO; **S51 A=NO/B=NO/C=NO** se mantiene.

[Conclusiones](../docs/capture/s69-audio-subsystem.md) · [informe](../analysis/s69_audio/audio_subsystem.md). Siguiente: muestreo/canales reales, muxer de audio en el contenedor de vídeo, semántica de las configs VGS/PR/MF/CONS/BANDI.

## S66 — montura de lente E-mount (línea general; sin relación con SilentShutter) (20-10-2026)

**VERIFICADO (31 tests, `tests/test_s66_lens_mount.py`):** el `av-cam.bin` de A6000 contiene un subsistema de montura de lente completo: código `0x436dfe6c`–`0x436e9ea4`, 646 logs en `0x43c95659`–`0x43c9a900`, ficheros internos `Mount_Controller.cpp`/`Mount_DividedInfo.cpp`. Bus cuerpo↔lente **UART** con handshake **CS/DATA** por GPIO (`gpio_get` `0x43b5e2bc`); **trama**: cabecera `0xF0`, longitud `size+8` LE, commtype `&7` en `+3`, **ID de comando en `+5`** (`0x07` ATTACH_INFO1, `0x0A` CS_CREDIT, `0x15` UPDATE_DATA, `0x16` LENS_SLEEP, `0x2B` ALPHA_LENS_INFO), checksum **u16 LE** (suma de `buf+1` durante `len-4`) y footer `0x55`; validación `HEADER_NG`→`FOOTER_NG`→`CHECKSUM_NG`→`DATASIZE_NG`→`COMMTYPE_NG`. Tipo de lente = 2 bits (`campo & 3`): 1 → **4.8 V** (4096 mV), 2 → no registrada, resto → desconocido (error `0xFF`; válido `0x0A`). Ciclo de vida completo en los 63 logs de la tarea `0x436e5e3c` (LENS_WEAR → UART_HZ → ATTACH_INFO1..4 → STARTUP_INFO → CS_CREDIT → WAKE_UP → POWEROFF → DETACH_1/2/COMP → LOGIC_ON/OFF → STANDBY). **FW de la lente** por el mismo bus con CAIF/C3P (emisor `0x436fe070`: `LUPDT_INFO`/`LUPDT_DATA`; capa CAIF `0x436ba2c8`) y **segundo bus al DSP de la lente** `[LENS_PDR]`/BonoboDSP (`0x437089d4`, `0x43708a88`, `0x43708cc4`, MMIO `0xf292d000`). 18 ficheros `/lens/VX91xx_lensfile.bin` (cabecera `LF` de 16 B: `u16@2=0x10`, `u32@4=filesize−0x10`, `u16@12=lens_id`; secciones `ED`/`CS`/`LC`; tabla de nombres en `0x43C22BF2`, 18 slots × `0x42`; parser en `0x43907c7c`) cargados por un servicio **dentro de `av-cam.bin`** (`0x43904fb0` → `0x43b2a7e2` → lookup `0x43907bc4` sobre la tabla `0x43C22BF2` → parser `0x43907c7c`), al que `Camera::Lens::ODL::Load` (`0x43721b9c`) los pide con `AsyncSend`/`AsyncRecieve` («lensfile» solo aparece en `av-cam.bin` en toda la partición `dev`); ficheros A6000 idénticos byte a byte a los de A6300; la A7S 3.20 no tiene este subsistema. Sombreado por lente: 11 `ss_LensMountShdValue[]` + 32 `us_LensMountShdGain[]`; perfil por tabla `tbb` de **69 modos de captura → 14 ShdMode** (`0x438ef418`); bloque SHD **idéntico** A6000/A7S (217 logs cada uno, solo cambia el prefijo `[CAMERA_MAIN_YC]:`). fw3.21 (A6000) **añade** 4.8 V, LENS_WEAR, DETACH/attach, ALPHA_LENS_INFO, CS_CREDIT, CHG FREQ y handshake `[HS]` frente a la fw3.20 (A7S), que conserva el núcleo y la ruta de FW-update.

**NO VERIFICADO:** pines físicos de CS/DATA y de la alimentación 4.8 V; unidades de `UART_HZ 750/1500`; nombre de cada ID de comando (la tabla de descriptores se registra en runtime); identidad del servicio que abre los ficheros de lente.

**Sin efecto en la línea SilentShutter:** fin electrónico NO VERIFICADO; **S51 A=NO/B=NO/C=NO** se mantiene.

[Conclusiones](../docs/capture/s66-lens-mount.md) · [montura](../analysis/s66/lens_power_attach.md) · [sombreado](../analysis/s66/lens_shading.md) · [clase/ODL](../analysis/s66/lens_class_and_jobs.md). Siguiente: pines GPIO del bus de lente (backup BK4 o esquema), framing/IDs de comando restantes, servicio que carga `/lens/VX91xx_lensfile.bin`.

## S61 — origen de parámetros IMX210 y flujo de mensajes (20-10-2026)

**A6000 (Claude, 22 tests):** TBH corregido (base `0x43806a08`; script/test de Sol actualizados). Bloque `obj+0xe20`: **A** (`0x437ab474`) escribe solo si `bit6(G[0xD])==0` con `G=0x43e964a4` (GOT+0x21a0; **no** el objeto de 0xF20 B: corrige S60) 6×`(G[0x168],G[0x16A])`; **B** (`0x43aecbec`) solo si `[[p]+0x3a]==1` (stage: 0 en `0x437a9d30`, `src+0xb4` en `0x437aa65c`, borrado si `G[0xD]` bit6). B ← `obj8=obj+0x2cc` ← P0 `0x43861ed0` (←`obj+0x2be..0x2d0`, origen NO localizado); 6.º par ← tabla BK4 `0x300AB` (idéntica en 5 `CX77500`: 18×`(0x2EA0,0x6028)`). Pares = ventanas lo/hi ±0x400 (H «tiempos» debilitada). Petición 9 ← `0x43b00ed8` ← **`HS_Main` `0x4378fef4`**; publicación ← **`VD_Pre` `0x43792a0c`**; petición 3 sin emisor; `0x8003030f`≈alias de `0x3030f`. Estados ALCANZABLES: 0 (un PERMITIDO). Fin electrónico **NO VERIFICADO**; **S51 A=NO/B=NO/C=NO.**

[Conclusiones](../docs/capture/s61-conclusions.md) · [parámetros](../docs/capture/s61-imx210-parameter-origin.md) · [mensajes](../docs/capture/s61-message-flow.md) · [matriz](../analysis/s61-evidence-matrix.json). Siguiente: escritores de `obj+0x2be..`/`G+0x168`/`G[0xD]`, leer `HS_Main` entero (¿fin de exposición?), sembrar Thumb en los 5 puntos.

## S60 — emisor de mensajes IMX210 y receptores A7S (20-10-2026)

**A6000 (Sol 6 tests + Claude):** `0x438069f0` = despachador de la tarea de mensajes `0x43806e38` (recv `0x3030f`); casos 4/10 son respuestas a 3/9 (`0x43b00fe6`/`0x43b00f62` → `0x43806400` → `0x8003030f`). Corrección: TBH base `0x43806a08` (casos → `0x43806c28`/`0x43806d06`). Los 24 B `+0xdd0` = `obj+0xe20..e37`: 6 pares u16 escritos por `0x437ab510` (A) y `0x43aecbfa` (B) vía accesor `0x43ae8504`; semántica de tiempo HIPÓTESIS. **A7S (Claude, 12 tests):** `0x1000/0x1001` = registros de traza (API `0x438f6864`, 381 llamadores) a la cola `0x8f013a`, no bloqueantes, eco de SetExposure/SetRead; Silent no los emite; consumidor no localizado. `0x439b3918`=memcpy ARM, `0x438f7114`=printf de trazas. **GPT:** auditoría NO obtenida (límite de uso hasta 17:56). Fin electrónico **NO VERIFICADO**; **S51 A=NO/B=NO/C=NO.**

[Conclusiones](../docs/capture/s60-conclusions.md) · [cruzada](../docs/capture/s60-cross-validation.md) · [matriz](../analysis/s60-evidence-matrix.json). Siguiente: auditoría GPT pendiente, productores de `obj+0x168/0x16a` y petición caso 3/9; traza pasiva autorizada para física.

## S59 — Claude + GPT-6.1 Sol: bloque IMX210 `+0xDD0` y constructor real A7S (20-10-2026)

**GPT (A6000, 11 tests):** escritor del bloque `0x437876dc()+0xdd0` = `0x43b00da0` (copia 80 B → `obj+0xdb4`; publicada por `0x43b00dd4` si `obj+0x57c≠0`; fuente `obj+0xd64` ← payload en `0x438069f0` casos 4/10). Constructor deja ceros: M no sale de constantes. `clk` NO es el objeto de histogramas (corrige S58-A §5). VdNum=`max(0,raw−0x3000)`. M/Tv/clk alcanzables 0x0B/0x2F: NO VERIFICADO. **Claude (A7S, 9 tests):** constructor real `C_Imager` = `0x436f3fc0`; con él las mismas 100 escrituras que S58, pero base P2S real `0xfc088300` y 3 tramas (127/94/26 B): S58-C (`0xf3c00300`, 5 tramas) era artefacto sintético. Mensajes `0x1000/0x1001` = lista blanca de modos `{0x0b,0x35,0x37,0x38}` (no estado sin inicializar; receptor sin localizar). Consumidor de ganancia `0x436f459c`: único llamador `0x436f5b40`. Revisión GPT corrigió C59-5/7/9/10. Fin electrónico IMX210 **NO VERIFICADO**; **S51 A=NO/B=NO/C=NO.**

[Conclusiones](../docs/capture/s59-conclusions.md) · [cruzada](../docs/capture/s59-cross-validation.md) · [matriz](../analysis/s59-evidence-matrix.json). Siguiente: emisor del payload de `0x438069f0` (origen real de M/Tv/clk) y receptores de `0x1000/0x1001` (Thumb sembrada); física: traza pasiva autorizada.

## S58 — productores AE y configuración A7S efectiva (Claude→Codex, 20-10-2026)

**Hito offline cerrado con cobertura delimitada:** productores `0x4383d4d0` y `0x4383c9dc` comprobados en Unicorn (600/600 y 300/300 en campañas); falta origen Tv/M/clk real. Productor/validador host NO son idénticos para todo VdNum/svr. **CORRECCIÓN de S57:** SetExposure A7S=`0x436f4168`, SetRead=`0x436f4a94`; matriz IMX235=69 filas de 0x14 B con selección indirecta de 15 columnas. Diferencias 0x4c→0x4e=14, 0x4d→0x4f=11. Cadena de cuatro métodos y P2S ejecutada para seis modos, objeto sintético y servicios stub; no es captura integral. Son 100 escrituras (99 DEV81 + 1 DEV83), no 99 totales. Umbral 0x1000 pertenece a ganancia; consumidor `0x436f459c` pone/borra bit4 de 0x81:0x5f, también en foto. **S51 A=NO/B=NO/C=NO.** No se demuestra fin electrónico del IMX210.

[Conclusiones y reproducción](../docs/capture/s58-conclusions.md) · [matriz](../analysis/s58-evidence-matrix.json). Siguiente: recuperar escritor del bloque `0x437876dc()+0xdd0` leído por `0x437aa65c`, con valores M/Tv/clk alcanzables; para semántica física, datasheet o traza pasiva autorizada. No repetir comparación de matriz S57 ni atribuir el umbral a exposición.

## S57 — antecedente; A7S corregida por S58 (Claude, 20-10-2026)

**VERIFICADO (`tests/test_s57_imx210_exposure.py` 34/34, Unicorn + Capstone + REA):** ID1 (dir 1) = **registro combinado**: SetMode carga bits 0/2 desde la matriz (A `0x4401ca2c`; B `0x4401c734` es copia de A en cada Execute), SetExposure fija bits 2,7,4,6 según ShutMode, `0x436d7c08` el bit 3 (SSB), `0x436d7cf0` borra 2,7,4 solo en la ruta de ajuste (`+0x279`, AdjustCmd 0x91). **SSB** se pide siempre tras SetExposure y antes de `Execute(1)` (5 productores; ausente en `Execute(0)` y en `ExposureTimerEnd!`); A7S lo genera dentro de SetExposure si `arg+2>0x1000`. **svd/shd/spl:** mapeo exacto (svd 12 b → ID3/ID4[3:0]; shd 14 b → ID5/ID6[5:0]; spl 12 b → ID7/ID8[3:0]; 400/400); `cap+0x650`=svd cuenta pasos del host (`cap+0x4b9c`) y `0x4381106c` valida `svd=n·svr_num−1`; productor AE (banco `0x43eb35d0`) NO localizado. ShutMode real en captura: solo 0 y 1. **IMX235 Silent** `0x4e/0x4f` = variantes mínimas de `0x4c/0x4d` (1–4 registros; dir `0x000C`) y 33–35/35 distintos de `0x0b`; sin comando de «terminar integración». **XPI** = CN0400 pin 6 → sensor F6 (también A7S), 0 cadenas `SHT_RST`. **P2S SyncMode** se escribe en `0xfc088800`; solo modo 2 usa banderas OSAL y disparo 1,0,1.
Fin electrónico de integración a resolución completa: **NO VERIFICADO** (ningún registro se reescribe al terminar). **S51 se mantiene.** Próximo: `trace_native_values` sobre el pipeline AE (`0x43844e80/0x4384b268/0x4385b234`) o traza pasiva CIS0+XPI+VD.
[Conclusiones](../docs/capture/s57-conclusions.md) · [Matriz](../analysis/s57-evidence-matrix.json). REA con `GHIDRA_MAXMEM=6G`, sesión cerrada.

## S56 — transporte de registros IMX210 (Claude, 20-10-2026)

**VERIFICADO (`tests/test_s56_imx210_transport.py` 26/26, emulación Unicorn del código real):** `SetExposure` solo escribe registros sombra; `Execute` (vtable+0x38) los envía por **P2S(DFE0)** (`0xfc088300`): los «IDs» (119 punteros `0x43fe995c`, mapa `0..0x155`, ID1 duplicado) son **direcciones de 16 bit**; trama `81|len|81|AH AL|datos`, 119 registros → 2 transmisiones, ida y vuelta exacta. `svd/shd/spl` = IDs 3–8 (+0x144–0x149); `ShutMode` 0–4 → ID1 = 40/C4/94/D4/C0 (solo el 2 carga 0x100/0x101). Pulso SSB = ID1 bit3 enviado 2 veces. CISIF = receptor (no bus de configuración). Cadena sin GPIO/P4C. A7S: mismo P2S, registros de 5 B con byte de dispositivo, sin ShutMode 2. SENS_B: sin consumidor (clústeres 0xf2a1/0xf2403 parecen reloj/ADC).
Fin electrónico de integración a resolución completa: **NO VERIFICADO**. **S51 se mantiene.** Próximo: traza pasiva CIS0+XPI+VD (decodificable) o rastrear origen de `0x43eb35d0`.
[Conclusiones](../docs/capture/s56-conclusions.md) · [Matriz](../analysis/s56-evidence-matrix.json). REA con `GHIDRA_MAXMEM=6G`, sesión cerrada.

## S55 — origen de los pares GPIO (base de backup BK4), A7S vs A6000 (Claude, 20-10-2026)

**VERIFICADO (`tests/test_s55_bionz_sync.py` 16/16):** los pares (canal, bit) de la tarea CA **no** vienen de código externo: slot de servicio `+0x2e0` = `Backup_read_4Byte` (liro.ko) y los valores están en
`0110_backup/*/CX77500_*.bin` (A6000; A7S `CX78500_*`), formato BK4 reconstruido de `backup.ko`. El escritor de `0x43e77298…0x43e772d4` es **`0x436bcef4`** (A7S `0x436dc054`; S54 no lo vio: store vía GOT).
Lectores = (3,17),(10,3),(0,12),(0,7),(5,14), salidas (7,15),(7,13): handshake SIO; banco 0 = `GPIO_S_n` (nfc.ko + esquema; (0,7)=CA_RELEASE_LOCK). Estructura **idéntica en A7S** (14 funciones 1:1, mismos IDs/valores;
único `set` extra de A7S = no-op). Ningún par con bit 9 fuera del banco 0 → `GPIO_9` sin lector GPIO (INFERENCIA); `SENS_B` sin rastro (NO VERIFICADO). `ExposureEndNotify`/`ExpStartComp` no leen GPIO.
IMX210 sin avance. H55-1 VERIFICADO, H55-2/4 descartadas en lo recuperado, H55-3/5/6/7 NO VERIFICADO. **S51 se mantiene.**
Próximo: traza pasiva P4C/VD/CIS0 autorizada; estático: bloque SENS_B (escritores `0xf2a1…`), IDs dinámicos de `0x43716dd0`.
[Conclusiones](../docs/capture/s55-conclusions.md) · [Matriz](../analysis/s55-evidence-matrix.json). REA: `analysis/rea-independent/bin/session_daemon.py` con `GHIDRA_MAXMEM=6G`, 1 sesión cerrada.

## S54 — P4C, tipo de mecanismo 0 y BIONZ (Claude, 20-10-2026)

**VERIFICADO (`tests/test_s54_p4c.py` 21/21):** `CA_1ST_CURTAIN_START` (P4C) llega a BIONZ por **`SENS_B` (AA13) y `GPIO_9` (AD21)**, igual en A7S (el esquema A7S sí está en
`docs/references/`: corrige «pines A7S inferidos» de S53). Darwin solo escribe **P4C←0** (9 sitios por ROM, nunca ←1; `0x51f2` conserva b12), también en la rama sin mecanismo;
en A7S Silent la escritura P4C se conserva. **Tipo 0 de A6000 ≡ rama Silent A7S** en exposición/diferidos/ADC (diff llamada a llamada), pero **no** en reposición (A7S Silent actúa
con `no_silent=1`; tipo 0 nunca) ni en lo previo a Darwin. Tipo = `[0x20000050+ch]` validado por `[0x200002c0+ch]` (manejador 33 de `0x2a1a0`); escritor NO localizado.
BIONZ: primitivas GPIO `0x43b5e2bc/22e/29a` (base `0xf2910000`); lectores de la tarea CA usan variables de pin sin inicializar en la imagen → **consumidor de P4C NO localizado**.
IMX210 sin avance. H54-1 INFERENCIA, H54-2 PARCIAL, H54-3/4/7 NO VERIFICADO, H54-5 PARCIAL reforzada, H54-8 INFERENCIA fuerte. **S51 se mantiene.**
Próximo: `av-cam` A7S (barrido `gpio_get`) + inicializador de pines; traza pasiva de P4C/`GPIO_9` autorizada.
[Conclusiones](../docs/capture/s54-conclusions.md) · [Matriz](../analysis/s54-evidence-matrix.json). SHA ROM A6000/A7S y `av-cam.bin` OK.

## S53 — parser CAIF de Darwin A7S vs A6000 (Claude, 19-10-2026)

**VERIFICADO (bytes, `tests/test_s53_darwin_caif.py` 10/10):** el paquete CAIF ev1 (22 B) llega a Darwin (FM3, base `0x4200`) por
MFS5 (P36–P38 = `MSS_*_DWN` ↔ IC6000 BIONZ X) como mensaje mss-async **ID `0x0c`** (código `03 01`, 22 B; identidad con op `0x10300`:
INFERENCIA fuerte). **Parser:** A7S `0x18396`, A6000 `0x17f8c`, idénticos salvo que A7S guarda `pkt[+0x12]&0x20` en `S+0xd0.b5`
(`0x18460`) → predicado `no_silent` `0x19a86`/`0x216c2` que **impide escribir P4D/P4E** (`1ST/2ND_CURTAIN_MG`; `0x2172c`, `0x21786`,
`0x217b2…`, diferidos `0x214dc/0x214fa`) y omite el seguimiento ADC. A6300 tiene la misma rama. **A6000 descarta el bit** y sus
escritores (`0x20cb2`, `0x20d00`, `0x20d26…`) no tienen argumento Silent. Modo 2 de `+0x0d`: sin consumidor (PARCIAL).
**Escenario B:** falta lógica de firmware en Darwin A6000 (además de LIRO e IMX210). **S51 se mantiene.** Pines A7S por inferencia.
[Conclusiones](../docs/capture/s53-conclusions.md) · [Matriz](../analysis/s53-evidence-matrix.json). SHA 3/3 ROM Darwin OK.

## S52 — clase 0, `+0x748` y cortinas (Claude+Codex, 19-10-2026)

**VERIFICADO:** la A7S **no suprime** el control de cortinas en LIRO. Envía igual el paquete CAIF ev1 al MCU de obturador, pero con
Silent **marcado** (`+0x12` bit `0x20`, `+0xd` modo 2; `0x4386329a/0x43863258`) y byte de clase = 3. Además deja de **esperar** las
respuestas del mecanismo: CAIF 3 y bandera `0x800000` (`0x438b1cba`, `0x438b726c`), según `captura+0x748`. Esa bandera es la misma que la
A6000 tiene en `+0x740`: tiene lectores pero ningún escritor (latente). La clase 0 llega a `param+9`: `0x43864c74→0x43f04c8c→R+0x69→cap+0x651→0x436f2938→vtable+0x28`.
Identidad de R resuelta por el coordinador (`analysis/s52_coordinator_check.py`). La clase sola no omite CAIF/MMIO (solo el mensaje `0x22`).
**INFERENCIA fuerte:** la decisión física la toma el MCU Darwin (parser CAIF no localizado). P5 NO VERIFICADO; **S51 se mantiene**.
Corrección: IMX235 `cfg2+4|=8` en todos los ShutMode (no solo 0). Próximo: parser CAIF en `darwin_core.bin` A7S vs A6000 (bit `0x20`).
[Conclusiones](../docs/capture/s52-parallel-conclusions.md) · [Matriz](../analysis/s52-evidence-matrix.json). SHA 8/8 + manifiestos OK.

## A7S Silent reconstruido (estático) — 19-10-2026

**VERIFICADO (bytes+LLVM+REA, test `work/claude/tests/test_a7s_silent_facts.py`):** en A7S 3.20, `0x40e3`→estado `+0x250`→conversor
`0x4379ec04` (tipo {0,2})→`captura+0x78c`→ (a) selector `0x43826d58`: tipo 2 ⇒ drive_mode `0x4e/0x4f` (IMX235, columnas propias,
45/69 campos distintos de `0x0b`); (b) política `0x438649bc`: tipo 2 ⇒ clase de obturación 0. A6000: receptor `+0x238` existe, pero su
selector `0x437f7f98` y su política `0x43842158` son el mismo código **sin** ramas Silent, y el IMX210 no tiene modos `0x4e/0x4f`.
H1 mayormente refutada; S51 (no parchear) se mantiene. Pendiente: clase 0 → cortinas. [Informe](../docs/capture/a7s-silent-reconstruction.md).

## Referencia comparativa — 19-10-2026

**Decisión del usuario:** A7S 3.20 sustituye a A6300 2.01 como referencia (A6300 queda histórica; supera la instrucción del 16-10).
Manuales Level 3: mismo CXD90027GF con 12 pares sub-LVDS; sensores IMX235 (A7S) / IMX210 (A6000). [Comparación](../docs/references/a7s-vs-a6000-service-manuals.md). Firmware A7S en `firmware/extracted/a7s-fw320`, sin analizar.

## Hito REA independiente (Línea B) — 19-10-2026

**VERIFICADO:** REA 6.5.0+Ghidra 12.1.4 abre `av-cam.bin` (raw ARM, base 0x43541000)
con `REA_GHIDRA_STARTUP_TIMEOUT_MS=900000`: análisis completo en ~459–486 s (por defecto
330 s no basta), 42006 procedimientos, pico RSS 2,3 GB. Frente a 464 entradas históricas:
363 exactas, 9 absorbidas, 92 ausentes (las Thumb sembradas a mano, p. ej. 0x43789cc0).
234/234 listados idénticos a Línea A; LLVM decodifica en las 38708 direcciones.
`libmprctrl.so`: 8 funciones coinciden en bytes, nº de instrucciones y offsets (análisis ~22 s).
**PARCIAL:** el decompilador B no pliega literales a `_DAT_f3c3xxxx` (Línea A sí, 19/234).
Setters 0x436c6288/6294 escriben `0xf3120000+0x48/+0x4c`; semántica NO_VERIFICADO.
**Sin evidencia nueva** de exposición electrónica independiente de cortinas.
Límite: la sesión REA no persiste (rea#1048 abierta); Línea A sigue siendo la referencia de verificación (Thumb sembradas); la exploración nueva va primero por REA: ver `docs/STATE.md` § Política de ingeniería inversa.
Línea A, `silent-liro.*`, firmware y S1–S48 intactos (SHA idénticos).
[Informe](../docs/capture/rea-independent-milestone.md). Próximo exacto S48 sin cambios.

## S51 — decisión vigente (19-10-2026)

**A=NO, B=NO, C=NO.** No hay una ruta electrónica demostrada ni un parche justificable, y tampoco una imposibilidad demostrada.
T1 (VERIFICADO): el modo `0..7` (getter `0x43842404`→`0x43eedecc`) solo llega al registro `0x4383fb6c` (+0x6d/+0x6e/+0x70,
serializado por `0x438e2b98`) y a eventos; `ModeRsvParam` = `0x43795a60(cap+0x4d0 drive_mode, +0x4d4, +0x4d5)`, con el drive_mode
fijado en `0x437f7ff4` sin depender del modo. C_Imager: `SetMode 0x436d62e4`, `SetExposure 0x436d6320`, `SetRead 0x436d6398`.
T3 (Codex): no hay guarda configurable sobre el cierre de la 2ª cortina. T2: ID1/100/101 sin dirección/semántica de sensor.
**Decisión: detener el parche.** Retomar solo con el datasheet del IMX210 o con una traza pasiva autorizada de la interfaz serie
del sensor. [Decisión](../docs/capture/s51-decision.md) · [Codex](../docs/capture/s51-codex-t2-t3.md). SHA 1490/1490 OK.

## S50 — estado anterior (19-10-2026)

**VERIFICADO (investigación paralela Claude+Codex):** `0xb6 A_LINEAR_ELEC_SHUT` sin fila de callback ni caso `C+0x60` → inerte. `0x4382dd78`
construye B desde C (`C+0x94/95→B+0x36/37`); `0x43842158` usa `C+0x94/95` como override del modo `0..7` (`0x43eefb1c+0x60`) que solo se exporta
a registros de estado. **CORRECCIÓN S49:** `1/2/3/6` = cantidad de callbacks, no clases. Bypass CA `+74f` no es foto silenciosa.
**Pregunta final: NO_VERIFICADO** (ni demostrada ni imposibilidad). Falta consumidor físico del modo y significado eléctrico ID1/100/101.
[Conjunto](../docs/capture/s50-parallel-conclusions.md) · [Claude](../docs/capture/s50-claude-electronic-config.md) · [Codex](../docs/capture/s50-codex-exposure-curtains.md). SHA 1490/1490 OK.

## S49 — estado anterior (19-10-2026)

**VERIFICADO:** `0x301d7` = id OSAL de la cola de comandos de ajuste/servicio; clave `0xce` = `S_IMAGER_CURTAINMODE`
(payload `(habilitar, valor)`). Tabla de servicios de `av-cam` copiada por `liro.ko` (`tsk_entry`, `memcpy(hdr[0x14]+0x24)`):
slots `0x4354129c/a0/b4` = `osal_unreg_msg_queue_cb/osal_reg_sync_msg_queue_cb/osal_dynamic_id`. Productor: puente USB
`libsencore` (`TransactionStart 0x25fc8`) y `adjstctl`/`libtestcmd`; `libObj` solo claves 0/1/0x67. **NO_VERIFICADO:** emisor
en uso normal y significado del valor. Informe: [S49](../docs/capture/s49-capture-config-producer.md). Próximo S50:
consumidores de `C+0x94/+0x95`, `C+0x60`, `0xb6`.

## S48 — estado anterior (19-10-2026)

**VERIFICADO:** servicios `+0x1e8/+0x1ec/+0x200` de la tabla `0x435410b4` están a 0 en el blob y solo se leen
(wrappers `0x43561298/0x435612b4/0x43561324`): el proveedor y el emisor del paquete `0x301d7` están **fuera de
`av-cam.bin`**. Función de alta `0x43789fdc` (crea manejador `0x301d7`). **NO_VERIFICADO:** emisor/productor de
`+0x1c/+0x1e`. Informe: [S48](../docs/capture/s48-service-table-provider.md). Próximo: buscar el emisor en
userland (`libObj.so` etc., hits `d7 01 03 00`) o cerrar la línea como frontera externa.

## S47 — estado anterior (19-10-2026)

**VERIFICADO:** entrada `0x43789cc0`, registrada con ID `0x301d7`;
fila clave `0xce` en `0x43ff29b8` → handler `0x43789708`.
Copia solicitud `0x140`B a `0x43e95420`; payload en `0x43e9543c`
→ argumento4 de `0x437da100` → `0x43ed4620` → callback `0x437dad78`.
`0x43ed44dc` es otra solicitud sintética, no el buffer recibido.
Callback ANTES de copia C: despacho `0x43792f9c` domina copia `0x43794096`;
`0x43ae90ce` copia `0x1a4` desde `0x43e9d3b4` a `0x43e9b380`,
incluyendo `+0x94/+0x95`. S46 no queda refutada por orden.
**PARCIAL:** productor original de los dos u16 anterior a `0x43789cc0`;
valor2 y propagación B/G. Servicio de registro `+0x1ec`, slot `0x435412a0=0`.
**Próximo exacto S48:** contrato/proveedor de ese registro y productor del
paquete ID `0x301d7`, clave `0xce`, stores `+0x1c/+0x1e`.
No repetir orden ni solicitud sintética como única fuente. Punto opcional VD
aplazado; clases1–3 físicas y VD/cortinas sin cierre. Hito S46–S52 abierto.
SHA/manifiestos intactos; sin git.
[Informe S47](../docs/capture/s47-payload-producer-and-order.md).

## S46 — antecedente (18-10-2026)

**VERIFICADO:** owner `0x43e15f18` → `0x436c6f3c` → `0x436c7950`
→ setter `0x43acee66` inicializa `0x43e16d2c=0xf3120000`;
destino de S45 base+220=`0xf3120220`, escritura condicional.
C fuente `0x43e9d3b4` construido con offsets partidos `1e40+2c`.
Callback `0x437dad78`, fila `0x43ff8adc`, clave `0xce`, escribe
C+94/+95 desde payload4B: primer u16!=0 → (1,low8(segundo u16));
primer u16=0 → (0,0). Scratch `0x43f7bbf4`, distinto de snapshot `0x43ef2474`.
**PARCIAL:** propagación condicional de (1,2) por copia a C/B/G;
productor del payload y orden completo pendientes. P=padre+1454 sin alias C.
Integración/cortinas y semántica eléctrica `0xf3120220` NO_VERIFICADO.
**Próximo exacto S47:** argumento4 de `0x437da100` hasta payload
`0x43ed4620`; productor de los dos u16 de clave `0xce` y orden frente
a `0x43792f9c/0x4379409e`; después semántica del controlador VD.
[Informe S46](../docs/capture/s46-vd-base-and-context-identity.md).

## S45 — antecedente (18-10-2026)

**VERIFICADO:** contexto437b5b14=43eaadd8, copia0xb0 desde43e993a4;
VD_Pre reconstruye este último desde raíz copiada43e99514.
C=contexto[14]=43e9b380, copia1a4 desde43e9d3b4. AliasP/C pendiente.
GetterIMX210+3a0=43ad9202, virtual+74;43ad90b6→438c828c usa el retorno,
calcula captura+570→43795dec→436c74c8→43ad2bd6 escribe base+220.
**PARCIAL:** controlador43e16d28, base=*(43e16d2c) sin escritor recuperado;
MMIO físico de esa escritura e integración/cortinas NO_VERIFICADO.
**Próximo exacto:** escritores43e9d3b4+94/+95/copiaP→C y escritor43e16d2c
desde owner43e15f18. No repetir getter+74 ni consumidor/virtual+a8.
Termina serie explícitaS40–S45; hito abiertoS46+, sin agotamiento/Línea E.
SHA/.gpr/.rep intactos; sin .git/commit.
[Informe S45](../docs/capture/s45-context-identity-and-physical-closure.md).

## S44 — antecedente (18-10-2026)

**VERIFICADO:** consumidor436d75f8 lee119 paresIDu16/byte+2 de43fe995c;
436d839c→436d79b0→75f8→backend+298→436d5ed0 carga MMIO,
436d5f60 pulsa B+8. Canales{1,2,0}; bancos43bc14e8.
Virtual+a8=436d65b8 compara nibble alto del registroID0 entre13 índices;
ignora flags y devuelve1 si cambia. No transporte dentro del comparador.
**PARCIAL:**4385cf2c produceP+95=2; P=raíz+2bc, alias con
C=*(contexto+50) no probado; snapshot43ef2474 candidato, no identidad.
**Próximo exacto:**origen del contexto de437b5b14 y campo+50 hastaP/C;
después lectoresIMX210+3a0 y semántica físicaID0/integración/VD/cortinas.
No repetir consumidor/virtual+a8; no agotamiento estático ni Línea E.
OSALbit31 y AF permanecen cerrados. SHA/.gpr/.rep intactos; sin .git/commit.
[Informe S44](../docs/capture/s44-register-consumer-mode-table.md).

## S43 — antecedente (18-10-2026)

**VERIFICADO:** PIC4401eee4; slots resueltos a estructuras4401c6xx–4401caxx,
ID u16 + dato byte+2, b3, sin MMIO directo/vtables.43ad9a40/43ad99d4
guardan estado en objeto+fc (la variable ya no representa base PIC).
**RECHAZO** códigos de bloqueo AF: cadenas SetSequenceMode img/fratechg/clamp,
ImgMode/IMAGE_FRAME_RATE/SYNC_RAW_OUTPUT_SIZE; virtual+94 consulta tabla de
modos del backend. **ACEPTO**4380e020/43902718 como log/trace.
**PARCIAL:** transporte de staging, lector IMX210+3a0 y escritor C+94/+95.
**Próximo exacto:** consumidores de registros por slots PIC y virtual+a8 desde
436d92e0; virtual+10 436d8ff4 es getter de0x70B, sin transporte. Después
C=*(contexto+50) en4382dd78→B43eae270→G43ea6ad4→43842158.
No cierre físico, agotamiento global, Línea E ni reapertura OSAL bit31.
SHA/proyecto intactos; sin .git, sin commit.
[Informe S43](../docs/capture/s43-exposure-mmio-and-lock-codes.md).

## S42 — antecedente (18-10-2026)

**VERIFICADO:** corrección de nomenclatura S41:436d6320 es wrapper,
436d634a llama virtual+28; vtable43fcc090+28=436d6f6d. Constructor436d72e8
y factoría436d6504 publican objeto43e7f4a8 en contenedor43e7f858.
Clase2: cargas BYTE en436d7136/7142 desde parámetro+08/+14,
buffers4401c6d2/4401c7ce, cálculo→objeto+3a0. Cortinas/VD NO_VERIFICADO.
**PARCIAL:**4382dd78 copia C=*(contexto+50), C+94/+95 a B43eae270+36/+37;
4384cb58→437b0480 copia c14B a G43ea6ad4;438412d0 pasa G al selector.
Escritor original de valor2 pendiente. No confundir stores43845b68/70:
son otro objeto. R43e9b548+5cc=43e9bb14=ImgState43e9baec+28;
lectores438553dc/4385558a pertenecen a43e18c60, no R.
Cadena de bloque0x44=68B hasta4378e334/43795a60 contrastada, pero sin
dependencia recuperada desde R+5cc. Descriptores3023: parser sin tipar.
**Próximo exacto:** escritores C+94/+95 hasta valor2; lectores IMX210+3a0
y buffers hasta transporte/cortinas; alias ImgState+28 hacia43eea2e4;
consumidor indirecto de getters3023. No reabrir OSAL bit31 sin evidencia nueva.
No agotamiento estático: Línea E no activada; A6300 existe, sin analizarlo.
SHA/proyecto intactos; sin .git, sin commit.
[Informe S42](../docs/capture/s42-exposure-call-identity.md), `analysis/ghidra/s42-findings.json`.

## S41 — antecedente (18-10-2026)

**PARCIAL:** cola principal30001 y snapshots3030f. Productores internos
4000/4036:43816448/43818c1c/43817e20→4381a138→435aa20c→4356120c.
Conversores:43bc59e0={1,0,5},43bc5a50={1,2,0,3}; nombres de opciones
NO_VERIFICADO. Case1:43b01026 envía objeto+4/564B; case10 largo:
43b00f62 envía objeto+6c0/5e0B, incluyendo copia previa en+6c4.
Destino8003030f frente a receptor3030f: bit31 sin resolver, no cerrar bucle.
R+458 o R+48→0,2,1,4 en VD_Pre; sin enlace demostrado a integración.
**Próximo:** productores de argumento1+36/+37 de43842158 (valor2),
argumentos+8/+14 de clase2 en436d6f6c y sincronía de cortinas;
metadatos3023 y lectores de R+5cc hasta argumentos tipados del sensor.
Slots OSAL en435410b4 cero: frontera de implementación; se activó Línea C
para contrastar selector EFCS separado: banco+41c, diagnóstico+7e y
anulación+36/+37. Clase2 alcanza rama distinta; cierre físico NO_VERIFICADO.
Sin agotamiento A/B universal.
SHA/proyecto intactos.
[Informe S41](../docs/capture/s41-message-origin-imx210.md), `analysis/ghidra/s41-findings.json`.

## S40 — antecedente (18-10-2026)

**PARCIAL:** `context[0]+24/+48/+458` provienen de staging43edf684,
escrito por comandos API4000/4036/3023 (bytes solicitud+0a/+09/+0e),
con ceros condicionales438040e8 y437935ae.43804cdc copia560B a raíz;
43804c82/43804d12→43b00d06 copian snapshot objeto+8. Tabla despacho
43fff30c:220×12B; tabla selección43ca3c21={1,1,0,1}.
API demostrada, menú/FPS/píxel y exposición/read-enable/generación física
NO_VERIFICADO. No agotamiento estático.43804cc8 toma staging;
43806a80/43806d50 toman mensaje+4/+8. **Próximo:** productores originales
de esos mensajes case1/10 de438069f0, después enlace
tipado a selectores IMX210. Proyecto readOnly/noanalysis y firmware intactos.
[Informe S40](../docs/capture/s40-context-origin-imx210.md), `analysis/ghidra/s40-findings.json`.

## Qué existe

- Grafo de conocimiento en `.knowledge-cache/knowledge.sqlite` (regenerable, gitignorado):
  **1189 entidades Function, 1764 relaciones CALLS deduplicadas (2604 fuentes de evidencia
  preservadas en `relation_sources`), 39 relaciones CORRECTS/SUPERSEDES.**
- Fuentes del grafo: dossiers JSON legacy, ~430 exports Ghidra (pseudocódigo decompilado),
  5 evidencias REA. Catalogadas por forma estructural en `knowledge/catalog/JSON-CATALOG.md`
  (2146 JSON, 108 familias; dos familias explícitamente excluidas por falta de identidad
  verificable — ver PROGRESS.md Fase 12.4.A).
- CLI unificada: `scripts/knowledge/search.py` (`exact`/`text`/`tree`/`section`/`graph`/
  `trace`/`claim`/`ask`/`freshness`). Servidor MCP: `scripts/knowledge/mcp_server.py`
  (11 tools, límite global 20000 chars).
- Benchmarks: línea base pre-rediseño en `knowledge/benchmarks/baseline-2026-10-18-pre-12.6.md`
  (NO editar). Benchmark rediseñado con verdad de referencia estructurada en
  `knowledge/benchmarks/report-v2.md` (generar con `scripts/knowledge/benchmark_v2.py`).

## Última fase completada

**S39 (18-10-2026):** av-cam SHA/memoria verificados; silent-liro solo
readOnly/noanalysis, sin mutaciones. Tres llamadores de 43814d24 convergen
en config+0c→43ef71a4→4387a6c4→caché 43e77ccc por unidad, valores
0/1/2/4; cambio invalida/reinicializa APL, sin campo hardware/pitch enlazado.
No confundir índices P con remapeo separado input+38. 43ae8d56 fija
context[2]=root+5a4; campo43e9bb14 tiene cuatro escrituras en VD_Pre,
copia/cero/remapeo según estado. Nombres de píxel y opción/FPS no demostrados.
**PARCIAL**, sin declarar agotamiento estático universal. Próximo: fuentes
context[0]+24/+48/+458 y copias masivas hasta solicitud/tabla tipada.
Incógnita física prioritaria: productor/handle/VD y cierre de integración.
[Informe S39](../docs/capture/s39-image-format-apl.md),
`analysis/ghidra/s39-findings.json`. Se conservan S31–S38 debajo como historial.

**S38 (18-10-2026):** SHA av-cam verificado, silent-liro readOnly/noanalysis;
.gpr/.rep intactos. 85 literales 61003c, 16 sin xrefs: pool compartido,
sin servidor/alta recuperados. Blob ORIL/LIRO, no ELF; readelf -d/-r y nm
fallan. Tabla 435410b4, slot +2e4=0 en archivo.
**FRONTERA ESTATICA AGOTADA** para resolución ELF/valor externo del slot
en este blob; no ausencia universal de receptor. Extents→P/APL y productor
físico YC NO_VERIFICADO. **Próximo paso exacto:** enum de formato S33,
input+38←P+1b4←context[2]+28, conversor 43814d24 y campos APL/stride/tamaño.
[Informe S38](../docs/capture/s38-dmm-osal-static-frontier.md),
`analysis/ghidra/s38-findings.json`. S31–S37 se conservan debajo como historial.

**S37 (18-10-2026):** `libmprctrl.so`, SHA
`514e14116caa1d15d75bd56641dabfe815f620b6208008929c44d8d70386011d`,
define AllocDmmMemory/FreeDmmMemory; proyecto nuevo `libmprctrl.gpr`, copia
0444 y export readOnly. Getters originales son **DmmAccessPLA**: leen
dirección/tamaño en respuesta+0x10/+0x14, sin demostrar dominio físico/lógico
ni valor concreto. AllocDmmMemory devuelve cabecera de paquetes, otro layout.
Cliente OSAL **0x61003c**, payload 0x18: compatible parcialmente con campos
S33, pero no idéntico a envoltura 0x55/0x70 ni prueba del slot av-cam.
PLT libObj 0xdc180 importa exactamente DmmCloseAndFree definido aquí,
con DT_NEEDED directo. **Productor físico YC NO_VERIFICADO.** Próximo:
receptor 0x61003c y proveedor tabla av-cam+0x2e4 hasta escritor de extents,
misma clave/ID Rendezvous y APL. [Informe S37](../docs/capture/s37-libmprctrl-dmm-extents.md),
`analysis/ghidra/s37-findings.json`. S31–S36 se conservan debajo.

**S36 (18-10-2026):** analizada únicamente `libInfraScalarMpr.so`, SHA
`b56b4c6172a60b879ebf405bc64e19e7456d230ff6125a21bbd4469e35c0d2c9`, en
proyecto Ghidra separado, export final readOnly. `AllocDmmMemory(int,ushort*)`
y `FreeDmmMemory(int)` son **UND**, no cuerpos locales. `AllocSharedMemory`
devuelve ID SysV y dirección virtual de `shmat`, usada en copia de datos still;
no demuestra origen YC/DMA ni relación con Rendezvous. Próximo: localizar
definidor de `_ZN9DmmAccess14AllocDmmMemoryEiPt` y
`_ZN9DmmAccess13FreeDmmMemoryEi`; resolver por separado slot av-cam.
[Informe S36](../docs/capture/s36-libinfra-scalar-mpr-memory.md),
`analysis/ghidra/s36-findings.json`. S31–S35 se conservan.

**S35 (18-10-2026), investigación de firmware:** los cuatro objetos DFE son
Ofmt/Ifmt; RTTI, vtables y métodos +8 de sus hijos resueltos. Leen y activan
bit 0 de SGC `0xfc0a1210/1310/1610/1710` (+0x1000 en unidad 1), sin lectura/ack
APL recuperado. Bit `0x00200000` sin causa física identificada; los usos en
enable del controlador son otro dominio. **FRONTERA ESTATICA AGOTADA para
esta vía**, no imposibilidad universal: falta routing/semántica hardware o traza
pasiva correlacionada APL/IRQ/VD/handle en cámara sin flashear. Ciclo físico
NO_VERIFICADO. Próximo: DMM importado `0x43561524`, `tabla+0x2e4`, productor
Rendezvous y lector YC real. [Informe S35](../docs/capture/s35-dfe-objects-static-frontier.md),
`analysis/ghidra/s35-findings.json`; S31–S34 se conservan debajo como historial.

**S34 (18-10-2026), investigación de firmware:** tres BL a `0x43814ea0`
contrastados con el blob; direcciones → MMIO → kick 0/1 síncronos en Image.
Ruta VD_Sequence demostrada; selector permite categoría HS para dos productores,
sin demostrar factibilidad conjunta de cada modo/rama. Sin llamada directa desde
Post/Drive. El evento Drive `0x80` puede preceder Sequence o venir de timer 4:
no demuestra fin DMA. Registrador DFE de cuatro callbacks y cuatro conversiones
de causa resueltos; falta mapear bancos APL a causa/estado/callback y handle/VD.
Kick en `…0500` es +0x100 respecto de bancos `…0400`. Cuadro propio/siguiente
y cierre inicio-exposición/DMA/fin-exposición **NO_VERIFICADO**.
[Informe S34](../docs/capture/s34-apl-dma-vd-interrupts.md),
`analysis/ghidra/s34-findings.json` / `s34-audit.json`; proyecto/binario intactos.

**S33 (18-10-2026), investigación de firmware:** AllocShare completo y sus
26 llamadas YC cerradas estáticamente (12 funciones, 13 parámetros locales
inicializados a cero). `input+0x10` referencia handles de trabajo, varias rutas
AllocRendezvous; helper `0x43814ea0` puede activar `+0xc8` y escribir
`input+0xd4=P+0xbc` en tres productores (también se propaga por copia).
Rama APL seguida hasta palabras de extents y registros MMIO en bancos
`0xf3850400/0xf3950400/0xf3a50400`; el flag secundario es estado de software.
La palabra `handle+4` es clave conservada de la solicitud, no dirección raster
demostrada. Despacho Image dentro de VD_Sequence y publicación alternativa
desde HS_Sequence (`0x43790b68`). Pendientes: proveedor importado DMM
(`tabla+0x2e4`), productor que satisface Rendezvous, pitch/formato y fin DMA físico.
[Informe S33](../docs/capture/s33-yc-rendezvous-producer.md),
`analysis/ghidra/s33-audit.json`. Proyecto y binario sin cambios; sin cámara.

**S32 (18-10-2026), investigación de firmware:** continuó S31 sin ampliar la
arquitectura de conocimiento. Resueltos `0x43ad6034` (despachador), su thunk
`0x43ad6052`, el adaptador `0x43b03a48`, registradores
`0x4379704c`/`0x43797090` y seis destinos de las listas VD. Nueva rama
`0x4379b44c→0x4390366c` prepara referencias DMM compartidas en el bloque YC;
no es únicamente temporización. CORRECCIÓN de S31: «YC out window overflow»
se imprime en `0x4379cb2e`, dentro de `0x4379bb90`; es comparación temporal,
no finalización DMA. Falta el handle fuente efectivo (`input+0x10/+0xd4`),
su mapeo a píxeles/pitch/formato y la tupla del consumidor remoto.
Evidencia estática, sin cámara: [informe S32](../docs/capture/s32-vd-callbacks-sync-ycout.md)
y `analysis/ghidra/s32-findings.json`. El pendiente S31 descrito abajo es histórico
y queda actualizado por S32; la captura física sigue NO_VERIFICADO.

**Fase 12.11** (2026-10-18): tras cerrar la arquitectura del sistema de conocimiento
(instrucción explícita del usuario de no ampliarla más), se retomó la investigación
principal del shutter completamente electrónico.

1. `SetRead` IMX210 (0x436d7e08) decompilada íntegra vía Codex: no lee
   Silent+0x238/+0x280 ni produce buffer YC/DMA (ver `docs/capture/silent-imager-consumers.md`).
2. Corregida línea obsoleta en `CONTEXT.md`: el alta/callback de `0x50004` ya estaba
   cerrado desde S28, no pendiente.
3. Descartado, por ausencia total de cadenas `IMX210`/`exposure`/`SilentShutter`/`EFCS`
   en los 90+ `.ko` del firmware A6000, que el control del sensor viva en un módulo de
   kernel separado — refuerza que todo vive en `av-cam.bin`/librerías de servicio.
4. **Hallazgo S31** (`docs/capture/s31-camera-main-sync-strings.md`): subsistema
   `CAMERA_MAIN_SYNC`/`DFECore` en `av-cam.bin` — motor de temporización VD del sensor
   que ninguna sesión S16–S30 había explorado (todas se centraron en la capa de
   servicio libObj.so/libBizFw.so). Decompiladas 8 funciones clave vía Codex:
   `VD_Pre` (0x43792a0c) →evento 0x40→ `VD_Sequence` (0x4379155c) →evento 0x100→
   `VD_Post` (0x4379210c) →cola→ `VD_Drive` (0x4378f410); variante `EC_VD_Post`
   (0x4378f848) guarda el número de VD procesado en 0x43e992dc, comprobado por
   `int_LM_Send1st_Handler` (0x43792750); `camIntHandler0/1` (0x436cf954/0x436cf780)
   despachan causas de interrupción reales. **VERIFICADO: acceso MMIO real** a
   registros físicos 0xf3c30110–0xf3c3015c vía 0x436ccd9c→0x43ad6006. **PARCIAL:**
   `VD_Sequence→0x43796954→0x4379bb90` (SyncYCout.cpp) es el candidato más cercano
   al productor YC, pero no entrega dirección de píxeles/plano/pitch/fin DMA.
   **Pendiente exacto:** resolver los destinos de las llamadas indirectas vía
   `0x43ad6034` desde las listas de trabajo de `VD_Drive`/`VD_Post`.

**Fase 12.6** (2026-10-18): validación del grafo ampliado + rediseño del benchmark.
Encontrado y corregido un bug real: 840 relaciones CALLS duplicadas (misma función
reanalizada en varias sesiones JSON generaba una relación por archivo en vez de una sola
con procedencia múltiple) — ver `relation_sources` y `_upsert_call_relation` en
`build_graph.py`. Añadida distinción llamada directa vs. vía thunk de Ghidra.

## Bloqueadores reales / pendiente

- **Prueba de integración E2E completada** (2026-10-18, Fase 12.10): relación CALLS real
  con evidencia exacta confirmada (`AsyncProcessor::execute()`→`captureStart()`, callsite
  `0x108144`) y una relación inexistente correctamente NO inventada. Checkpoint de prueba
  escrito por Claude Code recuperado por una sesión nueva de Codex (`get_current_state`,
  sin leer `CONTEXT.md`/`PROGRESS.md`), que además localizó la evidencia original y
  distinguió un hallazgo VERIFICADO de una pregunta NO_VERIFICADO real. Prueba inversa
  (checkpoint de Codex recuperado por Claude Code) también confirmada. Contexto medido:
  recuperación de Claude Code ≈4024 caracteres / ~1006 tokens estimados; sesiones Codex
  completas reportaron 29 247 y 16 805 tokens reales (cifra de sesión, no de una sola
  llamada — no comparable 1:1 con la estimación de Claude Code). Checkpoints de prueba
  eliminados tras verificar. Detalle completo en `PROGRESS.md` Fase 12.10.
- **Codex ya tiene registrado el servidor MCP** (resuelto 2026-10-18, con autorización
  explícita del usuario): `~/.codex/config.toml` ahora define
  `[mcp_servers.sony-a6000-knowledge]` (python3 del `.venv` del proyecto +
  `scripts/knowledge/mcp_server.py`). Respaldo previo en
  `~/.codex/config.toml.bak-20261018T114752`. Detalle completo en `PROGRESS.md` Fase 12.9.
- **El servidor MCP `sony-a6000-knowledge` para Claude Code aparece "Pending approval"**
  en `claude mcp list` dentro de esta sesión no interactiva: requiere que el usuario lo
  apruebe desde una sesión `claude` interactiva. Mientras tanto, la verificación anterior
  usó la función Python real del servidor (misma lógica, mismo archivo) como sustituto.
- **Validación desde sesión interactiva nueva** (no `exec`, ni en Codex ni en Claude Code):
  lo verificado arriba usa `codex exec` (no interactivo) y la función Python directa; el
  descubrimiento en el modo interactivo normal de cada cliente sigue sin confirmación
  externa del usuario.
- Mapeo de lenguaje natural a nodo de `trace` (p. ej. "¿qué llama a 0x50004?") sigue siendo
  manual: hay que ubicar el nodo primero con `search.py exact`.

**Siguiente objetivo (indicado por el usuario):** no ampliar más esta arquitectura salvo
defecto importante; volver a la investigación principal — captura completamente
electrónica en Sony A6000 — reutilizando las evidencias existentes.

## Siguiente acción sugerida

Ver "Próximo paso exacto" al final de `knowledge/PROGRESS.md`.

## S300 — barrido único de xrefs al state IMX210 (22-10-2026, agente B)

67 sitios únicos (15 xrefs a `0x43f72d02` + 42 al slot GOT `0x4401f990` + 16 lecturas de gates):
56 lectura, 6 escritura, 3 spill, 1 propagación, 1 dato. **Ningún escritor de `+3`/`+6`**; los gates
se leen como bitfield de 7 bits + signo en `FUN_43858338` (8 lectores cada uno). Únicos stores:
`+0x00` (`0x4383ac90`) y `+0x02` (4 instrucciones en `FUN_43833ff8`/`FUN_4383ace0`/`FUN_4383b2dc`).
Solo dos literales absolutos con el puntero en todo el blob: `0x4401f990` y `0x43ff3248`. Corrige el
sesgo +0x58 de la rev.1 (commit `75f5fa28`) y deja S176 como no reutilizable (artefactos ausentes).
[S300](../docs/capture/s300-state-xref-sweep.md), `analysis/s300_state_xref_sweep/state_xref_sweep.json`
(4 tests + 7 del test previo). Límite: estático, sin runtime/DMA/índice dinámico.

**Siguiente:** S301, mismo barrido en la A7S fw3.20 y tabla de diferencias.

## S301 — barrido A7S fw3.20 y diferencias con la A6000 (22-10-2026, agente B)

Estado A7S localizado en `0x43f7bce6` (slot GOT `0x440251e4`, entrada de tabla `0x43ff928c`),
derivado del dumper homólogo `0x437e0974` (patrón de gate idéntico). 79 sitios: 65 lectura,
8 escritura, 4 spill, 1 propagación, 1 dato. **Gates `+3`/`+6` idénticos** (código del dumper
semánticamente igual; solo cambian los pools) y sin escritores en ambas cámaras → no son el
mecanismo del silent shutter. Diferencias: la A7S escribe `+0xde` (`0x4386521a`) y el trío
`+0xe6/+0xe8/+0xea` (`0x438643a6/b2/bc`, divisiones ×10), y lee 11 campos que la A6000 no
(`+0x47,+0x60,+0x61,+0x6d,+0xae,+0xde,+0xdf,+0xe0,+0xe2,+0xe4,+0xe6`); la A6000 solo lee
`+0x7f`. Homología del objeto: INFERENCIA fuerte (índice 18 en la tabla, mismo rol). Semántica
del clúster: NO_VERIFICADA. [S301](../docs/capture/s301-a7s-state-xref-sweep.md).

**Siguiente:** S302, tablas de drive mode/exposición A7S↔A6000 campo a campo (S124/S134/S140).

## S302 — drive mode y exposición A7S↔A6000 (22-10-2026, agente B)

Misma estructura, offsets desplazados: guard `0xd70`→`0xd78`, `shut` `0x1f8`→`0x200`, `VdNum`
`+0xcc`→`+0xd8`, `svr_num` `+0x14e`→`+0x15e`; bloque de parámetros 4→3 palabras. A7S añade
selector textual `0x43826d58` (`tipo==2`→`0x4e/0x4f`) e indirección modo→columna con 34 códigos
(`0x43fee370`) y mapa `0x43c9c5b5` sobre 69 filas×16 B; A6000 usa columna directa sobre 59 filas
(`0x43fe9b74`). **Hallazgo:** mapa[0x4c..0x4f]=1 → los modos silent comparten columna de registro
con `0x4c/0x4d`; discrepancia con S204 marcada para re-verificar (no se edita CORRECTIONS).
[S302](../docs/capture/s302-drive-modes.md), `analysis/s302_drive_modes/compare.json` (4 tests).

**Siguiente:** S303, árbol de referencias de la tabla `0x43ff3200` y alcanzabilidad de callers de
`FUN_43858338`.

## S303 — árbol de la tabla 0x43ff3200 y callers del dumper (22-10-2026, agente B, rev.2)

Tabla `0x43ff3200`: **148** punteros únicos a objetos BSS (no 60), terminador `0x43ff3450`,
estado en índice 18 (`0x43ff3248`). Único literal de la base: slot GOT `0x4401f080`. Sin xrefs
por entrada (acceso indexado). Dumper `FUN_43858338`: **2** callers directos
(`0x43859868`/`0x43859892` en `FUN_43859710`); éste recibe 10 llamadas de 7 funciones y
`FUN_43859944` tiene 35. `0x437b617e` sin callers directos (negativo local). **Corrige** el sesgo
+0x58 de S303rev1/S304 (`0x438581e8`/`0x43858390` no son entradas). Alcanzabilidad runtime
NO_VERIFICADA; usuarios del GOT `0x4401f080` pendientes (S305). [S303](../docs/capture/s303-ref-tree-43ff3200.md),
`analysis/s303_ref_tree/ref_tree.json` (4 tests).

Rev.3 añade el contraste con REA: `procedure_callers` confirma 1 función para el dumper y 5 para el caller; el slot `0x4401f080` es **invisible** para REA (`undecodable`, 0 xrefs) y se localiza por bytes en `0x4378bb6c` (`GOT base 0x4401eee4 + 0x19c`), que lo pasa a una ruta de log. 3 sitios caen en huecos de cuerpo de Ghidra. **Siguiente:** desambiguar los 40 `add.w #0x19c` o pasar a los writers del clúster `+0xde..+0xea` de la A7S.

## S307 — el cluster A7S `+0xde`/`+0xe6..+0xea` está en código ausente en la A6000 (22-10-2026, agente B)

Firmas de 24 B alrededor de cada store: `+0xde` (`0x4386521a`) y `+0xe6/+0xe8/+0xea`
(`0x438643a6/b2/bc`) dan **0 coincidencias** en la A6000; dos escritores de `+0x02`
(`FUN_4385352c`, `FUN_4385a384`) también. Los stores a `+0x00` y uno de `+0x02` sí existen en la
A6000. `FUN_438645bc` (lee `+0xae`×1000, llama a los escritores) tiene **un** caller directo (`0x43861be4`)
y ningún puntero; la entrada correcta es `bc`, no `be` (corregido en S308). El selector silent
`0x43826d58` solo tiene 2 callers (`0x4354908c`, `0x43826df2`) y ninguno llama a este bloque: la
conexión modo→tiempos queda NO_VERIFICADA. [S307](../docs/capture/s307-a7s-only-writers.md),
`analysis/s307_a7s_writers/writers.json` (4 tests).

**Siguiente:** identificar la entrada indirecta de `FUN_438645be` (tabla de punteros/estructura) o
seguir `0x4354908c` (caller del selector) para cerrar el flujo del modo silent.

## S308 — flujo del selector silent y entrada del bloque de tiempos (22-10-2026, agente B)

El resultado del selector `0x43826d58` se guarda en `[sp+0x2c]` (`0x43549098`) y se pasa a
`0x43ad9704` (`0x435490c4`), un **thunk de llamada virtual** (S310: `vtable+0x64`): **no** va directo al bloque
de tiempos. El bloque es `FUN_438645bc` (S307 decía `…be`: corregido) con **un** caller directo,
`0x43861be4` (ruta de configuración: buffer 0x70 B + variante 1/2). Solo hay 4 punteros a
`0x43864xxx` y ninguno apunta al bloque. El enlace silent→tiempos sigue **NO_VERIFICADO**; el
siguiente paso es el consumidor de `0x43ad9704`. [S308](../docs/capture/s308-silent-flow.md),
`analysis/s308_silent_flow/flow.json` (3 tests).

**Siguiente:** consumidor de la estructura de `0x43ad9704` (dónde se lee el modo 0x4e/0x4f).

## S309 — la cadena silent/config de la A7S no está en la A6000 (22-10-2026, agente B)

Siete funciones (`0x43548c70` caller, `0x43826d58` selector, `0x43ad96fa` mensaje,
`0x43861a58` config, `0x438645bc` tiempos, `0x438642f0` trío, `0x43865100` `+0xde`): **0
coincidencias** de sus primeros 24 B en la A6000. Una firma de 12 B de `0x438642f0` sí aparecía,
pero era un prólogo genérico; con 24 B desaparece. Implica que la diferencia es código ausente,
no un valor distinto; la A6000 tiene su propia ruta de configuración (escribe `+0x02` desde 4
funciones, S300). Límite: no descarta una reescritura equivalente. [S309](../docs/capture/s309-chain-presence.md),
`analysis/s309_chain_presence/presence.json` (3 tests).

**Siguiente:** comparar la ruta de configuración propia de la A6000 (writers de `+0x02`) o el
consumidor del mensaje de `0x43ad96fa`.

## S310 — `0x43ad9704` es un thunk de llamada virtual (22-10-2026, agente B)

`0x43ad96fa`/`0x43ad9704` son thunks `obj->vtable[slot](...)`; la familia contigua usa slots
`0x64, 0x94, 0x58, 0x74, 0x40, 0x18`. El modo silent se pasa como argumento de una llamada
virtual (`vtable+0x64`), no a un “mensaje”. El consumidor real depende del objeto/vtable y queda
**NO_VERIFICADO**; corrige la descripción de S308. [S310](../docs/capture/s310-vtable-thunk.md),
`analysis/s310_vtable_thunk/thunk.json` (3 tests).

**Siguiente:** identificar el objeto/vtable de `r0` en `0x43549084` (constructor o RTTI) para
resolver el slot 0x64, o cerrar el carril con el estado actual.
