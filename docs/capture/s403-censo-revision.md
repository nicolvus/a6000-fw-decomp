# S403 — revisión individual de las 226 etiquetas pendientes del censo (D1)

25-10-2026. Cada etiqueta `pendiente` del [censo S178](../../analysis/s178_census/pendientes.md) se revisó con un procedimiento
reproducible: [d1_census_review.py](../../analysis/s403_pendientes/d1_census_review.py) → [d1_census_review.json](../../analysis/s403_pendientes/d1_census_review.json).
Es una revisión **léxico-estructural** (cómo aparece la etiqueta, en cuántos modelos, con qué referencias PIC y léxico). No
reconstruye funciones ni cambia ningún veredicto del censo; los 222 `NO_VERIFICADO` conservan su estado. Sin ejecutar firmware.

## Resultado

| Clase (por la forma de las cadenas) | Etiquetas |
|---|---:|
| Módulo propio (la etiqueta abre la cadena) | 101 |
| Subetiqueta (siempre tras otro prefijo, p. ej. `[CDIAG][CTRLHDDEC][VSYNC]`) | 118 |
| Campo de formato (`>>[X]%x`) | 6 |
| Mixta | 1 |

- 21 de las 226 están solo en A6000 (0 en A7S y A6300); el resto aparece en los tres modelos y es infraestructura común.
- Léxico de captura (obturador, exposición, sensor, imager…): 8 etiquetas con alguna cadena. Ninguna acredita un papel en la
  captura: `[ENCAUDSYNC]` («SILENT = %x») es silencio de **audio** del codificador de vídeo; `[ENCOUCUDMG]` («EDIT SHUTTER SPEED ERROR»)
  es una cadena de error de edición de datos de cámara dentro de un gestor de salida; `[PBX]` y `[IN]/[IN1]/[IN2]` son campos de trazas
  `[CAMERA_MAIN_YC]` y `[CAM_IMAGER]` (volcados de parámetros y direcciones de procesos ZIT).
- Las ocho de prioridad 1 (`[SDF_ERR]`, `[CMDMLTSYNC]`, `[SYNCENCSTART]`, `[SYNCSETMODE]`, `[EVF]`, `[PANELEVF]`, `[PNLEVF]`, `[VSYNC]`) y
  `[SYS_SENSER_CA_PUTS]` (prioridad 0, una sola cadena) son diagnósticos de infraestructura (sincronización de codificación, panel/EVF,
  `SDF`) sin cadena que los vincule al obturador; las nueve están en los tres modelos (`[EVF]` con 6 cadenas en A6000 frente a 2 en A7S y A6300).

## Las cuatro `ACEPTO`, decodificadas a nivel de cadenas

| Etiqueta | Cadenas | Qué son (por texto) | A7S / A6300 |
|---|---:|---|---|
| `[EXL]` | 22 | Comprobaciones de dimensiones del procesado de imagen: `initCamdcv`, `calCamdcvTanz`, anchos múltiplos de 8/16, límites `hsiz_* > 2240`, inicialización PFR | 22 / 22 |
| `[SFR]` | 18 | Infraestructura de sistema entre CPUs: `CpuSelectComp`, `osal_id`, `MsgInfoUniqueIdImplanter`, `SystemCmdNotifyMode` (modos 2D/3D/INIT), tiempos de ejecución | 22 / 44 |
| `[IMAGING_IMG]` | 7 | Guardas de nulo de `Image::Clone`, `Image::Branch`, `Image::Create` y de `ImageParam` (solo A6000) | 0 / 0 |
| `[DECMODEMGR]` | 30 | Gestor de modo del decodificador de reproducción: `CMD_ID_BEGIN_DEC`, `PAUSE_FRAME`, `NEXT_FRAME`, `TERM_DEC`, mudo de audio/vídeo | 30 / 37 |

Ninguna se relaciona con la captura en el texto. La semántica funcional (cuerpos, llamadores) sigue `NO_VERIFICADO`.

## Límites

Una clasificación por forma de cadena no demuestra identidad funcional. Las etiquetas «módulo propio» y «subetiqueta» no se
elevan a hito. Reabrir una etiqueta solo si un hallazgo de captura la enlaza por código.
