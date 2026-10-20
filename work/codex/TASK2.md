# Tarea 2 Agente B (Codex) — validación cruzada + DFE

Mismas restricciones que TASK.md. Escribe solo en `work/codex/`. NO uses el MCP `rea` sobre `av-cam.bin`
(agota 330 s); para av-cam usa LLVM (`llvm-objdump --triple=thumbv7-none-eabi`, ELF con `.text` en 0x43541000:
`work/claude/input/a7s-av-cam-view.elf`, `work/claude/input/a6000-av-cam-view.elf`, solo lectura) y Python propio.
Para `dfe.bin` (64 KiB) el MCP `rea` directo sí es viable (raw ARM, base 0x01000000).
Puedes leer `work/claude/scripts/*.py` pero escribe tus propios scripts en `work/codex/scripts/`.

## A. Validación independiente (refuta o confirma cada una con bytes/instrucciones)
Afirmaciones del Agente A (Claude), A7S 3.20 av-cam sha256 b857d338…103e, A6000 3.21 b60c845c…6bb9:
1. Tabla de mensajes LIRO: fila `0x40e3` → A7S handler `0x437a9cb0` guarda `payload[8]` en `0x43ea1d84+0x250`;
   A6000 handler `0x438032d4` guarda en `0x43edf684+0x238`.
2. A7S `0x4379ec04` (conversor Silent): tabla `0x43bc1658` = {0,2}; anulación diagnóstica fuerza 2; guardas
   `cap+0x4b84`, `cap+0x785`, `cap+0x1e0==0x19`. Llamadores `0x437b6f74` (→`[g+0x7e8]`) y `0x43813e94` (→`cap+0x78c`, y si 2, `cap+0x748=1`).
3. A7S selector `0x43826d58(modo, sub, tipoSilent)`: tipo 2 → `0x4e`/`0x4f`; A6000 `0x437f7f98(modo, sub)` sin rama Silent.
   Llamado desde A7S `0x43826dc0` / A6000 `0x437f7ff4`, que escriben `captura+0x4d0`.
4. Política de clase A7S `0x438649bc`: si `banco+0x404==2` → clase 0 (antes de EFCS `+0x424`); A6000 `0x43842158` no tiene esa rama.
5. IMX235: vtable `0x43fce050`, SetMode `0x436f3b44` busca en lista de 34 modos `0x43fee370` (incluye 4e/4f/50/51);
   aplicador `0x436f3928` usa remap `0x43c9c5b5` y filas de 20 B en `0x43fee598`; 4e/50→columna 12, 4f/51→columna 13.
   SetExposure `0x436f4168`: ShutMode (param+9) 0,1,3,4 válidos, 2 → "ShutMode:%d is not supported".
   IMX210 SetExposure `0x436d6f6c`: ShutMode 0..4 todos válidos.
6. ¿Qué escribe `banco+0x404` en A7S (`0x43862f1c`: `banco+0x404 = r6+0x76c`)? ¿Es el tipo Silent? Traza `+0x76c` / `src+0x1f8`. NO resuelto por A.

## B. DFE (tu especialidad)
1. Quién carga `/usr/dfe/dfe.bin` en A6000 (xref PIC a `0x43cd1b98`: patrón `ldr rX,[pc,#i]; add rX,pc`). ¿Existe código host
   equivalente en A7S (misma función sin la cadena, o con otra fuente)? ¿Hay cadenas "ROM"/"boot" DFE en A7S?
2. `dfe.bin` A6000: dispatcher de comandos desde el host (tabla de saltos, IDs), memoria compartida/mailbox.
   ¿Algún comando relacionado con modo de lectura / disparo / VD? No inventes semántica.
3. Host DFE en av-cam: funciones que envían comandos al DFE en la ruta de captura foto; ¿difieren A7S/A6000 en drive_mode 0x4e/0x4f?

Entregables: añade `crosscheck.md` (tabla afirmación → CONFIRMADO/REFUTADO/NO_VERIFICADO + evidencia) y actualiza tus
archivos y `codex_evidence.json`. Resumen final ≤15 líneas.
