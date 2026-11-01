# 10. Mapa del repositorio e investigación

| Ruta | Contenido |
|---|---|
| `wiki/` | Fuente de esta wiki (un workflow la publica en cada cambio) |
| `site/` | Tablero de GitHub Pages (`scripts/build_pages_status.py`) |
| `projects/electronic-shutter/` | Subproyecto del obturador electrónico |
| `scripts/replicar/` | Genera los núcleos de Darwin parcheados a partir del firmware oficial |
| `scripts/e25_05/` | Construcción y verificación de los paquetes 3.23/3.24 |
| `scripts/e25_27/` | Construcción y verificación del 3.25c |
| `scripts/camera_*.py` | Control de cámara por telnet/ADB y capa 2 |
| `scripts/senser_backup_dump.py` | Backup de NVRAM (solo lectura) |
| `tools/remote-shutter/` | App RemoteShutter |
| `references/` | pmca, fwtool y Tweak (vendorizados), manuales |
| `docs/` | Estado (`STATE.md`), pendientes (`PENDIENTES.md`), informes (`docs/capture/`) |
| `knowledge/` | Resumen operativo (`CURRENT.md`) e historial |
| `analysis/` | Evidencia por sesión (volcados de cámara: solo README, SHA256SUMS y JSON) |
| `tests/` | Verificadores; los que necesitan firmware se omiten en CI |

## Reproducir y verificar

```sh
source .venv/bin/activate
CI=1 python -m pytest tests -q                       # suite sin firmware (como en GitHub Actions)
python3 scripts/audit/repo_audit.py                   # enlaces, rutas citadas, cifras y SHA-256
python3 scripts/knowledge/search.py text "concepto"  # buscar sin releer el repositorio
```

## Ingeniería inversa

- REA (MCP) y Ghidra histórico (`silent-liro.gpr`, solo lectura). `av-cam.bin` tarda ≈ 8 min en frío: reutiliza una sola sesión (`docs/agent/bootstrap-desde-cero.md` §4).
- Por dónde empezar: `knowledge/CURRENT.md` → `docs/STATE.md` → `docs/PENDIENTES.md`.
- Tablero de progreso: <https://nicolvus.github.io/a6000-fw-decomp/progress/>.

## Navegación

| Necesito… | Voy a… |
|---|---|
| Contexto mínimo para retomar | [knowledge/CURRENT.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/knowledge/CURRENT.md) |
| Conclusiones y límites vigentes | [docs/STATE.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/STATE.md) |
| Qué falta (única lista) | [docs/PENDIENTES.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/PENDIENTES.md) |
| Incidente 3.25 y recuperación | [docs/capture/e26-recovery.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/e26-recovery.md) |
| Informes por subsistema | [docs/INDEX.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/INDEX.md) |
| Registro de pruebas en cámara | [docs/capture/registro-pruebas-camara.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/registro-pruebas-camara.md) |
| Historial cronológico | [knowledge/PROGRESS.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/knowledge/PROGRESS.md) |
| Tablero de progreso | <https://nicolvus.github.io/a6000-fw-decomp/progress/> |
| Uso por agentes | [docs/agent/README.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/agent/README.md), [AGENTS.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/AGENTS.md), [CLAUDE.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/CLAUDE.md) |


## Seguridad y contribución

- El código del repositorio no sube firmware de Sony, `*.bin`/`*.elf`, RAW ni datos personales (el número de serie, el
  correo personal y `libmprctrl.so` se borraron del historial el 31-10-2026; ver R7 en PENDIENTES). Los paquetes `.dat`
  listos para flashear se publican aparte, como GitHub Releases ([`fw-3.23-3.24`](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.23-3.24),
  [`fw-3.25c-experimental`](https://github.com/nicolvus/a6000-fw-decomp/releases/tag/fw-3.25c-experimental); no en el árbol de git), con su nota de copyright. Commits convencionales.
- Toda prueba en cámara lleva backup NVRAM previo y se anota en el registro; toda tarea actualiza [PENDIENTES](https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/PENDIENTES.md) en el mismo commit.

Cómo contribuir: [CONTRIBUTING.md](https://github.com/nicolvus/a6000-fw-decomp/blob/main/CONTRIBUTING.md).
