# S138 — el módulo `[CAMERA_MAIN_FC]` (9 trazas)

A6000 fw3.21 · `analysis/rea-independent/input/av-cam.bin` · vaddr = `0x43541000` + offset ·
regla de xrefs: **estricta** (`add rX,pc` con el `ldr rX,[pc]` más cercano), **13/13 sitios
recalculados a mano** (`analysis/s138_camera_main_fc/verify_sites.py`).

## Qué es

Capa de *glue* de `CAMERA_MAIN` hacia el subsistema de detección de caras/ojos **`Camera::FC`**.
La sigla **no se desarrolla**: su base textual es el namespace C++ `Camera::FC` (28 cadenas de
aserción, p. ej. `Camera::FC::FCTop::ExecApiNotifyStartTouch` `0x43cefa06`) y el árbol
`FC/**/*.cpp` (99 ficheros, `0x43cef12a`–`0x43cf707a`, S111). Código del módulo:
`0x437b7200`–`0x437b821e`. Impresor: logger privado OSAL `0x437b7158` (`r0=3`, `r1=5`, `r2=1`).

## Las 9 trazas (`0x43ca6944`–`0x43ca6aec`)

| vaddr | texto | sitios |
|---|---|---|
| `0x43ca6944` | `Eye data is invalid, but lc flag is true.` | `0x437b7268`, `0x437b72a6`, `0x437b72ee`, `0x437b7326` |
| `0x43ca6980` | `OSAL_ERROR: osal_alloc_timer` | `0x437b7548` |
| `0x43ca69af` | `OSAL_ERROR: osal_set_timer` | `0x437b7570` |
| `0x43ca69dc` | `OSAL_ERROR: osal_free_timer` | `0x437b77f4` |
| `0x43ca6a0a` | `APP MODE ERROR: face_on, obj_on` | `0x437b787c` |
| `0x43ca6a3c` | `OSAL_ERROR: BatteryInfo` | `0x437b7db6`, `0x437b7df6` |
| `0x43ca6a66` | `ReplyForTouchShutter ERROR - NULL cb_func` | `0x437b7fae` |
| `0x43ca6aa2` | `SetRequestReplyForTouchShutter ERROR - multiple request` | `0x437b8200` |
| `0x43ca6aec` | `SetRequestReplyForTouchShutter ERROR - NULL cb_func` | `0x437b820e` |

0 cadenas sin referencia. 13 sitios en **7 funciones**: `0x437b7200` (4), `0x437b74a4` (2),
`0x437b7778` (1), `0x437b7844` (1), `0x437b7d6c` (2), `0x437b7ea0` (1), `0x437b81f0` (2).

## Hallazgos verificados

* **Flags del contexto**: `[ctx+0xde]` y `[ctx+0xdf]` deben valer 1 (ojos); `face_on`=`[ctx+0x49c]`,
  `obj_on`=`[ctx+0x49e]` → `APP MODE ERROR` si ambos activos (`0x437b7866`–`0x437b787e`).
* **Disparo táctil**: callback guardado en la ranura global `0x43eb3bf0` (inicial 0) e invocado
  con `blx r1` en `0x437b7fa2`; flag de turno en `0x43f9a564`.
* **API exportada por *thunks*** (colas de ramificación `b.w`): `0x43aef72e`→`ReplyForTouchShutter`
  (`0x437b7ea0`, llamado desde `0x437b668c`), `0x43aef732`→copia del estado de áreas
  (`0x437b7fe4`, desde `0x4378f6a6`), `0x43aef736`→`SetRequestReplyForTouchShutter`
  (`0x437b81f0`, desde `0x4380a4c8` ← `0x43808058`). Cola adicional a `0x437b7598` en `0x43aef9ca`.
* **Única función sin referencia entrante**: `0x437b7778` (`osal_free_timer`), tras un barrido
  inverso de ramas (`bl`/`b.w`/`blx`/`b`) sobre toda la imagen.
* **No participa en la cadena de disparo táctil** (`0x3011` → `CamUser` → `CaptureStart`): ninguna
  de las 8 funciones de la cadena llama a la zona del módulo ni a la biblioteca `Camera::FC`.
  Su API de disparo táctil está cableada, pero por la capa de captura (`wrapper/Face.cpp` →
  `FC/Api/fc_api_tracking.cpp` `0x43cefa43`).

## Diferencial

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---:|---:|---:|
| token `[CAMERA_MAIN_FC]` | **9** | 0 | 0 |
| núcleos de texto presentes | 9 | **0/9** | **0/9** |
| fragmentos de código (8) | 8 | **0/8** | **0/8** |
| `TouchShutter` | **3** | 0 | 0 |
| `Camera::FC::` / `FC/` | 45 / 101 | 45 / 101 | 45 / 101 |

Material **propio de la A6000 fw3.21**; la biblioteca `Camera::FC` es **idéntica en los tres**.

## NO VERIFICADO

Fichero fuente del módulo (ninguna traza cita un `.cpp`); si `0x437b7778` se invoca desde otro
binario del paquete de firmware; significado del flag `lc`; destinatario de los mensajes OSAL
(temporizador, `BatteryInfo`); si el camino táctil del FC debía enlazar con `0x3011`.

[Informe](../analysis/s138_camera_main_fc/camera_main_fc.md) · [JSON](../analysis/s138_camera_main_fc/camera_main_fc.json)
