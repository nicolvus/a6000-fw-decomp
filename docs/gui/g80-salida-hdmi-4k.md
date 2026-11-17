# G80 — Salida HDMI 4K: fotos en 4K de fábrica; vídeo 4K por HDMI DESCARTADO

Fecha 16-11-2026 (G75 Tarea 28). Estático sobre `/usr` 3.21, más una captura del menú en el arnés (perfil `e2e46`, Sony 3.21 sin overlay, cerrado con `/salir`). Prueba: `tests/test_g80_hdmi_4k.py`.

## 1. Lo que ya existe (VERIFICADO)
- **«Repr. imagen fija 4K» (4K Still Image PB) está en el menú de reproducción de la A6000**, en la p. 2 (`docs/gui/img/g75/t28-repr-imagen-fija-4k.png`). Sale en gris porque el arnés no tiene un televisor 4K por HDMI («Connect to a TV that supports 4K», texto `0xf2ae`).
- La cadena completa está en el firmware:
  - el nodo `Output4kMode` en `CautionConfig.so`;
  - el modo QFHD (3840×2160) en `libInfraHdmi` (`handle_set_resolution … qfhd`, `PERMIT_HD_OUTPUT_IN_QFHD_MODE`);
  - `ObjDisplay`/`ObjRenderer` en `libObj` (`PRM_APP_HDMI_RESO_QFHD`, `SET_PATH_QFHD_THROUGH_RESIZE`);
  - la reproducción 4K y el redimensionado a 3840 en av-cam (VDF 4K, g77).

## 2. Lo que no se puede: vídeo 4K «limpio» por HDMI (lo del α7S)
Para sacar vídeo 4K por HDMI hace falta leer el sensor a 3840×2160 a 24/25/30 fps. El IMX210 no tiene ese modo de lectura y el vídeo llega a ~135 Mpx/s, frente a 249 Mpx/s ([g50](g50-4k-6k-photo.md), [g77](g77-4k-interno.md)). La salida HDMI en vivo de la A6000 se queda en 1080. **DESCARTADO**, por el mismo motivo que el 4K interno.

## 3. Arnés
El arnés no emula el HDMI (ni la conexión ni el EDID de un televisor 4K), así que la ruta de reproducción 4K no se puede ver funcionar en él. Como ya viene de fábrica, no hay nada que instalar ni que probar antes de la cámara.
