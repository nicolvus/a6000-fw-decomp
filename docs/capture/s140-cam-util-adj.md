# S140 — `[CAM_UTIL_ADJ]`: la utilidad de ajuste (A6000 fw3.21)

> Módulo con **22 trazas**, propio de la A6000 fw3.21. Informe completo:
> `analysis/s140_cam_util_adj/cam_util_adj.md` · datos: `cam_util_adj.json`.

## Qué es

La etiqueta `[CAM_UTIL_ADJ]` es el log de la **utilidad de ajuste** del firmware: una tarea
OSAL (`tsk_cam_adjctrl`) que recibe comandos de ajuste y un callback (`cam_adjcmd_handle_cb()`)
que los ejecuta. Lo que ejecuta es **escribir/leer tablas de calibración dentro de la RAM del
sensor** (`Senser RAM Access`, `Table Write`, `Table Read`), direccionadas por
`Module ID` + `Offset` + `Size` + `D0..D7`, y devolver el resultado por el canal «Sens Infra».

## Cifras (regla PIC estricta, canónica del repo)

| | valor |
|---|---|
| cadenas `[CAM_UTIL_ADJ]` | **22** (bloque `0x43ccdcee`–`0x43cce0f2`) |
| referenciadas / sitios | **22/22** · **22** sitios (1 por cadena) |
| funciones | **3**: `0x439007b0` (Table R/W, 6 trazas), `0x43900a24` (`cam_adjcmd_handle_cb`, 13), `0x43900c44` (`tsk_cam_adjctrl`, 3) |
| tabla de despacho | `0x440121f8`, 3 entradas: idx 1 → `0x439007b0`; idx 0 y 2 → stub `0x43b2a0b8` |
| callback registrado | puntero `0x43900a25` en la tabla de callbacks `0x4401f7a4` |

## Diferencial

- **La etiqueta es propia de la A6000 fw3.21**: token `[CAM_UTIL_ADJ]` = 22 / **0** / **0**
  (A6000 / A7S fw3.20 / A6300 fw2.01); interiores de texto **0/22** en A7S y **0/22** en A6300.
  Tampoco existen allí los prefijos `[CAM_UTIL]`, `[CAM_UTIL_SENS]` ni `[CAMERA_ADJ]`.
- **Pero la capa de comandos «Sens» es común a los tres**: 27 cadenas `Sens:*` con texto
  idéntico en los tres, y la tabla `{cmd,size,str}` de **51 entradas** con los **mismos cmd y
  size** (`0x0400015d`..`0x0400018f`) en los tres. Entradas clave:
  `Sens:AdjCmd CAIF`=`0x04020180`, `Sens:RAM Write`=`0x04000188`, `Sens:RAM Read`=`0x04020189`,
  `Sens:AdjCmd DwnCamera`=`0x0400018a`. Única diferencia de texto: cmd `0x04000167` =
  `Reserved` (A6000) vs `POFF return` (A7S/A6300).
  → Lo **nuevo en la A6000** es la **instrumentación**, no la función.
- Colateral: la convención `vaddr = 0x43541000 + file_offset` también vale para los
  `av-cam.bin` de A7S fw3.20 y A6300 fw2.01 (verificado en los punteros de la tabla «Sens»).

## Línea del obturador

**El módulo NO toca tiempos de obturación, iris, ISO ni lectura de imagen.** Ninguna de las 22
trazas lo nombra y ninguna de las 3 funciones llama a una API de obturador/iris/ISO (destinos
de llamada: log `0x43900728`, envío OSAL `0x4390092c`/`0x43561260`/`0x435612ec`,
`[CAM_UTIL_SENS]` `0x439023b8`, memcpy/memset). Es una vía **genérica de escritura de
calibración en el sensor**, no el punto donde se materializaría un «Silent»/EFCS.

## NO VERIFICADO

- Fichero fuente propio del módulo: **no consta** (ningún `.cpp`/`.h` referenciado desde
  `0x439007b0`–`0x43900d30`). Sería hermano de la familia `amSens*` — solo inferencia.
- Significado de `Module ID` (campo `+0x14`): qué tabla es iris/ISO/shutter/WB — **no verificado**.
- Significado de «Senser», «MS» e ids OSAL `0x008f013a` — **no verificado / no desarrollados**.
- Índices 0 y 2 de la tabla de despacho: stub «no soportado»; qué operación queda fuera
  — **no verificado**.
