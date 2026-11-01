# Contribuir

Gracias por querer ayudar. Este proyecto es ingeniería inversa del firmware de la Sony A6000; lo primero es no dañar cámaras.

## Antes de empezar

1. Lee la [Wiki CFW Sony a6000](https://github.com/nicolvus/a6000-fw-decomp/wiki) (fuente en [`wiki/`](wiki/Home.md)): requisitos, riesgos y glosario.
2. Entorno: `scripts/agent/bootstrap.sh` (descarga el firmware oficial 3.21 desde Sony; el repositorio **no** contiene firmware de Sony) o, solo para código y tests, `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
3. Contexto mínimo: [`knowledge/CURRENT.md`](knowledge/CURRENT.md) → [`docs/STATE.md`](docs/STATE.md) → [`docs/PENDIENTES.md`](docs/PENDIENTES.md).

## Reglas

- **Nada de pruebas en cámara sin backup de NVRAM**, y ningún flasheo sin autorización expresa del autor para ese caso. Los scripts de cámara usan la IP de la variable `A6000_HOST` (por defecto `192.168.1.29`).
- **No subas material de Sony** (`firmware/`, `*.bin`, `*.elf`, `*.tar.gz`, RAW, números de serie ni datos personales). Están en `.gitignore`.
- Conventional Commits. Un cambio de comportamiento lleva primero el test que falla.
- Tests: `CI=1 python -m pytest tests -q` (los que necesitan firmware se omiten); `ruff` y `mypy` sin avisos nuevos.
- Toda tarea que se haga, descarte o reabra actualiza [`docs/PENDIENTES.md`](docs/PENDIENTES.md) en el mismo cambio; todo pendiente nuevo se añade allí con ID, origen y criterio de cierre.
- Tras editar cualquier `.md` indexado: `python scripts/knowledge/index_docs.py && python scripts/knowledge/build_graph.py && python scripts/knowledge/export_corrections.py` y vuelve a ejecutar los dos primeros (ver la skill `knowledge-maintenance`).
- Los `.md` no son un historial: se editan para que digan la verdad actual; el historial está en Git. No dejes versiones antiguas ni notas de «antes decía».
- Si cambias la wiki, edita `wiki/`; un workflow la publica en la wiki de GitHub al fusionar en `main`.

## Licencia

Tu aportación queda bajo la [licencia MIT](LICENSE) del repositorio, que no cubre el material de Sony (ver [Copyright y uso](README.md#copyright-y-uso)).
