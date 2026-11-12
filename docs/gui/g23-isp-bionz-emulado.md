# G23-ISP — Modelo por software del procesador de imagen BIONZ X (T9, 12-11-2026; fase 2 el mismo día)

Código: `scripts/gui/isp/` (`extrae_tablas.py`, `raw_entrada.py` (nuevo), `modelo.py`, `valida_curvas.py`, `compara_real.py`, `extrae_bandas.py`, `prueba_shader.py`), `scripts/gui/harness/isp_web.py` (shader + panel; enganchado en `live.py`/`sensor_web.py`), `tests/test_gui_isp.py`. Datos: `analysis/gui/isp/` (versionables: `curvas.npz`, `tablas.json`, `sr2_standard.json`, `geometria_arw.json`, `compara_arw.json`, …). Etiquetas: **REAL** (bytes/volcado/RAW de la cámara) · **MEDIDO** (ajuste a fotos reales, reproducible con script) · **APROX** (estructura razonable, constante sin verificar, `shortcut:` en el código) · **NO_VERIFICADO**.

**Límite de fondo.** El ISP de la BIONZ X es hardware fijo: el firmware solo le programa tablas. Lo que se modela es lo que el firmware le entrega (curvas, matrices, parámetros), no el cálculo interno del chip. En la ventana en vivo la entrada no es el RAW del sensor sino sRGB (APROX); con ARW reales (`compara_real.py`) la entrada sí es RAW.

## 1. Estado por etapa
| # | Etapa | Estado | Fuente / evidencia / límite |
|---|---|---|---|
| 1a | Entrada RAW: negro, blanco, WB as-shot | **REAL** | SR2Private cifrado de cada ARW (§4): `0x7310` negro 512×4, `0x7313` WB RGGB (3148, 1024, 1024, 1644)/1024; blanco 16383 (`rawpy`) |
| 1b | Demosaico | **REAL** (algoritmo de OpenCV, no el de Sony) | mosaico RGGB 6024×4024; diferencia con la media 2×2 a resolución de vista previa 0,002 (inapreciable) |
| 1c | Corrección de lente (distorsión) | **MEDIDO** | la vista previa de la BIONZ X está corregida (barril) y recortada/escalada; el ARW de la A6000 no trae sus parámetros (SR2 sin `0x7032–0x7036`): se ajusta por foto `k1, k2, escala, dx, dy` (`geometria_arw.json`, correlación de gradientes 0,5–0,82); viñeteo: no corregido |
| 1d | Exposición `k` / DRO Auto | **MEDIDO** (`dro_auto_k`) / **NO_VERIFICADO** (algoritmo) | DRO Auto (MakerNote `0xb025` = 3) cambia la ganancia efectiva de 0,62 a 1,9 según la escena; `k = clip((0,073/p50)^0,228; 0,66; 1,46)` con p50 = mediana del verde lineal (31 ARW; error RMS en log k de 0,13). El algoritmo real (`Stage_BDRO.cpp`, `JudgeBdroRslt`, `SetBdroIdtData`, `SetDAEParam` en `av-cam.bin` 0x7861fa/0x78a350/0x764a17/0x764999) no se ha analizado |
| 2 | Matriz de color | **REAL** | `0x7800` de los 33 ARW (Creative Style Standard) = matriz de Backup `0x30001` índice 0 (y 2, 5–8) byte a byte (`(1292,−180,−88,−44,1340,−272,−24,−108,1156)/1024`); se aplica sobre el RGB de sensor tras WB, con cada canal saturado a 1 (MEDIDO: −0,6 ΔE en fotos con cielo quemado) |
| 2b | Deltas de color (conjuntos de 24 B, Backup `0x30001` `+0x100`/`+0x480`) | datos **REAL**, uso **NO_VERIFICADO** | 24 conjuntos de 12 int16 leídos del volcado; el núcleo elige `+0x7b` (siempre 7) y `+0x7c` (Pro 7, ITU709 Matrix 6, Movie ninguno, Still 0, Cinema 4); lectura portada de `0x437a44d0` (`modelo.conjunto_deltas`, REAL) → 3 variantes de 8 valores (4 con signo, 4 sin signo) sobre una base de ejecución NO_VERIFICADA; en la foto se aplica `tono4` (4 ejes de tono, giro + ganancia, valores MEDIDOS, §4.2) |
| 3 | Gamma por número (2048 pt) | **REAL** | `av-cam.bin` A6000/A7S/A6300 (§3). Foto Still/Standard: curva de 512 pt `0x7802` del propio ARW (`sr2_std`, idéntica en los 33 ARW; escala absoluta real, `k = 1`) |
| 3b | Cola de 13 u16 de cada curva | parcial **REAL** | [10] = número de gamma (87/87 curvas), [11] = 0 vídeo / 1 foto (87/87); [0–8], [9] (A6000 4, A7S/A6300 7) y [12] (1, 2; S-Log3 = 32) son códigos de clase sin significado establecido (2/3/4 separan «estándar» de «rango ancho»: 0x16, 0x18–0x1d, 0x1f) → NO_VERIFICADO |
| 4 | Black Level / Black Gamma / Knee | estructura **REAL del CFW** (`pp_tone.c`, G33), constantes **ESTIMADAS** | operaciones enteras sobre los 2048 puntos, portadas a `modelo.curva_pp` y al shader (CPU = shader 0/255). No son valores de Sony: el firmware original de la A6000 no implementa estas funciones (G32/G33) |
| 5 | Saturación, Color Phase, Color Depth | **APROX** | −8 = B&W es REAL (G27); el firmware reenvía los valores (`+0x24…+0x2f`) en un mensaje de colorimetría a otro procesador (G32/G34): ni escalas ni pesos por tono están en `av-cam`. Medición: en los ARW Standard la vista previa tiene un 25 % más de croma que el modelo (cociente 0,56–0,83 por tono) y desvío de tono 9° en rojos; una saturación global +1/+2 solo baja ΔE de 5,4 a 5,1 |
| 6 | Detail | **APROX** | máscara de enfoque sobre la luminancia (shader = CPU 0/255 en un borde); el núcleo calcula ganancias APC con tablas por ISO y estilo (G33), no mapeadas |
| 7 | YCbCr / rango (vídeo/datos), ruido, nitidez del JPEG | **NO_VERIFICADO** | sin dato; la vista previa real lleva reducción de ruido y realce que el modelo no tiene |
| 8 | Obturador (EFCS/Silent) | **MEDIDO** | cocientes por 8 bandas de `r87*/medidas.json` (`extrae_bandas.py`) |

