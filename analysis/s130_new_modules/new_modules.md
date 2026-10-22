# S130 — los 20 módulos "NUEVO/PROPIO" del mapa de etiquetado: ¿contenido nuevo o solo otra etiqueta?

> Hito de la **línea de ingeniería inversa general**. Cierra la pregunta que dejó abierta S128
> («comprobar uno por uno los 20 NUEVO/PROPIO»). Todos los datos salen de los bytes de la
> A6000 fw3.21, la A7S fw3.20 y el A6300 fw2.01. Sin efecto en S51.

## 1. Método

Para cada prefijo clasificado como `NUEVO/PROPIO` en el mapa de etiquetado (S128), se extrae el
**núcleo** de cada mensaje (el texto que sigue a `"[PREFIX]: "`) y se busca esa cadena como
**subcadena** en la A7S fw3.20 y en el A6300 fw2.01. Si aparece, se anota con qué etiqueta lo
envuelve el otro firmware.

| clase | criterio |
|---|---|
| **ETIQUETADO** | ≥ 80 % de los núcleos existen en la A7S (con otra etiqueta o sin ella) → solo cambia el nombre |
| **PARCIAL** | 20-80 % |
| **CONTENIDO NUEVO** | < 20 % → esos mensajes no están en los otros dos firmwares |

## 2. Resultado (los 20 módulos)

| prefijo | n A6000 | núcleos en A7S | núcleos en A6300 | clase | etiqueta en la A7S |
|---|---|---|---|---|---|
| `[IDT_OPD]` | 273 | **270** | 270 | ETIQUETADO | `[IDT]` (270) |
| `[DFE]` | 11 | **11** | 9 | ETIQUETADO | sin etiqueta (10) + `[DFE]` (1) |
| `[JPEG]` | 17 | 4 | 4 | PARCIAL | `[DMMYSIOCOM]` (2), `[ADF]` (1), sin etiqueta (1) |
| `[MOUNT_DEBUG]` | 132 | 2 | 2 | CONTENIDO NUEVO | `[BL]` (1), sin etiqueta (1) |
| `[CAMERA_MAIN_LC]` | 72 | 1 | 1 | CONTENIDO NUEVO | sin etiqueta (1) |
| `[SAD]` | 44 | 3 | 3 | CONTENIDO NUEVO | `[ADF]` (3) |
| `[TP_R]` | 18 | 2 | 2 | CONTENIDO NUEVO | `[DMMYSIOCOM]` (2) |
| `[ILLUMI]` | 34 | 1 | 1 | CONTENIDO NUEVO | `[PNLEVF]` (1) |
| `[ACCY]` | 106 | 0 | 0 | CONTENIDO NUEVO | — |
| `[VPH_API]` | 106 | 0 | 0 | CONTENIDO NUEVO | — |
| `[CLK_CTRL]` | 66 | 0 | 0 | CONTENIDO NUEVO | — |
| `[CAM_UTIL_ADJ]` | 22 | 0 | 0 | CONTENIDO NUEVO | — |
| `[CAM_UTIL_SENS]` | 21 | 0 | 0 | CONTENIDO NUEVO | — |
| `[CAMERA_IS]` | 17 | 0 | 0 | CONTENIDO NUEVO | — |
| `[DEPTH]` | 16 | 0 | 0 | CONTENIDO NUEVO | — |
| `[JOG]` | 14 | 0 | 0 | CONTENIDO NUEVO | — |
| `[ADC_DEBUG]` | 14 | 0 | 0 | CONTENIDO NUEVO | — |
| `[LIF_DEBUG]` | 13 | 0 | 0 | CONTENIDO NUEVO | — |
| `[PANDA]` | 10 | 0 | 0 | CONTENIDO NUEVO | — |
| `[CAMERA_MAIN_FC]` | 9 | 0 | 0 | CONTENIDO NUEVO | — |

Totales: **2 ETIQUETADO**, **1 PARCIAL**, **17 CONTENIDO NUEVO**.

## 3. Lectura

