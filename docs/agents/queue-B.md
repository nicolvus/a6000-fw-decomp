# Cola carril B (DeepSeek) — imager: estado, drive modes y gates (S300+) (estado: TODO | DOING | DONE <hash> | BLOCKED <causa>)

- DONE S300 Barrido único de xrefs a `0x43f72d02` (GOT `0x4401f990`) en A6000: total, tabla clasificada (spill/lectura/escritura/propagación) en `analysis/s300_state_xref_sweep/`; veredicto sobre writers de `+3`/`+6`. **Evidencia**: `docs/capture/s300-state-xref-sweep.md`, `analysis/s300_state_xref_sweep/xrefs_classified.json`, 7 tests verdes.

- DONE S303 (rev.2) Árbol de referencias de `0x43ff3200`: **148** entradas (no 60), terminador `0x43ff3450`, estado en índice 18; único literal de la base en GOT `0x4401f080`. Callers del dumper: **2** (`0x43859868`/`0x43859892` en `FUN_43859710`), 10 callers de éste en 7 funciones, `FUN_43859944` con 35. Corrige el sesgo +0x58 de S303rev1/S304. Evidencia: `docs/capture/s303-ref-tree-43ff3200.md`, `analysis/s303_ref_tree/ref_tree.json` (4 tests).

- SUPERSEDED S302 (rev.1 por otro proceso) `docs/capture/s302-drive-mode-exposure-tables.md`: reemplazado por la rev.2 `docs/capture/s302-drive-modes.md`, que aporta offsets verificados y la matriz 59/69 filas.

- SUPERSEDED S304 (rev.1) por S303 rev.2: `0x438581e8` y `0x43858390` son entradas reales +0x58 (interiores de `FUN_43858190` y `FUN_43858338`), y las «13 llamadas» son instrucciones internas. Ver §5 de `docs/capture/s303-ref-tree-43ff3200.md`.

- DONE S300 (rev.2 `b2f5ff12`) barrido completo y corregido (ver arriba).

- TODO S305 (rev.1, superseded) Analizar `FUN_43858390` por tramos y buscar el literal pool `0x4401f080`. **SUPERSEDED**: la base `0x43858390` es `FUN_43858338+0x58` (no es una función); ver S303 rev.2 §5. El literal del slot ya está localizado (`0x4401f080` → `0x43ff3200`).

- DONE S301 (`ef9ec487`) Barrido A7S fw3.20: estado `0x43f7bce6`, 79 sitios, gates idénticos sin escritores; A7S escribe `+0xde`/`+0xe6`/`+0xe8`/`+0xea` y lee 11 campos que la A6000 no. Evidencia: `docs/capture/s301-a7s-state-xref-sweep.md`, `analysis/s301_a7s_state_xref_sweep/state_xref_sweep.json` (4 tests).

- DONE S302 (`393472ef`) Drive mode/exposición campo a campo: offsets desplazados (ctx +8, VdNum +0xc, svr_num +0x10), bloque 4→3 palabras; matriz A6000 59×16 vs A7S 69×16 con 34 códigos y mapa modo→columna; modos silent comparten columna con 0x4c/0x4d. Evidencia: `docs/capture/s302-drive-modes.md`, `analysis/s302_drive_modes/compare.json` (4 tests).

- DONE S306 (cubierto en S303 rev.3 §2b) Usuarios del slot `0x4401f080`: REA devuelve `undecodable`/0 xrefs (no prueba ausencia); por bytes, `0x4378bb6c` lo carga con `GOT base 0x4401eee4 + 0x19c` y lo pasa a `0x435613e8`. `procedure_callers` valida 1 función para el dumper y 5 para `FUN_43859710`.
 (fix(B): S303 rev.2 arbol real de 0x43ff3200 y callers del dumper)

