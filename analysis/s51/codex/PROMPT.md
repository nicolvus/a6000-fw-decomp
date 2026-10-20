# S51 — Investigador Codex: pruebas T2 y T3 (decisión SÍ/NO)

Directorio: /home/nicolas/Documents/a6000 (proyecto `sony-a6000-electronic-shutter/`). Lee primero
`sony-a6000-electronic-shutter/analysis/s51/PLAN.md` (criterios prerregistrados, presupuesto) y, como antecedente,
`docs/capture/s50-parallel-conclusions.md` y `docs/capture/s50-codex-exposure-curtains.md` (tu informe anterior),
`s44-register-consumer-mode-table.md`, `s45/s46`. Usa el MCP de conocimiento antes de releer docs. No leas PROGRESS.md.

Claude hace T1 (modo 0..7/B/G → ModeRsvParam/C_Imager). **Tú haces T2 y T3, nada más:**

- **T2**: para ID1, ID100, ID101 (destinos de `SetExposure` caso 2, `436d7114..714a`) obtén la traducción ID → dirección
  de registro del sensor o campo de trama serie (tabla de S44 `43fe995c`, 119 pares ID u16/byte+2, empaquetado
  `436d5ed0`/`436d5f60`), y la fuente del selector `param+9` en captura fija (quién llama a SetExposure con 2).
  Si no existe documento legítimo del IMX210, NO asignes significado: di exactamente qué dato falta.
- **T3**: localiza la emisión del cierre de 2ª cortina en foto fija (Darwin P4E `2ND_CURTAIN_MG` / evento LIRO /
  MMIO `0xf2910048+banco*0x100`, `43b5e2b0`) y enumera TODAS sus condiciones de guarda. Decide: ¿alguna depende de un
  flag configurable (modo 0..7 `0x43eefb1c+0x60`, `C+0x94`, EFCS, `captura+74f`)? SÍ/NO con instrucciones.

## Herramientas y presupuesto
- Presupuesto: ≤ 60 min de trabajo. Regla de parada del PLAN: no amplíes referencias una vez cumplido el criterio.
- REA: hay UNA sesión compartida ya abierta (o abriéndose) por Claude. NO arranques otra ni la cierres. Espera a
  `sony-a6000-electronic-shutter/analysis/s51/shared/run/rea.sock.ready` y consulta por lotes:
  `python3 sony-a6000-electronic-shutter/analysis/rea-independent/bin/q.py sony-a6000-electronic-shutter/analysis/s51/shared/run/rea.sock guion.json salida.jsonl`
  (guion = lista JSON de {"tool","args"}). Lotes pequeños; la sesión la comparte Claude.
- LLVM: `sony-a6000-electronic-shutter/analysis/s51/shared/av.dis` (`.text` de av-cam, Thumb, direcciones absolutas,
  base 0x43541000; 3,7 M líneas: usa grep/awk, no lo cargues entero). Binario: `analysis/rea-independent/input/av-cam.bin`.
- REA no cubre muchas Thumb impares: respáldate en bytes/LLVM. Ghidra histórico `silent-liro.gpr` solo lectura y solo si
  es decisivo (RAM justa: avisa en el inbox antes).
- Consulta vacía de REA ≠ ausencia.

## Reglas
- Escribe SOLO en `analysis/s51/codex/` y `docs/capture/s51-codex-t2-t3.md`. No toques CURRENT.md, PROGRESS.md, grafo
  ni `analysis/s51/claude/`. Sin commits, sin push. Prohibido modificar/ejecutar/flashear firmware o tocar `silent-liro.*`.
- Clasifica: VERIFICADO / PARCIAL / INFERENCIA / NO_VERIFICADO, con función, instrucciones y evidencia.
- Mensajes para Claude: añade líneas a `analysis/s51/shared/inbox-for-claude.md`; lee `inbox-for-codex.md` de vez en cuando.
- Checkpoint en `analysis/s51/codex/CHECKPOINT.md` tras cada prueba.
- Informe final `docs/capture/s51-codex-t2-t3.md`, breve: para T2 y T3 → respuesta SÍ/NO o dato exacto que falta,
  evidencia principal (direcciones+instrucciones), rutas descartadas, tiempo y memoria. Autónomo, sin preguntas.
