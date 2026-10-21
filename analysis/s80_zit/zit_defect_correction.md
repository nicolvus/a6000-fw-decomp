# S80 — ZIT: corrección de defectos del sensor (DDC) en el imager (A6000 fw3.21)

**Alcance:** línea de ingeniería inversa **general** de la cámara: el subsistema **ZIT** del
`av-cam.bin`, la **corrección de defectos** (dark/defect pixels) del sensor, con su puente al motor
de imagen SA y sus conversiones de formato. No es la línea SilentShutter, ni la montura (S66), ni el
AF, ni ADJ_CMD, ni ZPD (S75 —aunque se relacionan, ver §6), ni el pipeline (S76).

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

Artefactos: `tests/test_s80_zit.py`.

---

## 1. Qué es (VERIFICADO)

El imager de la cámara (`Camera::Imager`) incorpora un motor de **corrección de defectos** con el
prefijo de traza `[CAM_IMAGER]:` y las clases RTTI:

| clase (nombre mangled) | dirección |
|---|---|
| `N6Camera6Imager12ZitMemBufferE` | `0x43cf768e` |
| `N6Camera6Imager18ZitZphDefectBufferE` | `0x43cf81a1` |
| `N6Camera6Imager21ZitZphLineTableBufferE` | `0x43cf96ef` |

**118 cadenas** contienen `ZIT`/`Zit` en la A6000 (75 en la A7S fw3.20).

## 2. Las cuatro áreas de memoria (VERIFICADO)

El motor trabaja sobre **cuatro búferes** ("shadow areas") registrados en
`ZIT:: shadowAddr adj:%x usr:%x slow:%x mend:%x` (`0x43cf7706`, ref `0x43a101c8`):

| área | significado | traza |
|---|---|---|
| `adj` | datos de **ajuste** (defectos de fábrica) | `ZIT:: Memory remain size [byte]: adj:%d usr:%d slow:%d mend:%d` (`0x43cf788e`) |
| `usr` | datos de **usuario** | idem |
| `slow` | datos de modo **lento** (long exposure) | `ZIT:: SLOW mendBuff skip` (`0x43cf7823`) |
| `mend` | búfer de **parche** (mend) | `ZIT:: mendBuff: addr%x max%dpt` (`0x43cf77f6`), `MendBuffInfo[%d][%d] TopPtr = 0x%08x, Size = %d` (`0x43cf784a`) |

Además: `ZIT:: <read:%d bank:%d> shadowBuff: addr%x max%dpt` (`0x43cf7771`) → los defectos se
organizan en **bancos por "read mode"** (`read mode` = modo de lectura del sensor).

## 3. El puente con el motor de imagen (SA) (VERIFICADO)

`Camera::Imager::ZitSaFunctionDriver` (clase propia) gestiona la llamada al SA:

- `ZitSaFunctionDriver: dmmHandleList is Full.` (`0x43cf9cd3`), `dmmHandle=0xffff` (`0x43cf9d0d`),
  `dmmHandle=0` (`0x43cf9d41`) → **handles DMM** con una lista limitada.
- `ZIT_SaOpen` / `ZIT_SaStart` / `ZIT_SaClose` (`0x43cfa2a7`, `0x43cfa2ca`, `0x43cfa2ee`, ref
  `0x43a19346`); firma embebida:
  `__uint16_t Camera::Imager::ZitSaFunctionDriver::ZIT_SaClose()` (`0x43cfa312`).
- `ZIT:: SA Driver StartCommand Send Success !!! [ SAID:%02x /CmdCode:%02x /OsalID:%04x ]`
  (`0x43cf9e1d`), `SA Driver START DONE Receive Info !!! [ SAID:%02x /cancel_que:%02x /int_fact:%02x ]`
  (`0x43cf9f8c`) y `SA Driver RESULT Receive Succeed !!! [ ResultID:%02x /UniqueID:%02x ]`
  (`0x43cfa1b6`).
- `ERROR: ZIT_SaOpen %x` / `ZIT_SaStart %x` / `ZIT_SaClose %x` → códigos de error propios.
- `%s: \`CloseFreeZitMMUParam' error` (`0x43cfa210`) → **MMU propio de ZIT**.

## 4. Las operaciones que se ejecutan en el SA (VERIFICADO)

Cada grupo de trazas corresponde a una función distinta (referenciada):

