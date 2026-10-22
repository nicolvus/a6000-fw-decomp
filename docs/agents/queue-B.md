# Cola carril B (DeepSeek) — imager: estado, drive modes y gates (S300+) (estado: TODO | DOING | DONE <hash> | BLOCKED <causa>)

- DONE S300 Barrido único de xrefs a `0x43f72d02` (GOT `0x4401f990`) en A6000: total, tabla clasificada (spill/lectura/escritura/propagación) en `analysis/s300_state_xref_sweep/`; veredicto sobre writers de `+3`/`+6`. **Evidencia**: `docs/capture/s300-state-xref-sweep.md`, `analysis/s300_state_xref_sweep/xrefs_classified.json`, 7 tests verdes.

- DONE S303 Árbol de referencias de `0x43ff3200` (pendiente de S176) y alcanzabilidad de callers de `FUN_43858338`. **Evidencia**: `docs/capture/s303-ref-tree-43ff3200.md`. Hallazgos: tabla contiene puntero a estado en +0x48; acceso vía GOT `0x4401f080`; callers de dumper NO_VERIFICADOS.

- DONE S302 Tablas de drive mode/exposición (S124, S134, S140) A7S vs A6000 campo a campo. **Evidencia**: `docs/capture/s302-drive-mode-exposure-tables.md`. Hallazgos: 11 filas (4 idénticos, 7 distintos); A6000 sin modos Silent (0x4e/0x4f), sin selector tipo==2, fórmula svd aritmética vs columnas estáticas A7S.

- DONE S304 REA/Ghidra: callers de `FUN_43858338` (dumper gates S153) y código que carga GOT `0x4401f080` (tabla `0x43ff3200`). **Evidencia**: `docs/capture/s304-rea-dumper-callers.md`. Hallazgos: dumper en 0x438581e8 lee gates state+3/state+6, caller único FUN_43858390 con 13 callsites en bucle; GOT 0x4401f080 acceso vía literal pool (sin xrefs REA); writers gates NO_VERIFICADOS.

- TODO S301 Mismo barrido en A7S fw3.20; tabla de diferencias.

- TODO S305 Analizar `FUN_43858390` por tramos (REA `file-offset`) para entender bucle principal; buscar literal pool `0x4401f080` (Ghidra `findReferencesTo`).