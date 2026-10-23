# S343 — la copia de 20 B de la fila T configura los seis bloques MMIO de canal

22-10-2026. Carril B. Sesión S343. **Solo lectura estática; sin firmware en ejecución, sin cámara, sin flasheo.**

## Pregunta

S336 dejó abierto el único camino de datos de las filas T sin seguir: `0x436f5f7c` copia 20 B de la fila, parchea `+5`/`+7` si `[estado+0x18]&1` y llama a `0x43ada310`. ¿Acaba eso en un log, en la trama P2S, en el DFE o en otra cosa?

## Veredicto

| Afirmación | Clasificación | Evidencia |
|---|---|---|
| `0x43ada310` forma un bloque de **44 B** = 20 B de la fila + **12 pares** `(flag,bit)` y rellena con `{0,0x0b}` | **VERIFICADO** | 4×`ldm`/`stm` + `ldr`/`str` (20 B), bucle `cmp r6,#0x18` paso 2, `adds r2,#0xb` |
| `0x43ada480` guarda el **id de canal** (`[obj+4]` = 0..5), cuenta los flags no nulos (`obj+8`) y despacha a **5 manejadores** | **VERIFICADO** | `str r3,[r0]`, bucle 12, `cmp r3,#0xc`, 4 `bl` + `b.w` |
| El manejador `0x436f6710` descompone los **bytes impares** de la fila en nibbles de **seis** bloques, uno por caso `tbh` | **VERIFICADO** | caso 0: 12 pares `ldrb r0,[r4,#1,3,…,0x17]` → 12 escritores sobre `0xf3122300` |
| El manejador `0x436f7480` escribe **1 bit por bloque** según el caso `tbb` (6) | **VERIFICADO** | `tbb` → `0x436f7490..ae` → `0x436f7724/78d8/7b10/7cc4/7f0c/8154` |
| La capa tiene **178** escritores de campo en A7S, **177** en A6000 y **178** en A6300 | **VERIFICADO** | patrón `ldr r3,[pc]; ldr r2,[r3,#off]; bfi r2,r0,#lsb,#w; str; bx lr` |
| Los seis bloques son **los mismos** que lee el selector `w0` de S340 | **VERIFICADO** | `0xf3122300/2200/3300/3200/0xfc0a3100/0xfc0a4100` en ambos artefactos |
| El único campo que la A6000 **no** tiene es `0xfc0a3100+0xc` bit 24 | **VERIFICADO** | diferencial de conjuntos `(bloque, offset, lsb, width)` |
| La cadena **no** toca la máscara DFE (`0xfc02a00c`) ni la P2S (`0xfc088300`) | **VERIFICADO** | 0 escritores con esos bloques |
| Semántica física de los seis canales | **NO_VERIFICADO** | sin datasheet; solo se conoce su mapa de campos |

**S51 no cambia (A = NO, B = NO, C = NO).**

## 1. La cadena

```
0x436f5f7c  copia 20 B de la fila T1 (+0x00..+0x13), parchea +5/+7 si [estado+0x18]&1
   └─ 0x43ada310(obj, copia, obj+0x16)   añade los 12 pares (flag,bit)
        └─ bloque de 44 B:  [20 B fila][12 × (flag, índice de bit)]
             └─ 0x43ada480(obj+4, bloque)
                  ├─ [obj+4] = bloque[0..3]      (id de canal 0..5)
                  ├─ [obj+8] = nº de flags ≠ 0   (≤ 12, si no: no despacha)
                  └─ 0x436f6710  (tbh 6 casos: nibbles por canal)
                     0x436f68ec  (reconstruye la máscara de 12 flags)
                     0x43544270  (bytes +4/+5/+6/+0x11: máscaras)
                     0x436f6b9c  (tabla con stride 0x78 × 0xa)
                     0x436f7480  (tbb 6 casos: 1 bit por canal)
```

Bytes del parche, en `0x436f5f7c`:

```
436f5fb8  3b7e       ldrb r3, [r7, #0x18]   ; estado+0x18
436f5fba  13f0010f   tst.w r3, #1
436f5fc0  9df80930   ldrb.w r3, [sp, #9]    ; fila+5 de la copia
436f5fc6  8df80b30   strb.w r3, [sp, #0xb]  ; si fila+5==0 -> fila+7 = 0
436f5fd2  e4f39df9   bl #0x43ada310
```

Y en `0x43ada310`:

