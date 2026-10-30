# E26-R12 — Auditoría estática del sistema de arranque (BootROM, Loader2, Darwin)

Fecha: 30-10-2026 · Parte de `aa37912a` (R11) · Solo análisis estático y emulación offline. Sin cámara, sin UART/USB, sin payloads.
Fuentes: `analysis/camera-dumps/20261020-174955/bootrom.bin` (24 576 B), `analysis/camera-dumps/updater-20261020-175427/bootloader.bin` (Loader2; dirección→offset: `addr − 0xc01f0000 + 0x22800`), `firmware/extracted/fw321/.../0640_darwin/darwin_core.bin`.
Scripts: `analysis/e26-recovery/r12-loader2-led-codes.py`, `r12-selector-emulation.py` · Tests: `tests/test_e26_r12_led_codes.py`.

## 1. Resumen ejecutivo

1. **Selector del BootROM (VERIFICADO en bytes):** `main` (`ffff1062`) lee `*(0xf2915000+0x10)` (literal `ffff12c0`, instrucciones `ffff1094..109e`), hace `ands r0,r0,#1` y lo guarda en `0xc0010010`. `bit0 = 1` → rama serie (`ffff10de`); `bit0 = 0` → arranque desde almacenamiento (`FUN_028c` → `FUN_02c6` → `FUN_013c`, salto a `0xc0030000`). La condición es un **registro externo** (`MISC_MODEREG`), no un valor del software. No se puede saber desde aquí qué contacto lo fija.
2. **Códigos de LED del BootROM (VERIFICADO):** `FUN_ffff0d62` parpadea `(código>>12)−1` veces lento y `código&0xfff` veces rápido. Los códigos que alcanzan esa función están en `0x1001..0x100e`, `0x2001..0x2005` y `0x3001..0x3004`: **máximo 2 lentos**. El patrón del usuario (3 lentos + 2 rápidos) **no puede salir del BootROM**.
3. **Códigos de LED de Loader2 (VERIFICADO):** `FUN_c01f3b74` recibe `−código` y descompone `n = −código` en miles / centenas / resto-100, con tres velocidades (`d`, `d/4`, `d/8`). El error **−302** da 0 + **3** + **2** (tres de velocidad media, dos rápidos), compatible con lo que el usuario describe. **−302 es solo la lectura más simple** (3002 y 3200 darían también 3+2 con otra repartición): HIPÓTESIS, no identificación del fallo.
4. **Corrección:** R7 anota `return 0xfffffed1 (-0x12e)`; `0xfffffed1 = −303`, `−0x12e = 0xfffffed2 = −302`. El literal real en el binario es −302 (`0xc01f2e1c`, `0xc01f3250`, `0xc01f4148`). Hay un typo hexadecimal en R7; el mapeo a patrón de LED cambia (3+3 vs 3+2).
5. **Darwin** conserva secuencia de alimentación por fases (`PwrCtrl Phase1..4`), watchdog virtual y canales serie `mss-sync/async` hacia BIONZ (hipótesis). No hay evidencia que atribuya el fallo a Darwin, a la NAND ni a BIONZ.

## 2. Grafo de arranque desde reset (VERIFICADO + emulación)

```
reset ffff0000 → ffff0058 (core id / pila)
  → main ffff1062
      FUN_d14, FUN_efc, FUN_d4c, FUN_244 (init reloj/GPIO/temporizadores)
      lee MODEREG(0xf2915010) bit0 ──────────────┐
  bit0 = 0 (arranque normal)                     bit0 = 1 (serie)
   FUN_028c (FUN_12d8: init almacenamiento)       ffff10de → GPIO4(0xf2910410) bit22:
     ≠0 → blink 0x1003/err                         =1 → FUN_0fa0 (receptor)
   FUN_02c6 (FUN_0150 lectura, 0xc0010000..)       =0 → sigue sondeando → FUN_0fa0 → FUN_0876
     0x3005→err 0x1004, 0x3006→err 0x1005       FUN_0876 (bucle bit-level, FUN_0634)
     otro ≠0 → return 0 (tratado como éxito)      errores 0x3001..0x3004, 0x100c/d, 0x2003..5
     0 → FUN_013c → bx 0xc0030000                 éxito → FUN_0144 (bx a dirección del marco)
  Cualquier error → FUN_0d62 (blink, no retorna)
```

