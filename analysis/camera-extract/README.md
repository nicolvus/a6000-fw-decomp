# Ejecutables y APK extraídos de la cámara (2026-10-21)

Generado con `scripts/camera_extract_all.py` + `/proc/*/maps` de todos los procesos en marcha. Los binarios (148 MB, propiedad de Sony) NO se versionan; solo este README y `manifest.json` (ruta en la cámara, copia local, tipo, tamaño, SHA-256 y si estaba cargado en ejecución).

- **773 archivos**: 18 APK (`/android/system/app` + `framework-res.apk`), 53 odex/dex, 38 jar/zip, 659 ELF (`nflasha15`=/usr 320, `nflasha16`=/android/system 199, `nflasha7`=rootfs 125, `nflasha3`=av-cam.bin/kernel 15) y 5 de la cámara en vivo por ADB (OpenMemories Tweak: APK, 3 `.so` y su dex).
- **268 están mapeados en memoria** por algún proceso (`cargado_en_ejecucion`); 20 rutas cargadas no tienen copia ejecutable: fuentes, `icudt44l.dat`, `zoneinfo.dat`, recursos de UI `/usr/share/app/*.uxc|.xdb|.uxb`, `/android/init`.
- El sistema instalado se copió del paquete oficial 3.21: los volcados de la NAND (`nand-20261020`) coinciden byte a byte con sus imágenes (`nflasha3/5/7/15/16`).
- Para regenerar: `python3 scripts/camera_telnet.py` (mapas) + `~/.local/share/pmca-venv/bin/python scripts/camera_extract_all.py analysis/camera-extract LOADED.txt`.