## 2. Fuentes de las tablas (`extrae_tablas.py`; todo reproducible)
- Curvas: 87 (24 A6000, 31 A7S, 32 A6300 incl. repetidas), todas monótonas; `a6000_v0a` = `a7s_v0a` byte a byte (G16). Las de vídeo `0x16`, `0x18`–`0x1d` no existen en la A6000 (el CFW las instala desde la A7S); `0x1f` (S-Log3) desde la A6300.
- Selector A7S `0x43cab54d` y A6300 `0x43db1e2b` (índice = valor de app, pares foto/vídeo): 3→22, 4→10, 5→0/0, 6–9→24–27, 10→28 (`0x1c`), 11→29 (`0x1d`), 12→`0x1f` (solo A6300); el de la A6000 está en blanco (`0x43cb56e6`).
- ids de Backup de PP: constructor `libObj.so 0x4a9a56` en Unicorn → 341 ids distintos, 1 B cada uno (G36); índices i: 0 Color Mode, 1 nivel, 7 Gamma, 8/9 Black Gamma, 10 Black Level, 11–15 Knee (modo, sens., máx., punto, pendiente), 16/17 Detail, 23–28 Color Depth, 29 Saturación, 30 Phase.
- **El volcado real no contiene ajustes PP significativos** (la A6000 de serie no los usa): el panel parte del perfil neutro y escribe en el `nvram.json` del perfil; negativos como int8 (NO_VERIFICADO).