- DONE S314 Procedencia real del selector y tabla `0x43fee3f8`: en `0x43549084` se carga **`r1`** (`[ctx+8]+0x21c`), no `r0`; el thunk del slot `0x64` es `0x43ad96f8` (no `0x43ad9704`, que va a `0x43ad9ada` y usa `vtable+0x24`). `ctx=0x43ea70a0` (getter `0x437b38ec`), sin escritor estático de `[ctx]`/`[ctx+8]`. Selector: `c==2 && b∈{0,1}` → `0x4e/0x4f`. Tabla `0x43fee3f8`: **95** registros de 6 B (`dev|0|reg:u16|data:u8|0`, 94×`0x81`, 1×`0x83`), terminador `0x43fee574`; la cifra «19 filas» no es reproducible. A6000: 0 apariciones del par `+0x21c/+0x220` y otra tabla en la misma VA (71 punteros, terminador `0x43fee41c`). Evidencia: `docs/capture/s314-selector-object.md`, `analysis/s314_selector_object/selector.json` (58 comprobaciones de `verify_selector.py`, 10 tests).

- TODO S315 Seguir la lista de 95 registros hasta el formateador: callers/reachability de `0x436f44c4` y `0x436f25f0` (registro→trama), comparar con la tabla A6000 de 71 entradas (`0x43fee300..0x43fee418`) y decidir si el modo silent usa una lista distinta (p. ej. la de `0x43fee578`/`0x43fee590`).

- BACKLOG S316 (si S315 no cierra): identificar índice/consumidor de las 68 filas de `0x43fee5ac` (`{ptr,16 B}`) y su relación con los 69 drive modes de S302.
- BACKLOG S317: resolver constructor/vtable de `[0x43e8dd98]` (objeto de `0x43ad9704`) o documentar la frontera cross-module con evidencia de ausencia local.

- DONE S315 Tres listas de registros aplicadas por `0x436f44c4(obj,modo,lista)`: **L95** `0x43fee3f8` (95) con `modo 2` en `0x436f5b32`; **L5** `0x43fee578` (5: regs `0x5f,0x61,0x88,0x94,0xe3`) con `modo 0` en `0x436f5b52`; **L1** `0x43fee590` (reg `0x00`, data `0x04`) con `modo 2` en `0x436f5422`. Getter `0x436f4588` → GOT `0x4402c940` → L95; slots `0x44025ec0`→L5 y `0x440292b0`→L1. L5 **no** es subconjunto de L95. Consumidor/getter/llamadas con **0 firmas** en la A6000. El enlace `modo 2`→silent sigue NO_VERIFICADO. Evidencia: `docs/capture/s315-register-lists.md`, `analysis/s315_register_lists/lists.json` (139 comprobaciones, 8 tests).

- TODO S316 Identificar el origen/escritor de las tres listas y del selector de modo: quién elige `modo 0/2` en `0x436f44c4` (callers de `0x436f53f4`/`0x436f5a14` y campo `+0x1b0/+0x1ac`), y si el modo silent usa L95/L5/L1 en runtime.

- BACKLOG S317 Identificar índice/consumidor de las 68 filas de `0x43fee5ac` (`{ptr,16 B}`) y su relación con los drive modes (S302).
- BACKLOG S318 Resolver constructor/vtable de `[0x43e8dd98]` (objeto de `0x43ad9704`) o documentar la frontera cross-module.

- DONE S316 Clase dueña de las listas: constructor `0x436f27b4` (vptr `0x43fce050` desde GOT `0x4402ac80`=`0x43fce048`), metadata de vtable `0x43fce048` (offset-to-top 0, typeinfo `0x43feeb20`), **45** entradas `0x43fce050..0x43fce100`, terminador `0x43fce104`. Métodos de listas en slots `+0x38` (`0x436f5a14`) y `+0x44` (`0x436f53f4`); wrapper de creación/registro `0x43ad9840` en slot `+0x04`. Campos `+0x1ac/+0x1b0/+0x2b4/+0x2dc/+0x394/+0x3dc` documentados. **0 firmas** en la A6000. Evidencia: `docs/capture/s316-class-vtable.md`, `analysis/s316_class_vtable/class.json` (81 comprobaciones, 6 tests).

