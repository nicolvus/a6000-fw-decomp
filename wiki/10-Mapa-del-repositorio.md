# 10. Mapa del repositorio e investigación

| Ruta | Contenido |
|---|---|
| `scripts/replicar/` | Genera los núcleos de Darwin parcheados a partir del firmware oficial |
| `scripts/e25_05/` | Construcción y verificación de los paquetes 3.23/3.24 |
| `scripts/camera_*.py`, `camera_silent.py` | Control de cámara por telnet/ADB y capa 2 |
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
