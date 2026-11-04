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

## 10. Tabla de ficheros de `CFG` y estado de sus destinos (03-11-2026, solo lectura)

**Rutas que referencia Loader3 (LEÍDO en la imagen en RAM):** `\boot\loadaddr.txt`, `\boot\vmlinux.bin`, `\boot\initrd.img`, `\updater\mode`, `\mode\cmode`, `\cipa.bin`, `\Backup.bin`/`.bak`.

**Tabla de configuración en RAM (`0xc005c000`, LEÍDO):** cinco entradas con ruta y rango de memoria, en este orden:

| Ruta | Rango de destino |
|---|---|
| `\sabin\idt_cam.bin` | `0x83501000`–`0x83540fff` |
| `\sabin\sa_dfdet.bin` | `0x96800000`–`0x9682ffff` |
| `\av-cam.bin` | `0x83541000`–`0x84140fff` |
| `\kemco.txt` | `0x80033000`–`0x80033fff` |
| `\initrd.img` | `0x80628000`–`0x80e27fff` |

`av-cam.bin` es el fichero que R36 sitúa en `nflasha3`. La relación entre esta tabla y la carga de ficheros de `CFG` es una INFERENCIA por los nombres y rangos; no se desensambló el código que la recorre.

**Destinos (LEÍDO por AP0, 8 palabras por rango):** `idt_cam` y `av-cam` leen `0xffffffff` en todas las posiciones muestreadas; `sa_dfdet` lee ceros; `kemco` (`0x80033000`) contiene código ARM; `initrd` contiene datos al principio (`0x077b…`) y `0xffffffff` más adelante. `0x80628000` es legible, así que la DDR de esa zona responde.

**Qué no permite concluir:** que `idt_cam` y `av-cam` estén a `0xffffffff` es compatible con «no cargados», pero también con relleno previo de la DDR. No se identificó qué fichero fallaba al devolver −302 (la pila del momento del fallo ya no existe: la CPU lleva en el bucle de LED).

**Siguiente paso posible:** desensamblar la función de `CFG` que recorre esta tabla y el bucle de ficheros (código en `0xc01f2f00`–`0xc01f3260`) para ver en qué orden carga y qué índice devuelve −302; es análisis estático sobre el volcado, sin tocar la cámara.

## 11. Análisis estático de `CFG` en Loader3: de dónde sale el −302 (03-11-2026)

Sobre el volcado de RAM (`0xc01f0000`, idéntico al original), desensamblado a mano; sin tocar la cámara.

- **`0xc01f2fe8`** lee la tabla de `0xc005c000` y recorre sus entradas (paso `0x90`) en orden. Para cada una cuya máscara de modo (`[entrada+0xc]` frente a `r7`) la selecciona llama a **`0xc01f2f24`**; si esta devuelve un valor negativo, el recorrido **termina y propaga el error**. Las no seleccionadas imprimen `CFG:skip`.
- **`0xc01f2f24`** (carga de un fichero): monta la partición `[entrada+0]` (`CFG_E:Mount part`, devuelve el código de la función de montaje) y lee el fichero de `entrada+0x10` hacia `[entrada+4]` con `0xc01f4654`. Si la lectura devuelve **≤ 0**: `CFG_E:Load file [%s]` y devuelve **`0xfffffed2` (−302)** en `0xc01f2f9a`. Si pasa, el tamaño se compara con el rango.
- **Entradas** (LEÍDO, §10): `idt_cam.bin`, `sa_dfdet.bin`, `av-cam.bin` e `initrd.img` están en la partición **3**; `kemco.txt` en la 2. El orden es `idt_cam`, `sa_dfdet`, `av-cam`, `kemco`, `initrd`.
- **Destinos** (LEÍDO, §10): `idt_cam` (`0x83501000`) no tiene datos (`0xffffffff`) y `sa_dfdet` (`0x96800000`) tampoco (ceros). Si la carga siguiera el orden de la tabla sin saltarse entradas, el primer fichero que no se cargó es **`\sabin\idt_cam.bin` de la partición 3** y el recorrido se detuvo ahí con −302.

**Conclusión (INFERENCIA fuerte, no verificada con registros):** el −302 procede de que la lectura de un fichero de la partición 3 devuelve ≤ 0 en `CFG`, lo que **encaja con R36** (la partición 3, `nflasha3`, no se lee bien) y no apunta a la firma de partición (§9, descartada). La partición se monta (no sale `Mount part`), pero la lectura del primer fichero falla.

