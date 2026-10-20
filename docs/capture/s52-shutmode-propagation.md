# S52 — Propagación de la clase 0 hasta ShutMode (`param+9`) en A7S 3.20 (consolidado, 19-10-2026)

Agente A propuso la cadena; Agente B la dejó **PARCIAL** por una única identidad no demostrada; el coordinador la resolvió por
instrucciones (abajo, paso 5). Estado final: **VERIFICADO estático**, con dos condiciones de ejecución como INFERENCIA.

| # | Paso | Instrucciones (A7S, base `0x43541000`, Thumb) | Estado |
|---|---|---|---|
| 1 | Política: tipo 2 ⇒ clase 0 | `0x438649f0 ldr.w r2,[r7,#0x404]; cmp r2,#2` → `0x43864a48 str r1,[r2,#0x5c]` con `r1=0`, `r2=G=0x43f06bc8` (literal `0x43864bd8` + PC) | VERIFICADO (A, B, coordinador). B había dado `0x43f06d5c..98` (PC mal aplicado) y lo corrigió en R2 |
| 2 | Getter | `0x43864c74: ldr r0,[G,#0x5c]; bx lr` | VERIFICADO |
| 3 | Copia global | único llamador `0x43861bfc` copia a `0x43f04c8c` | VERIFICADO (A, B: CONFIRMADO tramo) |
| 4 | Registro de fotograma | `0x4386347a ldr r3,[0x43f04c8c]; 0x4386347c strb.w r3,[r8,#0x69]`; `r8` = `0x43861f58(cap+0x1c0, cap+0x1b8)` (`0x438633f0..43863402`) | VERIFICADO |
| 5 | Copia al parámetro | `0x43862158`: `R = 0x43861f58(cap+0x1c0, cap+0x1b8)` (`0x43862184..8c`); `ldm R+0x60 → stm *[r6]` (12 B) ⇒ `param+9 = R+0x69` | VERIFICADO |
| 5b | Identidad de R (discrepancia A/B) | `0x43861f58` devuelve uno de **dos buffers estáticos** vía GOT: `0x43eb7f0c` o `0x43f0552c`, según `0x43b0b900(arg0)` y `arg1&1`; pasos 4 y 5 la llaman con **los mismos argumentos** | VERIFICADO estructura (coordinador); que el estado de selección no cambie entre ambas llamadas: INFERENCIA |
| 6 | Llamador | `0x43b1c8c0: [sp]=cap+0x648` → `0x43b1c8e2 bl 0x43862158` → `0x43b1c8e8 ldrb r3,[cap+0x648+9]; str [cap,#0x4cc]` ⇒ `param+9 = cap+0x651` | VERIFICADO |
| 7 | Override | `0x438b775c` fuerza `cap+0x651=0` si `0x439fb708()∈{2,3}` (igual A6000 `0x438c82bc`): ShutMode 0 existe **fuera** de Silent | VERIFICADO (A); condición semántica NO VERIFICADO |
| 8 | SetExposure | `0x438b77a4 add r1,r4,#0x648` → `0x438b77ac bl 0x436f2938` → `ldr r0,[r0]; ldr r3,[r0]; ldr r3,[r3,#0x28]; blx r3` | VERIFICADO |
| 9 | Despacho | vtable `C_ImagerCtrl_IMX235` `0x43fce050+0x28 = 0x436f4169` → `0x436f4198 ldrb.w r6,[r10,#9]`; `cmp r6,#4; bhi; tbb` | VERIFICADO (A, B); que el objeto en tiempo de ejecución sea IMX235: INFERENCIA fuerte (único imager de la A7S) |

Condicionales: la copia de `0x43862158` se salta si `[GOT]` byte0==0 y byte `+0x15`==0 (`0x4386216e..76`): condición de ejecución NO VERIFICADA.

## A6000

Mismo contrato: `0x4383fd6c` (≙ `0x43862158`), wrapper `0x436d6320` → vtable IMX210 `0x43fcc090+0x28 = 0x436d6f6d` → `0x436d6fb6 ldrb.w r9,[r1,#9]`.
La política A6000 `0x43842158` no produce clase 0 por la rama normal; overrides `+0x36/+0x37` (S50) y `0x438c82bc` sí pueden dar 0.
Quién produce `param+9=0` en A6000 en uso normal (vídeo/LV/AF/ráfaga/servicio): **NO VERIFICADO** (B3).

## Hipótesis H52-3

**VERIFICADO (estático):** el valor de clase 0 llega sin transformación (`strb` del byte bajo) a `param+9` del SetExposure IMX235.
Residual: estado del selector entre llamadas, condición de `0x4386216e`, tipo dinámico del objeto. Tests: `work/claude/tests/test_s52_curtain_facts.py`,
`work/claude/tests/test_s52_xcheck.py`, `work/codex/s52/test_s52_shutmode_facts.py`.
