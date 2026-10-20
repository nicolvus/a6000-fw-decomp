# Registro de instalación S52

- 19-10-2026: `python3 -m venv ~/.venvs/re && ~/.venvs/re/bin/pip install capstone unicorn keystone-engine lief` (PyPI). Motivo: emulación offline (Unicorn) de ramas ShutMode y desensamblado scriptable. Verificado por import.
- 19-10-2026: `session_daemon.py`: límite RSS del watchdog configurable por `REA_DAEMON_RSS_MAX_MB` (sin cambiar el valor por defecto). RAM del sistema: 15 GiB, ~7 GiB libres al inicio; dos sesiones REA `av-cam` (~2,3–3 GB cada una) caben de forma concurrente.

# Registro de instalación S53

- 19-10-2026: `pip install --user --break-system-packages capstone` (5.0.x, `~/.local`). Motivo: scripts `analysis/s53/*.py` con el Python del sistema. Redundante con `~/.venvs/re` (ya tenía capstone); se conserva. `sudo pacman` no disponible sin contraseña.
- 19-10-2026: Ghidra 12.1.4 headless usado directamente (`tools/providers/.../analyzeHeadless`, JDK 21 de `tools/providers`), sin límite de memoria adicional; tres proyectos nuevos `analysis/s53/ghidra/s53-*-darwin` (~5 MB c/u, ~2 min en total).