**Cabos sueltos.** (a) El mensaje `CFG_E:Load file` y `CFG:Load file` no están en el log de RAM: probablemente el nivel de log los filtra (los mensajes de error de `CFG` van con nivel 3 y 6; el log recoge los de nivel bajo). Es inferencia. (b) No se verificó qué máscara de modo se pasó a `0xc01f2fe8` ni que `idt_cam` no se saltara por `CFG:skip`. (c) Con el montaje correcto de la partición 3 y la lectura fallida, falta saber si el fallo es del formato recomprimido (R36) o de otra causa.

## 12. Punto de parada en el arranque: §11 queda contradicho (03-11-2026)

Se reinició la cámara (batería fuera y dentro) y se conectó por SWD durante el arranque con un script que hace `halt` en cuanto el DAP responde y coloca puntos de parada hardware (la CPU se reanuda y la cámara termina en el mismo bucle de LED con −302).

| Intento | Parada temprana | Puntos de parada | Resultado |
|---|---|---|---|
| 1 | `pc = 0xc00310e0` (código de Loader2) | `0xc01f2f88` (lectura del fichero en `CFG`) | **No saltó en 30 s**; la cámara acabó en el bucle de LED (`pc = 0xc01f4f98`, comprobado después) |
| 2 | No capturado (el script se detuvo al pasarlo a segundo plano) | — | Sin datos |
| 3 | `pc = 0xc01f4fe0` (Loader3, ya tarde) | `0xc01f3b74` (LED), `0xc01f2fe8`, `0xc01f2f24` | Ninguno saltó: la CPU ya estaba en la fase de error |

**Comprobación del mecanismo (MEDIDO):** un punto de parada hardware en `0xc01f4f96` (dentro del bucle de LED) saltó de inmediato; los puntos de parada funcionan.

**Consecuencia.** En el intento 1 la CPU pasó de Loader2 a Loader3 y terminó en el bucle de LED **sin ejecutar `0xc01f2f88`**, la lectura de ficheros de `CFG` (§11). Por tanto el −302 **no** procede, al menos en ese arranque, de esa lectura. §11 y la inferencia sobre `idt_cam.bin` quedan **sin respaldo**. Hay un matiz: el `halt` temprano pudo alterar la secuencia, aunque el estado final fue idéntico.

**Dónde puede estar el −302 (INFERENCIA débil):** `0xfffffed2` figura también en el módulo FAT (`0xc01f4148`, usado en seis puntos de `0xc01f3d90`–`0xc01f40ca`, junto a los literales `FAT_E:Failed to load partition table`, `error at reading PBR/FAT/Root Dir entry`). El log termina en `CFG:Set REG`, pero eso no prueba que el fallo esté en `CFG`.

**Pendiente:** llegar al punto de error (nuevo intento de captura con punto de parada en `0xc01f3b74` y la pila del llamador, o con puntos de parada en las funciones FAT). La captura depende de conectar antes de que Loader3 termine: una carrera que solo salió bien una vez de tres.

## 13. Corrección de §12: los puntos de parada puestos en Loader2 no sobreviven (03-11-2026)

En un cuarto intento la parada temprana cayó en Loader2 (`pc = 0xc00385cc`) y se colocó, entre otros, un punto de parada en la entrada de la función del LED (`0xc01f3b74`), que **se ejecuta en todo arranque que acaba en el patrón de LED**. No saltó en 30 s y la cámara volvió al bucle de LED. Por tanto los puntos de parada colocados durante Loader2 **no llegan a Loader3** (causa no determinada: reinicio o reprogramación de la lógica de depuración entre etapas, INFERENCIA).

**Consecuencia:** la evidencia de §12 (que `0xc01f2f88` no se ejecutó) **no es válida** y se retira. §11 vuelve a ser una hipótesis abierta, coherente con R13: solo P1 (`c01f2c98`, firma BOS) y P2 (`c01f2f24`, `CFG_E:Load file`) producen un −302 que llega al LED. P1 se descartó en §9 (la firma en RAM coincide). Queda P2 por confirmar.

**tLog en DDR (LEÍDO).** El log de Loader3 menciona `kLog[834e0000]` y `tLog[834c0000]`. `0x834c0000` contiene un registro `WCUN` con dos entradas de texto, `L: BOOT (VER 01.90)` y `L: load image`, y nada más; `0x834e0000` está vacío. No aporta el mensaje de error.

