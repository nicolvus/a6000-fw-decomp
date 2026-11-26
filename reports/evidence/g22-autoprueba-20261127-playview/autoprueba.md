# Autoprueba del arnés — 2026-11-26 09:24:02

Resultado: **PASS** (16/16 pasos)

| paso | resultado | evidencia |
|---|---|---|
| arranque | ✓ | primera pantalla en 138.9 s · arranque en frío, 138 s · 1 fotogramas · 0.5 fps · último:  |
| pantalla | ✓ | contenido dibujado 0.044, píxeles opacos 0.075 (OSD de la cámara ≈ 0,09; 0,003 = no compuso) |
| teclas-MENU | ✓ | opacos: disparo 0.08 → menú 1.00 → disparo 0.08 (menú ≥ 0,9 y vuelta ≤ 0,5: una pulsación por cambio) |
| dial-de-modos | ✓ | pantalla con contenido tras girar a M (0.045) |
| foto-disparador | ✓ | 1 foto(s) nueva(s), modelo EXIF ILCE-6000 |
| movie-grabando | ✓ | el anfitrión está grabando |
| movie-clip | ✓ | 1 clip(s) nuevo(s) MP4 |
| sd-lista | ✓ | 2 ficheros: ['PRIVATE/M4ROOT/CLIP/C0001.MP4', 'DCIM/100MSDCF/DSC00001.JPG'] |
| sd-fichero | ✓ | HTTP 200, 22041 B |
| sd-importar | ✓ | HTTP 200 → DCIM/100MSDCF/DSC00002.JPG |
| sd-borrar | ✓ | HTTP 200 → DCIM/100MSDCF/DSC00002.JPG |
| sd-formatear | ✓ | HTTP 200 → {'ok': True, 'borrados': 2} |
| camara-bateria | ✓ | modelo 5 % → enviado ['B 5'] |
| camara-usb | ✓ | HTTP 200 → ['U 1'] |
| reproduccion-abre | ✓ | 336 filas distintas de 480 y opacos 0.0000 tras pulsar Reproducción (≥ 100 filas = la vista cambió; 0 = la tecla no hizo nada) |
| cierre | ✓ | código 0, estado guardado 119 MiB |
