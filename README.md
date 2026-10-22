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
