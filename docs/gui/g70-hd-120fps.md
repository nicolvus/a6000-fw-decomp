# G70 — Full HD / HD 120 fps (PARCIAL: 1080p120 descartado; 720p120 con piezas en el firmware, cadena sin cerrar)

Fecha 15-11-2026. Solo estático (av-cam 3.21, `CautionConfig.so` 3.21); sin cámara, sin CFW, sin parche. Reproducible: `python3 -I scripts/imx210_fps_limits.py`, test `tests/test_imx210_fps_limits.py`.

## 1. Modos del sensor (corrige supuestos del encargo)
Los vídeo no usan 17 µs/línea: HMAX = 693 ciclos de 54,054 MHz = **12,82 µs** (17,1 µs solo es el barrido de 24 MP). Por eso 1124 líneas dan 60 Hz con VMAX 1300 y llegan a ~69 fps (margen de 12 líneas supuesto), no 52.

| Modo | Útil | HMAX | VMAX 60/50 | fps | fps máx. (VMAX=líneas+12) | Mpx/s |
|---|---|---|---|---|---|---|
| 0x0b/0x2f | 6000×4000 | 864 | 4176 | 14,98 | 16 | 360 |
| 0x01 | 2000×570 | 693 | 1300/1500 | 60 | 134 | 68 |
| 0x05/0x10/0x18/0x1a | 1996×1124 | 693 | 1300/(1350–1500) | 60 | 69 | 135 |
| 0x07 / 0x19 | 1996×1124 | 875 / 693 | 1287 / 1625 | 48 | 54 / 69 | 108 |
| 0x03 | 2000×800 | 693 | 1300/1500 | 60 | 96 | 96 |
| **0x12** | **2000×570** | 693 | **650/750** | **120 / 100** | 134 | 137 |
| 0x0a | 2000×232 | 693 | 300 | 260 | 320 | 121 |
| 0x0f | 1024×684 | 858 | 1050/1250 | 60 | 91 | 42 |

Sí hay modo ≥ 100 fps y ya está en la tabla de 13: **0x12 (120,0 / 100 Hz)** y 0x0a (260 Hz). El selector de vídeo `0x4380e43c` lo elige con el formato `cfg[+0x1d4]==4` (g50 / `imx210-video-readout.md` Sesión 3). Registro `ec` de 0x12: `131073` frente a `65537` del resto (marca HFR; significado INFERIDO).

## 2. Codificador
- **1080p120: descartado.** 1920×1080×120 = 249 Mpx/s; el modo de 1124 líneas no pasa de ~69 fps (lectura) y el tope medido de salida es 135 Mpx/s. Doble fallo, sensor y codificador.
- **720p120/100: hay código.** `ExCodecEncMp4` (av-cam 3.21) trae `[1280x720 100P][ActEnc]` y `[1280x720 100p][SetSeq]` y `[800x480 200P]`. El constructor de parámetros `0x43a7bba0` fija 0x500×0x2d0 (1280×720), VInType `0x20` en `0x436147a8` (log `ActEnc`), llamado desde `0x4361341c`. La A6000 no trae las cadenas `OUCRANK_120P_*` ni `setVRCS_..._120P_1920x1080` de la A6300 (esa sí codifica 1080p120). 2000×570×120 = 137 Mpx/s ≈ el tope de 135 Mpx/s (ligeramente por encima; las líneas útiles reales tras escalar a 720 líneas bajan el caudal codificado a 1280×720×120 = 110 Mpx/s).
- **Menú:** `CautionConfig.so` define los nodos `MovieRecordingSetting100_p_50M` (valor interno `0x14`) y `120_p_50M` (`0x15`), propiedades `0x0b=3, 0x0c=2`. Solo los lista `…SettingDefault` (22 nodos). La A6000 es el tipo 29 → `…Type04` (17 nodos, `_getSubNode` `0x108e71`, `tbb` idx 28 → `0x108ee2`), sin 100p/120p. Etiquetas «120p 50M» (0x204f727); formato de archivo `MovieFileFormatFRAMERATE_120p_MR`.

## 3. Veredicto
- 1080p120: **descartado** (límites de sensor y de codificador).
- 720p120 (HD 120): **viable en aritmética y con piezas presentes** (sensor 0x12, codificador MP4 720p100, nodo de menú 0x15); **no verificado** que `libObj` convierta el valor `0x15` en formato `cfg[+0x1d4]==4` ni que audio, buffering y MP4 acepten 120 Hz. Sin esa cadena la entrada de menú sería un interruptor sin efecto: no se implementó.
- Pieza mínima diseñada: añadir `120_p_50M` (y `100_p_50M` en PAL) al final de `Type04` (patrón G39/G58: lista nueva en segmento RW con relocalizaciones como `add_menu_entry.py`, sin sustituir) y verificar en el arnés con captura. Lo hecho hoy es la tabla de modos con test de bytes originales.

## 4. Ids de Backup
Si la opción exige un ajuste persistente nuevo (p. ej. frecuencia HFR), no se crea: queda para la tarea de infraestructura de ids de Backup (g69: solo 1 libre).

## 5. Prueba en el arnés (G75 T20, 16-11-2026)
El parche de lista (`scripts/gui/hd120_list_patch.py`, test `tests/test_g70_hd120.py`) se probó en vivo con el `/usr` de fábrica. Con XAVC S y NTSC, 120p 50M aparece en «Grabar ajuste», se elige y escribe en el Backup la clase de formato 4 (`0x1070c9a`). Está en gris («Función desactivada actualmente») en los modos automáticos y de escena por la regla de fábrica `isGrayedOutWithReason`, y habilitado en P/A/S/M. La lógica que corre es la copia de `viewUnified2.so`, no `cmn_view_processDataMgr.so`. Falta la grabación: la SD emulada no es SDXC. Detalle en [g75 Tarea 20](g75-arnes-e2e-objetivos.md).
