# G50 — 4K/6K Photo (incl. 4K Photo Burst S/S) (DESCARTADO; derivado reducido pendiente)

Fecha 15-11-2026. Solo estático (firmware 3.21 de la A6000, 2.01 de la A6300, 3.20 de la A7S, `docs/capture/imx210-video-readout.md`, R87); sin cámara, sin parche, sin CFW.

## 1. Modos de lectura del sensor (IMX210, `av-cam.bin` 3.21)
Los 13 modos de `0x43fea070` (periodo = a·b ciclos de 54,054 MHz, fila 72 B de `0x43bc1ae8`; VERIFICADO como datos):

| Modo | Útil (col×lín) | fps | Tiempo de línea | Uso |
|---|---|---|---|---|
| 0x0b / 0x2f | 6000×4000 (24 MP) | 14,98 (66,8 ms, 4176 líneas) | 864 ciclos = 15,98 µs (tabla); 17,135 µs medido en barrido (R87) | captura |
| 0x0f | 1024×684 | 59,94 / 50 | 858 ciclos = 15,9 µs | ventana LV |
| 0x01 / 0x03 | 2000×570 / 2000×800 | 59,94 / 50 | 693 ciclos = 12,8 µs | Live View |
| 0x12 | 2000×570 | 119,9 / 100 | 693 ciclos | vídeo HFR |
| 0x0a | 2000×232 | ≈260 | 693 ciclos | AF/medición |
| 0x05/0x10/0x18/0x1a | 1996×1124 (≈2,2 MP, 6000/3 con binning) | 59,94 / 50 | 693 ciclos | 1080p60/50 |
| 0x07 / 0x19 | 1996×1124 | 48 | 875 / 693 ciclos | 24p |

Ningún modo da ≥ 3840 columnas por debajo de 6000 (único ancho > 2000 es el completo 6000×4000). No hay modo de recorte 3840×2160; el 0x0f prueba que el sensor admite ventanas, pero no hay fila de tabla para una de 3840×2160.

Cálculo del recorte 1:1 de 3840×2160 con el tiempo de línea de lectura completa:
- 2160 líneas × 15,98 µs = 34,5 ms → 29,0 fps;
- 2160 líneas × 17,135 µs = 37,0 ms → 27,0 fps (con 2176 líneas: 37,3 ms, 26,8 fps).
- Caudal: 3840×2160×30 = 249 Mpx/s, frente a 6000×4000/66,8 ms = 359 Mpx/s leído hoy. **El sensor, en aritmética, daría ~27–29 fps; no hay ruta ni tabla de registros para pedirlo** (los registros 0x000–0x155 no tienen datasheet; INFERENCIA).

## 2. Codificador
- Los modos «vídeo» del imager sacan como máximo 1996×1124 (≈ 2,2 MP) a 59,94/50 Hz = 134,6 Mpx/s, es decir 1080p60/50. 4K a 30 fps (248,8 Mpx/s) es 2,0× ese caudal; 4K es 4× los píxeles de 1080p.
- Tablas de cadenas de la A6000 (`string_english.uxc`): `50p 28M(PS)`, `24p 50M`, … pero el mismo fichero lista `4K 24P/4K 30P/4K_30P_OUTPUT`, `100p/120p 50M`: es una tabla de texto compartida con otros modelos, **no prueba capacidad** (ya visto en g13/g14).
- `libObj` de la A6000 contiene código compartido `InfMovieEncoder` con `mp_RsrcAcsr4KMovRecAaLifo`, `needAcquire4KRsrc` y `60pMovRec`: son accesores de recurso con comprobación NULL; el IMX210 solo ofrece 1996×1124 (§1), así que el camino 4K no se alimenta.
- Comparación por imager en `av-cam.bin`: A6000 = **IMX210** (13 modos; este informe), A6300 = **IMX284** (`ImagerDrvParam_IMX284E`, 414 cadenas 4K/3840/2160 frente a 194), A7S = **IMX235** (12 MP; 4K solo por HDMI, 182). La A6300 tiene tablas propias y recursos 4K (`4KProxyRec`, `100M`/`60M` XAVC S) ausentes en la A6000. Tope de bits/nivel H.264 de la A6000: NO medido en este informe (no se localizó una tabla de perfil/nivel; las cadenas de UI dan 28 Mbps PS 50p/60p como máximo AVCHD y 50 Mbps XAVC S en tabla compartida).
- Como en la A7S (mismo BIONZ X y misma limitación; g40: solo difieren tablas de sensor/vídeo), el tope es 1080p60.

