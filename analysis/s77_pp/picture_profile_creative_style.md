# S77 — Creative Style y balance de blancos en la A6000 fw3.21

**Alcance:** línea de ingeniería inversa **general** de la cámara: el **Creative Style** (estilo
creativo) y el **balance de blancos**, tal y como aparecen repartidos entre el `av-cam.bin` y el
userland (`wrapperCreativeStyle.so`, `wrapperWhiteBalance.so`). No es la línea SilentShutter, ni la
montura (S66), ni el AF, ni ADJ_CMD (S73), ni el visor (S85/S86), ni las caras (S71), ni el wireless
(S72).

**Estado:** VERIFICADO = contra bytes/símbolos. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

> **Nota de revisión (21-10-2026).** El informe del subagente mezclaba tres cosas distintas y le
> atribuía al firmware things que no están: (a) daba por encontrada una **tabla de Picture Profile**
> en el offset `0xaa8d50`, que en realidad es **código Thumb**; (b) daba por presentes en
> `av-cam.bin` los nombres de parámetro `Highlight`, `Saturation`, `Sharpness` (0 apariciones) y
> `CreativeStyle`/`PictureProfile` (0 apariciones); (c) daba por inevitable una tabla de presets de
> WB (`Auto`, `Daylight`…) que **no aparece** en el firmware. Este documento es la versión
> verificada.

Artefactos: `tests/test_s77_pp.py`.

---

## 1. Los estilos creativos: dos tablas de nombres en `av-cam.bin` (VERIFICADO)

**Tabla 1** — `0x43ca6702`–`0x43ca676d`, **13 entradas** en este orden:

| # | estilo | dirección | | # | estilo | dirección |
|---|---|---|---|---|---|---|
| 0 | `Vivid` | `0x43ca6702` | | 7 | `Sunset` | `0x43ca673f` |
| 1 | `Neutral` | `0x43ca6709` | | 8 | `Nightview` | `0x43ca6747` |
| 2 | `Portrait` | `0x43ca6712` | | 9 | `Autumnleaves` | `0x43ca6752` |
| 3 | `Landscape` | `0x43ca671c` | | 10 | `Real` | `0x43ca6760` |
| 4 | `Clear` | `0x43ca672b` | | 11 | `Sepia` | `0x43ca6766` |
| 5 | `Deep` | `0x43ca6732` | | 12 | `Standard` | `0x43ca676d` |
| 6 | `Light` | `0x43ca6738` | | | | |

**Tabla 2** — `0x43ca678b`–`0x43ca67f0`, **12 entradas** (mismos nombres, **sin `Real`**):
`Vivid` `0x43ca678b`, `Neutral` `0x43ca6792`, `Portrait` `0x43ca679b`, `Landscape` `0x43ca67a5`,
`Clear` `0x43ca67b4`, `Deep` `0x43ca67bb`, `Light` `0x43ca67c1`, `Sunset` `0x43ca67c8`,
`Nightview` `0x43ca67d0`, `Autumnleaves` `0x43ca67db`, `Sepia` `0x43ca67e9`, `Standard` `0x43ca67f0`.

La **A7S fw3.20 tiene las mismas dos tablas** con los mismos 13/12 estilos
(`Vivid` `0x43cb540e`, `Neutral` `0x43cb5415`, `Deep` `0x43cb543e`, `Autumnleaves` `0x43cb545e`,
`Nightview` `0x43cb5453`, y la segunda tabla en `0x43cc5ab8`–`0x43cc5b08`): el juego de estilos
**no cambia** entre fw3.20 y fw3.21.

INFERENCIA: la diferencia entre las dos tablas (13 vs 12, la entrada `Real` sólo en la primera) es
que la primera incluye un estilo adicional "Real" o que la segunda es la lista "aplicable" y la
primera la "disponible". NO está demostrado qué tabla usa el código.

## 2. El balance de blancos: el bloque `wb_*` es del **display**, no de la foto (VERIFICADO)

En `av-cam.bin` las cadenas de WB están en `0x43c76c26`–`0x43c76c6b`, **dentro del bloque de ajuste
de panel `ADJ_CMD_AVBB_PANELEVF_*`** (S73, que empieza en `0x43c76c93`):

| cadena | dirección |
|---|---|
| `wb_b_data=%02X ` | `0x43c76c26` |
| `wb_data_tmp=%02X ` | `0x43c76c36` |
| `wb_r_data=%02X ` | `0x43c76c48` |
| `wb_data_tmp=%02X, ` | `0x43c76c58` |
| `wb_g_data=%02X ` | `0x43c76c6b` |
| `wb_w_data=%02X, ` | `0x43c76dca` |
| `wb_mask=%02X, ` | `0x43c76dbb` |
| `wb_w_data=%02X ` | `0x43c76e21` |
| `wb_mask=%02X ` | `0x43c76e13` |