## 3. Curvas: identificación y tabla tipo→id→matriz (cierra la contradicción G25 §1)
- **VERIFICADO por forma** (`valida_curvas.py` + ajuste afín en `tests/test_gui_isp.py`): `0x16` = BT.709 (RMSE 5·10⁻⁴, k 2,2); `0x1c` = **S-Log2** (RMSE 3·10⁻⁴; 0,0188 sin afín); `0x1f` = S-Log3 (RMSE 0,001); `0x1d` no es log (RMSE 0,043 con log libre; 0,0013 con familia gamma `a·(x+c)^p+d`) → compatible con ITU709(800%). Las fórmulas públicas están de memoria (`valida_curvas.py`).
- **Cadena (VERIFICADO con bytes):** `CamMsgConv` original de la A6000 (`libObj.so 0x9b3728`: `cmp r0,#0x480 → movs r3,#0xa`; `0x9b372e: cmp #0x481 → movs r3,#0xb`) y de la A7S (`0x92c580`) escribe **selector 10 para VALUEID 0x480 y 11 para 0x481**. La lista de nombres de `libObj` (`0xfde85c`) trae `VALUEID_PP_GAMMA_SLOG2` antes de `…_ITU709_800`, y G25 §1 da App2Obj 10 → 0x481, 11 → 0x480. Por tanto: **app 10 = ITU709(800%) → 0x481 → selector 11 → curva `0x1d`; app 11 = S-Log2 → 0x480 → selector 10 → `0x1c`.** Hasta hoy `modelo.CURVA_VIDEO` usaba selector = app (10→`0x1c`): estaba cruzado y el panel mostraba S-Log2 con la curva de ITU709(800%). Corregido (10→`a7s_v1d`, 11→`a7s_v1c`). El parche del CFW (`patch_libobj_pp.CAMCONV_TABLA`) ya intercambia esas dos entradas, así que la cámara con CFW es coherente; G25 §3 («`0x1c` = S-Log2, selector 10») era correcto y el error era leer «selector 10» como «app 10».
- **Tabla tipo→id→matriz de Color Mode de la A6000 (VERIFICADO, G27 + bytes `0x43ca66f2` = 15…21 y volcado):** VALUEID tipo 0 STD (creative style) → id 0 (=`0x13`); 1 TONE1 → `0x0f`; 2 TONE2 → `0x10`; 3 Pro → `0x11`; 4 ITU709 Matrix → `0x12`; 5 Movie → `0x13`; 6 Still → `0x14`; 7 Cinema → `0x15`; (+0x7a matriz, +0x7b, +0x7c): `0x0f`/`0x15` (8,7,4), `0x10` (8,7,5), `0x11` (6,7,7), `0x12` (7,7,6), `0x13` (6,7,0xff), `0x14` (0,7,0). Los índices de matriz 0, 6, 7, 8 son idénticos (la matriz 3×3 es la misma en todos los Color Mode de la A6000; la diferencia entre modos está en los conjuntos de deltas, §1 fila 2b). Las otras matrices de Backup (1, 3/4, 9–14) no las usa ningún Color Mode de la A6000; 14 = identidad. Nombres del panel: los de G24 (Pro 3, ITU709 Matrix 4, Movie 5, Still 6, Cinema 7; 8 B&W = Movie + saturación −8; 9–11 S-Gamut… solo en A7S/A6300).
- Movie/Still (A6000 `0x0a`/`f00`): forma de BT.709 con más contraste, no 709 puro (RMSE 0,043/0,035 con k libre).

## 4. RAW ↔ vista previa de la BIONZ X (`compara_real.py`, `raw_entrada.py`; 33 ARW de `~/Desktop/16161111`, e26-r85)
Todos: ISO 100, Creative Style **Standard**, DRO **3 (Auto)**, 6500 K. Hallazgos nuevos:
1. **SR2Private**: IFD `0xc634` → `0x7200/0x7201/0x7221` (offset, longitud, clave) y cifrado `sony_decrypt` (LFSR de dcraw); descifra bien (209 etiquetas coherentes). Da negro, WB, matriz `0x7800` y curva `0x7802` (512 pt) idénticos en los 33 ARW (`sr2_standard.json`).
2. **La vista previa no es el RAW sin más**: lleva corrección de distorsión (el RAW es de barril, la vista previa recta) y viene del fotograma completo 6024×4024 (no del recorte 6000×4000). Sin alinear no hay comparación píxel a píxel: ese era el grueso del ΔE 14,5 de DSC03779.
3. **DRO Auto es una ganancia de escena**: escenas oscuras (mediana 0,014) k* = 1,9; claras (0,7–0,9) k* = 0,62–0,73.
**Resultado (`compara_arw.json`; 32 de 33 ARW con alineación fiable, correlación ≥ 0,45; DSC03767 es una pared lisa y usa la geometría de DSC03769):**
| Exposición `k` | ΔE76 medio (media / mediana de las 32 fotos) | mín–máx | fotos < 3 | fotos < 5 |
|---|---|---|---|---|
| `k = 1` (sin DRO) | 6,4 / 5,2 | 1,5–12,8 | 1 | 14 |
| DRO Auto aproximado (`dro_auto_k`, sin ver la vista previa) | **5,4 / 5,4** | 2,5–7,7 | 1 | 13 |
| `k*` óptimo por foto (cota inferior de «solo ganancia») | **4,7 / 4,7** | 1,5–7,7 | 3 | 20 |

