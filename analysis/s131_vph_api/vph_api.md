# S131 — `[VPH_API]`: la API de parámetros del subsistema de display VPH (106 trazas)

> Hito de la **línea de ingeniería inversa general**. Verificación contra los bytes de la A6000
> fw3.21, la A7S fw3.20 y el A6300 fw2.01; convención **vaddr = 0x43541000 + file_offset**.
> Regla de referencias: la **estricta** (canónica, ver
> [`pic_xref_methodology.md`](../s106_imaging_cap/pic_xref_methodology.md)), con el mapa global
> `analysis/s106_imaging_cap/pic_refs_strict_global.json`. Sin efecto en S51.

## 1. Qué es

`[VPH_API]` es la traza de la **API de parámetros del subsistema VPH** (la tubería de display
de la cámara: OSD, panel, salida de línea, muteos, ayudas de encuadre). La sintaxis de las
trazas describe la llamada:

| forma | ejemplo | significado | n |
|---|---|---|---|
| `<nombre>` | `[VPH_API]<mode>` `0x43ce32e7` | **entrada**: se está fijando el parámetro | 49 |
| `<nombre>_sub` | `[VPH_API]<mode_sub>` `0x43ce3781` | variante **"sub"** del mismo parámetro | 42 |
| `>nombre<` | `[VPH_API]>mode_status<` `0x43ce3d0e` | **salida**: se lee el estado | 11 |
| `=x=` | `[VPH_API]=v_command_comp=` `0x43ce374b` | comparación de comando | 4 |

→ **60 familias de parámetros**, 106 trazas, en un bloque **contiguo** `0x43ce32e7`–`0x43ce3dfc`.

## 2. Arquitectura: un manejador por parámetro

Las 106 trazas las emiten **48 funciones**, agrupadas en **dos bloques de código**:
`0x4395aab8`–`0x4395b5f4` (39 manejadores) y `0x4395e1b8`–`0x4395e34c` (9), de 52 a 160 bytes
cada una (separaciones medidas: 68 B ×17, 76 B ×6, 64 B ×4, 72 B ×4, 52 B ×4; dos huecos de 156 B
y 160 B dentro del bloque grande). Cada manejador emite **una sola** traza → la API es una tabla
de funciones pequeñas, una por parámetro, y no un módulo con lógica propia.

(Las direcciones de esos manejadores **no** aparecen como punteros absolutos en el blob: la tabla
que los referencia está en formato relativo, o se despachan por índice; no verificado.)

## 3. Los 60 parámetros

| área | parámetros |
|---|---|
| modo y OSD | `mode`, `mode_status`, `mix_mode`, `osd_on`, `osdarea`, `osdarea_on`, `update_osd`, `update_yuv`, `osdmix_size_line`, `osdmix_size_panel`, `faceframe_on`, `update_faceframe`, `faceframe_color`, `timecode_on`, `update_timecode` |
| salidas de panel y línea | `line_out`, `panel_out`, `dualpanel_out`, `force_out`, `line_display`, `panel_display`, `hw_status`, `preset_area`, `black_frame` |
| **muteos** | `yuv_mute`, `yuv_mute_param`, `yuv_mute_immediately`, `chroma_mute`, **`shutter_mute_param`** |
| imagen y ayudas | `panel_brightness`, `panel_brightness_status`, `panel_cabc`, `panel_depth`, `panel_reverse`, `panel_ysetup`, `pictureeffect`, `ylevel_caution`, `zebra`, `peaking`, `gridline`, `histogram`, `histogram_result`, `testpattern`, `diceic_arb`, `laxo`, `yuv_delay` |
| línea de vídeo | `line_closedcaption`, `line_macrovision`, `line_vbidwss`, `line_sync_setup`, `line_fchr`, `line_hdmi_still_range` |
| otros | `parallax_adjust`, `set_color_temperature`, `set_eomainsub_inverse`, `set_extblackframe`, `set_extblackframe_livedemo`, `set_panel_osd_luminance` |

## 4. Lo relevante para la línea del obturador

La API incluye **el silenciador del obturador**, con **4 trazas**:

| traza | dirección |
|---|---|
| `[VPH_API]<shutter_mute_param>` | `0x43ce3634` |
| `[VPH_API]<shutter_mute_param_sub>` | `0x43ce3b5a` |
| `[VPH_API]>shutter_mute<` | `0x43ce3de4` |
| `[VPH_API]>shutter_mute_status<o/f:%d` | `0x43ce3dfc` |

- Las 4 cadenas `shutter_mute*` **no existen** en la A7S fw3.20 ni en el A6300 fw2.01 (0
  apariciones), mientras que la traza del silenciador en sí (`shutter mute on/off`, la del
  `[SFRS][PINSEND]` de S118) **sí** está en los tres firmware → la fw3.21 de la A6000 **añade el
  parámetro de API** del silenciador (no el mecanismo), coherente con S130.
- El silenciador afecta al **obturador mecánico** (el ruido de la cortina); en la API aparece
  como un parámetro más del display, junto a `yuv_mute` y `chroma_mute`. **No hay ningún indicio
  de obturador electrónico** aquí → **sin efecto en S51**.

## 5. Diferencial A6000 fw3.21 vs A7S fw3.20 / A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| trazas `[VPH_API]` | **106** | **0** | **0** |
| apariciones del token `VPH` | **134** | 24 | 24 |

→ El subsistema VPH es **mucho mayor** en la A6000 fw3.21 que en los otros dos firmware: no solo
se etiqueta la API (como en S128), es que **la API completa no está en ellos** (las 24 apariciones
de `VPH` de la A7S son de otro tipo: `VDF::set_vph_*`, `VphSetModePrmGen`, `VPH_ENUM_*`).

## 6. Verificaciones hechas

| afirmación | cómo se comprueba |
|---|---|
| 106 trazas, rango `0x43ce32e7`–`0x43ce3dfc` | extracción por prefijo con corte en fin de cadena |
| 49 entrada / 42 entrada_sub / 11 salida / 4 `=` | clasificación por la sintaxis de cada traza |
| 60 familias | unión de nombres base (sin `_sub`) |
| 48 funciones emisoras en `0x4395aab8`–`0x4395e34c` | mapa PIC estricto + prólogos Thumb; separaciones medidas |
| 0 trazas `[VPH_API]` en A7S/A6300; `VPH` 134 vs 24 vs 24 | `bytes.count()` sobre los tres blobs |
| `shutter_mute*`: 4 en la A6000, 0 en las otras | ídem |

## 7. NO VERIFICADO / abierto

- Cómo se referencia la tabla de los 48 manejadores (no hay punteros absolutos) y quién la
  invoca.
- Qué significan `laxo`, `diceic_arb`, `line_fchr`, `set_eomainsub_inverse`: **no se desarrollan
  las siglas**.
- Qué hace exactamente `shutter_mute_param` (¿silenciar el obturador durante la grabación?) y quién
  lo consume.
- Si el resto de la API VPH (104 trazas) está también ausente en la A7S (probable, por el
 recuento de `VPH`) — no comprobado una por una.
- Nada de esto **afecta a S51** (A/B/C = NO).

## 8. Ficheros de este hito

| fichero | contenido |
|---|---|
| `vph_api.json` | las 106 cadenas con su tipo, función y sitios PIC; las 60 familias; los ficheros fuente de la zona; el diferencial |
| `extract_vph_api.py` | script reproducible de la extracción |
