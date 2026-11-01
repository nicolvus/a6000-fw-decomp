# 12. Herramientas

Todas las rutas son relativas a la raíz del repositorio. Activa antes el entorno: `source .venv/bin/activate`.

## En el PC (sin cámara)

| Herramienta | Para qué | Uso |
|---|---|---|
| `scripts/agent/bootstrap.sh` | Descarga el firmware oficial 3.21, crea los entornos y lo desempaqueta | `scripts/agent/bootstrap.sh [--dry-run]` ([paso 2](https://github.com/nicolvus/a6000-fw-decomp/wiki/2-Entorno-y-firmware-oficial)) |
| `references/fwtool/fwtool.py` | Desempaqueta/inspecciona `.dat` y FDAT | `python references/fwtool/fwtool.py unpack -f X.dat -o salida/` |
| `scripts/replicar/generar_nucleos.py` | Parchea el `darwin_core.bin` oficial (tipo 0 y B1a) y comprueba sus SHA-256 | sin argumentos |
| `scripts/e25_05/build_packages.py` | Construye y verifica los paquetes 3.23 y 3.24 (69 comprobaciones, ≈ 85 s) | sin argumentos |
| `scripts/e25_27/build.py` / `verify_325c.py` | Construye el 3.25c y ejecuta sus 30 comprobaciones y la emulación del cargador | `build.py --out DIR --package`, luego `verify_325c.py` |
| `scripts/recovery/r1_manifest.py` | Inventario y verificación de hashes del respaldo y de los paquetes | `verify` |
| `scripts/audit/repo_audit.py` | Audita enlaces, rutas citadas, cifras y SHA-256 | sin argumentos |
| REA / Ghidra | Ingeniería inversa del firmware ([mapa](https://github.com/nicolvus/a6000-fw-decomp/wiki/10-Mapa-del-repositorio)) | `docs/agent/bootstrap-desde-cero.md` §4 |

## Con la cámara por USB

| Herramienta | Para qué | Uso |
|---|---|---|
| `pmca-console` ([Sony-PMCA-RE](https://github.com/ma1co/Sony-PMCA-RE)) | Info, flasheo de firmware e instalación de apps | `pmca-console info`, `pmca-console firmware -f X.dat` |
| `scripts/senser_backup_dump.py` | Backup de NVRAM, **solo lectura** ([paso 3](https://github.com/nicolvus/a6000-fw-decomp/wiki/3-Backup-de-NVRAM)) | `python scripts/senser_backup_dump.py DIR` |
| `scripts/senser_backup_restore.py` | Restaura la NVRAM desde tu copia | `python scripts/senser_backup_restore.py FILE SHA256` |
| `scripts/fdat_guard_probe.py` | Sondea el guard del actualizador **sin flashear** | `python scripts/fdat_guard_probe.py [VERSION ...]` |

## Con la cámara por Wi-Fi (telnet / ADB / HTTP)

Requisitos: [capa 2](https://github.com/nicolvus/a6000-fw-decomp/wiki/6-Capa-2-exposicion-uniforme) (Tweak con telnet y ADB activados, RemoteShutter abierta). Indica la IP de tu cámara
con la variable `A6000_HOST` o `--host` (por defecto `192.168.1.29`).

| Herramienta | Para qué | Uso |
|---|---|---|
| `scripts/camera_telnet.py` | Ejecuta comandos en el `telnetd` de la cámara (root, sin login) | `python scripts/camera_telnet.py --host IP 'uname -a'` |
| `scripts/camera_install_apk.py` | Instala un APK por ADB (puerto 5555) | `python scripts/camera_install_apk.py APK [IP]` |
| `tools/remote-shutter/` | App RemoteShutter: servidor HTTP en el puerto 8080 (`/shoot`, `/ss`, `/status`, `/info`, `/log`, `/jpg`) | `tools/remote-shutter/build.sh` (JDK 17 y build-tools en `~/.local/android-build`) |
| `scripts/camera_silent.py` | Parche de RAM de la capa 2 con guardián de 25 s: comprueba, parchea, revierte y verifica | se importa desde los scripts de prueba |
| `scripts/camera_silent_test.py` | Patrón de prueba de T050: guardián, referencias, disparos de 1/4000 a 1/30 y ráfaga de 4 | `python scripts/camera_silent_test.py SALIDA/` (escena fija, sin tocar la cámara) |
| `scripts/camera_suite.py` | Suite de verificación de imágenes: latencia, EXIF, luminancia, bandas y rearme | `python scripts/camera_suite.py SALIDA/ [--host IP] [--quick]` |

## Reglas al usarlas

- Los scripts de lectura no escriben nada; los de parche de RAM comprueban primero los bytes originales y no actúan si no coinciden.
- Nunca hagas pruebas en cámara sin backup de NVRAM.
- Registra cada prueba en `docs/capture/registro-pruebas-camara.md`.