Antes (primer pase, media 2×2, matriz de Movie/dcraw, sin alinear): DSC03773 5,6–7,1 → **2,9** (`k*`) / 5,8 (DRO auto); DSC03779 14,5 → **5,6** (`k*`) / 5,7 (DRO auto) / 8,2 (sin DRO). Por zonas de la vista previa (media de las fotos; sin DRO → DRO auto): sombras 7,9 → 5,1; medios 10,3 → 7,0; altas 5,4 → 5,4; **saturados (C* > 40) 15,5 → 12,4**; **planos (sin bordes) 4,7 → 5,0**.
**Objetivo ΔE76 < 3: NO alcanzado en general** (con `k*` solo DSC03806 1,5 —escena casi negra—, DSC03803 2,6 y DSC03773 2,9). Residuo explicado con datos:
- **Croma** (zona saturados 12–15): la vista previa tiene ~25 % más de croma que el modelo (cociente 0,56–0,83 por tono) y los rojos están 9° desviados; el estilo Standard aplica conjuntos de deltas de color (fila 2b) cuya semántica no está decodificada; una saturación global solo baja de 5,4 a 5,1 porque el defecto es por tono. Es el mayor bloque del error y es **recuperable**: requiere decodificar los conjuntos de 24 B (`+0x7b = 7`) con una escena de color conocido.
- **Medios tonos** (7,0): DRO real es parcialmente local (la mediana por bandas de señal cambia entre fotos con la misma curva) y no solo una ganancia; con `k*` todavía queda 4,7.
- **Planos** (4–5): ni el desalineado ni el realce explican este error; es tono/color (los dos puntos anteriores) más reducción de ruido y viñeteo (no corregido).
- No es el demosaico ni el negro/WB (REAL): la diferencia lineal media entre media 2×2 y demosaico real es 0,002.

### 4.1 T9-D y T9-B (12-11-2026)
- **T9-D sin material**: los 217 ARW del equipo (95 en `/home/nicolas/Documents/a6000`, incluidos `test images/` y `analysis/camera-dumps/`, y 122 en `~/Desktop`) tienen MakerNote `0xb020` = **Standard** (y `0xb029` color mode igual); no hay ningún ARW Vivid/Portrait/Landscape/B/W, así que no se añadieron matrices ni curvas. Hace falta disparar una escena por estilo en ARW+JPEG.
- **T9-B, firmware (REA, una sesión)**: `JudgeBdroRslt` = `FUN_438e8204` (única xref de la cadena en `0x438e84f8`) **no es el tono local**: elige el resultado del DRO (1/2/3 y máscara de motivos `bVar21`) comparando estadísticas de escena (`param_3+0x30/+0x24/+0x68/+0x98/+0x104`) con 2 juegos de 12 umbrales de un bloque de ajuste (`+0x86…+0xa5`; el segundo si `param_1+0x90 == 7`) interpolados por ganancia (Q15) y lo guarda en `+0xa7/+0xa8`. `SetBdroIdtData` = `FUN_4379f584` solo copia un bloque de **0x134 B** del estado (`+0x385c`) al bloque BDRO; la curva/ganancia local la calcula el hardware con esos parámetros de tiempo de ejecución (no estáticos en `av-cam.bin`). NO_VERIFICADO: el contenido de ese bloque (requiere traza en cámara/QEMU del ISP).
- **T9-B, medida** (32 ARW, 1/4 de resolución, zona medios L* 30–70 de la vista previa): sin DRO 10,9; `dro_auto_k` 7,4; mejor ganancia local probada (`k = (a/blur(log G))^b`, σ 10–30 px, 64 combinaciones) 6,7–6,8, no mejor que la global (6,7 con σ = 0); **cota con `k*` óptimo por foto para medios: 5,5, de ello 4,4 solo en a\*b\***. Conclusión: **criterio < 4 en medios NO alcanzable con DRO**: el residuo es croma (T9-A). `dro_auto_k` se mantiene.