- TODO S317 Identificar la tabla indexada por `obj+0x2b4` (`ldr r0,[r3,r2,lsl#2]` en `0x436f4546`) y comprobar si es la tabla de 34 códigos de S302 (`0x43fee370`) o la de 68 filas de `0x43fee5ac`; después, quién escribe `+0x1b0/+0x1ac` (`0x11`) para cerrar la selección de modo.

- BACKLOG S318 Resolver constructor/vtable de `[0x43e8dd98]` (objeto de `0x43ad9704`) o documentar la frontera cross-module.
- BACKLOG S319 Cerrar la frontera del `ctx` `0x43ea70a0`: buscar en módulos hermanos (`liro.ko`, `libObj.so`) el escritor de `[ctx]`/`[ctx+8]`.

- DONE S317 `obj+0x2b4` indexa **tres tablas paralelas** de stride `0x1c` (`0x436f618c`): T1 `0x43bbeb70` (→`obj+0x16`), T2 `0x43bbf2ec` (→`obj+0x2e`), T3 `0x43bbef34` (→`obj+0xa5`); campos `u32 +0x14`, `u16 +0x18`; `T3→T2 = 34` filas exactas, `T1→T3 = 0x3c4`. Base calculada con PC=(add+4) bit0=0 (REA/Ghidra y tablas de enum 1/2 confirman la lectura). 111 sitios `str [#0x2b4]` no atribuibles; entrada exclusiva A7S. Evidencia: `docs/capture/s317-mode-tables.md`, `analysis/s317_mode_tables/mode_tables.json` (39 comprobaciones, 6 tests).

- TODO S318 Resolver la alineación real y el rango de las tablas de `+0x2b4` con REA/Ghidra (tipos de datos en `0x43bbeb70..`) y buscar el escritor de `+0x2b4` para esta clase (xrefs al campo desde métodos propios).

- BACKLOG S319 Cerrar la frontera del `ctx` `0x43ea70a0`: buscar en módulos hermanos (`liro.ko`, `libObj.so`) el escritor de `[ctx]`/`[ctx+8]`.
- BACKLOG S320 Identificar la tabla de 68 filas `0x43fee5ac` y su relación con los drive modes (S302).

- DONE S318 Constructor paramétrico `0x436f3fc0(obj,idx)`: mismo vptr `0x43fce050`, tabla `0x43bbe1cc` indexada con `idx` (4 B), mapeo `0x43ad9162` (`1→0x10`, `2→0x40`, otro→1) en `obj+0x2dc`. Único llamador `0x436f2a8a` con `idx=0`; tabla homogénea solo hasta el índice 6 (desde 7 empaqueta dos `u16`), rango válido NO_VERIFICADO. 0 firmas en A6000. REA confirmó pseudo-código y `xrefs(0x4402ac80)` = `0x436f27be`,`0x436f3fda`. Evidencia: `docs/capture/s318-ctor-mode.md`, `analysis/s318_ctor_mode/ctor_mode.json` (24 comprobaciones, 6 tests).

- TODO S319 Cerrar la frontera del `ctx` `0x43ea70a0` (corregido +2): buscar en módulos hermanos (`liro.ko`, `libObj.so`) el escritor de `[ctx]`/`[ctx+8]` o documentar la ausencia con barrido de literales en esos binarios.

- BACKLOG S320 Identificar la tabla de 68 filas `0x43fee5ac` y su relación con los drive modes (S302).

