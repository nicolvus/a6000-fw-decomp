# E26-R21 — Receptor serie del BootROM: pin, trama y velocidad (30-10-2026)

Sin mediciones físicas: BootROM (`0xffff0554`, `0xffff05da`, `0xffff0634`, `0xffff0f52`) más el código fuente Sony del SoC (`analysis/session18/main/sony-oss-extracted/linux/arch/arm/mach-cxd90014/`). Test: `tests/test_e26_r19_r20_cierre.py`.

## 1. Resultado

1. **VERIFICADO (fuente Sony + binario).** `regs-misc.h`: `MISC_MODEREG_BOOT_SERIAL_IN = 0x0002`. La entrada serie del BootROM es el **bit 1 de `MODEREG` (`0xf2915010`) = pin `BOOT_SERIAL_IN` (IC6000 H21)**. Antes era inferencia (R9 §«no confirmado que bit 1 sea ese pin»). El bit 0 no está definido en el código Sony: `BOOT_MAIN` = bit 0 sigue como inferencia.
2. **BINARIO.** `0xffff0634` **no es un UART de hardware, es un receptor por software**: espera hasta el instante de muestreo de una tabla (`0xffff0f52` sobre el contador `0xf240310c`), lee `MODEREG` bit 1 y lo vuelve a leer tras un retardo de filtro (`0xffff05da`, debe coincidir; si no, error `0x3004`).
3. **BINARIO.** Trama de 11 bits: **inicio = 0** (un 1 en el primer instante → error `0x19`), **8 bits de datos LSB primero** (`cmp r4,#8`), **paridad impar** (el bit esperado es 1 cuando el XOR de los datos es 0) y **bit de parada**. Instantes en `tabla[0..10]` con `+0x24`/`+0x28` = paridad/parada.
4. **BINARIO.** `0xffff0554` elige perfil según GPIO(4,RDATA) bit 21 y lo deja en `0xc0010218`:

| Campo | bit21 = 1 | bit21 = 0 |
|---|---|---|
| tabla (`+0x1c`) | `0xffff1a1c`: paso 84 ticks/bit, 1.er instante 28 | `0xffff19f0`: paso 250 ticks/bit, 1.er instante 100 |
| filtro (`+0x10`) | 1 tick | 20 ticks |
| `+0x14/+0x18` | `0x15f900` (1 440 000) | `0x44aa20` (4 500 000) — uso no trazado |

5. **Velocidad (INFERIDO).** El BootROM programa el temporizador con `0x1030` = `TMST|TMCS_FREERUN|TMCK_DIV1`. En el código Sony, `TMCK_DIV4` = «1 MHz» (`hwtimer.c`) → reloj base 4 MHz, `DIV1` = **4 MHz**. Entonces: bit21=0 → 250 ticks = 62,5 µs = **16 000 baudios**; bit21=1 → 84 ticks = 21 µs ≈ **47 600 baudios** (nominal 48 000). Supone el mismo reloj base que Linux; si cambiara, ambas velocidades escalan por igual (relación fija 2,98).

## 2. Correcciones

- **Corrige R8/R9/R11:** `0x04A0/0x038D…` y `0x0E74/0x0B18…` no son divisores de baudios de un UART de 115 200; son temporizaciones del receptor por software. «Velocidad NO DETERMINADA» → ver §1.5 (inferida). Las notas «no confirmado que bit 1 sea ese pin» quedan resueltas por §1.1.
- El BootROM tampoco admite 115 200: ninguna de las dos velocidades se acerca.

## 3. Efecto práctico (solo teórico: sin hardware)

Un transmisor para la ruta serie necesitaría **8O1 a ~16 000 baudios** (strap bit21=0) o ~48 000 (bit21=1), nivel inactivo alto, sin sincronización previa. Un adaptador FTDI/CP210x admite esas velocidades con divisor personalizado. Sigue sin saberse qué pin físico es GPIO(4) bit 21 (por tanto qué perfil se usa en esta cámara) ni si la tabla de clave `0xc0001200` está vacía.

## 4. Límites

Reloj base del temporizador no verificado en silicio; semántica de `+0x14/+0x18`; espera del flanco de inicio (el contador se pone a cero antes de `0x634`, no trazado); GPIO(4) bits 21/22 sin nombre de pin.
