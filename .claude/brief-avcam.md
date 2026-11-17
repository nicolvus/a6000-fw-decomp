# Brief común para subagentes de integración av-cam en el arnés (G22-E)

Repo: /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter. Responde en español.

## Antes de empezar
- Lee CLAUDE.md del repo y del directorio padre. `knowledge/CURRENT.md` y `docs/PENDIENTES.md` son grandes: usa grep/head.
- Informe vivo de la integración: `docs/gui/g22-avcam-puente.md` (§5.x, una sección por sesión; lee solo las secciones que te cite el encargo, localizadas con `grep -n "^### 5\."`). Guía de uso del arnés: `docs/gui/g22-emulador-uso.md`. Código: `scripts/gui/harness/` (shim `sonyshim.c`, `live.py`, `im.sh`), `scripts/gui/avcam/` (puente, mensajes, ae).
- MCP `sony-a6000-knowledge` antes de investigar a mano. Firmware: REA primero (daemon `analysis/rea-independent/bin/session_daemon.py` + `q.py`; ver /home/nicolas/.claude/projects/-home-nicolas-Documents-a6000/memory/reference-rea-daemon-uso.md); capstone/bytes para lo decisivo. Ghidra solo de respaldo.

## Reglas que no puedes romper
- **Emulación fiel**: el arnés solo puede simular el dato verificado que cambia en la cámara real (decompilación, volcados reales, docs del repo). Nada de inventar eventos, recuentos ni valores; lo no verificable queda NO_VERIFICADO y sin modelar. Los atajos opt-in de diagnóstico se permiten si quedan apagados por defecto y documentados.
- Sin cámara, sin flasheo, sin construir CFW. Solo offline + arnés.
- Puedes editar `scripts/gui/harness/` y `scripts/gui/avcam/` (esta línea de trabajo es la dueña del arnés), salvo `scripts/gui/harness/android/` (cambios ajenos sin commit: no tocar). Mantén o amplía los tests (`tests/test_live_shimenv.py`, `tests/test_avcam_puente.py`, etc.) y córrelos.
- Perfiles de VM en `analysis/gui/g22/harness/live/` con prefijo propio de tu tarea; cierra cada VM al acabar (`POST /salir`, PID comprobado muerto). No mates procesos ajenos.
- Git: nunca `stash`, `reset`, `checkout --`, `clean`, ni `add -A`/`add .`. `git add` solo de rutas tuyas. Commit Conventional Commits terminado en `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Después `gh auth switch -u nicolvus`, `gh auth status`, `git push origin main` (si el remoto avanzó: `git pull --rebase` sin autostash solo si no hay conflicto con cambios ajenos; si no, deja el commit local y dilo).
- Documentación: nueva sección §5.NN siguiente en `docs/gui/g22-avcam-puente.md` (título con fecha y MEDIDO/estático); actualiza la fila `G22-E` de `docs/PENDIENTES.md` (añade al final, conciso) y una línea en el registro de fechas del final; `knowledge/CURRENT.md` solo si cambia el contexto mínimo; corre `scripts/knowledge/build_subsystem_index.py` y la reindexación de knowledge-maintenance. No toques README.md.
- Silencio entre herramientas. Ahorra contexto: filtra con head/grep/tail, nada de cat de ficheros grandes.
- Esperas: antes de esperar a un proceso (VM, demonio REA) comprueba en el primer minuto que está vivo (`pgrep`, log); toda espera lleva timeout ≤ 15 min. Para trazas del shim hace falta `WLALL=1` en `SHIMEXTRA` (§5.51). Al terminar, comprueba que no queda ninguna VM tuya (`pgrep -af qemu-system`, perfil propio). No dejes REA abierto con más de una VM tuya a la vez.
- No te detengas en dudas: decide con criterio y sigue. Si la vía principal se agota, prueba otra antes de entregar «parcial».

## Entrega (mensaje final, ≤ 15 líneas)
Resultado (cerrado / parcial), evidencia medida clave (perfil, trazas, captura PNG si aplica), cambios de código y tests, hash del commit y si hubo push, siguiente bloqueo concreto con hipótesis y dónde mirar.