**Siguiente captura:** muestrear el PC hasta verlo en Loader3 y solo entonces colocar puntos de parada en `0xc01f2f24` (entrada de P2), `0xc01f2f9a` (retorno −302 de P2) y `0xc01f3b74` (LED).

## 14. Captura encadenada y análisis estático de `Init Pwr2nd` (03-11-2026, solo lectura)

**Captura (MEDIDO).** El halt se pidió desde el BootROM escribiendo `DBGDRCR` por el APB-AP (`pc = 0xc003021c`). Después se pusieron puntos de parada encadenados, armando las tres etapas siguientes del log en cada parada. Saltaron, en este orden:

1. entrada de Loader3 (`0xc01f0000`)
2. `Init BlkDev` (`0xc01f115c`)
3. `Init FAT` (`0xc01f1178`)
4. `Switch Bkup` (`0xc01f118e`)
5. `Init DbgLv` (`0xc01f11b0`)
6. `Init Pwr2nd` (`0xc01f11bc`)

Los tres siguientes no saltaron en 30 s: `Pwr bootmode` (`0xc01f0a1c`), `Del LOG` (`0xc01f0a36`) y `Clr kLog` (`0xc01f0ab8`).

Tras reanudar en `Init Pwr2nd`, OpenOCD perdió el APB-AP (`Could not initialize the APB-AP`), volvió a leer el DPIDR y después dio tiempos de espera en `DSCR` (`InstrCompl`). Entre la parada 1 y la 2 hubo otra pérdida breve del APB-AP, y esa vez los puntos de parada sí sobrevivieron.

**Recorrido estático hasta `Pwr bootmode` (LEÍDO, Loader3 en RAM).** El arranque usa `PowerIC: 7` y `BootMode: 11`.

| Paso | Función | Hardware que toca |
|---|---|---|
| `Init Pwr2nd` | `c01f5948`, que llama a `c01f64d0` `XPWR_OFF`, `c01f590a` ADC de batería, `c01f63f2` flags de tecla y `c01f4aa0` escritura en Bkup | Lee parámetros de Bkup, lee el ADC y el temporizador `f2403000`, escribe en la Bkup en RAM. `XPWR_OFF` solo lee el puerto y el bit y los imprime; no escribe en GPIO |
| Rst Bkup | `c01f21c6` | Bkup |
| Date type | `c01f3514` | Bkup |
| `read MISCREG` | `c01f4ef8` | Solo lee `f2915000` y `f2912b10` y los copia a Bkup |
| Comprobaciones BOM | `c01f1de6` | GPIO `f2910000`/`f2912000`, temporizador y `f2406000` |
| Despacho de BootMode | `c01f2156`, luego `c01f1234`, `c01f1312` y `c01f132e` | Comprobado: el modo 11 llega a `c01f09e4` |
| `OFF HotIC` | `c01f60c2` | Pulso de GPIO en `f2910000 + puerto·0x100`: `+0x48`, `+0x44` y `+0x48`, 20 µs cada uno. El puerto y el bit salen de Bkup (`0xf90387`/`0xf90388`), valor no leído |
| `Pwr bootmode` | `0xc01f0a1c` | — |

En todo Loader3 no hay ninguna instrucción `mcr p14`, es decir, ninguna escritura en los registros de depuración por coprocesador. Tampoco aparecen como literales direcciones de reinicio, de reloj ni del bloque de depuración en ese tramo.

**Conclusión.** El código de `Init Pwr2nd` no borra los puntos de parada (LEÍDO). La pérdida coincide con la caída del enlace de depuración (APB-AP y luego `DSCR`), no con un paso concreto del código.

Hay dos hipótesis, ninguna probada (INFERENCIA):
- **(a)** El pulso de `OFF HotIC` u otra acción externa reinicia el dominio de depuración o el SoC.
- **(b)** El tiempo acumulado con la CPU parada dispara un vigilante externo, el SysCon (`Init Sync`, `SYC REIO`), que reinicia el BIONZ.

**Siguiente captura:**
- Marcadores más finos entre `0xc01f11c6` (retorno de `Init Pwr2nd`) y `0xc01f0a1c` (en particular `0xc01f0a16`, antes de `OFF HotIC`, y `0xc01f612c`, después del pulso).
- Menos lecturas por parada.
- Si se pierde el enlace, muestrear `DBGPCSR` y `DBGDSCR` por el APB-AP sin parar la CPU.

Si la pérdida se adelanta al añadir paradas, apoya (b). Si cae siempre en el mismo punto del código, apoya (a).

