# Sony A6000 Firmware Reverse Engineering

[![módulos](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-modulos.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![sesiones](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-sesiones.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)
[![pruebas](https://img.shields.io/endpoint?url=https://nicolvus.github.io/a6000-fw-decomp/badge-pruebas.json)](https://nicolvus.github.io/a6000-fw-decomp/progress/)

Ingeniería inversa del firmware de la **Sony A6000 (ILCE-6000, fw 3.21)**, con foco en una pregunta: ¿puede la cámara hacer
fotos a resolución completa **sin cierre mecánico** (obturador totalmente electrónico)?

> Restricciones activas: no se ejecuta firmware nuevo ni se flashea sin autorización expresa del usuario para un caso
> concreto. Las pruebas en cámara son solo por software, por USB, con backup NVRAM previo y solo con autorización expresa.
> El repositorio no incluye firmware ni volcados (ver [R1](../../docs/PENDIENTES.md)).

## Objetivo y alcance

- **Firmware analizado:** A6000 fw 3.21 (sensor IMX210, `av-cam`, `libObj.so`, `darwin_core` y módulos de kernel). Comparación con la
  **A7S fw 3.20** (IMX235, que sí ofrece Silent) y la **A6300 fw 2.01** (controles positivos).
- **Método:** análisis estático con REA (primero) y Ghidra como respaldo, verificado contra bytes e instrucciones. Cada
  afirmación se etiqueta `VERIFICADO`, `INFERENCIA` o `NO_VERIFICADO`. Política completa en [docs/STATE.md](../../docs/STATE.md).
- **Pruebas en cámara:** registro de cada prueba en [docs/capture/registro-pruebas-camara.md](../../docs/capture/registro-pruebas-camara.md)
  (T001–T039, por USB, con backup NVRAM previo a cada una). Ninguna prueba cambió el firmware de forma persistente.
- **Fuera de alcance por ahora:** flasheo persistente, parches permanentes y cualquier prueba sin autorización expresa.

## Estado técnico actual

| Pregunta | Respuesta (27-10-2026) |
|---|---|
| ¿Hay una ruta de exposición totalmente electrónica demostrada? | **NO**: decisión [S51](../../docs/capture/s51-decision.md) A=NO, B=NO, C=NO. Hay un candidato en curso (ver «Último cierre») |
| ¿Hay base para un parche justificable? | **NO**: falta identificar el fin electrónico de integración |
| ¿Está demostrado que el hardware lo impide? | **NO**: nada de lo analizado excluye un fin electrónico por filas |
| ¿Estado del obturador electrónico completo? | **Abierto, sin validar.** No hay ninguna captura silenciosa completa; ver [subproyecto](../../projects/electronic-shutter/README.md) |
| ¿Qué falta? | Lista única y viva: [docs/PENDIENTES.md](../../docs/PENDIENTES.md) |

## Para otro agente: estado en un minuto

**Pregunta de trabajo:** ¿puede la A6000 capturar a resolución completa sin cierre mecánico? **Respuesta vigente: no demostrado** (S51 A/B/C = NO).

| Línea | Estado a 27-10-2026 |
|---|---|
| E23 (registro `r5` con ShutMode 0 forzado) | Abierto: `r5` controla la exposición de forma monótona hasta ~4200, no uniforme. Inferencia, no prueba de obturador electrónico |
| Rearme y compuerta `0x1fe66` (E24-05…05g) | Cerrado con límite: `0x1fe66`=0 selecciona la lista `[0,7,8,9,10]` de la máquina exterior de Darwin y evita el motor, salvo el freno de la operación 5 |
| Captura sin rearme (E24-05h…05h-4) | Cerrado con límite, **sin bloqueo demostrado ni ausencia demostrable por estática**: el estado 31 espera P29 (`S+0x32=0`, sin plazo) o la FSM ADC-B (`S+0x32≠0`); los estados 3/32 exigen ADC-A y ADC-B terminales |
| Medición pendiente (E24-05e, E24-05h-5) | **Preparada y no ejecutada.** Los métodos T022/T023 leen solo DRAM de BIONZ (`0x83f91e20..0x83f91f30`); **no** leen la SRAM de Darwin. Matriz EFCS ABBAAB y criterios C1–C5 en el [protocolo](../../docs/capture/e24-05e-05h5-protocolo-lectura.md). Una foto normal no prueba el funcionamiento sin rearme |
| Flasheo de Darwin | **No autorizado** (E24-04: sin recuperación demostrada ante un fallo). E24-06 (conectar la cámara) tampoco |

**Límites que no se deben saltar:** nada se ejecuta en la cámara, se escribe en RAM ni se flashea sin autorización expresa del usuario para ese
caso; los valores de Darwin (SRAM `0x2000xxxx`, 12 magnitudes) no tienen vía de lectura demostrada; todo hallazgo se etiqueta
`VERIFICADO` / `INFERENCIA` / `NO_VERIFICADO`. Antes de reutilizar una conclusión, comprobar [docs/CORRECTIONS.md](../../docs/CORRECTIONS.md).

**Siguiente paso posible (requiere decisión del usuario):** autorizar la ejecución de las seis lecturas del protocolo, o evaluar una vía nueva
de lectura de Darwin (analizador lógico pasivo en P29/P4B/P4C/CAIF, E24-05h-2). Orden de lectura para retomar: [CURRENT](../../knowledge/CURRENT.md) →
[PENDIENTES](../../docs/PENDIENTES.md) (E24-05e, E24-05h-1/-5, E24-06) → [STATE](../../docs/STATE.md) → informes de [INDEX](../../docs/INDEX.md).

## Progreso

- **Censo documental de etiquetas de trazas:** 133/372 (35,75 %) con informe propio; 226 pendientes y 13 descartadas. Mide
  **documentación**, no código descompilado ni funcionamiento físico ([S178](../../docs/capture/s178-census.md)).
- **Cobertura de la ruta del obturador:** [matriz de descompilación y límites REA/Unicorn](../../docs/capture/s51-static-coverage-and-tool-limits.md).
- **Pruebas en cámara:** T001–T039 ejecutadas por USB con autorización expresa del usuario, con backup NVRAM antes de cada una.
  Hubo un incidente en T037 (r7=255) que dejó la cámara sin shell; se recuperó tras apagado completo con batería fuera y
  restauración de los cinco sitios parcheados ([registro](../../docs/capture/registro-pruebas-camara.md)).
- **Planes de prueba física:** [P1–P8](../../docs/capture/physical-test-plan.md), [P9–P12](../../docs/capture/s402-physical-test-mapping.md) y
  [P13–P21](../../docs/capture/physical-test-plan-2.md). Su ejecución depende de cada autorización; el estado de cada uno está en el registro.
- **Último cierre (27-10-2026):** E24-05h-4 (cierre estático de la captura sin rearme) y la preparación offline de E24-05e/E24-05h-5
  ([protocolo de lectura](../../docs/capture/e24-05e-05h5-protocolo-lectura.md), **no ejecutado**). E23 sigue ABIERTO; E24-04 a E24-05h-4
  cerrados con límite: no hay evidencia para autorizar otro flasheo de Darwin ni E24-06. Detalle en «Para otro agente».

![progreso](https://nicolvus.github.io/a6000-fw-decomp/progress/progress.svg)

<sub>Los badges se leen de GitHub Pages y se actualizan con cada despliegue. Tablero completo (cuadrados, familias, prioridades):
<https://nicolvus.github.io/a6000-fw-decomp/progress/> · índice de sesiones: <https://nicolvus.github.io/a6000-fw-decomp/>.
El flujo [Pages](../../.github/workflows/pages.yml) publica `site/`; `scripts/build_pages_status.py` genera los badges y `progress.svg`.
Fuente de métricas: [`analysis/s178_census/census.md`](../../analysis/s178_census/census.md).</sub>

## Principales hallazgos consolidados

- **Captura:** RecordStill (`0x908afc`) y RecordImage (`0x90b248`) de la A6000 son equivalentes a los de la A7S salvo líneas de log; la
  cola `0x40193` llega a un receptor LIRO. La activación real en ejecución sigue sin verificar
  ([S402](../../docs/capture/static-closure-2026-10-25.md), [contrato](../../docs/capture/recordstill-contract-audit-2026-10-23.md)).
- **Imager:** los gates `+3/+6` del estado IMX210 son idénticos a los de la A7S y no tienen escritor estático; el mecanismo por modo
  es el mismo código con datos distintos ([S341](../../docs/capture/s341-synthesis-b2.md)).
- **Silent (A7S):** vía UI → LIRO `0x40e3` → bit `0x20`; la A6000 carece del selector y del bloque de tiempos de la A7S, y los mensajes
  `…ForLiro` están rechazados en ambas ([S401](../../docs/capture/s401-a7s-silent-control-path.md), [S174](../../docs/capture/s174-forliro-api.md)).
- **Registro de exposición (E23):** con ShutMode 0 forzado, `r5` cambia la exposición de la foto; el efecto depende de la posición
  vertical y desaparece por encima de ~4200. Es **INFERENCIA** (lectura y reinicio con ritmos distintos), no prueba de obturador electrónico
  ([T035–T039](../../docs/capture/registro-pruebas-camara.md)).
- **Cortinas:** GPIO de cortinillas identificados (P4B–P4E); el enlace con el banco/bit del firmware no consta ([E11](../../docs/PENDIENTES.md)).
- **Recuperación y Darwin:** `darwin_core` controla también la energía del cuerpo y el actualizador USB no está demostrado sin él.
  No hay recuperación demostrada ante un fallo de Darwin; por eso no se autoriza ningún flasheo persistente
  ([E24-01](../../docs/capture/e24-01-arranque-recuperacion.md) a [E24-05a](../../docs/capture/e24-05-upd-y-rearme.md),
  [dictamen](../../docs/capture/e24-04-dictamen-seguridad.md)).
- **Conclusiones rectificadas:** qué se rectificó y con qué informe, en [docs/STATE.md](../../docs/STATE.md#conclusiones-corregidas-no-reusar-versiones-previas)
  y en [docs/CORRECTIONS.md](../../docs/CORRECTIONS.md) (derivado del grafo).

## Subsistemas investigados

Informes de `docs/capture/`, con sus pruebas y evidencia, por tema en **[docs/INDEX.md](../../docs/INDEX.md)**:
[captura](../../docs/INDEX.md#informes-por-subsistema) · sensor e imager · obturador · control y comunicación · procesamiento de imagen ·
otros (AF, estabilización, vídeo, Wi-Fi, audio, lentes, energía) · comparaciones A6000/A7S/A6300 · herramientas y validación.
Catálogo de módulos de trazas: [linea-general-re.md](../../docs/capture/linea-general-re.md).

## Navegación

| Necesito… | Voy a… |
|---|---|
| Contexto mínimo para retomar | [knowledge/CURRENT.md](../../knowledge/CURRENT.md) |
| Conclusiones y límites vigentes | [docs/STATE.md](../../docs/STATE.md) |
| Qué falta (abierto/bloqueado/cerrado) | [docs/PENDIENTES.md](../../docs/PENDIENTES.md) |
| Informes por subsistema | [docs/INDEX.md](../../docs/INDEX.md) |
| Registro de pruebas en cámara | [docs/capture/registro-pruebas-camara.md](../../docs/capture/registro-pruebas-camara.md) |
| Historial cronológico | [knowledge/PROGRESS.md](../../knowledge/PROGRESS.md) |
| Objetivo principal | [projects/electronic-shutter/](../../projects/electronic-shutter/README.md) |
| Versiones íntegras anteriores de README/CURRENT/STATE | [docs/history/](../../docs/history/README-historial-2026-10-26.md), [knowledge/history/](../../knowledge/history/CURRENT-historial-2026-10-26.md) |
| Uso por agentes (Claude Code, Codex) | [docs/agent/README.md](../../docs/agent/README.md), [AGENTS.md](../../AGENTS.md), [CLAUDE.md](../../CLAUDE.md) |

## Estructura del repositorio

| Ruta | Contenido |
|---|---|
| `docs/` | Estado, pendientes, índice, correcciones e informes (`docs/capture/`) |
| `knowledge/` | Resumen operativo (`CURRENT.md`), historial (`PROGRESS.md`) y backlogs de agentes |
| `analysis/` | Evidencia por sesión (`sNNN*/`), censo S178 y volcados de cámara (`camera-dumps/`, no versionados) |
| `scripts/` | Herramientas: volcado de NVRAM y estado de cámara (`senser_*`, `camera_*`), REA, índice de conocimiento (`knowledge/`), auditoría (`audit/`) |
| `tests/` | Verificadores `test_sNNN_*.py` de cada informe; los que necesitan firmware no versionado se omiten |
| `projects/electronic-shutter/` | Subproyecto del obturador electrónico |
| `site/` | Página de estado y badges publicados en GitHub Pages |

## Reproducir análisis y pruebas

```bash
source .venv/bin/activate
python3 scripts/knowledge/search.py text "concepto"       # buscar sin releer el repo
python3 scripts/knowledge/search.py exact "0x90b248"      # dirección o símbolo
python -m pytest tests -q                                 # pruebas; sin firmware, las que lo necesitan se omiten
python3 scripts/audit/repo_audit.py                       # auditoría mecánica: enlaces, pendientes, cifras
python3 scripts/knowledge/build_subsystem_index.py        # regenera docs/INDEX.md
```

Dependencias de CI: `knowledge/requirements-ci.txt`, más `pyelftools` y `numpy`. Cada informe `docs/capture/sNNN-*.md` tiene su evidencia
en `analysis/sNNN*/` y su verificador en `tests/test_sNNN_*.py`.

## Seguridad y contribución

- Toda prueba en cámara requiere autorización expresa del usuario para ese caso y backup NVRAM previo; el protocolo está en
  [registro-pruebas-camara.md](../../docs/capture/registro-pruebas-camara.md).
- No se suben firmware, `*.bin`/`*.elf`, volcados ni binarios de Sony; commits convencionales y por ruta.
- Toda tarea que se haga, descarte o reabra actualiza [docs/PENDIENTES.md](../../docs/PENDIENTES.md) en el mismo commit. El README solo
  cambia cuando cambia el estado global; las sesiones se documentan en su informe, en PENDIENTES, en STATE si cambia una
  conclusión y en PROGRESS.
