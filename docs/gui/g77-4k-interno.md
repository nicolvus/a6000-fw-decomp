# G77 — 4K interno: DESCARTADO (sin codificador 4K; 4K a 15 fps sin ruta ni forma de probarlo)

Fecha 16-11-2026 (G75 Tarea 25). Solo estático, sobre av-cam 3.21; sin cámara. Reproducible con `tests/test_g77_4k_interno.py`. Continúa la nota final de [g50](g50-4k-6k-photo.md).

## 1. 4K a 24/25/30 fps (lo que da el α7R II)
Descartado por g50: el IMX210 no tiene modo de lectura de ≥ 3840 columnas por debajo del completo, que da 6000×4000 a 15 fps; los modos de vídeo llegan a 1996×1124 a 60 Hz. Además, el caudal medido del vídeo es de 134,6 Mpx/s, frente a los 248,8 Mpx/s de 4K30.

## 2. La vía que quedaba: 4K a ≤ 15 fps desde la lectura completa
En aritmética cabe: 3840×2160×15 = 124 Mpx/s, por debajo del techo de 135 Mpx/s, y la lectura completa da 15 fps. Lo que hay en av-cam (VERIFICADO por bytes, `test_g77_4k_interno.py`):
- **Codificador MP4/XAVC S (`ExCodecEncMp4`): no hay configuración 3840×2160.** Las únicas que trae son 1920×1080 (25p/50p), 1440×1080 (25p/50i), 1280×720 (24/25/50/100p), 640×480 y 800×480 a 200p. Cada configuración tiene su `ActEnc`/`SetSeq` propio (tipo de entrada, ticks, GOP).
- **Sí hay piezas 4K, con referencias en el código:**
  - decodificación `ExCodecDecMp4::ActDecXAvcSMp4_30p_3840_2160`;
  - redimensionado de vídeo 4K (`vfx_4k_movie_prm_gen`, filtros `/usr/sabin/spica_musashi_mov_4k_{y,c}_tap_step{1,2}.bin`, que sí están en `/usr`);
  - una salida EE 4K («4K EE PIN»).

  Es el código común del BIONZ X que también usan los modelos 4K. INFERENCIA: el hardware maneja imágenes de 3840 de ancho, pero en la A6000 no hay camino de grabación que lo use.
- Para grabar 4K15 habría que crear desde cero:
  - la configuración del codificador (parámetros de secuencia H.264 de nivel 5.1, búferes y GOP);
  - el camino EE desde el modo de lectura completo (`0x0b`, de foto) hacia el vídeo, con el redimensionado 6000 → 3840;
  - el audio y el contenedor a 15 fps (no es una cadencia de XAVC S);
  - y la entrada de menú.

  Ninguna de esas piezas está en el firmware de la A6000.

## 3. Veredicto
**DESCARTADO.** 4K a 24/30 fps es imposible por el sensor y por el caudal (g50). 4K a 15 fps no tiene configuración de codificador, y lo que habría que crear no se puede probar fielmente antes de la cámara: el arnés no emula el hardware de codificación (MCAVC) y tampoco graba todavía (E2E-14). Eso va contra la regla del proyecto de verificar en el arnés lo que se instala, y un fallo del codificador en la cámara real no tiene diagnóstico.

**Alternativa que ya existe:** un timelapse 4K por fotos. El intervalómetro CFW (g61) con JPEG 16:9 (6000×3376) da fotogramas de más de 4K, que se montan después a 24/30p fuera de la cámara.
