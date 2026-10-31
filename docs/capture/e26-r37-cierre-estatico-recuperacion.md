# E26-R37 — Cierre estático tras R36: entrada al actualizador, paquete 3.26, consola UART y Darwin al encender

Fecha: 31-10-2026. Continúa [R36](e26-r36-causa-fallo-325.md). **Solo análisis offline** de `bootloader.bin` (Loader2 en `0x600`, Loader3 en `0x22800`), del volcado `dev_nflasha1.bin`, de los BK4 históricos y de `darwin_core.bin`. Sin cámara ni USB. Pedido del usuario: avanzar por (a) entrada sin NAND a una ruta que no lea `nflasha3`, (b) paquete de recuperación 3.26, (c) captura UART y (d) Darwin del 3.25 al encender, hasta cerrar todo lo estático.

Etiquetas: **BINARIO** (Capstone, bytes releídos) · **DATOS** · **SCRIPT** · **INFERENCIA**. Pruebas: [`tests/test_e26_r37_cierre_estatico.py`](../../tests/test_e26_r37_cierre_estatico.py) (5). Constructor: [`scripts/e26_recovery/build_326.py`](../../scripts/e26_recovery/build_326.py) → [`manifest-recuperacion-326.json`](../../analysis/e26-recovery/manifest-recuperacion-326.json).

## 1. Resumen

| Letra | Resultado |
|---|---|
| a | **Ninguna entrada sin escribir NAND.** Solo el modo 3 (UPDATER) evita `nflasha3`, y solo se elige si existe `\updater\mode` en `nflasha2`. Teclas, USB y batería no llevan a él. **Hallazgo útil:** basta un archivo vacío `\updater\mode` en `nflasha2` para que Loader3 arranque el actualizador de fábrica de `nflasha1` (intacto) en modo USER, que espera firmware por USB |
| b | **Paquete 3.26 listo y verificado dos veces** (`recuperacion-326/`): contenido oficial 3.21 idéntico al 3.24; solo cambian la versión y sus sumas. El 3.24 ya no sirve: el actualizador exige una versión mayor que 3.25 |
| c | **Una captura UART pasiva no confirmaría R36.** Loader2 y Loader3 solo escriben en la UART si `Backup[0x510015] == 1`, y vale 0 en los 12 volcados BK4. Sus mensajes van a un buffer en RAM que se pierde al apagar |
| d | **El Darwin del 3.25 solo puede comportarse como el 3.21 o como el 3.23, ambos probados en esta cámara.** El byte que lee la cueva se pone a 0 en cada reinicio de Darwin. Los vectores que pisa la cueva corresponden a IRQ que nunca se habilitan |

## 2. (a) Cómo elige Loader3 el modo de arranque (BINARIO)

`boot_dispatch` (`c01f11ec`) ejecuta `c01f0cca` (inicio, BOS y `nflasha2`), luego `c01f1de6` (elige modo), y salta por `[0xc00e0004]`:

| Modo | Destino | ¿Lee `nflasha3`? |
|---|---|---|
| 3 | `c01f1312` → tabla `tbb` en `c01f1320` → `c01f1334: bl c01f1378` (UPDATER) → `c01f068a` monta el dispositivo **1** (`c01f0696: movs r0,#1`) y carga `\boot\loadaddr.txt`, `vmlinux.bin`, `initrd.img` | **No** |
| 1, 2, 4, 5, 6, 10, 11, 12 | `c01f09e4` (Normal load) → RAMCFG `c01f2fe8` | Sí |
| 13, 14 | `c01f03e2` → RAMCFG `0x4000000` / `0x1000000` | Sí |
| 7, 8, 9 | `c01f036c` / `c01f129c`: reanudación desde RAM (warm/hot) | Solo útil con la RAM conservada (no tras quitar la batería) |

**Qué elige cada modo** (`c01f1de6`–`c01f2154`; casi todo son banderas del Backup leídas con `c01f498c`):

