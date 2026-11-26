# Autoprueba del arnés — 2026-11-26 09:57:02

Resultado: **PASS** (15/15 pasos)

| paso | resultado | evidencia |
|---|---|---|
| arranque | ✓ | primera pantalla en 150.1 s · arranque en frío, 149 s · 1 fotogramas · 0.5 fps · último:  |
| pantalla | ✓ | contenido dibujado 0.051, píxeles opacos 0.087 (OSD de la cámara ≈ 0,09; 0,003 = no compuso) |
| teclas-MENU | ✓ | opacos: disparo 0.09 → menú 1.00 → disparo 0.08 (menú ≥ 0,9 y vuelta ≤ 0,5: una pulsación por cambio) |
| dial-de-modos | ✓ | pantalla con contenido tras girar a M (0.045) |
| foto-disparador | ✓ | 1 foto(s) nueva(s), modelo EXIF ILCE-6000 |
| movie-grabando | ✓ | el anfitrión está grabando |
| movie-clip | ✓ | 1 clip(s) nuevo(s) MP4 |
| sd-lista | ✓ | 2 ficheros: ['PRIVATE/M4ROOT/CLIP/C0001.MP4', 'DCIM/100MSDCF/DSC00001.JPG'] |
| sd-fichero | ✓ | HTTP 200, 14500 B |
| sd-importar | ✓ | HTTP 200 → DCIM/100MSDCF/DSC00002.JPG |
| sd-borrar | ✓ | HTTP 200 → DCIM/100MSDCF/DSC00002.JPG |
| sd-formatear | ✓ | HTTP 200 → {'ok': True, 'borrados': 2} |
| camara-bateria | ✓ | modelo 5 % → enviado ['B 5'] |
| camara-usb | ✓ | HTTP 200 → ['U 1'] |
| cierre | ✓ | código 245 (SIGSEGV al cerrar tras guardar: G22-ARR3), estado guardado 118 MiB |
