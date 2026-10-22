# Cola carril D (Beam Free) — módulos de línea general pendientes (S500+) (estado: TODO | DOING | DONE <hash> | BLOCKED <causa>)

Tema: decodificación de módulos de la línea general de la A6000 fw3.21 no cubiertos por A/B/C, con comparación A7S fw3.20 y A6300 fw2.01. Foco inicial: módulos de mayor tamaño y exclusivos de A6000 relevantes para captura/imagen.

- DONE 381c75b3 S500 Decodificar `[VDF]` (243 trazas): visor, A6000 tiene 81 más que A7S/A6300. Informe docs/capture/s500-vdf.md; tests/test_s500_vdf.py (5 verdes).
- DONE 18a2ea0e S501 Decodificar `[STK]` (76 trazas): eliminado en A6300. Informe docs/capture/s501-stk.md; tests/test_s501_stk.py (5 verdes).
- DONE 2cbe4af6 S502 Decodificar [EIS] (estabilizacion electronica). Informe docs/capture/s502-eis.md; tests/test_s502_eis.py (5 verdes).
- DONE aa19fb01 S503 Decodificar [ZPD] (zero point detection/AF). Informe docs/capture/s503-zpd.md; tests/test_s503_zpd.py (5 verdes).
- DONE 0258cf16 S504 Decodificar [STABILIZER]. Informe docs/capture/s504-stabilizer.md; tests/test_s504_stabilizer.py (5 verdes).
- DONE 2348326f S505 Decodificar [VEF] (visor EVF, 149 trazas). Informe docs/capture/s505-vef.md; tests/test_s505_vef.py (5 verdes).
- DONE 6d4db7a5 S506 Decodificar [TD] (codec transcode/decode, 73 trazas). Informe docs/capture/s506-td.md; tests/test_s506_td.py (5 verdes).
- DONE 960a3170 S507 Decodificar [VIDENCSTAT] (70 trazas). Informe docs/capture/s507-videncstat.md; tests/test_s507_videncstat.py (5 verdes).
- TODO S508 Decodificar [GOLFSHOT] (65 trazas).
- TODO S509 Decodificar [WSX] (59 trazas).
- TODO S510 Al vaciar, regenerar la cola con los siguientes modulos pendientes del censo S178 (priorizar exclusivos A6000 y >40 trazas).
