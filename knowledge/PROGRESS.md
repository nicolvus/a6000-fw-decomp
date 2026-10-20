# Progreso — sistema de conocimiento Sony A6000

Checkpoint persistente. Actualizar al terminar cada etapa, antes de continuar
con la siguiente. No reescribir historial: añadir entradas nuevas.

## Fases (ver plan completo en el mensaje del usuario, 2026-10-18)

| # | Fase | Estado |
|---|------|--------|
| 1 | Validar/mejorar indexación FTS5 existente | COMPLETA |
| 2 | Indexación jerárquica (estilo PageIndex, sin dependencia) | COMPLETA |
| 3 | Grafo de conocimiento en SQLite | COMPLETA |
| 4 | Reconciliación de hallazgos (S19–S30, Darwin, EFCS, GPIO, WriteStill) | COMPLETA |
| 5 | Recuperación adaptativa (router de métodos) | COMPLETA |
| 6 | CLI unificada + servidor MCP | COMPLETA |
| 7 | Skills compartidas Claude/Codex | COMPLETA (ver caveat de verificación) |
| 8 | Memoria persistente / checkpoints de sesión | COMPLETA |
| 9 | Benchmarks reproducibles | COMPLETA |
| 10 | Validación final | COMPLETA |

## Archivos creados hasta ahora

- `scripts/knowledge/index_docs.py` — indexador incremental SHA-256 → SQLite FTS5
  + tablas jerárquicas `documents`/`nodes` (Repositorio→Subsistema→Documento→Sección).
  IDs estables = sha1(path::heading::occurrence)[:16]; no dependen del orden global.
- `scripts/knowledge/search.py` — CLI: `exact` (ripgrep), `text` (BM25),
  `tree` (navega subsistema/documento/sección sin cargar cuerpo),
  `section` (recupera texto original por rango de líneas, sin duplicar contenido en la DB).
- `tests/knowledge/test_index_docs.py` — 4 tests unittest, verdes (roundtrip, incremental,
  poda de borrados, jerarquía+recuperación exacta).
- `.knowledge-cache/knowledge.sqlite` — DB regenerable (gitignorada): 355 documentos,
  2684 secciones/nodos, 32 subsistemas (derivados de los 2 primeros componentes de ruta).
- `.venv/` + `knowledge/requirements-dev.txt` — entorno aislado con ruff/mypy/pytest.

## Fase 3 — Grafo de conocimiento (detalle)

- `scripts/knowledge/build_graph.py` — añade tablas `entities`/`relations` a la MISMA DB
  (no hay sistema paralelo). Dos fuentes, ambas deterministas:
  1. **Function/CALLS** desde JSON con forma `{binary, sha256, address_space, symbol_value,
     original_name, outgoing}` (detectado por forma, no por ruta fija). Una relación CALLS
     solo se crea si el nombre del destino en `outgoing` coincide EXACTAMENTE con el nombre
     de otra entidad del MISMO binario (misma sha256); si no hay coincidencia exacta se
     descarta (no se inventan destinos). Con los 3 dossiers reales: 3 entidades, 1 relación.
  2. **CORRECTS/SUPERSEDES** desde Markdown: busca palabras clave que los propios
     investigadores ya escribieron (CORRECCIÓN/corrige, superad[ao]/supera) línea por línea
     (no por sección completa — una sección larga como el índice del README NO genera
     relaciones falsas solo por contener la palabra en otro punto). El objetivo se resuelve
     por: (a) enlace Markdown en una ventana de ±2 líneas alrededor del marcador, o
     (b) referencia de sesión (`sesión N`/`SN`) en la MISMA línea del marcador (no en la
     ventana: el número de sesión del encabezado de la propia sección no debe colarse como
     objetivo — bug real detectado y corregido con test de regresión). Si una referencia de
     sesión es ambigua (más de 2 documentos candidatos), se descarta en vez de adivinar.
  - Cada relación guarda: `owner_source` (archivo que la genera; al reindexar/eliminar ese
    archivo se regeneran/eliminan solo sus relaciones, incluyendo huérfanos de archivos ya
    borrados), `source_path`, rango de líneas, `status` (del vocabulario controlado,
    detectado en el texto si está presente, `NO_VERIFICADO` por defecto) y `evidence`
    (cita textual literal).
  - Con los datos reales: 31 relaciones CORRECTS/SUPERSEDES (antes de la corrección del
    bug de ventana: 410 — la mayoría falsos positivos por proximidad de sección completa).
- `scripts/knowledge/search.py` gana `graph` (relaciones entrantes/salientes de un doc,
  con evidencia) y `claim` (conclusión vigente de un documento: qué lo corrige/supera).
  Verificado con consultas reales del plan: "¿qué corrigió S28?" → S23/S25 con cita exacta;
  conclusión vigente de S27 → corregido por README y superado según CONTEXT.md.
- `tests/knowledge/test_build_graph.py` — 4 tests: filtrado CALLS por nombre+binario exacto,
  no-confusión encabezado-vs-cuerpo en referencias de sesión, resolución por enlace Markdown
  + consulta de conclusión vigente, y poda de relaciones al eliminar el documento que las originó.

## Fase 4 — Reconciliación (detalle, PARCIAL)

Hecho y verificado:
- Respaldo íntegro de `CONTEXT.md`: `docs/history/CONTEXT.md.2026-10-18.bak` +
  `docs/history/CONTEXT.md.sha256.orig`. Verificado con `sha256sum -c --strict` → OK,
  y `diff` contra el original → idéntico.
- `scripts/knowledge/export_corrections.py` (nuevo): genera `docs/CORRECTIONS.md` (31 filas,
  derivado de `relations` tipo CORRECTS/SUPERSEDES) y `docs/OPEN-QUESTIONS.md` (382 filas,
  secciones con marcador NO_VERIFICADO/CONFLICTO_PENDIENTE vía FTS5). Documentos regenerables,
  marcados "no editar a mano". Test de regresión: `test_export_corrections.py` (1 test), verde.
- `docs/STATE.md` (nuevo): estado breve con enlaces a fuentes canónicas ya existentes
  (no reinterpreta nada, solo cita y enlaza): corrección Darwin base ROM 0x4200,
  SetImageWrited 0x1007 (no 0x1009), mapeo GPIO P4D/P4E/P4C/P4B, EFCS→IMX210, y la tabla
  de flujos completos/incompletos de `docs/estado-y-viabilidad-2026-10-17.md`.

Completado también:
- `CONTEXT.md` reducido de 1263 a 116 líneas: conserva verbatim solo S28–S30 (investigación
  activa) + punteros a `docs/STATE.md`, `docs/CORRECTIONS.md`, `docs/OPEN-QUESTIONS.md` y al
  historial íntegro. **Verificación de integridad:** `sha256sum` de
  `docs/history/CONTEXT-full-2026-10-18.md` (copia legible íntegra) coincide EXACTAMENTE
  con el hash original pre-edición (`5bd41bb4...`) — ningún contenido se perdió, solo se
  reubicó. El `.bak` binario-idéntico se conserva aparte.
- **Bug de auto-contaminación detectado y corregido:** al reindexar el propio
  `docs/CORRECTIONS.md` (que por diseño contiene la palabra "CORRECTS" y decenas de enlaces),
  el grafo generaba 121 relaciones circulares a partir de su propio export. Corregido
  excluyendo `docs/CORRECTIONS.md`/`docs/OPEN-QUESTIONS.md` de la extracción como fuentes
  primarias (`GENERATED_DOCS` en `build_graph.py`), con test de regresión que verifica
  reconstrucción estable (idempotente) tras reindexar los documentos generados.
- Total final estable tras dos pasadas consecutivas: 39 relaciones CORRECTS/SUPERSEDES,
  3 entidades Function, 1 CALLS. `docs/CORRECTIONS.md` y `docs/OPEN-QUESTIONS.md` regenerados.

No hecho (límite de alcance, no omisión):
- No se añadieron extractores para los JSON con esquema distinto al de `dossiers.json`
  (ver límite documentado en Fase 3): GPIO/IMX210/REA no están en el grafo todavía.

## Fase 5 — Recuperación adaptativa (detalle)

- `search.py ask <consulta> [--budget N]` (nuevo): clasifica la consulta con
  `classify_query` — `identifier` (dirección hex o símbolo sin espacios) → `exact`;
  `doc` (ruta `.md`) → relaciones entrantes (`claim`) + árbol (`tree`); `concept`
  (texto libre) → BM25 (`text`) + correcciones relacionadas de cada resultado vía grafo.
  Deduplica por `(ruta, línea)`, recorta por presupuesto de caracteres configurable
  (`--budget`, por defecto 2000) e informa cuántos resultados se mostraron vs. el total.
- Robustez corregida: `ask` ahora degrada sin fallar si `build_graph.py` no se ha
  ejecutado todavía (tabla `relations` ausente) — bug real encontrado por el test
  de regresión al indexar sin construir el grafo primero.
- `tests/knowledge/test_adaptive_search.py` (nuevo, 5 tests): clasificación de los
  3 tipos de consulta + recorte por presupuesto con aviso de truncado.
- Verificado con consultas reales: `ask "0x932a44"` (identifier), `ask
  "docs/capture/s27-effect-postprocess-rewire.md"` (doc), `ask "Darwin base ROM"`
  (concept, con corrección relacionada vía grafo incluida automáticamente).
- Total suite tras esta fase: 15/15 tests, ruff/mypy sin avisos.

## Fase 6 — CLI unificada + servidor MCP (detalle)

- CLI unificada: `search.py` ya cubre exact/text/tree/section/graph/claim/ask (fase 5);
  no se creó un entrypoint adicional porque multiplicaría comandos sin necesidad
  (`index_docs.py`/`build_graph.py`/`export_corrections.py` son operaciones de
  mantenimiento separadas a propósito, ejecutadas explícitamente, nunca disparadas
  desde una búsqueda de solo lectura).
- `scripts/knowledge/mcp_server.py` (nuevo): servidor MCP de solo lectura con el SDK
  oficial `mcp==2.3.0` (API `MCPServer`, antes `FastMCP` en mcp 1.x — instalado en
  `.venv/`, versión fijada en `knowledge/requirements.txt`). **No reimplementa lógica**:
  cada tool captura la salida de la función `cmd_*` correspondiente de `search.py` vía
  `contextlib.redirect_stdout` — una sola fuente de verdad para CLI y MCP.
  9 tools: `search_exact`, `search_documents`, `search_hybrid`, `find_symbol`,
  `get_document_section`, `query_graph`, `find_corrections`, `get_open_questions`,
  `get_current_state` — exactamente las operaciones mínimas pedidas, sin duplicar.
- **Verificado de verdad, no solo importado:**
  - `tests/knowledge/test_mcp_server.py` (4 tests) usa el servidor real en memoria:
    `list_tools()` confirma que las 9 herramientas se descubren vía protocolo MCP;
    `call_tool("search_exact", ...)` y `call_tool("get_current_state", ...)` devuelven
    datos reales del repositorio; una llamada con parámetro fuera de rango
    (`direction="sideways"`) no tira el servidor.
  - Arranque real por stdio: `python3 scripts/knowledge/mcp_server.py < /dev/null`
    sale con código 0 y sin stderr (smoke test de inicialización del transporte).
- Integración de clientes:
  - **Claude Code:** `.mcp.json` en la raíz del proyecto (nuevo), apunta al Python del
    venv del proyecto — no se tocó ninguna configuración MCP previa (no existía ninguna).
  - **Codex:** su configuración MCP vive en `~/.codex/config.toml` (fuera del proyecto,
    global del usuario); no se modificó un archivo global sin instrucción explícita.
    Snippet exacto para que el usuario lo añada si quiere usar el mismo servidor desde Codex:
    ```toml
    [mcp_servers.sony-a6000-knowledge]
    command = "/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/.venv/bin/python3"
    args = ["/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/scripts/knowledge/mcp_server.py"]
    ```
- Total suite tras esta fase: 19/19 tests, ruff/mypy sin avisos.

## Fase 7 — Skills compartidas (detalle)

- Fuente canónica única: `.claude/skills/{knowledge-navigation,contradiction-audit,
  knowledge-maintenance,session-checkpoint}/SKILL.md`. `.agents/skills/*` son enlaces
  simbólicos relativos a esa fuente (`ln -s ../../.claude/skills/<nombre> ...`),
  confirmado que no son copias divergentes: `readlink -f` de cada uno resuelve al
  archivo canónico real.
- Solo 4 skills, no las ~10 que enumera el plan original: se consolidaron
  `firmware-evidence`+`context-retrieval` dentro de `knowledge-navigation` y
  `graph-navigation` dentro de `contradiction-audit` porque todas invocan los
  mismos 2-3 scripts (`search.py`, `build_graph.py`) — crear una skill por
  subcomando de CLI habría sido redundante sin aportar procedimiento distinto.
  NO se crearon `firmware-comparison` ni `retrieval-benchmark`: no existe todavía
  una herramienta de comparación de firmware ni un harness de benchmarks que
  esas skills pudieran describir honestamente (ver Fase 9 pendiente).
- `CLAUDE.md` y `AGENTS.md` de proyecto (nuevos, no existían): breves, solo
  apuntan a las skills y a `knowledge/PROGRESS.md`/`docs/STATE.md`, sin duplicar
  contenido técnico.
- Validación estática de las 8 rutas (4 canónicas + 4 symlinks): frontmatter
  `name`/`description` presente y bien formado en todas — verificado con un
  parser real, no solo "se ve bien".
- **Caveat honesto de verificación:** no se pudo confirmar el descubrimiento EN
  CALIENTE por un Claude Code o Codex reales, porque esta misma sesión ya había
  cargado su listado de skills antes de que estos archivos existieran, y no hay
  forma de reiniciar la sesión desde aquí para re-listarlas; tampoco hay un
  binario de Codex disponible en este entorno para lanzarlo. Queda pendiente que
  el usuario confirme en una sesión nueva que `/knowledge-navigation` (u otro
  nombre de invocación de su cliente) aparece en el listado.

## Fase 8 — Memoria persistente / checkpoints (detalle)

- `scripts/knowledge/checkpoint.py` (nuevo): checkpoints estructurados JSON en
  `knowledge/checkpoints/` (directorio ya existía, vacío desde la Fase 1). Campos
  obligatorios según el plan: goal, done, files, findings, evidence, corrections,
  tests, blockers, next_actions, permissions_state. Nunca se edita el JSON a mano:
  se crea con flags de CLI (`create --goal ... --done ... --file ... ...`).
- `list`/`latest`/`show <id>` para leer sin tener que abrir archivos JSON directamente.
- **Bug real encontrado y corregido:** el timestamp inicial tenía resolución de
  segundo; dos checkpoints creados en el mismo segundo se ordenaban por el sufijo
  UUID aleatorio en vez de por orden de creación, así que `latest` podía devolver
  el equivocado. Corregido con microsegundos en el timestamp; test de regresión
  (`test_list_and_latest_reflect_created_checkpoint`) que crea dos seguidos y
  verifica el orden.
- `tests/knowledge/test_checkpoint.py` (3 tests: campos completos, list/latest,
  show por id parcial). Total suite: 22/22, ruff/mypy sin avisos.
- Primer checkpoint real creado: `knowledge/checkpoints/2026-10-18T05-10-01-412803Z-fe6147e3.json`,
  cubre las fases 1-8 de esta misma sesión con hallazgos, archivos, tests y bloqueos reales.

## Fase 9 — Benchmarks (detalle)

- `scripts/knowledge/benchmark.py` (nuevo): 7 consultas de referencia reales
  (SetImageWrited por dirección y por código corregido, GPIO cortinillas, EFCS,
  Darwin base ROM, comparación A6300, corrección de S27), cada una con una
  verdad de referencia fijada MANUALMENTE antes de ejecutar el script (ver
  campo `note` por consulta) — nunca "lo que el propio sistema devolvió".
  Compara ripgrep crudo sobre todo el repo vs `search.py text`(FTS5)/`exact` vs
  `ask` (adaptativo), midiendo latencia real, líneas, caracteres y una
  estimación de tokens (caracteres/4, marcada explícitamente como aproximación:
  no hay tokenizador real en este entorno). Salida regenerable:
  `knowledge/benchmarks/report.md` + `.json`.
