# Cola carril B (DeepSeek) — imager: estado, drive modes y gates (S300+) (estado: TODO | DOING | DONE <hash> | BLOCKED <causa>)

- DONE S300 (rev.2 `b2f5ff12`) Barrido único de xrefs a `0x43f72d02` (GOT `0x4401f990`) en A6000: **67 sitios** clasificados (55 lectura, 6 escritura, 3 spill, 2 propagación, 1 dato); cero writers de `+3`/`+6`; stores solo a `+0x00`/`+0x02`. Corrige el sesgo +0x58 de la rev.1. Evidencia: `docs/capture/s300-state-xref-sweep.md`, `analysis/s300_state_xref_sweep/state_xref_sweep.json`, 4+7 tests verdes.

- DOING S301 Mismo barrido en A7S fw3.20; tabla de diferencias.

- TODO S302 Tablas de drive mode/exposición (S124, S134, S140) A7S vs A6000 campo a campo.

- TODO S303 Árbol de referencias de `0x43ff3200` (pendiente de S176) y alcanzabilidad de callers de `FUN_43858338`.