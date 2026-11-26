# G112 — Open gate en el vídeo de la A6000: viabilidad y vías (25-11-2026)

Petición del usuario: buscar la manera de implementar *open gate* (grabar vídeo con toda la altura del sensor
APS-C 3:2, 6000×4000, en vez del recorte 16:9 de 6000×3376). Investigación en siete frentes paralelos
(pipeline de vídeo, sensor/BIONZ, ruta de CFW, estado del arte externo, conocimiento previo del repo, HDMI/control
y plan experimental). **Nada instalado, nada escrito en la cámara.**

## 0. Veredicto

| Vía | Resultado | Motivo (evidencia) |
|---|---|---|
| **6000×4000 grabando** | **IMPOSIBLE** | Sensor a resolución plena barre en **66,8 ms = 14,98 Hz** (`docs/capture/imx210-video-readout.md`) y el codificador no tiene raster > 1920×1080 (§2.3). Es el mismo muro que cerró [G77](g77-4k-interno.md). |
| **3:2 nativo 1440×960** | **ÚNICA vía de firmware viable** | Único raster 3:2 que pasa los dos validadores del codificador (§2.3): 1440 está en la lista blanca y la rama «no full HD» exige entrada = salida. |
| **3:2 nativo 1920×1280** | BLOQUEADO | `FUN_4391c540`: si el ancho es 1920 el alto **tiene** que ser 1080 (o 540 entrelazado). |
| **3:2 por HDMI / grabador externo** | NO EXISTE | HDMI tope 1080p/1080i (`docs/gui/g80-salida-hdmi-4k.md`); QFHD solo reproducción de fotos 4K. Peor: **al grabar el sensor cambia a 1996×1124**. |
| **Control por app/SDK** | NO EXISTE | `libObj` solo conoce `MOVIE_ASP_16_9/4_3/15_9`; `movieformat` de Camera Remote API es cadena opaca; PMCA no toca modos del sensor. |
| **Timelapse 3:2 desde foto** | **HOY, riesgo cero** | La foto ya graba 3:2 6000×4000 sin recorte; montaje fuera. Techo real 14,98 Hz (66,8 ms) de sensor. |

## 1. Qué significa aquí

Open gate = usar toda la altura del sensor (23,5×15,6 mm, **IMX210**) para tener campo de visión completo y
reencuadrar en post. En la A6000 el recorte 16:9 es **6000×3376**, así que open gate = **6000×4000 (+18,5 % de
alto)**; en un pipeline 1080p el valor está en el **campo de visión**, no en la resolución. Precedentes: ALEXA 35
4.6K 3:2 4608×3164, GH5 4992×3744, VENICE 2 8.6K 3:2. En Sony E-mount el único open gate público es el parche **en
RAM** de A7 IV / A7S III / FX3 (`Arcane Lantern`, nov-2026: 4 sitios en `libmpr.so` + 101 en `av-cam.bin`, tabla de
clip, 689 descriptores, cabeceras MP4 y **modo de sensor nuevo**; una cámara se cuelga al pasar a 60p). **No hay
nada publicado para la A6000** (0 repos).

## 2. La cadena, capa por capa

### 2.1 Sensor (IMX210) — el recorte está en el modo de lectura, no en el escalado
`docs/capture/imx210-video-readout.md` (13 modos, VERIFICADO) + `docs/gui/g70-hd-120fps.md`:

| Uso | Modo | Lectura | Notas |
|---|---|---|---|
| Foto | `0x0b`/`0x2f` | 6000×4000 | 16,0 µs/línea → 14,98 Hz (66,8 ms) |
| **Vídeo** | `0x05/0x10/0x18/0x1a/0x07/0x19` | **1996×1124** | binning 3×3, 12,833 µs/línea, 48–59,94 Hz |
| Live View foto | `0x01` | 2000×570 | 4000/7 |
| Live View foto | **`0x03`** | **2000×800** | 4000/5 **= altura completa 3:2**, anamórfico ÷3/÷5, 50/60 Hz |

