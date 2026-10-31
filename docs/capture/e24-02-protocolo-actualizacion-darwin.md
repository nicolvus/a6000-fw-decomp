# E24-02 — Bootloader de Darwin, protocolo de actualización y recuperación sin la aplicación (27-10-2026)

Solo análisis estático y pruebas offline sobre archivos ya presentes en el repositorio. No se conectó, reinició ni modificó la cámara; no se flasheó nada ni se escribió NVRAM/NAND. Continúa [E24-01](e24-01-arranque-recuperacion.md) (commit `84511a69`): Darwin (IC5700, MB9AF004B, FM3) alimenta el BIONZ desde `darwin_core.bin` (`DD_ON1/2/3`).

Fuentes (SHA-256 en [§ Pruebas](#pruebas-reproducibles)): `darwin_core.bin` oficial 3.21 (y los de A7S 3.20 y A6300 2.01 para comparar), `ud_darwin_firmup.elf`, `ud_darwin_init.elf` y `ud_darwin_reboot.elf` del initrd de `nflasha1` (volcado del 20-10), manual de servicio L3 (págs. 23 y 38 del PDF = hojas 6-11 y 6-26) y manual de periféricos FM3.

## Respuestas de cierre

| | Pregunta | Respuesta | Qué significa |
|---|---|---|---|
| **A** | ¿Evidencia verificable de un bootloader independiente de la aplicación Darwin? | **SÍ (existencia)** | Hay código de arranque distinto de `darwin_core` en `0x0000–0x41ff`: el core se carga en `0x4200`, el FM3 arranca por el vector de `0x0` y el propio core salta a ese vector. Su contenido y su lógica **no** se han visto |
| **B** | ¿Permite reprogramar una aplicación defectuosa desde una interfaz accesible? | **NO (no demostrado)** | Se demuestra el protocolo del lado BIONZ y la entrada desde una aplicación que responde. Que el arranque acepte una actualización con la aplicación rota no consta. Hay una vía física (puerto de descarga de Darwin en el esquema), no de software, sin demostrar |
| **C** | ¿Está demostrado que el BIONZ entra al actualizador si `darwin_core` no funciona? | **NO (no demostrado; evidencia en contra)** | Sin la secuencia `DD_ON*` del core no hay alimentación del BIONZ (E24-01). Que el arranque de Darwin la haga por su cuenta es desconocido |

Ninguno de los NO es una imposibilidad demostrada: falta el binario del arranque (`0x0–0x41ff`).

## 1. El bootloader propio de Darwin (tareas 1 y 2)

| Hecho | Evidencia | Estado |
|---|---|---|
| `darwin_core.bin` (157 276 B) se carga en `0x4200`: vector SP `0x20002a00`, reinicio `0x45c9` | Bytes; tamaño = `darwin.sum` | VERIFICADO |
| El FM3 toma el vector de reinicio de `0x0`. Por tanto el primer código que ejecuta tras cualquier reinicio **no es** `darwin_core` | Manual FM3 («Reset vector fetch») | VERIFICADO (manual) |
| El estado `Upd` del core (`0x8da8`, entrada 5 de la tabla de estados `0x25b50`, rótulo « Upd main») desactiva las IRQ del NVIC, escribe en el buzón de SRAM `[0x20000706]=4`, `[0x20000707]=0` y llama a `0x45bc` con `r0=0`. `0x45bc` = `ldr r1,[r0]; msr msp,r1; ldr.w pc,[r0,#4]`: **carga SP y PC del vector de `0x0`**. Es el único llamador | Bytes y Capstone | VERIFICADO |
| El core lee ese buzón (`0x20000700`) en su inicio: valores 1, 2, 3 y 5 en `0x46ca`, `0x46fe`, `0x4750`, `0x4774`; con 5 marca el indicador `0x40` (`0x4f3c`). Imprime « Start Darwin :Boo=%d.%d/Core=%d.%d » con los bytes `[8..0xb]` del buzón | Bytes | VERIFICADO el uso; el significado de cada valor del buzón es INFERENCIA (1 = arranque normal, 4 = petición de actualización, 5 = actualización terminada) |
| `ud_darwin_firmup.elf` acepta **dos destinos** de actualización: `1` = `darwin_boo.bin` y `2` = `darwin_core.bin`, con versiones independientes («OLD version boo = %04x, core = %04x») | Código (`0x8f62`: `movs r2,#1`; `0x9034`: `movs r2,#2`) | VERIFICADO |
| Ningún paquete (A6000 3.21, A7S 3.20, A6300 2.01) incluye `darwin_boo.bin`: `0640_darwin` solo trae `darwin_core.bin` y `darwin.sum` solo lista el core | Árbol de archivos y `config.xml` | VERIFICADO |
| `darwin_core` **no contiene código de programación de flash**: ningún comando `0x1550/0xaa8` y la única referencia a FLASH_IF es una lectura de `+0x100` (espejo CRTRMM) en `0x50e0`. La reescritura de flash la hace, por tanto, otro código: el arranque (INFERENCIA fuerte) | Barrido Capstone de todo el core | VERIFICADO (ausencia en el core) |
| `darwin_boo` es la imagen `0x0000–0x41ff` (16,5 KiB). Sony no la distribuye en los paquetes conocidos: el arranque se actualizaría solo con un paquete que la incluyera | Tamaño de la región; ausencia en paquetes | INFERENCIA |

Un salto sin reinicio (no hay `SYSRESETREQ`) conserva SRAM y el estado de los GPIO; solo el buzón cambia. **NO_VERIFICADO**: si el arranque reconfigura los pines `DD_ON1/2/3` (si los pusiera a 0 mientras el BIONZ ejecuta el actualizador, el propio actualizador se quedaría sin alimentación, de modo que lo normal es que no los toque o los vuelva a subir: INFERENCIA débil).

## 2. Cómo entra Darwin en modo actualización (tarea 5)

El que decide es **la aplicación Darwin**, a petición del BIONZ; el arranque solo actúa después.

```mermaid
sequenceDiagram
  participant B as BIONZ (updater: ud_darwin_init / ud_darwin_firmup)
  participant C as darwin_core (tarea COM 0xece4 → InitCom 0x4bca)
  participant L as Arranque FM3 (0x0–0x41ff, sin binario)
  B->>C: trama 0x80 B  [0]=0x11 [1]=4   (cada 20 ms hasta éxito o límite)
  C->>C: estado=4 → InitCom sale (beq 0x4e0c) y publica el estado
  Note over C: la tabla de estados tiene «Upd» (entrada 5): INFERENCIA que el estado 4 conduce a ella
  C->>C: Upd main: IRQ off, [0x20000706]=4
  C->>L: msr msp,[0]; pc=[4]  (salto al vector de 0x0)
  C-->>B: respuesta [0]=0x10 [1]=4  (+ versiones boot/core)
  B->>L: 0x14  [4]=destino(1 boo, 2 core) [5..8]=tamaño LE
  L-->>B: [1]=5 «actualizando», [8..11]=desplazamiento pedido, [12]=longitud (0 = fin)
  B->>L: 0x15  [1..4]=desplazamiento [5]=longitud [6..]=datos (≤ 0x78)
  Note over B,L: se repite hasta que la longitud pedida es 0. Fin: reinicio por 0x11 estado 3 + GPIO XPWR_OFF
```

Lo que está verificado de cada paso:

| Paso | Evidencia | Estado |
|---|---|---|
| Trama: 0x80 B, CRC-16-CCITT (semilla `0xffff`, poli `0x1021`) sobre los primeros `0x7e` B, guardada en `[0x7e..0x7f]` LE; transferencia full-duplex con `CS` por GPIO (`UdtrGpioWrite` 0 → `ioctl` → 1) | `ud_darwin_firmup.elf` `0x8b28/0x8b60`; el core calcula el CRC con el CRC por hardware del FM3 (`0x40039000`, función `0xa1dc`) | VERIFICADO |
| Respuesta válida: `[0]=0x10` (`COM_ID_NOTIFY_REG`) y CRC correcto; `[1]` = estado (4 listo, 5 «actualizando») | `0x8bfa`, `0x8cc4`, `0x8d0a`; cadenas «COM_DWN_STAT_UPDATING» | VERIFICADO |
| `0x11`: el core guarda `[1]` como estado; si vale 4 sale del bucle de comunicación. El estado 3 lo envía `ud_darwin_reboot` (junto con `XPWR_OFF`); el 7 tiene un tratamiento propio (`0xc61c`, no identificado) | `darwin_core` `0x4d20–0x4d3e`; `ud_darwin_reboot.elf` `0x8d06–0x8d12` | VERIFICADO |
| El core despacha **solo** `0x11`, `0x12`, `0x13` y `0x16` en `InitCom`; `0x14` y `0x15` **no** están en el core: los atiende el arranque | Barrido de las comparaciones de `0x4bca–0x4ec0` | VERIFICADO (ausencia en el core); la atribución al arranque es INFERENCIA fuerte |
| `0x14`: `[4]` = destino y `[5..8]` = tamaño del fichero (u32 LE). `0x15`: `[1..4]` = desplazamiento (u32 LE), `[5]` = longitud, datos desde `[6]`, tomados del fichero ya leído en memoria | `0x8c68–0x8c86`, `0x8d32–0x8d56` | VERIFICADO |
| El **dispositivo** manda el ritmo: pide desplazamiento y longitud en cada respuesta (`rx[8..11]`, `rx[12]`); el programa termina cuando pide longitud 0 | `0x8d7a–0x8d98` | VERIFICADO |
| `ud_darwin_firmup` **no comprueba** el resultado de la escritura: devuelve 0 si el enlace funcionó. Un fallo → «NG» y LED `0x63` | `us_darwin_firm.sh`; ELF | VERIFICADO |
| Si el arranque verifica la imagen (CRC, versión, firma) | — | NO_VERIFICADO |

**Matiz a E24-01:** `ud_darwin_init.elf` no es un «ping» inocuo. La trama `0x11` con estado 4 que envía en **cada** arranque del actualizador (tipo de circuito de energía 7; `chkfirm.sh` define `DARWIN=7`) hace que la aplicación Darwin salte a su arranque. De ahí que el actualizador siga dependiendo del estado de la aplicación aunque ignore el resultado.

## 3. Requisitos de `ud_darwin_firmup.elf` (tarea 4)

| Requisito | Detalle | Estado |
|---|---|---|
| Entorno | Se ejecuta desde `us_darwin_firm.sh` dentro del actualizador (`config.xml`: tras `us_crc32sum.sh darwin file`), es decir, con el BIONZ ya alimentado y `nflasha1` arrancado | VERIFICADO |
| Enlace | `/dev/sioN` y GPIO `CS`: ids de Backup `0xf900d4`, `0xf900b1`, `0xf9006d` (los mismos que `ud_darwin_init`). Si el enlace falla (apertura, `ioctl`, CRC, `com_id`) sale con error | VERIFICADO |
| Ficheros | `darwin_boo.bin` (opcional: si no abre, el destino 1 se omite) y `darwin_core.bin`. Ambos deben llevar la cadena `VERM.mm` (1–3 dígitos, ≤255). Sin `darwin_boo.bin` el core se reescribe siempre; solo se omite con boo y core idénticos a los del dispositivo | VERIFICADO |
| Respuesta del dispositivo a `0x11/4` | `rx[4..5]` = versión del arranque y `rx[6..7]` = versión del core (se imprimen como «OLD version boo/core») | VERIFICADO el uso; que el core las rellene del buzón `0x20000708..b` es INFERENCIA |
| Límites de tiempo | Espera de la respuesta de estado acotada por un límite temporal (constante no extraída de `ud_darwin_firmup`; `ud_darwin_init` usa `29 999 999`); el bucle de bloques sigue mientras el dispositivo pida longitud ≠ 0 | VERIFICADO (estructura); unidad NO_VERIFICADA |
| Integridad exigida en Linux | CRC-32 de `darwin.sum` (comprobado antes por `us_crc32sum.sh`) y formato `VER`; CRC-16 del enlace | VERIFICADO |

## 4. Aplicación Darwin inválida, colgada o corrupta (tarea 6)

| Caso | Consecuencia | Estado |
|---|---|---|
| **Colgada con el arranque vivo.** El core arma el watchdog hardware (`0x40011000`, control con los bits 1 y 0 (reinicio e interrupción, por el patrón del registro) en `0xa500`) y lo alimenta en `0xa524`; además lleva un watchdog virtual por tarea (cadena « Virtual watchdog:detected dead lock ») | Un bloqueo acaba en reinicio, vuelve a ejecutarse el arranque y de nuevo la aplicación. Un bucle de reinicios es posible | VERIFICADO (el uso del watchdog); periodo y efecto real INFERENCIA |
| **Responde pero sin función mecánica** (como los parches de bobinas de T024) | Mientras `InitCom`, la tabla `0x28c6c` (`DD_ON*`) y el salto `Upd` estén intactos, la cámara arranca, el actualizador llega y `ud_darwin_firmup` reescribe el core. T024 lo ejercitó en un sentido (3.21 → 3.22) | VERIFICADO el camino; el sentido inverso (3.23) no se ha ejecutado |
| **Rota la secuencia de encendido** (`0x28c6c`, `0x51c0`) o el reinicio | Sin `DD_ON*` no hay BIONZ: sin actualizador ni pmca (E24-01) | INFERENCIA fuerte |
| **Rotos `InitCom` o `Upd main`** (`0x4bca`, `0x8da8`, `0x45bc`) | El BIONZ arranca pero `ud_darwin_init`/`firmup` no consiguen el estado 4: «NG», LED `0x63`; no hay reescritura. Sin otra vía por software | INFERENCIA fuerte |
| **Imagen inválida de raíz** (vector/reinicio ilegibles) | Depende de si el arranque la valida (no visto) y de qué hace entonces con la alimentación. Desconocido | NO_VERIFICADO |
| **Actualización interrumpida** (ventana de `ud_darwin_firmup`, núcleo parcialmente escrito) y se pierde el reinicio o la alimentación | Queda el arranque con una aplicación incompleta: el caso de la fila anterior. Es la ventana más peligrosa de cualquier FDAT de Darwin | INFERENCIA |

Zona de Darwin que un parche no debe tocar (todo lo que mantiene la vía de recuperación): reinicio `0x45c8/0x43fc`, init del buzón `0x4638`, `0x51c0` (GPIO), tabla `0x28c6c` y manejadores `0x1578d/0x157a9/0x157c5`, tarea COM `0xece4`, `InitCom` `0x4bca`, `Upd main` `0x8da8`, salto `0x45bc`, watchdog `0xa500/0xa524`, CRC `0xa1dc`.

## 5. Fallo mecánico con alimentación frente a fallo de arranque (tarea 8)

| Síntoma | Qué está vivo | Vía por software |
|---|---|---|
| Cortinas/rearme/bobinas mal, cámara arranca y entra en menú | Arranque, `darwin_core` (energía y `InitCom`), BIONZ, `nflasha1` | **Sí, por el camino oficial**: pmca → sistema normal → `up.sh user` → actualizador → `ud_darwin_firmup` (el mismo que usó T024). Necesita FDAT versión mayor que la instalada (recuperación 3.23 preparada) |
| La cámara arranca pero el menú/disparo no responde (bloqueo de Darwin) | BIONZ vivo; Darwin parcialmente | Probable (el actualizador no usa el mecanismo), pero depende de `InitCom`/`Upd` y de que la entrada desde pmca (batería vía Darwin) siga funcionando |
| La cámara no enciende (sin respuesta al botón, sin USB) | BIONZ sin alimentación; Darwin muerto o sin secuencia | **Ninguna demostrada**; solo acceso al puerto de descarga/debug del MCU (§ 7), que exige abrir la cámara |
| Darwin en arranque con aplicación incompleta | Arranque FM3 | Desconocido; ver § 4 |

## 6. Métodos documentados de recuperación independientes de la aplicación (tarea 7)

Sin suponer que existen. Lo que hay:

- **Manual de servicio L3 local** (54 págs.): sin procedimiento de escritura de firmware ni de recuperación (solo esquemas y piezas). VERIFICADO por búsqueda de texto.
- **Modo de escritura serie del FM3** (manual de periféricos local, cap. 1, «Mode»): MD1=0, MD0=1 durante el reinicio por `INITX` entra en «Serial Writer Mode» («see Flash Programming Manual», que **no** está en el repositorio). VERIFICADO el texto; el protocolo, el canal UART y las protecciones de flash NO_VERIFICADO.
- **Esquema (hojas 6-11 y 6-26): el MCU tiene un puerto de descarga cableado.** En IC5700: `MD0` (L10) y `INITX` (L7) salen a las redes `MD0_DWN` y `XDWN_RESET` (islas de prueba `CL5701`, `CL701`); `P21/SIN0` y `P22/SOT0` salen como `DWN_UART_RXD/TXD`; los pines JTAG/SWD `P00–P04` (`TRST/TCK/TDI/TMS/TDO`) salen como `*_DWN` (islas `CL703–CL707`). Todo converge en el conector `CN4906` de 16 contactos de SY-1028 (`BOOT_MODE_1`, `UART_RXD/TXD_DWN`, `NSRST`, `TDO`, `RTCK`, `TCK/SWCLK`, `TMS/SWDIO`, `TDI`, `NTRST`, `DEBUG_MODE`) marcado **XX = no montado**; `MD1` (`PE0/MD1`) va a masa. VERIFICADO (lectura del esquema, renderizado y coordenadas del texto); conexiones finas (p. ej. `MD0_DWN` a través de `R4927`, no montada) LEÍDAS SOBRE IMAGEN, a confirmar con la placa.
- Que el SWJ-DP esté activo tras un reinicio: por defecto sí (`SPSR`: `JTAGEN0B/1S` = 1, manual FM3); que Darwin lo desactive no se ha comprobado.
- Que la flash esté protegida contra lectura/escritura por estos medios: NO_VERIFICADO.
- **Software:** ninguno. No hay botón ni combinación en el actualizador; el BootROM del BIONZ («Musashi Loader1») solo corre si Darwin lo alimenta (E24-01).

## 7. Vía de acceso que no dependa del arranque normal del BIONZ (tarea 9)

Dos candidatas, ambas **de hardware** y **sin demostrar**:

1. **Escritura serie del FM3** por `MD0_DWN` + `XDWN_RESET` + `DWN_UART_RXD/TXD`: independiente de la aplicación y del BIONZ, si la flash no lo impide.
2. **SWD/JTAG** por las islas `CL703–CL707` / `CN4906`: permite leer y reescribir el arranque y el core si la protección lo permite.

Ninguna entra en el alcance autorizado (exigen abrir la cámara y herramientas). De software no hay ninguna.

## 8. Hallazgo lateral (no se persigue en E24-02)

`InitCom` acepta además `0x12`: escribe bloques de `0x78` B en la RAM `0x20000000 + desplazamiento` (desplazamiento múltiplo de `0x78`, longitud `[5] ≠ 0`, marca el bloque en un mapa de bits `0x20002a13`) y `0x13` (sin analizar) y `0x16`, que copia hasta `0x78` B a una dirección absoluta comprobada en `0x20000000–0x20004000`. Esa región de RAM incluye el byte de tipo de mecanismo `0x20000050+canal` cuyo emisor no se localizó en [darwin-via-actualizacion](darwin-via-actualizacion-2026-10-26.md). INFERENCIA: es una ruta candidata para los datos de ajuste («Sens:AdjCmd DwnCamera», `GET_DARWIN_PARAM_INFO` en `adjstctl.elf`/`libsencore.so`). No se ha buscado el emisor en el lado BIONZ.

## 9. Evidencia que falta y comprobaciones offline posibles (tarea 10)

| Falta | Comprobación offline posible |
|---|---|
| Binario del arranque (`0x0–0x41ff`) | Solo por hardware (volcado SWD/serie): no autorizado. Offline: buscar `darwin_boo.bin` en paquetes de otros modelos Sony con Darwin (no hay en el repositorio) |
| Transición del estado 4 de `InitCom` a la entrada `Upd` de la máquina de estados (mensaje publicado en `0xed12` → quién lo consume) | Rastrear la cola 0 (`0x452c/0x4530`) hasta la tabla `0x25b50` |
| Semántica de los valores 1/2/3/5 del buzón `0x20000706` y de los bytes `[8..0xb]` | Seguir `0x4638`, `0x46b2`, `0x4f02` y las lecturas del buzón |
| Estado de `DD_ON*` en el salto a `Upd` (si el arranque los conserva) | Revisar `0x5d70` (llamado 32 veces desde `Upd`) y el literal `0x42668000`; no concluyente sin el arranque |
| Estado 7 de `0x11` y comandos `0x12/0x13/0x16` | Desensamblar `0xc61c` y los manejadores; buscar el emisor en `libsencore.so`/`adjstctl.elf` |
| Validación de la imagen por el arranque (CRC/firma) | Solo con el binario del arranque. Indicio: T024 muestra que un core con CRC-32 recalculado se acepta |
| Frecuencia del watchdog y reinicio efectivo | Desensamblar `0xa4d0–0xa524` y el valor de recarga |
| Protección de flash / SWJ-DP desactivado por Darwin | Buscar escrituras en `SPSR` (`0x40033100`) y en el área de seguridad |
| Fichas de pines de `CN4906`, estado montado/no montado de `R4927/R4917` | Placa real (físico) o imagen de alta resolución del esquema |

## Pruebas reproducibles

`python -m pytest -q tests/test_e24_02_darwin_update.py` (11 pruebas; las que necesitan binarios locales se omiten si faltan; requiere `capstone`, `mtools`, `7z` y `pdftotext`). Comprueba: ausencia de `darwin_boo.bin` en los tres paquetes; mapa del core (`0x4200`, SP/reinicio, tamaño); el salto `0x45bc` con el buzón en 4 y su único llamador; la entrada `Upd` de la tabla de estados; el despacho de `InitCom` (`0x11/0x12/0x13/0x16`, sin `0x14/0x15`); ausencia de código de flash en el core; CRC por hardware y watchdog; las constantes de `ud_darwin_firmup` (CRC-16, `0x7e`, `0x80`, `0x14`, `0x15`, estados 5 y `0x10`, destinos 1 y 2, desplazamiento y longitud en la respuesta); `ud_darwin_reboot` con estado 3; el puerto de descarga en las hojas del esquema; el texto del manual FM3.

```bash
mcopy -s -n -i analysis/camera-dumps/nand-20261020/dev_nflasha1.bin ::boot OUT/ && 7z x -oOUT/ird OUT/boot/initrd.img
llvm-objdump -d --triple=thumbv7-linux-gnueabi OUT/ird/usr/bin/ud_darwin_firmup.elf     # main 0x8e08, bloque 0x8c40, CRC 0x8b28
pdftoppm -f 23 -l 23 -r 500 -png -x 2300 -y 3050 -W 1900 -H 1350 references/manuals/a6000_service_L3.pdf OUT/md0   # MD0/INITX
pdftoppm -f 38 -l 38 -r 400 -png -x 4700 -y 2450 -W 1100 -H 1000 references/manuals/a6000_service_L3.pdf OUT/cn4906  # CN4906
```

| Archivo | SHA-256 |
|---|---|
| `darwin_core.bin` A6000 3.21 | `5f2be06d9885d154e8e0df46a611d6830d29754b4353f6e82cecfe66dd6a0bf4` |
| `darwin_core.bin` A7S 3.20 | `241f5d311991e8b4e0246b2edab4039517cab55daf431d4ad21670a8866174cf` |
| `darwin_core.bin` A6300 2.01 | `6249d4b7f70d31c50048c85ca39e61c1872b547a26fd4b4ad0343ca9811433ac` |
| `initrd:/usr/bin/ud_darwin_firmup.elf` | `fc1df1b27c191b10971637a97f24e62ea59bccaace7251708aae1e17c9594881` |
| `initrd:/usr/bin/ud_darwin_reboot.elf` | `1982ffd8acef969f462ac29ec44e031ee92c88597936e70d5a0ee25da8192c19` |
| `a6000_service_L3.pdf` | `4ab1630bffdba4aff01fa5934b8a1f3fe4bb54f4fefd6a7c19192836bda31aa5` |
| `fm3_peripheral_main.pdf` | `88846b10fcdc7485bee09c08b673c370127dc998f5b39de8cf2e3557971d3c26` |

## Límites

El arranque propio de Darwin sigue sin binario: todo lo dicho de él es deducido de lo que lo llama (el core) y de lo que lo usa (`ud_darwin_firmup`). El enlace entre el estado 4 y `Upd main` se apoya en la presencia del estado y del salto, sin haber trazado el mensaje intermedio. Las conexiones del puerto de descarga se leyeron en el esquema; no se contrastaron con la placa ni con el Flash Programming Manual de Infineon. Una búsqueda web no halló la versión oficial de ese manual; no se descargó nada.
