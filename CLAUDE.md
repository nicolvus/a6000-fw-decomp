# Sony A6000 — instrucciones de proyecto (Claude Code)

Silencio estricto durante la ejecución: prohibido emitir comentarios, reflexiones o narraciones intermedias entre herramientas (ej.: "Confirmo que...", "Ahora buscaré...", "Reviso ahora..."). Solo ejecuta y piensa en silencio. Cero gasto de tokens visibles durante la ejecución; comenta únicamente al finalizar por completo la tarea.

Antes de investigar manualmente, usa el sistema de conocimiento en
`scripts/knowledge/` (skills: `knowledge-navigation`, `contradiction-audit`,
`knowledge-maintenance`, `session-checkpoint` en `.claude/skills/`).

Al empezar una sesión: lee `knowledge/CURRENT.md` (resumen operativo breve) antes de
releer el repo, luego los pendientes relevantes de `docs/PENDIENTES.md` y solo los informes
necesarios (índice por subsistema: `docs/INDEX.md`); `knowledge/PROGRESS.md` (historial) solo
si necesitas el detalle de cómo se llegó al estado actual.
Al terminar: informe → PENDIENTES → `docs/STATE.md` (si cambió una conclusión) → `CURRENT.md`
(solo si cambió el contexto mínimo; ≤ ~150 líneas) → `PROGRESS.md` → `scripts/knowledge/build_subsystem_index.py`.
Después de editar cualquier `.md` indexado: corre `knowledge-maintenance`.
Antes de reutilizar un hallazgo: corre `contradiction-audit` (puede estar corregido/superado).

Commits: al terminar cada fase (S54 en adelante) haz SIEMPRE commit local de los cambios propios (Conventional Commits; excluye logs de sesión REA). El README principal solo se toca si cambia el estado global (tabla «Estado técnico actual» o «Último cierre»; nunca un párrafo por sesión Sxx) y haz `git push` a `origin` (GitHub personal nicolvus/a6000-fw-decomp, rama `main`) tras el commit (orden permanente del usuario, 2026-10-20).

Restricciones del proyecto: sin firmware ejecutado, sin cámara, sin flasheo salvo autorización expresa
del usuario para ese caso concreto; `git push` solo según la regla de commits. Detalle completo en `docs/STATE.md`.

Ingeniería inversa del firmware: **REA primero** (MCP `rea`: funciones, xrefs, llamadas, decompilación,
`trace_native_values`) y Ghidra histórico `silent-liro.gpr` (readOnly) como respaldo cuando REA no
reconoce/cubre la función (Thumb sembradas a mano) o para verificar bytes. Una consulta vacía de REA no
prueba ausencia. `av-cam.bin` tarda ~8 min en frío: reutiliza/abre UNA sesión con
`analysis/rea-independent/bin/session_daemon.py` + `q.py`, consulta por lotes y ciérrala al acabar el hito.
REA y Ghidra comparten motor; verifica lo decisivo contra bytes/instrucciones. Reglas completas:
`docs/STATE.md` § "Política de ingeniería inversa". Foco: obturador electrónico.

Cuenta GitHub: el usuario de este repo es `nicolvus`. Antes de cualquier operación contra `origin`
(push, fetch, `gh`), ejecuta `gh auth switch -u nicolvus` y confirma con `gh auth status` que está activa.

Pendientes: `docs/PENDIENTES.md` es el índice maestro de lo que falta. Regla permanente: toda tarea que se haga, descarte o reabra actualiza ese documento en el mismo commit, y todo pendiente nuevo que se descubra se añade allí (ID nuevo, origen y criterio de cierre). No se cierra una fase sin revisarlo.
