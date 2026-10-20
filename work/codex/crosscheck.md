# TASK2 — validación A7S/A6000 y DFE

Entradas inmutables: A7S `b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e`, A6000 `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`, DFE `fc4e314db24a72d584bd8795bd8f1144b003c97c390cb143d09b840b38bf9fcd`. Todas las direcciones de `av-cam` son Thumb con base `0x43541000`.

| Afirmación | Veredicto | Evidencia de bytes/instrucciones |
|---|---|---|
| 1. Fila LIRO `0x40e3` y stores de `payload[8]` | **CONFIRMADO** (handler); **NO VERIFICADO** (que la fila sea `0x40e3`) | A7S `0x437a9cb0`: `ldrb r2,[r0,#8]`, `add r3,pc`, `str.w r2,[r3,#0x250]`, con base efectiva `0x43ea1d84`. A6000 `0x438032d4` es idéntico con `#0x238`, base `0x43edf684`. No se recuperó la tabla que enlaza el ID. |
| 2. Conversor Silent A7S | **CONFIRMADO** | `0x4379ec04..56` lee `cap+0x4b84`, `+0x785`, compara `cap+0x1e0` con `0x19`; tabla `0x43bc1658` contiene `[0,2]`; si el diagnóstico `g+0x7a` es no nulo retorna 2. Las rutas citadas son **parciales**: `0x43826dc0` lee `cap+0x78c`, llama al conversor y almacena `cap+0x4d0`; la función `0x437b6f74` no fue verificada en esta pasada. |
| 3. Selector de modo | **CONFIRMADO** | A7S `0x43826d64`: `cmp r2,#2`; sub=0 retorna `0x4e` (`0x...6d7c`) y sub=1 `0x4f` (`0x...6da6`). `0x43826dc0..e04` pasa `cap+0x1e0,+0x6d0,+0x78c` y escribe `cap+0x4d0`. A6000 `0x437f7f98` solo compara r0/r1; su llamador `0x437f7ff4` pasa dos argumentos y escribe `+0x4d0`. |
| 4. Política de clase | **CONFIRMADO** | A7S `0x438649f0..fc`: `ldr.w r2,[r7,#0x404]; cmp #2;` salta a la ruta que almacena clase 0 antes de leer `r7+0x424` (`0x...49fe`). A6000 `0x43842158..e8` pasa de las guardas a `r7+0x41c`; no hay lectura `+0x404` en ese bloque. |
| 5. IMX235/IMX210 | **CONFIRMADO** | La lista A7S `0x43fee370` contiene 34 valores; índices 29–32 = `4e,4f,50,51`. `0x436f3928` indexa remap `0x43c9c5b5` y recorre filas de 20 B desde `0x43fee598`. A7S `0x436f4168` lee `param+9`; tras `cmp #4`, `tbb [pc,r6]` usa tabla en `0x436f4246`: caso 2 llega a `0x436f42fc`, que carga el literal que resuelve a la cadena `ShutMode:%d is not supported` en `0x43c9c96f`. A6000 `0x436d70be..c6` también acepta 0..4 mediante `tbb`; por tanto no tiene esa guarda de rechazo para 2. |
| 6. Escritor de `banco+0x404` | **CONFIRMADO** (copia), **NO VERIFICADO** (tipo Silent) | A7S `0x43862f18..1c`: `ldr.w r3,[r6,#0x76c]`; `str.w r3,[r7,#0x404]`. Esta pasada no demuestra que `r6+0x76c` sea `src+0x1f8` ni que codifique Silent; no se le asigna semántica. |

## DFE

| Pregunta | Resultado |
|---|---|
| Cargador A6000 `/usr/dfe/dfe.bin` | **NO VERIFICADO.** La cadena está en `av-cam` A6000 `0x43cd1b98`. El escáner de parejas Thumb `ldr literal; add pc` no obtuvo referencia directa; eso no descarta otra forma PIC, referencia indirecta o cargador externo. A7S contiene cadenas `DFECore`, `DFE_INT`, `DfeCpuKickRcvSgc` y `SubLVDS`, pero no una cadena equivalente `/usr/dfe/dfe.bin`. |
| Dispatcher/memoria compartida del DFE | **NO VERIFICADO para semántica.** REA (raw ARM `0x01000000`) detectó 83 procedimientos. El vector 0 salta mediante literal a `0x01005870`; el arranque pone registros a cero, inicializa pilas por modo CPU y llama a rutinas de cache. Esto acredita código ARM arrancable, no IDs host ni mailbox. No se atribuye comando alguno a lectura, disparo o VD. |
| Host DFE en ruta foto y 0x4e/0x4f | **NO VERIFICADO.** Las rutas A7S producen y almacenan esos valores; esta evidencia no alcanza una función que los empaquete para DFE ni un consumidor DFE. No hay comparación de comando DFE A7S/A6000 justificable. |

## Reproducción

```bash
python3 work/codex/scripts/task2_probe.py
llvm-objdump --triple=thumbv7-none-eabi -d --no-show-raw-insn \
  --start-address=0x43862e80 --stop-address=0x43863020 work/claude/input/a7s-av-cam-view.elf
rg -aob '/dfe/dfe.bin' work/claude/input/a6000-av-cam.bin
```

REA se aplicó al artefacto pequeño DFE como ARM raw con entrada/base `0x01000000`; no se abrió REA sobre `av-cam`.