| operación | traza | función |
|---|---|---|
| **Merge** (fusiona dos conjuntos de defectos) | `ZIT Merge:Info ch%01x [IN1] Adrs:%08x / Num:%04x [IN2] Adrs:%08x / Num:%04x [OUT] Adrs:%08x` (`0x43cf8bac`) | `0x43a13be8` |
| **ConvThin** (adelgaza/convierte defecto) | `ZIT:: SA CONV_THIN ProcInfo [ThinMode] %02x` (`0x43cfa4b4`) | `0x43a194c4` |
| **ConvUnity** (conversión a formato uniforme) | `ZIT ConvUnity: ProcInfo [OUT] Adrs:%08x / Num:%04x` (`0x43cfa798`) | `0x43a19908` |
| **ConvZ1C** (conversión Z1C) | `ZIT ConvZ1c: ProcInfo [IN] Adrs:%08x / Num:%04x` (`0x43cfa929`) | `0x43a19c58` |
| **Det** (detección) | `ZIT DET: DetectInfo [ch1..ch4] Adrs:%08x / Num:%04x` (`0x43cfad05`–`0x43cfadbc`), `ZIT DET: RAWInfo [AVE:%04x/MIN:%04x/MAX:%04x]` (`0x43cfadf9`) | `0x43a1a364` |
| **Hist** (histograma) | `ZIT Hist: SA START/END !!! [SAIP:%04x/ParamAddress:%08x]` (`0x43cfae6e`) | `0x43a1a834` |
| **ZphSA** (SA de zona de placa) | `ZIT ZphSA: saParamBuf is shortage.` (`0x43cfaef4`) | `0x43a1aafc` |
| **ConvDdc** (conversión DDC previa) | `ZitSA_ConvDdc: saParamBuf is shortage. %d %d` (`0x43cf88eb`) | `0x43a139c8` |

Reglas transversales (VERIFICADO): el SA exige que el búfer de parámetros tenga tamaño mínimo
(`saParamBuf is shortage`), que los formatos de entrada sean compatibles
(`input Format Error. input1:type%d != input2:type%d`) y que la conversión esté soportada
(`Conversion from format %d to format %d is not supported.`).

## 5. Detección, modos de lectura y variantes (VERIFICADO)

- `ZIT:: DetectFlag :%02x` (`0x43cf9aef`).
- `ZIT DET: DetectControlSW %d is not supported.` (`0x43cf8c87`).
- Trazas de registro: `ZIT:: SetZitLog_DetectSequencePre() index_id error :%d` (`0x43cf7e5f`),
  `SetZitLog_MassiveDefectDetectNum() defectMode error: %d` (`0x43cf7ea5`),
  `SetZitLog_DefectLvAndPos() dataAdr NULL` (`0x43cf7ef2`),
  `SetZitLog_DefectPosNum() readModeIdx error: %d` (`0x43cf7f2e`) → el motor registra **nivel de
  defecto y posiciones** y distingue **modos de defecto** (*massive defect*).
- Búferes de "Zph" (zona de placa): `ZitZphDefectBuffer::reCalcOffset` (`0x43cf81c6`),
  `::copyBuff` (`0x43cf82a7`/`0x43cf8303`), `::convertBackupSaveformat` (`0x43cf835f`);
  `ZphAdj_Merge_Req` (`0x43cf9717`), `ZphDetSA: unexpected defectKind: %d` (`0x43cf97c2`),
  `ZphAdj_Det_Req: zphLineBuff shortage.` (`0x43cf9811`).
- Formato de copia de seguridad: `ZIT_releaseDefectCorrectionData: freeMemory.` (`0x43cf83de`).
- Variantes: **long exposure** (`buildLongExpCapData_DDC:` con merge de datos `adj` + `usr` y
  conversión `convDdcByCpu`/`ZitSA_ConvDdc`) y **vídeo**
  (`MovieAdj_SpreadDefectsOverSharedPixels: work0 is shortage.`).
- Drivers en el nivel superior: `ZitDdcDriver: Invalid format. [%d][%d]` (`0x43cb5fc1`, ref
  `0x4386bbee`), `ZitDdcDriver: Invalid numPt.` (`0x43cb5ffa`) y
  `ZitZ1cDriver ch:%d is not exist.` (`0x43ca71b6`, ref `0x437b93c0`) → ambos cuelgan de
  `CAMERA_MAIN_IM`.

## 6. Relación con ZPD (S75) — INFERENCIA

ZIT y ZPD comparten el concepto de "posición de defecto" y el soporte de la **SRAM del sensor**
(`ImgDdcSetter::loadDefectPos ZPD_SRAM shortage`, S75). En el subsistema de caras hay además
`zpd area_layout error` (`FC/Alg/fc_alg_track_init.cpp`). INFERENCIA: **ZIT** es el motor que
*aplica* la corrección de defectos y **ZPD** el que *proporciona/valida* los datos de calibración de
la lente; no está probado el enlace programático exacto.

## 7. Diferencial A7S fw3.20 (VERIFICADO)

La A7S tiene **75** cadenas ZIT frente a **118** de la A6000: la fw3.21 añade las conversiones
`ConvThin`/`ConvUnity`/`ConvZ1C` completas (`SA START/END`, `ProcInfo`), el bloque `Zph`
(`ZphAdj_Merge_Req`, `ZphAdj_Det_Req`, `ZphDetSA`) y más trazas de `Merge`/`Det`/`Hist`.

## 8. Abierto (NO_VERIFICADO)

- Qué significan exactamente las siglas **ZIT** y **Zph** (no hay cadena que lo exponga).
- Qué es "read mode"/banco y cuántos hay (`READMODE_NUM_MAX` aparece en `numReadMode > READMODE_NUM_MAX.`).
- Formato binario de los datos de defecto (posiciones, niveles) y su origen (fichero de fábrica).
- Relación exacta ZIT↔ZPD.
- Qué algorithms del SA ejecutan Merge/ConvThin/ConvUnity/ConvZ1C (código dentro del SA, fuera del
  blob analizado).

## 9. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s80_zit.py -q
```
