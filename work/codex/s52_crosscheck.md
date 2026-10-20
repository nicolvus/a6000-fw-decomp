# S52 — validación cruzada independiente (Codex)

Fecha: 19-10-2026. Alcance estático; sin ejecutar firmware. Entradas verificadas:
`work/claude/input/{a7s,a6000}-av-cam.bin` (SHA-256 respectivos
`b857d338…925103e` y `b60c845c…e56bb9`) y sus `*-view.elf`.

Método: REA se abrió sobre `a7s-av-cam-view.elf`; la consulta de límites/llamadores
quedó en análisis frío y no se usó como prueba concluyente. Repetí los puntos con
LLVM (`llvm-objdump --triple=thumbv7-none-eabi`) y bytes del `.bin`; las direcciones
Thumb se contrastaron en los listados completos de `work/claude/s52/dis/`.

| # | Veredicto | Evidencia independiente y límite |
|---|---|---|
| 1 | **PARCIAL** | Confirmada la parte local: `0x438649f0..a48` selecciona tipo 2 y escribe clase 0 en `G+0x5c` (bytes en `0x438649f0`: `d7f80424022a02d1704a7a44`); `0x43864c74..7a` lee `G+0x5c`; `0x43861bfc..c04` lo guarda en `0x43f04c8c`; `0x43863478..7c` carga dicho global y escribe `r8+0x69`. También `0x43862184..ac` llama `0x43861f58(cap+0x1b8,cap+0x1c0)` y copia `registro+0x60..+0x6b` al buffer señalado por `r2`; en el llamador `0x43b1c8c0..e2`, `r2=sp` y `[sp]=cap+0x648`; `0x438b77a4..ac` pasa ese buffer a `0x436f2938`, cuyo `+0x28` es despacho virtual. `0x438b7750..5c` fuerza `cap+0x651=0` sólo tras comparar el retorno de `0x439fb708` con 2 y 3. **No queda probado que el `r8` de `0x43863478` sea el mismo registro elegido por `0x43861f58`, ni ausencia de escrituras intermedias a `cap+0x651`; por tanto no se confirma clase→`param+9`.** Frente a R2, R2 es correcta sobre la cadena completa; su conclusión local sobre los extremos necesita actualizarse con estas copias, pero no cierra la identidad del registro. |
| 2 | **PARCIAL** | `0x43813e94..ea2` llama al conversor, compara 2, guarda el tipo en `cap+0x78c` y escribe 1 en `cap+0x748` (bytes `8af7b6fe0228c4f88c0702d10123c4f8`). Las parejas de lectura A7S/A6000 y los efectos citados aparecen en LLVM. No reproduje exhaustivamente el recuento global «13 lectores / ningún escritor por puntero»; se confirma el escritor A7S y la equivalencia de offsets usada, no el conteo exhaustivo. |
| 3 | **CONFIRMADO** | En A7S, `0x43863258` compara `cap+0x76c` con 2 y prepara `2<<6` para el byte `+0xd`; `0x4386329a..b4` deriva y almacena bit 5 en `pkt+0x12` (bytes `d6f86c27a2f102014a4242eb010298f800105201`). `0x4386315c..74` toma clase 0/3 y escribe 2 en `pkt+1`; clase 1 toma la otra ruta. El homólogo A6000 `0x4384137c..96` no trata clase 0 como la ruta A7S. |
| 4 | **CONFIRMADO** | `0x438627d2..fe` permite continuar sólo para clase 1 o clase 3 con el flag auxiliar; clase 0 salta a `0x438627fe` antes de la llamada posterior. Bytes: `274b7b441b68012b06d0032b0ed1244b7b441b78`. Esto confirma la omisión local del envío tipo 3/`0x22`, no la semántica del receptor. |
| 5 | **PARCIAL** | `0x43b585aa` y `0x43b585b6` sólo validan índice `<=0x11`, fijan `r2` a 1/0 y ramifican a `0x4397d4c0`; los homólogos A6000 hacen lo mismo hacia `0x4398f9a4`. Es evidencia de helper GPIO general, no de un driver de cortina. No reproduje de forma fiable el número «~150 llamadores», por lo que no lo elevo a confirmado. |
| 6 | **CONFIRMADO** | Darwin A7S `0x216e8..21702` enmascara con 7 y acepta exactamente 1, 2 o 3; cualquier otro valor devuelve 0. Darwin A6000 homólogo `0x20c74..c8e` tiene la misma terna; A6300 `0x24700..71e` agrega comparación con 4. |
| 7 | **PARCIAL** | `VD_Pre` A7S `0x437b6f6c..7e` carga el ajuste `+0x250`, llama `0x4379ec04` y guarda su resultado en el bloque PC-relativo `+0x7e8` (= `0x43eaaac0`). Bytes: `d9f80030d3f85002e7f746fe07f5ba512c31c7f8`. Un barrido estático sin hallazgos no demuestra «sin lectores» frente a referencias indirectas/Thumb no recuperadas; esa segunda mitad sigue **NO VERIFICABLE**. |

## Resultado

Las pruebas confirmadas se añadieron a `s52/test_s52_shutmode_facts.py`. La
afirmación central de B1 permanece abierta: hay una ruta de copia hasta el buffer de
`SetExposure`, pero no una identidad demostrada entre el registro que recibe la clase
y el registro seleccionado por `0x43861f58`.
