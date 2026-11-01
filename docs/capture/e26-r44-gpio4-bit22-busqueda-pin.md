# E26-R44 — Búsqueda del pin físico de `GPIO(4,RDATA)` bit 22 (el salto a `serial_entry` sin clave): sin cierre, un candidato

Fecha: 31-10-2026. Continúa [R20](e26-r20-bootrom-selector.md)/[E26-R20-GPIO4](e26-r19-r20-cierre-estatico.md) a petición expresa del
usuario, tras confirmar en R44-bis (mismo informe, §1) que ese bit evita la clave de `nflasha0` por completo. Método: mismo
trazado vectorial de R43 (`pdftotext -bbox`, sin OCR) sobre la hoja IC6000 "GPIO SYS" (página 26) y revisión del GPL de Sony
(`regs-gpio.h`). Solo lectura, sin cámara.

Etiquetas: **BINARIO** (bytes de `bootrom.bin`, Capstone) · **ESQUEMA** · **FUENTE SONY** (GPL) · **INFERENCIA, no cierre**.

## 1. Por qué `GPIO4.22` es mejor objetivo que `CL1000` (BINARIO)

Desensamblado directo de `main` (`0xffff1062`–`0xffff1230`, Capstone sobre `bootrom.bin`), no el pseudocódigo de R23:

- `find_key` (`0x39c`) copia las dos palabras de `nflasha0` (`0xc0001200`) a la pila (`[sp+8]`/`[sp+0xc]`).
- `rx_packet` (`0x876`) recibe un paquete serie que **escribe el valor recibido en `[sp+4]`** (dirección de pila fija,
  deducible del binario, no secreta).
- `0xffff11ea`: `ldrd r0,r1,[sp,#4]; cmp r1,r0` — compara en una sola instrucción de 32 bits lo **recibido** (`[sp+4]`)
  contra la **clave guardada** (`[sp+8]`, primera palabra de `nflasha0`). Sin bucle byte a byte: no hay canal lateral de
  tiempos para adivinarla por partes. Si no coincide → `error_blink(0x2002)`.
- `error_blink` (`0xffff0d62`) es un **bucle infinito** (`b` hacia atrás en `0xffff0e08`, nunca retorna) — confirma
  "sin reintento" de R23/R34 a nivel de instrucción. Cada intento fallido exige un **ciclo completo de apagado/encendido**.
  Con 32 bits reales de clave (la segunda palabra es solo `~crc32`, no añade secreto) y ese coste por intento, la fuerza
  bruta por este interfaz **no es viable** (ni con reinicio automatizado: 2³² intentos a optimistas 1/s son >136 años).
- Si `GPIO4.22` (bit 22 de `0xf2910410`, "copia de GPIO4.22" en `[0xc0010010+4]`) ya es `!=0` al arrancar, `main` salta a
  `serial_entry()` en `0xffff10fe` **sin pasar nunca por `find_key`/`rx_packet`/la comparación anterior**. Es la misma
  llamada que abre la ventana de recepción (`rx_packet`/tipo "escritura RAM arbitraria" + tipo salto, R8/R9) pero **sin
  ningún secreto de por medio**. Esto ya estaba en R20/R23 (`E26-R20-GPIO4`); no es nuevo. Lo nuevo es la conclusión
  práctica: es una vía mejor que `CL1000`, porque no exige conocer ningún valor.

## 2. Búsqueda del pin físico (ESQUEMA)

`E26-R20-GPIO4` quedó cerrado con el límite «pines no identificables sin hoja de datos» porque el usuario pidió no hacer
el mapeo completo del esquema en esa fase. Repetido ahora con el mismo método de R43 (bbox + render dirigido, sin
rasterizar a ciegas):

- **Único bloque GPIO con nombre en las 54 páginas** (confirmado por R42, test `test_gpio_solo_puertos_0_y_1`): hoja
  IC6000, bloque **"GPIO SYS"** (página 26, columna 6-7), con dos grupos de bolas: `GPIO_S_0..16` (17 bolas) y
  `GPIO_SB_0..6` (7 bolas). Es el único candidato: ningún otro bloque del esquema completo usa el prefijo `GPIO`.
- El GPL de Sony (`regs-gpio.h`, `GPIO_REG(ch,reg)=(ch<<8)+reg_offset`) confirma que `0xf2910410` = canal **4**, registro
  `RDATA` (`0x10`) — pero **no da ningún nombre de pin por canal**; el mapeo canal→bola es interno de Sony y no está en
  el código GPL (`cxd90014_board.h` solo declara `extern void cxd90014_board_init(void)`, sin contenido).
- **No se puede confirmar que "GPIO SYS" sea el canal 4.** Ningún texto del esquema asocia ese bloque a un número de
  canal del mapa de registros; es un nombre de hoja, no un número de puerto interno del SoC.
- **Tampoco se puede confirmar qué bola es el bit 22**, aunque sí se puede acotar: si `GPIO_S_0..16` y `GPIO_SB_0..6`
  fueran los bits 0–16 y 17–23 de un mismo registro de 24 bits (hipótesis razonable pero no verificada — ningún dato la
  confirma ni la descarta), el bit 22 sería **`GPIO_SB_5`, bola N8**.

## 3. El único dato a favor de `GPIO_SB_5` (bola N8) — débil, no concluyente

