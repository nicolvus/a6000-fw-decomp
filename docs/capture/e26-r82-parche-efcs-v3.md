# E26-R82 — Parche EFCS v3: calibración por tabla EN SITIO, vía NVRAM, anexado y huecos (07-11-2026, estático)

Continúa [R81](e26-r81-auditoria-opus-parche-efcs.md) (parche BLOQUEADO: sin hueco ≥ 40 B), [R80](e26-r80-auditoria-parche-r76.md) y [R76](e26-r76-calibracion-propia-efcs.md). Todo es offline sobre `darwin_core.bin` 3.21 (base `0x4200`, Cortex-M3 Thumb-2) y volcados NVRAM propios. **No se tocó la cámara, no se escribió ningún volcado en ella y no se construyó ni instaló ningún paquete.** Etiquetas: **VERIFICADO** (dos métodos distintos) · **MODELO** · **SOLO CÁMARA**.

## 0. Resultado

| Vía | Resultado | Estado |
|---|---|---|
| **A** compactación en sitio | **Funciona.** El prefijo `0x18d6e..0x18e0f` (162 B) se reescribe con codificaciones más cortas y la búsqueda en tabla integrada, **en los mismos 162 B**. Sin gancho, sin cave, imagen del mismo tamaño (157 276 B). Equivalente al original con tabla vacía (1 000 000 estados al azar + 786 432 combinaciones exhaustivas) y con tabla igual a la vía C, con tres métodos | **Diseño elegido** |
| **D** solo NVRAM | Volcados listos para `B+0x86 = 1256` y `G+0x42 = 2157`, con tabla de exposición por velocidad y procedimiento | Listo; escribir **requiere autorización** |
| **C** anexar al final | El actualizador del BIONZ no limita el tamaño por debajo de 246 023 B y `darwin.sum` lo admite; el cargador de Darwin (`0x0–0x41ff`) no está disponible | Alternativa lista (`parchear_anexo`), **solo la cámara decide** si lo acepta. No hace falta |
| **B** lógica menor / hueco real | No hay hueco de código ≥ 40 B (dos métodos). Un `c(T)` lineal a tramos cabe, pero el error modelado sube de 2,2 % a 6,9 % (3 parámetros) o 12 % (2) | **Descartada** (dominada por A) |

Límite que no cambia ([R80 §2](e26-r80-auditoria-parche-r76.md)): Darwin mueve A/B igual para todo el cuadro; el degradado vertical de ±0,25 ms **no** se corrige. El parche es útil de 1/1000 hacia abajo; 1/2000 y 1/4000 siguen con la parte baja del cuadro oscura.

## 1. Vía D — solo NVRAM (generador `scripts/e26_r82/e26_r82_nvram.py`)

Base: el volcado más reciente, `analysis/camera-dumps/20261105-r64-post-var088/backup_flash.bin` (sha256 `727e41ff6ac4…`; es el estado actual de la cámara, con `0x30102+0x88 = 834` pendiente de restaurar a 334). Generados con `scripts/e26_r61/bk4_variante.py` en `analysis/camera-dumps/20261107-r82-nvram/` (no versionado, `SHA256SUMS` dentro):

| Variante | Propiedad | Cambio | sha256 |
|---|---|---|---|
| `var_b86_1256.bin` | `0x1850001+0x86` | 6 → 1256 | `3dac5b8556c4ad77f1ee2026b7a92b26b4a231a24c53c7017403606cb12fdc44` |
| `var_g42_2157.bin` | `0x1850000+0x42` | 3407 → 2157 | `3abc09b842942de2324b028a93bce1d5b56c22ac94ba12d2b2c530088cc1dc04` |

**Doble verificación.** (1) `BackupFile` valida cabecera y checksum al releer cada salida y compara las dos propiedades `0x1850000/1` con la base: solo cambia el s16 pedido. (2) Diferencia byte a byte contra la base: `b86` = 4 bytes (checksum `0x20,0x21` + datos `0xcfbea = e8`, `0xcfbeb = 04` → 0x04e8 = 1256) y `g42` = 3 bytes (checksum + `0xcfb22 = 6d`, `0xcfb23 = 08` → 0x086d = 2157), calculado a mano.

**Exposición por velocidad (MODELO R74/R80 con la cola a 0; emulando `0x18d6e` con Unicorn y verificando A/B contra el cálculo a mano, ±1 µs en los 23 códigos):**

