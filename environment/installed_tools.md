# Herramientas instaladas/modificadas (actualizado 20-10-2026)

| Herramienta | Versión | Ubicación | Verificación |
|---|---|---|---|
| capstone | 5.0.7 | venv persistente `~/.venvs/re` | `~/.venvs/re/bin/python -c "import capstone"` OK |
| unicorn | 2.1.4 | `~/.venvs/re` | import OK |
| keystone-engine | 0.9.2 (pip) | `~/.venvs/re` | import OK |
| lief | 1.0.0 | `~/.venvs/re` | import OK |
| capstone | 5.0.7 | `~/.local/lib/python3.14/site-packages` (python del sistema) | `python3 -c "import capstone"` OK |
| capstone/unicorn/keystone-engine/lief | ídem | `.venv/` del repo (para `pytest` del proyecto) | suite completa 292 OK |
| REA | 6.5.0 | `tools/rea/node_modules/rea-agents` (wrapper `scripts/rea`) | `scripts/rea doctor` → Ghidra OK |
| Ghidra | 12.1.4 | `tools/providers/ghidra_12.1.4_PUBLIC` (con `GHIDRA_INSTALL_DIR`) | `rea doctor`: headless/native decompiler/java OK |
| JDK | 21.0.12.1 | `tools/providers/jdk-21.0.12.1+1` (con `JAVA_HOME`) | `rea doctor`: java OK |
| Node | 26.11.1 | `/usr/bin/node` | `node --version` |
| npm | 12.2.1 | `/usr/bin/npm` (pacman) | `npm --version`; `npm ls` en `tools/rea` → `rea-agents@6.5.0` |
| Codex CLI | 0.162.1 | `/usr/bin/codex` (npm global) | `codex --version`; `codex mcp list` → 2 servidores |
| LLVM `llvm-objdump` | — | `/usr/bin/llvm-objdump` | presente |
| Python | 3.14.8 | `/usr/bin/python3` | `python3 --version` |

Ya presentes y sin reinstalar (20-10-2026): REA 6.5.0 (`scripts/rea`), LLVM `llvm-objdump`, Python 3.14, Codex CLI 0.162.1.
No instalados (no necesarios hasta ahora): angr, rizin/radare2, Ghidra headless independiente (REA lo embebe),
Hopper/IDA (proveedores opcionales de REA; no usados por el proyecto).

## Servidores MCP registrados (20-10-2026)

| Cliente | Archivo | Servidores |
|---|---|---|
| OpenCode | `~/.config/opencode/opencode.json` | `rea` (vía `scripts/rea mcp`), `sony-a6000-knowledge` |
| Codex CLI | `~/.codex/config.toml` | `[mcp_servers.rea]`, `[mcp_servers.sony-a6000-knowledge]` |
| Claude Code | `../.mcp.json` (ya existía) | `rea`, `sony-a6000-knowledge` |

Todos apuntan al mismo par de comandos del proyecto, de modo que REA y el índice de conocimiento son
intercambiables entre agentes. Skill de REA instalada en `~/.agents/skills/reverse-engineer-anything`
(vía `scripts/rea setup --client opencode --yes`).

## Cambios de configuración

- `analysis/rea-independent/bin/session_daemon.py` acepta `REA_DAEMON_RSS_MAX_MB`
  (por defecto **2600**, coherente con `GHIDRA_MAXMEM=2G`); `REA_GHIDRA_STARTUP_TIMEOUT_MS`
  (900 000 ms) y `GHIDRA_MAXMEM` (**2G**) ya eran ampliables por entorno.
- **Límite de memoria de Ghidra = 2 GB** (20-10-2026, por indicación del usuario): `GHIDRA_MAXMEM=2G`
  en `~/.config/opencode/opencode.json`, `~/.codex/config.toml`, `../.mcp.json` (Claude Code) y como
  valor por defecto del demonio. Motivo: con 3G y varias instancias de Ghidra simultáneas la máquina
  (13 GiB) sufría OOM y el servidor (opencode/REA) caía; 2G mantiene el análisis de `av-cam.bin`
  (~42 000 procedimientos) dentro del presupuesto y deja margen para el resto. Para más RAM:
  `GHIDRA_MAXMEM=5G REA_DAEMON_RSS_MAX_MB=6000`.
- `tools/rea/node_modules/.bin/rea` y `.../rea-agents` restaurados como **enlaces simbólicos** a
  `../rea-agents/scripts/rea.mjs` (npm los crea así; si son copias, el `import "../package.json"` del
  script resuelve a `node_modules/package.json` y REA no arranca con `ERR_MODULE_NOT_FOUND`).
- RAM del sistema: 13 GiB (~5 GiB libres con la sesión abierta); una sesión REA `av-cam` consume ~2,3–3 GB.