Las otras seis bolas de `GPIO_SB` tienen todas una función de cámara con nombre propio: `XEYE_SENS_OUT_MSS` (SB_6),
`XWLAN_RST` (SB_4), `XCS_IC_6000` (SB_3), `XCS_LCD` (SB_2), `XCS_EVF` (SB_0); `SB_1` llega a una isleta sin montar
(`LND153`). **`GPIO_SB_5` (N8) es la única sin ninguna etiqueta de red ni destino** en la página 26 completa (verificado
por coordenadas, no por inspección visual: ninguna etiqueta aparece en la franja `y≈408–411 pt` más allá de la propia
bola). Que sea la única "sobrante" del grupo es compatible con que esté reservada a una función de arranque/depuración
en vez de una función de cámara — pero es una observación circunstancial, no una prueba. Podría igual de bien estar sin
usar en esta variante de placa (como tantas otras bolas `XX`/`LND*` ya vistas en R29/R40/R42).

## 4. Cierre

**No cierra.** `E26-R20-GPIO4` se mantiene **CERRADO (límite)**: el pin físico de `GPIO4.22` sigue sin ser identificable
de forma estática. Se añade un candidato razonado (`GPIO_SB_5`, bola N8 de IC6000) y la constatación de que, si se
confirmara, sería una vía de recuperación **sin necesidad de ningún secreto** — mejor que `CL1000` y que leer la clave de
`nflasha0`. Confirmar requeriría una de estas dos cosas, ninguna disponible ahora:

- La hoja de datos interna de Sony del CXD90014 (mapa canal→bola de GPIO), o
- Rastrear en `av-cam.bin` **todos** los llamadores de la función genérica de lectura de GPIO que usa `banco<<8`
  (`0x44e990`, R31 §1 límite) buscando un llamador con banco 4 y alguna cadena de depuración asociada — pendiente nuevo
  `E26-R44-AVCAM-GPIO4`, requiere sesión REA de `av-cam.bin` (~8 min en frío), no iniciada en este informe.

## 5. Límites

- No se tocó la cámara ni se forzó ninguna bola.
- La hipótesis de numeración continua `GPIO_S`+`GPIO_SB` = bits 0–23 de un solo registro es una suposición razonable por
  la forma de los nombres, no una lectura del esquema ni del GPL.

## 6. `E26-R44-AVCAM-GPIO4` (sesión REA de `av-cam.bin`, 31-10-2026/01-11-2026) — rastreado, sin cierre

Sesión REA abierta sobre `av-cam.bin` (fw 3.21). Rastreo de **todos** los llamadores de la función genérica de lectura
de GPIO por banco, siguiendo la cadena completa (no solo el límite ya anotado en R31 §1):

- `FUN_4398f990(bank,bit)` (`return *(base+bank*0x100) >> bit & 1`) es la primitiva de más bajo nivel; `base =
  0xf2910010` (= `GPIO_RDATA`, confirmado). **Un solo llamador en todo el binario:** `FUN_43b5e2bc`.
- `FUN_43b5e2bc(bank,bit)` acota `bank` a **0–17** (`if (0x11 < bank) return 0;`) y elige entre `RDATA`
  (`0xf2910010+bank*0x100`) o `WDATA` (`0xf2910040+bank*0x100`) según un modo. **`bank=4` está dentro del rango
  permitido** (no lo descarta el límite): `bank=4` da exactamente `0xf2910410`, el registro que usa el BootROM.
- **26 llamadores** de `FUN_43b5e2bc` en todo el binario. Ninguno pasa `bank`/`bit` como constantes inmediatas: todos
  los resuelven en tiempo de ejecución contra el sistema de propiedades interno de Sony (identificadores opacos tipo
  `0x00f902a9`, fuera del rango de direcciones del binario — no son punteros, son IDs de una base de datos de
  propiedades, **el mismo mecanismo sin resolver de `E1`/`ModelScalarPb`**, `NO_VERIFICADO` desde antes de E26).
- Se identificaron por nombre **tres** de los 26 (tabla de registro de propiedades en `0x43fd9258`–`0x43fd9270`,
  triples `{nombre, nombre, manejador}`): `eosw_port`/`[EO_SW]` (`FUN_43592b48`), `rvport`/`[PanelReverse]`
  (`FUN_43592b98`), `esport`/`[EyeSens]` (`FUN_43592d20`). **Ninguno tiene relación con arranque/servicio**: son
  funciones normales de cámara (interruptor del visor, inversión de panel, sensor de proximidad del ocular).
- Los 23 llamadores restantes usan el mismo patrón de variable indirecta (sin nombre legible sin resolver cada uno);
  no se examinaron todos.

**Conclusión: no se identificó el pin de `GPIO4.22`.** La vía de `av-cam.bin` queda **bloqueada por el mismo límite que
`E1`**: los valores reales de `bank`/`bit` de cada propiedad no están en este binario como datos estáticos — se
resuelven contra una base de datos de propiedades cuyo contenido no se ha localizado. Resolver esto exigiría primero
cerrar `E1` (origen del local 4/2 a `ModelScalarPb`/`ModelPbCap`, ya `NO_VERIFICADO` en el proyecto desde antes de
E26) o encontrar la tabla de valores por defecto de esas propiedades en otro binario/partición. **No se sigue más en
este informe**: el límite es real y compartido con un pendiente ya existente, no un abandono arbitrario.

Sesión REA cerrada limpiamente (`q.py --shutdown`); `exp2-session-log.jsonl` restaurado con `git checkout` antes de
commitear, como indica la nota del proyecto.