| T µs (velocidad) | sin cambios | `B+0x86 = 1256` | `G+0x42 = 2157` |
|---|---|---|---|
| 244 (1/4000) | negro (−508 %) | −3,9 % | −3,9 % |
| 976 (1/1000) | negro (−127 %) | −6,6 % | −6,6 % |
| 1953 (1/500) | −67 % | −2,4 % | −2,4 % |
| 2458 (1/400) | −53 % | −14,4 % | −1,7 % |
| 3102 (1/320) | −42 % | −32,1 % | +1,6 % |
| 3906 (1/250) | −33 % | −33,0 % | +6,8 % |
| 4917 (1/200) | −22 % | −22 % | +12,5 % |
| 6204 (1/160) | −10 % | −10 % | +17,1 % |
| 7812 (1/125) | −0,8 % | −0,8 % | +16,0 % |
| 9834 (1/100) | 0 % | 0 % | +12,7 % |

Coincide con [R76 §0](e26-r76-calibracion-propia-efcs.md) salvo la cola (R76 usaba δ = 170 µs a ≥ 8 ms; con la cola a 0, `G42` sobreexpone +17 % a 1/160 en vez de +15 %). `B86` satura entre 2,1 y 3,3 ms; `G42` sobreexpone 1/200–1/100 (≥ +0,2 EV): ninguna sirve para todo el rango, de ahí el parche.

**Procedimiento (REQUIERE AUTORIZACIÓN; no ejecutado).** Los volcados dependen del estado de la NVRAM: antes de escribir, volcar de nuevo y regenerar desde ese volcado.
1. `python scripts/senser_backup_dump.py` (copia previa) y regenerar: `bk4_variante.py DUMP VARIANTE 0x1850001 0x86 1250` (o `0x1850000 0x42 -1250`).
2. `PYTHONPATH=references/pmca python scripts/senser_backup_restore.py VARIANTE SHA256` (comprueba región, tamaño, escribe, relee y sincroniza a flash).
3. **Reversión:** `senser_backup_restore.py` con el volcado del paso 1. Una variante a la vez; medir 1/4000…1/125 con EFCS activado.
Premisa nunca probada en cámara (R66 §1): que editar `0x185000x` cambie Darwin; esta prueba la comprueba.

## 2. Vía C — anexar el código tras `0x2a85c`

| Pregunta | Evidencia | Estado |
|---|---|---|
| ¿El actualizador del BIONZ limita el tamaño? | `ud_darwin_firmup.elf` lee el fichero con `stat` + `read(fd, 0x11a4d, st_size)` (`0x8f38–0x8f6c`, `0x900a–0x903e`); el buffer es `.bss` desde `0x11a4d` hasta `g_size` en `0x4db54` = **246 023 B**; no compara `st_size` con ninguna constante; solo exige que `read` devuelva `st_size`. El tamaño se envía al arranque de Darwin en la trama `0x14` (`[5..8]`) | VERIFICADO (desensamblado) |
| ¿`darwin.sum` / `us_crc32sum` lo admiten? | `uc_crc32sum.elf -c` compara tamaño y CRC-32 con la línea del `.sum` («size mismatch», «crc mismatch»); `scripts/e25_27/sums.py` reescribe ambos (8 hex, longitud de línea constante) y `tarball.py` admite miembros de otro tamaño | VERIFICADO |
| ¿Algo en el core depende del final de imagen? | `0x2a85c` aparece una sola vez como palabra (`0x2a754`): origen sin uso de la segunda entrada de la tabla de arranque (`0x2a744`), que es puesta a cero (R76b). Anexar no desplaza nada | VERIFICADO |
| ¿Cabe en la flash del MCU? | El A6300 2.01 lleva un `darwin_core` de **181 040 B** (termina en `0x30530`) y el A7S 3.20 de 161 248 B; A6000 y A6300 montan `MB9AF004BGL-G-103` en IC5700 (manuales de servicio locales; el A7S no tiene manual local). Con 64 B de cave el A6000 termina en `0x2a8a0`, por debajo de ambos | INFERENCIA (misma MCU; no hay manual de flash del MB9AF004B: no es una de las partes del manual FM3 local) |
| ¿El cargador `0x0–0x41ff` acepta un tamaño mayor que el instalado? | Es quien programa la flash (el core no contiene código de flash, E24-02 §1) y pide los bloques; su binario no está en ningún paquete ni volcado (R59: SWD descartado) | **SOLO CÁMARA** |
| ¿La versión del cargador del A6000 es la del A6300? | Desconocida (el cargador no se reescribe en las actualizaciones) | **SOLO CÁMARA** |

