# Registro de instalación S52

- 19-10-2026: `python3 -m venv ~/.venvs/re && ~/.venvs/re/bin/pip install capstone unicorn keystone-engine lief` (PyPI). Motivo: emulación offline (Unicorn) de ramas ShutMode y desensamblado scriptable. Verificado por import.
- 19-10-2026: `session_daemon.py`: límite RSS del watchdog configurable por `REA_DAEMON_RSS_MAX_MB` (sin cambiar el valor por defecto). RAM del sistema: 15 GiB, ~7 GiB libres al inicio; dos sesiones REA `av-cam` (~2,3–3 GB cada una) caben de forma concurrente.

# Registro de instalación S53

- 19-10-2026: `pip install --user --break-system-packages capstone` (5.0.x, `~/.local`). Motivo: scripts `analysis/s53/*.py` con el Python del sistema. Redundante con `~/.venvs/re` (ya tenía capstone); se conserva. `sudo pacman` no disponible sin contraseña.
- 19-10-2026: Ghidra 12.1.4 headless usado directamente (`tools/providers/.../analyzeHeadless`, JDK 21 de `tools/providers`), sin límite de memoria adicional; tres proyectos nuevos `analysis/s53/ghidra/s53-*-darwin` (~5 MB c/u, ~2 min en total).

# Registro de instalación S62 (20-10-2026) — máquina nueva (CachyOS, 13 GiB RAM)

Objetivo: dejar el entorno del repo `nicolvus/a6000-fw-decomp` operativo para continuar (REA primero),
con los mismos requisitos que la máquina anterior. Todo el contenido del repo ya estaba presente
(firmware extraído 4,6 GB, proyectos Ghidra históricos, `tools/rea/node_modules`, `.venv/` del repo).

## Paquetes Python

- `python3 -m venv ~/.venvs/re && ~/.venvs/re/bin/pip install capstone==5.0.7 unicorn==2.1.4 keystone-engine lief==1.0.0`
  → import OK en los cuatro módulos (emulación Unicorn + desensamblado Capstone + parcheo Keystone).
- `pip install --target ~/.local/lib/python3.14/site-packages capstone==5.0.7` → Python del sistema con
  capstone (el `python3` de CachyOS no trae `pip` ni `ensurepip` utilizable; `--target` reproduce
  `pip install --user`). Nota: el paso de S53 con `pip install --user --break-system-packages` ya no es
  reproducible en esta máquina; el resultado es el mismo.
- `.venv/bin/pip install capstone==5.0.7 unicorn==2.1.4 keystone-engine lief==1.0.0` → el `.venv/` del repo
  (el que usa el servidor MCP de conocimiento) necesita las mismas librerías porque `pytest tests/`
  importa Capstone/Unicorn en 10 módulos de test.

## Sistema (sudo)

- `pacman -S --needed --noconfirm npm` → npm 12.2.1 (Node 26.11.1 ya estaba). Necesario para
  reinstalar `tools/rea/node_modules` si se pierde (`npm ci` en `tools/rea`).
- `npm install -g @openai/codex@0.162.1` → Codex CLI 0.162.1, la versión registrada en
  `environment/dependencies.json` (no estaba en esta máquina).

## Reparación de REA (no era un problema de versión)

`tools/rea/node_modules/.bin/rea` y `.../rea-agents` eran **copias** de `rea-agents/scripts/rea.mjs`,
no enlaces simbólicos: el `import("../package.json")` del script resolvía a
`tools/rea/node_modules/package.json` (inexistente) y REA moría con `ERR_MODULE_NOT_FOUND`.
Corregido con enlaces simbólicos a `../rea-agents/scripts/rea.mjs` (igual que hace npm):
`ln -sfn ../rea-agents/scripts/rea.mjs node_modules/.bin/rea`. Verificado: `scripts/rea --help` y
`scripts/rea doctor` → Ghidra 12.1.4 + JDK 21.0.12.1 OK (solo faltan Hopper/IDA, no usados).