- **Bug real encontrado y corregido durante la propia ejecución:** 2 de 21
  comparaciones daban "fallo" porque el snippet BM25 resalta coincidencias
  insertando `[corchetes]` DENTRO del token (`1ST_[CURTAIN]_MG`), rompiendo la
  subcadena esperada (`1st_curtain_mg`). El sistema sí encontraba el documento
  correcto (verificado manualmente); el defecto estaba en el criterio de acierto
  del benchmark, no en la recuperación. Corregido quitando `[`/`]` antes de
  comparar. Resultado final real: **21/21 aciertos**.
- Resultado honesto más relevante (sin inventar porcentajes): para consultas
  conceptuales, ripgrep crudo sobre todo el repo devuelve decenas de MB (p. ej.
  "darwin-rom-base": 191.760.545 caracteres, ~47.9M tokens estimados) porque
  coincide con logs de sesiones de cientos de miles de líneas; `search.py text`
  (FTS5) y `ask` devuelven ~2-3 KB (~250-670 tokens estimados) para la MISMA
  consulta, con el documento correcto entre los primeros resultados. La
  reducción es una consecuencia medida de indexar por sección en vez de grepear
  archivos completos, no una optimización ad-hoc para la demo.
- `tests/knowledge/test_benchmark.py` (1 test, verifica estructura del reporte
  con un corpus de prueba pequeño, no valores absolutos que dependen de la
  máquina). Total suite: 23/23, ruff/mypy sin avisos.

## Fase 10 — Validación final (detalle)

Ejecutado en una sola pasada, 18-10-2026:
1. Reconstrucción completa desde cero (`rm .knowledge-cache/knowledge.sqlite` +
   index→graph→export→reindex→rebuild): 359 archivos, 2697 secciones, 3 entidades,
   40 relaciones — estable, mismos totales que ejecuciones anteriores.
2. `pytest tests/knowledge -q`: 23/23 passed.
3. `ruff check scripts/knowledge tests/knowledge` + `mypy --ignore-missing-imports`:
   sin avisos.
4. `python3 scripts/knowledge/mcp_server.py < /dev/null`: exit=0, sin stderr
   (arranque real por stdio).
5. Integridad de `CONTEXT.md`: `sha256sum docs/history/CONTEXT-full-2026-10-18.md`
   == hash original pre-edición (`5bd41bb4...`) — confirmado de nuevo, no solo
   en la Fase 4.
6. `firmware/` y `analysis/ghidra/*.gpr` listados (no leídos/modificados):
   estructura intacta, ningún archivo binario tocado por este trabajo.
7. Sin repositorio `.git` en el proyecto: no hubo riesgo de commit/push accidental;
   ninguna operación de git se ejecutó en ninguna fase.

## Entorno de desarrollo

- `.venv/` creado en la raíz del proyecto (autorizado por el usuario, aislado, sin sudo).
- Versiones fijadas en `knowledge/requirements-dev.txt`: ruff 0.17.1, mypy 2.4.0, pytest 9.1.1.
- Activar con `source .venv/bin/activate` antes de `ruff check` / `mypy` / `pytest`.

## Pruebas ejecutadas

- `python3 -m unittest tests.knowledge.test_index_docs` → OK (3/3), 2026-10-18.
- Búsqueda exacta sobre `0x4383fd6c` y `SetImageWrited`: resultados correctos,
  incluida la corrección S12 (`0x1007` no `0x1009`).
- Búsqueda textual BM25 sobre "SilentShutter EFCS" y "Darwin base ROM": resultados pertinentes.
- `ruff`/`mypy`: NO DISPONIBLES en este entorno (solo quedan cachés `.ruff_cache`/`.mypy_cache`
  de sesiones previas, sin binarios instalados). Pendiente: crear venv del proyecto
  (autorizado por el usuario) e instalar ahí antes de validar estilo.

## Bloqueos activos

- Ninguno crítico. `ruff`/`mypy` ausentes (no bloquea funcionalidad, sí la validación de estilo).

## Límite de alcance documentado (Fase 3)

Solo se incorporaron JSON con la forma exacta `{binary, sha256, address_space,
symbol_value, original_name}` (3 entidades reales, en `analysis/functions/dossiers.json`).
Otros JSON de análisis con esquemas distintos (p. ej. `rea-takePicture-decompile.json`,
`silent-shutter-converter.json`, tablas IMX210/GPIO) NO están todavía en el grafo:
cada esquema heterogéneo necesitaría su propio extractor, y generalizar a ciegas
violaría el requisito de "no generar miles de relaciones irrelevantes". Pendiente:
añadir extractores específicos por esquema cuando se prioricen (candidatos naturales
para la Fase 4: GPIO fm3-gpio-shutter-mapping, EFCS capture-selector, WriteStill/SetImageWrited).

## Archivos nuevos de la Fase 4

- `docs/STATE.md` — estado breve con enlaces a fuentes canónicas.
- `docs/CORRECTIONS.md`, `docs/OPEN-QUESTIONS.md` — generados, regenerar con
  `export_corrections.py` tras cada `build_graph.py`.
- `scripts/knowledge/export_corrections.py` + `tests/knowledge/test_export_corrections.py`.
- `docs/history/CONTEXT-full-2026-10-18.md` (copia legible íntegra, indexada),
  `docs/history/CONTEXT.md.2026-10-18.bak` + `.sha256.orig` (respaldo binario-verificado).
- `CONTEXT.md` reescrito (116 líneas: S28–S30 + punteros).

## Fase 11 — auditoría independiente y corrección de defectos (2026-10-18)

Una auditoría del usuario (no de este mismo sistema) encontró defectos reales de
exactitud y de evaluación en lo entregado en las fases 1-10. Se corrigieron con
pruebas de regresión nuevas (39 tests totales, antes 23); cada fix documenta el
bug reproducido en el docstring/comentario del propio código.

**P1 — Exactitud del grafo (CERRADO):**
- `build_graph.py::build_function_graph` indexaba CALLS por nombre corto de método en
  un `dict` que se sobrescribía: si dos clases del mismo binario compartían nombre de
  método (p. ej. `A::run()` y `B::run()`), la llamada podía apuntar a la clase
  equivocada según el orden de inserción — el caso exacto que describió la auditoría.
  Fix: `qualified_name()` nuevo (conserva el calificador `ns::Clase::metodo`); se
  intenta primero resolución por nombre calificado exacto, y solo se cae a nombre
  corto cuando es ÚNICO en el binario; si es ambiguo, NO se genera arista (ni la
  correcta ni la incorrecta). Tests:
  `test_ambiguous_short_name_in_same_binary_is_discarded_not_misrouted`,
  `test_qualified_outgoing_name_disambiguates_same_short_name`.
- CORRECTS/SUPERSEDES: antes el status se detectaba buscando el vocabulario en toda
  la ventana de ±2 líneas, pudiendo atribuir un status de una oración vecina no
  relacionada. Ahora se busca primero en la línea del propio marcador. Además se
  separaron relaciones con enlace en la MISMA línea del marcador (evidencia directa)
  de relaciones cuyo enlace solo aparece en la ventana (proximidad, no demostración):
  estas últimas se marcan `CONFLICTO_PENDIENTE` y `extraction_method` distinto
  (`...window_candidate` vs `...same_line`), nunca heredan un status más fuerte por
  cercanía. Test: `test_link_only_in_window_is_candidate_not_verified`.

**P2 — Recuperación de contexto (PARCIAL, ver pendientes):**
- `ROOT = Path.cwd()` en los 6 scripts dependía del directorio desde el que se
  invocara el proceso. Nuevo `scripts/knowledge/_paths.py::find_root()`: busca hacia
  arriba desde cwd el marcador `CLAUDE.md`; cae a cwd si no lo encuentra (preserva el
  comportamiento de los fixtures de test, que deliberadamente no tienen marcador).
- `_budget_print` (router `ask`): un primer resultado más grande que el presupuesto se
  imprimía completo (la condición `shown > 0` lo eximía del recorte) — el presupuesto
  quedaba sin efecto real. Ahora se trunca también el primer bloque. Tests:
  `test_single_oversized_block_is_truncated_not_printed_whole`,
  `test_budget_print_never_exceeds_budget_across_multiple_blocks`.
- `cmd_exact`/rama `identifier` de `ask`: `rg --max-count N` limita POR ARCHIVO, no en
  total; con muchos archivos la salida combinada podía seguir siendo enorme. Ahora el
  límite se aplica en Python sobre el total de líneas combinadas (límite global real).
  Test: `test_global_limit_caps_total_lines_across_all_files`.
- `cmd_section` ganó `--subtree` (y la tool MCP `get_document_section` el parámetro
  `subtree`): por defecto devuelve solo el contenido PROPIO de la sección (hasta su
  primer sub-encabezado); con `--subtree` incluye todos los descendientes hasta el
  siguiente encabezado del mismo nivel o superior. Antes solo existía el modo "propio"
  sin forma de pedir el árbol completo. Tests: `test_default_section_excludes_children`,
  `test_subtree_includes_children_but_not_next_sibling`.
- `cmd_text` ganó `--offset` (paginación real sobre FTS5 `LIMIT`/`OFFSET`). Test:
  `test_offset_returns_different_page`.
- Nuevo comando `search.py freshness` + tool MCP `check_index_freshness`: compara el
  SHA-256 actual de cada doc contra la tabla `files` y reporta archivos
  modificados/añadidos/eliminados desde el último `index_docs.py`. Antes no había
  ninguna forma de saber si el índice estaba desincronizado. Tests en
  `tests/knowledge/test_freshness.py` (4 casos).
- `split_sections` (`index_docs.py`) descartaba TODO el texto anterior al primer
  encabezado Markdown. Ahora se conserva como sección `(preámbulo)` (nivel -1, nunca
  ancestro de un encabezado real en `build_tree`, para no corromper la jerarquía).
  Tests: `test_preamble_before_first_heading_is_preserved`,
  `test_preamble_does_not_become_parent_of_first_heading`.
- Límite MCP global: `mcp_server.py::_captured` ahora trunca cualquier salida a
  `MCP_MAX_CHARS = 20000` (antes una tool podía devolver una respuesta de tamaño
  arbitrario si el cliente pedía un `--limit`/`--budget` grande).
- **Pendiente real (no cerrado):** "ampliación de fragmentos por identificador" más
  allá de `--subtree`/`--offset` (p. ej. pedir N líneas de contexto arbitrarias
  alrededor de un `node_id`) no se implementó — el alcance actual cubre los dos casos
  concretos que pidió la auditoría (subárbol completo, paginación de `text`), no un
  mecanismo general de contexto configurable.

**P3 — Calidad del conocimiento (CERRADO en lo señalado):**
- `export_open_questions` generaba `docs/OPEN-QUESTIONS.md` buscando por TEXTO LIBRE
  las palabras NO_VERIFICADO/CONFLICTO_PENDIENTE en cualquier sección indexada: una
  sección que solo EXPLICA el vocabulario de status (sin ser una relación real del
  grafo) se contaba como pregunta abierta. Con el corpus real esto causaba 384 "filas"
  falsas. Ahora sale de la tabla `relations` (solo relaciones con ese status): tras
  rebuild completo, `docs/OPEN-QUESTIONS.md` pasó de 384 a **39 filas reales**.
  Test: `test_open_questions_ignores_sections_that_only_mention_the_word`.
- Mensaje de `cmd_claim`/`find_corrections` cuando no hay relaciones entrantes: antes
  decía "se mantiene como fuente vigente" (afirmación no demostrada por la ausencia de
  datos). Ahora aclara explícitamente que la ausencia de correcciones registradas NO
  demuestra vigencia.
- Tests de contradicción/corrección parcial/referencia histórica: ya existían
  parcialmente en `test_build_graph.py` (resolución de sesión, no auto-contaminación);
  se añadieron los de ambigüedad de nombre y candidata-vs-verificada arriba. No se
  amplió a un conjunto de "contradicciones narrativas" más allá de lo que el grafo
  determinista puede detectar (sigue siendo deliberadamente NO basado en inferencia de
  LLM: ver diseño original).

**P4 — Benchmarks (NO ABORDADO esta sesión):** sigue comparando presencia de
subcadena en la salida, no precisión de fuentes/rangos/evidencias, y no distingue
tokens estimados de tokens realmente consumidos por un agente real. Rediseñarlo es
trabajo no trivial (requiere una verdad de referencia estructurada, no solo una
subcadena esperada) y se deja pendiente explícitamente, no se improvisó una versión
a medias.

**P5 — Integración y memoria (PARCIAL):**
- Checkpoint actualizado con esta fase (ver `knowledge/checkpoints/`, el de esta
  sesión referencia fases 9-11 como completas, no pendientes).
- Verificación real de MCP/skills desde una sesión NUEVA de Claude Code o Codex sigue
  sin poder hacerse desde dentro de esta misma sesión (limitación estructural, igual
  que en la Fase 7).
- Extractores por esquema para GPIO/IMX210/OSAL/REA/Ghidra: NO implementados. Sigue
  siendo trabajo futuro (ver límite de Fase 3 arriba), ahora con la ambigüedad de
  nombres ya resuelta en el extractor existente para cuando se añadan.

## Fase 12.1-12.2 — segunda auditoría: negación, duplicados, raíz y streaming (2026-10-18)

Segunda auditoría independiente (Fase 12), con casos reproducidos nuevos distintos
de los de la Fase 11. Se corrigieron todos los de 12.1 (crítico) y los de 12.2 con
reproducción concreta; 12.3 ya estaba sustancialmente cubierto por la Fase 11 y no
se tocó sin necesidad. 12.4-12.10 (extractores por esquema, consultas multietapa,
rediseño de benchmark, verificación cruzada de clientes, `CURRENT.md`) **NO se
abordaron esta vuelta** — alcance explícitamente fuera de esta sesión, ver abajo.

**12.1.A — Negación en CORRECTS/SUPERSEDES (CERRADO):** `VERIFICADO: esta revisión
NO corrige [el informe antiguo](old.md).` generaba igualmente `CORRECTS` con status
`VERIFICADO`, ignorando la negación. `build_graph.py` ahora detecta una partícula
negativa (`no/nunca/jamás/tampoco`) en las ~4 palabras previas al marcador, sin
cruzar el final de la oración anterior; si está negado, el status se fuerza a
`CONFLICTO_PENDIENTE` y el `extraction_method` queda marcado `..._negated`, nunca
`VERIFICADO` pese al vocabulario cercano. Test:
`test_negated_correction_mention_is_not_verified`.

**12.1.B — Identidad ambigua de funciones:** ya resuelta en la Fase 11 (nombre
calificado completo + descarte si el nombre corto es ambiguo en el binario). La
auditoría pide además modelo de cámara, versión de firmware, hash de binario, base
de carga y modo ARM/Thumb como parte de la identidad — **no se añadieron**: el único
dossier de función real del repo (`analysis/functions/dossiers.json`, 3 items) no
contiene esos campos. Añadirlos ahora sería inventar estructura que el dato real no
tiene; se deja documentado para cuando los extractores de 12.4 (Ghidra/REA) los
aporten con datos reales.

**12.1.C — `UNIQUE constraint failed: entities.id` con dossiers duplicados
(CERRADO):** la misma función (misma identidad técnica: sha256+address_space+
symbol_value) en dos JSON distintos hacía fallar el segundo `INSERT`. Se añadió la
tabla `entity_sources` (entity_id, owner_source, original_name, confidence) para
procedencia múltiple: la entidad se crea una sola vez (primera fuente = canónica),
cada dossier adicional solo añade/actualiza su fila de procedencia vía `INSERT ...
ON CONFLICT DO UPDATE` (idempotente, no vuelve a fallar al re-ejecutar). Si dos
fuentes dan `original_name` distinto para la misma identidad técnica, se registra el
conflicto en `entities.extra` (`name_conflict`) en vez de sobrescribir en silencio o
descartar la segunda fuente. Al eliminar un dossier, la entidad solo se borra si
NINGUNA fuente viva la sigue aportando. Tests:
`test_duplicate_function_across_dossiers_does_not_crash_and_keeps_both_sources`,
`test_contradictory_metadata_between_dossiers_is_flagged_not_silently_overwritten`,
`test_removing_one_of_two_dossiers_keeps_entity_alive_via_remaining_source`.
Verificado además con `build_graph.py` ejecutado dos veces seguidas sobre el repo
real: idempotente, mismo resultado (3 entidades, 1 CALLS, 39 CORRECTS/SUPERSEDES).

