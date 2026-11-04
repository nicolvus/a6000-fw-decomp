# E26-R52 — Primera prueba física del selector EFCS/Electronic en el 3.27: el modo no llega a Darwin

Fecha: 04-11-2026. Petición del usuario: comprobar por qué el obturador electrónico no funciona en el 3.27 instalado ([R51](e26-r51-respaldo-clave-nflasha0-nvram-326.md)). Sonda SWD (RP2040, AP0 = AHB-AP) en solo lectura, cámara en marcha y sin halt.

Etiquetas: **MEDIDO** · **INFERENCIA** · **NO VERIFICADO**.

## 1. Observación del usuario

Con EFCS desactivado la cámara se comporta como de fábrica; el sonido es el de doble cortina (**dicho por el usuario, no medido**).

## 2. Parches de BIONZ cargados (MEDIDO)

Direcciones físicas = virtuales + `0x40000000`.

| Sitio | Leído | Esperado (manifiesto) |
|---|---|---|
| `0x4384133e` | `00bf 00bf` (NOP, NOP) y `bl` a la cueva a partir de `0x43841342` | igual |
| `0x438c82fe` (enganche C3-B) | `79f4 9ffa` | `79f49ffa` |
| `0x43541800` (cueva del selector) | `00232370 d9f81c24 a27301 29 …` (movs/strb, `ldr.w r2,[sb,#0x41c]`, `strb r2,[r4,#0xe]`, cmp, beq, b.w, bx lr) | coincide con E25-24b |
| `0x43541840` (cueva C3-B) | código presente (`b502 d4f8 …`) | no comparada byte a byte |

## 3. Campo EFCS (MEDIDO)

`0x43edf684+0x210` (física `0x83edf894`) vale 0 con EFCS activado y **1 con EFCS desactivado**; `+0x238` (`0x83edf8bc`) vale 0. El selector de BIONZ recibe el cambio.

## 4. Paquete BIONZ→Darwin (MEDIDO)

Vigilancia de 70 s de la ventana `0x83f91e20..+0x110` (paquete de 22 B en `0x83f91e32`) con 3 fotos sueltas a 1/250 con EFCS desactivado y 3 con EFCS activado (la ventana cambió 3 veces):

| t | `+0x210` | `pkt[0x0e]` |
|---|---|---|
| 6 ms | 1 | **0** |
| 23,4 s | 1 | **0** |
| 37,8 s | 0 | 0 |

Con `+0x210 = 1` el selector debía escribir 1 en `pkt[0x0e]` ([E25-24b §2.2](e25-24b-implementacion-selector.md)); el búfer enviado quedó en 0. Se desconoce qué recibe Darwin en el instante del disparo (ver §6 y §7): la deducción «Darwin recibe 0» de la primera redacción no está probada.

## 5. Código del copiador (MEDIDO en `av-cam.integrated.bin`)

`0x43845f2e..0x43845f34`: `ldr r3,[r5]` → `ldr.w r2,[r3,#0x210]` → `str.w r2,[r4,#0x41c]`. No hay llamadas directas (`bl`/`blx`) a la función que lo contiene (`0x43844e80`), se invoca por puntero. En ese mismo cuerpo `sb` y `r4` son registros distintos (`mov sb,r2`; `r4=[sp+0x8c]`).

## 6. Medidas con halt y muestreo rápido (04-11-2026, MEDIDO)

Breakpoint de hardware en la cueva `0x43541800` en los 4 núcleos (OpenOCD, `cortex_a`, AP1) y, aparte, muestreo de AP0 cada ~0,7 ms sin parar la cámara.