## Skills y MCP

- `.agents/skills/{contradiction-audit,knowledge-maintenance,knowledge-navigation,session-checkpoint}`
  estaban borrados en el checkout (son enlaces simbólicos a `.claude/skills/*`): restaurados con
  `git checkout -- .agents/skills`.
- `scripts/rea setup --client opencode --yes` → registra el servidor `rea` en
  `~/.config/opencode/opencode.json` e instala la skill de REA en `~/.agents/skills/reverse-engineer-anything`.
- `~/.config/opencode/opencode.json`: se sustituyó el comando por el wrapper canónico del proyecto
  (`scripts/rea mcp`) y se añadió el servidor `sony-a6000-knowledge`, igual que en `../.mcp.json`.
- `~/.codex/config.toml` (no existía): creado con `[mcp_servers.rea]` y `[mcp_servers.sony-a6000-knowledge]`
  (mismos comandos) + `trust_level` del proyecto. Verificado con `codex mcp list` → 2 servidores `enabled`.

## Verificación funcional

- Suite completa: `pytest tests/ -q` → **292 passed, 39 subtests** (antes 290 passed + 2 failed).
- Fallo corregido: `tests/test_s61_imx210.py` fallaba en la suite completa (no en aislamiento) porque
  `analysis/s61/xr.py` y `analysis/s56/xr.py` comparten nombre de módulo: pytest importa todos los
  módulos de test antes de ejecutar ninguno, `sys.modules['xr']` quedaba con el de S56 y `import xr`
  devolvía la API sin `callers`. Ahora S61 carga su módulo por ruta con nombre propio (`xr_s61`);
  las aserciones no cambian.
- MCP REA: `open_binary` + `binary_overview` + `close_binary` sobre `libmprctrl.so` (ELF ARM) →
  Ghidra 12.1.4 como proveedor, `image_base 0x10000`, sin limitaciones bloqueantes.
- MCP de conocimiento: `initialize`/`tools/list` correctos (11 herramientas) e índice al día
  (`check_index_freshness` → "Índice al día").

## Cómo reabrir la sesión REA de `av-cam.bin` (~8 min en frío)

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
python3 analysis/rea-independent/bin/session_daemon.py analysis/rea-independent/run/rea.sock \
  '{"path": "/home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter/analysis/rea-independent/input/av-cam.bin", "format": "raw-binary", "architecture": "arm", "entry_point": "0x43541000", "provider_id": "ghidra"}' \
  > analysis/rea-independent/run/rea-daemon.log 2>&1 &
# listo cuando exista analysis/rea-independent/run/rea.sock.ready
python3 analysis/rea-independent/bin/q.py analysis/rea-independent/run/rea.sock guion.json salida.jsonl
# cierre: q.py <sock> --shutdown
```

# Límite de memoria de Ghidra = 2 GB (20-10-2026, indicación del usuario)

Motivo: durante S62 convivieron varias instancias de Ghidra (demonio REA + MCP `rea` + subagentes) y
la máquina (13 GiB) sufría presión de memoria: el watchdog del demonio (`REA_DAEMON_RSS_MAX_MB=3800`)
mataba la sesión y el proceso `opencode` caía (reinicios del servidor observados durante el hito).

Cambios:
- `GHIDRA_MAXMEM=2G` en `~/.config/opencode/opencode.json`, `~/.codex/config.toml` y `../.mcp.json`
  (Claude Code) — antes `3G`/`2560m`.
- `analysis/rea-independent/bin/session_daemon.py`: `GHIDRA_MAXMEM` por defecto `2G` y
  `REA_DAEMON_RSS_MAX_MB` por defecto `2600` (antes `3G`/`3800`).
- `docs/STATE.md` (política REA) actualizado al nuevo valor.

Para ampliar: `GHIDRA_MAXMEM=5G REA_DAEMON_RSS_MAX_MB=6000` en el entorno del demonio.
