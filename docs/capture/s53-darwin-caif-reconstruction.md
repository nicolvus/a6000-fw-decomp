# S53 — Darwin: arquitectura, transporte MSS y parser CAIF ev1 (19-10-2026)

Análisis estático exclusivamente (Claude Code; Ghidra 12.1.4 headless + capstone 5.0 + LLVM). Sin cámara, sin ejecución de
firmware, sin modificar originales. Direcciones Darwin **ROM, base `0x4200`** (offset de archivo = dirección − `0x4200`).
Prueba reproducible: `python3 -m unittest tests.test_s53_darwin_caif` (10/10). Scripts y proyectos: `analysis/s53/`.
Comparación: [s53-darwin-a7s-a6000-comparison.md](s53-darwin-a7s-a6000-comparison.md) ·
cortinas: [s53-curtain-actuator-control.md](s53-curtain-actuator-control.md) ·
viabilidad: [s53-a6000-silent-feasibility.md](s53-a6000-silent-feasibility.md) · [conclusiones](s53-conclusions.md).

## 1. Imágenes (S53-A)

| ROM | Ruta (`firmware/extracted/…/0640_darwin/darwin_core.bin`) | Tamaño | SHA-256 |
|---|---|---:|---|
| A6000 3.21 | `fw321/firmware.tar_unpacked` | 157 276 | `5f2be06d…0bf4` |
| A7S 3.20 | `a7s-fw320/payload/firmware.tar_unpacked` | 161 248 | `241f5d311991e8b4e0246b2edab4039517cab55daf431d4ad21670a8866174cf` |
| A6300 2.01 (control) | `a6300-fw201/payload/firmware.tar_unpacked` | 181 040 | `6249d4b7…33ac` |

**VERIFICADO:** MCU Fujitsu/Cypress FM3 `MB9AF004BGL` (IC5700, esquema A6000), Cortex-M3, little-endian, Thumb-2.
Base `0x4200` (ya probada para A6000/A6300; para A7S: reset `0x45f9`→archivo `0x3f8` y la tabla de despacho repite el vector
de reset). Pila inicial A7S `0x200026d0`, A6000 `0x20002a00`.

**Interrupciones (VERIFICADO):** todos los IRQ apuntan a un único manejador (A6000 `0x6808`, A7S `0x67fa`) que lee
`ICSR` (`0xe000ed04`) y salta a `*(0x4300 + 4·(nº excepción − 1))`. La disposición de la tabla `0x4300` corresponde a
`IRQCMODE=1` del manual FM3 (Doc. 002-05586, tabla de vectores): vectores 31–38 = MFS ch.0–7 combinados
(A6000 `0xeeb4…0xef08`), 28/29 = EXINT. Los manejadores MFS llaman a callbacks en RAM `0x20002c1c + 12·slot` (+8),
instalados por `0xee70` según el modo MFS: `0x00` UART→`0xa55d`, `0x40` CSIO→`0x9f9b`, `0x80` I²C→`0x103a1`.

**Descriptores serie (A6000 `0x279e8`, 0x4c B):**

| # | MFS | Pines (alias PDOR) | Uso (cadenas/llamadores) | Red en esquema A6000 (hoja IC5700) |
|---|---|---|---|---|
| 0 | ch.3 `0x40038300` | P50/P51/P52 | «DD com» (`0x15ef4`…) | CAM_SI_1 / CAM_SO_1 / CAM_SCK_1 |
| 1 | ch.5 `0x40038500` | P36/P37/P38 | **mss-sync** (`0x11d40`, tramas 128 B) | **MSS_SO_DWN / MSS_SI_DWN / MSS_SCK_DWN** (+P39 DWN_CSDIR_MSS) |
| 2 | ch.4 `0x40038400` | P0A/P0B/P0C | — | CAM_SI_2 / CAM_SO_2 / CAM_SCK_2 |
| 3 | ch.5 (otra config.) | P36/P37/P38 | **mss-async** (`0x12172`, mensajes por ID) | íd. |

