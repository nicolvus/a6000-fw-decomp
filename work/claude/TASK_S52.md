# S52 — Agente A (Claude): cortinas, secuenciador y `captura+0x748`

Directorio exclusivo: `work/claude/` (scripts nuevos en `work/claude/s52/`). No escribas fuera salvo lectura.
NO empieces de cero: lee primero `docs/capture/a7s-silent-reconstruction.md`, `work/claude/a7s_silent_execution_trace.md`,
`work/claude/a7s_shutter_modes_comparison.md`, `work/codex/crosscheck.md`, `docs/capture/s50-parallel-conclusions.md`,
`docs/capture/s51-decision.md`, `docs/capture/efcs-capture-selector.md` (A6000) y `docs/STATE.md` § Política de ingeniería inversa.
Usa el sistema de conocimiento (`scripts/knowledge/`, MCP `sony-a6000-knowledge`) para localizar hallazgos A6000 previos
(VD_Pre/VD_Sequence/VD_Post/VD_Drive, CAMERA_MAIN_SYNC, DFECore, cortinas, `0x4383fd6c`, override `+0x36/+0x37`).

## Entradas (solo lectura; hashes en `analysis/s52-hashes.initial.sha256`)
- A7S 3.20 `work/claude/input/a7s-av-cam.bin` / `a7s-av-cam-view.elf` (base `0x43541000`, Thumb).
- A6000 3.21 `work/claude/input/a6000-av-cam.bin` / `a6000-av-cam-view.elf`.
- Herramientas: LLVM (`work/claude/scripts/dis.sh`, escáneres `pcrel_scan.py`, `movwt_scan.py`, `ldst_imm_scan.py`),
  Python con capstone/unicorn en `~/.venvs/re/bin/python`, REA vía daemon.

## REA (sesión propia, no compartida)
```bash
nohup python3 analysis/rea-independent/bin/session_daemon.py work/claude/run/rea.sock '{"path":"<ruta abs a firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin>","format":"raw-binary","architecture":"arm","entry_point":"0x43541000"}' > work/claude/run/daemon.log 2>&1 &
# espera work/claude/run/rea.sock.ready (~8-10 min en frío); luego por lotes:
python3 analysis/rea-independent/bin/q.py work/claude/run/rea.sock lote.json salida.jsonl
python3 analysis/rea-independent/bin/q.py work/claude/run/rea.sock --shutdown   # al terminar
```
`REA_GHIDRA_STARTUP_TIMEOUT_MS=900000` ya lo pone el daemon; si necesitas más RAM exporta `GHIDRA_MAXMEM=5G REA_DAEMON_RSS_MAX_MB=6000`
solo si `free -g` muestra ≥4 GiB disponibles (Codex corre otra sesión REA en paralelo). Un timeout o consulta vacía NO prueba ausencia.
Mientras REA arranca, avanza con LLVM/bytes. Todo hallazgo decisivo: verificado contra instrucciones LLVM y bytes.

## Objetivos (detalle completo en el encargo del usuario; resumen operativo)
- **A1** Productores/consumidores de `captura+0x748` (A7S): no solo el offset literal; punteros ajustados (`cap+0x700`+0x48, etc.),
  copias memcpy a estructuras derivadas, callbacks/virtuales. Preguntas: quién lo escribe, quién lo lee, si se copia al secuenciador,
  si se consulta antes de controlar el obturador, si cambia orden de eventos o habilita/inhibe un callback físico, si toca la secuencia VD,
  o si es solo informativo. No atribuyas semántica sin efecto demostrado.
- **A2** Desde la política `0x438649bc`: dónde se guarda la clase (0/1/3/5) y TODOS sus consumidores; por clase: funciones, parámetros,
  callbacks, eventos, temporizadores, escrituras a registros, interrupciones, salidas. No confundas nº de callbacks con clase (corrección S50).
- **A3 (máxima prioridad)** Subsistema que controla físicamente cortinas (1ª/2ª), motor/actuador, magnet/solenoide, GPIO, potencia,
  temporizadores de obturación, sensores de posición, rearme/charge. Cadenas/RTTI (`Shutter`, `Curtain`, `Mech`, `Front`, `Rear`, `First`,
  `Second`, `Drive`, `Motor`, `Magnet`, `Charge`, `Sequence`, `VD`, `Exposure`) y funciones sin símbolo.
  **Prueba central:** ¿la ruta de clase 0 omite llamadas/eventos/escrituras MMIO que sí ocurren con clase 1/3? Identifica función,
  condición, ruta 0, ruta 1/3, diferencia, destino físico/controlador y la evidencia de esa identidad. Una llamada omitida sin efecto
  identificado NO prueba cortina inmóvil.
- **A4** Equivalentes A7S de VD_Pre/VD_Sequence/VD_Post/VD_Drive/CAMERA_MAIN_SYNC/DFECore: cómo cambia Silent la preparación,
  integración, inicio de lectura, interrupciones, fin de exposición, sincronización de obturador. Tareas asíncronas ⇒ no reconstruir
  cronología solo por orden de instrucciones.
- Compara cada componente encontrado con A6000 (existe / falta / difiere), por bytes/instrucciones.

## Entregables (en `work/claude/`)
`s52_curtain_control_trace.md`, `s52_silent_flag_consumers.md`, `s52_shutter_class_callgraph.dot`, `s52_vd_sequence_comparison.md`,
`s52_mmio_curtain_map.csv`, `s52_evidence.json`. Con direcciones, offsets, fragmentos ASM, xrefs y cómo reproducir.
Además: test nuevo independiente `work/claude/tests/test_s52_curtain_facts.py` (no modifiques `test_a7s_silent_facts.py`), que
compruebe bytes/destinos de salto/offsets/condiciones de rama de tus afirmaciones VERIFICADAS con LLVM/capstone sobre las copias de entrada.
Para hipótesis H52-1, H52-2, H52-6: evidencia a favor/en contra, confianza, incógnitas, próxima comprobación, estado
(VERIFICADO/INFERENCIA/HIPÓTESIS/DESCARTADO/NO VERIFICADO). Mantén un checkpoint vivo en `work/claude/s52/CHECKPOINT.md`
(funciones ya analizadas, callejones sin salida) para poder reanudar.

## Prohibido
Flashear, ejecutar firmware real, modificar binarios originales, `silent-liro.*`, `analysis/ghidra`, informes consolidados, `git push`,
escribir en `work/codex/`. Si una línea llega a frontera estática, documenta exactamente qué falta y pasa a la siguiente.
Error histórico: `0x43826dc0` llama al selector de drive_mode, no al conversor; los llamadores del conversor `0x4379ec04` son
`0x437b65a0` y `0x43813d90`.
