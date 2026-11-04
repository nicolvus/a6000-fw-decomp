# E26-R53 — Paquete 3.29: el selector lee el ajuste EFCS en vivo (offline, sin instalar)

Fecha: 04-11-2026. Continúa [R52](e26-r52-prueba-fisica-selector-327.md). Petición del usuario: probar una «compuerta pegajosa». Se eligió una variante que no toca Darwin (ver §1).

Etiquetas: **MEDIDO** · **INFERENCIA** · **NO VERIFICADO**.

## 1. Por qué no se parchea Darwin

R52 §6.1 demostró que el paquete de captura (`pkt[8]=0xa0`) sale de BIONZ con `pkt[0x0e]=1`, y que el paquete anterior (`pkt[8]=0`) lleva 0 aunque `+0x210=1`. **INFERENCIA:** `cap+0x41c` solo se rellena en la captura (`0x43845f34`), así que los demás mensajes `0x0c` llevan 0 y reescriben `S+0x3e` en Darwin antes de que la compuerta `0x4318` lo lea.

Hacer pegajosa la compuerta en Darwin no cabe: la tabla de vectores solo deja 2 B libres además de la cueva actual (14 B + literal), la «zona de NOP» de `0xdf06` (80 B) es una función llamada desde `0xdfbe`/`0xdfcc`, y no hay huecos de ceros dentro del código. Se cambia en su lugar el origen del dato en BIONZ.

## 2. Cambio (BIONZ, `patch_bionz.py`)

La cueva `0x43541800` lee el **ajuste EFCS en vivo** (`0x43edf684+0x210`, literal `0x43edf894`) en lugar de `[sb+0x41c]`:

```
0x43541804  ldr r2,[pc,#0xc]    ; antes: ldr.w r2,[sb,#0x41c] (4 B); ahora 2 + 2 B
0x43541806  ldr r2,[r2]
...
0x43541814  .word 0x43edf894    ; literal (4 B, alineado)
```

Mismo tamaño de código (20 B) más el literal: `CAVE_LEN = 24`, hasta `0x43541818` (la C3-B empieza en `0x43541840`, sin solape). Cada paquete `0x0c` lleva así el modo, sea o no de captura. C3-B sigue usando `cap+0x41c` (solo actúa en captura). Cambian 4 bytes más de BIONZ: 93 distintos respecto al original (antes 89) y 115 en total (antes 111).

## 3. Pruebas (MEDIDO, offline)

* Regresión escrita antes del cambio: `test_emu_bionz_lee_ajuste_en_vivo` (`cap+0x41c=0`, ajuste en vivo 0/1, ambas ramas) falló y pasa tras el parche.
* Tests `e25_24`, `e25_25`, `e25_26`, `e25_27` y `e26*` actualizados; la evidencia versionada (`analysis/e25-24..27/evidence.json`, `manifest.json`) regenerada.
* `verify_325c.py` generalizado (`--dat`, versiones 3.25/3.27/3.29; el 3.29 solo puede diferir del 3.25 previsto dentro de `av-cam` y lleva la cueva): **31/31** sobre el 3.29 (`analysis/e25-27/verify-329.json`) y **31/31** sobre el 3.27, es decir, el 3.29 pasa todo lo del 3.27 y una comprobación más.
* Incidente de proceso: al reconstruir los artefactos se sobrescribió el 3.25 original del bloqueo (`analysis/e25-27/artifacts`, no versionado), que fijan los tests históricos R16/R30/R39. Se regeneró desde su commit (`078ed42e`, mismo CRC y tamaño de `nflasha3`: `4125580340`, 11 572 480 B) y esos tests pasan.

## 4. Paquete

| Archivo (no versionado) | SHA-256 |
|---|---|
| `analysis/e25-27/artifacts-329/package-3.29/firmware_packed.dat` | `3e4834e0e0c4e38bcad913a6fb70f7293cf9bad67ebfc838e9a3b9dbb19c6a7d` |
| `…/firmware_packed.fdat` | `16fd349d6fa3cdb82d83618a1c49cc37a546b8408a08cb8ac8acc94ffd227cfd` |
| `av-cam.integrated.bin` | `55db4d4f5037b41909d1a33123276b5ffa0f328633d8e0153a79efd333a07f9e` |

Mismo contenido que el 3.25c (tar, `nflasha3` en forma de Sony, Darwin) salvo la cueva del selector; versión de cabecera 3.29 (mayor que el 3.27 instalado).

## 5. Qué se espera y qué no se sabe

* **Esperado (INFERENCIA):** con EFCS desactivado, cualquier paquete `0x0c` lleva `pkt[0x0e]=1`; Darwin retiene el 1 en `S+0x3e` y la compuerta `0x4318` suprime bobinas y motor.
* **Medida de comprobación en BIONZ (sin parar la cámara):** muestrear `0x83f91e40` (búfer enviado) y `0x83ed4956`; debe valer 1 también en mensajes sin captura.
* **NO VERIFICADO:** que Darwin conserve el 1 y que la compuerta actúe; que el RAW (C3-B) salga bien; el cuelgue de flash de R51 §6 sigue presente.
* Vuelta atrás: 3.28 oficial (R51 §4) o el 3.27 (R50).
* **No instalado:** requiere orden expresa del usuario.

