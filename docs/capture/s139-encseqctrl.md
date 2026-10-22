# S139 — `[ENCSEQCTRL]`: el control de secuencias de codificación (46 trazas)

> A6000 **fw3.21** (`analysis/rea-independent/input/av-cam.bin`; vaddr = `0x43541000` + offset).
> Regla de referencias: **estricta** (canónica del repo). 96/96 sitios **reconfirmados**
> de forma independiente (`analysis/s139_encseqctrl/verify_sites.py`).

**VERIFICADO (34 tests, `tests/test_s139_encseqctrl.py`):** 46 cadenas `[ENCSEQCTRL]`
(46 textos distintos) en `0x43c4bce5`–`0x43c4c796`; **46/46 referenciadas**, **96 sitios**,
**32 funciones** emisoras en `0x435d6ad0`–`0x435d90ac`; **0** cadenas muertas. La única
cadena intercalada en el bloque es el fichero fuente `seqCtrl/mcAvcEncSeqCtrl.cpp`
(`0x43c4bd0f`); la clase es **`McAvcEncSeqCtrl`** (RTTI `0x43c4320f`), del componente
`Avbb-MovieCodec_131H` (ruta de build `0x43c41227`). Id de log del módulo: `0x0e` (las 82 llamadas al logger del módulo).

**Qué es**: el **controlador de la secuencia de codificación AVC/H.264** del MovieCodec.
Recibe los comandos del codificador y los ejecuta como una **máquina de estados** que
cronometra todo en **VFC** (video frame count). Estados: u32 en `obj+0x15B84`
(getter `0x43a5d2da`, setter `0x435d715c`, 17 llamadores); valores observados
**0,1,2,3,4,6,7,8,10,11** (5 y 9 no aparecen → NO VERIFICADO).

**18 ids de mensaje** (`0x8101`–`0x8112`) atendidos por `ProcAvcMsg` (`0x435d8d38`,
`tbh` de 18 entradas en `0x435d8d50`): 12 con nombre (`OPEN_COMP`, `CLOSE_COMP`,
`INITIALIZE_MOVIE/STILL_COMP`, `ENC_PICTURE_COMP`, `ENC_FINAL_PICTURE_COMP`,
`FINALIZE_COMP`, `RELEASE_ES_COMP`, `SET_MOVIE_QUALITY_INFO_COMP`, `SET_FACE_INFO_COMP`,
`RELEASE_PICTURE_NOTIFY`, `GET_ES_NOTIFY`) y 6 sin nombre (`0x810b`–`0x8110`).
Otros hitos: tabla **O/U Crank** de 57×8 B en `0x43b93bf4`; **35 nº de línea** del
`.cpp` recuperados (89–2237) → el fichero original tiene ≥2237 líneas.

**Relaciones**: con **S132** (`[CLK_CTRL]`) sólo **temporal e indirecta**: el módulo razona
en VFC y **consume** el reloj que fija `CLKTYPE`/`sysv_delay` (0 menciones de `CLKTYPE`).
Con **S137** (`[CTRLCORE]`) por la **interfaz de códec** (`McAvcEncModeMgr` →
`mcAvCtrlIf.cpp`/`mcAvCtrlCore.cpp`, distintos de `cdCtrlCore.cpp`); el cruce es el
evento `AVSC_CID_MPRNTFY_ENC_SA_CONFIRM_EVENT` (`0x43c4c332`, único `AVSC_CID` del binario).
Con **S106** (`[IMAGING_CAP]`) de forma **indirecta**, por el sincronizador
`[SYNCENCSTART]` (`mcSyncEncStart.cpp`, `0x43620dd0`–`0x43621298`), que fija
`beginEncTimingVFC` en el `McAvcEncSeqCtrl`. Con **S114** (motor de secciones) **ninguna
directa** (0 llamadas entre ambos). Con **S115** (`[CAM_IMAGER]`) **ninguna**: es aguas
abajo del imager, sólo cronometra sus frames.

**Diferencial**: **A7S fw3.20 idéntico** (46/46 textos, 46 referenciadas, 96 sitios,
32 funciones; la tabla `tbh` de `ProcAvcMsg` es **byte a byte igual**). **A6300 fw2.01
superset**: 50 cadenas, 50 referenciadas, 100 sitios, 34 funciones; 45 textos comunes,
5 nuevos (`quickRestartVfc`, `ouCrankStopVfc`, `Remain/gopNum`, `EnsRestartTime(VFC)`,
`Audio Buffer Overflow detected in Terminate encode Sequence`).

**Línea del obturador — sin efecto**: 0 apariciones de `shut`, `silent`, `electro`, `mech`,
`sensor`, `imager`, `expos`, `drive`, `readout`, `jpeg`, `bracket`, `sweep`, `flicker`,
`curtain` o `liveview` en las 46 trazas. Los únicos `still`/`movie` son **modos de
inicialización del codificador** (`…INITIALIZE_STILL_COMP` `0x43c4c44f`,
`…INITIALIZE_MOVIE_COMP` `0x43c4c40e`, `…SET_MOVIE_QUALITY_INFO_COMP` `0x43c4c5fd`).
⇒ **S51 (A/B/C) = NO**.

**NO VERIFICADO**: significado de la sigla `ENCSEQCTRL` (sin base textual; la clase es
`McAvcEncSeqCtrl`); estado ↔ método (`Exec*State` se invocan por tabla, no por `bl`);
semántica de los valores de la tabla O/U Crank; los 6 ids sin nombre; quién crea el
objeto (0 punteros absolutos de 4 B a sus métodos); qué es exactamente `VFC`; qué es
`m_beginEncCompTime`; sentido de `ReviseNum`.

[Informe](../analysis/s139_encseqctrl/encseqctrl.md) · [datos](../analysis/s139_encseqctrl/encseqctrl.json).
