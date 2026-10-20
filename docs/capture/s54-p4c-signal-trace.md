# S54-A — P4C / `CA_1ST_CURTAIN_START`: escritores, transiciones y destino (20-10-2026)

Análisis estático (Claude Code; capstone 5.0.7 con barrido `skipdata`, pseudocódigo REA/Ghidra 12.1.4 solo en el lado BIONZ). Sin cámara,
sin emulación. Darwin: base ROM `0x4200` (A6000 3.21 `5f2be06d…0bf4`, A7S 3.20 `241f5d31…6174cf`). Pruebas: `python3 -m unittest tests.test_s54_p4c`
(21 pruebas, ver §7). Scripts: `analysis/s54/p4c_scan.py`. Matriz: [`analysis/s54-evidence-matrix.json`](../../analysis/s54-evidence-matrix.json).

## 1. Red y pines (VERIFICADO, texto vectorial + inspección visual)

| Extremo | A6000 (IC6000 `MHZ4G8G01A`) | A7S (IC1001 `MHZ4G8G11D`) |
|---|---|---|
| Darwin FM3 | `P4C/SOT2_1` = `CA_1ST_CURTAIN_START` (salida GPIO) | `P4C/SOT2_1`: **misma columna** que la red (texto del manual A7S del repo, líneas 5780/5877) |
| BIONZ X, hoja 26/(4/7) | **`SENS_B` (bola AA13)** — flecha de entrada, junto a `AS_PWM*`, `SENS_A`, `IRIS0`, `ND_*`, `MSHUT_EN`, `STRB_ON*` | `SENS_B`, `AA13`, red en la fila siguiente (líneas 3506–3508): mismo patrón |
| BIONZ X, hoja GPIO (p. 28 A6000) | **`GPIO_9` (bola AD21)** con la misma red (recorte visual) | `GPIO_9` y la red en las líneas 3959–3961 |

Novedad frente a S53: S53 solo situaba la red «en la hoja de IC6000». Ahora la red llega a **dos pines de BIONZ**: el pin dedicado `SENS_B`
(bloque mecánico/diafragma) y el GPIO de propósito general `GPIO_9`. **Corrección de S53:** «pines A7S inferidos, sin esquema A7S» queda superado:
el manual Level 3 de A7S está en `docs/references/sony-ilce-7s-level3-sm.txt`; P4B–P4E coinciden por columna con las mismas redes. La polaridad
y el reposo siguen sin demostrarse. Fuente A6000: `scripts/schematic_pin_nets.py` p. 26/28 + recorte renderizado.

## 2. Escritores de P4C en Darwin (alias bit-band `0x42668230`)

Escritor único `0x51c0` (A6000) / `0x5200` (A7S): `ldr r2,=0x42668000; str r1,[r0,r2]` (bytes idénticos). Lector `0x51c6`/`0x5206` (+6) sobre
`0x42666000` (**PDIR**: nivel real del pin). Barrido de **todas** las llamadas `bl` (177 A6000 / 176 A7S) con propagación de constantes y lectura manual:

| Familia | A6000 | A7S | Valor P4C |
|---|---|---|---|
| Exposición «a0<0» | `0x20d26`: sitios `0x20d8a`, `0x20dba`, `0x20df6` | `0x217b2`: `0x2181c`, `0x2184c`, `0x21888` | **0** |
| Exposición «a0=0» | `0x20e0e`: `0x20e30`, `0x20e64`, `0x20e96→0x20e6e` | `0x218a0`: `0x218c6`, `0x218fa`, `0x2192c→0x21904` | **0** |
| Exposición «a0>0» | `0x20e98`: `0x20ece`, `0x20f14`, `0x20f34` | `0x2192e`: `0x21968`, `0x219ae`, `0x219ce` | **0** |
| Inicialización GPIO | `0x584c`: `DDR4=0x7e3f` (b12 salida), `PDOR4=0` (`0x58f6/0x58fa`); perfiles `0x25bfc+n·0x98` vía `0x55d0` | íd. | ver §3 |

- **VERIFICADO (bytes+desensamblado, 2 métodos: barrido capstone y lectura de cada cuerpo):** en tiempo de ejecución **no existe ninguna escritura
  P4C←1** (9 sitios por modelo, todos `movs r1,#0`). La única otra vía a `PDOR4` es `0x51f2(4,0x4000,0x9fff)`: máscara que **conserva b12**; único
  llamador `0x20e3e`.
- Los saltos `0x20e96→0x20e6e` y `0x2192c→0x21904` reutilizan la llamada con `r0=0x230,r1=0`: segundo P4C←0 en la rama «sin mecanismo»
  (no escriben P4E, contra lo que sugiere la etiqueta del salto).
