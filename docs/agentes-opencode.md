# Agentes autónomos (opencode) — carta común y prompts

Referencia de comparación: **A7S fw3.20** (misma generación y plataforma que la A6000 fw3.21, con
silent shutter). El A6300 queda solo como contraste secundario; no abrir líneas nuevas con él.

## Carta común (pegar al inicio de cada agente)

Trabajas de forma autónoma y continua en el proyecto Sony A6000 (ver `CLAUDE.md`, `docs/STATE.md`,
`knowledge/CURRENT.md`). Objetivo: entender cómo la A7S implementa el obturador silencioso/electrónico y
qué falta o difiere en la A6000. No te detengas tras una tarea: ejecuta el bucle hasta agotar el backlog
y vuelve a generarlo.

**Bucle (repetir sin pedir confirmación):**
1. `git fetch && git rebase origin/main` en tu rama de trabajo.
2. Toma el siguiente ítem de tu backlog (`knowledge/agents/<tu-id>-backlog.md`; créalo si no existe).
3. Antes de reutilizar un hallazgo previo, corre `contradiction-audit`. Busca primero en
   `scripts/knowledge/` antes de investigar a mano.
4. Escribe primero el test/reproducción que falla; luego el análisis (REA primero, Ghidra `silent-liro.gpr`
   como respaldo; verifica lo decisivo contra bytes). Una consulta vacía no prueba ausencia.
5. Informe en `docs/capture/sNNN-<tema>.md` con etiquetas VERIFICADO / INFERENCIA / NO_VERIFICADO y su
   límite. JSON + tests en `analysis/sNNN_<tema>/`.
6. `knowledge-maintenance` (solo reindexar; no edites `CORRECTIONS.md`/`OPEN-QUESTIONS.md`, los regenera el humano); `ruff` y `mypy` sin avisos nuevos; tests relevantes en verde.
7. Un commit por fase (Conventional Commits, sin logs de sesión REA), actualiza el README con la fase,
   y `git pull --rebase origin main && git push origin HEAD:main`. Si el push falla por carrera, repite
   rebase+push (máx. 5). Si hay conflicto en README/CURRENT.md, conserva ambas entradas.
8. Marca el ítem hecho, añade los ítems derivados al backlog y continúa.

**Numeración de sesiones (evita colisiones):** agente A usa S200–S299, B S300–S399, C S401–S499.

**Un tema = una sesión.** Prohibido abrir una sesión por cada xref o cada cadena suelta: agrupa por
subsistema y cierra con una tabla.

**Límites duros:** sin firmware ejecutado, sin cámara, sin flasheo, sin tocar `.venv`/ignorados, sin
`push --force`, sin reescribir historia, no editar archivos de otro agente (solo los tuyos más
README/CURRENT.md por append). No expongas secretos. Si algo exige cámara o decisión humana, anótalo en
`knowledge/agents/NEEDS-HUMAN.md` y sigue con otro ítem.

**Parada:** solo si (a) backlog vacío y 2 regeneraciones seguidas sin hallazgos nuevos, o (b) tests/CI
rotos que no puedas arreglar en 3 intentos (anótalo en NEEDS-HUMAN.md).

## Agente A — Sensor y driver: A7S (IMX235) vs A6000 (IMX210) (S200+)

Solo investigación; el triaje de preguntas abiertas ya está hecho (`analysis/s400_open_questions_triage/`:
51 correcciones aplicadas, 81 falsos positivos del extractor, 0 preguntas técnicas vigentes).
1. Con S57/S58 como base, extender la comparación de modos de captura A7S↔A6000 a registros y tiempos de
   lectura/exposición que aún no estén cubiertos; una tabla por subsistema.
2. Nota: S169 dice que A7S y A6000 tienen 0/0 de `CheckSet*` de LiroSeq → la A7S implementa el silent
   shutter por otra vía. Identificar cuál (drive mode, tabla de timings, mensaje a Liro).
3. Clasificar cada diferencia: idéntico, distinto, ausente en A6000.

## Agente B (DeepSeek) — Imager: estado, drive modes y gates (S300+)

Ver `docs/agentes-opencode-deepseek.md`.

## Agente C — Ruta de control: configuración → LIRO → imager (S401+)

1. Seguir en A7S la ruta `SilentShutter` configuración → receptor LIRO → estado del imager y compararla con
   A6000 (partiendo de `silent-shutter-status.md`, E018/E019, S174 `…ForLiro`: A6000 rechaza todos).
2. Para cada diferencia, indicar cuál de las ocho pruebas de `physical-test-plan.md` la confirmaría o
   refutaría, y proponer pruebas nuevas si faltan (solo redactar, no ejecutar).
3. Al agotar la ruta, escribir `docs/capture/tesis-obturador-electronico.md`: hipótesis, evidencia, qué la
   refutaría.

## Colas

Cada agente lee y actualiza su cola `docs/agents/queue-<A|B|C>.md` (estado por ítem) y deja notas breves en
`docs/agents/outbox-<A|B|C>.md`. Al vaciarla, la regenera según su backlog.