Son, por tanto, los **datos de calibración de WB del display** (los sub-bloques R/G/B de
`WB_SubB_*_Adrs`, S73), **no** el balance de blancos de la fotografía. En `av-cam.bin` **no existe**
ninguna cadena `CreativeStyle`, `PictureProfile`, `Highlight`, `Saturation`, `Sharpness`, `ColorTone`
ni `wb_shift` (0 apariciones cada una) → el control del WB **fotográfico** y del estilo creativo vive
**solo en el userland**.

## 3. El userland (VERIFICADO)

### 3.1 `wrapperCreativeStyle.so` (8 420 B)

Símbolos (mangled, la .so está *stripped* de la tabla de símbolos pero conserva los nombres en
`.dynstr`):

- `WrapperCreativeStyle::getCreativeStyle(ViewBaseProduct*, WRAPPER_CREATIVE_STYLE*)`
- `WrapperCreativeStyle::setCreativeStyle(ViewBaseProduct*, WRAPPER_CREATIVE_STYLE)`
- `WrapperCreativeStyle::convertProcessValueIdToValue(int, WRAPPER_CREATIVE_STYLE*)`
- `WrapperCreativeStyle::convertValueToProcessValueId(WRAPPER_CREATIVE_STYLE&, int&)`
- `WrapperCreativeStyle::isInhOn(ViewBaseProduct*, WRAPPER_CREATIVE_STYLE, int)`
- `CmnViewProcessDataMgr::getInstance(ViewBaseProduct*)` / `setView(ViewBaseProduct*)`
- `WrapperSettingUtil::isInhOn(ViewBaseProduct*, unsigned int)`
- `stella::8BitArray<unsigned int>` / `stella::8BitArray<unsigned short>` + `stella_print_log`
- Ruta de compilación embebida:
  `/home/jp10239/git-work/build/141H/141H.DSLR.DM_UUD3.reco.LATEST.diadem.set/Guiengine_131H/`
  → modelo interno **141H** (= ILCE-6000) y motor de GUI **"Diadem"**.

INFERENCIA: `WRAPPER_CREATIVE_STYLE` es el enumerado de estilos y `convert*` traduce entre el
identificador de proceso y el valor; la biblioteca es un **envoltorio de ajuste** (wrapper) sobre el
motor de GUI.

### 3.2 `wrapperWhiteBalance.so` (15 556 B)

- `WrapperWhiteBalance::getWhiteBalance(ViewBaseProduct*, WRAPPER_WHITE_BALANCE*, int*)`
- `WrapperWhiteBalance::setWhiteBalance(ViewBaseProduct*, WRAPPER_WHITE_BALANCE, int, int, int)`
  → **tres parámetros enteros** (INFERENCIA: WB + compensación en dos ejes, p. ej. ámbar/verde).
- `WrapperWhiteBalance::resetAdjustmentValue(ViewBaseProduct*, WRAPPER_WHITE_BALANCE)`
- `WrapperWhiteBalance::isInhOn(ViewBaseProduct*, WRAPPER_WHITE_BALANCE)`
- Persistencia: `WrapperSettingUtil::readBackup/writeBackup(ViewBaseProduct*, unsigned int, void*)`
  → `BackupManager::Bkup_Read_Setting_Attr(int, int, void*)` → el WB se guarda en el **backup de
  ajustes** (el mismo almacén BK4 que usa el proyecto para otras cosas).
- Aplicación: `ViewBase::getModelInfo(char const*, int, ParamList*, char const**)` y
  `ViewBase::requestModelExecute(char const*, unsigned char, ParamList*)` → el valor se aplica
  mediante el "model execute" del GUI engine; `ParamBase`/`PrmNumber`/`ParamList` con `PrmNumber::GET`.
- Contexto: `WrapperSettingUtil::getExposureMode`, `isMovieState`, `isMREP`.

### 3.3 Otras bibliotecas de compensación (VERIFICADO por nombre de fichero)

`cmnShiftExposureCompensation.so`, `cmnShiftFlashCompensation.so`, `cmnShiftIris.so`,
`cmnShiftIso.so`, `cmnShiftShutterSpeed.so` — el motor de ajustes de la GUI. **No existen**
`cmnShiftHSV.so` ni `cmnShiftWB.so` (esta última idea estaba en el enunciado del hito y se ha
descartado al comprobar los ficheros).

## 4. Abierto (NO_VERIFICADO)

- Cuál de las dos tablas de estilos usa el código, y qué significa la entrada `Real`.
- Los **valores** asociados a cada estilo (tablas de parámetros): no están en `av-cam.bin` ni en las
  .so analizadas (están en el GUI engine / en el modelo de ajuste).
- El enumerado `WRAPPER_CREATIVE_STYLE` y `WRAPPER_WHITE_BALANCE` completos (nombres y orden).
- El mapeo PP1..PP6/Off del Picture Profile: **no hay ninguna traza de "Picture Profile" en el
  firmware**; el control está en el userland y no se ha localizado.
- Los presets fotográficos de WB (Auto/Daylight/…): no aparecen como cadenas en el firmware.
- Rangos de la compensación de WB.

## 5. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s77_pp.py -q
```
