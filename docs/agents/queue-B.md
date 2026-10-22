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