- DONE S319 Frontera del `ctx 0x43ea70a0` (corregido +2): 40 sitios `ldr/add pc` (31 lectura, 1 store a `+0x44`, 3 arg, 5 indirectos), **0 stores a `[ctx]`/`[ctx+8]`**; 0 literales absolutos en `av-cam` y en `kmod/*`/`lib/*`. Veredicto **NO_VERIFICADO** (la ausencia no prueba ausencia cross-module; candidatos `0x437c7b0c`/`0x437ca5c8`). Evidencia: `docs/capture/s319-ctx-boundary.md`, `analysis/s319_ctx_boundary/ctx_boundary.json` (16 comprobaciones, 5 tests).

- TODO S320 Seguir los candidatos que reciben `ctx` como argumento (`0x437c7b0c`→`0x437c83e8`, `0x437ca5c8`) para localizar el escritor de `[ctx]`/`[ctx+8]`, o cerrar la frontera con un barrido de `memcpy`/`stm` con destino `ctx` en todo el blob.

- BACKLOG S321 Identificar la tabla de 68 filas `0x43fee5ac` y su relación con los drive modes (S302).

- DONE S320 Los aplicadores de listas usan la **misma trama**: `0x43ad968a` (modo !=2) y `0x436f25f0` (modo 2) comparten 7 instrucciones y el formateador `0x43ad9666`; modo 2 añade un reintento (`r0==2` → `0x43ad92e6`, segundo intento y log). El modo elige la lista, no la trama. 0 firmas en A6000. Evidencia: `docs/capture/s320-frame-retry.md`, `analysis/s320_frame_retry/frames.json` (20 comprobaciones, 5 tests).

- TODO S321 Identificar la tabla de 68 filas `0x43fee5ac` (`{ptr,16 B}`) y su relación con los drive modes (S302); buscar su índice/consumidor.

- BACKLOG S322 Decodificar el contenido de la trama en `0x43ad9666`→`0x43ad9628`/`0x436f2554` (formato de registro y cabecera).

- DONE S321 `0x43fee5ac` es la fila 1, no la base: matriz real `0x43fee598`, 69 filas `{u32 destino; u8 valores[16]}`, terminador `0x43feeafc`; **0** referencias de código a `0x43fee5ac`. Consumidor `0x436f3928` (vtable `0x43fce050`, slot `+0xa0`) hace `*(u8*)destino = valores[mapa[modo]]` con mapa `0x43c9c5b5` (82 B, columnas 0..14; la 15 sin uso). Los 69 destinos son el byte `data` (registro+4) de 69 de los **98** registros contiguos de 6 B `{dev,0,reg,data,0}` del pool `0x44021ec2..0x44022108` (97×`0x81`, 1×`0x83` = `0x440220d8` reg `0x17`); 29 no se tocan. 66 destinos están en L95 y 3 solo en L5 (`0x44022018`/`0x44022072`/`0x44022090`); L5 = esos 4 fuera de L95 + `0x4402204e`, y L1 = `L95[0]`. A6000: misma clase (vtable `0x43fcc090`, 45 entradas), slot 40 `0x436d6570`, matriz `0x43fe9b74` (59 filas), registros de **4 B** `{reg:u16,data,0}` y **sin** mapa (columna directa); segunda matriz en ambos casos a cero (puertas `+0x2b0` A7S / `+0x266` A6000). `0x4e`/`0x4f` comparten la columna 1 con otros 35 códigos → sin columna silent exclusiva. Evidencia: `docs/capture/s321-matrix-rows.md`, `analysis/s321_matrix_rows/matrix_rows.json` (138 comprobaciones, 14 tests).

- TODO S322 Decodificar el contenido de la trama en `0x43ad9666`→`0x43ad9628`/`0x436f2554` (formato de registro y cabecera).

- DONE S322 Trama A7S byte-alineada `81|03|device|address8|data8`; 1200/1200 tramas de 12 escenarios S58 reproducen los registros, una trama por registro. `0x43ad9666` devuelve 0/1/2 (éxito/rechazo/sin espacio); modo 2 conserva formato y solo reintenta. Evidencia: `docs/capture/s322-frame-format.md`, `analysis/s322_frame_format/frame_format.json` (1282 comprobaciones, 6 tests).

