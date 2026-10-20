# S53 — Del parser CAIF a las bobinas de cortina (19-10-2026)

Base ROM `0x4200`. Contexto: [reconstrucción](s53-darwin-caif-reconstruction.md). Pines y cadena de potencia de A6000:
[fm3-gpio-shutter-mapping.md](fm3-gpio-shutter-mapping.md) (P4D = `1ST_CURTAIN_MG`, P4E = `2ND_CURTAIN_MG`,
P4C = `CA_1ST_CURTAIN_START`; FET Q6832 → bobinas 1C/2C). Prueba: `tests/test_s53_darwin_caif.py`.

## Escritor físico

**VERIFICADO:** A6000 `0x51c0` y A7S `0x5200` son idénticos (`f74a81507047`: `str r1,[r0, 0x42668000]`), es decir
escritura bit-band en PDOR del FM3. `+0x234` = PDOR4 bit 13 (P4D), `+0x238` = PDOR4 bit 14 (P4E), `+0x230` = P4C.
Las redes son del esquema **A6000**; para A7S se aplica por **INFERENCIA** (mismo MCU/banco/offsets y código homólogo; no
hay esquema A7S en el repositorio).

## Escritores de bobina

| Acción | A7S | A6000 | Diferencia |
|---|---|---|---|
| P4D ← 0 | `0x2172c(no_silent)`: escribe solo si tipo∈{1,2} **y `no_silent≠0`** | `0x20cb2()`: tipo∈{1,2} | A7S añade argumento Silent |
| P4E ← 1 (+`0x21b5a`) | `0x21786(no_silent)`: tipo≠0 **y `no_silent≠0`** | `0x20d00()`: tipo≠0 | íd. |
| Exposición negativa / 0 / positiva (bloqueante) | `0x217b2/0x218a0/0x2192e(…, no_silent)` | `0x20d26/0x20e0e/0x20e98(…)` | A7S: rama «sin mecanismo» si tipo==0 **o Silent** |
| Paso diferido (cola de eventos) | `0x214dc`: `0x2172c(0x216c2())`; `0x214fa`: `0x21786(0x216c2())`, `0x216ac` solo si no Silent | `0x20a8a`: `0x20cb2()`; `0x20aa4`: `0x20d00()`, `0x20c4a` siempre | predicado `S+0x154` b4 |
| Seguimiento de posición ADC | `0x2116e`/`0x21282` requieren `0x216c2()` | `0x20734`/`0x2083c` sin esa condición | A7S no mide/verifica fases en Silent |

`0x216c2` devuelve `S+0x154` bit 4, que fijan las primitivas `0x19d34/0x19d6a/0x19db2/0x19dcc/0x19e00` con su argumento
`no_silent` (procedente de `0x19a86` = `!(S+0xd0 & 0x20)`).

**Rama Silent A7S en `0x217b2` (VERIFICADO, pseudocódigo + bytes):** si `tipo==0 || no_silent==0` → `0x20dfa`, `0x21b5a`,
espera activa del tiempo de exposición, **`P4C ← 0`**, marca de tiempo en `S+0x10`; **no** escribe P4D ni P4E. En la rama
mecánica escribe `P4E←1`, espera, `P4C←0`, `P4D←0` (orden según `param_2`). A6000 `0x20d26` tiene la rama «sin mecanismo»
idéntica, pero solo se toma con **tipo de mecanismo 0** (`0x20c74`), nunca por un campo del paquete.

## Secuencias (esquema de análisis, no comportamiento físico demostrado)

- **Mecánica (ambas):** parser → primitivas de exposición → P4E/P4D según tiempo → seguimiento ADC de fases
  (`S+0x153`, [máquina de estados](darwin-state-machine.md)) → rearme.
- **Silent A7S:** parser (`S+0xd0.b5=1`, clase→2) → primitivas con `no_silent=0` → solo temporización y `P4C`
  (`CA_1ST_CURTAIN_START` hacia IC6000) → sin seguimiento ADC → fin.

**Prueba decisiva (sección 7 del encargo): ENCONTRADA en A7S, AUSENTE en A6000.** La rama evita activar las bobinas y omite
la medición de posición. **NO VERIFICADO:** polaridad física (qué nivel libera cada cortina), estado de reposo de las
cortinas en Silent y que no exista otra ruta (p. ej. rearme o prueba de servicio) que mueva el mecanismo durante Silent.