## 3. Ráfaga JPEG de 8 MP a ~27–30 fps sin vídeo
- Ráfaga de serie: 11 fps × 24 MP = 264 Mpx/s; 8 MP × 30 = 249 Mpx/s (4K UHD 8,29 MP × 30 = 248,8). El caudal de píxeles del pipeline de foto *en ráfaga* ya cubre 8 MP × 30, pero:
  - está fijado por obturador mecánico/lectura completa: un cuadro cada 66,8 ms (14,98 fps máx., modo 0x0b); no existe un modo de lectura de 8 MP (§1), de modo que a 30 fps habría que sustituir la lectura, no solo recortar la salida;
  - el tamaño M (12 MP) / S (6 MP) lo hace el ISP *después* de leer 24 MP; no baja el tiempo de lectura (66,8 ms);
  - sin modo, no hay cadena de captura 8 MP/30 fps (la ruta C JPEG sin obturador, `electronic-still-low-resolution.md`, está NO ACCESIBLE con la evidencia: modos 0x08/0x11 ajenos al IMX210).
- Escritura: 8 MP JPEG ≈ 3 MB × 30 = 90 MB/s, por encima de una SD UHS-I realista (no medida aquí; INFERENCIA).

## 4. Extracción en reproducción (Photo Capture)
- A6300: `ViewPhotoCapture` (`viewUnified3.so`), `LG_viewphotocapture::Layout*`, `viewPhotoCapture.uxc` en `global.xdb`, ajuste `4kPhotoCapture` (`cmnViewSetting*`, `Fn/Custom/AEL/Playback` en `CautionConfig.so`).
- A6000: 0 ficheros con `ViewPhotoCapture/viewPhotoCapture`; sin `viewUnified*`, `global.xdb` ni `CautionConfig` con `4kPhotoCapture`. La única coincidencia de `Photo Capture` es texto francés ajeno. La A7S tampoco la tiene (0).
- La A6000 solo conserva `SequenceMovieCaptureStart` (código compartido; también en la A6300). La vista de extracción no existe: habría que crear la vista y el flujo, y sin vídeo >1080p solo extraería 2 MP.

## 5. Veredicto
**4K/6K Photo: DESCARTADO.** Sin modo de lectura registrado de ≥3840 columnas (solo 6000 completo a 15 fps y 1996×1124 a 60 Hz), sin codificador 4K en un BIONZ X con IMX210 (tope 1080p60 / 134,6 Mpx/s frente a 248,8), sin vista de extracción en el firmware. La ráfaga 8 MP/30 fps queda limitada a 15 fps por el modo de lectura completa.
**Derivado reducido (pendiente acotado, sin implementar):** «FHD Photo»: extraer fotogramas de 1996×1124 (≈ 2 MP) a 60 fps desde el modo de vídeo 0x10/0x1a hacia JPEG (ruta C). Ver pendiente G50-FHDPHOTO.

## 6. Relación con «4K interno» (Vídeo)
Comparten el límite: ni el imager IMX210 ni el codificador (1080p60) admiten 4K; «4K interno» queda sujeto al mismo veredicto (modo ≥3840 columnas inexistente + codificador). No se cierra aquí; se anota en PENDIENTES.
