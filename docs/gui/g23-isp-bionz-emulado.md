# G23-ISP — Modelo por software del procesador de imagen BIONZ X (T9, 12-11-2026)

Código: `scripts/gui/isp/` (`extrae_tablas.py`, `modelo.py`, `valida_curvas.py`, `compara_real.py`, `extrae_bandas.py`, `prueba_shader.py`), `scripts/gui/harness/isp_web.py` (shader + panel; enganchado en `live.py`/`sensor_web.py`), `tests/test_gui_isp.py`. Datos: `analysis/gui/isp/` (212 KB, versionable). Etiquetas: **REAL** (bytes/volcado) · **APROX** (estructura razonable, constante sin verificar, `shortcut:` en el código) · **NO_VERIFICADO**.

**Límite de fondo.** El ISP de la BIONZ X es hardware fijo: el firmware solo le programa tablas. Lo que se modela es lo que el firmware le entrega (curvas, matrices, parámetros), no el cálculo interno del chip. La entrada del emulador no es el RAW del sensor sino sRGB (APROX).

## 1. Pipeline modelado y estado de cada etapa
| # | Etapa | Estado | Evidencia / límite |
|---|---|---|---|
| 1 | sRGB → lineal × exposición `k` | APROX | no hay RAW; `k` = nivel de entrada de la LUT, deslizador (con S-Log3 el ajuste da `k` = 5,48: 18 % gris en el índice ≈ 67 de 2047) |
| 2 | Black Level | APROX | existencia/orden por G16; 0,002 por unidad inventado |
| 3 | Matriz de color 3x3 | REAL (valores) | Backup `0x30001`, 15 matrices int16 (1024 = 1,0), índices 0–7 en `+0x48`, 8–14 en `+0x400`, paso 18 B (G27 §5; filas suman 1024, comprobado). Movie = índice 0 (G27). Resto de Color Mode → matriz: NO_VERIFICADO (se usa la 0); se aplica sobre sRGB lineal, no sobre RGB de sensor |
| 4 | Gamma por número | REAL | LUT de 2048 u16 (salida 10 bit) por curva, tabla `0x44001404` (A6000), `0x43ffa290` (A7S), `0x441bc70c` (A6300), cola de 13 u16 (no decodificada). Valor app→curva: G25/G18 (3→`0x16`, 4/5→`0x0a`, 6–9→`0x18`–`0x1b`, 10→`0x1c`, 11→`0x1d`, 2→`0x1f` A6300); Still en foto = `f00` |
| 5 | Saturación, Color Phase, Color Depth | APROX | −8 = B&W es REAL (G27); pasos 0,125/unidad, 2°/unidad, 6 %/unidad y pesos por tono inventados |
| 6 | Detail | APROX | máscara de enfoque sobre luminancia, solo en el shader |
| 7 | Black Gamma, Knee, YCbCr/rango, DRO, estilo creativo, ruido | NO_VERIFICADO (no implementado) | rodilla/rango probablemente en la cola de la curva; sin decodificar |
| 8 | Obturador (EFCS/Silent) | MEDIDO | cocientes por 8 bandas arriba→abajo de `r87*/medidas.json` (fotos del usuario, `extrae_bandas.py`); la tabla EFCS de la cámara cambió entre tandas, por eso se ofrece cada tanda por separado |

## 2. Fuentes de las tablas (extraídas por `extrae_tablas.py`; todo reproducible)
- Curvas: 87 (24 A6000, 31 A7S, 32 A6300 incl. repetidas), todas monótonas; `a6000_v0a` = `a7s_v0a` byte a byte (G16). Las de vídeo `0x16`, `0x18`–`0x1d` no existen en la A6000: el CFW las instala desde la A7S; `0x1f` (S-Log3) desde la A6300.
- Selector A7S `0x43cab54d`: (3→22, 4→10, 5→0/0, 6–9→24–27, 10→28, 11→29); el de la A6000 está en blanco (`0x43cb56e6`, G16).
- ids de Backup de PP: constructor `libObj.so 0x4a9a56` ejecutado en Unicorn → `[obj+0x5dc+(perfil·31+i)·4]`: perfil 0–3 en `0x10702f8+p…`, 4–9 en `0x107062b+(p−4)…`, PP10 en `0x1070631…`, 341 ids distintos, 1 B cada uno (G36). Índices i: 0 Color Mode, 1 nivel, 7 Gamma, 8/9 Black Gamma, 10 Black Level, 11 Knee, 17 Detail, 23–28 Color Depth RGBCMY, 29 Saturación, 30 Phase (G23/`pp_menu_spec`). Rangos = validador de la A6000.
- **El volcado real (`20261105-volcado-total-nvram`) NO contiene ajustes PP significativos**: la A6000 de serie no usa esos elementos (valores sueltos, p. ej. gamma = 0, no definido). El panel parte del perfil neutro del modelo y escribe en el `nvram.json` del perfil; negativos como int8 (NO_VERIFICADO).

