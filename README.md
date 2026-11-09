# Sony A6000 — Silent Shutter

[![English version](https://img.shields.io/badge/🇬🇧_English_version-blue?style=for-the-badge)](README.en.md)

[![módulos](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-modulos.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![sesiones](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-sesiones.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![pruebas](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-pruebas.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![CI](https://github.com/nicolvus/a6000-fw-decomp/actions/workflows/tests.yml/badge.svg)](https://github.com/nicolvus/a6000-fw-decomp/actions/workflows/tests.yml)

Ingeniería inversa del firmware 3.21 de la Sony A6000 (ILCE-6000: BIONZ + microcontrolador Darwin) para disparar con
obturador electrónico. **Hito:** con el firmware modificado **3.23** (parche de 2 bytes sobre Darwin) la cámara real disparó en
silencio y sin error. **Después**, el firmware integrado **3.25** dejó la cámara sin arrancar por un error de formato en la partición
`nflasha3`, ya identificado y corregido en el **3.25c**. Esa cámara **se recuperó el 03-11-2026 por SWD** con el firmware oficial 3.26 ([R49](docs/capture/e26-r49-cierre-recuperacion-326.md)). Después se instaló en ella el **3.27** (el contenido del 3.25c con cabecera 3.27), con el que arranca ([R51](docs/capture/e26-r51-respaldo-clave-nflasha0-nvram-326.md)); el obturador electrónico aún no está validado ([R52](docs/capture/e26-r52-prueba-fisica-selector-327.md)).

> **⚠️ 3.25c: experimental.** El [3.25c](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.25c-experimental) corrige los errores
> que bloquearon el 3.25 (30/30 comprobaciones y emulación del cargador real sin fallos) y arrancó en la cámara del autor instalado como 3.27 (mismo contenido, otra cabecera), pero
> **solo se ha probado en una cámara** y el obturador electrónico no está validado. El 3.25 original no se publica. Instalar cualquier firmware modificado puede dejar la cámara inservible y **no hay
> recuperación independiente demostrada**. Lee [Estado actual y límites](https://github.com/nicolvus/a6000-fw-decomp/wiki/14-Estado-actual).

## Documentación

Todo el detalle vive en la **[Wiki CFW Sony a6000](https://github.com/nicolvus/a6000-fw-decomp/wiki/Home)** (fuente en [`wiki/`](wiki/Home.md)): requisitos y riesgos, cómo replicarlo de principio a fin, cómo funciona el parche,
resultados, estado actual y límites, herramientas, glosario y mapa del repositorio. La wiki está en español e inglés; los informes de investigación y los comentarios del código, solo en español. Los paquetes ya construidos están en el
[release `fw-3.23-3.24`](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.23-3.24) y, como *pre-release* experimental, en
[`fw-3.25c-experimental`](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.25c-experimental) (3.25c y 3.26 de vuelta atrás). [Tablero de progreso](https://nicolvus.github.io/a6000-fw-decomp/progress/) (estado actual, cobertura y pruebas) · [portada del sitio](https://nicolvus.github.io/a6000-fw-decomp/).

| Versión | Qué hace | Estado |
|---|---|---|
| 3.23 | Parche de Darwin: el motor y las bobinas del obturador nunca se mueven | **Instalado y confirmado** en cámara real: silencioso y sin errores |
| 3.24 | Darwin oficial con número de versión 3.24 (vuelta atrás desde el 3.23) | Verificado offline, nunca instalado |
| 3.25 | EFCS / selector Electronic desde el menú | **Dejó sin arrancar la cámara del autor** (no publicado) |
| 3.25c | 3.25 con `nflasha3` en el formato exacto de Sony | Publicado como experimental; verificado offline; su contenido se instaló en la cámara del autor como 3.27 |
| 3.26 | Contenido oficial de Sony con número de versión 3.26 (vuelta atrás desde el 3.25c) | Verificado offline; instalado una vez en la cámara del autor para recuperarla ([R49](docs/capture/e26-r49-cierre-recuperacion-326.md)) |
| 3.27 | Contenido del 3.25c con cabecera 3.27 (la cámara ya estaba en 3.26) | **Instalado** en la cámara del autor, no publicado como `.dat` ([R50](docs/capture/e26-r50-paquete-327.md), [R51](docs/capture/e26-r51-respaldo-clave-nflasha0-nvram-326.md)) |
| 3.28 | Contenido oficial de Sony con cabecera 3.28 (reserva si el 3.27 falla) | Construido; verificado offline, no instalado, no publicado |

**Estado:** el firmware 3.23 (T040) hace disparar la cámara en silencio y sin error; el 3.25 (E26) dejó la cámara del autor sin arrancar; su causa está corregida en el 3.25c (experimental, probado en una sola cámara como 3.27, [R45](docs/capture/e26-r45-firmware-325c-experimental.md)) y esa cámara se recuperó por SWD con el actualizador oficial y el 3.26 ([R49](docs/capture/e26-r49-cierre-recuperacion-326.md)).
Detalle en [Estado actual y límites](https://github.com/nicolvus/a6000-fw-decomp/wiki/14-Estado-actual). Contribuir: [CONTRIBUTING.md](CONTRIBUTING.md).

## Funciones objetivo

Detalle en [Objetivos](https://github.com/nicolvus/a6000-fw-decomp/wiki/16-Objetivos) (✅ = verificada en cámara). ≈ = modelo de Sony según mi memoria, sin verificar (la búsqueda web solo confirmó Silent Shooting → α7S, FTP → α9 y AF Track Sens → α99 II); puede no ser el primero.

| Función | Categoría | Origen | Estado |
|---|---|---|---|
| Silent Shooting | En curso | Sony α7S | ⬜ |
| Picture Profiles PP1–PP10 | En curso | ≈Sony α7R III | ⬜ |
| Obturación máxima 1/8000 | Foto | ≈Sony α7 | ⬜ |
| ISO expandido hasta 409600 | Foto | Sony α7S | ⬜ |
| Pixel Shift Multi Shooting / High Res Shot / Handheld High Res Shot | Foto | ≈Sony α7R III; Olympus E-M1 II, E-M1X; Panasonic G9 | ⬜ |
| 4K/6K Photo (incl. 4K Photo Burst S/S) | Foto | Panasonic GH5, G9 | ⬜ |
| Pre Capture photo / Pro Capture / Pre-Burst 4K/6K | Foto | Olympus E-M1 II; Panasonic GH5, G9 | ⬜ |
| Post Focus | Foto | Panasonic GH5, G9 | ⬜ |
| Multiple Exposure | Foto | Canon EOS 7D Mark II; Nikon D850; Olympus E-M1 II | ⬜ |
| Live Composite | Foto | Olympus E-M1 II | ⬜ |
| Live Bulb / Live Time | Foto | Olympus E-M1 II | ⬜ |
| Bulb Timer | Foto | Canon EOS 7D Mark II | ⬜ |
| Focus Shift Shooting / Focus Stacking | Foto | Nikon D850; Panasonic GH5, G9; Olympus E-M1 II, E-M1X | ⬜ |
| Smile Shutter | Foto | Sony α5100 | ⬜ |
| Intervalómetro interno | Foto | ≈Sony α9 | ⬜ |
| Interval AE Tracking Sensitivity / Exposure Smoothing | Foto | ≈Sony α7R III; Nikon D850 | ⬜ |
| Anti-Flicker Shooting / Flicker Reduction / Flicker Scan | Foto | Canon EOS 7D Mark II; Nikon D500, D850; Fujifilm X-T3; Olympus E-M1 II, E-M1X | ⬜ |
| Keystone Compensation | Foto | Olympus E-M1 II, E-M1X | ⬜ |
| Live ND | Foto | Olympus E-M1X | ⬜ |
| Rating de fotografías en cámara | Foto | ≈Sony α9 | ⬜ |
| S-Log2 | Imagen y color | ≈Sony α7S | ⬜ |
| S-Log3 | Imagen y color | ≈Sony α7S II | ⬜ |
| HLG 1-3 | Imagen y color | ≈Sony α7R III | ⬜ |
| D Range Priority | Imagen y color | Fujifilm X-T3 | ⬜ |
| Color Chrome Effect | Imagen y color | Fujifilm X-T3 | ⬜ |
| Importación de LUTs | Imagen y color | Sony ZV-E1 | ⬜ |
| Film simulation directo | Imagen y color | Fujifilm X-T5 | ⬜ |
| Full HD / HD 120 fps | Video | ≈Sony α6300 | ⬜ |
| Variable Frame Rate | Video | Panasonic GH5 | ⬜ |
| 4K interno | Video | ≈Sony α7R II | ⬜ |
| Dual Video Recording | Video | ≈Sony α7R III | ⬜ |
| Salida HDMI 4K | Video | Sony α7S | ⬜ |
| Timecode / User Bit | Video | ≈Sony α7S II | ⬜ |
| Loop Recording | Video | Panasonic GH5 | ⬜ |
| Movie Silent Control / Silent Multi Controller | Video | Fujifilm X-T3; Sony α99 II | ⬜ |
| Anamorphic Desqueeze | Video | Panasonic GH5 | ⬜ |
| Synchro Scan | Video | Panasonic GH5 | ⬜ |
| Auto Object Framing | Video | ≈Sony ZV-E1 | ⬜ |
| Voice Memo | Video | ≈Sony α9 | ⬜ |
| Zebra 0–109 % | Monitorización | ≈Sony α6400 | ⬜ |
| Waveform Monitor | Monitorización | Panasonic GH5 | ⬜ |
| Vectorscope | Monitorización | Panasonic GH5 | ⬜ |
| Gamma Display Assist | Monitorización | ≈Sony α7R III | ⬜ |
| Sports Finder Mode | Monitorización | Fujifilm X-T3 | ⬜ |
| Eye AF en tiempo real | Enfoque | ≈Sony α9 | ⬜ |
| Seguimiento AF en tiempo real (3D Tracking / EOS iTR AF) | Enfoque | ≈Sony α6400; Nikon D500, D850; Canon EOS 7D Mark II | ⬜ |
| Ajustes de sensibilidad del seguimiento AF (AF-C Custom Settings / AF-C Cases) | Enfoque | Sony α99 II; Fujifilm X-T3; Panasonic GH5; Olympus E-M1 II; Canon EOS 7D Mark II | ⬜ |
| AF Acceleration/Deceleration Tracking | Enfoque | Canon EOS 7D Mark II | ⬜ |
| AF Range Control | Enfoque | ≈Sony α99 II | ⬜ |
| AF Micro Adjustment | Enfoque | ≈Sony α99 | ⬜ |
| Pre-AF | Enfoque | Fujifilm X-T3 | ⬜ |
| AF Point Auto Switching / Zone Area Switching | Enfoque | Canon EOS 7D Mark II; Fujifilm X-T3 | ⬜ |
| Starry Sky AF | Enfoque | Olympus E-M1 II | ⬜ |
| Intelligent Subject Detection AF | Enfoque | Olympus E-M1X | ⬜ |
| Carga USB con la cámara encendida | Sistema y conectividad | ≈Sony α7 II | ⬜ |
| FTP Background Transfer | Sistema y conectividad | Sony α9 | ⬜ |

## Copyright y uso

**Copyright.** Los dos `.dat` del [release `fw-3.23-3.24`](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.23-3.24) son el
firmware oficial de Sony 3.21 con una modificación binaria mínima y documentada en `darwin_core.bin` (2–9 bytes; ver
[Cómo funciona el parche](https://github.com/nicolvus/a6000-fw-decomp/wiki/8-Como-funciona-el-parche) y [E25-05](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e25-05-preparacion-paquetes-323-324.md)).
Los del [release `fw-3.25c-experimental`](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.25c-experimental) son el mismo firmware
con 22 bytes cambiados en `darwin_core.bin` y 89 en `av-cam.bin` (3.25c), o sin cambios salvo el número de versión (3.26)
([R45](docs/capture/e26-r45-firmware-325c-experimental.md)).
El firmware original es © Sony Corporation, que conserva todos los derechos sobre él. El autor **no tiene ninguna licencia de Sony**
sobre ese firmware y este repositorio no reclama titularidad sobre él. Que el proyecto sea abierto no cambia eso: la apertura
alcanza solo a lo que el autor escribió (scripts, análisis, documentación), no a la parte de Sony contenida en los `.dat`.
Se publican con fines de investigación e interoperabilidad (ingeniería inversa para modificar el comportamiento del hardware que el
autor posee), sin incluir código fuente de Sony. Esta nota documenta la postura del autor, no es una garantía legal, y los
archivos se retirarán si Sony lo solicita.

**Uso.**
- Todo se ofrece «tal cual», sin garantía de ningún tipo; usarlo es bajo tu propio riesgo y puede inutilizar la cámara (ver [Estado actual y límites](https://github.com/nicolvus/a6000-fw-decomp/wiki/14-Estado-actual)).
- Pensado para investigación, aprendizaje y uso personal en una cámara de tu propiedad. No lo uses para eludir protecciones con fines ilícitos ni para redistribuir firmware de Sony por tu cuenta.
- El código, los scripts, el análisis y la documentación del autor se publican bajo licencia [MIT](LICENSE). Esa licencia **no** cubre el firmware de Sony ni los `.dat` del release, ni el material de terceros de abajo.

**Material de Sony y de terceros que usa el proyecto**
- **Código fuente publicado por Sony** para esta cámara (Linux y demás paquetes de código abierto). Se usa para entender el arranque, los controladores y la consola de Loader2/Loader3. Conserva su licencia original (GPL y otras); las copias extraídas están en `analysis/session18/`.
- **Manual de servicio de nivel 3** de la ILCE-6000/6000L/6000Y (Rev. 1.1), de acceso público en la web. Se usa como fuente de esquemas eléctricos y de hojas de la placa. El PDF **no** se versiona (está en `.gitignore`); en `references/manuals/` solo hay el manifiesto con su hash y origen y unas pocas páginas de ejemplo.
- **Firmware oficial 3.21**: lo descarga cada persona desde el servidor de Sony con `scripts/agent/bootstrap.sh`; no se incluye en el repositorio.
- **Herramientas de terceros** con su propia licencia: [Sony-PMCA-RE](https://github.com/ma1co/Sony-PMCA-RE), [fwtool.py](https://github.com/ma1co/fwtool.py) y [OpenMemories-Tweak](https://github.com/ma1co/OpenMemories-Tweak) en `references/`.
