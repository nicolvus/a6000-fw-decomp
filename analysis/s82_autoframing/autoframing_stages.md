# S82 — AutoFraming y las etapas de control del pipeline de captura (A6000 fw3.21)

**Alcance:** línea de ingeniería inversa **general** de la cámara: las tres etapas de **AutoFraming**
(encuadre automático) del pipeline de captura y las **etapas de control/comunicación** que las
rodean, con sus logs y su relación con el motor de imagen (SA). No es la línea SilentShutter, ni la
montura (S66), ni el AF, ni ADJ_CMD, ni ZPD, ni `apc_*`, ni ZIT, ni ADF, ni el visor, ni las caras
(S71), ni el wireless (S72), ni el IDT (S89).

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

> **Nota de revisión (21-10-2026).** El borrador del subagente acertaba en las tres etapas de
> AutoFraming y en el log de "framing forzado", pero usaba **una dirección equivocada**
> (`Stage_WaitControl.cpp`, que está en `0x43cad784`; en `0x43cad6fd` está
> `Stage_RchRcv_ResizeTrim` — error corregido también en S76) y afirmaba que en la A7S el
> AutoFraming "está disperso o ausente". **Es falso:** la A7S fw3.20 tiene las mismas tres etapas
> (`0x43cc26ac`/`0x43cc26c2`/`0x43cc26e1`) y el mismo log (`0x43cc265b`).

Artefactos: `tests/test_s82_autoframing.py`.

---

## 1. Las tres etapas de AutoFraming (VERIFICADO)

| etapa | A6000 fw3.21 | A7S fw3.20 |
|---|---|---|
| `Stage_AutoFraming.cpp` | `0x43cc71a3` | `0x43cc26ac` |
| `Stage_AutoFraming_ResizeRotate` | `0x43cc71b9` | `0x43cc26c2` |
| `Stage_AutoFraming_Branch` | `0x43cc71d8` | `0x43cc26e1` |

**El juego de etapas es idéntico en las dos cámaras** (VERIFICADO: 3/3 cadenas en cada modelo).

## 2. El "framing forzado" y la validación del encuadre (VERIFICADO)

- `[IMAGING_CAP]: Debug) ResizeRotate Framing size force set: offset[%d,%d] size[%d,%d] rotate[%d]`
  (`0x43cc7143`; en la A7S `0x43cc265b`) → el AutoFraming **impone** el offset, el tamaño y el
  **ángulo de rotación** del encuadre.
- Antes de fijarlo, la etapa valida la geometría (todas en `0x43cc6e5f`–`0x43cc70f2`):
  - `ResizeRotate Paramter Error: ImageAreaResize.us_Size_X = %d` (`0x43cc6e5f`),
    `… us_Size_Y = %d` (`0x43cc6eaa`).
  - `… canvas_size.ul_SizeX(%d) < ImageAreaResize.us_Frame_X(%d)+Im…` (`0x43cc6ef5`) y su gemelo en Y
    (`0x43cc6f79`): el **lienzo (canvas)** debe contener el área de imagen.
  - `… Paramter Align Error: ImageAreaResize.us_Frame_X = %d` (`0x43cc6ffd`), `us_Frame_Y`
    (`0x43cc704f`), `us_Size_X` (`0x43cc70a1`), `us_Size_Y` (`0x43cc70f2`): el área debe estar
    **alineada** (la A6000 exige múltiplos de 8/16 píxeles por el bloque del sensor).

INFERENCIA: el AutoFraming no recorta libremente: **calcula un encuadre** (offset/tamaño/rotación) y
lo **valida** contra el lienzo y la alineación del bloque de píxeles antes de fijarlo.

## 3. Las etapas de control y comunicación (VERIFICADO, direcciones corregidas)