El sensor **ya sabe leer las 4000 líneas** (modo `0x03`, en uso hoy en Live View/EE). No existe ningún modo
~1996×1333 para 24/25/30p: la tabla de modos (`0x43fea070`) y la fila Camcore `0x43bc16dc` (72 B por modo, ancho
`+0x1c`, alto `+0x3c`) no lo tienen. Geometría: `0x43bc16dc[7]`/`[15]`, HMAX/VMAX `0x43bc1ae8`/`0x43bc1b84`.

**El alto no es un registro, es un código** (nuevo, `work/opengate/04-sensor-darwin.md` §3): matriz `0x43fe9b74`
(59 filas × 20 B) — `0c`→4000, `2c`→1124, `5c`→800, `6c`→570, `7c`→232. Prueba de que codifica y no es libre:
`0x01` (570) y `0x03` (800) difieren en **dos celdas** (`0x000` y `0x015`) y no existe el valor que daría 1333.
Transporte al imager: P2S(DFE0) `0xfc088300`, trama `81|len|81|AH AL|datos`, 119 registros sombra `0x43fe995c`.

**Aritmética que decide** (mismo informe, §1): con binning 3 (4000/3 = 1333) el 3:2 cabe a **24/25/30 fps**
(17,1 ms de barrido de 41,7) y a 48 Hz; **a 59,94 Hz no cabe** (1300 líneas máx. < 1333). Es decir: **el recorte
16:9 lo impone el modo de 60p, no 24/25/30**. El reloj de referencia es **54,000 MHz** (PAL 693×1500, NTSC
693×1300): el «techo de 134,6 Mpx/s» de G50/G77 **no es hardware**, porque en foto el DFE mueve 375 Mpx/s
(6000 columnas / 16,0 µs).

### 2.2 Modelo, formato y despacho (lo que hay que tocar para que la cámara *quiera* grabar 3:2)
- Selector de modo de vídeo `FUN_4380e43c` (caso 7) con la clase de formato en `cfg[+0x1d4]`; gate de capacidad
  `FUN_43ad909c` (`vtable+0x94`); ratio EE/Crop `0x43cb1458`→`FUN_4354a678` (xref `0x4354aae0`) y
  `0x43ad908e`→`0x43ad9644`.
- Orden de formato: `MSGID_SET_MOVIE_FORMAT_CMD 0x750e` → orden LIRO `0x4000` de **23 B**: clase `0xd`, tamaño
  `0xf`, **aspecto `0x11`**, ancho `0x14` (mapa en [G78](g78-dual-video-proxy.md) §2 y [G76](g76-variable-frame-rate-sq.md) §5;
  traza real en [G75](g75-arnes-e2e-objetivos.md):511). Valores de aspecto: **16:9, 4:3 y 15:9; 3:2 no existe.**
- `libObj` sí tiene el **vocabulario** 3:2/4K (`MOVIE_ASPECT_3_2` en `0xda6df6`, `MOVREC … ASPECT(2:3_2)` en
  `0xdc675b`, datos `3840/2880/3240×2160` en `0xc3450a`), y `GetStdMovieFormatInfo` /
  `PARAMID_MOVIE_SIZE_ACT/_RAW` existen (anclas `0xe25f38`, `0xe26168`) pero **no están documentados**: es el punto
  donde muere o vive un formato 3:2 de verdad. `libmpr` **no puede etiquetar** 3:2 (`emAspectRatio` y
  `pixelAspectRatio` sin 3:2); `PARAMID_SQUEEZE_ASPECT_*` = NOT FOUND.

### 2.3 Codificador — aquí muere el 3:2 «bonito»
Descompilado en esta investigación (`work/opengate/01-pipeline-video.md` §3):

- `FUN_436120cc` → wrapper `0x43a7c8fa` → `FUN_43613274` (índice→constructor, `tbh`) → **`FUN_436124b8` elige
  configuración por coincidencia EXACTA de (ancho, alto)** contra **5 rasters**: 640×480, 800×480, 1280×720,
  1440×1080/540, 1920×1080. Otro tamaño → índice 0 + log.