Alternativa lista, no necesaria: `parchear_anexo()` (`e26_r76_parche_darwin_tabla.py`) devuelve la imagen + 4 B de relleno + cave de 64 B en `0x2a860` y el gancho `bl 0x2a860` en `0x18d7c` (157 344 B). Su emulación da los mismos retardos A/B que la vía A en los 1866 códigos Tv; se usa como **oráculo independiente** de la semántica. Un paquete así necesitaría una prueba de aceptación en cámara (con relleno inerte, sin cambiar código) antes de confiar en él.

## 3. Vía A — compactación en sitio (diseño elegido)

**Idea.** El parche de R76 hacía `bl 0x18a2e → bl cave`. En vez de un cave, se reescribe el prefijo de la función de tiempos, que ya lee todo lo necesario y es donde se llama a `0x18a2e`:

| Qué se quita o acorta | Bytes |
|---|---|
| `str r0,[r7,#0x48]` de `0x18d7a` (se sobrescribe sin lectura intermedia) | 2 |
| `bl 0x1b308` (es `bx lr`; solo reescribe `lr`, ya guardado y recargado por el siguiente `bl`) | 4 |
| pares `ldrb+ldrb+orr` y `add.w #off` + `ldrb…` → `ldrh.w [base,#off]` (G+0x42, G+0x44/46, B+0x12a/12c/12e; todos en direcciones pares) | ≈ 70 |
| `ubfx+cmp #1` → `cmp.w r6,#0x40000000` (bit 1:0 de `B+0xcd`); doble lectura de `S+0x31` → una; `cmp.w #0x80000000` → `adds r1,r0,r0` | ≈ 12 |

Con eso el prefijo con la tabla ocupa **162 B = los 162 B originales** (4 B de `nop` sin ejecutar antes del último bloque). Nada salta al interior del prefijo desde fuera (`referencias_externas` vacío) y la entrada `0x18d6e` y el empalme `0x18e10` no cambian. Los literales (`S=0x200036d8` en `0x18f54`, `B=0x20000300` en `0x18f50`, `G=0x20000480` en `0x18f5c`) son los originales y se reutilizan.

**Tabla** (propiedad `0x1850000`, `G+0x48..0x7f` = `0x200004c8`, hoy ceros): 14 entradas `{s16 Tmax', u16 c}` **sin terminador**, con `T' = T − G42` (lo que devuelve `0x18a2e`, ya en `r0`; no hace falta guardar `T`). Gana la primera con `T' ≤ Tmax'` (con signo); relleno `{−32768, 0}`. Solo con EFCS (`S+0x31 & 3 ≠ 0`) y `S+0x60` bit 1 = 0 (la compuerta de `0x18a2e`). `c` fuera de `[0, 2000]` µs se ignora (`cmp.w #2000; bhi` sin signo cubre ambos extremos). Tabla a ceros = neutra. El bucle para en 14 entradas aunque la NVRAM esté corrupta. `Tmax'` depende de `G42` del volcado (el generador lo lee de él).

**Código** (ensamblado con Keystone, decodificado con Capstone; `scripts/e26_r82/e26_r82_compactacion.py`): `push.w {r4-r8,lr}; ldr r7,S; ldrh r0,[r7,#0x32]; bl 0x19a12; bl 0x18a2e; ldrb.w r5,[r7,#0x31]; and r5,r5,#3; cbz r5,skip; ldrb.w r2,[r7,#0x60]; lsls r2,r2,#30; bmi skip; ldr r1,G; add.w r1,#0x48; add.w r3,r1,#56; loop: cmp r1,r3; bhs skip; ldrsh r2,[r1],#4; cmp r0,r2; bgt loop; ldrh r2,[r1,#-2]; cmp.w r2,#2000; bhi skip; add r0,r2; skip: str r0,[r7,#0x48]; …` (bloque `S+0x94` idéntico) y las tres ramas del cálculo de `ip` con `ldrh.w`. Bytes (162 B, `0x18d6e`):

```
2de9f041784f788e00f04cfefff758fe97f8315005f00305a5b197f86020920710d4724901f1480101f13803994209d231f9042b9042f9dc31f8022cb2f5fa6f00d81044b864d7f8940018b1011800d10020b86428467b8f624c05bb94f8cd2001256249960704d1b1f8421001eb030c17e0b6f1804f06d1b4f82a11b4f82c2101eb020c0de0b1f84420b1f846609119b4f82e2101eb020c03e000bf00bf00259c46
```

