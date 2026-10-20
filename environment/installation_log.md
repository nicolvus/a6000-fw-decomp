# Registro de instalación S52

- 19-10-2026: `python3 -m venv ~/.venvs/re && ~/.venvs/re/bin/pip install capstone unicorn keystone-engine lief` (PyPI). Motivo: emulación offline (Unicorn) de ramas ShutMode y desensamblado scriptable. Verificado por import.
- 19-10-2026: `session_daemon.py`: límite RSS del watchdog configurable por `REA_DAEMON_RSS_MAX_MB` (sin cambiar el valor por defecto). RAM del sistema: 15 GiB, ~7 GiB libres al inicio; dos sesiones REA `av-cam` (~2,3–3 GB cada una) caben de forma concurrente.