- **`FUN_4391c540`** (emite los strings `0x43cd95a7`/`0x43cd971a`): `input_picture_width ∈ {640, 800, 1280, 1440,
  1920}` y **si ancho = 1920, alto = 1080** (o 540 entrelazado). Es decir, 1920×1280 muere aquí, no en una
  comparación incidental: son restricciones del motor Mojito/ZIMA.
- Único hueco explotable: la config **1440×1080** (índice 1, ctor `0x43a7bf56`) admite la rama «no full HD»
  (entrada = salida) → **1440×960** con un `mov.w`. En el paquete `pp` instalado no hay `libmpr.so`, así que si hay
  que tocar `libmpr` sería un estreno en este repo (mecánicamente posible: 7,0 MiB libres en el ext2).

### 2.4 Entrega (CFW) — resuelta, el problema no es el empaquetado
`build_cfw_film.py:169` → `build_nflasha15.py:71` → `build_base_pp.py:42` (exige tamaño idéntico de `AV-CAM.BIN`)
→ `build_package_nflasha15.py:33` (CRC de `part_image.sum`, `--sin-wbi`) → `audit_package_nflasha15.py:157`
(29 comprobaciones). Instalación `pmca-console firmware … --flash --confirm`; rescate por SWD (R48). Límites:
2 373 bloques, ≤ 129 sectores, bloque 0 intacto, cualquier cambio en `/usr` obliga a `--sin-wbi` (WBI de Sony
invalidado). `pp`/`film`/`film_ui`/`iso`/`exfine` son **flags** de constructor, no particiones.

## 3. Discrepancias entre los siete informes (resueltas por evidencia)

1. **1440×960 vs 1920×1280.** Dos informes proponen 1920×1280 (24/25/30p, 73,7 Mpx/s, cabe en caudal). Gana
   **1440×960**: el validador `FUN_4391c540` está descompilado y prohíbe 1920 con alto ≠ 1080. 1920×1280 queda
   como objetivo *posterior* si se parchea ese validador (pelear con Mojito), no como primer paso.
2. **Techo de caudal.** El «135 Mpx/s» de G50/G77 se usó en dos informes como límite duro; el análisis del DFE
   (375 Mpx/s en foto) lo desmiente como límite de hardware. No cambia el veredicto (el muro es el codificador),
   pero sí la aritmética: 2000×1333@30 = 80 Mpx/s es asumible.
3. **`0x03` = 2000×800 es anamórfico**, no «3:2 completo a 60 Hz»: se reescala en el ISP. Su uso para *grabar* es
   HIPÓTESIS; su uso en Live View está verificado. Sirve para medir por HDMI, no como prueba de open gate.
4. **El recorte vertical en vídeo es INFERENCIA numérica, no hecho medido** (1996×1124 ≈ 6000/3 × 3376/3). Falta
   la medida física del §5-M1 antes de afirmarlo en ningún sitio.

## 4. Vías ordenadas por coste/riesgo

| # | Vía | Qué cuesta | Qué da |
|---|---|---|---|
| V0 | **Timelapse/ráfaga 3:2 6000×4000** con montaje externo | 0 firmware; intervalómetro | Campo completo del sensor, hasta 14,98 Hz (66,8 ms) reales → 24p con interpolación. Es lo que ya propone [G77](g77-4k-interno.md):28 para 4K. |
| V1 | **Encoger la salida a 1440×960 sin tocar el sensor** (Fase 1) | Parche de codificador (E8+E9), reversible | Prueba de que la cadena encoder+fichero acepta un raster no estándar. La imagen sería un 3:2 **escalado desde 16:9 = deformada**: solo vale como test. |
| V2 | **Readout 3:2 real + 1440×960** (la vía de verdad) | Fila Camcore + código de alto del sensor + tabla de formatos + validador de aspecto | 3:2 nativo a 24/25/30p, escalado uniforme 0,72 desde 1996×1333. |
| V3 | **Anamórfico**: grabar 1920×1080 con el 3:2 comprimido en vertical y descomprimir en post | Solo readout 3:2 (encoder intacto) | 1620×1080 útiles (o 1920×1280 estirado). Clip «achatado» en cámara; sin squeeze en firmware. |
| V4 | 1920×1280 nativo | V2 + parche del validador Mojito | Mejor raster, riesgo de encoder sin estado de retorno. |
| V5 | 6000×4000 grabando | Modo de sensor nuevo + codificador ≥6 Mpx | Descartado (§0). |
| V6 | 3:2 por HDMI con grabador | Nada de firmware | Nada: 1080p pillarboxeado como máximo, y solo desde Live View de foto. |

