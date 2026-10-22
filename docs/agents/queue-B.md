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