| Modo | Condición | Origen |
|---|---|---|
| **3** | `c01f1e10: bl c01f159a` («`BOM:chk updater`»: monta el dispositivo 2 y busca `\updater\mode`); `c01f1e14: cbz r0` → si **existe**, `movs r0,#3` | archivo en `nflasha2` |
| 5 | `chk adjust` (Backup `0x510011` + archivo `\mode\cmode` en `nflasha2`) o `chk ank` (lectura analógica de teclas dentro de la ventana Backup `0x5d000b`/`0x5d000c`, `0x5d0011` veces) | Backup + teclas → **ajuste de fábrica, que sí lee `nflasha3`** |
| 8, 9, 12, 6, 4, 2, 10, 11, 13, 14, 7 | `chk reboot`, `ontimer`, `image_update`, `usbcharge`, `cipa`, `hotboot`, `warmboot`, `ssboot`, `rmem`/`load_off`, … | Backup y estado de energía |
| 1 | por defecto | — |

Al final, `c01f2122` vuelve a mirar `\updater\mode`. Si no existe, `c01f51f4` **envía** el modo al subprocesador («`BOM_E:Sync mode`»). Envía, no recibe: el subprocesador no puede imponer el modo 3. **No hay ninguna otra instrucción que fije 3** (`movs r0,#3` + `b c01f212c` solo aparece en `c01f1e16`).

**Corrección de R26 §1.2 (punto 2):** R26 leyó al revés el `cbz r0,#0xc01f1e1a`. Cuando el archivo **no** existe, el salto se toma y sigue la cadena normal. Cuando **existe**, se ejecuta `movs r0,#3` y se elige UPDATER. Así, el archivo no es una «condición necesaria de la cadena especial 7–9/13/14»: elige directamente el modo 3.

**El actualizador de fábrica (DATOS, `dev_nflasha1.bin` del 20-10, FAT12 de 2013):**
- Contiene `\boot\loadaddr.txt` (`0x81528000,0x80628000`), `vmlinux.bin` (977 820 B) e `initrd.img` (cramfs, 3 809 280 B).
- El 3.25 no tocó `nflasha1`.
- Su `UdtrMain.sh` lee `/setting/updater/mode1|2|3|6`. Si solo existe `mode`, entra en **MODE_USER**: `execute_ufp.sh` → `prepare-usb.sh` → `sauu` espera un firmware por USB.
- Si existe `\updater\comp` (presente en el volcado de `nflasha2`), borra `mode*` al empezar. Por tanto, la actualización tiene que hacerse en esa misma sesión.