**12.2.A — Resolución de raíz rota fuera del proyecto (CERRADO):** caso reproducido
y verificado manualmente: ejecutar cualquier script desde `/tmp` (cwd ajeno, sin
`CLAUDE.md` en ningún ancestro) hacía que `find_root()` devolviera ese mismo `/tmp`
como raíz (fallback antiguo), con 0 documentos indexados. `_paths.py` ahora
prioriza: (1) variable de entorno `SONY_A6000_KB_ROOT` explícita, validada contra
`CLAUDE.md`; (2) ascenso desde cwd buscando `CLAUDE.md` (comportamiento previo); (3)
**nuevo** — si (2) no encuentra nada, ascenso desde la ubicación de INSTALACIÓN del
propio `_paths.py`, que sí resuelve al proyecto real; (4) cwd sin resolver, último
recurso solo para fixtures de test que deliberadamente no tienen `CLAUDE.md` propio.
Verificación manual: `cd /tmp && python3 .../search.py freshness` ahora imprime
"Índice al día" contra el proyecto real, no "0 archivos". Todos los fixtures de test
que simulaban un proyecto aislado (`test_adaptive_search.py`, `test_build_graph.py`,
`test_checkpoint.py`, `test_export_corrections.py`, `test_freshness.py`,
`test_index_docs.py`, `test_benchmark.py`) ahora escriben su propio `CLAUDE.md`
vacío, para no depender implícitamente del fallback. Tests nuevos en
`test_paths.py`: ascenso normal, fallback a instalación, override por entorno válido
e inválido (`SystemExit`).

**12.2.B — `rg` bufferizaba toda la salida en memoria (CERRADO):** `cmd_exact` y la
rama `identifier` de `cmd_ask` usaban `subprocess.run(capture_output=True)`, que
bufferiza TODO el stdout de `rg` antes de devolver nada — con miles de coincidencias,
cientos de MB en memoria por solo mostrar `--limit`. Nuevo helper `_rg_stream()`
(compartido por ambos) usa `Popen` y lee el pipe línea a línea, cortando en cuanto se
alcanza `RG_MAX_SCAN = 5000` líneas leídas o `RG_TIMEOUT_S = 10s`, lo que ocurra
primero — sin esperar a que `rg` termine de buscar en todo el corpus. El límite
mostrado (`--limit`) sigue aplicándose en Python, ahora sobre el stream, no sobre una
lista ya completa. Test: `ExactStreamingCapTest` (genera >5000 líneas coincidentes,
verifica que se corta y que el aviso de tope aparece).

**12.2.C — Límites de contexto en todas las rutas:** ya cubiertos por `budget`
(`ask`), `limit` (`exact`/`text`/`identifier`), `--subtree`/`--offset` (`section`),
y el tope global MCP de 12.2.D. Las consultas del grafo (`cmd_graph`) y
`find_corrections`/`cmd_claim` ya tenían `LIMIT` explícitos desde la Fase 11; no se
tocaron sin necesidad.

**12.2.D — Tools MCP sin tope (CERRADO):** `get_current_state()` devolvía
`docs/STATE.md` COMPLETO sin pasar por `MCP_MAX_CHARS` (único tool que no usaba
`_captured`); `get_open_questions` tampoco pasaba por el tope global de caracteres
(solo recortaba por líneas). Nuevo helper `_cap_chars(texto, offset)` compartido por
`_captured` y ambas tools: aplica el mismo tope global Y admite paginación por
`offset` (en caracteres) para seguir leyendo más allá del corte. Tests:
`test_get_current_state_respects_global_mcp_char_limit`,
`test_get_current_state_offset_paginates`.

**12.3 — Calidad del conocimiento:** ya cubierto en Fase 11 (mensaje de `cmd_claim`
sobre no-vigencia por ausencia; `OPEN-QUESTIONS.md` basado en grafo, no en texto
libre). No se reescribió sin necesidad.

**Verificación real ejecutada:** rebuild completo (`index_docs.py --rebuild`
implícito vía reindex normal: 359 archivos, 2727 secciones, sin cambios de conteo —
esperado, ya eran correctos desde la Fase 11), `build_graph.py` dos veces seguidas
(idempotente: 3 entidades, 1 CALLS, 39 CORRECTS/SUPERSEDES ambas veces, "0 entidades"
nuevas en la segunda), `export_corrections.py` (CORRECTIONS.md 39 filas,
OPEN-QUESTIONS.md 39 filas, sin regresión a 384), `search.py freshness` (al día tras
reindexar), suite completa: **50/50 tests** (eran 39 al cierre de la Fase 11; +11
nuevas: 1 negación, 3 duplicados/conflicto, 4 resolución de raíz, 1 streaming, 2
límite MCP), `ruff check` y `mypy` limpios sobre `scripts/knowledge` y
`tests/knowledge`. Verificado que ningún archivo fuera de
`scripts/knowledge`/`tests/knowledge`/`knowledge/`/`docs/CORRECTIONS.md`/
`docs/OPEN-QUESTIONS.md` fue modificado (firmware, proyectos Ghidra/REA y evidencias
originales intactos).

**Pendiente real, explícitamente NO abordado esta vuelta (Fase 12.4-12.10):**
- Extractores por esquema para GPIO, IMX210, OSAL/CAIF, REA, Ghidra (12.4): requiere
  primero inspeccionar los ~2146 JSON reales bajo `analysis/` (solo se hizo un
  muestreo puntual para confirmar que no hay campos de identidad extendida) y diseñar
  un esquema de extracción por formato — trabajo de varias sesiones, no un parche.
- Consultas técnicas multietapa (12.5): dependen de que 12.4 aporte entidades/
  relaciones reales más allá de las 3 funciones actuales; prematuro sin esos datos.
- Rediseño de benchmark con verdad de referencia estructurada (12.6): sigue
  pendiente desde la Fase 11, sin cambios esta vuelta.
- Validación real desde sesión nueva de Claude Code/Codex (12.7): no se puede
  ejecutar desde dentro de esta misma sesión; requiere confirmación del usuario desde
  fuera.
- `knowledge/CURRENT.md` + reescritura de `AGENTS.md`/`CLAUDE.md` para leer el resumen
  breve primero (12.8): no implementado.

## Fase 12.4-12.5 — inventario, extractores Ghidra/REA y consultas multietapa (2026-10-18)

**12.4.A — Inventario determinista (CERRADO):** nuevo `scripts/knowledge/inventory_json.py`
agrupa los 2146 JSON bajo `analysis/` por FIRMA ESTRUCTURAL (forma de claves+tipos, no
contenido ni nombre de archivo) en ~0.4s, sin leer ninguno con el contexto del LLM. Salida:
`knowledge/catalog/JSON-CATALOG.md` (108 familias, tabla legible) y
`json_inventory.json` (detalle completo por archivo). Hallazgo clave: el 60% de los
archivos (`analysis/elf-cache/*`, 1282) son solo metadatos ELF (exports/imports/soname),
sin relaciones verificables — registrados, sin extractor. Una familia de 61 archivos
(`coverage, function_count, targets`, xrefs Ghidra) tiene referencias reales en 52/61
pero SIN campo de hash de binario: identidad insuficiente para anclar a un binario
concreto sin riesgo de colisión de direcciones entre binarios distintos — registrada,
sin extractor, por decisión explícita (no inventar binary_sha256).

**12.4.B — Extractor Ghidra (CERRADO, impacto principal):** la familia dominante real
(`{source_sha256: str, functions: [...]}`, ~430 de los 2146 archivos, detectada por FORMA)
resultó ser pseudocódigo decompilado real con direcciones, no solo nombres: cada función
trae `pseudo_code` con llamadas `FUN_<dirección>(...)` y, en varios archivos,
`firmware_profile` (p. ej. "ILCE-6000 3.21"), `rom_base`/`raw_base`. Nuevo
`build_ghidra_function_graph()` en `build_graph.py`: crea entidades Function por
(binary_sha256, dirección) — SOLO para `status == "decompiled"` (sin inventar evidencia
donde Ghidra no la produjo) — y relaciones CALLS resolviendo `FUN_<hex>` contra el grafo
completo (no solo el archivo actual, ya que el mismo binario se analiza en decenas de
JSON temáticos distintos), descartando toda dirección con 0 o >1 candidatos. Identidad
parcial explícita: `address_space = "unknown"` (Ghidra no lo reporta aquí; nunca se
adivina ARM/Thumb). Tests: `test_ghidra_functions_family_creates_entities_and_address_based_calls`,
`test_ghidra_function_without_decompiled_status_is_not_an_entity`,
`test_ghidra_call_to_address_without_evidence_is_discarded`,
`test_ghidra_calls_resolve_across_different_owner_files_same_binary`,
`test_rerunning_ghidra_extractor_is_idempotent`.

**12.4.B — Extractor REA (CERRADO):** familia real de 5 archivos con forma
`{subject: {digest: {sha256}}, operation, normalized_result}`, en dos variantes:
`procedure_pseudo_code` (una función; nombre extraído del comentario
`/* ns::Clase::metodo() */`) y `batch_decompile` (varias funciones NOMBRADAS por archivo,
con `status`/`procedure.status` propios — solo se usan entradas `"ok"`/`"resolved"`).
Cubre, con datos reales, exactamente los dominios OSAL (`osal_snd_msg`,
`osal_reg_sync_msg_queue_cb`, `reg_sync_msg_queue_cb`) y NFC/CAIF
(`nfc_rsrc_sio_init`, `nfc_rsrc_dev_send_data`, `nfc_rsrc_dev_recv_data`) pedidos en
prioridad 2. Nuevo `build_rea_evidence_graph()`: mismas garantías que el extractor Ghidra,
más resolución de llamadas POR NOMBRE (no solo por dirección) cuando el nombre es único en
el binario — encontró una relación real: `osal_reg_sync_msg_queue_cb --CALLS-->
reg_sync_msg_queue_cb`. Tests: `test_rea_procedure_pseudo_code_shape_creates_entity`,
`test_rea_batch_decompile_shape_resolves_named_call`,
`test_rea_unresolved_batch_item_is_not_an_entity`, `test_rerunning_rea_extractor_is_idempotent`.

**Por qué NO se construyeron extractores separados para Darwin/GPIO e IMX210/IMX284
(prioridades 3-4):** se inspeccionaron sus JSON reales (`a6000-darwin-adc-phase-
notification.json`, `a6300-imx284-readout-helpers.json`, `a6300-shared-queue-
producers.json`, etc.) y comparten EXACTAMENTE la misma forma estructural que la familia
Ghidra de 12.4.B (`source_sha256` + `functions` con `pseudo_code`) — ya quedan cubiertos
por ese mismo extractor sin duplicar código. Las variantes de GPIO específicas vistas
(`darwin-dma-gpio-checkpoint.json`, `a6000-darwin-phase-table-verified.json`) son
documentos únicos (count=1 en el catálogo), sin estructura repetida que justifique un
extractor dedicado — permanecen como conocimiento solo en Markdown/texto libre.

**Refactor de deduplicación:** se extrajo `_upsert_function_entity()` (idempotencia +
conflicto de metadatos de la Fase 12.1.C) a una función compartida por los TRES
extractores (dossiers.json, Ghidra, REA), evitando triplicar esa lógica.

