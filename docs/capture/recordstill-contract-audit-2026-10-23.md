# Auditoría de contrato RecordStill / RecordImage (23-10-2026)

## Resultado y alcance

**RECHAZO** la equivalencia entre A7S `0x847e1c` y A6000 `0x90b248`.
La etiqueta histórica `RecordStill::Execute` de S380–S385 para `0x90b248`
no está sustentada por un símbolo C++: el cuerpo se identifica internamente como
**RecordImage**. La candidata A7S es **RecordStill**, un helper llamado desde
RecordImage. Son niveles distintos del mismo flujo.

Este informe **CORRIGE** [S382](s382-recordstill-callers.md) y
[S385](s385-libobj-a6000-vs-a7s-diff.md), incluidos los nombres y negativos
históricos que sobreviven en resúmenes anteriores. No cambia S51.

Las direcciones siguientes son VA del ELF, intervalos semiabiertos `[inicio, fin)`.
Identidad de los archivos `libObj.so`, SHA-256:

- A6000 fw3.21: `8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a`.
- A7S fw3.20: `084d4c3a2a7730c919c5059e1caeb0551b52ccb653f5c4fb945358727a2c4f65`.

## Contrato y cuerpo contrastados

| Aspecto | A7S `0x847e1c` | A6000 `0x90b248` |
|---|---|---|
| Traza de entrada | ` RecordStill :` | ` RecordImage :` |
| Nombre en diagnósticos | `RecordStill` | `RecordImage` |
| Reserva local de stack | `0x358` (+ `0x20` guardado) | `0xb04` (+ `0x24` guardado) |
| Entradas utilizadas | `r0`, `r1`, `r2`, `r3`, palabra en SP de entrada | objeto en `r0`, mensaje en `r1`; no usa `r2/r3` entrantes antes de redefinirlos |
| Operación inicial | `GetParam` de `0x1001`, `0x1002`, `0x100e`, después `0x1007/0x1006` | helper `0x910e1c`; si éxito, crea Struct de `0x28` bytes y `AddParam(0x100f)` |
| Operación posterior | conversión de fechas, metadatos, llamada `0x83c9a0` y limpieza | prepara captura/Exif y llama a su helper RecordStill en `0x90bbdc` |
| Retorno normal | `r0=r5` en `0x8480f8`, antes del epílogo | `r0=r5` en `0x90beaa`, antes del epílogo |

**Hechos de ABI:** en A7S `0x847e32: 92 46` preserva `r2` en `sl`;
`0x847e34: 98 46` preserva `r3` en `r8`;
`0x847e36: d7 f8 70 93` carga `sb,[r7,#0x370]`.
Como `r7=SP_actual+8` y el marco total mide `0x378`, esa carga consume
el quinto argumento desde el SP de entrada. Los tipos exactos de los argumentos
3–5 siguen siendo inferencias; no se inventa una firma C++.

En A6000 `0x90b2a4: 41 f2 0f 01` es `movw r1,#0x100f`;
`0x90b2aa` llama a `MWF::ObjMsg::AddParam` por PLT `0xe01a8`.
La diferencia de contratos se apoya en flujo de registros y llamadas, además de cadenas.
El retorno transmite un resultado de software; no demuestra persistencia física
ni terminación de una exposición. Su tipo C++ y el significado de cada código no se presuponen.

## Referencias a cadenas: cálculo comprobable

LDR literal usa `Align(PC+4,4)`; el ADD posterior usa su propio `PC+4`.
Se lee la palabra del pool mediante PT_LOAD y se suma módulo `2^32`.

| Modelo / carga | Pool / palabra | ADD | Cadena resultante |
|---|---|---|---|
| A7S `0x847e26` | `0x848104` / `0x0046f0f7` | `0x847e30` | `0xcb6f2b`: ` RecordStill :` |
| A7S `0x847f4e` | `0x84811c` / `0x0046fc65` | `0x847f52` | `0xcb7bbb`: `RecordStill` |
| A6000 `0x90b254` | `0x90b730` / `0x004d419c` | `0x90b25c` | `0xddf3fc`: ` RecordImage :` |
| A6000 `0x90b310` | `0x90b738` / `0x004d4a58` | `0x90b316` | `0xddfd72`: `RecordImage` |

