# S334 — Los 12 pares se colapsan en máscaras `u16` (carril B)

> **Aviso D4 (25-10-2026):** [S340](s340-w0-selector.md) rectifica `w0` como «código de operación»: es un selector de canal MMIO (`0x436f74c0`).

22-10-2026. Carril B. Sesión S334. **Solo lectura estática; sin firmware en ejecución, sin cámara, sin flasheo.**

## Pregunta

S331 dejó tres bloques de 12 pares `(flag, byte)` en `obj+0x16`, `obj+0x2e` y `obj+0xa5`. ¿Qué los consume y qué representan?

## Veredicto

| Afirmación | Clasificación | Evidencia |
|---|---|---|
| El segundo byte del par **no es un offset de estado**: es un **índice de bit** | **VERIFICADO** | `0x43ada370`: `ldrb r4,[r1,r2]` (flag), `ldrb r4,[r4,#1]`, `lsls.w r4, r5(=1), r4`, `orrs`, `uxth` |
| Los 12 pares se **colapsan en una máscara `u16`** | **VERIFICADO** | Bucle `r2 = 0,2,…,0x16` (`cmp r2,#0x18`); resultado en `obj+0x68` (`strh.w r0,[r3,#0x68]`) |
| Variante con destino: `0x43ada402(obj, pares, dst, op)` guarda la máscara en `[dst]` | **VERIFICADO** | `strh r5,[r2]` y tail `0x436f822c` |
| `0x436f61f8` colapsa `obj+0x16 → obj+0x68` y `obj+0xa5 → obj+0xf8` (op 1) | **VERIFICADO** | `add.w r1,r4,#0x16` + `bl 0x43ada370`; `#0xa5`/`#0xf8`/`r3=1` + `b 0x43ada402` |
| `0x436f60ac` aplica la máscara de `obj+0x68` con op 0 | **VERIFICADO** | `add.w r1,r4,#0x68`, `movs r2,#0`, `bl 0x436f81b4` |
| El `w0` de T1/T2 es un **código de operación** (T1: 0/1, T2: 2/3) | **VERIFICADO** | `0x436f5eac`: `muls r2,r5,#0x1c`, `ldr r2,[r3,r2]`, `cmp r2,#1` / `cmp r1,#2` / `cmp r1,#3` |
| `0x436f822c` aplica la máscara (lectura, `~valor ^ máscara`, escritura) | **VERIFICADO (forma)** | `bl 0x436f82b0` / `0x436f8314`, `mvns`, `eors`, `uxth`, `bl 0x436f82a0` |
| Qué hay detrás de `0x436f8290/82a0/82d0/82e8/8300/8314/8324` (¿MMIO? ¿P2S?) | **NO_VERIFICADO** | No resuelto en esta sesión |

**S51 no cambia (A = NO, B = NO, C = NO).**

## 1. Colapso de pares en máscara

```
0x43ada370: movs r2, #0
0x43ada372: mov r3, r0            ; obj
0x43ada374: mov r0, r2            ; acumulador = 0
0x43ada378: ldrb r4, [r1, r2]     ; flag del par
0x43ada37a: cbz r4, 0x43ada38a
0x43ada37c: adds r4, r1, r2
0x43ada37e: movs r5, #1
0x43ada380: ldrb r4, [r4, #1]     ; byte del par = índice de bit
0x43ada382: lsls.w r4, r5, r4     ; 1 << índice
0x43ada386: orrs r0, r4
0x43ada388: uxth r0, r0
0x43ada38a: adds r2, #2
0x43ada38c: cmp r2, #0x18         ; 12 pares
0x43ada38e: bne 0x43ada378
0x43ada390: strh.w r0, [r3, #0x68]  ; máscara de 16 bits
0x43ada3a0: b.w 0x436f822c        ; aplicar
```

La misma forma con destino variable en `0x43ada402` (`strh r5,[r2]`).

Consecuencia: el «valor» que las tablas T aportan no es un dato del sensor, sino **qué bit** se activa en una máscara de 16 bits, y solo para los campos habilitados por la máscara de 12 bits de la fila.

## 2. Quién consume los bloques

| Bloque | Colapsa en | Quién | Op |
|---|---|---|---|
| `obj+0x16` | `obj+0x68` | `0x436f61f8` → `0x43ada370` | 0 |
| `obj+0xa5` | `obj+0xf8` | `0x436f61f8` → `0x43ada402` | 1 |
| `obj+0x68` | — | `0x436f60ac` → `0x436f81b4` | 0 |
| `obj+0x2e` | (no se le ha visto colapsar en esta sesión) | — | — |

## 3. Códigos de operación por modo

`0x436f5eac(obj, posición, flag)` lee el `w0` de T1 y de T2 para la fila del modo:

| Modo | `T1.w0` | `T2.w0` | `T3.w0` | Máscaras T1/T2/T3 |
|---|---:|---:|---:|---|
| `0x4c` | 0 | 2 | 4 | `0x3ff` / `0x3ff` / `0xfff` |
| `0x4d` | 0 | 2 | 4 | `0x3ff` / `0x3ff` / `0xfff` |
| `0x4e` | 0 | 2 | 4 | `0x3ff` / **0** / `0xfff` |
| `0x4f` | 0 | 2 | 4 | `0x3ff` / **0** / `0xfff` |
| `0x50` | **1** | **3** | 4 | `0x3ff` / 0 / `0xfff` |
| `0x51` | **1** | **3** | 4 | `0x3ff` / 0 / `0xfff` |
| `0x0b` | 0 | 2 | 4 | `0x3ff` / 0 / `0xfff` |

El vocabulario `w0` medido es T1 ∈ {0,1}, T2 ∈ {2,3}, T3 = 4. La diferencia entre los pares silent (`0x4c`/`0x4d` frente a `0x4e`/`0x4f`) sigue siendo la **máscara de T2**; `0x50`/`0x51` son los que cambian de código de operación.

## 4. Aplicación de la máscara

`0x436f822c(obj, máscara, op)`:

- `op = 0`: `0x436f82b0` (lectura) → `~valor ^ máscara` → `uxth` → `0x436f82a0` (escritura) → `0x436f8290(máscara)` → `0x436f82d0(byte[4])`.
- `op = 1`: `0x436f8314` (lectura) → mismo xor → `0x436f8300` → `0x436f82e8`.
- `op = 2` u otro: solo traza (`0x438f7114`).

La forma es un **read-modify-write de 16 bits por campo**, pero la capa de acceso (`0x436f82xx`) no se ha resuelto: no se afirma que sean MMIO ni que lleguen al sensor.

## Límites

- Solo estático: no se ejecuta el flujo.
- La semántica de `0x436f8290/82a0/82d0/82e8/8300/8314/8324` queda **NO_VERIFICADA**.
- El índice de bit sale del objeto `0x43dc02e0` en runtime: el mapeo campo→bit no está verificado.
- Que las máscaras acaben en una trama P2S es INFERENCIA.
- S51 (A/B/C) no cambia.

## Reproducción

```bash
.venv/bin/python analysis/s334_pair_dataflow/build_pair_dataflow.py
.venv/bin/python analysis/s334_pair_dataflow/verify_pair_dataflow.py  # 111 comprobaciones
.venv/bin/python -m unittest tests.test_s334_pair_dataflow             # 9 tests
```

Artefactos: `analysis/s334_pair_dataflow/pair_dataflow.json`, `build_pair_dataflow.py`, `verify_pair_dataflow.py`, `tests/test_s334_pair_dataflow.py`.