- DONE S323/S328 La segunda matriz (slot `0x44026088` A7S / `0x44026694` A6000) apunta a una tabla **a cero** (`0x43e8de00`/`0x43e80160`); su offset solo lo usa el bucle del accesor y no hay store estatico. Primera palabra 0 = terminador → **el segundo bucle no ejecuta**. Productor runtime (otro modulo/DMA) NO_VERIFICADO. Evidencia: `docs/capture/s328-second-matrix.md`, `analysis/s328_second_matrix/second_matrix.json` (28 comprobaciones, 6 tests).

- DONE S324 `0x43fee370` es `u32[34]` (136 B, termina en L95); «29/30» de S204 = posiciones del array, no columnas. Ningún par de columnas de la matriz difiere en 1 registro (mínimo 2) → «1 registro (0x000c/0x000a)» no reproducible; la tabla de 34 columnas queda NO_VERIFICADA. Setter de modo/sub = slot 8: A7S `0x436f3b44` (1..0x51, modo→+0x1ac, sub→+0x2b0) y A6000 `0x436d6b50` (1..**0x47** → rechaza `0x4e`/`0x4f`, modo→+0x170, sub→+0x266); la puerta de la segunda matriz es el `sub`. Evidencia: `docs/capture/s324-columns-audit.md`, `analysis/s324_columns_audit/columns_audit.json` (53 comprobaciones, 8 tests).

- DONE S325 `0x43c9c5b5` es `posicion->columna` de **34** entradas (no `modo->columna` de 82): `0x43ada284` devuelve el **indice** en el `u32[34]` de `0x43fee370` y el accesor lo usa como indice del mapa. `0x4e`->col **12**, `0x4f`->**13**, `0x4c`/`0x4d`->**5**; la matriz **si distingue** silent (14 y 11 registros). **SUPERSEDE** el «columna 1 / no distingue» de S302/S321. Evidencia: `docs/capture/s325-position-map.md`, `analysis/s325_position_map/position_map.json` (41 comprobaciones, 7 tests).

- DONE S326 La tabla de «34» de S202/S204 es **T2** (`0x43bbf2ec`, 34 filas de `0x1c`, una por modo), no 34 columnas. `0x4c`/`0x4d`: `+0x14=0x3ff`, `+0x18=2`; `0x4e`: `+0x14=0` (1 campo); `0x4f`: `+0x14=0`, `+0x18=3` (2 campos). Igualdades `0x4e≡0x51`, `0x4f≡0x50`, `0x4c≡0x4d`. `0x3ff` solo en `{0x13,0x1f,0x4c,0x4d}` y `3` solo en `{0x0b,0x35,0x4f,0x50}` → no es firma silent. S204 parcialmente reproducido. Evidencia: `docs/capture/s326-t2-fingerprint.md`, `analysis/s326_t2_fingerprint/t2_silent_fingerprint.json` (45 comprobaciones, 7 tests).

- DONE S327 Solo hay dos escritores de `obj+0x2b4`: el constructor base lo pone a 0 y el **constructor parametrico** `0x436f3fc0(obj,idx)` guarda su argumento (`0x436f40fe`, `r6=r1`). Unico llamador estatico con **idx=0** → se lee la fila 0 de T1/T2/T3. 9 lectores, ninguno derivado de un codigo de modo → la correspondencia fila<->modo de S326 queda **NO_VERIFICADA** y las filas 29/30 no son alcanzables por esta via. Evidencia: `docs/capture/s327-row-index-writer.md`, `analysis/s327_row_index_writer/row_index_writer.json` (24 comprobaciones, 6 tests).

- TODO S328 Buscar una instancia construida con `idx != 0` (constructor `0x436f3fc0` por puntero, tabla de factorias o modulo hermano) para decidir si T1/T2/T3 llegan a indexarse por modo.