sha256 de la imagen parcheada: `2366d3099e81cff0286760c62c99d28b19a119ac320592870b819c5e673870aa` (original `5f2be06d9885…`). Solo cambian 139 bytes, todos dentro de `0x18d6e..0x18e0f`. No toca `PD.PROTECTED` ni `PD.PATCHES` (3.30–3.38: `0x4318..`, `0x4330`, `0x1fe6c`, `0x20c78`).

**Verificación (tres métodos independientes entre sí):**

| Método | Qué se compara | Resultado |
|---|---|---|
| 1. Emulación diferencial (Unicorn) original frente a reescrita, de `0x18d6e` a `0x18e10` | registros vivos (`r0,r3,r4,r5,r7,ip,sp`), pila y 32 KB de RAM (S, G, B), con `S+0x48` = original + `c`. Estado: `S+0x31`, `S+0x60`, `Tv`, `S+0x3a`, `S+0x94` (0, `0x80000000`, ±), `G+0x40/42/44/46`, `B+0xcd` (0…255), `B+0x12a..0x12f`; tablas válidas, corruptas y sin terminador | **1 000 000 estados al azar (semilla 82; 200 000 repetidos con el código final) sin una diferencia; barrido exhaustivo de 786 432 combinaciones, repetido con la tabla final** (Tv `0x1000..0x1fff` × `S+0x31` × `S+0x60` × `S+0x94` × `B+0xcd` con los valores NVRAM reales: 0 diferencias; 57 336 con `c ≠ 0`) |
| 2. Modelo en Python escrito a mano desde el desensamblado original (incluye `0x19a12` calculado de los bytes y `0x18a2e`) | `r0, r3, r4, r5, ip, S+0x48` por estado | Coincide en todos los estados anteriores |
| 3. Imagen con el cave anexado (vía C, otro código y otra tabla de bytes) y emulación completa de `0x18d6e` | `(rama, retardo A, retardo B)` por código Tv | **Idéntico en los 1866 códigos Tv entre ≈ 1/4000 y 1/22** (`tests/…v3.py`); sin tabla idéntico al original; EFCS desactivado, `S+0x60` bit 1 y `S+0x31 ∈ {1,2,3}` idénticos; ninguno cae en la rama intermedia `0x20544` |
| Estática | Capstone: ramas a `0x18e10`, literales por `pc`, accesos de media palabra a direcciones pares (válidos aun con `UNALIGN_TRP`), sin referencias externas al prefijo, bytes `≥ 0x18e10` intactos | OK |

Registros no comparados (muertos en `0x18e10`): `lr` (el siguiente `bl` lo reescribe; nadie lo lee en `0x18e10..0x18e47`), `r1`, `r2`, `r6` y `r8` se reasignan antes de leerse.

**Exposición modelada con la tabla de la unidad** (T de `0x19a12`; modelo R74 con la cola a 0; error ≤ 2,2 % en la escala de 1/3 EV):

| T µs | 244 | 307 | 387 | 488 | 614 | 775 | 976 | 1229 | 1551 | 1953 | 2458 | 3102 | 3906 | 4917 | 6204 | 7812 | 9834 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c µs | 1264 | 1264 | 1287 | 1287 | 1310 | 1310 | 1310 | 1310 | 1310 | 1266 | 1266 | 1266 | 1050 | 793 | 462 | 24 | 24 |

Tabla (`Tmax µs, c µs`): `(347,1264) (551,1287) (1752,1310) (1982,1266) (2091,1157) (2199,1374) (3504,1266) (4411,1050) (5560,793) (7008,462) (9834,24)`; en la NVRAM: `0cf4f004 d8f40705 89f91e05 6ffaf204 dcfa8504 48fb5e05 6100f204 ec031a04 69081903 110ece01 1b191800` + 3 entradas de relleno `00800000`. Es el modelo: la tabla real sale de la calibración en cámara (`e26_r76_calibrar_efcs.py ajustar`).

**Límites.** Unicorn no modela temporizadores ni el NVIC: el bucle añade como máximo 14 vueltas (≈ 100–150 ciclos) antes de la sección con IRQ desactivadas, fuera del intervalo medido. Se elimina el `str` intermedio de `S+0x48` (T sin ajustar durante microsegundos); no se buscaron otros lectores de `S+0x48`. `S+0x94 ≠ 0` sigue anulando `S+0x48` (también el `c`), igual que antes. Los códigos Tv continuos entre dos velocidades de la escala de 1/3 EV pueden tener hasta ≈ 7 % de error (tramos de guarda para esquivar la ventana intermedia, §5).

## 4. Vía B — huecos y lógica menor

