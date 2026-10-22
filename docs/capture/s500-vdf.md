# S500 — módulo `[VDF]` (línea general, visor/display)

## Alcance

Decodificación del módulo `[VDF]` del `av-cam.bin` A6000 fw3.21, comparado con
A7S fw3.20 y A6300 fw2.01. Tema de línea general (no sensor/driver A, no estado
imager B, no ruta de control C).

## VERIFICADO

- **Volumen de trazas:** A6000 = 243 cadenas `[VDF]` (rango `0x43c813fc`–`0x43c8d525`);
  A7S = 162; A6300 = 162. Diferencia A6000−A7S = **81 cadenas exclusivas** de la A6000.
  Fuente: `strings` sobre los tres `av-cam.bin` (`analysis/s500_vdf/vdf_compare.json`).
- **Inventario REA:** 241 cadenas reconocidas como datos definidos por Ghidra
  (`analysis/s500_vdf/vdf_strings.json`); las 2 restantes solo aparecen con `strings`
  (no están tipadas como string en el autoanálisis).
- **Referencias de código:** 298 xrefs desde las 241 cadenas a código; 78 funciones
  contenedoras resueltas (`analysis/s500_vdf/vdf_functions.json`), más 146 xrefs que
  caen fuera de cualquier función Ghidra (posible código no reconocido o datos).
- **Función más referenciada:** `FUN_4368b874` (`0x4368b874`, 12 xrefs).
- **Subsistemas inferidos de las cadenas (VERIFICADO por texto):**
  - **OSD / notificación:** `[OSD]`, `<OSD notify>`, `OsdForceStopper`, `VphSetOsdAreaCall`,
    `validOsdNum`, `startX`, `width`, `height`.
  - **EVF / paralaje:** `VDF_SET_EVF_PARALLAX_{INIT,ALLOC,RC_FILL,UPDATE,FREE,END,DRAW}`,
    `s_EvfParallaxCreateYCDataStructure`, `EvfParallaxDesignBuilder`, `VdfDisplayCmdSetDetectExtEvf`.
  - **Panel / línea / HDMI:** `PanelOut`, `Lineout`, `LineOutPin`, `out_pin0_send`,
    `outPin3Send.`, `VdfDisplayCmdSetPanelOut`, `VdfDisplayCmdSetLineLRMix`,
    `HDMI_VIDEO`, `HDMI_FORMAT_QFHD`, `VdfDisplayCmdSetDetectExtPanel`.
  - **YUV / resize / QFHD (4K):** `UpdateYuvQfhdThroughResize`, `CallRcQfhdDivisionResizeLine/Panel`,
    `CallVfxQfhdDivisionTransfer`, `QFHD_RESIZE`, `VDF_YC_3840_MEM_RELEASE`,
    `VDF_YC_1920_MEM_RELEASE`, `VDF_YC_PANEL_MEM_RELEASE`.
  - **4K playback (PB):** estados `VDF_4KPB_STATUS_{PLAY->PAUSE, PAUSE->PLAY,
    PAUSE->PAUSE_TRIM, PAUSE_TRIM->PAUSE, PAUSE_TRIM->PAUSE_TRIM_PLAY,
    PAUSE_TRIM_PLAY->PLAY}`.
  - **Pines / envío-recepción:** `pin_send.`, `recv`, `SystemCmdPinSend`, `VdfInputCmdSetYuvLayoutOption`,
    `VdfInputCmdReleasePinandMem`, `VdfInputCmdTemporaryImageOsdMutePin`.
  - **Memoria YC:** `AllocLineYcMem.`, `EscapeDispMem.`, `ReleaseLineYcMem`,
    `ReleasePanelYcMem`, `ReleaseQfhdYcMem`, `YcPinFree(YC/SDS_YCC)`.
  - **EO index:** `SetRgbPathEo`, `SetRgbPathEoElse`, `EO index YcMem.`, `EO index yuvWork`.
  - **Histograma:** `Y_HIST_ON/OFF`, `YRGB_HIST`, `RepeatYHistStart/ReStart`.
  - **Backup / suspensión:** `SusRes`, `Backup_read(BKID_VDF_CIPA_MEM)`,
    `BKID_UPM_BOOT_CIPA_FLAG`, `BootInit()`, `BootExit()`.
  - **Servicio SRVC:** `VdfSrvcCmdSetLiveDemo`, `VDF_SRVC_LIVE_DEMO_SEQ_ERROR`,
    `BKID_VDF_SRVC_SET_HISTOGRAM_COMP_FREQ`.
  - **Errores / diagnóstico:** `[ERROR]`, `[RE]`, `rcct_Acquire/Fill/Release`, `Retry`.
- **Exclusivos de la A6000 (81):** concentran la ruta QFHD/4K (`UpdateYuvQfhdThroughResize`,
  `CallRcQfhdDivision*`, `CallVfxQfhdDivisionTransfer`, `VDF_4KPB_STATUS_*`,
  `VDF_YC_*_MEM_RELEASE`, `AllocLineYcMem`, `EscapeDispMem`, `Release*YcMem`,
  `YcPinFree`), el índice EO (`SetRgbPathEo*`, `EO index ...`) y el paralaje EVF.
  Los 162 comunes incluyen la base OSD/HDMI/panel/línea/pines/hist/backup.
  Ver `analysis/s500_vdf/vdf_compare.json` (`exclusive_a6000_strings`).

## INFERENCIA

- `VDF` = subsistema de **visualización/salida de imagen** (visor EVF, panel LCD,
  HDMI) con conversión YUV, resize y gestión de buffers YC; no es un módulo de
  captura/sensor. El acrónimo exacto no está en las cadenas (posible
  *View Display Function*); INFERENCIA.
- La A6000 añade sobre la base A7S/A6300 una ruta de **4K/QFHD** (resize dividido
  RC+VFX, buffers 3840/1920, estados PB) y el **índice EO** (path RGB 2D/EO),
  además del paralaje EVF. INFERENCIA: estas rutas son las que explican los 81
  strings exclusivos.
- Las 146 xrefs fuera de función sugieren código no reconocido por el autoanálisis
  de Ghidra o referencias desde datos; no se intentó sembrar Thumb a mano en esta sesión.

## NO VERIFICADO

- Nombres de fichero fuente (no aparece ningún `.cpp`/`.c` en las cadenas `[VDF]`).
- Semántica física de los buffers (pitch, formato, tamaño) y de los estados PB.
- Correspondencia con servicios `MSG_ID_VDF_*` (no se cruzó con S98/S100).
- Si alguno de los 81 strings exclusivos afecta al obturador electrónico: no hay
  relación textual con SilentShutter; se considera fuera de la línea electrónica
  hasta evidencia contraria.

## Artefactos

- `analysis/s500_vdf/vdf_strings.json` (241 cadenas REA)
- `analysis/s500_vdf/vdf_xrefs.json` (298 xrefs)
- `analysis/s500_vdf/vdf_functions.json` (78 funciones contenedoras)
- `analysis/s500_vdf/vdf_unresolved_xrefs.json` (146 xrefs sin función)
- `analysis/s500_vdf/vdf_compare.json` (comparación A6000/A7S/A6300)
- `tests/test_s500_vdf.py` (5 tests, verdes)

## Límite

Análisis estático sobre `av-cam.bin`; sin ejecución ni cámara. Las conclusiones de
subsistema son inferencia a partir de cadenas y xrefs; no se decompilaron las 78
funciones en esta sesión (solo se identificaron).