**Consecuencia:** la intervención física mínima ya no es reescribir los 11 MB de `nflasha3`. Basta crear un archivo vacío de 0 B en `\updater\` de `nflasha2` (una entrada de directorio FAT). Después se instala por USB un paquete de versión > 3.25, como en T024/T040. Sigue exigiendo escribir en la NAND, por lector externo o por la vía serie del BootROM con la clave de `nflasha0` ([R33](e26-r33-veracidad-clave-nflasha0.md)). No está autorizado ni probado.

## 3. (b) Paquete de recuperación 3.26 (SCRIPT, verificado dos veces)

`build_326.py` parte del 3.24 verificado en E25-05 (`.dat` `e1345aff…`, `.fdat` `24ee9b42…`). Cambia el byte `versionMinor` (`0x24 → 0x26`) y recalcula, sin reempaquetar los 200 MB:
- el CRC de la cabecera FDAT;
- la suma del primer bloque de 1024 B;
- su cifrado (los 512 B iniciales van con una sola pasada AES);
- el CRC DEND.

| Comprobación | 3.24 (base) | 3.26 |
|---|---|---|
| DEND, sumas de bloque, CRC de cabecera | ok | ok |
| `.dat` descifrado entero = FDAT plano (auditor E25-06) | sí | sí |
| Versión / modelo / región | 3.24 / `0x41030035` / 0 | **3.26** / `0x41030035` / 0 |
| `firmware.tar` y `updater.img` | oficiales (`97024649…`, `b6d51752…`) | idénticos |
| Bytes FDAT distintos | — | `[8,12)` CRC y `[32]` versión |
| Rangos `.dat` distintos | — | `[140,156)`, `[172,188)`, últimos 4 B (el mismo patrón que E25-05 midió entre 3.23 y 3.24) |
| Segunda verificación con `fwtool` | — | `readDat` (DEND), descifrado CXD90014 de los primeros 4096 B = FDAT, `readFdat` → 3.26 |

Resultado: `.dat` `c730f8e2…`, `.fdat` `e652ddb5…` en `analysis/darwin-patch/fdat/recuperacion-326/` (no versionado, como los demás paquetes).

Restaura el `nflasha3` y el Darwin oficiales sin tocar las calibraciones, igual que una actualización de Sony. No se ha probado en la cámara. Solo sirve si el actualizador vuelve a estar accesible (§2).

## 4. (c) Qué mostraría una UART pasiva (BINARIO + DATOS)

- `c01f3670` (log de Loader3) escribe en la UART (`c01f50c0`) si `[0xc0060000] ≥ nivel`. Escribe en un buffer de RAM (`c01f3640`) si `[0xc0060004] ≥ nivel`.
- `c01f35c0` llama a `c01f4edc`, que devuelve 1 solo si `Backup[0x510015] == 1`. En otro caso, pone a 0 el nivel UART y el registro de la UART no se inicializa (`c01f5008` no se llama).
- Loader2 tiene la misma lógica (`c00308d0`, `c003126c`, misma estructura en `0xc0060000`).
- **DATOS (12 volcados BK4):** `0x510015 = 00`, `0x510003 = 00`, `0x510006 = 06`. La consola está apagada y el log, incluido el `ERROR: Blinking LED[…]` de nivel 1, solo va al buffer de RAM.

R6 ya advertía que el logger podía estar silenciado. Con los 12 volcados queda claro que lo está. **Corrección de R36 §10 y de la recomendación de R12/R14:** una UART pasiva no mostraría nada de Loader2/Loader3 con la configuración de fábrica. La única confirmación externa sin abrir la cámara es grabar el LED (`E26-R14-LED-MEDIDA`). Eso confirma el código −302 de Loader3, pero no qué productor lo generó. El argumento diferencial de R36 sigue siendo la base.

## 5. (d) Darwin del 3.25 al encender (BINARIO)

| Comprobación | Resultado |
|---|---|
| Cueva `0x4318` | `ldr r2,=0x20003716; ldrb r2,[r2]; cbz r2 → b.w 0x1b080` (ruta Sony); si no es cero, `movs r0,#0; bx lr` (sin movimiento, como el 3.23) |
| Valor al reiniciar Darwin | la tabla de carga C (`0x2a744`) pone a cero `0x20002ed0…+0xf8c` con `0x4494`, y `0x20003716` está dentro → **0 = ruta Sony** hasta la primera captura |
| Valor sin reinicio de Darwin | el último `pkt[0x0e]` copiado por `0x17ff8`/`0x17ffc`; E25-24b no encontró otros escritores |
| Vectores pisados | la cueva ocupa las entradas 70–73 y 76 (IRQ 54–57 y 60), que valían 0 en Sony. Darwin solo habilita interrupciones con escrituras a `NVIC_ISER0` (`0xe000e100`: bits 14, 17, 24, 31). No hay ningún literal `0xe000e104` (ISER1, IRQ 32–63) ni de VTOR → esas IRQ nunca se habilitan |

**Conclusión:** cualquier valor del byte reproduce uno de dos comportamientos probados en esta cámara: 0 → Darwin 3.21 (uso normal) y ≠ 0 → B1a del 3.23 (T040–T053, arranques y apagados incluidos). Queda un riesgo no evaluable estáticamente: que el mecanismo quede a medio estado al alternar ambos modos (por ejemplo, apagar tras una captura electrónica con el menú en EFCS). Eso solo se resuelve en la cámara.

## 6. Correcciones trazables

- **R26 §1.2 punto 2:** condición invertida; `\updater\mode` presente → modo 3 (UPDATER, dispositivo 1).
- **R36 §10, R12 y R14 (recomendación de UART pasiva):** con `0x510015 = 0`, Loader2/Loader3 no escriben en la UART; la captura no confirmaría la causa.
- **E25-05 §límites, punto 6 («presupuesto de versiones»):** tras el 3.25, la recuperación es 3.26 (o mayor), ya construida.

## 7. Lo que queda (todo físico)

- Crear `\updater\mode` en `nflasha2` o restaurar `nflasha3`. Ambas cosas exigen escribir en la NAND: lector externo o BootROM serie con la clave de `nflasha0`.
- Grabar el LED para confirmar el patrón 0/3/2.
- Validar en la cámara la alternancia EFCS/electrónico del Darwin 3.25 si alguna vez se vuelve a instalar.

No queda ningún pendiente estático abierto que cambie la decisión de recuperación.
