# Sony A6000 Firmware Reverse Engineering

[![módulos](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-modulos.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![sesiones](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-sesiones.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![pruebas](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-pruebas.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)

Ingeniería inversa **estática** del firmware de la **Sony A6000 (ILCE-6000, fw 3.21)**, con foco en la línea de captura y en una
pregunta concreta: ¿puede la cámara hacer fotos a resolución completa **sin cierre mecánico** (obturador totalmente electrónico)?

> Restricciones activas: no se ejecuta firmware en cámara, no se flashea (salvo autorización expresa del usuario para un
> caso concreto) y no hay pruebas físicas hasta agotar la ingeniería inversa necesaria. El repositorio no incluye firmware
> ni volcados (ver [R1](docs/PENDIENTES.md)).

## Objetivo y alcance

- **Firmware analizado:** A6000 fw 3.21 (sensor IMX210, `av-cam` + `libObj.so` y módulos de kernel). Se compara con la **A7S fw 3.20**
  (IMX235, que sí ofrece Silent) y la **A6300 fw 2.01** (controles positivos).
- **Método:** REA/Ghidra + bytes y decodificación independiente (LLVM); cada afirmación se etiqueta `VERIFICADO`, `INFERENCIA` o
  `NO_VERIFICADO`. Política completa en [docs/STATE.md](docs/STATE.md).
- **Fuera de alcance por ahora:** parches, flasheo, ejecución de firmware, pruebas en cámara — salvo autorización
  expresa del usuario para un caso concreto.

## Estado técnico actual

| Pregunta | Respuesta (26-10-2026) |
|---|---|
| ¿Hay una ruta de exposición totalmente electrónica demostrada? | **NO** — decisión [S51](docs/capture/s51-decision.md): A=NO, B=NO, C=NO |
| ¿Hay base para un parche justificable? | **NO** — falta fin electrónico de integración identificado |
| ¿Está demostrado que el hardware lo impide? | **NO** — nada de lo analizado excluye un fin electrónico por filas |
| ¿Estado del obturador electrónico completo? | **Abierto, sin validar.** Hay piezas reutilizables, ninguna captura silenciosa completa; ver [subproyecto](projects/electronic-shutter/README.md) |
| ¿Qué falta? | Lo estático está cerrado con límite (E1 `NO_VERIFICADO`); el resto necesita datos (hojas de datos IMX210/IMX235, mapa de pines) o cámara. Lista única: [docs/PENDIENTES.md](docs/PENDIENTES.md) |

## Progreso

- **Censo documental de etiquetas de trazas:** 133/372 (35,75 %) con informe propio; 226 pendientes y 13 descartadas. Mide **documentación**,
  no código descompilado ni funcionamiento físico ([S178](docs/capture/s178-census.md)).
- **Cobertura de la ruta del obturador:** [matriz de descompilación y límites REA/Unicorn](docs/capture/s51-static-coverage-and-tool-limits.md).
- **Pruebas físicas:** [P1–P8](docs/capture/physical-test-plan.md), [P9–P12](docs/capture/s402-physical-test-mapping.md) y
  [P13–P21](docs/capture/physical-test-plan-2.md) propuestas, **ninguna ejecutada**, diferidas por orden del usuario.
- **Último cierre (26-10-2026):** E19, E17 y el resto de E10 cerrados con límite; E20 en su límite estático; CI de la suite (R2); auditoría
  integral del repositorio. Cierres y su evidencia: [S403](docs/capture/s403-cierre-pendientes.md).

![progreso](https://nicolvus.github.io/a6000-fw-decomp/progress/progress.svg)

<sub>Los badges se leen de GitHub Pages y se actualizan con cada despliegue. Tablero completo (cuadrados, familias, prioridades):
<https://nicolvus.github.io/a6000-fw-decomp/progress/> · índice de sesiones y verificador Sx: <https://nicolvus.github.io/a6000-fw-decomp/>.
El flujo [Pages](.github/workflows/pages.yml) publica solo `site/`; `scripts/build_pages_status.py` genera `docs/progress/index.html`,
`site/badge-*.json` y `progress.svg`. Fuente de métricas: [`analysis/s178_census/census.md`](analysis/s178_census/census.md).</sub>

## Principales hallazgos consolidados

- **Captura:** RecordStill (`0x908afc`) y RecordImage (`0x90b248`) de la A6000 son equivalentes a los de la A7S salvo líneas de log; la
  cola `0x40193` llega a un receptor LIRO. La activación real en ejecución sigue sin verificar
  ([S402](docs/capture/static-closure-2026-10-25.md), [contrato](docs/capture/recordstill-contract-audit-2026-10-23.md)).
- **Imager:** los gates `+3/+6` del estado IMX210 son idénticos a los de la A7S y no tienen escritor estático; el mecanismo por modo
  (matriz → T1/T2/T3 → máscara → MMIO DFE/CISIF) es el mismo código con datos distintos ([S341](docs/capture/s341-synthesis-b2.md)).
- **Silent (A7S):** vía UI → LIRO `0x40e3` → bit `0x20`; la A6000 carece del selector y del bloque de tiempos de la A7S, y los mensajes
  `…ForLiro` están rechazados en ambas ([S401](docs/capture/s401-a7s-silent-control-path.md), [S174](docs/capture/s174-forliro-api.md)).
- **Cortinas:** GPIO de cortinillas identificados (P4B–P4E); el enlace con el banco/bit del firmware no consta ([E11](docs/PENDIENTES.md)).
- **Conclusiones rectificadas:** qué se rectificó y con qué informe, en [docs/STATE.md](docs/STATE.md#conclusiones-corregidas-no-reusar-versiones-previas)
  y en [docs/CORRECTIONS.md](docs/CORRECTIONS.md) (derivado del grafo).

## Subsistemas investigados

Informes de `docs/capture/`, con sus pruebas y evidencia, por tema en **[docs/INDEX.md](docs/INDEX.md)**:
[captura](docs/INDEX.md#informes-por-subsistema) · sensor e imager · obturador · control y comunicación · procesamiento de imagen ·
otros (AF, estabilización, vídeo, Wi-Fi, audio, lentes, energía) · comparaciones A6000/A7S/A6300 · herramientas y validación.
Catálogo de módulos de trazas: [linea-general-re.md](docs/capture/linea-general-re.md).

## Navegación

| Necesito… | Voy a… |
|---|---|
| Contexto mínimo para retomar | [knowledge/CURRENT.md](knowledge/CURRENT.md) |
| Conclusiones y límites vigentes | [docs/STATE.md](docs/STATE.md) |
| Qué falta (abierto/bloqueado/cerrado) | [docs/PENDIENTES.md](docs/PENDIENTES.md) |
| Informes por subsistema | [docs/INDEX.md](docs/INDEX.md) |
| Historial cronológico | [knowledge/PROGRESS.md](knowledge/PROGRESS.md) |
| Objetivo principal | [projects/electronic-shutter/](projects/electronic-shutter/README.md) |
| Versiones íntegras anteriores de README/CURRENT/STATE | [docs/history/](docs/history/README-historial-2026-10-26.md), [knowledge/history/](knowledge/history/CURRENT-historial-2026-10-26.md) |
| Uso por agentes (Claude Code, Codex, DeepSeek) | [docs/agent/README.md](docs/agent/README.md), [AGENTS.md](AGENTS.md), [CLAUDE.md](CLAUDE.md) |

## Reproducir análisis y pruebas

```bash
source .venv/bin/activate
python3 scripts/knowledge/search.py text "concepto"      # buscar sin releer el repo
python3 scripts/knowledge/search.py exact "0x90b248"      # dirección o símbolo
python -m pytest tests -q                                 # CI=1 omite lo que necesita firmware no versionado
python3 scripts/audit/repo_audit.py                       # auditoría mecánica: enlaces, pendientes, cifras
python3 scripts/knowledge/build_subsystem_index.py        # regenera docs/INDEX.md
```

Cada informe `docs/capture/sNNN-*.md` tiene su evidencia en `analysis/sNNN*/` y su verificador en `tests/test_sNNN_*.py`. El firmware y los
volcados de cámara no están en el repositorio: las pruebas que los necesitan se omiten en CI.

## Seguridad y contribución

- No se ejecuta firmware ni se toca la cámara; toda prueba física requiere autorización expresa y backup NVRAM previo.
- No se suben firmware, `*.bin`/`*.elf`, volcados ni binarios de Sony; commits convencionales y por ruta.
- Toda tarea que se haga, descarte o reabra actualiza [docs/PENDIENTES.md](docs/PENDIENTES.md) en el mismo commit. Una sesión nueva **no**
  añade párrafos aquí: se documenta en su informe, en PENDIENTES, en STATE si cambia una conclusión y en PROGRESS.