- `0x584c` se vuelve a ejecutar solo desde el cambio de estado de energía `0x87ba` (llamador `0x8a42`) y desde el arranque `0x47fa`: el **rearme de P4C**
  (si existe) ocurre ahí o fuera del código recorrido: **NO VERIFICADO**.
- Limitaciones: escritura por registros GPIO directos fuera del alias bit-band, o puentes DDR/PFR, no se han excluido globalmente;
  el seguidor de constantes ignora ramas (por eso los dos saltos se verifican a mano).

## 3. Nivel inicial de P4C (PARCIAL)

Perfiles de pines (6, `0x25bfc+n·0x98`): P4C nivel inicial 0 en los perfiles 0,1,2,4,5 y **1** en el 3 (`mask 0x1038` con nivel 1). Qué perfil usa
la placa A6000 depende del ID leído por `0xcf3a`/selector `0x5b36`: **no resuelto**. Si la placa usara el perfil 3, P4C reposa en alto y
`P4C←0` sería un flanco de bajada; con el resto de perfiles P4C ya estaría en 0 y la escritura no cambiaría el pin. **Polaridad/idle: NO VERIFICADO.**

## 4. Orden de eventos por variante (evidencia de código, no de tiempos físicos)

`0x20544(a0,a1)` despacha: `a0<0`→`0x20d26(−a0,a1)`, `a0=0`→`0x20e0e(a1)`, `a0>0`→`0x20e98(a0,a1)`; espera `t=5n−5` (n≥2) en ticks `0x93e6`.
Siempre con tipo≠0 y tipo=0 (A6000) / no_silent (A7S) como se indica; `E`=P4E, `D`=P4D, `C`=P4C, `w(t)`=espera activa.

| Función | Mecánica (tipo 1/2/3; A7S no Silent) | Sin mecanismo (A6000 tipo 0 · A7S Silent) |
|---|---|---|
| `0x20d26`, a1≠0 | `0x20408`,`0x210c0`, E←1, w(t), [tipo≠3: D←0], **C←0**, tick, `0x202c2` | `0x20408`,`0x210c0`, w(t), **C←0**, tick |
| `0x20d26`, a1=0 | ..., E←1, w(t), **C←0**, tick, [tipo≠3: D←0], `0x202c2` | íd. |
| `0x20e0e`, a0=0 | `0x202c2`, [≠3: D←0], tick, **C←0**, E←1 (o `0x51f2`: D←0,E←1 a la vez) | `0x202c2`, tick, **C←0** (×2) |
| `0x20e98`, a0>0 | `0x202c2`, **C←0**, [≠3: D←0], w(t), E←1 (variante a1=0: D←0 antes de C←0) | `0x202c2`, **C←0**, w(t) |

Hallazgos: (i) **P4C←0 es la única operación presente en todas las ramas y variantes**, también cuando no se mueve ninguna cortina; (ii) en la rama
mecánica de `0x20e98`/`0x20e0e` P4C←0 es adyacente a la liberación D←0 (1ª cortina), coherente con el nombre «1st curtain start» pero **no demostrado**;
(iii) en `0x20d26` P4C←0 va *después* de w(t) y de E←1; (iv) `S+0x10` recibe el tick de P4C←0 (`0x16e8c`) y lo lee `0x173d2` como diferencia contra
`0x93e6` con umbral `0x3a98` (15 000 ticks): temporizador de vigilancia del propio Darwin; reloj del tick **no resuelto**.
**A7S normal vs. Silent:** cambian los escritores de bobinas (P4D/P4E se omiten) y el seguimiento ADC; **número, valor y orden de las escrituras P4C no cambian**.

## 5. Lectura de P4C y propagación a BIONZ por software

`0x1ecfe` (A7S `0x1f6be`) devuelve el nivel PDIR de P4C; lo llama `0x16390` que arma una palabra de estado (bit `0x80`; otros bits: ADC/PI, etc.).
Quién envía esa palabra a BIONZ y en qué mensaje: NO VERIFICADO (el parser de peticiones de estado no se recorrió).

## 6. Conclusión parcial y límites

P4C←0 es una marca de «inicio» emitida por Darwin **en todas las capturas, también sin mecanismo**, con polaridad y consumidor no demostrados.
Consumidor BIONZ: ver [s54-bionz-darwin-sync.md](s54-bionz-darwin-sync.md).

## 7. Pruebas

`tests/test_s54_p4c.py`: SHA-256 (ROM + `av-cam.bin`), escritor/literales, 9 sitios P4C por modelo (valor 0), constante `0x230`, ausencia de P4C←1,
`0x584c`/`0x51f2`, lector 0x1ecfe/0x16390, nivel inicial por perfil, columnas de esquema A7S. Ejecutadas: 21/21 OK (20-10-2026).