| etapa | A6000 fw3.21 | A7S fw3.20 | función |
|---|---|---|---|
| `Stage_CaComm.cpp` | `0x43cc7b9c` | `0x43cc2d53` | comunicación de captura; en su vicinity: `Wait E-MountLens ReduceVoltage Wait(%d ms)` (`0x43cc7aa4`) y `CA CaptureReq RETRY(%d)` |
| `Stage_CameraHAPI.cpp` | `0x43cc7bad` | `0x43cc2d83` | punto de entrada de la API de la app (Sony "HAPI") |
| `Stage_Notify.cpp` | `0x43caccd6` | `0x43cb07bb` | notificaciones del pipeline (`Stage_NotifyLongExpNRCapturing` `0x43caccb7`) |
| `Stage_WaitControl.cpp` | **`0x43cad784`** | `0x43cb0f69` | control de espera (en `0x43cad6fd` está `Stage_RchRcv_ResizeTrim`) |
| `Stage_SACC` / `Stage_SACC.cpp` | `0x43c9ee6c` / `0x43c9f18a` | `0x43ca484d` / `0x43ca4a8a` | área "Still" (SACC) |
| `Stage_Common.cpp` | `0x43cac363` | `0x43cb0098` | común: reintentos de `CapSeqID`, `check cont_max` |
| `Stage_DevLater.cpp` | `0x43cac51b` | `0x43cb01ef` | post-desarrollo (`Load_RawFile) arw_file_num digit over %d`) |
| `Stage_DualRec.cpp` | `0x43cac9f8` | `0x43cb0591` | grabación dual BAYER + CLEARVID |

Las **mismas ocho etapas** existen en la A7S fw3.20 (VERIFICIDO) → el esqueleto del pipeline de
captura es el mismo en ambas cámaras.

## 4. Relación con el motor de imagen (SA) — INFERENCIA por proximidad en rodata

El orden de las cadenas en el blob sigue el orden del código, así que las trazas de error de SA
situadas junto al nombre de una etapa le pertenecen:

| etapa | trazas de SA vecinas | función SA |
|---|---|---|
| `Stage_CaComm` | `sa_func_CONTP_acquire error` (`0x43cc7bfa`), `sa_func_CONTP_start error` (`0x43cc7c6a`), `sa_func_CONTP_release error` (`0x43cc7d2d`) | `CONTP` |
| `Stage_DualRec` | `sa_func_DUALREC_BAYER_acquire` (`0x43cac9c1`), `sa_func_DUALREC_BAYER_start` (`0x43caca0a`), `sa_func_DUALREC_CLEARVID_acquire` (`0x43cac6cf`), `sa_func_DUALREC_CLEARVID_start` (`0x43cac867`) | `DUALREC_BAYER` / `DUALREC_CLEARVID` |
| `Stage_SACC` | `sa_func_NFLASH_start error` (`0x43c9ef73`), `sa_func_NFLASH_acquire error` (`0x43c9f20f`), `sa_func_NFLASH_release error` (`0x43c9f1df`) | `NFLASH` (el flash) |

**No se ha encontrado ninguna llamada `sa_func_*` en la vicinity de las etapas de AutoFraming**: el
encuadre automático se aplica con **parámetros de imagen propios** (resize/rotate del módulo
`ImageAreaResize`) y no con una función SA con nombre.

## 5. Abierto (NO_VERIFICADO)

- Cómo se calcula el encuadre (qué dato del sensor o del AF lo origina) y qué es exactamente la
  "rotación" que se impone.
- La correspondencia entre los parámetros del encuadre y los `apc_*` del motor YC (S78).
- Qué intercambian `Stage_CaComm` y `Stage_CameraHAPI` con la app (¿HAPI = la misma API que
  `libHapiLib.so` de S72?).
- Por qué `Stage_Notify` y `Stage_WaitControl` están en posiciones distintas en A6000 y A7S.
- Qué es exactamente "SACC" (¿*Still Area Capture Calculation*?).

## 6. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s82_autoframing.py -q
```
