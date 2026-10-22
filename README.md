# Sony A6000 Firmware Reverse Engineering

Proyecto de ingeniería inversa del firmware **Sony A6000 (fw 3.21)**, con foco en la línea de captura y el obturador electrónico.

> Restricciones activas: sin ejecutar firmware en cámara, sin flasheo y sin pruebas físicas no autorizadas.

## Estado rápido

- **Resumen operativo:** [`knowledge/CURRENT.md`](knowledge/CURRENT.md)
- **Estado de investigación y reglas:** [`docs/STATE.md`](docs/STATE.md)
- **Historial de fases:** [`knowledge/PROGRESS.md`](knowledge/PROGRESS.md)
- **Agentes autónomos y triaje S400:** [`docs/agentes-opencode.md`](docs/agentes-opencode.md), [`analysis/s400_open_questions_triage/`](analysis/s400_open_questions_triage/README.md) (132 filas: 51 correcciones aplicadas, 81 falsos positivos, 0 vigentes)
- **Catálogo de hitos técnicos:** [`docs/capture/linea-general-re.md`](docs/capture/linea-general-re.md)

## Avance total


- **Línea general de módulos:** **25.81%** (**96/372**) cubiertos — **58** con hito propio y **38** como sub-etiqueta de un módulo ya decodificado; **276 pendientes reales**.
- **Módulos “contenido nuevo” (S130):** **100%** (**17/17**) cerrados.
- **Obturador completamente electrónico:** [S51](docs/capture/s51-decision.md) mantiene la decisión de no parchear; [P1–P8](docs/capture/physical-test-plan.md) siguen sin ejecutarse.

