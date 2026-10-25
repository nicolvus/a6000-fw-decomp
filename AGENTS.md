# Sony A6000 — instrucciones de proyecto (Codex)

Silencio estricto durante la ejecución: prohibido emitir comentarios, reflexiones o narraciones intermedias entre herramientas (ej.: "Confirmo que...", "Ahora buscaré...", "Reviso ahora..."). Solo ejecuta y piensa en silencio. Cero gasto de tokens visibles durante la ejecución; comenta únicamente al finalizar por completo la tarea.

Antes de investigar manualmente, usa el sistema de conocimiento en
`scripts/knowledge/` (skills en `.agents/skills/`, enlazadas a la fuente
canónica en `.claude/skills/`: `knowledge-navigation`, `contradiction-audit`,
`knowledge-maintenance`, `session-checkpoint`).

Al empezar una sesión: lee `knowledge/CURRENT.md` (resumen operativo breve) antes de
releer el repo; solo recurre a `knowledge/PROGRESS.md` (historial completo) si necesitas
el detalle de cómo se llegó al estado actual.
Después de editar cualquier `.md` indexado: corre `knowledge-maintenance`.
Antes de reutilizar un hallazgo: corre `contradiction-audit` (puede estar corregido/superado).

Restricciones del proyecto: sin firmware ejecutado, sin cámara, sin flasheo.
Al terminar cada cambio versionable: validar, crear un commit convencional y subirlo
a `origin/main` con la cuenta `nicolvus`, sin pedir nueva confirmación. La instrucción
del usuario del 23-10-2026 autoriza esta publicación habitual; no incluir firmware
ni archivos ignorados. Detalle completo en `docs/STATE.md`.

Ingeniería inversa del firmware: **REA primero** (MCP `rea`: funciones, xrefs, llamadas, decompilación,
`trace_native_values`) y Ghidra histórico `silent-liro.gpr` (readOnly) como respaldo cuando REA no
reconoce/cubre la función (Thumb sembradas a mano) o para verificar bytes. Una consulta vacía de REA no
prueba ausencia. `av-cam.bin` tarda ~8 min en frío: reutiliza/abre UNA sesión con
`analysis/rea-independent/bin/session_daemon.py` + `q.py`, consulta por lotes y ciérrala al acabar el hito.
REA y Ghidra comparten motor; verifica lo decisivo contra bytes/instrucciones. Reglas completas:
`docs/STATE.md` § "Política de ingeniería inversa". Foco: obturador electrónico.

Servidor MCP compartido con Claude Code: ver `knowledge/PROGRESS.md` (Fase 6)
para el snippet de `~/.codex/config.toml` necesario para habilitarlo aquí.

Pendientes: `docs/PENDIENTES.md` es el índice maestro de lo que falta. Regla permanente: toda tarea que se haga, descarte o reabra actualiza ese documento en el mismo commit, y todo pendiente nuevo que se descubra se añade allí (ID nuevo, origen y criterio de cierre). No se cierra una fase sin revisarlo.
