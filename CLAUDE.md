# Sony A6000 — instrucciones de proyecto (Claude Code)

Silencio estricto durante la ejecución: prohibido emitir comentarios, reflexiones o narraciones intermedias entre herramientas (ej.: "Confirmo que...", "Ahora buscaré...", "Reviso ahora..."). Solo ejecuta y piensa en silencio. Cero gasto de tokens visibles durante la ejecución; comenta únicamente al finalizar por completo la tarea.

Antes de investigar manualmente, usa el sistema de conocimiento en
`scripts/knowledge/` (skills: `knowledge-navigation`, `contradiction-audit`,
`knowledge-maintenance`, `session-checkpoint` en `.claude/skills/`).

Al empezar una sesión: lee `knowledge/CURRENT.md` (resumen operativo breve) antes de
releer el repo; solo recurre a `knowledge/PROGRESS.md` (historial completo) si necesitas
el detalle de cómo se llegó al estado actual.
Después de editar cualquier `.md` indexado: corre `knowledge-maintenance`.
Antes de reutilizar un hallazgo: corre `contradiction-audit` (puede estar corregido/superado).

Commits: al terminar cada fase (S54 en adelante) haz SIEMPRE commit local de los cambios propios (Conventional Commits, sin `git push`; excluye logs de sesión REA).

Restricciones del proyecto: sin firmware ejecutado, sin cámara, sin flasheo,
sin `git push` salvo instrucción explícita. Detalle completo en `docs/STATE.md`.

Ingeniería inversa del firmware: **REA primero** (MCP `rea`: funciones, xrefs, llamadas, decompilación,
`trace_native_values`) y Ghidra histórico `silent-liro.gpr` (readOnly) como respaldo cuando REA no
reconoce/cubre la función (Thumb sembradas a mano) o para verificar bytes. Una consulta vacía de REA no
prueba ausencia. `av-cam.bin` tarda ~8 min en frío: reutiliza/abre UNA sesión con
`analysis/rea-independent/bin/session_daemon.py` + `q.py`, consulta por lotes y ciérrala al acabar el hito.
REA y Ghidra comparten motor; verifica lo decisivo contra bytes/instrucciones. Reglas completas:
`docs/STATE.md` § "Política de ingeniería inversa". Foco: obturador electrónico.