Emulación (`r12-selector-emulation.py`, Unicorn, solo entradas de periférico modeladas): `MODEREG=0` entra por `ffff10a2` (arranque normal); `MODEREG=1/3` entra por `ffff10de` y llega a `FUN_0876`, que muestrea `MODEREG` bit1 (`ffff08b2`). `GPIO4` bit22 cambia la ruta de espera (`ffff10f6` directo a `FUN_0fa0` o sondeo previo). **Límite:** el almacenamiento no está modelado, así que el código `0x1004` del caso `MODEREG=0` es un artefacto de la emulación, no una predicción de la cámara.

Observación estática (no probada): en `FUN_02c6` un retorno de `FUN_0150` distinto de 0, `0x3005` y `0x3006` cae en `ffff0304 → return 0` (éxito aparente) y salta a `0xc0030000`.

## 3. Origen de las condiciones de bifurcación

| Condición | Instrucción | Origen | Clase |
|---|---|---|---|
| Serie vs. almacenamiento | `ffff1096 ldr r0,[r0,#0x10]; ands #1` | `0xf2915010` bit0 (registro externo) | Registro externo; contacto físico NO identificado |
| Entrada serie (datos) | `ffff08b2` en `FUN_0876` | `0xf2915010` bit1 = `BOOT_SERIAL_IN` | Registro externo |
| Divisor de baud | `FUN_0554` | `0xf2910410` bit22 (GPIO4 RDATA) | Registro externo; relación con bit1 NO demostrada |
| Espera/tiempo | `FUN_0efc/0f36/0f52` | contadores `0xf240300c/0xf240310c` | Hardware libre |
| Éxito de almacenamiento | `FUN_028c/02c6` | lecturas NAND, bits `0x20410` | Estado del dispositivo |
| Códigos de error | `movw` inmediatos | constantes ROM | ROM |
| Flag en `0xc0010010` | `ffff109e str` | copia software de MODEREG bit0 | Derivado |

R8/R9 describen la bandera como «`DAT_ffff12c0+0x10` bit 0»: `DAT_ffff12c0` es el literal `0xf2915000`, es decir MODEREG; la bandera no es de software.

## 4. Mapa de interfaces serie

| Señal | Registro/destino | Independiente | Evidencia |
|---|---|---|---|
| `BOOT_SERIAL_IN` | `0xf2915010` bit1 (BootROM) | Entrada leída por polling, no es un UART de periférico | R8/R9/R12 §3 |
| `DEBUG_UART0_RXD/TXD` | UART0 de BIONZ (AB19 TX) → CN4906 pin 4/5, CM4008 → Multi Terminal | Periférico UART0 | Esquema pág. 38 (R11) |
| `UART_RXD/TXD_MSS` | Mismo net que `DEBUG_UART0_*` en CN4906 | Alias de nombre, mismo hilo | R11 tabla CN4906 |
| `0xf2910410` bit22 | GPIO4 RDATA (selecciona divisor) | Entrada GPIO | R8/R9 |
| `0xf2915010` bit0 | Selector de modo | Entrada de estrapping | R12 §3 |

No hay evidencia de que `BOOT_SERIAL_IN` comparta contacto con `DEBUG_UART0_RXD`: en el esquema solo los une el net hacia CN4001 pin 9 vía R4003/R4002 (`XX`). Darwin tiene su propio SIO (`sio_err[mss-sync]` en `0xddeb`, `[mss-async]` en `0xe207`); el vínculo exacto con los nets MSS del esquema queda NO VERIFICADO. No se diseña ningún procedimiento de escritura.

## 5. Dependencias Darwin / BIONZ (estático, parcial)