**Huecos (`scripts/e26_r82/e26_r82_huecos.py`).** Método 1 (flujo): recorrido recursivo desde los vectores, todas las palabras-puntero de la imagen, y los destinos de cada `bl`/`b.w` decodificados en cada halfword; sigue ramas, `tbb/tbh`, literales y bloques `IT` (un retorno predicado no termina el flujo): cubre el 97 % del código hasta `0x25c5c`. Método 2 (barrido): cada byte no cubierto se clasifica por contenido (ceros, 0xff, ASCII ≥ 75 %) y por referencias entrantes (ramas, palabras-puntero con y sin bit 0, `adr`, `ldr` pc-relativo) desde cualquier halfword. Rangos ≥ 40 B sin cubrir: 11; **ninguno es código libre**: 3 tienen referencias (tablas de la máquina de estados `0x25b38`, cargador de arranque `0x4434`), 8 son colas de cadenas ASCII de `printf` (`0x25290` es un `printf` real, no un stub), y `0x4304..0x43fc` es la tabla de vectores, cuyas únicas zonas a cero (`0x4316..0x4327`, `0x432e..0x4333`) ya usa el parche 3.30–3.38. **R81 queda confirmado con un segundo método:** no hay hueco de código ≥ 40 B (las cadenas son datos vivos).

**Lógica menor.** Con el modelo de R74/R80, error máximo en las 17 velocidades de la escala con `c` sin caer en la ventana intermedia: tabla de 11 entradas **2,2 %**; `plateau + rampa` (3 parámetros, mejor ajuste `a = 1280, T1 = 1800, T2 = 8800`) **6,9 %**; `c` constante hasta `T2` (2 parámetros) **12 %**. Cabría en ≈ 40 B pero necesita hueco (no lo hay) y empeora la exposición: dominada por A, que da la tabla completa sin hueco.

## 5. Cambios en los scripts (R81-CPREV, R80 §3)

* `e26_r76_calibrar_efcs.py`: `c` aplicado = el de la **tabla** previa (`c_tabla`), no el punto fijo (R81 hallazgo 4); `T` efectivo de `0x19a12` (`t_efectivo`: 1/4000 = 244 µs, 1/500 = 1953, 1/320 = 3102, 1/250 = 3906; hallazgo 5); `G+0x42`, `B+0x86`, `B+0x8a` leídos del volcado (`--nvram`, `leer_unidad`); `Tmax'` con el `G42` del volcado al escribir.
* `e26_r76_parche_darwin_tabla.py`: `parchear()` = vía A; `parchear_anexo()` = vía C; `parchear_hueco_r76()` mantiene el bloqueo de R81; formato de tabla nuevo (14 × `{s16, u16}`); `usar_unidad()`; la rama corta satura en A = 1 µs; **cola del modelo a 0** (R62 §2: ≈ 0 por franjas a 8 ms; R74 §4: la pérdida se anula hacia `B − A` ≈ 4–5 ms; los 170/160 µs eran artefacto de la normalización); `MARG` 40 → 8 µs (T sale exacto de `0x19a12`).
* Efecto conocido: 1/500 (T = 1953 µs) cae junto a la ventana intermedia `0x20544` (T' de 3257 a 3457 µs, no modelada). Con el modelo R74 queda fuera (−1,6 %); si la pérdida real es ≈ 8 % mayor, el `c` ideal cae dentro y se empuja a un borde (error ≈ 7 %, límite de R80 §3).
* `scripts/e25_27/build.py`: `efcs_tabla_allowed_addresses()` (`0x18d6e..0x18e0f`) y `efcs_tabla_diff()`, **sin conectar a `apply_patches`**: no se construye ni se instala nada.

## 6. Lo que solo se decide en cámara

1. Que editar `0x1850000/1` llegue a Darwin (vía D; es la prueba más barata y reversible).
2. Que el cargador acepte el `darwin_core` parcheado (mismo tamaño que los 3.30–3.38, que se instalaron sin NG; la vía A no cambia el tamaño). Solo la vía C depende además de aceptar un core más largo.
3. La curva δ real, el degradado vertical y la tabla definitiva (`calibrar ajustar` sobre dos tandas de fotos).
4. Que las ramas `0x20544` no se alcancen en la práctica (verificado solo en emulación).

> **Corrección a [R81](e26-r81-auditoria-opus-parche-efcs.md):** el bloqueo del parche (c) se levanta con un diseño que no necesita hueco (vía A). Lo demás de R81 (cave `0x13d5a` en función viva, no hay ≥ 40 B libres) queda confirmado. R81 §3 (i) anexar y (iii) solo NVRAM siguen siendo alternativas válidas (C y D).