## 5. Plan por fases (con criterio de cierre)

- **F0 — estática, sin cámara (barata, 1–2 sesiones REA sobre `av-cam.bin`).** Cerrar los dos puntos ciegos:
  (a) **dónde se escribe el número de líneas del modo** (`SetRead` `FUN_436d7e08`, `0x436d8c48`, `0x436d8e20`: ¿sale
  de los 59 registros o de un parámetro derivado?); (b) quién rellena el **bloque de formato de 0x84 B**
  (`obj+0x404`): ¿`libObj` o una tabla de `av-cam`? Sin (b) no se sabe si el cambio es tabla o cueva.
  Cierre: ruta escrita, o imposibilidad demostrada. Añadir de paso el **enum 3:2 de `0x4000`** y el vínculo
  modo→descriptor (`0x43ad908e`→`0x43ad9644`, nunca resuelto).
- **M0 — sin cámara.** Validar el estimador geométrico del plan experimental con recortes/letterbox/anamórfico
  sintéticos + `tests/test_opengate_geometria.py`. Métrica R_v = 1080·s_v/(4000·s_p): 0,843 (recorte) vs 1,000
  (altura completa), 15,7 % de separación frente a ±0,2 % de error.
- **M1 — una sesión física (~1 h, solo lectura).** F1/F2 foto 3:2 y 16:9 + V1/V2 vídeo 60p/24p + estrobo 1 kHz y
  blanco móvil (n_líneas = T_read/t_line distingue 1124 de 1333). Con capturadora, M4: HDMI en modo foto
  (open gate externo ~1620×1080, sin firmware).
- **F1 — encoder-only.** Repurposar 1440×1080 → 1440×960 y grabar con el sensor en 16:9. Cierre: clip legible de
  1440×960 con la cadena intacta (o encoder sin arrancar, que también es información).
- **F2 — readout 3:2** (solo si F1 graba): modo ~1996×1333 + salida 1440×960 + marcado de aspecto best-effort
  (`OTHER` en `libmpr`). Requiere F0(a).
- **F3 — anamórfico** (plan B si Mojito resulta intocable): V3.

## 6. Riesgos que hay que aceptar por escrito

1. **El arnés no graba** (E2E-15): la primera prueba real de un raster nuevo es en la cámara, y un fallo del
   codificador no tiene diagnóstico ni watchdog documentado del lado `ExCodecEncMp4`.
2. **Un código de alto inventado** (`0x2c` → 1333) puede dar un cuadro con 209 líneas de basura o colgar el imager.
3. **Cada iteración exige flasheo**; si no arranca, hay que **abrir la cámara** para forzar el actualizador por SWD
   (historial real: `todo`/`iso` en bucle, `exfine` «sin espacio» — una build auditada al 100 % puede no arrancar).
4. **Cambiar el alto del modo afecta al Live View y al ratio EE/Crop** (AF, encuadre, marcas de recorte).
5. **Audio y contenedor**: a 15 fps no hay formato estándar; V0/V3 exigen montaje externo.
6. **Citar «el vídeo recorta en vertical» como hecho** cuando sigue siendo inferencia hasta M1.

## 7. Anexos (locales, no versionados)

`work/opengate/01-pipeline-video.md` (pipeline y 13 enganches), `02-ruta-cfw.md` (flujo de build/instalación y
comandos), `03-exterior.md` (estado del arte, A7 IV, alternativas), `04-sensor-darwin.md` (IMX210, registros,
aritmética), `05-conocimiento-repo.md` (vaciado y contradiction-audit), `06-hdmi-control.md` (HDMI, API, PMCA),
`07-experimento-fisico.md` (protocolo M0/M1/M4). 2 648 líneas con citas `ruta:línea` y URL.
