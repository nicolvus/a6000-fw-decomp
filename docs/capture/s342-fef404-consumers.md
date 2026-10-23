# S342 — `0x43fef404` sí tiene consumidores: es la tabla de ids de `Camera::Lens::ODL`

22-10-2026. Carril B. Sesión S342. **Solo lectura estática; sin firmware en ejecución, sin cámara, sin flasheo.**

## Pregunta

S337 cerró `0x43fef404` con un negativo **acotado a literales absolutos** («0 referencias literales»). S341 dejó abierta la pregunta «consumidor de `0x43fef404`». ¿Existe un consumidor que llegue por **puntero calculado** (base PIC `ldr rX,[pc,#imm]` + `add rX,pc`)?

## Veredicto

| Afirmación | Clasificación | Evidencia |
|---|---|---|
| `0x43fef404` es una tabla de **69** entradas de 4 B `{u16 id, u16 0x000d}` que termina en `0x43fef518` | **VERIFICADO** | 69 pares; segundo campo `0x000d` en las 69 |
| Tiene **dos** consumidores estáticos por base PIC: `0x437056f8`/`0x437056fc` y `0x43705754`/`0x43705756` | **VERIFICADO** | base calculada `0x43fef404` en ambos; 0 literales absolutos (S337 se mantiene para literales) |
| Los dos consumidores iteran **exactamente 69** veces (`cmp r7,#0x45`; `cmp.w r5,#0x114` con paso 4) | **VERIFICADO** | `0x43705724` / `0x4370576a` |
| Va acompañada de un array de **69 punteros** en `0x43fef520` (slot GOT `0x44028c78`) | **VERIFICADO** | valor del slot y 69 dwords; sin base PIC directa al array |
| Los 69 punteros y el array de 256 entradas anterior apuntan a una región **`.bss`** de 2,47 MB a cero en la imagen | **VERIFICADO** | run de ceros `0x43d58231..0x43fb2ba0` |
| Los consumidores se invocan desde el init de **`Camera::Lens::ODL`** | **VERIFICADO** (llamadores + cadenas) | `bl` en `0x4373d0b4`/`0x4373d2f2`, cadenas `Camera::Lens::ODL…`, `Camera::Lens::Initialize(UPM_BOOT_FACTOR*)` |
| La tabla es un registro de **ids de datos de aberración del objetivo** (id → buffer) | **INFERENCIA (alta)** | ids + punteros a `.bss` + módulo ODL; no hay símbolo que lo nombre |
| Es una tabla de tiempos | **NO** (refuta el candidato de S329) | sin valores temporales, sin índice por modo, sin escrituras |
| Significado del campo `0x000d` y de cada id | **NO_VERIFICADO** | constante 13 en las 69 entradas; sin consumidor que lo interprete |

**S51 no cambia (A = NO, B = NO, C = NO).**

## Detalle

### 1. La tabla y su vecindario (A7S fw3.20)

```
43fef004  ef03e943 22c6f943 22c6f943 22c6f943   <- array de 256 punteros (empieza aquí)
...
43fef3f0  22c6f943 22c6f943 22c6f943 22c6f943
43fef400  22c6f943 46000d00 4e000d00 0f000d00   <- fin del array + tabla {id,0x000d}
43fef410  2e000d00 2f000d00 31000d00 14000d00
...
43fef510  45000d00 4b000d00 00000000 fdc7f943   <- fin de tabla; hueco de 8 B
43fef520  08e1f643 28e3f643 1ecef943 fdc7f943   <- array compañero de 69 punteros
```

- **Array de 256 punteros** `0x43fef004..0x43fef404`: 256 dwords; **225** valen `0x43f9c622` y **169** de ellos son el run contiguo que S337 midió. No es un «prefijo» de la tabla: es un array que **termina** justo donde empieza la tabla (`0x43fef404 - 0x43fef004 = 0x400 = 256×4`). Lo consume `0x4373f1d0` con límite `cmp.w r3,#0x100` (`0x4373f1dc`) e índice `cmp r5,#0xff` (`0x4373f1ec`), vía el slot `0x440253ac → 0x43fef004`.
- **Tabla** `0x43fef404..0x43fef518`: 69 × `{u16 id, u16 0x000d}`, ids únicos en `0x01..0x64` (69 de los 100 valores posibles).
- **Hueco de 8 B**: `0x00000000`, `0x43f9c7fd` (mismo patrón en las tres cámaras).
- **Array compañero** `0x43fef520..0x43fef634`: 69 punteros, todos dentro del run de ceros. Sólo se alcanza por el slot GOT `0x44028c78` (0 bases PIC directas).

### 2. Consumidor A — `0x437056ec`

```
437056f2  104d       ldr r5, [pc, #0x40]      ; GOT base = 0x44024540
437056f6  7d44       add r5, pc
437056f8  0f4e       ldr r6, [pc, #0x3c]      ; literal 0x008e9d04 en 0x43705738
437056fa  01a9       add r1, sp, #4
437056fc  7e44       add r6, pc               ; r6 = 0x43fef404  (base de la tabla)
437056fe  3359       ldr r3, [r6, r4]         ; tabla[i]
43705704  7b44       add r3, pc
43705708  0d4b       ldr r3, [pc, #0x34]      ; offset 0x4738
4370570a  55f80380   ldr.w r8, [r5, r3]       ; 0x44028c78 -> 0x43fef520
4370570e  54f80830   ldr.w r3, [r4, r8]       ; compañero[i]
...
4370571a  00eb8700   add.w r0, r0, r7, lsl #2
43705720  5af636f8   bl #0x4355f790
43705724  452f       cmp r7, #0x45            ; 69 iteraciones
43705726  e7d1       bne #0x437056f8
43705728  3046       mov r0, r6               ; tabla
4370572a  4146       mov r1, r8               ; array compañero
4370572c  59f6bcff   bl #0x4355f6a8
```

