# S52 fase C — validación por Claude de los hallazgos de Codex

19-10-2026. Repetido con LLVM (`s52/dis/*.dis`), bytes, capstone y un **arnés Unicorn propio**
(`s52/xcheck_emu.py`, salida `s52/xcheck_emu.json`). Test independiente: `tests/test_s52_xcheck.py` (7/7 OK).
Fuentes Codex leídas: `work/codex/s52_*.md`, `s52_shutmode_emulation.json`, `s52_sensor_register_trace.csv`,
`s52/emulate_setexposure.py`, `s52/CHECKPOINT.md`. No se modificó nada en `work/codex/`.

## (1) Tabla B2 — bits por ShutMode

Despacho verificado: IMX235 `0x436f423e cmp r6,#4; bhi 0x436f42fc; tbb` (tabla `0x436f4246` → casos
`424c/425c/42fc/4290/42c4`); IMX210 `0x436d70be cmp.w r9,#4; bhi.w 0x436d728e; tbb` (tabla `0x436d70ca` →
`70d0/70e0/7114/717a/71ae`). `r6`/`r9` = `param+9` (`0x436f4198`, `0x436d6fb6`).

| Afirmación Codex | Veredicto | Evidencia propia |
|---|---|---|
| IMX235 `cfg+4`: 0→`00`, 1→`04`, 3→`14`, 4→`40`; 2 → error `438f7114` | **CONFIRMADO** (con inicial 0) | caso 0: `bfc b2`, `bfc b6`, salta a la cola `42d2` que hace `bfc b4`; caso 1: `orr 4`, `bfc b6`, `bfc b4`; caso 3: `orr 4`, `bfc b6`, `orr 0x10`; caso 4: `bfc b2`, `orr 0x40`, (cola) `bfc b4`. Con inicial `0xff`: 0→`ab`, 1→`af`, 3→`bf`, 4→`eb` (el byte real conserva b0,b1,b3,b5,b7) |
| (omisión) | **PARCIAL** | Codex no tabula la 2.ª escritura: `cfg2+4 \|= 8` en **todos** los casos 0/1/3/4 (`0x436f4276`, `42aa`, `42de`). Corrige también mi propia tabla anterior (`a7s_shutter_modes_comparison.md`), que lo atribuía solo a la clase 0 |
| IMX210 `cfg+2`: 0→`40`, 1→`c4`, 2→`94`+copias `param+8/+0x14`, 3→`d4`, 4→`c0` | **CONFIRMADO** | caso 0: `bfc b2`, `bfc b7`, cola `71bc`: `bfc b4`, `orr 0x40`. Inicial `0xff`: 0→`6b`, 1→`ef`, 2→`bf`, 3→`ff`, 4→`eb`; copias a `0x4401c6d2`/`0x4401c7ce` |
| Rango diferencial IMX210 modo 3 = `436d7114..78` | **REFUTADO** | `0x436d7114` es el caso **2**; el caso 3 es `0x436d717a..71a8` (TBB) |
| Fronteras (primera llamada) 0:`436f2d10`/`436d6f50`, 1:`436f2cf4`/`436d6f34`, 3:`4355de98`/`4355faf0`, 4:`436f2d10`/`436d6f50` | **CONFIRMADO** | mismas `bl` en el desensamblado |
| «La diferencia 0 vs 1 vs 3 es de bits» | **CONFIRMADO**; además difiere la temporización: 0/4 usan `0x436f2d10` (`[r0]>>8+1`), 1 usa `0x436f2cf4`×`r7`, 3 usa `param+0xc`/1000+1 → `img+0x3d4` (IMX235) | instrucciones `0x436f4284..42f6` |

## (2) Fidelidad del arnés Unicorn de Codex

| Aspecto | Veredicto | Detalle |
|---|---|---|
| Mapeo del blob y lectura de bytes | CONFIRMADO fiel | blob en `0x43541000`; GOT del blob intacta |
| Punto de entrada a mitad de función (`0x436f423e`, `0x436d70be`) con `r2/r3/r8` sintetizados | **PARCIAL** | Los punteros de campo los resuelve el prólogo por GOT; Codex los sustituye por buffers propios: los bits son correctos, la **identidad** del campo no queda probada. Mi arnés arranca en la entrada real y obtiene los campos reales: IMX235 `0x440220ac` (=`*0x440220a8`+4) y `0x44021ff2`; IMX210 `0x4401ca2e` (=`0x4401ca2c`+2) |
| «Los tres SHR dan el mismo patrón» | **PARCIAL / artefacto** | Cierto solo porque el arnés empieza después del prólogo y se para en la 1.ª llamada. El prólogo IMX210 escribe `param+0/+4/+6` (SHR y similares) en ~12 campos (`0x4401c67a…0x4401c812`, mi emulación) y el IMX235 los pasa a `0x43ad9ec6` (3 llamadas). La conclusión «no prueba efecto eléctrico» se mantiene |
| Escrituras de modo | no son artefactos | reproducidas con mi arnés (entrada real, `bl` externos sustituidos por retorno, relleno `00`/`ff`) |
| Globals simuladas | riesgo bajo | ambos arneses leen valores iniciales del blob para globals RAM (p. ej. `0x44021ff2` inicial `0x04`, overrides `+0x2d/+0x2e/+0x2f`); en cámara pueden diferir. Mi caso 0 IMX235 pasa por el log `0x438f7114` porque `r7==0` con esos valores iniciales |