### 4.2 T9-A deltas de color (12-11-2026)
- **Firmware (REA, una sesión, cerrada):** `0x437a44d0` lee el conjunto `idx` como **24 int8** (no 12 int16: los `-32640` eran `0x80 0x80`) y devuelve 3 × 8 int16: `v0 = base + s[0:8]`, `v1 = v0 + s[8:16]`, `v2 = v0 + s[16:24]`. `base` (`0x437a4450`) = 4 int8 + 4 u8 de una estructura de ejecución (`+0x34…0x37` con signo, `+0x30…0x33` sin signo; o de `FUN_437a1514()+0x1a` si `+0xa8 == 1`): no está en `av-cam.bin` ni en el volcado (NO_VERIFICADO). `0x437a3014` interpola entre las 3 variantes según `param_2 >> 16` (umbrales u16 en `+0x120…+0x12c`, Q8; probablemente nivel de señal/ISO) y `0x43aee18c` escala los 4 primeros ×4 y los 4 últimos ×8 (los últimos multiplicados por una ganancia). Los conjuntos 4 y 11 llevan `-128` en los 4 sin signo (croma a cero: B/N/sepia). Estructura deducida: **4 ejes de tono con giro (con signo) y ganancia (sin signo)**; el significado exacto de los registros del bloque de color es de hardware.
- **Implementación:** `modelo.conjunto_deltas` (puerto exacto) y `modelo.tono4` (4 ejes sobre atan2(Cr, Cb), interpolación lineal; ejes −122/−26/50/124°, giros 8,5/−4,4/35/−6,9°, ganancias 1,17/1,31/0,60/1,31), ajustados en 16 ARW y validados en los otros 16 (saturados 12,1 → 6,7 en el grupo de validación). Solo en foto (`aplica(..., foto=True)`); vídeo y shader sin cambio.
- **Medida, 33 ARW a resolución completa (`compara_real.py`):**

| Modo | ΔE76 medio | sombras | medios | altas | saturados | planos |
|---|---|---|---|---|---|---|
| antes, `dro_auto_k` | 5,4 | 5,1 | 7,0 | 5,4 | 12,4 | 5,0 |
| ahora, sin DRO | 5,6 | 7,8 | 9,8 | 4,4 | 10,2 | 3,1 |
| ahora, `dro_auto_k` | **4,8** | 5,0 | **6,5** | 4,4 | **7,1** | 3,7 |
| ahora, `k*` | 3,9 | 4,4 | 5,9 | 4,2 | 7,0 | 2,5 |

  **Criterio saturados < 5 NO alcanzado (7,1)**; medios (T9-B) 7,0 → 6,5 (5,9 con `k*`), tampoco < 4. Para cerrar hace falta la base en ejecución (traza del bloque de color en cámara o QEMU del ISP) o una carta de color.

## 5. Calibrar (flujo)
1. `compara_real.py ARW… --salida x.json` (ΔE por foto, zonas y los tres modos de exposición); `--barrido` prueba cada curva; `raw_entrada.py ARW…` regenera `sr2_standard.json`. Requiere `opencv-python-headless` y `scipy` en `.venv`.
2. Para otro estilo creativo/PP: misma escena en ARW+JPEG; el SR2 de cada ARW trae su matriz y curva (leer `0x7800/0x7802` antes de ajustar nada).
3. Para Saturación/Phase/Depth: escena con colores conocidos (carta) por valor de ajuste.

## 6. Verificación hecha
- `python -m pytest tests/test_gui_isp.py tests/test_gui_harness.py -q`: 32 pasan, 5 lentas omitidas. Nuevas: SR2 = Backup 0, `curva_pp` = `pp_tone.c`, 10/11 por forma y bytes de `CamMsgConv`, DRO y Detail en CPU, ARW real (se omite sin el material). `ruff check` en verde.
- **Shader WebGL2 = CPU**: 7 casos × 8 colores + borde (Detail), diferencia máxima 1/255 (SwiftShader) y 0/255 (GPU Intel por ANGLE). Incluye Black Level/Black Gamma/Knee manual y auto.
- **Rendimiento** (`prueba_shader.py --fps 600 [--gpu]`, 640×480, incluye copia 2D→textura, Detail, curva PP y `getImageData`): SwiftShader ≈ 23 fps, GPU Intel (Iris Xe) ≈ 64 fps; ambos ≥ 15 fps.
- Límites: no probado con QEMU ni webcam física; la corrección de lente y `dro_auto_k` salen de una sola sesión de fotos (misma lente/estilo); la muestra no cubre otros estilos creativos.
