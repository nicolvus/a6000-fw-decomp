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
- DONE cd6fac05 S508 Decodificar [GOLFSHOT] (63 trazas REA). Informe docs/capture/s508-golfshot.md; tests/test_s508_golfshot.py (5 verdes).
- DONE 60fad377 S509 Decodificar [WSX] (BSFS, 59 trazas). Informe docs/capture/s509-wsx.md; tests/test_s509_wsx.py (5 verdes).
- DONE 51a8d3fa S510 Decodificar [RE] (54 trazas). Informe docs/capture/s510-re.md; tests/test_s510_re.py (5 verdes).
- DONE 93cc54d4 S511 Decodificar [INT_ERROR] (53 trazas). Informe docs/capture/s511-int-error.md; tests/test_s511_int_error.py (5 verdes).
- DONE f016266c S512 Decodificar [ENCOUCSTAT] (49 trazas). Informe docs/capture/s512-encoucstat.md; tests/test_s512_encoucstat.py (5 verdes).
- DONE 3ee87e6d S513 Decodificar [CONFIG] (47 trazas). Informe docs/capture/s513-config.md; tests/test_s513_config.py (5 verdes).
- DONE fc0fe2a4 S514 Decodificar [BT] (44 trazas). Informe docs/capture/s514-bt.md; tests/test_s514_bt.py (5 verdes).
- DONE S515 Decodificado [AUDPINEDTR] (34 trazas); [BL] ya cubierto en S186. Informe docs/capture/s515-audpinedtr.md.
- TODO S516 Decodificar [PNL] (panel, 41 trazas).
- TODO S517 Al vaciar, regenerar la cola con los siguientes modulos pendientes del censo S178 (priorizar exclusivos A6000 y >40 trazas).
