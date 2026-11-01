# Sony A6000 — Silent Shutter

[![módulos](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-modulos.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![sesiones](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-sesiones.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![pruebas](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-pruebas.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![CI](https://github.com/nicolvus/a6000-fw-decomp/actions/workflows/tests.yml/badge.svg)](https://github.com/nicolvus/a6000-fw-decomp/actions/workflows/tests.yml)

Ingeniería inversa del firmware 3.21 de la Sony A6000 (ILCE-6000: BIONZ + microcontrolador Darwin) para disparar con
obturador electrónico. **Hito:** con el firmware modificado **3.23** (parche de 2 bytes sobre Darwin) la cámara real disparó en
silencio y sin error. **Después**, el firmware integrado **3.25** dejó la cámara sin arrancar; hoy el proyecto investiga su
recuperación, solo con análisis offline.

> **⚠️ No instales el 3.25.** Tras instalarlo, la cámara del autor no arranca (LED 3 lentos + 2 rápidos). Instalar cualquier firmware
> modificado puede dejar la cámara inservible y **no hay recuperación independiente demostrada**. Lee [Estado actual y límites](https://github.com/nicolvus/a6000-fw-decomp/wiki/14-Estado-actual).

## Documentación

Todo el detalle vive en la **[Wiki CFW Sony a6000](https://github.com/nicolvus/a6000-fw-decomp/wiki/Home)** (fuente en [`wiki/`](wiki/Home.md)): requisitos y riesgos, cómo replicarlo de principio a fin, cómo funciona el parche,
resultados, estado actual y límites, herramientas, glosario y mapa del repositorio. Los paquetes ya construidos están en el
[release `fw-3.23-3.24`](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.23-3.24). [Tablero de progreso](https://nicolvus.github.io/a6000-fw-decomp/progress/) (estado actual, cobertura y pruebas) · [portada del sitio](https://nicolvus.github.io/a6000-fw-decomp/).

**Estado:** el firmware 3.23 (T040) hace disparar la cámara en silencio y sin error; el 3.25 (E26) dejó la cámara del autor sin arrancar y hoy se estudia su recuperación solo offline.
Detalle en [Estado actual y límites](https://github.com/nicolvus/a6000-fw-decomp/wiki/14-Estado-actual). Contribuir: [CONTRIBUTING.md](CONTRIBUTING.md).

## Copyright y uso

**Copyright.** Los dos `.dat` del [release `fw-3.23-3.24`](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.23-3.24) son el
firmware oficial de Sony 3.21 con una modificación binaria mínima y documentada en `darwin_core.bin` (2–9 bytes; ver
[Cómo funciona el parche](https://github.com/nicolvus/a6000-fw-decomp/wiki/8-Como-funciona-el-parche) y [E25-05](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e25-05-preparacion-paquetes-323-324.md)).
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