## (3) CSV de 48 campos IMX235

| Afirmación | Veredicto | Evidencia |
|---|---|---|
| 48 filas de la matriz `0x43fee598` (69 filas) difieren entre columnas 0/12/13 | **CONFIRMADO** | recalculado desde bytes (no desde mi JSON): 48/48 coinciden en `field`, col0, col12, col13 (45 difieren col0↔col12 + 3 solo col13) |
| Lector `0x436f3928` (`ldr [row]`, `strb [field_ptr]`) | **CONFIRMADO** | `0x436f393a..3942`: `ldrb r5,[r2+r1+4]; strb r5,[r4]; ldr r4,[r2]` |
| Uso «copia byte de la columna elegida; consumidor no resuelto» | **CONFIRMADO** | ninguna fila tiene otra clasificación que NO VERIFICADO (no hay filas «distintas» que muestrear) |
| Columna `field` | **PARCIAL** | es el u16 en `ptr-2`, no un registro del sensor demostrado; además el CSV omite la tabla alternativa (`+0x2b0`, `0x436f394e`) |

## (4) Frontera B1 de Codex frente a mi cadena

Codex: «no hay transferencia tipada clase→`param+9`; lector de `+0x5c` no tipado; despacho virtual no resuelto».
**Queda cerrada en lo estático (CONFIRMADO salvo dos condiciones):**

1. Lector tipado de `G+0x5c`: getter `0x43864c74` (`ldr r3,[pc]; add r3,pc; ldr r0,[r3,#0x5c]`, G=`0x43f06bc8` por PIC),
   único llamador `0x43861bfc` → `0x43f04c8c`.
2. `0x43863478..7c`: `0x43f04c8c` → registro `r8+0x69`; `r8` = `0x43861f58(cap+0x1e0, cap+0x1d8)` (`0x438633f8`).
3. `0x43862158` llama al mismo `0x43861f58` (`0x4386218c`) y copia `+0x60..+0x6b` a `*param` → `param+9`.
4. `0x43b1c8e2`: `[sp]=cap+0x648` → `cap+0x651`; `0x438b77ac`: `0x436f2938(img, cap+0x648)`.
5. Despacho: `0x436f294c..52` `ldr r0,[r0]; ldr r3,[r0]; ldr r3,[r3,#0x28]; blx r3`; vtable IMX235 `0x43fce050+0x28 = 0x436f4169`.

Condiciones que siguen abiertas (INFERENCIA): la copia solo ocurre si `[r9]!=0 || [r9+0x15]!=0` (`0x4386216e..76`);
que `0x43861f58` elija el **mismo** banco en ambos momentos depende de `0x43b0b900()`; que el objeto imager sea la
instancia IMX235 (tipado dinámico); y el orden etapa `0xc1` → SetExposure. Además `cap+0x651` se fuerza a 0 si
`0x439fb708()∈{2,3}` (`0x438b775c`) y SetExposure solo se llama con `cap+0x4bb0==0`.

## (5) drive_mode `0x4e/0x4f` frente al control de cortinas

| Punto | Resultado |
|---|---|
| Constructor del paquete CAIF `0x43862e24` | no lee `cap+0x4d0` (sin `[r6,#0x4b0]`/`[rX,#0x4d0]`); los bits Silent vienen de `cap+0x78c`. El llamador `0x4382822c` calcula ModeRsvParam `0x437b8948(cap+0x4d0,…)` y SetMode-reserva `0x436f2848` antes, pero ese descriptor (`sp+0x34`) no se pasa al constructor (recibe `sp+0x48`) — VERIFICADO en el llamador; callees del constructor no recorridos |
| Esperas S3–S7 | gobernadas por `cap+0x748`, ninguna lee `cap+0x4d0` (barrido de las 5 funciones: 0 accesos salvo ReadExecute) |
| `0x438b68cc` (flags de la petición ReadExecute, = A6000 `0x438c73f8`) | único consumidor hallado: `drive_mode-0x37 ≤ 1` → flags `0x15`; si no `0x11/0x19`. `0x4e/0x4f` siguen la rama normal (como `0x0b`) |
| Mapeo secundario `0x43826c90` | `0x4e→0x50`, `0x4f→0x51` solo si tipo≠2: en Silent no se aplica |

Conclusión: drive_mode y la ruta CAIF/esperas son **paralelas**, ambas derivadas de `cap+0x78c`; no se halló un punto
donde `0x4e/0x4f` modifique el paquete o las esperas. PARCIAL por cobertura (callees no exhaustivos).

## Hipótesis Codex tras la validación

H52-3 → **CONFIRMADO** estático con las condiciones de (4). H52-4 → sin cambio (NO VERIFICADO; la clase no omite
envíos CAIF, ver `s52_curtain_control_trace.md`). H52-5 → NO VERIFICADO (de acuerdo). H52-7 → DESCARTADO como código
existente (de acuerdo: 13 modos IMX210 sin `0x4e/0x4f`, verificado en S51/S52).
