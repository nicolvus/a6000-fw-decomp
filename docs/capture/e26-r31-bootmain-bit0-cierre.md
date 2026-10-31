# E26-R31 — Cierre estático: `MODEREG` bit 0 = `BOOT_MAIN` (`CL1000`) (31-10-2026)

Cierra la inferencia de [R20](e26-r20-bootrom-selector.md) §1.6 (`E26-R19-BOOTMAIN`) solo con código, fuentes Sony y esquema; sin hardware. Test: `tests/test_e26_r31_bootmain_bit0.py`.

Etiquetas: **BINARIO** (bytes/desensamblado) · **FUENTE SONY** (OSS) · **ESQUEMA** · **DEDUCCIÓN**.

## 1. Inventario completo de lectores de `MODEREG` (`0xf2915010`, «MODEREAD» en Sony)

| Consumidor | Bits | Uso | Etiqueta |
|---|---|---|---|
| BootROM `main` (`0xffff1094`, literal `0xffff12c0`) | **0** | selector: 0 = Loader2 por NAND, 1 = ruta de servicio/serie (R20/R23) | BINARIO |
| BootROM receptor (literal `0xffff0968`) | 1 | muestreo serie `BOOT_SERIAL_IN` (R21) | BINARIO + FUENTE SONY |
| Loader3 `0xc01f4ef8` (archivo `0x276f8`) | todos, en bruto | `ldr r0,[r4,#0x10]` → argumento de registro; sin prueba de bits | BINARIO |
| `mcmn_drv.ko` `getmsindata` | 16 | `MSX_INS_HIZ` (inserción Memory Stick) | BINARIO (cadena propia) |
| `mcmn_drv.ko` `getmmccddata` / `getmmcwpdata` | 24/26 · 25/27 | detección y protección de escritura de las ranuras MMC | BINARIO |
| `vmlinux` (fw 3.21) | — | la base `0xf2915000` solo se usa con `+0x00` (TYPEID) y `+0x20/+0x30/+0x44/+0x48/+0x50` | BINARIO |
| `av-cam.bin` (fw 3.21) | — | sin literal `0xf2915xxx` y **sin ningún `movt #0xf291`** (Thumb-2 T1 ni ARM A1; control positivo: el mismo barrido halla los 216 `movt #0x43bd`). Sí direcciona MMIO físico por literal (GPIO `0xf2910000`, temporizador `0xf2403000`), así que la ausencia es significativa | BINARIO |
| Loader2 | — | sin literal de la base `MISC` ni `movt #0xf291` | BINARIO |

Literales de la base `MISC` (`0xf2915000`) en la ROM: solo `0x968` y `0x12c0`; en `bootloader.bin`: solo `0x27768`. En los binarios escaneados (`*.bin`, `*.elf`, `*.ko`, secciones WBI), `0xf2915010` solo aparece en `mcmn_drv.ko` (A6000, A7S, A6300) y su copia WBI.

## 2. Deducción

1. **El bit 0 es un pin de arranque (BINARIO).** Su único consumidor en todo el firmware es el selector del BootROM; decide entre cargar la imagen principal de NAND y la ruta de servicio. Ningún otro código lo trata como dato de tarjeta, DDR o depuración.
2. **Los pines no-de-arranque del registro están identificados y ocupan bits altos (BINARIO).** 16 = `MSX_INS_HIZ` (red homónima en el esquema), 24–27 = CD/WP de MMC. Con eso, los bits bajos quedan para el bloque de arranque.
3. **El bloque BOOT del IC6000 tiene exactamente tres redes (ESQUEMA, A6000 pág. 24 y A6300 pág. 26):** `DDRCKSEL` (P8), `BOOT_SERIAL_IN` (H21), `BOOT_MAIN` (P7).
4. **`BOOT_SERIAL_IN` = bit 1 (FUENTE SONY CXD90014 + BINARIO R21).**
5. **`DDRCKSEL` no es el bit 0.** (a) Ningún software lo consume: `bootloader.bin`, que contiene la inicialización de la LPDDR2 (`musashi LPDDR2 Initialize`), no prueba ningún bit de `MODEREG`; es un strap de hardware. (b) En el chip hermano CXD4132 (FUENTE SONY) `DDRCKSEL` está en el bit 24, lejos del par de arranque. (c) Un pin de reloj DDR no selecciona «NAND o serie», que es lo que hace el bit 0. (d) ESQUEMA A6000 pág. 24 (captura aportada por el usuario, 31-10-2026): `DDRCKSEL` (P8) termina en un trazo corto **sin red ni isleta**; su nivel lo fija solo el IC6000 y nadie puede cambiarlo en la placa. En cambio `BOOT_MAIN` (P7) llega a `CL1000`, punto de prueba montado (círculo doble, frente a la isleta discontinua no montada `LND103` de `XRESET_18`). Es la única entrada del bloque BOOT preparada para forzarse desde fuera, como corresponde a un selector de modo de servicio.
6. **Nomenclatura Sony (FUENTE SONY CXD4132):** `MODEREAD_BM1 = 0x2` → «Boot Mode 1» en el bit 1; en CXD90014 ese mismo bit pasa a llamarse `BOOT_SERIAL_IN`. El par de arranque es BM0/BM1 = bits 0/1; BM1 = `BOOT_SERIAL_IN`, así que BM0 = la otra red de arranque = `BOOT_MAIN`.

**Conclusión: `MODEREG` bit 0 = `BOOT_MAIN` (IC6000 P7) = `CL1000`. CERRADO estáticamente por exclusión exhaustiva** (todos los lectores del registro inventariados; las tres redes BOOT asignadas o descartadas).

## 3. Límites

- `av-cam.bin` tiene un acceso GPIO genérico (`0xf2910000 + banco<<8`, lectura `>> bit & 1` en archivo `0x44e990`). Un llamador con banco `0x50` alcanzaría `0xf2915000`, pero el registro está en `+0x10` y ese acceso lee `+0x00`; no se enumeraron los argumentos de todos sus llamadores.

- Ninguna fuente nombra literalmente el bit 0 (`regs-misc.h` de CXD90014 solo define el bit 1). El cierre es deductivo, no una definición de hoja de datos.
- La polaridad física (si el nivel alto en `CL1000` produce bit 0 = 1) sigue sin probarse. El valor lógico en reposo sí se conoce: bit 0 = 1 ([R32](e26-r32-moderreg-valor-real.md), backup de la cámara).
- A6300: `BOOT_MAIN` va a la isleta `LND188` y `DDRCKSEL` a `LND911`, sin strap montado. `R6048 XX` está en la alimentación PCIe, no en `BOOT_MAIN`; no aporta polaridad.