Las otras cinco referencias A7S a `RecordStill` son `0x847f60`, `0x847fd6`,
`0x847fe8`, `0x848018`, `0x84803a`. Los diagnósticos también apuntan a
`ObjStillRecorderCore.cpp` (`0xcb84db` A7S, `0xde2f8f` A6000).
Estos nombres identifican el contexto de código; no son símbolos exportados del método.

## Límites y parejas correctas

| Contexto | A6000 | A7S |
|---|---|---|
| RecordStill | `0x908afc..0x908e2c` | `0x847e1c..0x84814c` |
| RecordImage | `0x90b248..0x90c088` | `0x84a568..0x84b3a8` |

Son intervalos entre entradas `.ARM.exidx` PREL31, corroborados por prólogos,
retornos y referencias locales. Un intervalo unwind puede incluir pools, tablas
y bloques de excepción; no equivale por sí solo a una lista exacta de instrucciones.
En A7S RecordStill el código rectilíneo decodificable termina con
`0x848100: bd e8 f0 87` (`pop.w {...,pc}`), pool `0x848104..0x84814c`,
y nuevo prólogo `0x84814c: 2d e9 f0 41`.
En A6000 RecordImage hay pools interiores y bloques posteriores que vuelven atrás;
no se corta la función en el primer pool/retorno encontrado.

**Hecho estructural:** las 260 instrucciones de RecordStill, desde cada entrada
hasta el retorno incluido (`0x2e8` bytes), tienen idénticos offsets, tamaños y
mnemónicos. Los bytes solo difieren en **43 BL/BLX** y **seis inmediatos de
diagnóstico en r3**, que aumentan nueve unidades en A7S. El test enumera esas
excepciones; no oculta otras diferencias ni incluye el pool como código.

**Inferencia fuerte de homología**, no demostración de equivalencia de todos los
callees ni del comportamiento físico. RecordImage A7S tiene también
`movw r1,#0x100f` en `0x84a5c4` y AddParam en `0x84a5ca`:
el negativo histórico «cero MOVW 0x100f en A7S» queda **RECHAZADO**.

La relación entre niveles queda comprobada por dos BL con los mismos bytes
`fc f7 8e ff`: A6000 `0x90bbdc → 0x908afc`; A7S
`0x84aefc → 0x847e1c`. Los 16 bytes previos de preparación de argumentos son
idénticos; incluyen la quinta entrada almacenada en `[sp]`.

## Llamadores A6000 y búsqueda indirecta

**ACEPTO** ambos BL a `0x90b248`:

| Sitio / bytes | Intervalo contenedor | Entradas observadas |
|---|---|---|
| `0x90de2e` / `fd f7 0b fa` | `0x90d7e8..0x90e148` | entrada `r0=mensaje`, `r1=contexto`; conserva en `r6/r4`; al BL `r0=r4,r1=r6` |
| `0x91634e` / `f4 f7 7b ff` | `0x9162d0..0x91647c` | entrada `r0=contexto`, `r1=mensaje`; conserva en `r4/r6`; al BL `r0=r4,r1=r6` |

El significado objeto/mensaje se infiere del uso (`GetMessageId` y campos de objeto).
`0x90de2c` es un bloque interior. **RECHAZO** `0x91631e` como entrada:
`0x916316: df e8 00 f0` es `tbb [pc,r0]`; los 13 bytes
`07 6d 12 1d 6d 27 32 6d 6d 3d 6d 4f 61` en `0x91631a` son su tabla.
El índice procede de `GetMessageId - 0x10000003`, limitado a `0xc`.
Para `0x10000005`, índice 2, `0x91631a + 2*0x12 = 0x91633e` conduce al BL.

**ACEPTO el consumidor indirecto.** La tabla `StateMgr::_FuncEntry` empieza en
`0x101ef0c` y ocupa `0x258` bytes: 25 filas de `0x18` bytes. Sus campos son
`{estado_actual, id_mensaje, check_fn, call_fn, next_state_fn, estado_siguiente}`.
Las 25 palabras `call_fn` son `0x90d7e9` (bit Thumb incluido), en
`0x101ef18 + n*0x18`, `n=0..24`, con relocación `R_ARM_RELATIVE` (23).
La primera fila es `[0,0x10000003,0x907ba1,0x90d7e9,0x907c95,1]`;
la fila 22, en `0x101f11c`, es para estado 2 y mensaje `0x10000005`.

