# S340 — `w0` es un selector de registro MMIO (carril B)

22-10-2026. Carril B. Sesión S340. **Solo lectura estática; sin firmware en ejecución, sin cámara, sin flasheo.**

## Pregunta

S334/S336 dejaron `w0` (primer `u32` de cada fila de T1/T2/T3) como «código de operación» sin interpretar. ¿Qué hace exactamente?

## Veredicto

| Afirmación | Clasificación | Evidencia |
|---|---|---|
| `0x43ada4d8` es un *tail-call* a `0x436f74c0`, que hace `tbb [pc,r1]` con **6 casos** y valida `r1 ≤ 5` | **VERIFICADO** | `cmp r1,#5; bhi → log y 0`; `tbb [pc,r1]`; tabla `03 06 09 0c 0f 12` |
| Cada caso lee **un registro MMIO distinto**: `0xf3122300`, `0xf3122200`, `0xf3123300`, `0xf3123200`, `0xfc0a3100`, `0xfc0a4100` | **VERIFICADO** | Literales de cada rama (6/6) |
| El desplazamiento es `+0x30` en 4 casos y `+0x24` en 2 | **VERIFICADO** | `ldr r0,[r3,#0x30]` (casos 0, 2, 4, 5) y `#0x24` (casos 1, 3) |
| `0x436f605c` **suma** la lectura seleccionada por `w0` de T1 y de T2, y devuelve `u16` | **VERIFICADO** | Dos `ldr r1,[r3,r5]`, dos `bl 0x43ada4d8`, `adds r0,r0,r6`, `uxth` |
| `w0` medido: T1 ∈ {0,1}, T2 ∈ {2,3}, T3 = 4 | **VERIFICADO** | Tablas `0x43bbeb70`/`0x43bbf2e8`/`0x43bbef30` por posición de modo |
| **Qué mide** cada canal | **NO_VERIFICADO** | Sin datasheet; no se conoce el bloque `0xf3122xxx` ni `0xfc0a3xxx/4xxx` |

**S51 no cambia (A = NO, B = NO, C = NO).**

## 1. El conmutador

```
0x436f74c0: push {r3, lr}
0x436f74c2: cmp r1, #5
0x436f74c4: bhi 0x436f74f6          ; fuera de rango → log y 0
0x436f74c6: tbb [pc, r1]            ; tabla 0x436f74ca
0x436f74ca: 03 06 09 0c 0f 12       ; → 0x436f74d0, d6, dc, e2, e8, ee
...
0x436f7734: ldr r3, [pc, #4]        ; 0xf3122300
0x436f7736: ldr r0, [r3, #0x30]
0x436f7738: bx lr
```

| Caso | Función | Base | Offset |
|---:|---|---|---|
| 0 | `0x436f7734` | `0xf3122300` | `+0x30` |
| 1 | `0x436f78e8` | `0xf3122200` | `+0x24` |
| 2 | `0x436f7b20` | `0xf3123300` | `+0x30` |
| 3 | `0x436f7cd4` | `0xf3123200` | `+0x24` |
| 4 | `0x436f7f1c` | `0xfc0a3100` | `+0x30` |
| 5 | `0x436f8164` | `0xfc0a4100` | `+0x30` |

## 2. Uso por modo

`0x436f605c` lee `w0` de T1 y de T2 para la posición del modo, llama a `0x43ada4d8` con cada uno y suma:

| Modo | T1 (`w0`) | T2 (`w0`) | T3 (`w0`) |
|---|---:|---:|---:|
| `0x4c`/`0x4d` | 0 | 2 | 4 |
| `0x4e`/`0x4f` | 0 | 2 | 4 |
| `0x50`/`0x51` | 1 | 3 | 4 |
| `0x0b` | 0 | 2 | 4 |

Es decir: T1 y T2 seleccionan **canales distintos** del conmutador y el firmware suma sus lecturas; los modos `0x50`/`0x51` son los únicos que cambian de canal (T1: 0→1, T2: 2→3).

## 3. Corrección

- **S334**: `w0` no es un «código de operación» que solo se compara con 1/2/3; es un **selector de registro MMIO** (0..5) que el conmutador usa para leer un canal.

## Límites

- Solo estático: no se ejecuta el conmutador.
- No se sabe **qué mide** cada canal (`0xf3122200/2300/3200/3300`, `0xfc0a3100/4100`) ni por qué se suman dos lecturas.
- Los valores de `w0` se miden en las tablas; su origen en runtime no se ha rastreado.
- S51 (A/B/C) no cambia.

## Reproducción

```bash
.venv/bin/python analysis/s340_w0_selector/build_w0_selector.py
.venv/bin/python analysis/s340_w0_selector/verify_w0_selector.py  # 57 comprobaciones
.venv/bin/python -m unittest tests.test_s340_w0_selector           # 8 tests
```

Artefactos: `analysis/s340_w0_selector/w0_selector.json`, `build_w0_selector.py`, `verify_w0_selector.py`, `tests/test_s340_w0_selector.py`.
