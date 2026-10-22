# Cola carril D (Beam Free) — módulos de línea general pendientes (S500+) (estado: TODO | DOING | DONE <hash> | BLOCKED <causa>)

Tema: decodificación de módulos de la línea general de la A6000 fw3.21 no cubiertos por A/B/C, con comparación A7S fw3.20 y A6300 fw2.01. Foco inicial: módulos de mayor tamaño y exclusivos de A6000 relevantes para captura/imagen.

- DONE 381c75b3 S500 Decodificar `[VDF]` (243 trazas): visor, A6000 tiene 81 más que A7S/A6300. Informe docs/capture/s500-vdf.md; tests/test_s500_vdf.py (5 verdes).
- DONE 18a2ea0e S501 Decodificar `[STK]` (76 trazas): eliminado en A6300. Informe docs/capture/s501-stk.md; tests/test_s501_stk.py (5 verdes).
- TODO S502 Decodificar `[EIS]` (estabilización electrónica) y su relación con captura.
- TODO S503 Decodificar `[ZPD]` (zero point detection / AF) y su relación con captura.
- TODO S504 Decodificar `[STABILIZER]`.
- TODO S505 Al vaciar, regenerar la cola con los siguientes módulos pendientes del censo S178 (priorizar exclusivos A6000 y los >40 trazas).