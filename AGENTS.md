# Sony A6000 — instrucciones de proyecto (Codex)

Silencio estricto durante la ejecución: prohibido emitir comentarios, reflexiones o narraciones intermedias entre herramientas (ej.: "Confirmo que...", "Ahora buscaré...", "Reviso ahora..."). Solo ejecuta y piensa en silencio. Cero gasto de tokens visibles durante la ejecución; comenta únicamente al finalizar por completo la tarea.

Antes de investigar manualmente, usa el sistema de conocimiento en
`scripts/knowledge/` (skills en `.agents/skills/`, enlazadas a la fuente
canónica en `.claude/skills/`: `knowledge-navigation`, `contradiction-audit`,
`knowledge-maintenance`, `session-checkpoint`).

Al empezar una sesión: lee `knowledge/CURRENT.md` (resumen operativo breve) antes de
releer el repo, luego los pendientes relevantes de `docs/PENDIENTES.md` y solo los informes
necesarios (índice por subsistema: `docs/INDEX.md`); `knowledge/PROGRESS.md` (historial) solo
si necesitas el detalle de cómo se llegó al estado actual.
Al terminar: informe → PENDIENTES → `docs/STATE.md` (si cambió una conclusión) → `CURRENT.md`
(solo si cambió el contexto mínimo; ≤ ~150 líneas) → `PROGRESS.md` → `scripts/knowledge/build_subsystem_index.py`.
Después de editar cualquier `.md` indexado: corre `knowledge-maintenance`.
Antes de reutilizar un hallazgo: corre `contradiction-audit` (puede estar corregido/superado).

## Regla permanente: las reglas vigentes están en `a6000-handoff-context`

Este repo es la fuente de reglas del trabajo, pero las reglas nuevas —sobre todo las que fijan
el orden del repo (qué documento manda, jerarquía, dónde va cada cosa)— se publican en
`https://github.com/nicolvus/a6000-handoff-context` (privado). Al empezar cada sesión y antes de
decidir algo sobre el orden del repo, ejecuta `bash scripts/agent/sync_rules.sh`: baja lo vigente a `.handoff-rules/` y
lista qué difiere de las copias locales. **Manda GitHub**: aplica en la sesión lo que traiga y,
si la copia local versionada se quedó atrás, actualízala en el mismo commit. Nunca sobrescribas
la copia local con un snapshot más antiguo: si GitHub aún no trae esta regla, esta regla sigue
vigente y no se borra. Norma: `ORDEN.md` §11.

Restricciones del proyecto: sin firmware ejecutado, sin cámara, sin flasheo salvo autorización
expresa del usuario para ese caso concreto.
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

Orden del repositorio: `ORDEN.md` es vinculante (dónde va cada fichero, nombres, estados, pares ES/EN de la wiki);
compruébalo con `python3 scripts/audit/check_order.py` antes de cada commit.

Pendientes: `docs/PENDIENTES.md` es el índice maestro de lo que falta. Regla permanente: toda tarea que se haga, descarte o reabra actualiza ese documento en el mismo commit, y todo pendiente nuevo que se descubra se añade allí (ID nuevo, origen y criterio de cierre). No se cierra una fase sin revisarlo.

## Regla permanente: reinicio experimental en cada sesión física

La cámara puede cambiar de lugar, orientación y escena entre sesiones. Antes de cada experimento físico, identificar de nuevo cámara e IP actuales; comprobar Telnet y RemoteShutter, modelo, versión y hashes pertinentes, originales T050, punteros GOT y mapa de memoria. Localizar de nuevo M, cap y demás objetos dinámicos antes de usarlos; no reutilizar direcciones históricas sin verificarlas. Confirmar estabilidad y disponibilidad de la cámara.

Registrar una línea base propia antes de fotografiar: objetivo y focal, apertura, ISO, velocidad efectiva, modo y configuración de obturador, luz, escena y encuadre, temperatura si disponible, balance de blancos, batería y condiciones relevantes. Marcar como desconocido lo que no se pueda medir. Para comparaciones cuantitativas, crear controles en la misma sesión, mantener escena, luz, apertura, ISO y encuadre constantes en lo posible, conservar RAW originales y metadatos, y verificar velocidad efectiva. No comparar sesiones distintas sin demostrar equivalencia.

Distinguir histórico, actual y comparable. Verificar integridad inicial y final, estado de firmware, acceso a memoria y ausencia de modificaciones en cada sesión; registrar condiciones, evidencia y resultados. Solo lecturas y fotografías normales autorizadas: sin escribir RAM, MMIO, firmware ni NVRAM. No hace falta repetir la ingeniería inversa estática; sí toda validación experimental física.