Las redes `MSS_*` llegan a **IC6000 = MHZ4G8G01A (BIONZ X)** en la hoja de IC6000 (A6000 L3 p.26), junto con
`CA_1ST_CURTAIN_START` y `CA_RELEASE_LOCK_MSS`. Por tanto el enlace BIONZ↔Darwin es MFS5 (CSIO). **NO VERIFICADO:** qué
dispositivo es «DD» en MFS3, y el reparto de tareas completo del RTOS (solo se reconstruyó lo necesario).

## 2. Transporte del paquete CAIF ev1 (S53-B.1)

Tabla de mensajes asíncronos MSS (A6000 `0x27c68`, A7S `0x28bb8`; 16 B por ID desde `0x0b`: `{tx, rx, longitud, código}`).
El ID `0x0c` es el **único de 22 bytes** y el único de recepción con ese tamaño:

| | A6000 | A7S |
|---|---|---|
| Entrada ID `0x0c` | `0x27c78`: rx `0x2000344c`, len `0x16`, código `03 01 02` | `0x28bc8`: rx `0x2000321c`, len `0x16`, código `03 01 02` |
| Copia estable (lector índice 6 → ID `0x0c`) | `0x1efb8(6)` → `0x20003a00` | homólogo `0x1709c` |
| Parser | **`0x17f8c`** | **`0x18396`** |
| Estructura destino S | `0x200036d8` | `0x200034a0` |

El emisor `0x121b6` arma la cabecera `f0, código[0..2], longitud(u16)`. **INFERENCIA fuerte:** el ID `0x0c` es el CAIF ev1
operación `0x10300` de LIRO (coinciden longitud 22 B y el par `03 01`; el resto de la codificación no se ha emparejado
byte a byte). **VERIFICADO:** el constructor LIRO A7S `0x43862e24` escribe `pkt[+0x00..+0x15]` (22 B) por el mismo puntero,
y el parser Darwin consume los mismos 22 offsets → correspondencia 1:1 de offsets (sin cabecera intercalada en el cuerpo).

## 3. Parser CAIF ev1 (S53-B.2/B.3)

Ambos parsers son el mismo código salvo una inserción. Campos (S = estructura de control del obturador):

| pkt | Destino | Comentario |
|---|---|---|
| `+0x00` | `S+0x30` | `S+0x30==0 && S+0x43==0` ⇒ aceptar (retorno 1) |
| `+0x01` | `S+0x31` | clase; reescrita después según tipo de mecanismo (`0x202ba`/`0x20c90`): 1/2 → `&~3`; 3 → `+1`; 4 → `+2` |
| `+0x02..03` | `S+0x32` | u16 (0 ⇒ `S+0x3c=0`) |
| `+0x04..0b` | `S+0x34..0x3a` | `S+0x3a==0` ⇒ 7000 |
| `+0x0c` | bits 0-5 → `S+0x3c`; bits 6-7 → `S+0x46` bits 2-3 | también leído por `0x16ecc/0x17812` (timeouts) y `0x1e794` (indicador) |
| `+0x0d` | `S+0x3d` (byte entero) | lectores hallados solo prueban el **bit 0** |
| `+0x0e..11` | `S+0x3e..0x41` | |
| `+0x12` | bit 3 → `S+0x42`; bit 0 → `S+0xd0` b0; **A7S: bit 5 → `S+0xd0` b5** | ver abajo |
| `+0x13..15` | `S+0xd1..d3` | |

**VERIFICADO (bytes A7S `0x18460..0x18488`, ausentes en A6000 tras `0x18052`):**

```text
ubfx r1, r0, #5, #1          ; r0 = pkt[+0x12]
bfi  [S+0xd0], r1, #5, #1     ; S+0xd0.b5 = Silent
lsls r0, #0x1a ; bpl          ; si Silent:
S+0x31 = (S+0x31 & ~3) + 2    ;   clase forzada a 2 (luego sujeta al tipo de mecanismo)
```

A6300 2.01 (cámara con Silent) contiene la misma inserción en su parser `0x1943e` (control positivo).
A6000 no tiene ningún otro lector de `S+0xd0` bit 5 (búsqueda en el pseudocódigo completo y barrido de `ldrb/strb #0xa0`).

