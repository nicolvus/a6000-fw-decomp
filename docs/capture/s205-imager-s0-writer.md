# S205 — Escritor de `S[0]` y origen del bloque de modo IMX210 (G+0x224)

22-10-2026. Agente A (sensor y driver), sesión S205 (rango S200–S299). **Solo investigación estática; sin ejecutar firmware, sin cámara, sin flasheo.**

## Veredicto resumen

| Preguesta | Estado | Veredicto |
|---|---|---|
| ¿Quién escribe `S[0]` (selector de fila IMX210)? | **NO_VERIFICADO** | No localizado; S se accede vía puntero en registro (argumento de función), no por dirección absoluta. |
| ¿`0x43843a44` es código Thumb real? | **VERIFICADO** | Prólogo `push.w {r4-r8, sb, sl, fp, lr}`; función de staging que copia 4 bancos de 16 B. |
| ¿Origen del bloque de modo `G+0x224`? | **PARCIAL** | `0x43843a44` copia 4 bancos de 16 B desde `origen+0x2c` a `destino+0x64`; quién llena el origen no se cerró. |
| ¿REA resuelve `0x43843a44`? | **NO (antes)** / pendiente | S146: `not_in_procedure`. Ahora bytes confirman que es función real; REA no se consultó por API desconocida del daemon. |

## Contexto (S141/S146/S147, vigentes tras contradiction-audit)

- `S = 0x43eb35d0`, 0x148 B, BSS cero en la imagen; `memset` en `0x437b56b4` (S142).
- `S[0]` selecciona fila; fila en `S+4+16·S[0]`; copia de 16 B a `S+0xc4` (S141).
- `0x43843a44` prepara 4 bancos de 16 B (`S+4+16·banco`) desde `G+0x224` (`0x43eb07fc`) (S141).
- `0x43b0893c` copia la fila del banco `S[0]` a `S+0xC4..0xD0` (S141).
- `0x43849fb8` construye el bloque de exposición (S141).
- S142: xrefs directas a S son `0x437b56b4` (memset 0x148 B) y `0x437b59ce` (lee `S+0xda`). Ninguna escribe `S[0]`.
- S146: REA `resolve_containing_procedure(0x43843a44)` → `not_in_procedure`; `file-offset:` no permite seeding.

## Evidencia de bytes (S205)

### 1. `0x43843a44` es función de staging real (VERIFICADO)

Desensamblado de `0x43843a44` (Capstone, bytes originales):

```
0x43843a44: push.w {r4, r5, r6, r7, r8, sb, sl, fp, lr}
0x43843a48: mov r5, r3
0x43843a4a: ldr r3, [r0, #0x20]
0x43843a4c: sub sp, #0x1c
0x43843a4e: ldr r4, [pc, #0x370]     ; literal desde pool (dirección destino)
0x43843a56: add r4, pc               ; r4 = dirección destino
0x43843a5e: strb r3, [r4]            ; escribe byte en destino
...
0x43843af2: add.w r3, r7, #0x2c      ; r3 = origen + 0x2c (fila de modo)
0x43843af6: add.w lr, r8, #0x64      ; lr = destino + 0x64
0x43843afa: adds r7, #0x10
0x43843afc: add.w r8, r8, #0x10
0x43843b00: ldm r3, {r0, r1, r2, r3} ; carga 16 B desde origen+0x2c
0x43843b02: stm.w lr, {r0, r1, r2, r3}; almacena 16 B en destino+0x64
0x43843b06: add.w r1, r4, #0x6e
0x43843b0a: add.w r0, fp, #0xa4
0x43843b0e: movs r2, #6
0x43843b10: blx #0x439c5320          ; copia/memcpy de 6×2 B
0x43843b14: ldrh.w r3, [sl, #0x86]
...
0x43843b24: strh.w r3, [sb, #0xbc]
```

Interpretación: `0x43843a44` copia 4 bancos de 16 B (`0x10` de stride) desde un origen (bloque de modo, `G+0x224` + offset) hacia `S+4+16·banco+0x2c` (destino). Es el *builder* de filas de modo (coherente con S141/S147).

### 2. No hay slot GOT directo a S (VERIFICADO)

Barrido de palabras en el GOT (`0x44010000`–`0x44020000`): **0 slots** con valor `0x43eb35d0` (S). S no se accede por literal absoluto.

### 3. No hay store directo a S[0] como literal absoluto (VERIFICADO)

Barrido de instrucciones `str`/`strb`/`strh` en `0x436d5000`–`0x436daa00` (C_Imager), `0x4383a000`–`0x4383d000` (pipeline) y `0x43843a38`–`0x43843d00` (staging): **0 stores** a `0x43eb35d0` como literal absoluto.

S se pasa como puntero en registro (argumento de función `r0`), por eso no aparece como xref directo ni store a dirección absoluta.

### 4. Literales a G+0x224 (0/0)

Barrido de literales que apunten a `0x43eb07fc`: **0** en las regiones auditadas. El origen `G+0x224` se construye indirectamente (base G + offset), no por literal absoluto.

## Clasificación

| Campo | Escritor localizado | Subsistema | Clasificación en A6000 |
|---|---|---|---|
| `S[0]` (selector de fila) | NO (puntero en registro) | Pipeline de captura | NO_VERIFICADO |
| `S+4+16·banco` (bancos de fila) | `0x43843a44` (staging) | Modo de lectura | DISTINTO vs A7S (matriz estática) |
| `S+0xc4` (fila activa) | `0x43b0893c` | Lectura de fila | PARCIAL |
| Bloque de modo `G+0x224` | origen no cerrado | Modo de lectura | NO_VERIFICADO (origen) |

## Comparación A7S (IMX235) vs A6000 (IMX210) en este punto

- **A7S:** matriz de modos estática en `0x43fee370`/`0x43fee598` (34 modos × 35 registros); selector `0x43826d58` (drive mode `tipo==2` → Silent `0x4e`/`0x4f`, S201). No hay estructura `S` análoga recuperada.
- **A6000:** estructura `S` dinámica (`0x43eb35d0`) con `S[0]` como selector de fila; `0x43843a44` llena bancos desde `G+0x224`.

Clasificación: **DISTINTO** (arquitectura de selección de modo distinta; A7S usa matriz estática por modo, A6000 usa estructura S con selector dinámico).

## Límites

- Sin REA/Ghidra concluido para `0x43843a44` (daemon no se consultó por API de argumentos desconocida; autoanálisis Ghidra no terminó en el tiempo disponible). El análisis de bytes verifica que es función real, pero no cierra el dataflow completo de `S[0]`.
- `S[0]` se escribe vía puntero en registro; sin rastrear todos los callers de `0x43843a44` no se sabe quién le pasa el índice de fila.
- `G+0x224` se construye indirectamente (base + offset); el llenado del origen no se cerró.

## Artefactos

- `analysis/s205_imager_s0_writer/test_s205_s0_writer.py` (5 pruebas de bytes, en `analysis/`)
- `analysis/s205_imager_s0_writer/s0_writer_bytes.py` (análisis de staging)
- `analysis/s205_imager_s0_writer/s0_writer_deep.py` (barrido GOT/literales)
- `tests/test_s205_imager_s0_writer.py` (a crear)
- `docs/capture/s205-imager-s0-writer.md` (este informe)

## Siguiente (S206)

Tabla completa de los 119 registros sombra IMX210 (S56 rec_map) vs los 35 registros matriz IMX235 (S57), dirección por dirección y función por función; clasificación idéntico / distinto / ausente en A6000 por subsistema.