En `libObj.so`, `0x91776e/0x91777a` resuelven la base `0x101ef0c`;
`0x917770` fija tamaño `0x258`, `0x91777c` llama a `memcpy` y
`0x917782/0x917786` pasan 25 filas a `StateMgr::AddEntry`. El gestor se
guarda en `ObjStillRecorder+0x8c` (`0x917774`). La entrada de objeto
`0x916650` llama a `0x919908` (`0x916676`); el manejador obtiene el ID del
mensaje y llama a `StateMgr::ChangeState` con el gestor (`0x919bd4/0x919bdc`).

En `libmprctrl.so`, `StateMgr::ChangeState` (`0x1cf18`) recorre filas de
`0x18` bytes, compara estado e ID (`0x1cf52..0x1cf62`), ejecuta `check_fn`
si existe y pasa la fila a `StateMgr::CallFunc` (`0x1cf7e`). Este último
lee `call_fn` en `fila+0xc` (`0x1ceea`) y hace **`blx r3` en `0x1cef2`**.
Así queda demostrado el consumo de los 25 punteros hacia `0x90d7e8`, cuyo
BL interior `0x90de2e` alcanza RecordImage para el caso `0x10000005`.
La activación concreta en una cámara y los estados observados en ejecución
siguen **NO_VERIFICADO**; el flujo estático no acredita ejecución física.

**Negativos acotados:** no aparecen las palabras exactas `0x90b248/0x90b249`
ni `0x9162d0/0x9162d1` en PT_LOAD respaldado por archivo. Eso no excluye
direcciones calculadas, tablas relativas, punteros creados en runtime, veneers
ni despachos externos. No se interpreta un resultado vacío como ausencia de llamadas.
La VA `0x101ef18` corresponde al offset de archivo `0x1016f18`; no son intercambiables.

## Método y validación

REA primero: consultas de función, xrefs y contención sobre la candidata A7S;
función y xrefs excedieron 300 s cada una. Contención de `0x84803a` devolvió
`found=false/not_in_procedure`, evidencia
`ev_f9469adfd014e220f5ba584ee0fe69f0892a8570cfdb1b9ab06cd6188c6b333b`.
No se reconciliaron esas coordenadas con la base de carga del proveedor:
el resultado no prueba ausencia de la función ELF. Se conserva la respuesta en
`analysis/s380_libobj_map/rea_recordstill_coverage.json`.
Un intento local restringido devolvió `provider_unavailable/runtime_missing`.
El reintento local con JDK existente se cerró durante autoanálisis tras más de
diez minutos; no aportó un dossier utilizable. Ambas sesiones se cerraron.
Los contratos y límites aquí afirmados proceden del contraste estático siguiente,
no de una decompilación REA que no se obtuvo. Sin instalaciones.
En esta ampliación, REA abrió `libObj.so` pero la consulta de segmentos superó
300 s; se contrastaron directamente `libObj.so` y el símbolo exportado
`StateMgr::CallFunc` de `libmprctrl.so` con bytes y dos decodificadores.
El contraste decisivo usa bytes, PREL31 y LLVM `llvm-objdump --triple=thumbv7-linux-gnueabi`,
con Capstone como segundo decodificador. No se cuenta REA/Ghidra como motores independientes.

Regresiones: `analysis/s380_libobj_map/tests/test_recordimage_contract.py`;
lector reproducible: `analysis/s380_libobj_map/recordimage_audit.py`.
La suite S380 completa pasa **54 tests**; los 33 tests relevantes de índice,
grafo y exportación también pasan.
Ruff y mypy pasan en los cuatro Python tocados; mypy de `src` pasa.
Los 397 avisos Ruff de `src/tests` están en archivos no modificados.
Los antiguos tests de ventanas dejan
de llamar «funciones contenedoras» a bloques y ahora exigen un operando BL inmediato,
sin posibilidad de aprobar por un bucle que no encuentra operandos.

Sin firmware ejecutado, cámara, flasheo ni validación física. No se atribuye
obturador electrónico a este flujo de grabación ni se resuelve `0x40193`.
