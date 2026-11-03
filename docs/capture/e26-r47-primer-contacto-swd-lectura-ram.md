# E26-R47 — Primer contacto SWD con la A6000 bloqueada: DAP abierto y lectura de RAM (solo lectura)

Fecha: 03-11-2026. Ejecución física de las fases F1–F7 de [R46](e26-r46-procedimiento-fisico-swd.md), con autorización del usuario. **No se escribió en NAND ni en RAM.** Hubo escrituras de control en `CSW`/`TAR` del AP (necesarias para leer) y, en §9, `halt`/`resume` de la CPU 0 y las escrituras de depuración que hace OpenOCD (`cortex_a`) para ello.

Etiquetas: **MEDIDO** · **LEÍDO** (dato leído por SWD) · **INFERENCIA** · **NO VERIFICADO**.

## 1. Montaje (MEDIDO)

| Elemento | Detalle |
|---|---|
| Sonda | RP2040 Zero con `debugprobe-zero` v2.3.0 (inindev/debugprobe-zero, CMSIS-DAPv2 `2e8a:000c`); SWCLK = GP10, SWDIO = GP11, GND físico |
| Cámara | Hilo al pad del lado BIONZ de R4911 (SWCLK) y de R4912 (SWDIO), más masa. Opción 5a de R46. R4911, R4912, R4915, R4916 y CN4906 sin montar |
| Tensión en reposo (cámara bloqueada) | R4911 = 3,09 V y R4912 = 3,09 V (lado BIONZ), dentro del criterio 3,0–3,3 V de F4 |
| Herramienta | OpenOCD 0.12.0 con `swd newdap` + `dap create` (sin target; `dap info` falla sin target en esta versión) |
| Velocidades | 100 kHz (primer contacto) y 1 MHz (volcados). A 1 MHz las 256 palabras de prueba coincidieron con las de 100 kHz |

## 2. DAP (LEÍDO)

| Dato | Valor |
|---|---|
| DPIDR | `0x3ba02477` (válido) |
| AP0 | IDR `0x44770001` (AHB-AP; `CSW=0x02800062`, `BASE=0xffffffff`) |
| AP1 | IDR `0x24770002` (APB-AP; `CSW=0x80000042`, `BASE=0x80000000`) |
| AP2 | IDR `0x14760010` (JTAG-AP) |
| AP3–AP5 | IDR 0 (vacíos) |

El tipo de AP se dedujo del campo `[3:0]` del IDR; no se contrastó con documentación del CXD90014. `CTRL/STAT` del DP **no se leyó**.

**Conclusión:** no hay bloqueo de lectura por eFuse. La mayor incógnita de R46 («DAP bloqueado por eFuse») queda resuelta **para lectura** por AP0. La escritura no se probó.

## 3. Lectura de memoria (LEÍDO)

- AP0 `@0x00000000` y `@0x00000004` = `0xe59ff0e8` (`ldr pc,[pc,#0xe8]`, vectores ARM). INFERENCIA: código de arranque.
- Volcado RAM `0xc0000000`–`0xc0100000` (1 MiB): dos pasadas a 1 MHz (~91 s cada una) **idénticas byte a byte**. SHA-256 `ce4274aea48a06a42ae3b1cd19c287999c3350b395fee4ef997a0b4854a2efa9`. 253 de 256 bloques de 4 KiB con datos.
- Volcado RAM `0xc0100000`–`0xc0300000` (2 MiB): SHA-256 `f0800e39aeb274d798d75b6a52013b4358de3405b04dbbfa123305c45e8ce85a`. Dos pasadas (~180 s cada una) **idénticas byte a byte**.
- `[0xc006000c]` = 0.

Los volcados contienen código de Sony y la tabla de `0xc0001200`: **no se versionan** (quedan fuera del repo).

## 4. Loader3 en RAM (LEÍDO + cotejo con volcado del 20-10)

- La imagen en `0xc01f0000`–`0xc0205800` (43 páginas de 0x800 = 88 064 bytes) es **idéntica byte a byte** a `bootloader.bin` del volcado `updater-20261020-175427` (offset `0x22800`). 0 bytes distintos.
- Por tanto el Loader3 que corre en la cámara bloqueada es el original de Sony, sin modificar. Los bytes en `0xc01f3bf6` son `e7 e7`, el salto hacia atrás de R40 (bucle de parpadeo).
- El código contiene los literales `ERROR: Blinking LED[LDR2=%d LNG=%d SHT=%d]` y `ERROR: Loader boot failed.` junto a ese bucle. Son literales: no prueban por sí solos qué ruta se ejecutó.

## 5. Log de Loader en RAM (LEÍDO)