1. **Solo dos de los veinte son un cambio de etiqueta**: `[IDT_OPD]` (ya resuelto en S120: 270 de
   273 núcleos están en la A7S bajo la etiqueta `[IDT]`) y `[DFE]` (11/11: 10 sin etiqueta en la
   A7S y 1 ya con `[DFE]`). Es decir, el mapa de etiquetado de S128 se apoyaba en estos dos casos
   límite y el resto son de verdad material que **no está** en la A7S ni en el A6300.
2. **La A6000 fw3.21 trae módulos que los otros dos firmwares no tienen**: `[ACCY]` (106),
   `[VPH_API]` (106), `[MOUNT_DEBUG]` (132), `[CAMERA_MAIN_LC]` (72), `[CLK_CTRL]` (66),
   `[ILLUMI]` (34), `[DEPTH]` (16), `[PANDA]` (10), `[CAMERA_MAIN_FC]` (9)… Varios de ellos son
   **etiquetas nuevas** (no solo mensajes nuevos): el token `ACCY`, `VPH_API`, `CLK_CTRL`,
   `CAMERA_MAIN_LC`, `MOUNT_DEBUG`, `ILLUMI` y `PANDA` **no aparece ni una vez** en la A7S ni en
   el A6300 (0 coincidencias del propio prefijo).
3. **Detalle relevante para la línea del obturador**: el módulo `[VPH_API]` (la API de cámara)
   incluye una **API de silenciador de obturador que es nueva** en esta fw3.21:
   `<shutter_mute_param>` `0x43ce3634`, `<shutter_mute_param_sub>` `0x43ce3b5a`,
   `>shutter_mute<` `0x43ce3de4`, `>shutter_mute_status<o/f:%d` `0x43ce3dfc`. Las 4 cadenas
   `shutter_mute*` **no existen** en la A7S fw3.20 ni en el A6300 fw2.01 (0 apariciones), mientras
   que la traza del silenciador en sí (`shutter mute on/off`, la del `[SFRS][PINSEND]` de S118)
   **sí** está en los tres firmwares. Es decir: la fw3.21 **añade el parámetro de API** del
   silenciador, no el mecanismo.

## 4. Advertencia metodológica (importante)

La comparación A6000-fw3.21 ↔ A7S-fw3.20 ↔ A6300-fw2.01 mezcla **dos variables**: la versión del
firmware y **el modelo de cámara**. Lo que este hito mide es «presente en la A6000 fw3.21 y
ausente en la A7S fw3.20 y en el A6300 fw2.01», que **no** permite separar «nuevo en la fw3.21»
de «propio de este modelo». En el repositorio solo hay tres blobs de `av-cam.bin`
(A6000 fw3.21, A7S fw3.20, A6300 fw2.01) y **no hay una fw anterior de la propia A6000**, así
que la separación no es posible con los datos locales.

## 5. Verificaciones hechas

| afirmación | cómo se comprueba |
|---|---|
| 20 módulos en la clase NUEVO/PROPIO | `label_map.json` de S128 |
| presencia de los núcleos en la A7S/A6300 | búsqueda de subcadena sobre los blobs |
| etiquetas con las que aparecen en la A7S | barrido de runs con prefijo `[X]` |
| `shutter_mute*` ausente en A7S/A6300 | `bytes.count()` sobre los tres blobs |
| tokens `ACCY`, `VPH_API`, `CLK_CTRL`, … ausentes en A7S/A6300 | ídem |

## 6. NO VERIFICADO / abierto

- Si cada uno de los 17 módulos «contenido nuevo» es *nuevo en la fw3.21* o *propio del modelo
  A6000* (hace falta una fw anterior de la A6000; no está en el repositorio).
- Qué son exactamente `[ACCY]`, `[VPH_API]`, `[CLK_CTRL]`, `[DEPTH]`, `[PANDA]`: **no se desarrollan
  las siglas** sin base textual.
- El significado de la API nueva de silenciador (`shutter_mute_param`, `_sub`, `_status`) y quién
  la consume.
- Nada de esto **afecta a S51** (A/B/C = NO): el silenciador es del obturador **mecánico**.

## 7. Ficheros de este hito

| fichero | contenido |
|---|---|
| `new_modules.json` | los 20 módulos con sus cifras y ejemplos |
| `new_modules.py` | script reproducible del análisis |