## 3. Validación numérica (`valida_curvas.py` → `validacion_curvas.json`)
- **S-Log3 (A6300 `0x1f`): RMSE 0,001** contra la fórmula pública (de memoria: `(420+261,5·log10((x+0,01)/0,19))/1023`) con `k` = 5,48: identificación VERIFICADA por forma. Negro 42/1023.
- Curvas de cine/log de la A7S: `0x1c` encaja mejor con S-Log2 (RMSE 0,019), Cine1–4 entre 0,022 y 0,037 con la misma fórmula: el ajuste NO discrimina Cine de S-Log2 con `k` libre. `0x16` llega a 1 727/1 023 (rango extendido; ¿ITU709(800%) en vez de ITU709?). **Contradicción abierta**: G25 §1 da app 10 = ITU709(800%) y 11 = S-Log2, pero la forma pone S-Log2 en `0x1c` (selector 10). Sin cerrar; el panel muestra el nombre de G25 con «INFERENCIA».
- Movie/Still (A6000): BT.709 con `k` libre RMSE 0,043/0,035: forma de 709 con más contraste, no es 709 puro.
- Las fórmulas S-Log2/S-Log3/BT.709 no están en el repo: confirmar contra los documentos de Sony.

## 4. Primer caso real (`compara_real.py`, fotos `~/Desktop/16161111`)
ARW A6000: el RAW trae la vista previa JPEG 1616×1080 hecha por la BIONZ X. MakerNote de DSC03773/3779: Creative Style **Standard**, DRO 3 (Auto), 6500 K. Modelo: RAW − negro (512) × WB as-shot → sRGB lineal (dcraw) → exposición `k` óptima → curva → comparar.
- DSC03773 (mecánica, 1/350 f3,5): ΔE76 medio **5,6–7,1 con todas las curvas** (Still `f00`: 6,9, `k` 2,9; Cine1: 5,6); no hay curva que gane con claridad. Diferencias por canal −0,6…−2,3/255 (Still).
- DSC03779 (f5,6): Still ΔE76 medio 14,5 (p95 44,5).
- Lectura honesta: error alto y común a todas las curvas; falta DRO Auto (no modelado), la matriz de Creative Style Standard (se usa la de Movie), demosaico, ruido y escena no neutra. Curva tonal real medida (mediana verde por bandas, en los JSON): lineal 0,0023→0,14, 0,011→0,19, 0,049→0,45, 0,22→0,82 (escena oscura, pocos puntos altos).

## 5. Calibrar (flujo)
1. Misma escena en ARW+JPEG por cada PP/gamma (`compara_real.py *.ARW --gamma N --ajustes '{"saturation":2}' --salida x.json`); `--barrido` lista el ΔE de cada curva. Para pares sin RAW: `--entrada original.jpg --foto camara.jpg`.
2. Ajustar `PASO_*` y `MATRIZ_COLOR` en `modelo.py` (y los espejos de `tablas_json`) hasta bajar el ΔE; no cerrar sin una escena por PP. Criterio: ΔE76 medio < 3.
3. Medir una carta de grises (RAW) para fijar `k` por curva y la entrada real.

## 6. Verificación hecha
- `pytest tests/test_gui_isp.py` (10): curvas monótonas/reproducibles desde `av-cam.bin`, matrices, S-Log3, LUT CPU, ids de Backup (`0x10701ea` = gamma PP1…), ΔE, bandas y **shader WebGL2 = CPU en 8 colores × 4 PP (diferencia máxima 0/255, Chromium headless + SwiftShader)**. No cubre `Detail`.
- Captura del panel: `analysis/gui/g22/harness/t9/panel.png` (gitignored). No se ha probado con QEMU ni en webcam física; el rendimiento a ≥ 15 fps a 640×480 no se midió (SwiftShader).