- CHECKPOINT S321–S328 (2026-10-22): corregido el mapa de columnas (`0x43c9c5b5` = posición→columna, 34 entradas) y la tabla «de 34» (T2, 34 filas); cerrada la segunda matriz (vacía, sin productor estático) y el índice `obj+0x2b4` (argumento del constructor, 0). 100/100 tests del carril (S314–S328) verdes.

- TODO S329 Localizar la tabla de **tiempos** por modo del A7S (S202 §3) y comprobar si `0x4e`/`0x4f` difieren de `0x4c`/`0x4d`; si no aparece, cerrar la pregunta con barrido de la región de tablas de modo.

- DONE S329 **No existe tabla de tiempos por modo en el A7S.** Estructuras por modo: lista `u32[34]`, mapa posición→columna, matriz de 69 filas (valores de registro) y T1/T2/T3 `34×0x1c` = `(índice a 2 descriptores, máscara de 12 bits)`. Único consumidor `0x436f618c`: lee solo `+0x14` (índice, `mla 12*r2`) y `+0x18` (máscara, `asrs`); 22 B por fila sin leer. **Corrige S317/S326**: T2 `0x43bbf2e8` y T3 `0x43bbef30` (4 B menos), índice ∈{0,1} y `T3→T2 = 34×0x1c`; caen `0x4e≡0x51`/`0x4f≡0x50`. Matriz: `0x4e`/`0x4c` = 14 registros, `0x4f`/`0x4d` = 11, `0x4c≡0x4d`, sin valor exclusivo de silent. Barrido de dos regiones: 0 tablas de tiempos referenciadas. Evidencia: `docs/capture/s329-mode-timing-tables.md`, `analysis/s329_mode_timing_tables/mode_timing.json` (1202 comprobaciones, 13 tests).
- TODO S330 Buscar una instancia de `0x436f3fc0` con `idx != 0` (tabla de factorías, puntero o módulo hermano) para decidir si T1/T2/T3 llegan a indexarse por modo.
- TODO S331 Rastrear el productor runtime de la segunda matriz (escrituras a `0x43e8de00`/`0x43e80160`, posible DMA u otro módulo de `liro.ko`/`libObj.so`).
- TODO S332 Interpretar los campos de T2 (`+0x14`: `0x3ff`/0; `+0x18`: 2/3) siguiendo sus lectores en `0x436f618c` y el consumidor de `obj+0x16/+0x2e/+0xa5`.
- TODO S333 Contrastar el vocabulario de modos: A6000 acepta `1..0x47` (13 códigos) y A7S `1..0x51` (34); mapear los 13 códigos de la A6000 y ver si alguno es «silent-like» en su matriz de 59 filas.

- SUPERSEDED (parcial) S326 Las bases de T2/T3 eran 4 B altas (`0x43bbf2ec`/`0x43bbef34`); las correctas son `0x43bbf2e8`/`0x43bbef30`, con lo que el «campo +0x14» que S326 leyó era en realidad `+0x10` (ceros) y el `+0x18` era el índice. Las igualdades `0x4e≡0x51` y `0x4f≡0x50` **no se sostienen** (difieren en `w0`: `0x02` vs `0x03`). `0x4c≡0x4d` sí se mantiene. Ver S329.
- TODO S334 Identificar quién consume los bloques `obj+0x16`, `obj+0x2e` y `obj+0xa5` (12 pares flag/valor que escribe `0x436f618c`) y si llegan a la trama P2S `81|03|dev|addr|data` o a otro mensaje.
- TODO S335 Caracterizar el objeto `0x43dc02e0` (`ip = *(0x44024808)`): ventanas `+0x20` y `+0x60`, qué offsets usan las 12 entradas de la tabla B y quién escribe esas ventanas.
- TODO S336 Explicar `w0` (2/3/4/1) y `w4` (`0x01000101`/`0x01000102`) de las filas T1/T2/T3: ¿contadores, flags empaquetados o ids de bloque?
- TODO S337 Identificar el consumidor del único candidato estricto del barrido: `u16[69]` en `0x43fef404` (valores 1..78).
- TODO S330 (vigente) Buscar una instancia de `0x436f3fc0` con `idx != 0` (tabla de factorías, puntero o módulo hermano) para decidir si T1/T2/T3 llegan a indexarse por modo.

