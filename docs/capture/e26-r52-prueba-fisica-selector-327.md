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

Con `+0x210 = 1` el selector debía escribir 1 en `pkt[0x0e]` ([E25-24b §2.2](e25-24b-implementacion-selector.md)); salió 0. Darwin recibe 0 y la compuerta `0x4318` deja pasar el movimiento original.

## 5. Código del copiador (MEDIDO en `av-cam.integrated.bin`)

`0x43845f2e..0x43845f34`: `ldr r3,[r5]` → `ldr.w r2,[r3,#0x210]` → `str.w r2,[r4,#0x41c]`. No hay llamadas directas (`bl`/`blx`) a la función que lo contiene (`0x43844e80`), se invoca por puntero. En ese mismo cuerpo `sb` y `r4` son registros distintos (`mov sb,r2`; `r4=[sp+0x8c]`).

## 6. Hipótesis (INFERENCIA; no distinguidas)

1. **`sb` del constructor `0x43841070` no es el `r4` del copiador:** la cueva lee `[sb+0x41c]`, un objeto distinto de donde se guarda el EFCS.
2. **`cap+0x41c` se copia más tarde que el uso** (otro disparo, otra vía de captura).
3. **Otro `strb` posterior** pone `pkt[0x0e]` a 0 (el de `0x43841476` se anuló, pero puede haber otro).
4. El paquete vigilado no es el del disparo (improbable: `pkt[0]=0`, formato y tamaño coinciden con T022/T023).

## 7. Límites

* Darwin (`0x20003716`, cueva `0x4318`) no es legible por AP0 (error); la bandera de Darwin no se midió.
* No se localizó `cap` en la RAM: el contexto `0x83edf684` tiene los campos fuente a 0, así que no sirven de huella.
* No se probó el RAW ni el rango de velocidades.
* Solo lectura; nada escrito en la cámara. El cuelgue de flash de R51 §6 sigue presente (`loadavg` ~75).

## 8. Siguiente paso

Decidir entre (a) leer `[sb+0x41c]` del constructor con un punto de parada (halt, ya usado en R49), (b) corregir la cueva para leer el mismo objeto que el copiador, o (c) volver al 3.28 oficial. No instalar nada sin orden.
