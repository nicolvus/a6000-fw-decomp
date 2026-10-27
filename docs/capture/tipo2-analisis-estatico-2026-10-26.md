# Seguimiento estático de `G+0x784` (tipo de obturador) en `av-cam.bin` — 26-10-2026

Motivo: T020 demostró que forzar `G+0x784`=2 no cambia el obturador. Se busca dónde se consume el valor.
Método: barrido de bytes de `av-cam.bin` (base `0x43541000`) por `ldr/str.w [rN,#0x784]` + desensamblado con capstone (Thumb). Las coincidencias con `rn=r15` son cargas de literal, descartadas.

## Accesos reales a `G+0x784` (VERIFICADO por bytes)
| Dirección | Tipo | Nota |
|---|---|---|
| `0x4378fb94` | escritura (a 0) | init de G, junto a `+0x780`, `+0x788` |
| `0x43793182/96`, `0x437931b6`, `0x4379323a/70/82/96` | escrituras | selector (`0x4379316a`) y ramas |
| `0x4378f5bc`, `0x4378f5c8` | lectura | pasa `G+0x784` (r0) y `G+0x778` (r1) a `0x4378dfdc`; en la rama alternativa (`+0x780`≠0 y `[..]≠0x807`) usa otra copia |
| `0x43737228` | lectura | suma `+0x784 + +0x780` en un cálculo de parámetros de otro objeto (r4) |
| `0x43ab8a78` | falso positivo | llamada por vtable (offset 0x784 de una tabla), no es G |

## Consumidor: `0x4378dfdc(tipo, arg)` (VERIFICADO)
- Compara `tipo` con el anterior; si cambia, desarma el modo previo y arma el nuevo.
- tipo 1 → `0x4359f174(3)` → `0x4359fd90`; tipo 2 → `0x4359eed0(3,0)` → `0x4359f4f8`; tipo 0 → desarma (`0x4359f12c`/`0x4359ee78` según el anterior).
- Registra eventos `0x2012`–`0x2016` (`0x43901a8c`) y guarda el resultado en variables globales; luego consulta `0x4359ecc0` y `0x4378dda0`.
- `0x4359fd90`/`0x4359f4f8`/`0x4359f5f4` operan sobre una tabla de 10 entradas (8 B) de un gestor de recursos/temporizadores (`0x435611b8`, `0x4359f87c`): no construyen ninguna orden CAIF ni escriben MMIO del obturador.

## Conclusión (INFERENCIA, con límite)
El tipo 2 llega hasta un gestor de recursos del módulo `0x4359xxxx` que se arma/desarma por tipo (1 y 2 usan rutas distintas, 0 las desarma). En ese tramo no aparece ninguna decisión que cambie el obturador físico, coherente con T020. La orden hacia Darwin no se arma en este camino; el siguiente paso sería identificar quién consume la "variable global" que guarda `0x4378dfdc` (y `0x4378dda0`) y dónde se arma la orden de captura. NO_VERIFICADO que el bit `0x20` se pierda aquí o en Darwin.
