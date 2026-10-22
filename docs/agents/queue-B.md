# Cola carril B (DeepSeek) — imager: estado, drive modes y gates (S300+) (estado: TODO | DOING | DONE <hash> | BLOCKED <causa>)

- DONE S300 Barrido único de xrefs a `0x43f72d02` (GOT `0x4401f990`) en A6000: total, tabla clasificada (spill/lectura/escritura/propagación) en `analysis/s300_state_xref_sweep/`; veredicto sobre writers de `+3`/`+6`. **Evidencia**: `docs/capture/s300-state-xref-sweep.md`, `analysis/s300_state_xref_sweep/xrefs_classified.json`, 7 tests verdes.

- DONE S303 Árbol de referencias de `0x43ff3200` (pendiente de S176) y alcanzabilidad de callers de `FUN_43858338`. **Evidencia**: `docs/capture/s303-ref-tree-43ff3200.md`. Hallazgos: tabla contiene puntero a estado en +0x48; acceso vía GOT `0x4401f080`; callers de dumper NO_VERIFICADOS.

- TODO S301 Mismo barrido en A7S fw3.20; tabla de diferencias.

- TODO S302 Tablas de drive mode/exposición (S124, S134, S140) A7S vs A6000 campo a campo.