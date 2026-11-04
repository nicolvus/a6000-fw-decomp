# E26-R55 — 3.31: la página cambiada de cada bloque TPZL va comprimida (LZ77 de Sony)

Fecha: 04-11-2026. Continúa [R51 §6.6](e26-r51-respaldo-clave-nflasha0-nvram-326.md) y [R54](e26-r54-paquete-330-envio-pkt0e.md). Offline; sin instalar.

Etiquetas: **MEDIDO** · **INFERENCIA** · **NO VERIFICADO**.

## 1. Causa

Leer `dnflasha3` sector 12 (bloque TPZL 0) cuelga el LZP de Linux; el bloque 48, también recompuesto, se lee bien (R51 §6.6, MEDIDO). Diferencia (MEDIDO): `_splice` guardaba la página cambiada **sin comprimir** (`0x0F`, 4100 B). En el bloque 0 la página 9 (cuevas del selector, del envío y C3-B) pasaba de 303 B a 4100 B y el bloque de 51 a **59 sectores**: cabecera + bloque 0 = 33 280 B > 32 KiB. El bloque 48 también lleva una página almacenada, pero no cambia de sectores (110). INFERENCIA: el LZP de Linux no admite que el bloque 0 (o la cabecera más el bloque 0) supere 32 KiB; Loader3 sí, y el modelo de R39 no lo modela.

## 2. Cambio

* `tpzl.encode_lz`: codificador del formato de Sony (`0xF0`, ventana 4095, longitudes 3–16/32/64, copias solapadas, grupos de 8 literales con flags 0, fin = índice 0 / distancia 0; repertorio comprobado contra los 5904 registros de `nflasha3`: 5851 LZ77 y 53 almacenados), con análisis óptimo (9 bits por literal, 17 por coincidencia).
* `_splice` elige el menor entre LZ77 y almacenado.
* `verify_325c.py`: comprobación nueva `cabecera_y_bloque_0_en_32_kib` (3.31).

## 3. Resultado (MEDIDO, offline)

| Bloque | Sony | 3.30 | 3.31 |
|---|---|---|---|
| 0 | 26 112 B (51 sect.) | 30 208 B (59) | 26 122 B usados → **52 sect.**; cabecera + bloque = 29 696 B |
| 48 | 110 sect. | 110 | 110 |
| 57 | 110 sect. | 112 | 110 |

La página 9 comprimida ocupa 410 B (294 B no nulos: código sin repeticiones; el análisis óptimo no gana nada). `verify-331.json` 33/33 (también 33/33 el 3.30); tests TPZL, constructor y emulación R39 (36) pasan. Paquete `analysis/e25-27/artifacts-331/package-3.31/firmware_packed.dat` (`e8c705e4…`, no versionado).

**NO VERIFICADO:** que el límite real sea 32 KiB (podría ser «no crecer de sectores»: el bloque 0 queda en 52 frente a 51) y que con esto adb no cuelgue. Prueba en cámara: `dd if=/dev/dnflasha3 skip=12 count=1` y activar adb.

## 4. En cámara (04-11-2026, MEDIDO): no lo arregla

Instalado 3.30 → 3.31 (`Done`; reporta 3.31). Sin adb, `dd if=/dev/dnflasha3 bs=512 skip=12 count=1` **no termina** en 15 s y el hilo `bdev_dnflasha` queda en `mumin_devif_wait_trans`: el mismo cuelgue que con el 3.30. La hipótesis del tamaño (§1) queda **descartada**: con el bloque 0 en 52 sectores y la cabecera + bloque 0 en 29 696 B el fallo sigue. Falta una línea base: si la lectura cuelga también con el contenido oficial de Sony (3.28), la causa no está en los parches; si no, está en el contenido del bloque 0 (no en su tamaño).
