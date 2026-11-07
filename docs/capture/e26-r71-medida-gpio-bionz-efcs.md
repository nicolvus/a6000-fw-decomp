# E26-R71 — Medida en cámara de los GPIO del BIONZ durante el disparo, con EFCS activado y desactivado (07-11-2026, solo lectura)

Ejecuta E26-R66-RESET ([R69](e26-r69-revision-informes-efcs.md) §4) con autorización del usuario. Firmware oficial 3.37. Sonda SWD del BIONZ (Debugprobe `E6698030DF5B3936`, DPIDR `0x3ba02477`). `analysis/e26-r59/bz_mon.py` lee el registro de entrada (`+0x10`) de los bancos GPIO `0xf2910000 + 0x100·n`. Solo lectura de MMIO por AHB-AP, sin detener la CPU. Disparó el usuario a mano; la cámara no estaba en la red.

Registros: `analysis/e26-r71/bz_gpio_1019.log.gz` (8 bancos, 140 barridos/s ≈ 7 ms) y `bz_gpio_rapido_1023.log.gz` (bancos 0 y 7, 573 barridos/s ≈ 1,7 ms).

Etiquetas: **MEDIDO** · **INFERENCIA**.

## 1. Tanda 1: 8 bancos, 3 + 3 + 3 + 3 disparos (MEDIDO)

* Hay bits que cambian solos en reposo, sin relación con los disparos: `b0.20`, `b0.29`, `b3.12`, `b5.22` y `b5.28`. Se descartan como ruido.
* Los 12 disparos dan el mismo patrón, y ningún otro bit de los 8 bancos lo acompaña:
  * `b0.21`, `b1.29` y `b3.9` hacen una envolvente de 140 a 220 ms;
  * `b7.23` y `b0.8` hacen un pulso;
  * `b7.21` hace un pulso de ≈ 66 ms.
* Con EFCS desactivado, `b7.23` sube unos 70 ms antes que `b0.8`. Con EFCS activado suben a la vez. Es el paso mecánico de cerrar la primera cortina antes de exponer, y confirma qué tanda es cada modo.

## 2. Tanda 2: bancos 0 y 7, 10 + 10 + 10 disparos (MEDIDO; media ± error típico, ms)

| | `b7.23` ancho | `b0.8` ancho | `b7.23↑ → b0.8↑` | `b0.8↓ → b7.21↑` | `b7.21` ancho |
|---|---|---|---|---|---|
| EFCS activado, 1/1000 | 16,6 ± 0,2 | 15,7 ± 0,4 | 0,0 ± 0,3 | 0,1 ± 0,3 | 66,9 ± 0,3 |
| EFCS activado, 1/125 | 22,1 ± 0,2 | 19,9 ± 0,2 | 0,9 ± 0,2 | 0,0 ± 0,4 | 66,9 ± 0,3 |
| EFCS desactivado, 1/1000 | 87,9 ± 0,3 | 15,9 ± 0,2 | 70,5 ± 0,4 | 0,8 ± 0,3 | 66,3 ± 0,3 |

## 3. Lectura

* **`b7.21` es la lectura del sensor (INFERENCIA fuerte).** Dura 66–67 ms en todos los casos, aproximadamente 1/15 s, y empieza exactamente cuando baja `b0.8`.
* **`b0.8` acaba cuando acaba la exposición, y ese final sigue al evento B de Darwin (INFERENCIA fuerte).**
  * De 1/1000 a 1/125, con EFCS activado, `b0.8` se alarga 4,2 ± 0,5 ms.
  * Darwin retrasa B (la suelta de la segunda cortina) 0 µs a 1/1000 (rama corta) y 4572 µs a 1/125 (rama larga) (R66 §3), una diferencia de 4,57 ms.
  * Las dos cifras coinciden, así que el BIONZ arranca la lectura un tiempo fijo después de B.
* **Con EFCS activado y desactivado a 1/1000, el BIONZ hace lo mismo:** `b0.8` dura 15,7 frente a 15,9 ms y la lectura arranca igual. La diferencia entre modos está solo antes de exponer (`b7.23`, los 70 ms del cierre mecánico).
* **P4C no se identifica.**
  * Si fuera `b7.23` con la polaridad directa (sube en la preparación y baja en A), a 1/1000 debería ser 2,4 ms *más largo* que a 1/125, porque A se retrasa 2401 µs. Se mide 5,5 ms más corto: con la polaridad directa no es P4C.
  * Con la polaridad invertida (baja en A y vuelve a subir en el rearme de R70 §2, que espera a que acabe la exposición), el pulso encajaría con lo medido. No se puede decidir.
  * Ningún otro bit de los 8 bancos tiene un flanco donde caería A, unos 2,4 ms después del inicio a 1/1000. O P4C entra por un banco que no estaba en la medida, o es `b7.23` invertido, o su pulso es más corto que el periodo de muestreo.
* **Sobre el fallo físico:** en todos los disparos con EFCS activado llegan al BIONZ las señales del mecanismo y del sensor, y la exposición termina donde dice Darwin. No hay indicio de una línea muerta, pero tampoco está probado que P4C llegue.

## 4. Estado y siguiente paso

* **E26-R66-RESET: PARCIAL.**
  * Medido: el final de la exposición en el BIONZ sigue a B, y a 1/1000 el BIONZ hace lo mismo con EFCS activado y desactivado.
  * Falta: identificar P4C y medir cuándo arranca el reinicio electrónico respecto a A.
* Decisivo, en este orden:
  1. Confirmar si en estas tandas las fotos a 1/1000 con EFCS activado salieron negras.
  2. Analizador lógico (≥ 1 MHz) en P4C (CN4900) junto con `b7.23` y `b0.8`: identifica P4C y mide el retardo de 1,27 ms.
  3. Sin analizador: continuidad P4C ↔ AA13/AD21 con la cámara apagada.
* E26-R49-SONDA sigue esperando: hace falta la sonda para repetir con el analizador.
