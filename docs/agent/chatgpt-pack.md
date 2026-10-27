# Pack para ChatGPT web (pegar al inicio del chat)

> Copia portátil de las reglas y del estado. Fuente: `AGENTS.md`, `.claude/skills/*`,
> `knowledge/CURRENT.md`. Si hay conflicto, manda el repo.

## Reglas

- Investigación estática: sin firmware ejecutado, sin cámara, sin flasheo (salvo autorización
  expresa del usuario para un caso concreto).
- Silencio: ejecutar sin narrar pasos intermedios; comentar solo al terminar.
- REA primero (funciones, xrefs, decompilación, `trace_native_values`); Ghidra
  histórico `analysis/ghidra/silent-liro.gpr` (readOnly) solo como respaldo o para
  verificar bytes. Una consulta vacía de REA no prueba ausencia. Verificar lo
  decisivo contra instrucciones/bytes; separar VERIFICADO / INFERENCIA / NO_VERIFICADO.
- Antes de reutilizar un hallazgo: auditar si está corregido/superado
  (`docs/CORRECTIONS.md`, `docs/OPEN-QUESTIONS.md`, `python scripts/knowledge/search.py claim <doc>`).
- Tras editar `.md` indexado: `index_docs.py`, `build_graph.py`, `export_corrections.py`,
  reindexar y confirmar que el grafo da el mismo total.
- Al cerrar fase: commit local (Conventional Commits, solo archivos propios) y push
  a `origin/main`; el README solo cambia si cambia el estado global (no una sesión nueva).
- Foco: obturador completamente electrónico del A6000. Decisión vigente S51:
  A=NO, B=NO, C=NO (sin ruta electrónica demostrada y sin parche justificable).

## Mapa del repo

- `firmware/extracted/fw321/firmware.fdat` — firmware A6000 3.21 (SHA-256
  `b60c845c…e56bb9`); `dev/nflasha3_unpacked_unpacked/av-cam.bin` (código, base `0x43541000`).
- `docs/STATE.md` — restricciones y política de REA. `docs/capture/` — informes por sesión.
- `knowledge/CURRENT.md` (estado breve), `knowledge/PROGRESS.md` (historial),
  `docs/CORRECTIONS.md` y `docs/OPEN-QUESTIONS.md` (generados).
- `scripts/knowledge/search.py` — `exact|text|tree|section|graph|trace|claim|ask`.
- `analysis/` — matrices de evidencia y artefactos por sesión.

## Estado vigente (S62)

- PMCA/`updatershell`: inyecta un fdat propio (cramfs con `libupdaterbody`), el
  updater lo ejecuta y expone shell USB `0x23` (`SHEL`, `PULL`, `PUSH`, `BK*`).
  `serviceshell` (senser + HASP) da terminal y backup `0x603`.
- `bk w 0x003e0005` escribe la propiedad BK4 `modelName` (subsistema `0x3e`/índice 5,
  16 B, attr solo-lectura) en `/setting` (`nflasha2`); NO es una dirección.
- El efecto «shell mode» al escribir `ILCE-6001` es NO VERIFICADO: esa cadena no
  existe en el firmware 3.21.
- IMX210: transporte y parámetros caracterizados; fin de exposición electrónico
  NO VERIFICADO. S51 se mantiene.

## Skills (resumen)

- `knowledge-navigation`: localizar símbolo/dirección/documento con `search.py`
  y citar ruta:línea.
- `contradiction-audit`: `search.py claim`/`graph` + `docs/CORRECTIONS.md`; nunca
  tratar `NO_VERIFICADO` como `VERIFICADO`.
- `knowledge-maintenance`: reindexar y reconstruir; el paso 5 debe repetir el total del paso 2.
- `session-checkpoint`: leer `PROGRESS.md`/`STATE.md` al reanudar; registrar una
  entrada breve con próximo paso exacto.

## Convención de respuestas

Español, tono directo. Citar archivo:línea. No declarar completado si queda algo
esencial pendiente; marcar lo no verificado como tal.