Buffer en `0xc006001c`. Loader2 v33.01.90 → Loader3: inicializa alimentación y DDR (`LD3:ddr:0/serr:1/ld:0`), monta la partición 2 (FAT12) sin error, `BootMode: 11` (sin actualizador) y termina en:

```
LD3:Load Image
LD3:Run Config(init HW)
CFG:Set PORT [sz=4608]
CFG:Set INT  [sz=3072]
CFG:Set REG  [sz=768]
```

Después hay bytes sin escribir. **No aparece −302 ni fallo de lectura de `nflasha3`.**

## 6. Discrepancia con R36 / wiki 14 (a verificar)

R36 infiere que la primera lectura de `nflasha3` falla y que Loader3 da −302. El log muestra que Loader3 llega a `Load Image` y a `Run Config(init HW)` y se detiene dentro de esa configuración, sin mensaje de error. Dos lecturas posibles, ninguna demostrada:
1. El buffer no registra el error final (el log puede cortarse antes del fallo).
2. El fallo no está en la lectura de `nflasha3` sino después (configuración de hardware o carga de imagen).

Esto no refuta R36: la ejecución real de Loader3 sigue sin conocerse. Pero reduce la confianza en que escribir `nflasha3` (R46 F8-B) o `\updater\mode` (F8-A) resuelva el bloqueo.

## 7. No verificado (tras §9)

Por qué el log de RAM no recoge el mensaje final de error; qué función devuelve el −302 (ver §9); `CTRL/STAT`; escritura en NAND desde el BIONZ (R39: solo análisis).

## 8. Siguiente paso propuesto (sin ejecutar)

Ninguna escritura en NAND hasta localizar qué comprobación devuelve −302 (§9). Siguiente lectura útil: nombre del fichero de configuración que intenta cargar `CFG` y su partición.

## 9. `halt` de la CPU 0 y registros (03-11-2026, autorizado por el usuario)

**ROM table (APB-AP, `0x80000000`; LEÍDO).** Tabla anidada en `0x80100000` con 16 componentes en `0x80110000`–`0x8011f000`: cuatro **Cortex-A5** (part `0xc05`, depuración en `0x80110000`, `0x80112000`, `0x80114000`, `0x80116000`) con sus PMU (`0x9a5`), CTI (`0x906`) y ETM (`0x955`). Se actuó solo sobre el núcleo 0 (`0x80110000`).

**Halt (MEDIDO).** OpenOCD `cortex_a -ap-num 1 -dbgbase 0x80110000`: la CPU 0 estaba `running`; halted en Thumb, modo Supervisor, `cpsr=0x800001f3`, MMU y cachés activas. Diez muestras halt/resume: **PC = `0xc01f4f98` siempre**. Tras cada muestra se hizo `resume`; la CPU quedó `running`.

**Dónde está parada (LEÍDO + desensamblado de la RAM).** `0xc01f4f88` es una espera activa: `r1 = [0xf240300c]` mientras `r1 < r4`. El contador de `0xf240300c` avanza (tres lecturas: `0x99bc5`, `0x9a152`, `0x9a72e`) y `r4` toma valores distintos entre muestras (`0xf4240`, `0x1e8480`): es el temporizador del **bucle de parpadeo de LED** (`c01f3b74`, R13/R40), no un cuelgue.

**Código de error (MEDIDO).** `c01f3b74` calcula `r4 = −código`, `LDR2 = r4/1000`, `LNG = (r4%1000)/100`, `SHT = r4%100`. En la segunda muestra `r7 = 0` (LDR2), `r8 = 3` (LNG), `r6 = 2` (SHT): el código es **−302**. R36 lo infería; ahora está medido en registros y coincide con el LED observado (3 largos + 2 cortos).

**Qué devuelve −302 (INFERENCIA, no cerrado).** El literal `0xfffffed2` aparece en `0xc01f2e1c`, `0xc01f3250` y `0xc01f4148`. Se descarta el de `0xc01f2e1c` (`BOS_E:Partition signature error`): la firma esperada `"8246"` está en RAM en el puntero `0xc00e04ac` y coincide. El de `0xc01f3250` es la rama `CFG_E:Load file [%s]` (la lectura de un fichero devuelve ≤ 0) y encaja con el último mensaje del log (`CFG:Set REG`); el de `0xc01f4148` es de la capa FAT. No se determinó cuál se ejecutó. Si es el de `CFG`, el fallo estaría en la carga de un fichero de configuración tras `Run Config(init HW)` y no en la lectura de `nflasha3` que supone R36.

**Pila (LEÍDO).** `sp_svc = 0xc01ebfe0`, `lr_svc = 0xc01f4f95`; retornos en `0xc01f1333`, `0xc01f123b` y `0xc01f01ef` (despacho de modo de arranque 11 en Loader3).