Por iteración arma `(tabla[i], callback 0x43adb6e3, compañero[i])` y llama a `0x4355f790` con un puntero de salida `*(0x44026240) + 4·i`; al final llama a `0x4355f6a8(tabla, compañero)`. Ambos helpers son *thunks* que despachan por `[global+0x14] + 0x2c8 / 0x29c`.

### 3. Consumidor B — `0x43705748`

```
4370574a  0d20       movs r0, #0xd            ; 13
43705750  094b       ldr r3, [pc, #0x24]      ; offset 0x4738
43705754  0949       ldr r1, [pc, #0x24]      ; literal 0x008e9caa en 0x4370577c
43705756  7944       add r1, pc               ; r1 = 0x43fef404
43705758  e258       ldr r2, [r4, r3]         ; compañero (0x43fef520)
4370575a  59f6ddff   bl #0x4355f718           ; (0xd, tabla, compañero)
4370575e  084b       ldr r3, [pc, #0x20]      ; offset 0x1d00
43705762  e858       ldr r0, [r5, r3]         ; *(0x44026240) = 0x43e906f4
43705766  5af621f8   bl #0x4355f7ac
4370576a  b5f58a7f   cmp.w r5, #0x114         ; 276 B = 69·4
4370576e  f6d1       bne #0x4370575e
```

El segundo bucle recorre 69 dwords de `0x43e906f4` (dirección **en `.bss`**, cero en la imagen) registrando cada elemento con `0x4355f7ac`.

### 4. Quién los llama

| Consumidor | `bl` desde |
|---|---|
| A `0x437056ec` | `0x4373d0b4` |
| B `0x43705748` | `0x4373d2f2` |

Ambos sitios están en el módulo `0x4373c000..0x4373e400`, cuyas cadenas PIC son `Camera::Lens::ODL::ODL_ERR …` (`Alloc`, `Free`, `Load`, `AllocLensAberrationData`, `LoadLensAberrationData`), `base.err_code = 0x%x`… y `void Camera::Lens::Initialize(UPM_BOOT_FACTOR*)` (26 cadenas en la ventana). El init también registra `0(2..6)` con `0x4373f2e8`.

### 5. Las tres cámaras

| | A7S fw3.20 | A6000 fw3.21 | A6300 fw2.01 |
|---|---|---|---|
| Tabla | `0x43fef404` | `0x43feae1c` | `0x441b0b1c` |
| Entradas | **69** | **47** | **69** |
| Array compañero | `0x43fef520` (slot `0x44028c78`) | `0x43fead58` (slot `0x44022ab0`) | `0x441b0c38` (slot `0x441fcb9c`) |
| Base GOT | `0x44024540` | `0x4401eee4` | `0x441fa214` |
| Consumidor A / bucle | `0x437056ec` / `0x45` | `0x436eb2cc` / `0x2f` | `0x43734bd8` / `0x45` |
| Consumidor B / bucle | `0x43705748` / `0x114` | `0x436eb328` / `0xbc` | `0x43734c34` / `0x114` |
| Callers A / B | `0x4373d0b4` / `0x4373d2f2` | `0x4372162a` / `0x4372187a` | `0x4373ac20` / `0x4373ae5e` |

- **El bucle siempre itera tantas veces como entradas tiene la tabla** (69/47/69): el recuento no se lee de la tabla, es una constante compilada de la misma lista.
- Los ids de la A6000 son **subconjunto estricto** de los del A7S: faltan exactamente `0x4f..0x64` (22 ids). La A6300 tiene **la misma lista** que la A7S.
- Base de la A6300 corroborada de forma independiente: la cadena de S168 `position num in rolling is strange %d` está en el offset que implica `BASE = 0x43541000`.

## Correcciones

- **S337**: «sin consumidor estático» es correcto **solo para literales absolutos** (siguen siendo 0). El firmware direcciona tablas con `ldr`+`add pc`; barriendo esas bases aparecen **dos** consumidores. El resto de S337 (forma `{id,0x000d}`, 69 entradas, fin `0x43fef518`, run de 169 `0x43f9c622`) se confirma.
- **S341 §5** (pregunta abierta «consumidor de `0x43fef404`»): **cerrada**.
- **S329** (no hay tabla de tiempos por modo): **se mantiene**. La tabla no tiene ninguna relación funcional con los modos: el consumidor no la indexa por modo, no la escribe y sus ids no son los registros de la matriz (los 69 registros de `0x43fee598` son `0x81`/`0x83`).

## Límites

- Solo lectura estática; sin runtime, cámara ni flasheo.
- Que la tabla pertenezca a `Camera::Lens::ODL` es **INFERENCIA** a partir de los llamadores y de las cadenas del init: no existe símbolo con ese nombre.
- Los 69/47 punteros apuntan a `.bss` (2,47 MB a cero en la imagen): no se puede saber qué objeto vive en cada dirección ni si se llena en runtime.
- No se asigna significado al campo `0x000d` ni a los ids.
- Los 20 códigos que coinciden numéricamente entre ids y vocabulario de modos (20 de 34) **no** establecen relación: ningún consumidor cruza ambas cosas.

## Reproducción

```bash
.venv/bin/python analysis/s342_fef404_consumers/build_fef404_consumers.py
.venv/bin/python analysis/s342_fef404_consumers/verify_fef404_consumers.py   # 60 comprobaciones
.venv/bin/python -m unittest tests.test_s342_fef404_consumers                 # 11 tests
```

Artefactos: `analysis/s342_fef404_consumers/fef404_consumers.json`, `build_fef404_consumers.py`,
`verify_fef404_consumers.py`, `tests/test_s342_fef404_consumers.py`.
