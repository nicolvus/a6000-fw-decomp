# S103 — Prefijos de traza exclusivos de la A6000
**Hito:** documentar los seis tokens `[PREFIJO]` de la A6000 (fw3.21) ausentes en la A7S (fw3.20)
sin hito propio. **Método:** bytes de `av-cam.bin`, conteo S79 y xrefs PIC; sin firmware, cámara,
Ghidra ni REA. Informe: `analysis/s103_prefixes/a6000_prefixes.md`; prueba: `tests/test_s103_prefixes.py` (6 tests, verde).

| Prefijo | n | Qué es | Evidencia principal |
|---|---:|---|---|
| `ADC_DEBUG` | 14 | ADC de 12 canales de LIRO (`TSK_ADC`, `boot_exit_adcliro`) | mensaje OSAL 0x20 B, cabecera `0xfff1`, 12 halfwords en `[msg+6]` (`0x4398eb22`) |
| `AVR` | 2 | Clase de accesorio **LANC-AVR** de `ACCY` | `LANC-AVR Attached` (`0x43c252b4`); handlers `0x43565680/0x435656d4` |
| `ADR` | 1 | Campo **dirección** de una apertura de imagen, no un módulo | mensaje IM open de `0x43901d50`: `[4]`=ADR, `[8]`=SIZE |
| `BKID` | 4 | **Backup ID**: callback de cambio y registro/anulación | `backupId size (BKID_SDF_QTBL_C)` (`0x43c77aeb`), `Backup_read(BKID_*)` |
| `AVOUT` | 2 | Clase de accesorio **AvOut** de `ACCY` | `AvOut Attached` (`0x43c25260`); tipo 0 del dispatcher `0x435646a4` |
| `CAMCORE` | 37 | Librería **Camera::CamCore**: SGC, RDC/PFR, AIF/DMA | RTTI `N6Camera7CamCore8RdcImageE` (`0x43c906b6`) |
**Lectura:** `ADC_DEBUG` describe el bloque ADC que LIRO arranca en boot (comandos `ADC_GET_DATA*`
con `unit_no` y 12 canales). `AVR`/`AVOUT` no son módulos sino clases de accesorio de `ACCY`, con
attach/detach que conmutan máscaras GPIO. `ADR` y `BKID` son campos entre corchetes dentro de logs de
`CAM_UTIL_SENS`/`LIF_DEBUG`: dirección de carga y backup ID, respectivamente. `CAMCORE` es el core de
cámara (selección de controlador por modo, tablas SGC, procesado RDC/PFR, AIF, recursos, DMA) y su
última cadena enlaza con la corrección de puntos defectuosos (`setDefectPt`, `0x43cebcb2`).

**Corrección a S73:** existen cinco cadenas `ADJ_CMD_LIRO_DRIVERS_ADC_LIRO_ADC_*` (`0x43ce4fc5`–
`0x43ce507a`), no cuatro; solo cuatro tienen xref PIC y `GET_DATA` (`0x43ce4fc5`) no está referenciada.

**Frontera (NO_VERIFICADO):** qué magnitud mide cada canal ADC y la función eléctrica de AvOut no se
deducen del binario; requieren esquema o traza en cámara.
