# Sony A6000 Firmware Reverse Engineering

Proyecto de ingeniería inversa del firmware **Sony A6000 (fw 3.21)**, con foco en la línea de captura y el obturador electrónico.

> Restricciones activas: sin ejecutar firmware en cámara, sin flasheo y sin pruebas físicas no autorizadas.

## Estado rápido

- **Resumen operativo:** [`knowledge/CURRENT.md`](knowledge/CURRENT.md)
- **Estado de investigación y reglas:** [`docs/STATE.md`](docs/STATE.md)
- **Historial de fases:** [`knowledge/PROGRESS.md`](knowledge/PROGRESS.md)
- **Catálogo de hitos técnicos:** [`docs/capture/linea-general-re.md`](docs/capture/linea-general-re.md)

## Avance total

![linea-general](https://img.shields.io/badge/línea_general-14.78%25-yellow)
![modulos-nuevos](https://img.shields.io/badge/módulos_nuevos-100%25-brightgreen)

- **Línea general de módulos:** **14.78%** (**55/372**) decodificados.
- **Módulos “contenido nuevo” (S130):** **100%** (**17/17**) cerrados.

<progress value="55" max="372"></progress>

Fuente de métricas: [`analysis/s178_census/census.md`](analysis/s178_census/census.md).

### Visualización en GitHub Pages

- Tablero de avance en cuadrados: <https://nicolvus.github.io/a6000-fw-decomp/progress/>

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
