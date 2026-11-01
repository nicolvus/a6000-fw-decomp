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
> modificado puede dejar la cámara inservible y **no hay recuperación independiente demostrada**. Lee [Límites y riesgos](#límites-y-riesgos).

## Estado técnico actual

| Aspecto | Estado (31-10-2026) |
|---|---|
| Cámara | **Bloqueada** tras instalar el 3.25 (actualizador al 100 % y Done; testimonio del usuario, sin captura UART ni lectura de NAND) |
| Causa | **Identificada offline** ([R36](docs/capture/e26-r36-causa-fallo-325.md)): el `nflasha3` recomprimido del 3.25 no respeta el formato que lee el descompresor por hardware (359/369 bloques empiezan a mitad de sector y Loader3 no transmite ese desplazamiento; 3 bloques son un solo registro de 64 KiB en vez de 16 de 4 KiB). La primera lectura de la partición falla y Loader3 da −302 (3 lentos + 2 rápidos). El 3.23 no tocaba `nflasha3`. Falta la confirmación física (vídeo del LED; la UART está silenciada, R37) |
| Recuperación | Solo hay que restaurar `nflasha3` y existe copia válida ([R30](docs/capture/e26-r30-updater-done-boundary.md)). La vía serie del BootROM se abre en cada arranque pero exige una clave guardada en `nflasha0`, nunca volcada ([R32](docs/capture/e26-r32-moderreg-valor-real.md), [R33](docs/capture/e26-r33-veracidad-clave-nflasha0.md)). Mínimo físico identificado ([R37](docs/capture/e26-r37-cierre-estatico-recuperacion.md)): un archivo vacío `\updater\mode` en `nflasha2` hace que Loader3 arranque el actualizador de fábrica de `nflasha1` (intacto) y acepte firmware por USB; el paquete **3.26** (contenido oficial) ya está preparado. En el último volcado de `nflasha2` basta **1 byte lógico** (recuperar una entrada `MODE` borrada, [R38](docs/capture/e26-r38-guard-y-entrada-updater.md)), y el guard del actualizador acepta el 3.26. Ese byte no se puede reprogramar en su sitio con un lector externo (MuMin + ECC, [R39](docs/capture/e26-r39-estatico-profundo.md)): hace falta escribir desde el propio BIONZ. No está autorizado |
| Obturador silencioso | Logrado con el 3.23 (T040, confirmado por el usuario); exposición por filas medida en el RAW ([E25-10](docs/capture/e25-10-exposicion-por-fila.md)) |
| Selector EFCS / Electronic (3.25) | Implementado y verificado **solo offline** (emulación); nunca validado en la cámara ([E25-24b](docs/capture/e25-24b-implementacion-selector.md), [E25-27](docs/capture/e25-27-construccion-firmware-integrado.md)) |
| Verificación | 4 427 pruebas en local (las que leen firmware se omiten en CI); censo de etiquetas 133/372; 291 sesiones S + 74 informes de fase E; 12/24 planes físicos con prueba; registro T001–T056 |

**Último cierre:** E26 R40 (31-10-2026) — JTAG/SWD del BIONZ analizado como alternativa a escribir la NAND con lector externo: ningún
cargador bloquea el DAP CoreSight y el chip trae `defconfig` de fábrica para arrancar bajo depurador, pero sigue siendo físico
(falta población de R4911/R4912 y el eFuse de seguridad). Detalle por informe en [knowledge/CURRENT.md](knowledge/CURRENT.md).

## Wiki: replicarlo de principio a fin

La guía paso a paso vive en la **[Wiki CFW Sony a6000](https://github.com/nicolvus/a6000-fw-decomp/wiki)** (fuente versionada en [`wiki/`](wiki/Home.md)):

| Paso | Página |
|---|---|
| Qué necesitas y qué puede salir mal | [Requisitos y riesgos](wiki/1-Requisitos-y-riesgos.md) |
| Repositorio, entorno y firmware oficial 3.21 | [Entorno y firmware oficial](wiki/2-Entorno-y-firmware-oficial.md) |
| Copia de seguridad de la NVRAM | [Backup de NVRAM](wiki/3-Backup-de-NVRAM.md) |
| Construir y verificar los `.dat` 3.23 y 3.24 | [Construir los paquetes](wiki/4-Construir-los-paquetes.md) |
| Flashear el 3.23 | [Instalar el 3.23](wiki/5-Instalar-el-3.23.md) |
| Exposición uniforme por filas (RAM) | [Capa 2](wiki/6-Capa-2-exposicion-uniforme.md) |
| Si algo falla | [Volver atrás y recuperación](wiki/7-Volver-atras-y-recuperacion.md) |
| Scripts y apps con su uso | [Herramientas](wiki/12-Herramientas.md) |
| Fundamentos y resultados | [Cómo funciona](wiki/8-Como-funciona-el-parche.md) · [Resultados y límites](wiki/9-Resultados-y-limites.md) |

Los dos paquetes ya construidos están en el [release `fw-3.23-3.24`](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.23-3.24)
(hashes `4c21353d…` y `e1345aff…`); construirlos tú desde el firmware oficial da exactamente los mismos. La versión anterior de este README,
con el detalle del parche, el incidente del 3.25 y las mediciones, está en la wiki y en los informes de `docs/capture/`.

## Límites y riesgos

- **Sin recuperación independiente** ([E24-04](docs/capture/e24-04-dictamen-seguridad.md), [E25-04](docs/capture/e25-04-recuperabilidad-y-decision.md)): Darwin también controla la energía. El caso real es el 3.25.
- **Lo offline no garantiza el arranque:** el 3.25 pasó todas las comprobaciones offline y bloqueó la cámara ([R36](docs/capture/e26-r36-causa-fallo-325.md)).
- **Escenarios sin medir con el 3.23:** operación 5 de Darwin (P40/P41=3) y P4B/P4C siguen activos; su efecto físico no se midió.
- **Respaldo:** la copia externa del respaldo (R1) sigue sin verificar.

## Navegación

| Necesito… | Voy a… |
|---|---|
| Contexto mínimo para retomar | [knowledge/CURRENT.md](knowledge/CURRENT.md) |
| Conclusiones y límites vigentes | [docs/STATE.md](docs/STATE.md) |
| Qué falta (única lista) | [docs/PENDIENTES.md](docs/PENDIENTES.md) |
| Incidente 3.25 y recuperación | [docs/capture/e26-recovery.md](docs/capture/e26-recovery.md) |
| Informes por subsistema | [docs/INDEX.md](docs/INDEX.md) |
| Registro de pruebas en cámara | [docs/capture/registro-pruebas-camara.md](docs/capture/registro-pruebas-camara.md) |
| Historial cronológico | [knowledge/PROGRESS.md](knowledge/PROGRESS.md) |
| Tablero de progreso | <https://nicolvus.github.io/a6000-fw-decomp/progress/> |
| Guía de réplica (wiki; punto de entrada para replicar) | [wiki/Home.md](wiki/Home.md) |
| Uso por agentes | [docs/agent/README.md](docs/agent/README.md), [AGENTS.md](AGENTS.md), [CLAUDE.md](CLAUDE.md) |

## Estructura

| Ruta | Contenido |
|---|---|
| `wiki/` | Guía de réplica de principio a fin (fuente de la wiki de GitHub) |
| `docs/` | Estado, pendientes, índice, correcciones e informes (`docs/capture/`) |
| `knowledge/` | Resumen operativo (`CURRENT.md`), historial (`PROGRESS.md`) y auditoría (`audit/`) |
| `analysis/` | Evidencia por sesión; de los volcados de cámara solo se versionan README, `SHA256SUMS`, registros, JSON y JPEG reducidos |
| `scripts/` | Volcados, estado de cámara, recuperación (`recovery/`), empaquetado, auditoría, REA y conocimiento |
| `tests/` | Verificadores por informe; los que necesitan firmware o el manual de servicio se omiten en CI |
| `projects/electronic-shutter/` | Subproyecto del obturador electrónico |
| `site/` | Tablero de GitHub Pages (generado por `scripts/build_pages_status.py`) |

## Reproducir y verificar

```bash
source .venv/bin/activate
CI=1 python -m pytest tests -q                       # suite sin firmware (como en GitHub Actions)
python3 scripts/audit/repo_audit.py                   # enlaces, rutas citadas, cifras y SHA-256 de volcados
python3 scripts/knowledge/search.py text "concepto"  # buscar sin releer el repositorio
```

## Copyright y uso

**Copyright.** Los dos `.dat` del [release `fw-3.23-3.24`](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.23-3.24) son el
firmware oficial de Sony 3.21 con una modificación binaria mínima y documentada en `darwin_core.bin` (2–9 bytes; ver
[Cómo funciona el parche del 3.23](#cómo-funciona-el-parche-del-323) y [E25-05](docs/capture/e25-05-preparacion-paquetes-323-324.md)).
El firmware original es © Sony Corporation, que conserva todos los derechos sobre él. El autor **no tiene ninguna licencia de Sony**
sobre ese firmware y este repositorio no reclama titularidad sobre él. Que el proyecto sea abierto no cambia eso: la apertura
alcanza solo a lo que el autor escribió (scripts, análisis, documentación), no a la parte de Sony contenida en los `.dat`.
Se publican con fines de investigación e interoperabilidad (ingeniería inversa para modificar el comportamiento del hardware que el
autor posee), sin incluir código fuente de Sony. Esta nota documenta la postura del autor, no es una garantía legal, y los
archivos se retirarán si Sony lo solicita.

**Uso.**
- Todo se ofrece «tal cual», sin garantía de ningún tipo; usarlo es bajo tu propio riesgo y puede inutilizar la cámara (ver [Límites y riesgos](#límites-y-riesgos)).
- Pensado para investigación, aprendizaje y uso personal en una cámara de tu propiedad. No lo uses para eludir protecciones con fines ilícitos ni para redistribuir firmware de Sony por tu cuenta.
- El código, los scripts, el análisis y la documentación del autor se publican bajo licencia [MIT](LICENSE). Esa licencia **no** cubre el firmware de Sony ni los `.dat` del release, ni el material de terceros de abajo.

**Material de Sony y de terceros que usa el proyecto**
- **Código fuente publicado por Sony** para esta cámara (Linux y demás paquetes de código abierto). Se usa para entender el arranque, los controladores y la consola de Loader2/Loader3. Conserva su licencia original (GPL y otras); las copias extraídas están en `analysis/session18/`.
- **Manual de servicio de nivel 3** de la ILCE-6000/6000L/6000Y (Rev. 1.1), de acceso público en la web. Se usa como fuente de esquemas eléctricos y de hojas de la placa. El PDF **no** se versiona (está en `.gitignore`); en `references/manuals/` solo hay el manifiesto con su hash y origen y unas pocas páginas de ejemplo.
- **Firmware oficial 3.21**: lo descarga cada persona desde el servidor de Sony con `scripts/agent/bootstrap.sh`; no se incluye en el repositorio.
- **Herramientas de terceros** con su propia licencia: [Sony-PMCA-RE](https://github.com/ma1co/Sony-PMCA-RE), [fwtool.py](https://github.com/ma1co/fwtool.py) y [OpenMemories-Tweak](https://github.com/ma1co/OpenMemories-Tweak) en `references/`.

## Seguridad y contribución

- El código del repositorio no sube firmware de Sony, `*.bin`/`*.elf`, RAW ni datos personales (el número de serie, el
  correo personal y `libmprctrl.so` se borraron del historial el 31-10-2026; ver R7 en PENDIENTES). Los dos paquetes `.dat`
  listos para flashear se publican aparte, como [GitHub Release](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.23-3.24)
  (no en el árbol de git), con su nota de copyright. Commits convencionales.
- Toda prueba en cámara lleva backup NVRAM previo y se anota en el registro; toda tarea actualiza [PENDIENTES](docs/PENDIENTES.md) en el mismo commit.