Cadenas de `darwin_core.bin` (offsets de archivo): `PwrCtrl: Phase1..4: Enable ch` y `Error! PhaseN` (`0x118a0..0x11988`), `Virtual watchdog:detected dead lock` (`0x3a04`), `[ERR]wakeup msg` (`0x4450`), `[ERR]PWRSPL` (`0x48e3`), `kBBOOT` (`0x48fe`), `power key: usb boot event` (`0x6d18`), `VBUS Short Detected` (`0xd57c`), `Batt ocv/ccv`, `sio_err[mss-sync/async]`, `DWN_VER0.78` (`0x21938`).

```
batería/USB ─▶ Darwin (FM3): PwrCtrl Fase1..4 (alimentación por canales, error por fase)
      │ power key / usb boot event / wakeup msg
      ▼
BIONZ ◀── MODEREG strap (modo) ── BootROM ffff0000 ─▶ Loader2 (c01f0000, bootloader.bin)
                                                    └▶ Loader3 / kernel (0xc0030000 …)
Darwin ⇄ BIONZ: SIO `mss` (sync/async), supervisión por watchdog virtual de tareas de Darwin
```
Lo que sigue sin leerse: la lógica que decide el valor del strap `MODEREG` bit0 y la política de reset de BIONZ por Darwin (no en `darwin_core.bin` analizado). Esto es esquema arquitectónico, no un grafo verificado función a función.

## 6. Rutas de error y diagnóstico del LED

| Fuente | Codificación | Patrón posible | Verificado |
|---|---|---|---|
| BootROM `FUN_0d62` | `(c>>12)−1` lentos + `c&0xfff` rápidos | `0x1001..0x100e` (0 lento), `0x2001..0x2005` (1 lento), `0x3001..0x3004` (2 lentos); 3+2 imposible | SÍ (`ffff0d62..0e08`, callers `0fe6..126e`) |
| Loader2 `FUN_c01f3b74` | `n=−c`: `n/1000`, `(n%1000)/100`, `n%100` con retardos `d`, `d/4`, `d/8` | −302 → 3 medios + 2 rápidos; −304/−306/−308 → 3 + 4/6/8 | SÍ (`c01f3b74..3bf6`, `r12-loader2-led-codes.py`) |
| Loader3 / NAND | No decodificado en R12 | — | NO |

Consumidores del literal −302 en Loader2: funciones en `c01f2c98`, `c01f2f24` (rama FAT/montaje de R7b), `c01f3d8a`, `c01f3e54`, `c01f3fd0`, `c01f407e` (zona `FUN_c01f3d50` «Init FAT», R7). −306 (nueve usos, incl. `c01f04b2` del kernel NULL según R7b), −304 (`c01f6c4c`), −308 (`c01f51c6`).

Conclusión admisible: el patrón del usuario es **compatible** con un error −302 de Loader2 en la familia FAT/almacenamiento y **no es** un código de BootROM. No se atribuye el fallo: faltan la identificación del consumidor concreto que se ejecutó y el dato real de qué parpadeos son «lentos».

## 7. Auditoría de resultados anteriores

| Punto | R7/R8/R9/R11 | Estado R12 |
|---|---|---|
| eSRAM | R9 decía 16 MiB; R11 corrigió a 1 MiB (`0xc0000000–0xc0100000`) | CONFIRMADO (mapa del emulador 0x100000; accesos `0xc000500c`, `0xc0010010`, `0xc0030000` dentro) |
| Checksum | CRC-32 reflejado `0xEDB88320`, `~acc` final | CONFIRMADO (`ffff0c00..0c0a`, acumulador `ffff077e..0794`) |
| Selector | «`DAT_ffff12c0+0x10` bit 0» sin origen | AMPLIADO: es MODEREG bit0 (registro externo) |
| Códigos LED | R7: `0xfffffed1 (-0x12e)` | **CORREGIDO**: −302 = `0xfffffed2`; `0xfffffed1` = −303 |
| Fallback de FUN_02c6 | R8 no lo recoge | NUEVO: códigos distintos de 3005/3006 → éxito aparente |
| Thumb/ARM | `ffff1062` y funciones ≥ `0x244` son Thumb; `0x58` y vectores ARM | CONFIRMADO |
| Emulación vs. hardware | Unicorn sin NAND/temporizadores reales | Declarado en cada salida; no es prueba física |