## 6. Resultado en cámara (04-11-2026, MEDIDO): el cambio no arregla el obturador

Instalado con `pmca-console firmware -f` (3.27 → 3.29, `Done`; la cámara reporta 3.29). El usuario: el sonido sigue siendo de doble cortina («el fix no funciona»).

* Cueva cargada en RAM: `0x43541800 = 00232370 034a 1268 a273 0129 01d0 …`, literal `0x43edf894` en `0x43541814` (leído por SWD). El campo EFCS vale 1 con EFCS desactivado.
* Muestreo de `0x83ed4948` (búfer del constructor) y `0x83f91e32` (búfer enviado) con un disparo a 1/250 (`+0x210 = 1`):

| t | `pkt[8]` | `pkt[0x0e]` (búfer constructor) | `pkt[0x0e]` (búfer enviado) |
|---|---|---|---|
| 24 401 ms | `0xa0` (captura) | **1** | 0 |
| 24 403 ms (+2 ms) | `0x00` | **0** (`00 40 00 18 bd 13 …`, paquete en reposo) | 0 |

**Resultado:** el paquete de captura lleva 1, como en el 3.27. Dos milisegundos después el búfer vuelve al paquete en reposo con `pkt[0x0e] = 0`: **no lo escribe el constructor** (con el 3.29 cada paso por el constructor da 1), sino otra rutina que restaura el paquete por defecto. La causa supuesta en §1 (`cap+0x41c` sin rellenar en paquetes sin captura) **no explica el fallo**: queda descartada como causa única. El búfer enviado (`0x83f91e32`) no llega a verse en 1, así que no está demostrado que sea el que sale hacia Darwin.

**Sin resolver:** qué recibe Darwin y qué ve la compuerta `0x4318`. Sin leer `0x20003716` por SWD a Darwin (R52 §8, E24-02 §6: pines 11/12 de `CN4906`) o sin localizar la rutina que restaura el paquete, no se distingue. Vuelta atrás: 3.28 (R51) o 3.27 (R50).

## 7. Investigación posterior solo con la sonda de BIONZ (04-11-2026)

| Medida | Resultado | Fiabilidad |
|---|---|---|
| Muestreo AHB fino (~1 ms) de `0x83f91e32` y `0x83ed4948` en dos sesiones de 100–150 s | sin ningún cambio aunque el usuario disparó | **dudosa**: AP0 lee la DRAM sin pasar por las cachés de la CPU; lo que se ve depende de cuándo se expulsan las líneas |
| Breakpoint en el emisor del evento 1 (`0x436b8a50`, copia `payload+0x40` → `0x43f91e32`), en un disparo | `r0 = 0x43ed4948` (mismo búfer que el constructor). Vista de la CPU: `00 40 00 18 bd 13 00 00 00 00 53 0e 00 40 00 00 …` (`pkt[8]=0`, `pkt[0x0e]=0`); vista AHB al mismo tiempo: `pkt[8]=0xa0`, `pkt[0x0e]=1` | MEDIDO, pero no se sabe si esa llamada es anterior o posterior a la cueva en ese disparo |
| `0x4382fac8` (usado en R52 §6.1 como «rutina de envío») | es la conversión de tiempo a µs de E25-11 (`[cap+0x4da]`), no el envío | **corrige R52 §6.1**: aquella lectura no prueba lo que sale hacia Darwin |
| Darwin: llamadores de las compuertas | `0x20c74` (bobinas) es alcanzable desde la tarea de captura `0x1811a`; `0x1fe66` (motor) solo desde otras tareas. `S+0x30..0x47` se borra solo al empezar la tarea (`0x196fa`, llamada única desde `0x1815c`) | MEDIDO (estático) |
| Darwin: llamadores de `0x1b080` | 24 sitios; solo `0x20c78` y `0x1fe6c` pasan por la cueva `0x4318` (como en el 3.23 que sí silenció la cámara en T040) | MEDIDO (estático) |

**Incidentes:** cinco reinicios de la cámara por paradas que no se reanudaban (`resume` sin pasar el breakpoint, o `resume` que falla tras leer memoria por la CPU: el núcleo c2 quedaba parado y el bucle registraba la misma parada cientos de veces hasta que saltaba el vigilante). Dos OpenOCD huérfanos ocuparon la sonda y se cerraron con `kill -9` sin haber examinado los núcleos. **No repetir paradas con este script** sin resolver antes el `resume` en el núcleo de BIONZ (modo Supervisor, c2).

**Hipótesis vigente (INFERENCIA):** lo que el emisor del evento 1 copia hacia Darwin lleva `pkt[0x0e]=0`: o se envía antes de que la cueva escriba el 1, o algo lo restaura entre la cueva y el envío. No está demostrado el orden.