```
43ada318  0fcf       ldm r7!, {r0, r1, r2, r3}   ; 16 B de la fila
43ada320  3b68       ldr r3, [r7]                ; + 4 B = 20
43ada328  a35d       ldrb r3, [r4, r6]           ; par: flag
43ada336  03eb4000   add.w r0, r3, r0, lsl #1    ; destino = copia+0x14+2·i
43ada344  182e       cmp r6, #0x18               ; 12 pares (stride 2)
43ada35a  0b32       adds r2, #0xb               ; relleno {0, 0x0b}
43ada368  00f08af8   bl #0x43ada480
```

## 2. Los seis bloques y sus campos

Los casos del `tbb` de `0x436f7480` van, uno a uno, al último escritor del grupo de cada bloque:

| Caso | Bloque | Bit que escribe |
|---|---|---|
| 0 | `0xf3122300` | `+0x28` bit 0 |
| 1 | `0xf3122200` | `+0x20` bit 0 |
| 2 | `0xf3123300` | `+0x28` bit 0 |
| 3 | `0xf3123200` | `+0x20` bit 0 |
| 4 | `0xfc0a3100` | `+0x28` bit 0 |
| 5 | `0xfc0a4100` | `+0x28` bit 0 |

El descompresor `0x436f6710` usa los **bytes impares** de la fila: caso 0 → 12 nibbles en `0xf3122300` (`+0` lsb `0x1c..0`, `+4` lsb `0xc..0`), caso 1 → `0xf3122200` (`+0`, `+4`, `+8`), y así los seis.

Reparto de los 178 escritores:

| Bloque | Escritores |
|---|---|
| `0xf3122300` | 31 |
| `0xf3122200` | 25 |
| `0xf3123300` | 31 |
| `0xf3123200` | 25 |
| `0xfc0a3100` | 34 (33 en A6000) |
| `0xfc0a4100` | 32 |

Los campos son nibbles de 4 bits en `+0`, `+4`, `+0x20`, `+0x24`; bits sueltos y campos de 1–2 bits en `+0xc`; un bit en `+0x28`; y escrituras de palabra completa en `+8`, `+0x10`, `+0x14`, `+0x18`, `+0x1c`, `+0x38`, `+0x40`, `+0x44`.

## 3. Los mismos seis bloques que lee `w0`

S340 documentó que `w0` selecciona `0xf3122300/2200/3300/3200/0xfc0a3100/0xfc0a4100` y lee `+0x30` (cuatro) o `+0x24` (dos). Los getters del A7S son `0x436f7734`, `0x436f78e8`, `0x436f7b20`, `0x436f7cd4`, `0x436f7f1c` y `0x436f8164` — **un getter por bloque**, en el mismo vecindario de código que los escritores.

Consecuencia estructural: la fila T1 **configura** los seis canales y `w0` **lee** el canal configurado. Esto no identifica la magnitud física, pero cierra el circuito «fila T → hardware» por el lado de la escritura de campos.

## 4. Diferencial A7S ↔ A6000 ↔ A6300

- Escritores: **178** (A7S), **177** (A6000), **178** (A6300).
- La A6000 no tiene **ningún** campo exclusivo; le falta **uno** del A7S: `0xfc0a3100 + 0xc`, bit 24 (A7S `0x436f8180`). Es el único bit diferencial de toda la capa.
- El A6000 tampoco usa el idioma de getter `ldr r3,[pc]; ldr r0,[r3,#off]; bx lr` (6 en A7S, 0 en A6000/A6300). Que lea los bloques por otra ruta queda **NO_VERIFICADO**.

## 5. Corrección y límites

- **Cierra** el TODO S343 de la cola y el camino de datos que S336 dejó abierto.
- **No cambia** S329/S331/S334/S335: la ruta de máscaras (`0x436f618c` → pares → `0x43ada370` → `0x436f822c` → `0xfc02a00c`/`0xf292b004`) es **independiente** de esta ruta de copia de fila; ningún escritor de esta capa toca `0xfc02a00c` ni `0xfc088300`.
- **Límites**: solo lectura estática; los seis bloques se etiquetan como «canales» porque hay 6 casos y `w0` los usa, no porque se conozca su función; `0x436f68ec`/`0x43544270`/`0x436f6b9c` se describen por su efecto sobre el bloque de 44 B, sin descomposición línea a línea; la ausencia del bit 24 en la A6000 es estática.

## Reproducción

```bash
.venv/bin/python analysis/s343_row_copy_chain/build_row_copy_chain.py
.venv/bin/python analysis/s343_row_copy_chain/verify_row_copy_chain.py   # 45 comprobaciones
.venv/bin/python -m unittest tests.test_s343_row_copy_chain               # 11 tests
```

Artefactos: `analysis/s343_row_copy_chain/row_copy_chain.json`, `build_row_copy_chain.py`,
`verify_row_copy_chain.py`, `tests/test_s343_row_copy_chain.py`.