**Modo 2 de `pkt[+0x0d]` (H53-2):** Darwin guarda el byte íntegro en `S+0x3d`; en ambas ROM los lectores encontrados
sobre S (A6000 `0x17a82…0x1820a`; A7S `0x17e82…0x18642`, `0x1d040`, `0x1d342`) solo usan o fijan el bit 0.
**No se encontró consumidor de los bits 6-7** (cobertura: pseudocódigo Ghidra de 2002/2055 funciones + barrido capstone;
una búsqueda vacía no prueba ausencia).

## 4. Consumidores del bit Silent en A7S (S53-B.3 / D)

`0x19a86` = predicado **no_silent** = `!(S+0xd0 & 0x20)`. Se pasa como argumento en la fase de exposición `0x191a6`
(y `0x17e44`, `0x18aa4`, `0x193fe`, `0x19562`) a las primitivas `0x19d34/0x19d6a/0x19db2/0x19dcc/0x19e00/0x19e48`, que lo
copian a `S+0x154` bit 4 (leído después por `0x216c2` en los manejadores diferidos) y lo entregan a los escritores de bobina.
Detalle hasta el pin en [s53-curtain-actuator-control.md](s53-curtain-actuator-control.md).

Además, en Silent (`0x191a6`) no se aplica la corrección `0x18e66` a `S+0x48` y los manejadores `0x2116e`/`0x21282`
no arrancan ni evalúan el seguimiento de posición por ADC (no hay error de fase `0x16958(6,1,0x20,…)`).

## 5. Ruta completa reconstruida (S53-E)

```text
BIONZ X (IC6000, av-cam): 0x43862e24 construye pkt (Silent: +0x12|=0x20, +0x0d modo 2, +0x01 clase→2)
  → CAIF ev1 0x436d8354 (22 B, op 0x10300) → cola de dispositivo 0x740017 (ABI sio)          [VERIFICADO S52]
  → MSS_SO/SI/SCK_DWN (P36–P38) = MFS5 CSIO de Darwin                                          [VERIFICADO esquema A6000 + descriptores]
  → mss-async 0x12172/0x122a6, tabla ID 0x0c (22 B, código 03 01)                               [VERIFICADO bytes; identidad ev1: INFERENCIA fuerte]
  → copia 0x1efb8(6) / 0x1709c → parser 0x17f8c (A6000) / 0x18396 (A7S)                         [VERIFICADO]
  → A7S: S+0xd0.b5 → no_silent 0x19a86 / 0x216c2 → primitivas de exposición
  → escritores PDOR bit-band 0x42668000+0x234 (P4D) / +0x238 (P4E) → FET Q6832 → bobinas 1C/2C [pines: esquema A6000; A7S: INFERENCIA]
```

**NO VERIFICADO / subordinado:** mensaje tipo 3/`0x22` (C1 de S52, `0x438627d2`, `0x43aed4ba`, `0x437c3114`) — no se
buscó su receptor en Darwin; respuestas CAIF ev3; polaridad física exacta (qué nivel suelta cada cortina).

## Herramientas y entorno

- `capstone` 5.0 instalado de forma permanente para el usuario (`pip install --user --break-system-packages capstone`;
  `sudo pacman` no disponible sin contraseña).
- Ghidra headless con `analysis/s53/ghidra/S53SeedDarwin.java` (verifica SHA-256; siembra vectores, tabla `0x4300` y
  punteros Thumb a prólogos `push`) y `S53DumpDecomp.java` (pseudocódigo de todas las funciones). `fold_literals.py`
  sustituye `DAT_<literal>` por su valor ROM. Proyectos `s53-*-darwin.rep` y volcados `.c` son regenerables (ignorados en git).
- REA 6.5.0 disponible (Ghidra 12.1.4, JDK 21) pero no se usó para Darwin: es el mismo motor y el análisis completo por
  lotes con scripts era más directo para 3 ROM pequeñas; todo lo decisivo se verificó contra bytes originales.
- Vista ELF nueva `analysis/a7s-darwin-rom-analysis-view.elf` (`.text` en `0x4200`, bytes idénticos al original).
- SHA-256 de las tres ROM comprobados antes y después (la prueba los exige).
