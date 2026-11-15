# G51 — Pre Capture / Pro Capture a resolución completa (VIABLE POR FASES, sin implementar)

Fecha 15-11-2026. Solo estático (REA sobre `av-cam.bin` 3.21, base `0x43541000`) más lectura del repo; sin cámara, sin parche, sin CFW. La parte 4K/6K es la ya descartada en [g50](g50-4k-6k-photo.md).

## 1. ¿Ráfaga con Silent?
- No hay medición. T050 (`camera_silent_test.py`, [wiki 6](../../wiki/6-Capa-2-exposicion-uniforme.md)) solo probó 12 disparos y «ráfaga de 4» con el parche aplicado por telnet **a cada disparo/ráfaga**; las «ráfagas largas» constan como no probadas ([wiki 6](../../wiki/6-Capa-2-exposicion-uniforme.md), condiciones de seguridad).
- Estáticamente no hay fila propia de Silent: el selector `0x437eabfc` usa la misma tabla de 15 filas para monodisparo y ráfaga (8/12) ([s19](../capture/s19-stage-rawplayinit-reuse.md) §209). Por tanto la ráfaga Silent es plausible, no demostrada.
- Techo físico: lectura completa 66,8 ms ⇒ ≈ 15 fps ([imx210-video-readout](../capture/imx210-video-readout.md), g49/g50); de serie 11 fps mecánico.

## 2. Estructura de ráfaga localizada (REA, cruzado con docs)
- La captura se arma en `0x437df338`: reserva RAW `0x437e1e48` (único llamador), recursos de intervalo `0x437e0fc0`, **retención S2** `0x43afbe46` (llamada desde `0x437df338` y `0x437df0a4`): es un contador de referencias (`+2` de un objeto: 0→1 devuelve 1, si no incrementa), no un lector del pulsador. Contexto de ráfaga en `Image/Param +0x4ad4`, índice `+0x54a8`, flags `+0x54a5` ([shutter-trigger-state-machine](../capture/shutter-trigger-state-machine.md) §120–135).
- Lado Darwin: estado 5 «ráfaga» y 9/11 (mono/ráfaga) ([STATE](../STATE.md), E24-05a/f).
- Existe un anillo real, **pero no es el de captura**: `CAMERA_MAIN_SYNC: RingBuf Warning: overwrite %d frames` (cadena `0x43cb1b68`, único xref `0x4354b750`+`0x4354bff2`/`0x4354c618`, estado de sincronización que lee el contador `+0x84` con `0x4379a9fc`), con `dmm AllocNew/Free JPGRINGBUF_unit_type` (`0x43cb28ad`, xref `0x4354d9c8`) y `Resource/JpegRingBuf.cpp` (`0x43ca4aca`, `0x4379a7ec`: tipo 0/1/2 ⇒ 3/6/12 unidades). Es el anillo de JPEG de vídeo/Live View (tamaño fijo 3/6/12 cuadros, sobrescribe). Sirve de precedente de «anillo con sobrescritura», no de búfer de 24 MP.
- No localizado: el predicado «sigue mientras S2» ni la cola de grabación de la ráfaga (queda como F1). Un xref vacío de REA no prueba ausencia (`BURST_CNT` `0x43cb4bfe` sin xrefs: dato por tabla).

## 3. Diseño mínimo y coste
Dato: 24 MP RAW ≈ 24 MB comprimido; el búfer de serie (≈ 21 RAW ≈ 500 MB) es la cota de memoria disponible para foto, compartida con la salida a SD.
| Punto | Sitio del parche | ¿Cabe en el `.dat`? | Coste |
|---|---|---|---|
| (a) arrancar con S1 | origen del mensaje de captura (`0x0c`, E24-05a) / condición que crea la petición ([`0x437dfe4c`], retención S2 `0x43afbe46`); falta ubicar el predicado S1→S2 | Sí, está en `av-cam.bin` (bytes), pero hay que comprobar el AF/AE de S1 y el obturador mecánico/Silent | 0 |
| (b) anillo de N sin grabar | la cola de codificación/grabación de la ráfaga (no localizada) debería **liberar el más viejo en vez de encolar**; hoy cada cuadro se encola y se vacía a SD | Lógica nueva (decenas de instrucciones Thumb, hace falta cueva); riesgo alto: liberación exacta de lo adquirido ([state-machine](../capture/shutter-trigger-state-machine.md) §237) | N × 24 MB: N=5 ⇒ 120 MB, N=10 ⇒ 240 MB, N=15 ⇒ 360 MB; con previos + posteriores ≤ ≈ 21 cuadros (≈ 500 MB) |
| (c) encolar anillo + siguientes con S2 | recorrer el anillo hacia las etapas de codificación (reutiliza Stage_RawPlayInit, precedente de captura sin sensor, s19) | Plausible en el `.dat`; metadatos EXIF/DCF de cuadros pasados | sin memoria extra; escritura SD ≈ 24 MB × N en ráfaga |
Contras que no cambian: a 15 fps con anillo 10 se cubren ≈ 0,67 s de pre-captura; sensor y DSP en lectura continua con S1 elevan temperatura y consumo.

## 4. Parche
No se implementa nada: el único punto pequeño (a) depende de un predicado S1/S2 que no está localizado, y sin él un test de bytes originales sería inventado. Cierre = pendientes acotados.

## 5. Veredicto: VIABLE POR FASES (confianza media-baja; no probado)
Sin límite de hardware demostrado (a diferencia de g50), pero el riesgo está en (b). Pendientes: G51-PROCAP-F1…F4 en [PENDIENTES](../PENDIENTES.md).
Límites: sin medir ráfaga Silent ni liberación de búferes; REA solo estático; el anillo `JPGRINGBUF` identificado es de vídeo.
