# S505 — módulo `[VEF]` (efectos/mapas del visor, línea general)

## Alcance

Decodificación del módulo `[VEF]` del `av-cam.bin` A6000 fw3.21, comparado con
A7S fw3.20 y A6300 fw2.01.

## VERIFICADO

- **Volumen de trazas:** A6000 = 149 cadenas `[VEF]`; A7S = 141; A6300 = 144.
  Fuente: `strings | grep -c '\[VEF\]'`.
- **Inventario REA:** 149 cadenas (`analysis/s505_vef/vef_strings.json`,
  rango no contiguo dentro de `0x43c…`).
- **Referencias de código:** 193 xrefs (`analysis/s505_vef/vef_xrefs.json`); 59 funciones
  contenedoras resueltas (`analysis/s505_vef/vef_functions.json`), 65 xrefs sin función.
- **Subsistemas inferidos (VERIFICADO por texto):**
  - **Downconversion:** `DOWNCON: NTSC 60i60p/30p24p`, `PAL 50i50p/25p`.
  - **Efectos:** `effect duplication`, `receive duplication`, `EffectReadyNotify/Comp`,
    `set_effect`, `cancel`, `NO_REC Sepia Err`, `EFFECT NO_REC WIPE PARAM ERR`,
    `colorbar`, `mute Off`.
  - **Mapas:** `Map Area alloc`, `Not Match Map Size`, `Not Finish Create Map`,
    `MapGen Tsk Priority`, `zoom start/end`.
  - **Señal/vídeo:** `ExecSignalFlow60P{first,Second,Third}`, `transTime`, `exec time`.
  - **RC (remote control):** `rc callback`, `rc result error`, `iib driver ena_sync`.
  - **Memoria:** `Alloc YCMem`, `free DMM_UNITTYPE_DATEREC_WORK_YC`, `dmm alloc err`,
    `YcPin MemMgrOpenErr`, `workHandle`, `Map Area alloc err`.
  - **Infraestructura OSAL:** `InfraMulticast {Regist/Unregist/Pause/PauseRelease}Comp`,
    `MsgInfoUniqueIdImplanter`, `SubsystemAccessorIf::SetMode`, `reply_osal_id`.
  - **Errores:** `[ERROR] Invalid clk_rate`, `AddSndSds AddrErr`, `RcvSdsAddrErr`,
    `SndSdsAddrErr`, `overflow`, `can't detect R Image info`.
- **Comparación:** A6000 (149) ligeramente por encima de A6300 (144) y A7S (141);
  sin grandes diferencias cualitativas. Ver `analysis/s505_vef/vef_compare.json`.

## INFERENCIA

- `[VEF]` = subsistema de **efectos y mapas del visor** (view effects): downconversion,
  efectos de imagen (sepia, wipe), mapas de zoom y control de memoria YC.
- Muy cercano a `[VDF]` (S500) pero centrado en efectos/mapas, no en salida de imagen.

## NO VERIFICADO

- Semántica de los efectos y mapas; relación con captura.
- Si las diferencias cuantitativas (149 vs 141/144) son solo de diagnóstico.

## Artefactos

- `analysis/s505_vef/vef_strings.json` (149 cadenas REA)
- `analysis/s505_vef/vef_xrefs.json` (193 xrefs)
- `analysis/s505_vef/vef_functions.json` (59 funciones)
- `analysis/s505_vef/vef_compare.json` (comparación A6000/A7S/A6300)

## Límite

Análisis estático sobre `av-cam.bin`; sin ejecución. 65 xrefs sin función resuelta.