- DONE S330 Único `BL` a `0x436f3fc0` (`0x436f2a8a`) con `movs r1,#0` → `idx=0` constante; sin literales ni slot de vtable; la llamada está en una **factoría singleton** (`0x436f2a7c`) que publica el objeto en `0x440245cc → 0x43e8d994` y no tiene `BL` directo. `obj+0x2b4 = 0` siempre → T1/T2/T3 solo aportan la fila 0 (modo `0x0b`); la huella por modo de S326 no se aplica por esta vía. Evidencia: `docs/capture/s330-ctor-instances.md`, `analysis/s330_ctor_instances/ctor_instances.json` (21 comprobaciones, 8 tests).

- DONE S331 **Corrige S317/S327/S330**: la firma real es `0x436f618c(obj, posicion_modo, flag)`. `mov r5,r1` + `muls r5,r2,r5` (stride 0x1c) y los dos llamadores (`0x436f3be2`, `0x436f4480`) prueban que la fila es la **posición del modo** (índice de `0x43ada284`); `obj+0x2b4` es un **flag de log** (`cmp r2,#1`). Hermanos `0x436f61f8`/`0x436f60ac` con la misma firma. Huella silent en **T2**: máscara `0x3ff` para `0x4c`/`0x4d` y 0 para `0x4e`/`0x4f`; T1/T3 idénticas. Evidencia: `docs/capture/s331-consumer-signature.md`, `analysis/s331_consumer_signature/consumer_signature.json` (157 comprobaciones, 10 tests).
- SUPERSEDED (parcial) S330 El veredicto «solo se aplica la fila 0» es **falso** (S331). El singleton existe y `obj+0x2b4` vale 0, pero eso solo desactiva un log.
- SUPERSEDED (parcial) S327 `obj+0x2b4` no es el índice de fila; es el flag del tercer argumento.

- DONE S332 El mecanismo por modo es **compartido**: el setter A6000 `0x436d6b50` (límite `0x47`) busca en 13 códigos (`0x43fea070`), guarda la posición en `obj+0x17c`, aplica la matriz (slot 40) y llama a `0x436d8e6c(obj+0x18, posición, flag)`; éste lee `+0x14`/`+0x18` (stride `0x1c`) y rellena 2 bloques (`obj+0x14`, `obj+0xa1`). Tablas `0x43bc20dc`/`0x43bc2248`; descriptores compartidos `0x43c949a7` (3 filas). Diferencias: 13 vs 34 modos, 2 vs 3 tablas, descriptores `{0}` vs `{0,1}`, 0 vs 30 máscaras cero. Evidencia: `docs/capture/s332-a6000-tables.md`, `analysis/s332_a6000_tables/a6000_tables.json` (343 comprobaciones, 11 tests).

- DONE S333 Vocabulario y columnas: 13 códigos A6000 (`0x43fea070`) vs 34 A7S (`0x43fee370`); 12 compartidos, `0x2f` solo A6000, 22 solo A7S (incl. `0x4c`–`0x51`). La columna de la matriz **es** la posición en la A6000 (sin mapa) y en el A7S pasa por `0x43c9c5b5`. Vectores distintos: **7/13** en A6000 (alias `{0x05,0x07,0x10,0x18,0x19,0x1a}`, `{0x0b,0x2f}`) y **15/34** en A7S (12 grupos). Los silent no tienen vector exclusivo. Evidencia: `docs/capture/s333-mode-vocabulary.md`, `analysis/s333_mode_vocabulary/mode_vocabulary.json` (20 comprobaciones, 9 tests).