No se modifican R7–R11 en sitio: las correcciones quedan aquí y en `CORRECTIONS.md`.

## 8. Matriz de evidencia

| ID | Afirmación | Tipo | Estado |
|---|---|---|---|
| E1 | Selector = MODEREG bit0 en `ffff1094..109e` | Bytes + emulación | VERIFICADO |
| E2 | BootROM no emite 3 lentos | Bytes (todos los callers) | VERIFICADO |
| E3 | Loader2 decodifica −302 como 0/3/2 | Bytes (`c01f3b74..`) | VERIFICADO |
| E4 | Literales −302/−304/−306/−308 y consumidores | Escaneo de bytes | VERIFICADO |
| E5 | Typo `0xfffffed1` en R7 | Aritmética | VERIFICADO |
| E6 | Fallo de la cámara = −302 | Inferencia | HIPÓTESIS |
| E7 | Darwin SIO `mss` ⇄ BIONZ | Cadenas | HIPÓTESIS |
| E8 | Fallo en Darwin/NAND/BIONZ | — | SIN EVIDENCIA |
| E9 | Valor real de MODEREG bit0 en la cámara | Hardware | NO DETERMINABLE offline |

## 9. Incertidumbres documentales

- Contacto físico que fija MODEREG bit0 y bit1 (esquema sin trazar).
- Qué parpadeos ve el usuario como «lentos»: la tercera velocidad de Loader2 es `d/8`, la segunda `d/4`; `d` = `0x3d0900` (4 000 000, literal `c01f3c40`) en unidades de `FUN_c01f4f88` (espera activa); su conversión a milisegundos queda pendiente. Con `d`, `d/4` y `d/8` las tres velocidades son 1 : 4 : 8.
- Qué función concreta devolvió −302 en el fallo real.
- El volcado `bootloader.bin` es de `updater-20261020`; la cámara con fallo puede tener otra copia en NAND.

## 10. Recomendaciones para investigación offline posterior

1. Convertir `d = 0x3d0900` y el reloj de `FUN_c01f4f88` para pasar −302 a milisegundos y comparar con el vídeo/observación del LED.
2. Mapear los seis consumidores de −302 a las cadenas de log de Loader2 (`LD3_E_*`) por función.
3. Revisar en `darwin_core.bin` las funciones que escriben las líneas de strap/reset (xrefs a `PwrCtrl`), con REA/Ghidra.
4. Comparar `bootloader.bin` y la copia secundaria del backup por hash y por tabla de errores.
5. Ampliar la emulación solo con entradas de periférico; no generar tramas serie.

## Cierre Q1–Q7

| Q | Respuesta |
|---|---|
| Q1 | SÍ, flujo reset→main→dos ramas reconstruido en bytes y emulación (§2). |
| Q2 | PARCIAL: el origen es MODEREG bit0 (registro externo), identificado; el contacto físico no. |
| Q3 | PARCIAL: `BOOT_SERIAL_IN` (MODEREG bit1) es una entrada por polling distinta del UART0 de BIONZ; comparten solo el net hacia CN4001/R4003 (§4). |
| Q4 | PARCIAL: dependencias de alimentación, watchdog, wakeup y SIO identificadas por cadenas (§5); sin grafo función a función. |
| Q5 | SÍ: el patrón 3+2 no sale del BootROM y sí de Loader2 −302 (HIPÓTESIS sobre el valor real); códigos tabulados (§6). |
| Q6 | SÍ: corregidos typo de R7 (−303 vs −302) y origen de la bandera del selector; eSRAM y CRC confirmados. |
| Q7 | Medir `d`, mapear consumidores de −302 a logs, xrefs de Darwin a líneas de strap, comparar copias del loader (§10). |
