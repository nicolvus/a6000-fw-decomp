# Herramientas instaladas/modificadas (S52, 19-10-2026)

| Herramienta | Versión | Ubicación | Verificación |
|---|---|---|---|
| capstone | 5.0.7 | venv persistente `~/.venvs/re` | `~/.venvs/re/bin/python -c "import capstone"` OK |
| unicorn | 2.1.4 | `~/.venvs/re` | import OK |
| keystone-engine | (pip) | `~/.venvs/re` | import OK |
| lief | 1.0.0 | `~/.venvs/re` | import OK |

Ya presentes y sin reinstalar: REA 6.5.0 (`scripts/rea`), LLVM `llvm-objdump` (`/usr/bin`), Python 3.14, Codex CLI 0.162.1.
No instalados (no necesarios hasta ahora): angr, rizin/radare2, Ghidra headless independiente (REA lo embebe).
Cambio de configuración: `analysis/rea-independent/bin/session_daemon.py` acepta `REA_DAEMON_RSS_MAX_MB`
(por defecto 3800, igual que antes); `REA_GHIDRA_STARTUP_TIMEOUT_MS`/`GHIDRA_MAXMEM` ya eran ampliables por entorno.