| Medida | Resultado |
|---|---|
| Parada en la cueva durante un disparo con EFCS desactivado | `pc=0x43541800`, `r1=1` (rama `[sp+0x44]==1`), `r9 (sb)=0x43ea976c`, `r4=0x43ed4948`; `+0x210 = 1` |
| `[sb+0x41c]` tras el disparo | **1** (`0x83ea9b88`). `cap+0x41c` pasa a 1 unos 8 ms después de que `+0x210` pase a 1 (muestreo) |
| Watchpoint de escritura en `r4+0xe` (`0x43ed4956`) | Salta en `pc=0x43541808` con `r2=1`: la cueva **escribe 1** en `pkt[0x0e]` |
| Muestreo de `0x83ed4956` (búfer `r4`) y `0x83f91e40` (búfer enviado) en un disparo | `r4buf[0x0e]` = **1 durante una sola lectura (< ~1 ms) y vuelve a 0**; `sent[0x0e]` no llegó a verse en 1 |
| Parches en el constructor `0x43841070` | No hay más `strb [r4,#0xe]`; las únicas escrituras con base `r4` son `+0xa..+0xd` y `+0x12..+0x15` |

**Resultado:** la selección **sí funciona dentro de BIONZ**: `+0x210 → cap+0x41c → cueva → pkt[0x0e] = 1`. La hipótesis 1 de la versión previa de este informe (objeto distinto) queda **descartada**. El 1 dura menos de un milisegundo en el búfer del constructor y el búfer enviado queda en 0.

### 6.1 Breakpoint en la rutina de envío `0x4382fac8` (MEDIDO)

Breakpoint de hardware sin watchpoints; en cada parada se leyó el paquete por AP0 (`r4 + 0x40000000`, 22 B) y se reanudó. Dos paradas, ambas con `+0x210 = 1`:

| t | Paquete (22 B) | `pkt[0x0e]` |
|---|---|---|
| 22,7 s | `00 42 80 12 bd 13 00 00 00 00 53 0e 00 40 00 00 …` | **0** (`pkt[8]=0`) |
| 30,7 s | `00 42 80 12 bd 13 00 00 a0 00 53 0e 00 40 01 00 …` | **1** (`pkt[8]=0xa0`) |

**Resultado:** en el segundo paquete, el que lleva el comando de captura (`pkt[8]=0xa0`), BIONZ **sí entrega 1 en `pkt[0x0e]` a la rutina de envío**. El primero (sin `pkt[8]`) no es el disparo. El 0 persistente que se veía después es de un mensaje posterior. El lado BIONZ del selector está demostrado en hardware.

**Incidente (2.º reinicio):** tras la segunda parada, OpenOCD dio `DSCR_DTR_RX_FULL` / `Error waiting for InstrCompl` y la cámara se reinició otra vez, ahora sin watchpoint. Las paradas con leer-y-reanudar también son peligrosas en esta cámara (el halt se alarga por la lectura por AP0 desde el mismo DAP).

**Incidente:** el segundo intento (watchpoint además del breakpoint) dejó el núcleo parado más de 6 s y la cámara se **reinició** (`DSCR` con errores). No repetir con watchpoints.

## 7. Hipótesis restantes (INFERENCIA; sin distinguir)

1. Darwin recibe el 1 (medido en el envío) y un mensaje `0x0c` posterior, sin `pkt[8]`, reescribe `S+0x3e` con 0 antes de que la compuerta `0x4318` se evalúe (INFERENCIA más probable).
2. El búfer `0x83f91e32` no es el que sale por el transporte en este camino, y la copia a Darwin ocurre antes de la cueva o no pasa por ella.
3. Darwin recibe 1 pero la compuerta no actúa (por ejemplo, otro consumidor del tipo de bobina).

## 8. Límites

* Darwin (`0x20003716`, cueva `0x4318`) no es legible por AP0: no se midió lo que recibe ni la compuerta.
* No se localizó quién pone a 0 el byte tras la cueva.
* No se probó el RAW ni el rango de velocidades. Solo se detectó un disparo en el muestreo de 60 s con 3 fotos.
* El cuelgue de flash de R51 §6 sigue presente (`loadavg` ~75).

## 9. Siguiente paso

El fallo está en Darwin o entre el envío y la compuerta. Sin una lectura de la SRAM de Darwin (`0x20003716`) no se puede distinguir. Diseño posible, solo offline y sin instalar: hacer la compuerta de Darwin *pegajosa* (que `pkt[0x0e]==1` fije la bandera hasta el siguiente `pkt[0x0e]==0` con `pkt[8]!=0`). No instalar nada sin orden.