[![módulos](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-modulos.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![sesiones](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-sesiones.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![pruebas](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-pruebas.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)

![progreso](https://nicolvus.github.io/a6000-fw-decomp/progress/progress.svg)

<sub>GitHub no permite incrustar páginas en el README: los badges se leen de Pages y se actualizan con cada despliegue; el tablero completo (cuadrados, familias, prioridades) está en la [página de progreso](https://nicolvus.github.io/a6000-fw-decomp/progress/).</sub>

Fuente de métricas: [`analysis/s178_census/census.md`](analysis/s178_census/census.md).

### Visualización en GitHub Pages

- Tablero de avance en cuadrados (módulos, sesiones y pruebas físicas, estilo [AnyPS5](https://boykopovar.github.io/AnyPS5/progress.html)): <https://nicolvus.github.io/a6000-fw-decomp/progress/>
- Índice de sesiones y verificador Sx: <https://nicolvus.github.io/a6000-fw-decomp/> (generado desde los informes versionados).

El flujo [Pages](.github/workflows/pages.yml) publica solo `site/`; el generador
`scripts/build_pages_status.py` actualiza el índice y genera `docs/progress/index.html` y los badges `site/badge-*.json` y `progress.svg` (solo en Pages).

### Fase del agente A — sensor y driver (S200–S204)

Completado: comparación de registros y tiempos de lectura/exposición IMX235 (A7S fw3.20) vs IMX210 (A6000 fw3.21), una tabla por subsistema (`docs/capture/s201-imx210-imx235-registers.md`, `s202-imx210-imx235-timing.md`, `s204-clasificacion-final.md`). La A7S implementa el obturador silencioso por **drive mode** (`tipo==2` → modos `0x4e`/`0x4f`, selector `0x43826d58`) y su tabla de timings, no por `CheckSet*` de LiroSeq (0/0 en ambos) ni por mensaje `…ForLiro` (rechazado en ambos). La A6000 no tiene modos de lectura silenciosa equivalentes. **S51 sin cambios (A=NO, B=NO, C=NO).**

## Fase del agente D — módulos de línea general (S500+)

S500 cerrado: módulo `[VDF]` (visor/display) — 243 cadenas en A6000 vs 162 en A7S/A6300; 81 exclusivas de la A6000 concentran la ruta QFHD/4K, el índice EO y el paralaje EVF. 78 funciones contenedoras y 298 xrefs. Informe `docs/capture/s500-vdf.md`, tests `tests/test_s500_vdf.py` (5 verdes). S501 cerrado: módulo `[STK]` (saliencia/tracking) — 76 cadenas en A6000/A7S, 0 en A6300; idéntico A6000/A7S. Código Thumb no sembrado: 143 xrefs sin función resuelta. Informe `docs/capture/s501-stk.md`, tests `tests/test_s501_stk.py` (5 verdes). S502 cerrado: módulo `[EIS]` (estabilización) — 4 cadenas `[CAMERA_IS][EIS]` exclusivas de A6000; 3 funciones. Informe `docs/capture/s502-eis.md`, tests `tests/test_s502_eis.py` (5 verdes). S503 cerrado: módulo `[ZPD]` (zero point detection/AF) — 55 cadenas en A6000 vs 10 A7S/48 A6300; RTTI `Camera::ZPD` completo; 9 funciones. Informe `docs/capture/s503-zpd.md`, tests `tests/test_s503_zpd.py` (5 verdes). S504 cerrado: módulo `[STABILIZER]` (estabilización) — 3 cadenas exclusivas de A6000; 1 función. Informe `docs/capture/s504-stabilizer.md`, tests `tests/test_s504_stabilizer.py` (5 verdes). Cola regenerada S505+.

## Objetivo técnico vigente

Responder con evidencia estática si la A6000 puede soportar captura totalmente electrónica a resolución completa, separando siempre:

- **HECHO verificado**
- **INFERENCIA**
- **NO VERIFICADO**

## Estructura mínima del repo

- `docs/capture/`: informes por hito (Sxx)
- `analysis/`: scripts y evidencia reproducible
- `knowledge/`: estado operativo y continuidad
- `projects/electronic-shutter/`: subproyecto del obturador electrónico

## Nota histórica

La versión extensa anterior del README se conserva en:
[`docs/history/README-historial-2026-10-21.md`](docs/history/README-historial-2026-10-21.md)

### Fase del agente B — imager: estado y gates (S300–S399)

S300 cierra el barrido único de xrefs al objeto de estado del IMX210 (`0x43f72d02`, slot GOT `0x4401f990`): 67 sitios clasificados (56 lectura, 6 escritura, 3 spill, 1 propagación, 1 dato), **cero escritores de los gates `+3`/`+6`** (8 lectores de cada uno en el dumper `FUN_43858338`) y únicos stores a `+0x00`/`+0x02`. Corrige el sesgo +0x58 de la rev.1. [`docs/capture/s300-state-xref-sweep.md`](docs/capture/s300-state-xref-sweep.md).
S301 repite el barrido en la **A7S fw3.20** (estado `0x43f7bce6`, slot GOT `0x440251e4`): 79 sitios (65 lectura, 8 escritura, 4 spill, 1 propagación, 1 dato). Gates `+3`/`+6` **idénticos** a la A6000 (mismo dumper, 8+8 lecturas, cero escritores) → no son el mecanismo silent. La A7S añade escrituras en `+0xde` y `+0xe6/+0xe8/+0xea` y 11 campos de lectura que la A6000 no usa. [`docs/capture/s301-a7s-state-xref-sweep.md`](docs/capture/s301-a7s-state-xref-sweep.md).
S302 compara drive mode y exposición campo a campo: la función de comprobación de parámetros desplaza **todos** sus offsets (contexto +8, `VdNum` +0xc, `svr_num` +0x10) y el bloque copiado pasa de 4 a 3 palabras; la A7S añade una indirección modo→columna (34 códigos en `0x43fee370`, mapa `0x43c9c5b5`) sobre una matriz de 69 filas × 16 B (A6000: 59). Los modos Silent `0x4e/0x4f` comparten columna de registro con `0x4c/0x4d` (contradicción a re-verificar con S204). [`docs/capture/s302-drive-modes.md`](docs/capture/s302-drive-modes.md).
S303 resuelve el árbol de referencias de la tabla `0x43ff3200`: **148** entradas (la rev.1 contaba 60), terminador `0x43ff3450`, estado en el índice 18; único literal de la base en el slot GOT `0x4401f080`. El dumper de gates tiene **2** callers directos (`0x43859868`/`0x43859892`, ambos en `FUN_43859710`), que a su vez recibe 10 llamadas de 7 funciones; `FUN_43859944` acumula 35. Corrige el sesgo +0x58 de S303rev1/S304. REA confirma 1/5 funciones y **no ve** el slot `0x4401f080` (undecodable); por bytes su usuario está en `0x4378bb6c`. [`docs/capture/s303-ref-tree-43ff3200.md`](docs/capture/s303-ref-tree-43ff3200.md).
S307 localiza el origen de las escrituras exclusivas de la A7S: `+0xde` (`0x4386521a`) y `+0xe6/+0xe8/+0xea` (`0x438643a6/b2/bc`) viven en funciones cuya firma de store de 24 B **no existe en la A6000** (0 coincidencias); dos escritores de `+0x02` también son A7S-only. `FUN_438645bc` (tiempos: lee `+0xae`×1000) tiene un único caller directo (`0x43861be4`) y ningún puntero. [`docs/capture/s307-a7s-only-writers.md`](docs/capture/s307-a7s-only-writers.md).
S308 cierra el flujo: el código de modo del selector (`0x4e/0x4f`) se guarda en `[sp+0x2c]` y se pasa a `0x43ad9704` (thunk de llamada virtual, S310), **no** al bloque de tiempos; éste (`0x438645bc`, entrada corregida) tiene un único caller `0x43861be4` y ningún puntero en tablas. El enlace silent→tiempos queda **NO_VERIFICADO**. [`docs/capture/s308-silent-flow.md`](docs/capture/s308-silent-flow.md).
S309 comprueba la presencia de la cadena silent/config en la A6000: las **siete** funciones (selector, caller, constructor de mensaje, bloque de tiempos y sus dos escritores) tienen **0 coincidencias** de sus primeros 24 B. La diferencia no es un valor distinto en el mismo código: es **código ausente**. [`docs/capture/s309-chain-presence.md`](docs/capture/s309-chain-presence.md).
S310 corrige el mecanismo del paso anterior: `0x43ad9704` es un **thunk de llamada virtual** (`obj->vtable[slot]`), no un constructor de mensajes; la familia contigua usa slots `0x64/0x94/0x58/0x74/0x40/0x18`. El consumidor del modo queda en una llamada virtual no resuelta → **NO_VERIFICADO**. [`docs/capture/s310-vtable-thunk.md`](docs/capture/s310-vtable-thunk.md).
S311 cierra la comparación simétrica: de los cuatro escritores de `+0x00`/`+0x02` de la A6000, **dos no están en la A7S** y dos son helpers compartidos. Cada firmware trae su propio código de configuración; el de la A7S añade el selector y el bloque de tiempos. [`docs/capture/s311-a6000-config.md`](docs/capture/s311-a6000-config.md).
S312 cierra el círculo del cluster A7S `+0xae`/`+0xde..+0xea`: sus **seis** funciones consumidoras también tienen **0 coincidencias** en la A6000. Con S300–S311, el cuadro queda: gates idénticos sin escritor, matriz de registros con indirección en la A7S, selector `tipo` y subsistema de tiempos exclusivos de la A7S. [`docs/capture/s312-cluster-consumers.md`](docs/capture/s312-cluster-consumers.md).
S313 consolida el carril B (S300–S312): gates `+3/+6` idénticos y sin escritor, matriz de registros con indirección solo en la A7S, y un subsistema de selector/tiempos (`0x43826d58`, `0x438645bc`) exclusivo de la A7S; documenta lo abierto (objeto/vtable del slot `0x64`, tabla `0x43fee3f8`, semántica física). [`docs/capture/s313-synthesis-carril-b.md`](docs/capture/s313-synthesis-carril-b.md).
