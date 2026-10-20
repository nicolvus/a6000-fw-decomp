# S60 — validación cruzada

20-10-2026. Intercambio con GPT-6 Sol (`codex exec -m gpt-6-sol`, esfuerzo medium) y verificación independiente de Claude.

## Ejecuciones de Codex

| Ejecución | Sandbox | Resultado | Registros |
|---|---|---|---|
| Investigación IMX210 (A6000) | workspace-write | exit **1** al final por límite de uso; **entregables escritos antes del corte**: `docs/capture/s60-sol.md`, `tests/test_s60_sol.py` (6 tests OK al re-ejecutarlos), `analysis/s60/sol/`. Falta su mensaje final (`last-message.txt` no existe). | `analysis/s60/sol/run.log`, `exit.code` |
| Auditoría de hallazgos A7S/A6000 de Claude | read-only | exit **1**: «usage limit … try again at 5:56 PM» sin ninguna respuesta | `analysis/s60/sol-audit/` |

**No se obtuvo la auditoría de GPT.** Es una limitación de S60, no una conformidad. No se simuló. Queda pendiente repetir `analysis/s60/sol-audit/task.md` cuando se renueve el cupo.

## Verificación de Claude de los hallazgos de Sol (bytes A6000, SHA `b60c845c…bb9`; `analysis/s60/claude/verify_sol.py`)

| Afirmación de Sol | Resultado |
|---|---|
| Receptor `0x43806e38` llama a `0x438069f0` y libera (recv `0x3030f`, timeout −1) | ACEPTO (bytes). Es una tarea de mensajes. |
| Caso 4 → `0x43b00d94`; caso 3 → `0x43b00fe6`; caso 9 → `0x43b00f62`; ambos emisores llaman `0x43806400` (envío a `0x8003030f`) | ACEPTO (bytes). |
| Tabla TBH `0x43806a04`: caso 4 → `0x43806c24`, caso 10 → `0x43806d02` | **CORRIJO:** la base de `tbh` es `pc=0x43806a08`; entradas reales `0x43806c28` y `0x43806d06` (casos 3/9: `…bde`/`…cbe`). Los cuerpos citados (llamadas a `0x43b00d94/fe6/f62`) están dentro y coinciden: sin efecto en sus conclusiones. |
| Orden de publicación `d64→db4`, luego `e04→d64` | ACEPTO (desensamblado `0x43b00dd4..0x43b00e1a`). |
| Escritor último de `obj+e04` no localizado | MATIZO: `obj+e04` se alcanza por el accesor `0x43ae84da` (1 llamador, `0x4376682c`, que escribe **un byte**): el bloque `e04..e53` es un registro compuesto por muchos productores (S60-C8). Los 24 B `e20..e37` (= `payload+0x20`) tienen dos productores (S60-C7). |
| Tv/clk/N/svr/VdNum (S60-08..10) | No re-verificado en S60 (sin cupo de GPT para contraste); se hereda su clasificación PARCIAL/NO VERIFICADO. |
| «El bit 31 entre IDs no está resuelto» | ACEPTO: emisores usan `0x8003030f` y el receptor `0x3030f`; la semántica depende de la tabla OSAL del objeto en tiempo de ejecución. |

## Contradicciones y correcciones

- S60-01 de Sol (direcciones TBH) corregido arriba; sin cambio en conclusiones.
- Hallazgo propio **no** es confirmación de Sol: S60-C7/C8 son aportes de Claude sin auditoría de GPT.
- Se mantiene la clasificación S59 de `0x1000/0x1001` y se **eleva** de INFERENCIA a VERIFICADO su naturaleza de traza (S60-C1..C3): antes solo «más probable».
- Ninguna conclusión se da por buena por coincidencia entre modelos; todas las confirmadas tienen test reproducible.
