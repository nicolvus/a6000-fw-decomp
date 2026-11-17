# G78 — Dual Video Recording = grabación proxy de Sony: presente de fábrica sin menú (PARCIAL)

Fecha 16-11-2026 (G75 Tarea 26). Análisis estático sobre `libObj` 3.21 y av-cam 3.21, más una prueba en la VM de av-cam. Sin cámara ni CFW. Pruebas: `tests/test_g78_proxy.py` y `tests/test_avcam_ee_start.py::test_av_cam_guarda_el_proxy_de_la_orden_0x4000`.

## 1. Qué es
El α7R III graba a la vez el vídeo principal y una copia ligera (*proxy*, 720p MP4) o en dos tarjetas. La A6000 tiene una sola ranura, así que la versión aplicable es la **proxy**. En la A6000 la opción de menú «DualRecImageSize» es otra cosa: la foto durante el vídeo.

## 2. Cadena de fábrica (VERIFICADO por bytes)
| Capa | Pieza |
|---|---|
| Nombres (`libObj`) | `PARAMID_MOVIE_PROXY` `0x99bd`, `…SIZE_PROXY` `0x99be`, `FRAME_RATE_PROXY` `0x99bf`, `…ASPECT_RATIO_PROXY` `0x99c0`, `…CONTENT_TYPE_PROXY` `0x99c1`, `…QUALITY_PROXY` `0x99c2`, `…SIZE_H_PROXY` `0x99c3`; `VALUEID_MOVIE_PROXY_ON/OFF` `0x498/0x499`, `HD720_PROXY` `0x49b`, `FR_30_25P_PROXY` `0x4a0`, `CONTENT_TYPE_MP4_PROXY` `0x4a7`, etc. |
| UI (`libObj` `0x5ffb20`) | Arma `MSGID_SET_MOVIE_FORMAT_CMD` `0x750e` con el formato del vídeo y los 7 parámetros proxy. **PROXY = ON (`0x498`) si el byte global `0x10ab200` ≠ 0**; ese global lo pone a 1 `0x5f8ec6` en los modelos `model/MOVIE_REC_MANUAL_PROXY` y `model/MOVIE_REC_MULTI_CTRL_PROXY`. En la A6000 ningún menú elige esos modelos. |
| `ObjCamera` (`CamMsgConv` `0x9b6ad4`) | `0x750e` → orden LIRO **`0x4000`** (EE, 0x17 B): proxy → byte `0xe`, tamaño `0xf`, cadencia `0x10`, aspecto `0x11`, tipo `0x12`, calidad `0x13`, ancho `0x14`. Si falta cualquier parámetro, registra un error y no envía la orden. |
| av-cam (manejador `0x43804058`) | Guarda el byte `0xe` en `0x43edf684+0x2c`. Si cambia, registra el evento `0x2042` con tamaño, cadencia, aspecto y ancho del proxy. **Probado en la VM:** proxy ON → 1, OFF → 0. |
| av-cam (vídeo) | Salida «PROXY PIN» del EE (`[PROXYPin] vx vy rx ry`) y segundo codificador (`ActEnc_2nd`) |
| `libmpr` | Ficheros y marcas proxy (`FlashProxyQuadrupleMark`, `Proxydischargemark`, `2ndFullPath`) |

## 3. Veredicto
**Viable en principio (PARCIAL):** el firmware trae la cadena completa de grabación proxy, igual que la de S&Q (g76), y solo falta la petición. La pieza mínima sería un ajuste CFW «Proxy» y una cueva que ponga a 1 el global `0x10ab200` (o que añada `0x99bd` = ON) antes de que `0x5ffb20` arme el formato.

**Límites:**
- **Caudal (INFERENCIA):** 1080p60 más un proxy 720p30 da unos 152 Mpx/s, por encima de los ~135 medidos (g50/g70). El proxy solo cabría con el vídeo principal a ≤ 30p.
- **Valores proxy en la UI:** tamaño, cadencia y demás vienen de campos del modelo (`+0x224…+0x238`) que valen −1 fuera de los modelos proxy. Con −1 no se añade el parámetro y el conversor rechazaría la orden entera. Así que la cueva debe dar también valores válidos (p. ej. 720p, 30p, MP4) o activar el modelo proxy de Sony. NO_VERIFICADO.
- **Arnés:** `0x5ffb20` no se ejecutó con las acciones que el arnés alcanza (MOVIE se detiene en el aviso de la tarjeta, E2E-14), así que la ruta de la UI no se puede probar en vivo hasta que se pueda grabar.

## 4. Pendientes (DVR-F1…F3)
1. DVR-F1: inyectar en el arnés `0x750e` con un juego completo de parámetros (`Z`; valores tomados de la UI de fábrica cuando la grabación funcione) y ver la `0x4000` con proxy ON en av-cam.
2. DVR-F2: ajuste «Proxy» en la carpeta CFW y cueva en `0x5ffb20` (global + valores proxy), con Unicorn y arnés.
3. DVR-F3: grabar en el arnés y comprobar los dos ficheros y el caudal (depende de E2E-14).