**12.1.A ampliado — límite de la ventana de negación corregido tras la observación del
usuario:** "analizar solo 4 palabras antes del marcador no demuestra cobertura
completa" era correcto — se cambió a buscar la negación en TODA la oración (acotada por
`.`/`;` con límite de palabra real, no un punto dentro de `old.md`) en AMBOS lados del
marcador, cubriendo también matices adversativos posteriores ("corrige, pero nunca de
forma completa"). Tests:
`test_negation_further_than_four_words_before_marker_is_still_detected`,
`test_adversative_hedge_after_marker_in_same_clause_is_not_verified`. Sigue siendo un
filtro léxico determinista, no semántico: negación doble o ironía compleja puede seguir
sin detectarse (limitación documentada, no resoluble sin inferencia de LLM, fuera del
diseño de este sistema).

**12.5 — Consultas multietapa (demostrado):** nuevo subcomando `search.py trace` +ool MCP
`trace_relations`: recorrido BFS real sobre `relations` hasta N saltos, sin ciclos, con
evidencia y procedencia por arista; si no hay relación registrada, lo dice explícitamente
en vez de inventar un salto. Demostrado contra el grafo real:
`python3 scripts/knowledge/search.py trace <eid de osal_reg_sync_msg_queue_cb> --direction out`
devuelve la cadena real `osal_reg_sync_msg_queue_cb --CALLS--> reg_sync_msg_queue_cb` con
el pseudocódigo como evidencia. Tests: `test_two_hop_chain_is_followed`,
`test_max_hops_limits_depth`, `test_disconnected_node_reports_no_relations_not_an_error`,
`test_reverse_direction_follows_incoming_edges`. **No implementado:** las consultas en
LENGUAJE NATURAL que pide 12.5 como ejemplo ("¿qué funciones participan en 0x50004?")
requerirían mapear primero esas constantes/strings a entidades — el mecanismo de
recorrido (`trace`) ya existe y es real, pero traducir una pregunta en prosa a un nodo de
partida sigue siendo manual (vía `search.py exact "0x50004"` primero para ubicar el nodo).

**Resultado medido del grafo, antes/después de 12.4 (mismo corpus real, sin binarios
reanalizados — solo extracción de evidencia YA EXISTENTE en `analysis/`):**

| | antes (Fase 11) | después (Fase 12.4) |
|---|---|---|
| Entidades Function | 3 | **1189** |
| Relaciones CALLS | 1 | **2643** (incluye 39 CORRECTS/SUPERSEDES; CALLS puro: 2603 netas) |
| Fuentes de evidencia usadas | 1 dossier | 1 dossier + ~430 JSON Ghidra + 5 JSON REA |

Verificado: `build_graph.py` ejecutado dos veces seguidas → idempotente (segunda vez:
"0 entidades" nuevas, mismo total). 65/65 tests, ruff/mypy limpios. Firmware/Ghidra/REA
originales intactos (no se reanalizó ningún binario; solo se leyeron JSON ya exportados).

**Pendiente real, explícitamente NO abordado esta vuelta:**
- 12.6 (rediseño de benchmark con verdad de referencia estructurada): AHORA SÍ tiene
  sentido abordarlo, porque el grafo ya tiene datos reales que medir (antes solo había 1
  relación CALLS). Sigue sin implementarse.
- 12.7 (validación MCP/skills desde sesión nueva Claude Code/Codex): no ejecutable desde
  esta misma sesión.
- 12.8 (`knowledge/CURRENT.md` + reescritura de `AGENTS.md`/`CLAUDE.md`): no implementado.
- Consultas multietapa en lenguaje natural (mapeo automático de constantes/direcciones
  mencionadas en prosa a nodos del grafo): no implementado, ver nota en 12.5 arriba.

## Fase 12.6 — validación del grafo ampliado + rediseño del benchmark (2026-10-18)

### 1. Validación del grafo real (muestreo estratificado, antes de tocar el benchmark)

Verificado contra la DB real (1189 entidades, 2604 relaciones CALLS antes de la corrección
siguiente):

- **Evidencia localizada en todas las CALLS:** `evidence` nunca NULL/vacío (0 filas).
- **Mismo binario origen/destino:** 0 relaciones con `binary_sha256` distinto entre src/dst
  (comprobado con JOIN sobre las 2604 relaciones, no una muestra).
- **`FUN_<hex>` no conecta espacios de direcciones distintos:** por diseño, la resolución
  siempre filtra por `binary_sha256` antes de buscar la dirección — confirmado.
- **OSAL `0x50004` y Darwin `0x4200` NO son direcciones de función:** `SELECT ... WHERE
  address IN ('0x50004','0x4200')` → 0 filas. Ambos solo existen como texto en Markdown
  (identificador de mensaje OSAL y base ROM Darwin respectivamente), nunca como entidad
  Function — correcto, el grafo no los confunde.
- **BUG REAL encontrado y corregido — relaciones duplicadas sin deduplicar:** la misma
  llamada `FUN_X -> FUN_Y` reanalizada en varios JSON de sesión (el mismo binario se
  exporta repetidamente) creaba una fila `relations` POR ARCHIVO (`relation_id` incluía
  `source_path`), violando el requisito explícito de la auditoría ("relaciones repetidas
  deduplicadas sin perder procedencia"). Medido en la DB real: 616 grupos duplicados, 840
  filas sobrantes. **Corregido:** nueva tabla `relation_sources` (mismo patrón que
  `entity_sources`) + helper `_upsert_call_relation()` — una sola fila `relations` por
  `(src,dst,type)`, con cada archivo que la respalda registrado en `relation_sources` sin
  perder procedencia. Tras la corrección: **1764 relaciones CALLS reales** (2604 fuentes de
  evidencia conservadas en `relation_sources`), 0 duplicados, idempotente (segunda
  reconstrucción: 0 entidades/0 relaciones nuevas). Test de regresión:
  `test_same_call_reported_by_two_owner_files_deduplicates_but_keeps_both_provenances`.
- **Llamadas directas vs. indirectas (vía trampolín):** Ghidra nombra el trampolín en una
  dirección como `thunk_FUN_<addr>`; antes se fusionaba silenciosamente con una llamada
  directa `FUN_<addr>(`. Ahora `_is_thunk_call()` distingue
  `ghidra:pseudo_code_call_same_binary_via_thunk` de la variante directa (comprobado que no
  hay falsos positivos por falta de `\b`: 0 coincidencias con prefijo alfanumérico tipo
  `PTR_FUN_`; sí existen `thunk_FUN_` reales, verificados caso por caso — el destino al que
  apuntan en el corpus actual no coincide con ninguna entidad conocida, por lo que ninguna
  relación quedó finalmente etiquetada `_via_thunk`: hallazgo documentado, no inventado).
  Test: `test_ghidra_call_through_thunk_is_tagged_as_indirect_not_direct`.
- **Cobertura faltante identificada, NO inventada:** la cadena EncodeStill documentada
  manualmente en `CONTEXT.md:26` (`90b248→90a810→90ad20→8fe6f8→71cf58→44f834`) no tiene
  NINGUNA de esas direcciones como entidad Function en el grafo (ese binario/rango no fue
  parte del corpus Ghidra/REA decompilado). `trace` sobre esas direcciones devuelve "Sin
  relaciones", correctamente — no se fabricó la ruta. Ver caso `multi-encodestill-chain-no-coverage`
  en el benchmark v2.

### 2-5. Benchmark rediseñado (`scripts/knowledge/benchmark_v2.py`)

- Línea base previa (`baseline-2026-10-18-pre-12.6.md`, metodología de subcadena) **conservada
  sin modificar**, tal como exigía la instrucción.
- Verdad de referencia estructurada en `knowledge/benchmarks/reference_queries_v2.json`:
  16 consultas, 8 categorías (exact/conceptual/historical/relational/multietapa/negative/
  ambiguous/partial), subsistemas Darwin, GPIO, IMX210, OSAL, EncodeStill, WriteStill. Cada
  entrada cita su fuente manual (`note`), fijada ANTES de ejecutar el benchmark y SIN pedirle
  la respuesta al propio grafo/`ask`.
- Scoring real, no subcadena: exact/conceptual/historical exigen afirmación Y ruta fuente;
  relational/multietapa exigen la arista/cadena CALLS exacta; negative exige que el método
  NO afirme el hecho fabricado; ambiguous exige >=2 fuentes distintas expuestas (no una
  respuesta falsamente única); partial exige abstención.
- 4 métodos, mismo presupuesto (`--budget 1000` para `ask`; sin recorte para `rg` a
  propósito, para medir el costo real de "sin motor"): `rg` crudo, `fts5` (`search.py
  text`/`exact`), `graph` (`search.py trace`/`graph` — SOLO cuando la consulta tiene un
  nodo/documento real; si no aplica, se omite esa fila en vez de simular con otro método
  bajo la misma etiqueta).
- **Resultado (Precision@1):** `graph` 5/6 = 0.83 — pero ese 6 son EXACTAMENTE las
  consultas relacionales/multietapa que `rg`/`fts5` no pueden resolver en absoluto (una
  arista CALLS entre dos funciones, o una cadena de 2 saltos). `fts5` y `ask` 8/17 = 0.47
  cada uno (dominan en conceptual/histórico, donde el grafo no tiene nodo aplicable). `rg`
  7/17 = 0.41, con un costo real desproporcionado: en consultas genéricas ("callback",
  "init") recorre TODO el repo sin recorte y devuelve >100M caracteres — ilustra
  exactamente el problema que motiva el proyecto, no es un error de medición.
- **Limitaciones documentadas explícitamente en el propio reporte, SIN ajustar el
  benchmark para forzar mejores números** (instrucción explícita del usuario): el criterio
  `partial` exige salida vacía, lo que no distingue "afirmé algo falso" de "listé archivos
  reales sin resolver una relación concreta" — probablemente subestima el acierto real de
  `rg`/`fts5` ahí. La memoria (RSS Δ) es una aproximación por diferencia de
  `ru_maxrss` acumulado entre procesos hijo, no una medición aislada. Los tokens son
  SIEMPRE estimados (caracteres/4): no hay tokenizador real ni reporte de uso de un agente
  real disponible en este entorno, y el reporte lo dice explícitamente para no declarar un
  ahorro de tokens real a partir de bytes.
- **Conclusión de utilidad del grafo (punto 5 de la auditoría):** las 1764 relaciones CALLS
  SÍ aportan información que ningún `grep`/FTS5 puede reconstruir — llamadas entre
  funciones decompiladas (`osal_reg_sync_msg_queue_cb -> reg_sync_msg_queue_cb`, cadenas de
  2+ saltos) no están escritas en ningún documento Markdown, solo existen en el pseudocódigo
  Ghidra/REA ya procesado. El grafo NO ayuda (y no se le pidió que ayudara) en consultas
  conceptuales/históricas que dependen de prosa de investigación, ahí FTS5/`ask` siguen
  siendo el método correcto. Esto confirma que el valor del grafo es específico a relaciones
  de llamada verificables, no un reemplazo general de la búsqueda textual.

## Fase 12.7 — validación MCP/skills (lo verificable desde esta sesión)

- `.mcp.json` (Claude Code): rutas absolutas al Python del venv del proyecto; arranque real
  `python3 scripts/knowledge/mcp_server.py < /dev/null` desde `/tmp` (fuera del repo) sale
  sin error — confirma que el fix de resolución de raíz (Fase 12.3) también cubre el
  arranque MCP desde un cwd ajeno al proyecto.
- `.claude/skills/*/SKILL.md` (4 skills): frontmatter `name`/`description` presente y
  específico en las 4; directorios reales, no symlinks rotos; sin implementaciones
  duplicadas.
- `test_mcp_server.py`: protocolo real en memoria (`list_tools`, `call_tool`) — 11 tools
  descubiertas, llamadas reales devuelven datos del repo, entrada inválida no tira el
  servidor.
- **Hallazgo re-confirmado (no nuevo, ya documentado en la Fase 6): Codex sigue sin tener
  registrado el servidor MCP.** `~/.codex/config.toml` no tiene
  `[mcp_servers.sony-a6000-knowledge]` (solo `trust_level` para este proyecto); el snippet
  exacto para añadirlo está en la Fase 6 de este documento. No se editó el archivo global
  sin autorización explícita.
- **Única limitación real, documentada y no resuelta desde aquí:** el descubrimiento de
  skills/MCP por un cliente Claude Code o Codex RECIÉN iniciado (sesión nueva, fuera de este
  proceso) no es verificable desde dentro de esta misma sesión — requiere que el usuario lo
  confirme.

## Fase 12.8 — optimización de inicio

- `knowledge/CURRENT.md` (nuevo): resumen operativo de ~2.7 KB (2678 bytes) vs. 43962 bytes
  de `PROGRESS.md` completo — reducción del 94% en lo que una sesión nueva necesita leer
  primero. `CLAUDE.md`/`AGENTS.md` actualizados para leer `CURRENT.md` primero y recurrir a
  `PROGRESS.md` solo si se necesita el detalle histórico completo.

## Verificación final de esta vuelta

67/67 tests (eran 65; +2 por los bugs encontrados en 12.6), ruff/mypy limpios,
`build_graph.py` idempotente (dos reconstrucciones seguidas sobre la DB real: 0
entidades/0 relaciones nuevas en la segunda). Firmware/Ghidra/REA/evidencias originales
intactos — solo se editó `scripts/knowledge/`, `tests/knowledge/`, `knowledge/`,
`CLAUDE.md`, `AGENTS.md`.

## Fase 12.9 — registro real del servidor MCP en Codex (2026-10-18, autorizado por el usuario)

Usuario autorizó explícitamente editar `~/.codex/config.toml` (fuera del scope normal del
proyecto) con condiciones concretas (respaldo previo, no tocar otros servidores/credenciales,
usar el Python del `.venv`, validar sintaxis, confirmar con `codex mcp list`, probar con una
sesión real, verificar skills, no modificar firmware/evidencias, restaurar respaldo si falla).

1. **Respaldo:** `~/.codex/config.toml.bak-20261018T114752` (copia íntegra previa a cualquier
   edición).
2. **Estado previo confirmado:** no existía ningún bloque `[mcp_servers.sony-a6000-knowledge]`
   (grep antes de editar); no había duplicado posible.
3. **Cambio aplicado:** añadido al final del archivo, sin tocar ningún otro
   `[mcp_servers.*]`/`[projects.*]`/credencial existente:
   ```toml
   [mcp_servers.sony-a6000-knowledge]
   command = "/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/.venv/bin/python3"
   args = ["/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter/scripts/knowledge/mcp_server.py"]
   startup_timeout_sec = 30
   ```
   Se usó la ruta del `.venv` (no su `realpath`, que resuelve a `/usr/bin/python3.14` sin el
   `sys.path`/paquetes del venv — `mcp_server.py` depende del paquete `mcp` instalado ahí).
4. **Validación de sintaxis:** `tomllib.load()` sobre el archivo completo, sin errores.
5. **`codex mcp list`:** `sony-a6000-knowledge` aparece listado, estado `enabled`, comando y
   args correctos; el resto de servidores (`rea`, `context-mode`, `codex_app`, etc.) intactos.
6. **Sesión Codex real** (`codex exec --skip-git-repo-check`, no interactiva — el proyecto no
   es un repositorio git por diseño del proyecto, confirmado en entorno; se usó el flag de
   solo-lectura para permitir la ejecución, no para saltar ninguna verificación de seguridad):
   - Descubrió exactamente **11 tools**: `check_index_freshness`, `find_corrections`,
     `find_symbol`, `get_current_state`, `get_document_section`, `get_open_questions`,
     `query_graph`, `search_documents`, `search_exact`, `search_hybrid`, `trace_relations`.
   - `search_exact("0x50004")` y `get_current_state()` devolvieron datos reales del repo
     (README.md:93, docs/OPEN-QUESTIONS.md, docs/STATE.md), sin fabricación.
   - Segunda sesión: `search_exact("P4D")` localizó
     `docs/capture/fm3-gpio-shutter-mapping.md:16` (P4D/PDOR4 bit13/`0x42668234` →
     1ST_CURTAIN_MG); `query_graph(doc=..., rel_type="CALLS")` devolvió "Sin resultados" y
     Codex lo reportó como abstención explícita, **sin inventar una relación CALLS** para
     completar la respuesta — comportamiento correcto, no un fallo a corregir.
7. **Skills compartidas:** las 4 skills de `.agents/skills/` (`contradiction-audit`,
   `knowledge-maintenance`, `knowledge-navigation`, `session-checkpoint`) son enlaces
   simbólicos directos a `.claude/skills/<misma-skill>` — correspondencia 1:1 confirmada por
   `readlink`, no copias que puedan desincronizarse.
8. **Sin errores que corregir:** no hubo fallo de integración; no fue necesario restaurar el
   respaldo. Firmware/Ghidra/REA/evidencias no se tocaron (ningún archivo fuera de
   `~/.codex/config.toml` + `knowledge/CURRENT.md` + esta sección).

**Limitación real no resuelta:** lo anterior usa `codex exec` (modo no interactivo). El
descubrimiento de tools/skills en una sesión **interactiva** normal del cliente Codex (la UI
de chat, no `exec`) sigue sin confirmación directa desde dentro de este proceso — sería
necesario que el usuario lo abra y lo confirme.

## Fase 12.10 — prueba de integración extremo a extremo (2026-10-18)

Objetivo: validar el ciclo completo grafo→checkpoint→recuperación cruzada Claude Code↔Codex
con medición de contexto, sin modificar firmware ni evidencias.

1. **Relación CALLS positiva con evidencia exacta:** `trace 6dec9cf1a9f52b76 --direction out
   --type CALLS` → `SCALARDAEMON::CommandProcessorCameraTakePicture::AsyncProcessor::execute()`
   `--CALLS-->` `SCALARDAEMON::SystemEventIssuerCamera::captureStart()`, estado `PARCIAL`,
   fuente `analysis/functions/dossiers.json`, evidencia "via PLT at callsite 0x108144".
   **Relación inexistente no inventada:** `trace d8c6c582d352e037 --direction out --type
   CORRECTS` → "Sin relaciones... no es evidencia de que no exista relación" (abstención
   explícita, correcta).
2. **Checkpoint Claude Code → Codex:** se escribió un marcador temporal identificable
   (`CKPT-CC-20261018T150425Z`) en `docs/STATE.md` (fuente real de `get_current_state`).
   Una sesión nueva `codex exec --skip-git-repo-check`, instruida a usar SOLO tools MCP (sin
   leer archivos a mano), citó el id exacto vía `get_current_state`, localizó la evidencia
   original de la afirmación GPIO citada en el checkpoint con `search_exact` en
   `docs/capture/fm3-gpio-shutter-mapping.md:16` y `:24`, y distinguió correctamente ese
   hallazgo **VERIFICADO** de una pregunta real **NO_VERIFICADO** (SilentShutter → final de
   exposición, `get_open_questions`, fuente `docs/capture/README.md:40`) — no las confundió.
3. **Checkpoint Codex → Claude Code (sentido inverso):** una sesión nueva `codex exec`
   escribió, con una edición de archivo real (no solo texto de respuesta), el marcador
   `CKPT-CODEX-20261018T151044Z` al final de `docs/STATE.md`. Desde Claude Code se invocó
   la función `get_current_state` real del servidor MCP (misma lógica que expone la tool;
   la tool en sí aparece como "Pending approval" en `claude mcp list` para esta sesión no
   interactiva — ver limitación abajo) y se recuperó el id exacto sin leer `CONTEXT.md` ni
   `PROGRESS.md`.
4. **Medición de contexto por recuperación:**

   | Recuperación | Caracteres | Tokens estimados (chars/4) | Tokens reales |
   |---|---:|---:|---:|
   | Codex recupera CKPT-CC + evidencia + pregunta abierta (sesión completa) | — | — | **29 247** (reportado por `codex exec`) |
   | Codex escribe CKPT-CODEX (sesión completa) | — | — | **16 805** (reportado por `codex exec`) |
   | Claude Code recupera CKPT-CODEX vía `get_current_state` | **4024** | **1006** | sin cifra real disponible (este entorno no expone tokens reales por llamada de Claude Code) |

   Los tokens reales de Codex son de la **sesión `exec` completa** (razonamiento + varias
   llamadas a tools), no solo de `get_current_state`; no son comparables 1:1 con los 1006
   estimados de una sola llamada de Claude Code — se reportan ambos sin forzar una
   equivalencia que no existe.
5. **Codex interactivo:** no verificable desde este proceso (mismo límite que Fase 12.9);
   no se declara fallo del sistema por esto.
6. **Limpieza:** ambos marcadores `CKPT-CC-*`/`CKPT-CODEX-*` se eliminaron de
   `docs/STATE.md` al terminar la prueba; no se tocó ningún otro contenido del archivo ni
   del historial real.
7. **Hallazgo nuevo, no corregido aún (no bloquea la prueba):** el servidor MCP
   `sony-a6000-knowledge` aparece como **"⏸ Pending approval"** en `claude mcp list` para
   esta sesión de Claude Code — requiere que el usuario lo apruebe desde una sesión
   interactiva (`claude`) para que las tools MCP (no solo la CLI equivalente) estén
   disponibles aquí. La prueba de este apartado usó la función Python real del servidor
   (idéntica lógica, mismo archivo fuente) como sustituto exacto mientras tanto.

## S33 — origen YC por handles Rendezvous (18-10-2026)

AllocShare `0x4390366c/0x43902df8` completo; 26 llamadas a `0x4379b44c`
desde 12 funciones, 13 inputs locales borrados por `0x43b03a5e` (0x104 bytes).
`+0x10` apunta a handles del trabajo; helper `0x43814ea0` puede activar
`+0xc8` y escribir `+0xd4=P+0xbc` en tres productores, propagado por copia.
APL llega a traducción de prefijos y configuración MMIO en bancos
`0xf3850400/0xf3950400/0xf3a50400`; no se identificó fin DMA físico.
Rastreados AllocRendezvous y despacho Image de VD_Sequence; segunda publicación
desde HS_Sequence `0x43790b68`. El backend DMM está importado y su entrada
inicial contiene cero: no se inventa destino ni dirección raster.
Auditor S33 PASS (SHA, 29 llamadas totales, inputs y proyecto idéntico).
Ruff: nueve avisos anteriores ajenos; auditor sin avisos nuevos; mypy PASS.
Sin cámara, instalaciones, commit (no hay `.git`) ni push.
[Informe S33](../docs/capture/s33-yc-rendezvous-producer.md).

## S35 — Objetos DFE y frontera estática APL/IRQ (18-10-2026)

Resueltos los cuatro objetos a Ofmt/Ifmt por constructores y RTTI, así como
sus vtables y +8 de OfSgc/OutSgc/RcvSgc/LnkSgc. Lectura/RMW de bit 0 en
SGC `0xfc0a1210/1310/1610/1710` y +0x1000 para unidad 1. No lectura/ack
APL recuperado ni cadena a EC/LM. Barrido: 49 instrucciones con inmediatos
objetivo y 479 coincidencias crudas; bit `0x00200000` sin semántica física
demostrada en `fact`. Sus usos en enable/disable IRQ no identifican esa causa.
**FRONTERA ESTATICA AGOTADA para esta vía concreta**, sin afirmar
imposibilidad estática universal. Hace falta routing/semántica hardware o
traza pasiva APL/DFE/IRQ/VD con identidad de handle/frame, sin flashear.
Siguiente incógnita: proveedor DMM `0x43561524`, entrada `tabla+0x2e4`,
productor Rendezvous y consumidor YC. No investigada en esta tanda.
[Informe S35](../docs/capture/s35-dfe-objects-static-frontier.md), exports
`analysis/ghidra/s35-objects*.{json,c}` y `s35-causes-scan.json`.
SHA verificado antes de exportar; proyecto `-readOnly -noanalysis` preservado.
Auditor primero falla por evidencia ausente, luego PASS. Sin cámara,
ejecución de firmware, instalaciones, flasheo ni push; sin `.git`, sin commit.
Tests de conocimiento: 67 PASS. Ruff auditor y mypy src/auditor PASS;
nueve avisos Ruff previos en tests ajenos. Mantenimiento de índice/grafo y
derivados ejecutado en cinco pasos, con totales estables.

## Pendiente real (no resuelto esta vuelta, con causa documentada)

- **Vigente S40 — contexto de modo:** API4000/4036/3023 y staging43edf684
  resueltos; faltan productores de snapshots alternativos y semántica exacta
  de bytes. No equiparar configuración software con exposición, habilitación
  de lectura o generación de cuadro IMX210. Cobertura de alias PARCIAL;
  no frontera estática agotada. Detalle al final en S40.

- **Actualización S37:** el definidor C++ ya es `libmprctrl.so`; no repetir su
  búsqueda. Getters DmmAccessPLA leen palabras de respuesta, sin conversión ni
  uso raster local que determine físico/lógico. AllocDmmMemory produce paquetes;
  el servicio OSAL 0x61003c entrega los pares. Su payload 0x18 comparte campos
  con S33, pero no su envoltura ni validaciones: identidad del slot av-cam y
  enlace a P+0x18c/+0x194/+0xbc y APL siguen NO_VERIFICADO. El enlace nominal
  de DmmCloseAndFree S30 sí queda verificado por símbolo, PLT/relocación y
  DT_NEEDED. [Informe S37](../docs/capture/s37-libmprctrl-dmm-extents.md).
- **S36 — proveedor DMM ausente de libInfraScalarMpr:** AllocDmmMemory y
  FreeDmmMemory son UND. El `void**` de SharedMemory viene de SysV `shmat`,
  con copia still demostrada; no cierra identidad con YC/Rendezvous ni
  cmd 2/id 0x55/longitud 0x70 del slot av-cam.
- Confirmación de descubrimiento MCP/skills desde una sesión **interactiva** (no `exec`) de
  Claude Code o Codex verdaderamente nueva: requiere al usuario, fuera de esta sesión.
- Aprobación del servidor MCP `sony-a6000-knowledge` en esta sesión de Claude Code (aparece
  "Pending approval"): requiere al usuario en una sesión interactiva de `claude`.
- Mapeo de lenguaje natural a nodo de `trace` (ver Fase 12.5): sigue siendo manual.
- La cadena EncodeStill documentada en `CONTEXT.md:26` no tiene cobertura en el grafo
  (direcciones fuera del corpus Ghidra/REA decompilado actual); analizarla requeriría
  decompilar ese rango, no es un bug del extractor.

## Fase 12.11 — retorno a la investigación principal: EFCS/SilentShutter/CAMERA_MAIN_SYNC (2026-10-18)

Instrucción del usuario: dar por cerrada la ampliación del sistema de conocimiento
y retomar la ingeniería inversa del shutter completamente electrónico, usando
Codex + MCP + índices existentes, sin repetir investigaciones cerradas.

1. **SetRead IMX210 descartada como consumidor de Silent.** `0x436d7e08` decompilada
   íntegra vía `codex exec` (proyecto `analysis/ghidra/silent-liro.gpr`, solo lectura):
   rechaza estado 0x11, calcula parámetros de registros sombra (`0x43ad9262` x4),
   escribe `0x4401c73a`, llama `GetImagerTemperature`; ningún tramo lee Silent+0x238/
   +0x210/+0x280 ni el switch de configuración 0x438b8902 (casos 1→11,2→8,4→12,8→13).
   No produce ni referencia buffer YC/DMA. Exports: `analysis/ghidra/
   imx210-setread-config-static-20261018.json` y 5 más con mismo prefijo. Añadido a
   `docs/capture/silent-imager-consumers.md`.
2. **Corrección de `CONTEXT.md`:** la sección "Próximo paso de investigación vigente"
   seguía pidiendo localizar "el alta/callback de 0x50004", pese a que S28 (17-10-2026)
   ya lo había cerrado (receptor InfraImaging en `0x4379744c`). Se corrigió para no
   reabrir trabajo cerrado; queda solo el productor sensor/DMA como pendiente real.
3. **Descartado un driver de kernel separado para el sensor.** Se listaron los ~90
   módulos `.ko` de las tres variantes de firmware disponibles (a6000/a6300/a7s) y se
   buscaron cadenas `IMX210`/`exposure`/`SilentShutter`/`EFCS`/`C_ImagerCtrl` en cada
   uno: cero coincidencias. `dmm.ko` (gestor de buffers, ya analizado en S16-S18) y
   `mcmn_drv.ko` (resultó ser GPIO de tarjeta MMC/ROM-write-protect, no "MechaCommon"
   como se había hipotetizado) se revisaron explícitamente y se descartaron. Esto
   refuerza que todo el control del sensor vive en `av-cam.bin` y las bibliotecas de
   servicio ya analizadas, no en un driver V4L2 independiente.
4. **Hallazgo nuevo: subsistema `CAMERA_MAIN_SYNC`/`DFECore`** (`docs/capture/
   s31-camera-main-sync-strings.md`). Búsqueda de cadenas en `av-cam.bin` (no
   decompilación) reveló un motor de temporización VD del sensor con logs
   (`VD_Drive`, `EC_VD_Post`, `VD_Post`, `No Read. cause:no expose/1st expose`,
   `camIntHandler0/1`) que ninguna sesión S16–S30 había tocado: todas se centraron en
   la capa de servicio (`libObj.so`/`libBizFw.so`/`dataflowInfraFramework.so`) en vez
   de este motor interno de `av-cam.bin`. Decompiladas 8 funciones vía `codex exec`
   (30 funciones totales exportadas, headless `-readOnly -noanalysis`, SHA-256
   verificado):

   | Función | Dirección | Rol verificado |
   |---|---|---|
   | `VD_Pre` | `0x43792a0c` | Prepara estado/callbacks, señala evento `0x1a/0x40` |
   | `VD_Sequence` | `0x4379155c` | Espera `0x40`, ejecuta secuencia, señala `0x100` |
   | `VD_Post` | `0x4379210c` | Espera `0x100`, encola `VD_Drive` |
   | `VD_Drive` | `0x4378f410` | Espera `0x1a/0x80`, comprueba VD actual, ejecuta trabajos pendientes |
   | `EC_VD_Post` | `0x4378f848` | Evita reprocesar un VD ya hecho; guarda su número en `0x43e992dc` |
   | `int_LM_Send1st_Handler` | `0x43792750` | Compara `0x43e992dc` con el VD actual; reprograma o marca EC pendiente |
   | `camIntHandler0` | `0x436cf954` | Acumula causas de interrupción (máscara `0x03380000`), despacha 4 slots de callback |
   | `camIntHandler1` | `0x436cf780` | Cuenta llamadas, log cada 1000 |

   Secuencia real: **`VD_Pre` →evento 0x40→ `VD_Sequence` →evento 0x100→ `VD_Post`
   →cola→ `VD_Drive`**, asíncrona y condicionada (no una llamada lineal). La variante
   EC llega por `0x437926fc` o el callback `0x43791454`, condicionado al predicado
   `0x4378e90c`.

   **VERIFICADO — acceso MMIO real:** `0x436ccd9c→0x43ad6006` escribe registros
   físicos entre `0xf3c30110` y `0xf3c3015c`. Es la primera evidencia estática de
   escritura directa a hardware mapeado en memoria encontrada en esta línea de
   investigación (su efecto físico no se ha observado: no hay cámara conectada).

   **PARCIAL — candidato a productor YC:** `VD_Sequence→0x43796954→0x4379bb90`
   (diagnóstico `SyncYCout.cpp`) envía parámetros por
   `0x43797afc/0x7b10/0x7b24/0x7b38→0x435a9928`; aquí vive la cadena "YC out window
   overflow". Es el candidato más cercano al productor sensor/DMA buscado desde S22/S30
   (`docs/capture/s22-sensor-to-yc.md`, `s30-pipelines-capture-encode.md`), pero no
   entrega dirección de píxeles, plano, pitch ni finalización DMA.

   **NO_VERIFICADO:** si `VD_Drive`/`VD_Post` marcan fin de lectura/DMA o solo
   temporización — recorren listas de trabajo con llamadas indirectas vía
   `0x43ad6034` cuyos destinos concretos no se resolvieron. Dato que falta y
   procedimiento no destructivo: resolver estáticamente esos destinos (siguiente paso
   recomendado) y, para comportamiento físico, una captura pasiva correlacionada de
   VD/lectura/interrupciones en hardware real sin flashear.

   Exports: `analysis/ghidra/camera-main-sync-final-decompilation.{c,json}`,
   `camera-main-sync-final-evidence.json`, `camera-main-sync-string-xrefs.json`,
   `camera-main-sync-entry-xrefs.json`.

Mantenimiento ejecutado tras ambas ediciones de documentación (`index_docs.py` →
`build_graph.py` → `export_corrections.py` → `index_docs.py` → `build_graph.py`):
total estable en 1226 entidades / 1977 relaciones en el paso de confirmación.

## S34 — APL/DMA, VD e interrupciones (18-10-2026)

Tres BL al helper `0x43814ea0` contrastados con blob/listing; direcciones,
registros MMIO y kick 0/1 ocurren síncronamente en el productor Image.
Ruta VD_Sequence demostrada; selección condicional de categoría HS para dos
productores, sin prueba de factibilidad conjunta de todos los predicados.
Sin llamador directo desde Post/Drive. El evento Drive `0x80` puede preceder
Sequence o venir de timer 4: no acredita fin DMA ni identifica cuadro físico.
Registrador `0x436cfae0`, cuatro slots y conversor `0x43ad68e0` resueltos;
falta correspondencia banco APL→estado/causa IRQ→callback→handle/VD→EC/LM.
Baseline propio anterior a apertura y hashes persistentes idénticos; 116
consultas exportadas (incluyen datos/interiores, no 116 funciones distintas).
Auditor primero falló por evidencia ausente; después PASS.
[Informe S34](../docs/capture/s34-apl-dma-vd-interrupts.md).
Ruff del auditor y mypy src/auditor PASS; nueve avisos Ruff previos en tests
ajenos sin tocar. Tests de conocimiento: 67 PASS. Mantenimiento en cinco pasos,
grafo 1419 entidades / 2725 relaciones antes de reindexar derivados.
Sin cámara/ejecución/flasheo/instalaciones/push. Sin `.git`, sin commit.

## Pendiente real (no resuelto esta vuelta, con causa documentada)

- **Cierre físico APL/VD:** S35 agota la vía de los cuatro objetos DFE:
  tipos y métodos resueltos, bancos SGC distintos de APL. Falta routing/estado
  hardware, semántica del bit `0x00200000` en `fact`, callback con handle/VD y
  latch frente a VD físico. Requiere especificación o traza pasiva correlacionada;
  no repetir resolución de vtables como pendiente. Ciclo físico NO_VERIFICADO.
- **Productor físico sensor/DMA del YC:** S33 cierra la construcción de input y
  su referencia Rendezvous, no quién llena los píxeles. Falta resolver proveedor
  importado DMM (`base+0x14`, entrada `+0x2e4`), quien satisface claves de
  `P+0x18c/+0x194` y del secundario `P+0xbc`, extents/pitch/formato y señal
  física de fin de escritura.
- Confirmación de descubrimiento MCP/skills desde una sesión interactiva nueva
  (no `exec`): requiere al usuario, fuera de esta sesión.
- Aprobación del servidor MCP `sony-a6000-knowledge` en esta sesión de Claude Code
  (aparece "Pending approval"): requiere al usuario en sesión interactiva de `claude`.
- Mapeo de lenguaje natural a nodo de `trace`: sigue siendo manual.
- La cadena EncodeStill documentada en `CONTEXT.md:26` no tiene cobertura en el grafo;
  decompilarla no es un bug del extractor.

## S58 — continuación de Claude y cierre offline (20-10-2026)

- Recuperados productores AE y emulación A7S bajo condiciones explícitas; seis informes en `docs/capture/s58-*.md`, 24 evidencias y 12 hipótesis. Se conservan exportaciones REA heredadas y firmware original.
- Correcciones S57: identidad SetExposure/SetRead, matriz IMX235; auditoría adicional corrige parser que omitía DEV83 y equivalencia incondicional de fórmulas productor/host. Consumidor de petición AGC `0x436f459c` probado en cinco modos.
- Verificación: 23 tests S58 y 60 S56/S57; campañas 600/600 y 300/300; ruff F/E9 y mypy con imports omitidos limpios en 25 archivos. Integridad: firmware 5/5, silent-liro 9/9, Ghidra 1328/1328. Detalle y comandos en [conclusiones](../docs/capture/s58-conclusions.md).
- Mantenimiento de índice/grafo/derivados ejecutado; correcciones A7S documentadas con enlaces explícitos. S51 A=NO/B=NO/C=NO; sin hardware, instalaciones ni push. Constructor A7S y semántica eléctrica permanecen fuera de cobertura.
- Validación de conocimiento: 61 tests ajenos al archivo MCP pasan. `test_mcp_server.py` se detiene por timeout de 15 s en `test_call_tool_get_current_state_reads_real_file` (espera asyncio/AnyIO); la suite completa se interrumpió tras 53 tests. No se modificó esa infraestructura; esta limitación queda abierta y el índice se comprobó mediante CLI.

## Próximo paso exacto

**Vigente tras S58 (20-10-2026):** recuperar el escritor del bloque `0x437876dc()+0xdd0` que `0x437aa65c` copia como 12 u16, y sus restricciones por modo hasta M/Tv/clk. Reutilizar `analysis/s58/rea-out/` y `analysis/s58/reproduce.py`; no repetir matriz de S57 ni apertura REA en frío sin necesidad. Inicialización real A7S y efecto eléctrico de integración siguen pendientes. Las instrucciones S40 de abajo son históricas, no el próximo paso vigente.

0. **Vigente después de S40:** seguir productores originales de mensajes
   case1/10 de438069f0 (43806a80/43806d50 toman mensaje+4/+8;
   43804cc8 toma staging43edf684), conservando offsets de snapshot+8
   frente al objeto contenedor. Fuentes API4000/4036/3023 del staging
   +24/+48/+458 ya demostradas. Seguir bloque+450..+458 hacia selectores
   IMX210 con identidad de objeto/campo/llamada; no inferir SetExposure,
   read-enable ni generación de cuadro desde copia de configuración.
   Alias y nombres de opción/FPS/píxel PARCIAL/NO_VERIFICADO.
   No reabrir AllocShare ni discriminación APL; no agotamiento universal.

0. **Después de S38 (antecedente):** resolver enum de formato PARCIAL S33:
   input+38←P+1b4←context[2]+28 y conversor 43814d24 hasta consumidores
   APL de formato, stride y tamaño. Asignar nombres solo con evidencia
   inequívoca. La vía ELF del slot DMM +2e4 en av-cam quedó agotada;
   receptor y productor YC siguen NO_VERIFICADO. Los pasos siguientes
   S37/S36/S35 son antecedentes, no prioridad vigente.

0. **Después de S37 (vigente):** localizar receptor OSAL **0x61003c** y
   resolver proveedor `av-cam base+0x14/+0x2e4`; seguir quién escribe los pares
   `reply+0x10/+0x14`, contrastar adaptadores/envolturas y una misma clave/ID
   hasta Rendezvous y YC/APL. Probar dominio y unidades con consumidor o mapeo;
   después pitch/formato, caché/reciclaje y fin DMA. La lectura de un campo
   llamado Adrs no sustituye esas pruebas. Los pasos S36/S35 debajo se
   conservan como historia; la búsqueda del definidor S36 ya está resuelta.

0. **Después de S36:** localizar definidor de
   `_ZN9DmmAccess14AllocDmmMemoryEiPt` y `_ZN9DmmAccess13FreeDmmMemoryEi`;
   verificar símbolo definido y seguir asignación/mapeo/mensajes. Resolver el
   slot av-cam independientemente antes de afirmar backend común. No confundir
   SharedMemory SysV con DMM. Ver [S36](../docs/capture/s36-libinfra-scalar-mpr-memory.md).

1. **Después de S35:** resolver proveedor DMM importado `0x43561524`, tabla
   `base+0x14`, entrada `+0x2e4`; seguir productor que satisface Rendezvous
   `P+0x18c/+0x194` y secundario `P+0xbc`, hasta lector YC real con handle,
   extents/pitch/formato y reciclaje. No investigado en S35. Ver
   [S35](../docs/capture/s35-dfe-objects-static-frontier.md).
   Para frontera física agotada: documentación hardware o traza pasiva
   correlacionada APL/IRQ/VD/handle en cámara sin flashear. No reabrir los
   26 llamadores S33 ni atribuir fin DMA al evento Drive `0x80`.
2. No ampliar más la arquitectura del sistema de conocimiento salvo defecto importante
   (instrucción explícita del usuario, Fase 12.10/12.11).
3. Si se prioriza: mapeo de constantes/direcciones en lenguaje natural a nodos de `trace`.
4. Si se prioriza, embeddings locales SOLO si un benchmark futuro demuestra mejora real
   sobre BM25+grafo (el benchmark v2 actual no lo justifica).

## S37 — definidor DMM y frontera de extents (18-10-2026)

SHA original/copia libmprctrl verificado antes de nm. Proyecto Ghidra nuevo,
copia 0444, cero dependencias y export final readOnly; silent-liro intacto.
1066 entradas exportadas con pseudocódigo/listing, incluyendo PLT y externos.
AllocDmmMemory/GetDmmExtList, cuerpo allocate/open/share, getters PLA y
close/free completos. Corregida atribución inicial de los getters a DmmAccess:
los mangled son DmmAccessPLA. Modo12 pide tipo 0x8125b/subarea3, no bytes.
Layout de paquetes distinto de respuesta raw. Dirección/tamaño son palabras
externas, no valores físicos demostrados. OSAL 0x61003c/payload0x18;
campos compatibles con S33, envoltura y validación diferentes. Slot av-cam
sin resolver. PLT libObj 0xdc180→JUMP_SLOT 0x102d024 importa el mismo símbolo
definido aquí, con dependencia directa; runtime no observado.
Auditor: primer fallo por findings ausente, luego PASS. Sin .git, sin commit.
PT_LOAD nativo confirma endpoint/tabla mode12; relocación y dependencia S30
auditadas. Ruff/mypy auditor y mypy src PASS; Ruff src/tests conserva nueve
avisos previos en tests ajenos. Conocimiento 67 PASS; mantenimiento en cinco
pasos estable en 1455 entidades / 2763 relaciones.
Sin firmware ejecutado/cámara/flasheo/instalaciones/push. Ver informe S37.

## S38 — frontera DMM/OSAL del blob (18-10-2026)

SHA original y memoria Ghidra coinciden. Solo silent-liro readOnly/noanalysis;
script sin mutaciones de programa, manifiestos .gpr/.rep intactos.
85 literales 61003c, 16 sin referencias; pool compartido y clientes DMM
exportados con helpers completos. Ningún servidor/alta recuperado: las
lagunas de referencias impiden afirmar ausencia universal.
readelf -d/-r y nm fallan: ORIL/LIRO, no ELF. PIC→440205c0→base→tabla
435410b4; slot 2e4 en 43541398 cero en archivo. **FRONTERA ESTATICA
AGOTADA** para resolución ELF/valor externo de ese slot en este blob.

**Pendiente real:** servidor/escritor de reply+10/+14 y binding externo
siguen sin identidad; ninguna misma clave/handle une extents a P/APL.
**Próximo paso exacto:** enum de formato PARCIAL S33,
input+38←P+1b4←context[2]+28 y 43814d24 hasta bits APL, stride y tamaño.
No atribuir formato por geometría ni fin DMA por evento Drive.
Ver [S38](../docs/capture/s38-dmm-osal-static-frontier.md), exports
`analysis/ghidra/s38-*.json/.c` y auditor con tabla stdout clasificada.
Auditor primero falló por consulta del export incorrecto, luego por findings
ausente; corregidos. Sin .git, cambios sin commit ni push.

Validación final S38: auditor PASS; Ruff/mypy auditor y mypy src PASS;
Ruff src/tests mantiene nueve avisos previos. Conocimiento 67 PASS.
Mantenimiento en cinco pasos estable: 1455 entidades / 2768 relaciones.

## S39 — enum de formato y discriminador APL (18-10-2026)

Ocho exports JSON/pseudocódigo s39-, SHA y memoria cotejados antes de cada
export. Proyecto silent-liro readOnly/noanalysis; ningún cambio de funciones,
contexto ni permisos de memoria. Manifiestos S38 coinciden antes/después.
Tres llamadores43814d24 pasan config+0c a4387a1fc/4387a758; actual43ef71a4,
anterior43ef71a0.4387a6c4 convierte grupos0/1/2/3→0/1/2/4 y436bec28
solo compara/guarda caché43e77ccc+unidad*4. Cambio→43acb7be→invalidación
y reset de referencias/perfiles; sin enlace demostrado a bits MMIO/pitch.
P+1b4 e input+38 usan índices distintos: conservar remapeo S33 separado.
Strings YUV/RAW/RTTI vecinas no establecen tabla de nombres por índice.
43ae8d56 confirma root43e9b548/context43e99208/context[2]=43e9baec;
VD_Pre43792a0c escribe43e9bb14 en437934b4/4379357c/437935aa/437935ea:
copia de contexto0+24, remapeo de+48/+458, o cero condicional.

**Pendiente real:** nombres de píxel, pitch, fuente tipada de opciones/FPS;
alias/copias masivas no resueltos exhaustivamente. Ningún cierre físico nuevo.
**Próximo paso exacto:** origen de context[0]+24/+48/+458 hasta solicitud o
tabla tipada y cálculo real de pitch por separado. Prioridad global S31–S39:
misma clave/handle/VD desde productor físico hasta fin DMA y cierre de
integración. No reabrir AllocShare ni tomar detección de cambio como registro.
No se declara rama estática universalmente agotada.
Ver [S39](../docs/capture/s39-image-format-apl.md),
`analysis/ghidra/s39-findings.json` y auditor con tabla stdout clasificada.
Auditor primero falla por findings ausente; luego verifica hashes, PIC,
TBB, consumidores y manifiestos. No hay .git: cambios sin commit ni push.

Validación S39: auditor PASS; Ruff y mypy del auditor PASS; mypy src PASS.
Ruff src/tests conserva los nueve avisos previos en cuatro tests sin tocar.
Conocimiento: 67 PASS. Mantenimiento de cinco pasos: 1455 entidades /
2771 relaciones, comprobación de estabilidad al cierre. Proyecto y binario
intactos; sin firmware ejecutado, cámara, flasheo, instalaciones ni push.

## S40 — origen del contexto de modo y frontera IMX210 (18-10-2026)

Solo silent-liro.gpr, av-cam.bin, -readOnly -noanalysis; SHA original y bytes
cargados cotejados. Manifiestos persistentes .gpr/.rep idénticos antes/después.
Sin releer S31–S38 ni reabrir AllocShare/AllocRendezvous/APL como hardware.

**VERIFICADO:** 43804cdc copia560B desde staging43edf684 a raíz43e9b548;
43804c82/43804d12→43b00d06 copian snapshotobjeto+8. Contiene los tres
campos+24/+48/+458; no basta consultar sus xrefs absolutas. Escritores
staging:438040bc←u8(solicitud+0a),comando4000;438040e8←cero condicional;
43803958←u8(solicitud+09),comando4036;43809378←u8(solicitud+0e),
comando3023 si solicitud+8!=0.437935ae fuerza raíz+48=0 localmente.
43b00cd0 alimenta snapshot+8 por copia560B;43b00bba lo inicializa a cero.
Tabla despacho43fff30c,220filas×12B: u16comando+0,punteroThumb+4,
byteflag+8; bytes restantes sin significado inventado. Filas4000/4036
resueltas a43804059/4380394d. Selector43ca3c21={1,1,0,1}, índice
raíz+450-1, condicionado por bit7(context[2]+269). Layout3023:
+450:u32←u8+8,+454:u16←u16+a,+456:u16←u16+c,+458:u32←u8+e.

**PARCIAL:** exhaustividad frente a alias/bases desplazadas/stores múltiples;
productores de cada snapshot alternativo. Barrido Ghidra215candidatos
450/454/458 y8977al añadir24/48, con función y xrefs por instrucción.
Otros objetos con+458 no son escritores de raíz por coincidencia numérica.
**INFERENCIA:** bloque alternativo con geometría (fallback320×240).
**NO_VERIFICADO:** opción de menú/FPS/nombre de píxel, enlace SetMode o
SetExposure, habilitación física de lectura y generación de cuadro.
La rama no está agotada estáticamente; no se sustituye por búsqueda genérica.

**Pendiente real:** contrato externo de bytes API y procedencia completa de
snapshots alternativos; no cerrar exposición/lectura/generación por copia.
**Próximo paso exacto:** productores de mensajes case1/10 de438069f0;
43804cc8 toma staging,43806a80/43806d50 toman mensaje+4/+8.
Después consumidores del bloque+450..+458 hacia
selectores IMX210 con identidad demostrada de objeto/campo/llamada.
Ver [informe S40](../docs/capture/s40-context-origin-imx210.md),
`analysis/ghidra/s40-findings.json` y exports JSON/.c s40-.

Validación: auditor primero falla por findings ausente, luego PASS;
Ruff del auditor PASS, mypy src/auditor PASS. Ruff src/tests mantiene nueve
avisos previos en tests ajenos sin tocar. Pytest conocimiento:67PASS.
Mantenimiento obligatorio en cinco pasos completado:1455entidades /
2772relaciones tanto en paso2 como en paso5; grafo estable tras derivados.
Sin .git: cambios sin commit. Sin ejecución firmware/cámara/flasheo/
instalaciones/producción/push. **VEREDICTO: CAMBIOS** para exhaustividad y
semántica IMX210; ACEPTO origen API/copia y RECHAZO equivalencia con sensor.

## S41 — productores de mensajes y valores IMX210 (18-10-2026)

Solo silent-liro.gpr/av-cam.bin con -readOnly -noanalysis, SHA y memoria
cargada contrastados en cada export. Sin releer S31–S39 completos.
Exports s41- JSON/.c, inventario y auditor en analysis/ghidra; informe
[S41](../docs/capture/s41-message-origin-imx210.md).

**VERIFICADO:** cola30001, hilo437fee08, alta437ff098; snapshot3030f,
hilo43806e38/alta43806e68.4356120c envío indirecto slot1d4,
43561260 recepciónslot1e0,435612ec liberaciónslot1f4.
Productores4000/4036:43816448/43818c1c/43817e20→4381a138
→435aa20c→4356120c, destino30001. Tablas43bc59e0={1,0,5} y
43bc5a50={1,2,0,3}, entrada de claves numéricas vía435613b0.
VD_Pre selecciona R+458/R+48 y remapea0,1,2,3→0,2,1,4 en+5cc.

**VERIFICADO:** productorcase1 43b01026:objeto+4/564B; productorcase10
largo43b00f62:objeto+6c0/5e0B, con copia previa43b00cd0→objeto+6c4.
Case10corto43b00f22:objeto+ca0/28B, sin bloque560B. Reciben mensaje+4
y mensaje+8 en43806a80/43806d50, este último soloestado2.
**PARCIAL:** envíos a8003030f frente a recepción3030f; bit31 de OSAL
sin resolver. No se presenta como un bucle local probado.
**INFERENCIA:** intercambio entre roles y almacén de configuración.
**NO_VERIFICADO:** nombre UI/PTP, constructor original3023, campo tipado
SetMode/SetExposure/VMAX/HMAX, lectura y cierre físico de integración.

**Pendiente real:** destino con bit31 y otro participante del protocolo,
productor3023 y origen de las claves4000/4036; valores+5cc hasta sensor.
**Próximo paso exacto:** resolver tablaOSAL slots1d4/1e0 y reserva;
tipar datos43bf37c4/43bf344e/43bf3736/43bf341e de filas3023 en
43ffe020/340/6d0/740: sus destinos437fd5e4/437fd3b0/437fd0b0/437fd11c
son getters Thumb de tres instrucciones, no productores de solicitudes.
Seguir lectores con identidadR+5cc hasta bloque44B4380f440/SetSequenceMode.
Slots de importación OSAL435410b4+1d4/+1e0 son cero en el blob;
frontera de implementación/enrutamiento, sin agotamiento universal A/B.
Se activa Línea C y se contrastan selector43842158, configuración43844e80
y consumidor438c828c/436d6f6c, sin convertir clase2 en captura validada.

Auditor primero FAIL por manifiesto ausente, después rechaza ARM temporal;
corregido Thumb sin modificar el proyecto: auditor PASS. Ruff auditor PASS,
mypy src/auditor PASS; nueve avisos Ruff previos en cuatro tests ajenos.
Pytest conocimiento67PASS; mantenimiento completo cinco pasos:
1455entidades/2774relaciones en ambas reconstrucciones, grafo estable.
SHA y manifiestos .gpr/.rep intactos. Sin .git: cambios sin commit; sin push.
**VEREDICTO: CAMBIOS** para cierre extremo a extremo y semántica IMX210.

Línea C contrastada:43845f30/34 común+210→banco+41c;
4384215e/19e flags+4bc y+41c seleccionanclase1/3 normalmente.
438421f0 diagnóstico+7e=3 fuerza2;438422bc/d2 control+36=1/+37=2
también permite2.438c830c llamaSetExposure salvo+4b9c!=0;
dispositivo2/3 fuerza0en+655.436d6fb6 leeparámetro+9 y backendacepta0..4:
clases1/3/2 producenmáscaras c4/d4/94; clase2 ademásusa+8/+14.
**NO_VERIFICADO:** fin electrónico, factibilidad de clase2 y cuadro válido.
**Pendiente real actualizado:** productores de los controles+36/+37 y
contrato de argumentosclase2, metadatos3023 y valoresR+5cc.
**Próximo paso exacto actualizado:** seguir llamadores de43842158 hasta
escritores+36/+37 valor2, y clase2 de436d6f6c hasta sincronía de cortinas.
OSAL bit31 requiere proveedor adicional; no repetir la resolución de slotcero.

## S42 — identidad de exposición y productores de control (18-10-2026)

Proyecto único silent-liro.gpr, av-cam.bin, readOnly/noanalysis; SHA esperado
antes/después y bytes cargados verificados. Manifiestos S38 .gpr/.rep intactos.
Sin releer S31–S40 completos, firmware ejecutado, cámara, flasheo, instalaciones,
producción ni push. Exports nuevos `analysis/ghidra/s42-*` e informe
[S42](../docs/capture/s42-exposure-call-identity.md).

**CORRECCIÓN VERIFICADA de S41:**436d6320 es wrapper y436d6f6c otro cuerpo.
436d6344/46/48/4a desreferencia contenedor/objeto/vtable y llama slot+28.
Constructor436d72e8 instala43fcc090;43fcc0b8 contiene436d6f6d.
Factoría436d6504 construye43e7f4a8 y43ad9054 lo publica en43e7f858,
contenedor devuelto por436d6118.438c830c llama wrapper: vínculo virtual
demostrado para ese backend; no BL directo ni alias ni traza física.

**VERIFICADO:**clase2 lee BYTE parámetro+08/+14 en436d7136/7142;
escribe buffers4401c6d2/4401c7ce y calcula u16objeto+3a0 en436d71e0.
No se transforma el ushort* decompilado en cargas u16 inexistentes.
**NO_VERIFICADO:**transporte físico, cortinas, sincronía VD_Drive/VD_Post,
unidades del tiempo, cierre electrónico y YC válido.

**VERIFICADO/PARCIAL:**4382e3a8/b2 copia C+94/+95 desde C=*(contexto+50)
a B43eae270+36/+37;437b5b14 conserva B para4384b268 y4384cb58→437b0480
publica c14B enG43ea6ad4.438412d0 pasa G al selector43842158.
Valor2 original y realizabilidad de rama pendientes.43845b68/70 son otro objeto,
no prueba del escritorG. Inventario ampliado de stores byte+36/+37 en listado;
no exhaustivo frente a código sin listar, copias o bases desplazadas.

**VERIFICADO:**R43e9b548+5cc=43e9bb14=ImgState43e9baec+28.
Lectores438553dc/4385558a pertenecen a43e18c60, descartados por identidad.
4380f440 copia0x44=68B a43e994d0;4378ea8c copia a43e99320,
4378eac6→4378e334 y4378e360→43795a60. Dependencia desdeR+5cc
**NO_VERIFICADO**, cadena solicitada se corta antes del bloque fuente43eea2e4.
Getters3023 devuelven secuencias compactas; descripción/metadatos es INFERENCIA,
parser/consumidor tipado NO_VERIFICADO. No confundir con configuración de sensor.

**Pendiente real:**escritor original C+94/C+95 y valor2, lectores IMX210+3a0
y transporte de los dos buffers, parser3023 y lectorR+5cc por aliasImgState+28.
**Próximo paso exacto:**seguir C=*(contexto+50) del productor4382dd78,
manteniendo B43eae270→G43ea6ad4→43842158; identificar stores C+94/+95
antes de atribuir modo mecánico/EFCS/clase2 a opción de usuario. En paralelo
lógico, sin aperturas simultáneas del proyecto, lectores objeto+3a0 y
ImgState+28 con identidad; consumidor indirecto de filas3023.
Sin agotamiento estático declarado; Línea E no activada aunque existe
firmware/extracted/a6300-fw201. No reabrir bit31 OSAL sin evidencia distinta.

Auditor primero FAIL por manifiesto ausente y después PASS. Ruff: nueve avisos
previos en tests ajenos, ninguno nuevo en auditor. Mypy src/auditor PASS.
Sin .git: cambios sin commit. **VEREDICTO: CAMBIOS** para cierre físico/origen2;
ACEPTO identidad virtual/usos byte, RECHAZO equivalencia de cuerpos y
consumidores por offset sin identidad. Validación del grafo al cierre debajo.

## S43 — PIC de exposición y revisión de códigos de modo (18-10-2026)

Proyecto silent-liro.gpr/av-cam.bin exclusivamente readOnly/noanalysis;
SHA esperado antes/después y memoria cargada contrastados. Auditor comprueba
manifiestos históricos .gpr/.rep. Sin releer S31–S42 completos, ejecutar firmware,
cámara, flasheo, instalaciones, producción ni push. Sin .git, sin commit.
Exports `analysis/ghidra/s43-*`; [informe S43](../docs/capture/s43-exposure-mmio-and-lock-codes.md).

**VERIFICADO:** PIC4401eee4, slots436d72a0..dc resueltos a estructuras
4401c6xx–4401caxx con IDu16 y valorbyte+2; primeros IDs3..8, segundo grupo144..149.
Clasificación b3: registros preparados en software, sin MMIO literal ni vtables.
Formato completo/transporte físico PARCIAL; nombres de registros INFERENCIA.
43ad9a40/43ad99d4 solo guardan estado: iVar18 ya es objeto+fc, no base PIC.

**ACEPTO**4380e020/43902718 como log/trace. **RECHAZO** hipótesis AF/lock:
43ca2585 contiene SetSequenceMode img/fratechg/clamp/bb_out/cap_end;
4380e43c tiene ImgMode/IMAGE_FRAME_RATE/SYNC_RAW_OUTPUT_SIZE y consulta
virtual+94→43ad95ce→43ad9438 (búsqueda en tabla de modos, devuelve ff si ausente).
No asignar nombre SetSequenceMode a4380e43c: cadena pertenece a4378e334.
Relación R+5cc→bloque y escritura física desde esta rama NO_VERIFICADO.

Virtual+4c436d92e0 busca dos modos y llama virtual+a8 con índices/flags.
Virtual+10436d8ff4 copia0x70B desdeobjeto+180, sin transporte. Listados temporales
sin crear funciones; primer rango atravesó pool, reintento con parada en retorno.
Inventario515 matches+3a0/stores+94/+95: candidatos sin identidad, no exhaustivo.

**Pendiente real:**transporte de registros preparados, lector IMX210+3a0,
escritor original C+94/+95 y valor2, dependencia R+5cc y parser3023;
cortinas/VD/fin electrónico y YC válido NO_VERIFICADO.
**Próximo paso exacto:**consumidores de registros4401c6xx–4401caxx por slots PIC;
resolver virtual+a8 llamado436d938c desde436d92e0 con índices de modos/flags.
Después C=*(contexto+50) en4382dd78 y stores originales+94/+95, conservando
B43eae270→G43ea6ad4→43842158. No reabrir OSALbit31; Línea E no activada,
sin agotamiento estático global. Virtual+10 queda cerrado como getter software.

Auditor S43 PASS tras distinguir listado de decompilación en dos métodos no
definidos. **VEREDICTO: CAMBIOS** para cierre físico, tareas1–3 documentadas.

Validación final S43: mantenimiento completo index_docs→build_graph→
export_corrections→index_docs→build_graph. Ambos builds:1455 entidades,
2777 relaciones,58 CORRECTS/SUPERSEDES; grafo estable. Export56 filas de
correcciones y55 preguntas; índice372 archivos/2833 secciones.
`pytest tests/knowledge -q`:67 PASS (11.50s). Auditor SHA/PIC/.gpr/.rep PASS.
Ruff auditor PASS; comando solicitado src/tests conserva9 avisos anteriores en
tests ajenos, sin cambios allí. Mypy src+auditor:sin problemas en6 archivos.
Sin avisos nuevos en lo tocado. No se ejecutó otro agente ni revisión Claude.

## S44 — consumidor de registros y tabla de modos (18-10-2026)

Solo silent-liro.gpr/av-cam.bin, readOnly/noanalysis; SHA esperado antes/después,
memoria cargada y manifiestos históricos .gpr/.rep contrastados. Sin guardar,
ejecutar firmware, cámara, flasheo, instalaciones, producción ni push.
Sin releer S31–S43 completos ni reabrir AF/OSALbit31.
Exports `analysis/ghidra/s44-*`; [informe S44](../docs/capture/s44-register-consumer-mode-table.md).

**VERIFICADO:**436d839c→getter436d79b0→tabla43fe995c,119 punteros;
436d75f8 consumeIDu16 y byte+2, backendobjeto+298 empaqueta con
436d5e04→43ad8fe0→43ad8fa2. Fin/overflow→436d5cdc→436d5ed0
escribe bytes como palabras en bancoA+40+4*i;436d5f60 pulsa1→0→1 enB+8.
Tabla43bc14e8 da bancosf3c00300/fc088300/fc089300 y controles asociados;
constructor mapea variantes a canales{1,2,0}. Esperas evento18 no prueban
fin de integración. Clasificaciónb3 de S43 permanece correcta.

**VERIFICADO:**virtual+a8=436d65b8 compara nibbles altos de fila43fe9b74,
destino4401c6ae=registroID0+2, usando dos índices sobre13 modos;
ignora flags, devuelve1 si difieren,0 si coinciden. Sin escritura/transporte.
**PARCIAL:**4385cf2c produceP+95=2 con condiciones de campos y sobrescritura
posterior posible a8;P=raíz+2bc en437b43b4.4385ca3c inicializaP+94/+95.
Alias conC=*(contexto+50) de4382dd78 sin demostrar;43ef2474 es snapshot
condicional de0x6b0B, no identidad probada.44004894 es tablaID/puntero.

**Pendiente real:**identidadP/C y escritor originalC+94/+95;lectoresIMX210+3a0,
semántica físicaID0/IDs3–8/144–149 y enlace a integración/VD/cortinas;
dependenciaR+5cc/parser3023 sin cerrar. Captura electrónica NO_VERIFICADO.
**Próximo paso exacto:**resolver origen del contexto pasado a437b5b14 y su
campo+50 hasta raíz+2bc/snapshot43ef2474. Solo entonces trasladar condiciones
de4385cf2c aC y seguir valor2 haciaB43eae270→G43ea6ad4→43842158.
Después lectoresIMX210+3a0 y significado físicoID0. No repetir consumidor ni
virtual+a8. Sin frontera estática agotada: Línea E no activada.

Auditor S44 primero FAIL por manifiesto ausente y después PASS:119 registros,
13 modos, nibbles,MMIO,SHA y .gpr/.rep. ACEPTO consumidor/MMIO/virtual+a8;
RECHAZO alias por offset y cierre físico. **VEREDICTO: CAMBIOS** para estos
pendientes. No hay .git utilizable: cambios sin commit;sin revisión por agente.

Validación S44:pytest tests/knowledge67 PASS(6.15s);ruff auditor PASS,
mypy src/auditor PASS;ruff src/tests conserva9 avisos previos en tests ajenos.
Auditor de SHA/.gpr/.rep PASS. Primer ciclo estable1455/2778, pero contenía
un falso CORRECTS generado por una frase de auditoría sobre S43;se reformuló
esa frase sin tocar el extractor. Mantenimiento completo repetido:
ambos builds1455 entidades/2777 relaciones/58 CORRECTS/SUPERSEDES;estable.
Índice373 archivos/2844 secciones;export56 correcciones/55 preguntas.

## S45 — identidad del contexto y consumidor del timing (18-10-2026)

Solo silent-liro.gpr/av-cam.bin, readOnly/noanalysis; SHA esperado y memoria
contrastados por exportador, manifiestos .gpr/.rep intactos por auditor.
Sin guardar, cámara, firmware ejecutado, instalaciones ni push.
Exports `analysis/ghidra/s45-*`;
[informe S45](../docs/capture/s45-context-identity-and-physical-closure.md).

**VERIFICADO:**437b4eb4 construye contexto43eaadd8→437b4df0→437b5b14;
437b4f2c copia0xb0 desde43e993a4, reconstruido enVD_Pre desde raíz
copiada43e99514.43ae8d56 fija contexto+50=raíz+1e6c=C43e9b380;
43ae8faa copia1a4 desde raíz original43e9b548+1e6c=43e9d3b4.
**PARCIAL:**P de437b43b4=padre+1454 en dos llamadores;falta copiaP→C,
sin atribuir aC condiciones de4385cf2c ni alias con snapshot43ef2474.

**VERIFICADO:**vtableIMX210+74=43ad9203;getter43ad9202 leeobjeto+3a0.
Wrapper43ad90b6, llamado438c835e, conserva retorno para cálculo de
captura+570;43795dec→43ad3b92→436c74c8 lo consume hasta43ad2bd6,
escritura base+220, condicional por caché. Controlador43e16d28 publicado
desde owner43e15f18+e10. **PARCIAL:**base=*(43e16d2c),cero enarchivo,
sin escritor inicial identificado;MMIO/integración/VD/cortinas NO_VERIFICADO.
Semántica eléctricaID0/IDs3–8/144–149 no recuperada ni agotada.

**Pendiente real:**escritor/copia de43e9d3b4+94/+95 hastaP/B/G y base
43e16d2c hasta destino físico+220;semántica de integración/lectura/cortinas.
La serie explícitaS40–S45 termina aquí;hito continúa abiertoS46+.
No hay agotamiento estático real: no se activa Línea E ni se abre A6300.
**Próximo paso exacto:**resolver escritores43e9d3b4+94/+95,incluyendo offsets
partidos y copias,antes de transportar valor2 desdeP=padre+1454/snapshot.
Resolver inicialización43e16d2c desde owner43e15f18;después contrastar
base+220 con controladorVD. No repetir getter+74,consumidor/virtual+a8,
OSALbit31 niAF. No inferir captura electrónica desde escritura indirecta.

Auditor S45:FAIL por resumen ausente;FAIL por transcripción decimal de raíz/C;
corregida contra literales;PASS de SHA/memoria/.gpr/.rep/contexto/getter.
ACEPTO identidad del contexto y consumidor de timing;RECHAZO aliasP/C por
offset y cierre físico. **VEREDICTO: CAMBIOS**. Sin .git utilizable:sin commit.

Validación S45:pytest tests/knowledge67 PASS(6.72s);ruff del auditor PASS;
mypy src+auditor PASS(6 archivos). Ruff src/tests conserva los9 avisos previos
en tests ajenos,sin avisos nuevos en lo tocado. Auditor final SHA/.gpr/.rep PASS.
Mantenimiento completo:index_docs→build_graph→export_corrections→index_docs→
build_graph;ambos builds1455 entidades/2777 relaciones/58 CORRECTS/SUPERSEDES,
grafo estable. Export56 correcciones/55 preguntas. Índice374 archivos/2856 secciones.

## S46 — base VD y escritor directo de C (18-10-2026)

[Informe S46](../docs/capture/s46-vd-base-and-context-identity.md),
exports `analysis/ghidra/s46-*`. Solo silent-liro.gpr, siempre readOnly/noanalysis,
sin guardar ni crear funciones. Firmware ORIL en base lógica `0x43541000`;
SHA esperado verificado antes/después y memoria cargada contrastada por exportador.
Manifiestos S46 de los 10 archivos protegidos (firmware, .gpr y .rep) idénticos.
Sin cámara, firmware ejecutado, flasheo, instalaciones ni git.

**VERIFICADO:** `0x436c2250` llama inicialización `0x436c6f3c` con owner
`0x43e15f18`. En `0x436c6f74` entrega owner+e10=`0x43e16d28` y
literal `0x436c71f8=0xf3120000` a `0x436c7950`. BL `0x436c7964`
→ `0x43acee66` escribe base en `0x43e16d2c`; r1 conservado en ensamblador,
aunque el pseudocódigo lo omita. La escritura condicional de S45 en
`0x43ad2bd6` tiene destino `0xf3120220`. Sin atribuir fin de integración.

**VERIFICADO:** C fuente=`0x43e9d3b4`, construido por raíz+1e40+2c
en `0x43792f8e/0x43792f94` y entregado a `0x437da078` en `0x43792f9c`.
Dispatcher `0x43ed461c`, callback vía `0x437da314` con r1=C.
Tabla `0x43ff8308`, fila `0x43ff8adc={0xce,0x43ff7414,1}`;
slot contiene `0x437dad79`. Callback Thumb `0x437dad78` copia payload4B
desde `0x43ed4620` a scratch `0x43f7bbf4`. Primer u16!=0 →
`0x43e9d448=1`, `0x43e9d449=low8(segundo u16)`; primer u16=0 → ambos cero.
Stores exactos `0x437dad92/0x437dad9a/0x437dad9e`, selección de tabla con
byte `0x43e959eb=0`, clave0xce y cursor de callback válido.

**PARCIAL:** propagación condicional de (1,2) por copia1a4 a C consumido
`0x43e9b380` y copias B=`0x43eae270`→G=`0x43ea6ad4`→`0x43842158`.
No prueba un payload concreto, ausencia de sobrescritura en toda ejecución,
factibilidad dinámica ni efectos eléctricos. P=padre+1454 y snapshot
`0x43ef2474` siguen sin alias/copia a C; no se transplantan condiciones de P.
El scratch nuevo tampoco es ese snapshot.

**Pendiente real:** productor de los dos u16 del payload clave0xce;
orden completo de preparación/copia; relación P/C no demostrada;
semántica eléctrica de `0xf3120220`, integración y cortinas NO_VERIFICADO.
**Próximo paso exacto S47:** argumento4 de `0x437da100`, copia a
`0x43ed4620=0x43ed461c+4`, localizar productor de clave0xce y demostrar
sus dos u16/orden frente a `0x43792f9c/0x4379409e`; después semántica VD.
No reabrir OSALbit31, hipótesis AF ni consumidor/virtual+a8; sin agotamiento/Línea E.

**Validación:** auditor FAIL inicial por resumen ausente, luego PASS;
contrasta bytes del setter, literal base, PIC, fila de tabla, slot Thumb,
scratch y ramas/stores del escritor. Integridad final PASS en 10 archivos.
Pytest tests/knowledge:67 PASS(5.16s). Ruff de ambos scripts S46 PASS tras
corregir dos comparaciones constantes del auditor; src/tests conserva nueve
avisos previos en cuatro tests ajenos, sin cambios en ellos. Mypy src+ambos
scripts:PASS(7 archivos). Listados temporales suplen funciones no definidas;
no se confunden exports .c vacíos con decompilación válida.
ACEPTO base VD y escritor C con identidad/condiciones; RECHAZO alias P/C
y cierre físico. **VEREDICTO: CAMBIOS** para el hito físico. Sin git/commit.

Mantenimiento completo S46: index_docs→build_graph→export_corrections→
index_docs→build_graph. Ambos builds:1455 entidades/2777 relaciones,
58 CORRECTS/SUPERSEDES; total de relaciones idéntico, sin autocontaminación.
Export56 correcciones/55 preguntas; índice375 archivos/2866 secciones.
La anotación final de resultados se reindexa con el mismo ciclo completo.

## S47 — entrada del payload y orden de copia C (19-10-2026)

Informe: `docs/capture/s47-payload-producer-and-order.md`.
**VERIFICADO:** nuevas llamadas `0x437896ce/0x4378975a` a `0x437d9f9c`,
recuperadas de bytes Thumb fuera de funciones definidas. Callback receptor
`0x43789cc0` registrado en `0x4378a3e6` con ID `0x301d7`.
Tabla índice0 `0x43ff23b0`, fila `0x43ff29b8={0xce,0x43789709}`;
handler `0x43789708` copia0x140B a `0x43e95420` por slot GOT `0x4401f0c0`.
Payload en `0x43e9543c/+2` → argumento4 de `0x437da100` → copia0x124B
a `0x43ed4620` → despacho `0x437da078/0x437da2d8` → `0x437dad78`.
Solicitud sintética `0x43ed44dc` es otra entrada; no es el buffer recibido.

**VERIFICADO:** callback ANTES de copia C en misma invocación de VD_Pre.
CFG con2276 nodos y5TBB: `0x43792f9c` domina `0x43794096`; no hay retorno
desde `0x4379409a` al despacho. Raíz destino `0x43e99514`, origen `0x43e9b548`;
subcopia `+0x1e6c`,0x1a4B en `0x43ae90ce`, desde `0x43e9d3b4` a
`0x43e9b380`. Incluye `+0x94/+0x95` → destino `0x43e9b414/0x43e9b415`.
No se refuta S46 por orden; `0x4379409e` es llamada posterior, no la subcopia.

**PARCIAL:** productor original de u16 en paquete+1c/+1e anterior a entrada
`0x43789cc0`, valor2 y propagación a B/G. Nuevo servicio+1ec del registrador
`0x435612b4`: slot `0x435412a0=0`; proveedor/contrato sin resolver.
No se reabren bit31/S41, AF/S43, consumidor/virtual+a8/S44 ni alias P/C/snapshot.
**NO_VERIFICADO:** relación VD/cortinas; punto opcional3 aplazado porque1 sigue
incompleto. No se concluyen rutas independientes. Clases1–3 sin nuevo cierre físico.
**Próximo exacto S48:** proveedor/contrato del registro ID0x301d7, entrada+1ec,
y productor del paquete clave0xce, stores+1c/+1e antes de `0x43789cc0`.
Hito S46–S52 abierto. ACEPTO cadena interna/orden; RECHAZO productor original
identificado y cierre físico. **VEREDICTO: CAMBIOS**.

**Validación S47:** auditor FAIL inicial (findings ausente), después PASS:
2787 registros de listado contrastados con firmware, tablas/PIC, thunk mixto
Thumb/ARM, rango y dominancia. Huellas antes/después PASS,10 archivos protegidos.
Ruff scripts S47 sin avisos nuevos; src/tests conserva9 avisos en4tests ajenos.
Mypy src+4scripts S47 PASS(9archivos). Una consulta concurrente fue rechazada
por bloqueo del proyecto; se repitió secuencialmente, sin forzar locks ni guardar.
Sin git/commit/push, firmware ejecutado, cámara, flasheo ni instalaciones.
Pytest conocimiento: **67 PASS** (6.01s), log `s47-pytest.log`.
Mantenimiento completo index→graph→export→index→graph: **1455 entidades y
2778 relaciones en ambos builds**, idénticos;59CORRECTS/SUPERSEDES.
Export57correcciones/56preguntas; índice376archivos/2875secciones antes de
esta anotación final. Log final `s47-maintenance.log`; se repite el ciclo completo
tras registrar resultados, sin editar fuentes entre sus dos builds.


## Hito REA independiente (19-10-2026)

REA 6.5.0 usado como Línea B sin tocar `silent-liro.gpr/.rep` ni S1–S48. Experimentos en
`analysis/rea-independent/` (pre-registro, guiones, salidas, manifiestos SHA-256 inicial/final idénticos).
Resultados, tiempos, coincidencias/diferencias y recomendaciones: `docs/capture/rea-independent-milestone.md`.
Resumen: libmprctrl (8 funciones) coincide; av-cam completa en ~8 min con timeout ampliado y 78 % de cobertura de entradas históricas;
sin evidencia nueva de obturador electrónico. No se rediseñó el sistema de conocimiento.


## S50 — investigación paralela Claude + Codex (19-10-2026)

Dos procesos con sesiones REA propias (`analysis/s50/`). Resultado y límites en `docs/capture/s50-parallel-conclusions.md`. `0xb6` inerte; filas `1/2/3/6` = nº de callbacks (corrige S49); override `C+0x94/95`→modo 0..7 solo hacia estado; pregunta final NO_VERIFICADO. SHA 1490/1490 intactos. Próximo S51: consumidor físico del modo / `C_Imager::SetMode` y semántica ID1/100/101.

## S52 — trazado de cortinas y propagación de clase 0 (Claude + Codex, 19-10-2026)

Agentes: A Claude (Opus 5.5, medium, `work/claude/`), B Codex (`gpt-5.6-terra`, medium, `work/codex/`; R1 superficial → R2 dirigida
con REA+Unicorn → validación cruzada). Sesiones REA separadas y cerradas. Instalado `~/.venvs/re` (capstone/unicorn/keystone/lief, ruff), ver
`environment/`. `session_daemon.py` admite `REA_DAEMON_RSS_MAX_MB`. Resultado: Silent A7S marca el paquete CAIF y omite esperas
mecánicas (no suprime envíos); `+0x748`≙A6000 `+0x740` latente; clase 0→`param+9` VERIFICADA (discrepancia A/B resuelta por el
coordinador, `analysis/s52_coordinator_check.py`); corrección `cfg2+4|=8` en todos los ShutMode IMX235. P5 NO VERIFICADO, S51 vigente.
Detalle: `docs/capture/s52-parallel-conclusions.md`. Hashes 8/8 y manifiestos intactos. Próximo: parser CAIF Darwin (bit `0x20`).

## S53 — Darwin: transporte MSS y parser CAIF (Claude, 19-10-2026)

Solo Claude (Opus 5.5), sin subagentes ni Codex. Ghidra headless sobre las tres ROM Darwin (`analysis/s53/`), capstone y LLVM;
REA no se abrió (mismo motor; lote directo más rápido para ROM pequeñas). Vista ELF nueva `analysis/a7s-darwin-rom-analysis-view.elf`.
Resultado: receptor = mss-async ID `0x0c` sobre MFS5; parser A7S `0x18396` / A6000 `0x17f8c`; A7S consume el bit Silent `0x20`
y deja de accionar P4D/P4E; A6000 no. Escenario B; S51 vigente. Detalle: `docs/capture/s53-conclusions.md`. Suite 42/42.
Próximo (no iniciado): traza pasiva autorizada de `MSS_SO_DWN`/bobinas, consumidor LIRO de `CA_1ST_CURTAIN_START`, efecto del tipo 0.


## S54 — P4C, tipo 0 y sincronización BIONZ (20-10-2026)
- Hecho: rastreo de escritores P4C en ambas ROM Darwin (`analysis/s54/p4c_scan.py`), esquema BIONZ (SENS_B/GPIO_9, A6000 y A7S), diff tipo 0 ↔ Silent, origen del byte de tipo,
  primitivas GPIO de BIONZ (`analysis/s54/bionz_gpio_calls.py`, REA sesión única 440 s cerrada). Informes `docs/capture/s54-*.md`, matriz `analysis/s54-evidence-matrix.json`, tests `tests/test_s54_p4c.py` (21/21).
- Herramienta: REA `rq.py` (cliente compacto del demonio) en `analysis/s54/rq.py`; ruff instalado en `~/.local/bin` (sin avisos en archivos nuevos); sin dependencias nuevas de proyecto.
- Frontera: consumidor BIONZ de P4C (pares pin→(canal,bit) sin inicializar en `av-cam`), escritor del byte de tipo, polaridad/rearme P4C, IMX210 (sin datasheet).
- Próximo exacto: `av-cam` A7S 3.20 — barrido `gpio_get` y localizar el inicializador de `0x43e77298…`.


## S55 — origen de pares GPIO, A7S vs A6000 (20-10-2026)
- Hecho: equivalentes GPIO en A7S (`get 0x43b585c2, cfg 0x43b58534, set 0x43b585a0`), tabla de sitios (`analysis/s55/gpio_calls_diff.py`), descubrimiento de la base de backup BK4 (`analysis/s55/bk4.py`), inicializador de pines
  (`pin_init.py`), usuarios de variables (`var_users.py`), eventos/MMIO (`events_mmio.py`). Informes `docs/capture/s55-*.md`, matriz `analysis/s55-evidence-matrix.json`, tests 16/16.
- Herramientas: REA (1 sesión, `GHIDRA_MAXMEM=6G`, cerrada) para confirmar wrapper `+0x2e0` y empaquetado de pines; capstone/readelf/llvm-objdump para el resto; sin dependencias nuevas.
- Corrección: «variables sin escritor» de S54 es incorrecta (escritor `0x436bcef4`, store vía GOT).
- Frontera: banco de los `GPIO_n` (sin «S»), `SENS_B`, valores por unidad (`Backup.bak`), IMX210.
- Próximo exacto: escritores de `0xf2a10000–0xf2a30000`/`0xf2400000` (candidato SENS_B); IDs dinámicos de `0x43716dd0`; traza pasiva autorizada.


## S56 — transporte de registros del IMX210 (20-10-2026)
- Hecho: cadena `SetExposure → registros sombra → Execute → consumidor 0x436d75f8 → formateador P2S → RAM P2S(DFE0) 0xfc088340` reconstruida y **emulada con Unicorn** (`analysis/s56/{p2s_emu,setexp_emu,rec_users,xr,rq}.py`); REA (sesión única `GHIDRA_MAXMEM=6G`, cerrada) confirmó consumidor y llamadores. Informes `docs/capture/s56-*.md`, matriz `analysis/s56-evidence-matrix.json` (`build_matrix.py`), tests 26/26. Dependencia nueva: `unicorn` (pip --user).
- Hallazgos: IDs = direcciones 16 bit; trama `81|len|81|AH AL|datos`; `svd/shd/spl` = IDs 3–8; ShutMode→ID1; pulso SSB; CISIF = receptor; A7S mismo P2S con registro de 5 B.
- Frontera: semántica de registros IMX210 y de `CIS0_SHT_RST→XPI`; consumidor SENS_B; origen de `0x43eb35d0` (tiempo→banco).
- Próximo exacto: traza pasiva CIS0/XPI/VD (decodificable con `p2s_emu.frames`) o rastreo estático de `0x43eb35d0+0xc4..0xd8`. S51 se mantiene.


## S57 — semántica de ID1, SSB, svd/shd/spl, Silent IMX235, XPI y sincronía P2S (20-10-2026)
- Hecho: escritores y bits de ID1 (seguimiento GOT→registro `analysis/s57/bitops.py`), rejilla 13 modos × 5 ShutMode × SSB con el código real (`analysis/s57/{emu57,id1_grid}.py`, 130 casos con dos rellenos de memoria), productores/orden de SSB, mapeo exacto svd/shd/spl (`c_timing.py`, 400/400), cadena de producción hasta el banco `0x43eb35d0`, matriz efectiva IMX235 (`imx235_matrix.py`), esquema XPI, modos de SyncMode del P2S (`sync_modes.py`).
  Informes `docs/capture/s57-*.md`, matriz `analysis/s57-evidence-matrix.json` (33 entradas, H57-1…10), tests `tests/test_s57_imx210_exposure.py` 34/34.
- Herramientas: REA (1 sesión, `GHIDRA_MAXMEM=6G`, cerrada; salidas en `analysis/s57/rea-out/`; cliente `analysis/s57/rq.py`), Capstone y Unicorn; sin dependencias nuevas; `ruff --select F,E9` limpio; mypy no instalado.
- Hallazgos: ID1 combinado; SSB = strobe de aplicación de exposición (no fin); svd cuenta pasos del host/VD; Silent A7S = modos de lectura; AdjustCmd fija las banderas +0x277…+0x27c; XPI sin controlador visible.
- Correcciones: B de ID1 es copia de A (no valor propio); no se reproduce «ShutMode 4 escrito en captura»; el pulso ocupa dos bloques de trama separados por una cabecera de 5 B.
- Frontera: productor AE de las filas de banco (`S+0xC4…0xD8`), unidades de svd/shd/spl, ID1 eléctrico, XPI, evento que activa las banderas del P2S, tabla de categorías de AdjustCmd.
- Próximo exacto: `trace_native_values` sobre el pipeline AE; o traza pasiva CIS0/XPI/VD autorizada. S51 se mantiene.


## S59 — Claude + GPT-6.1 Sol: bloque IMX210 `+0xDD0` y constructor real C_Imager A7S (20-10-2026)
- Hecho: GPT (`codex exec`, gpt-6.1-sol/medium) recuperó el escritor `0x43b00da0` del bloque `0x437876dc()+0xdd0` (publicación `0x43b00dd4`, fuente `obj+0xd64`), corrigió la atribución de `clk` de S58 y delimitó VdNum/host (`docs/capture/s59-sol.md`, `tests/test_s59_sol.py` 11/11). Claude localizó y emuló el constructor real `C_Imager` `0x436f3fc0` y rehízo los escenarios (`analysis/s59/claude/`, `tests/test_s59_claude.py` 9/9). Revisión cruzada de GPT (solo lectura) → CAMBIOS aplicados.
- Hallazgos: M no es constante de construcción (payload externo); S58-C base/tramas P2S eran artefactos (real `0xfc088300`, 3 tramas), registros intactos (100 escrituras); mensajes `0x1000/0x1001` = lista blanca de modos; Execute sin ramas de registros exclusivas de Silent bajo depuración `0xff`; consumidor de ganancia con único llamador directo.
- Herramientas: REA (1 sesión A7S + 1 sesión A6000 de GPT, cerradas), Capstone, Unicorn; sin dependencias nuevas.
- Frontera: emisor del payload de `0x438069f0` (origen M/Tv/clk), receptores de `0x1000/0x1001`, servicios Darwin/OSAL stub, física del sensor.
- Próximo exacto: sembrar Thumb en los emisores/receptores anteriores; traza pasiva CIS0+XPI+VD autorizada. S51 se mantiene.
