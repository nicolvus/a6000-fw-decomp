# Sony A6000 — obturador electrónico y CFW

[![English version](https://img.shields.io/badge/🇬🇧_English_version-blue?style=for-the-badge)](README.en.md)

[![módulos](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-modulos.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![sesiones](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-sesiones.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![pruebas](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-pruebas.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![CI](https://github.com/nicolvus/a6000-fw-decomp/actions/workflows/tests.yml/badge.svg)](https://github.com/nicolvus/a6000-fw-decomp/actions/workflows/tests.yml)
[![Featured in Awesome REA](https://img.shields.io/badge/Featured%20in-Awesome%20REA-f0b429)](https://github.com/AIshihzong/awesome-reverse-engineer-anything)

Ingeniería inversa del firmware **3.21** de la Sony A6000 (ILCE-6000: BIONZ + microcontrolador Darwin) para
conseguir **obturación electrónica** y añadir funciones que la cámara no tiene. El repositorio contiene análisis,
parches, scripts y documentación; el firmware de Sony no se versiona aquí (lo descarga
`scripts/agent/bootstrap.sh` desde el servidor de Sony).

## Estado ahora (25-11-2026)

| Área | Cómo está | Evidencia |
|---|---|---|
| **Obturador electrónico** | **Funciona** en la cámara del autor desde el CFW **3.30** (envío en línea de `pkt[0x0e]` + compuerta de Darwin). El **3.23** fue el primer hito: parche de 2 bytes en Darwin y la cámara dispara sin mover motor ni bobinas | [R54](docs/capture/e26-r54-paquete-330-envio-pkt0e.md), [T040](docs/capture/registro-pruebas-camara.md) |
| **Silent calibrado** | Exposición uniforme por filas; en el CFW **3.77** queda nivelada de 1/1250 a 1/50 (E = 17,135 µs·n + 564 µs) | [R87](docs/capture/e26-r87-disparo-remoto-y-recalibracion.md) |
| **EFCS** | Selector EFCS/Electronic en el menú. Con EFCS activo se pierde ≈1,27 ms y la foto sale **negra desde 1/1000**, también con firmware oficial de Sony: la causa es física, no de firmware | [R74](docs/capture/e26-r74-conclusion-final-efcs-negro.md), [R83](docs/capture/e26-r83-informe-final-efcs-negro.md) |
| **Cámara del autor** | CFW de la serie 3.93/4.0x sobre la base Silent (`pp` es la última build auditada); el paquete oficial 3.21 de vuelta atrás está verificado | [G105](docs/gui/g105-builds-por-funcion.md), [auditoría del CFW](reports/film-pb-1-auditoria-cfw-20261127.md) |
| **Vídeo (FILM-PB-1)** | **Abierto**: los clips se graban y se ven en el PC, pero la cámara no los reproduce. Se descartó que sea un parche; la causa probable es que «Selector PAL/NTSC» no casa con la cadencia de los clips, y ese ajuste no está expuesto en el menú de este modelo | [causa probable](reports/film-pb-1-causa-sistema-tv-20261127.md) |
| **Interfaz (GUI)** | Arnés QEMU que arranca `im.elf` 3.21 y dibuja menús, iconos y ajustes sin tocar la cámara; encima se construyen los CFW con función nueva | [carril GUI](docs/gui/README.md), [G22](docs/gui/g22-arnes-ui-qemu.md) |
| **Carga USB encendida** | En investigación: la orden llega a Darwin, pero con cargador de pared no se aplica | [informe](docs/capture/usb-carga-encendida.md) |
| **Recuperación** | Cerrada: cámara recuperada el 03-11-2026 por SWD, forzando el actualizador de fábrica sin escribir NAND | [R49](docs/capture/e26-r49-cierre-recuperacion-326.md) |

## Serie de firmware

Los números son **builds internos**, no versiones de Sony: cada uno es un `.dat` construido desde el 3.21 oficial y
verificado offline antes de instalar. Se instalan con `pmca-console firmware --flash` (y `--reflash` para cambiar
entre builds del mismo número).

| Build | Qué añade | Estado |
|---|---|---|
| 3.23 / 3.24 | Parche de Darwin: motor y bobinas del obturador nunca se mueven / misma carga con número 3.24 | Instalado y confirmado en cámara (3.23); 3.24 verificado offline |
| 3.25 | Selector EFCS/Electronic desde el menú | **Dejó la cámara sin arrancar**: formato TPZL de `nflasha3` (incidente E26, [R36](docs/capture/e26-r36-causa-fallo-325.md)) |
| 3.25c / 3.26 / 3.27 | El 3.25 con `nflasha3` en forma de Sony, y las vueltas atrás | 3.26 instalado por el actualizador oficial para recuperar la cámara; 3.27 = 3.25c instalado |
| 3.30 – 3.38 | Obturador electrónico real (`pkt[0x0e]` en línea) y calibración | Instalados y probados en cámara |
| 3.76 / 3.77 | Silent calibrado en `av-cam` (ShutMode 0 + `r5`) | Validado en RAM; base de los CFW siguientes |
| 3.93 (`base`/`film`/`pp`/`exfine`/`iso`) | Una build por función sobre la base Silent: Film Simulation, Picture Profile, Extra Fine, ISO | Instaladas y probadas de una en una; `iso` deja la cámara en bucle de arranque |
| 4.01 – 4.02 | Receta de Film por la GUI + iconos Fn; bisección del vídeo (solo Silent) | Instaladas; es cuando se detecta FILM-PB-1 |
| 4.03 / 4.04 | Núcleo de la 4.02 con `/usr` de Sony / Sony 3.21 intacto salvo `nflasha5` (control) | Construidas y auditadas, sin instalar |

## Límites y riesgos

> **⚠️ Instalar firmware modificado puede dejar la cámara inservible.** La recuperación del BIONZ por SWD está
> probada ([R48](docs/capture/e26-r48-plan-recuperacion-actualizador-swd.md),
> [R49](docs/capture/e26-r49-cierre-recuperacion-326.md)), pero **no hay recuperación independiente del firmware de
> Darwin demostrada** y solo se ha probado en **una cámara** del autor. Lee
> [Estado actual y límites](https://github.com/nicolvus/a6000-fw-decomp/wiki/14-Estado-actual) antes de tocar nada.

- El obturador electrónico está medido en una cámara y una unidad de sensor; con EFCS activo, negro desde 1/1000.
- Con el CFW actual **la cámara no reproduce vídeo** (FILM-PB-1); grabar y ver en el PC sí funciona.
- Las cifras del tablero (módulos, sesiones, pruebas) miden documentación y verificadores, no funcionamiento en cámara.

## Documentación

| Dónde | Qué hay |
|---|---|
| **[Wiki](https://github.com/nicolvus/a6000-fw-decomp/wiki/Home)** ([fuente](wiki/Home.md), ES/EN) | Requisitos y riesgos, replicar de principio a fin, cómo funciona el parche, resultados, estado, herramientas, glosario y mapa del repositorio |
| [Tablero de progreso](https://nicolvus.github.io/a6000-fw-decomp/progress/) · [portada](https://nicolvus.github.io/a6000-fw-decomp/) | Estado, cobertura y pruebas generados del repositorio |
| [knowledge/CURRENT.md](knowledge/CURRENT.md) | Contexto mínimo para agentes |
| [docs/STATE.md](docs/STATE.md) | Conclusiones vigentes y límites |
| [docs/PENDIENTES.md](docs/PENDIENTES.md) | Tareas abiertas, bloqueadas y cerradas (única fuente) |
| [docs/INDEX.md](docs/INDEX.md) | Informes por subsistema; los informes están en [`docs/capture/`](docs/capture/) y en [`reports/`](reports/) |
| [FUNCIONES.md](FUNCIONES.md) | Lista completa de funciones objetivo |
| [ORDEN.md](ORDEN.md) · [ORDER.md](ORDER.md) | Reglas de orden del repositorio (vinculantes; las comprueban `scripts/audit/check_order.py` y `tests/test_order.py`) |

Los informes de investigación y los comentarios del código están en español; la wiki y este README, en español e inglés.

## Funciones objetivo

**En la cámara:** base Silent, Picture Profiles PP1–PP10 (menú, listas y selector), Film Simulation, Extra Fine
(con el fallo abierto de «sin espacio en la tarjeta») y los iconos/textos propios de la GUI. **Construidas y
auditadas, con el arranque en bucle por resolver:** ISO expandido. **En investigación:** LUTs, HLG, 1/8000, el resto
de la lista. Estado por función y modelo de origen en [FUNCIONES.md](FUNCIONES.md) y en
[Objetivos](https://github.com/nicolvus/a6000-fw-decomp/wiki/16-Objetivos).

**Descartadas por ahora:** nivel digital (el sensor de orientación es óptico y binario,
[R88](docs/capture/e26-r88-sensor-inclinacion-swd.md)), anamorphic desqueeze (la tabla de parámetros de `av-cam` 3.21
no define el parámetro) y open gate grabando a 6000×4000 (el sensor da 14,98 Hz; la única vía de firmware sería
1440×960, [G112](docs/gui/g112-opengate-video-3-2.md)).

## Construir e instalar

1. `scripts/agent/bootstrap.sh` descarga el 3.21 oficial de Sony (el repositorio **no** contiene firmware).
2. Los paquetes se construyen con los scripts del repositorio: ver
   [Construir los paquetes](https://github.com/nicolvus/a6000-fw-decomp/wiki/4-Construir-los-paquetes) y
   [Instalar el 3.23](https://github.com/nicolvus/a6000-fw-decomp/wiki/5-Instalar-el-3.23). Los `.dat` no se
   publican en el repositorio ni en un release.
3. Antes de cualquier prueba en cámara: backup de NVRAM y autorización expresa del propietario; la IP se toma de
   `A6000_HOST`.

## Estructura del repositorio

```
docs/        informes (capture/), estado, pendientes, índice, carril GUI (gui/)
knowledge/   contexto mínimo, historial y grafos del sistema de conocimiento
scripts/     bootstrap, construcción de paquetes, arnés GUI, herramientas de análisis
tests/       verificadores de cada conclusión (pytest; los que necesitan firmware se omiten)
analysis/    evidencia reproducible y resultados
wiki/        fuente de la wiki (páginas ES y en-* en inglés)
src/, tools/, references/, projects/   código de análisis, utilidades y referencias de terceros
```

## Calidad y contribución

`CI=1 python -m pytest tests -q`, más `ruff` y `mypy` sin avisos nuevos; la CI no usa firmware. Reglas completas en
[CONTRIBUTING.md](CONTRIBUTING.md).

## Copyright y uso

**Copyright.** Los `.dat` que se construyan con estos scripts son firmware oficial de Sony con una modificación
binaria mínima y documentada en `darwin_core.bin` y en `av-cam.bin` (ver
[Cómo funciona el parche](https://github.com/nicolvus/a6000-fw-decomp/wiki/8-Como-funciona-el-parche)). El firmware
original es © Sony Corporation, que conserva todos los derechos; el autor no tiene licencia de Sony sobre él y este
repositorio no reclama titularidad. La apertura del proyecto alcanza solo a lo que el autor escribió (scripts,
análisis, documentación), no a la parte de Sony. Se publica con fines de investigación e interoperabilidad
(ingeniería inversa sobre hardware propio), sin código fuente de Sony. Esta nota documenta la postura del autor, no
es una garantía legal.

**Uso.** Todo se ofrece «tal cual», sin garantía; usarlo es bajo tu propio riesgo y puede inutilizar la cámara.
Pensado para investigación, aprendizaje y uso personal en una cámara de tu propiedad. El código, los scripts, el
análisis y la documentación del autor están bajo licencia [MIT](LICENSE), que **no** cubre el firmware de Sony ni el
material de terceros.

**Material de Sony y de terceros:**

- **Código fuente publicado por Sony** (Linux y demás paquetes abiertos): para entender el arranque, los
  controladores y la consola. Conserva su licencia original.
- **Manual de servicio de nivel 3** de la ILCE-6000/6000L/6000Y (Rev. 1.1), de acceso público: fuente de esquemas y
  hojas de placa. El PDF no se versiona; en `references/manuals/` solo hay manifiesto con hash, origen y páginas de
  ejemplo.
- **Firmware oficial 3.21**: lo descarga cada persona desde el servidor de Sony.
- **Herramientas de terceros** con su licencia: [Sony-PMCA-RE](https://github.com/ma1co/Sony-PMCA-RE),
  [fwtool.py](https://github.com/ma1co/fwtool.py) y
  [OpenMemories-Tweak](https://github.com/ma1co/OpenMemories-Tweak).
