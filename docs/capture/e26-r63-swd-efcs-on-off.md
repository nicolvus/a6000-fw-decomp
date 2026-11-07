# E26-R63 — SWD del BIONZ con EFCS activado y desactivado; serie 1/500–1/125 (05-11-2026)

> **Corregido por [R66](e26-r66-bloques-darwin-en-nvram-1850000.md):** la prueba 8 (§6, `0x30102+0xc6`) no tocó Darwin, porque `0x30102` no es el bloque B. Las medidas por SWD de §1–§2 siguen vigentes.

Solo lectura (`analysis/e26-r59/bz_mon.py`, AP0, ~400 barridos/s), 3.37 oficial. Fotos `test images/DSC03555–03562` (M, f/7,1, ISO 5000). Log: `analysis/camera-dumps/20261105-r63-swd/mon_efcs_on_off.log`. Reconstrucción: `scripts/e26_r63/replay_swd.py`; medida: `scripts/e26_r63/medir_pares.py`.

Etiquetas: **MEDIDO** · **VERIFICADO** (código) · **INFERENCIA**.

## 1. Darwin sí recibe una marca de EFCS (MEDIDO; corrige R58 §7 y R62 §1)

| Disparo (hora log) | Foto (EXIF) | `pkt[1]` (`0x83ed4948+1`) | ID1 del sensor (`0x8401ca2e`) |
|---|---|---|---|
| 22:38:45 1/512, :52 1/256, :55 1/181, 22:39:01 1/128 | `03555–03558` EFCS On | **`0x02`** | `0xdc → 0xd4` |
| 22:39:22 1/128 (primer disparo tras cambiar el ajuste) | `03559` EFCS Off | `0x42` | `0xdc → 0xd4` |
| 22:39:27 1/181, :30 1/256, :33 1/512 | `03560–03562` EFCS Off | **`0x40`** | `0xcc → 0xc4` |

* El resto del paquete (Tv aparte) es igual: `pkt[0xa..b] = 0x0e53`, `pkt[0xd] = 0x40`. La duración `0x83eee76c` es la nominal en ambos modos.
* `03559` lleva EFCS Off en el EXIF pero el sensor se programó con el ID1 de EFCS (`d4`) y `pkt[1] = 0x42`: **el primer disparo tras cambiar el ajuste es mixto**. A 1/125 no se nota (no hay pérdida).
* Darwin (VERIFICADO): `S+0x31` (`pkt[1]`) se lee en ~30 sitios, por bits 0–1, 2–3 (`0x0c`), 4–5 (`0x30`), 6 y 7. Solo `0x196a2` prueba el bit 6: devuelve 1 si `S+0x31 & 3 == 0` **o** si el bit 6 está puesto. Con el tipo de mecanismo 1/2 (`&~3`), EFCS on (`0x02 → 0x00`) y EFCS off (`0x40`) dan lo mismo ahí y en `0x18d6e` (`r5 = 1`). **No se ha encontrado aún un consumidor de Darwin que trate distinto los dos modos.** Falta recorrer los usos del bit 7 (`lsls #0x18`) y de los campos `0x30`.

## 2. Los registros del sensor no dependen del Tv en la foto (MEDIDO)

En la foto, el bloque `0x8401c670–0x8401c7e8` (registros IMX210 de T032/T033) toma **los mismos valores a 1/512, 1/256, 1/181 y 1/128, y en ambos modos**. Lo que difiere entre modos en la región vigilada es solo ID1 (`d4`/`c4`, bit 4). La vista en directo sí cambia (`0x0a8b`/`0x0a01` en la pareja `c742/c746`).

* **INFERENCIA:** en la foto EFCS el reinicio electrónico no se programa con un valor dependiente de T en estos registros. Por tanto, el inicio lo fija un evento o retardo, y el cierre, Darwin con T + corrección. Encaja con que restar líneas a `sl` (R60) no cambiara la luz: `sl` no parece llegar al sensor en la foto. No se ha vigilado todo el banco de registros; otro bloque podría llevarlo.

## 3. Pérdida por franjas en esta serie (MEDIDO; luz sin control de parpadeo)

on/off global: 1/500 **0,38**; 1/250 **0,78**; 1/200 **0,86**; 1/125 **1,035**. Con k = 1,035 (1/125), δ global = 1,26 / 0,98 / 0,85 / 0 ms. A 1/500 δ crece de 1,09 (arriba) a 1,48 ms (abajo), como en R57. **δ no es constante: baja de forma gradual de 2 a 8 ms**, no en un escalón. La referencia mecánica pura no es estable (a 1/200, EFCS off/T vale 1,3–1,7 frente a 1/125): parpadeo o cambio de luz. Las cifras de 1/250 y 1/200 tienen error de ±0,2 ms o más.

## 4. Prueba 6, primer volcado (antes de quitar la batería)

`analysis/camera-dumps/20261105-r63-pre-bateria/` (3.37). BK4 `0x30100`: suma de la tabla 1615, `0x11 = 62`; `f2..f7` = `8809 f810 cf12`, que solo cambia en el contador.

**Resultado (05-11-2026, MEDIDO):** batería fuera ≥10 min. El EXIF de `DSC03563/03564` marca 00:00:12–23 del 2014-01-01, así que el reloj se reinició y el corte de alimentación fue total.

* Fotos a 1/500: `03563` EFCS Off, `03564` EFCS On. on/off = **0,338** (antes 0,381), con franjas 0,46 → 0,12 de arriba abajo. **Mismo síntoma.**
* Segundo volcado `20261105-r63-post-bateria/`. `0x30102` es idéntica. `0x30100` cambia en `0x11–0x2e`: la tabla vuelve a **suma 1400, `0x11 = 49`**, el nivel del 20-10 (1418, 49), cuando antes valía 1615/62.
* **Conclusión:** el reinicio completo de Darwin devuelve su tabla aprendida a los valores del estado sano, y el fallo sigue. **El estado de la SRAM de Darwin y la tabla `0x30100` quedan descartados como causa.**

## 5. Siguiente

* Recorrer en Darwin los consumidores de `S+0x31` bit 7 y `0x30`, y la ruta del primer disparo mixto.
* Prueba 6 (batería fuera).
* Repetir la serie con luz continua (o a la luz del día) para medir δ(T) sin parpadeo.

## 6. Prueba 8: `0x30102+0xc6` = +100 µs (05-11-2026, MEDIDO; revertida)

Escrita sobre el volcado de seguridad `20261105-r63-seguridad-pre-c6/` (variante SHA-256 `77558a94…ec94b`, 3 bytes; verificada en memoria y sincronizada). Reinicio y fotos `DSC03563 (1)`/`03564 (1)` (1/500) y `03565`/`03566` (1/1000), con ISO 5000 y f/7,1. La numeración y el reloj volvieron a empezar tras el reinicio, por eso los nombres repetidos.

| Caso | on/off global | Franjas (arriba → abajo) |
|---|---|---|
| 1/500 base (tras batería) | 0,338 | 0,46 … 0,12 |
| 1/500 +100 µs | 0,350 | 0,45 … 0,24 |
| 1/1000 +100 µs | −0,05 (negro) | ≈ 0 |

* **Sin efecto medible.** Ni EFCS activado gana luz ni cambia el patrón (+3,5 %, dentro del ruido; la luz de la escena bajó un 25 % entre series, pero el cociente on/off la compensa).
* Interpretación: o el término `s8[B+0xc6]` no entra en la ruta usada (por ejemplo, si `[S+0x48]` no cae en el rango que elige `+0xc6`), o el retardo `ip` (`0x1a738`) no gobierna el inicio de la exposición. A diferencia de `+0x88` (R61), no hay prueba de que llegue a Darwin.
* **Revertida** restaurando `backup_flash.bin` del volcado de seguridad (verificación en memoria correcta, sincronizado a flash).

## 7. Corrección: todo R63 se midió con la variante de R61 activa (MEDIDO, 05-11-2026 23:21)

`0x30102+0x88` vale **834 µs** (variante R61, +500) en `r63-pre-bateria`, `r63-post-bateria`, `r63-seguridad-pre-c6` y `r64-seguridad`. Vale **334** (original) en `post-restaura-30102` (21:59, memoria y flash). La restauración de R61 **no persistió**: tras un apagado normal, el valor volvió a 834.

* **INFERENCIA:** igual que `0x30100` (R58 §8), `0x30102` se reescribe al apagar desde una copia en RAM (del BIONZ `0x43e97970` o leída de Darwin). Restaurar el BK4 sin reiniciar no basta.
* Consecuencia: las series `03555–03566` de R63 (§1–§6: on/off, batería fuera, +0xc6) se hicieron con `+0x88` = 834. Las conclusiones cualitativas se mantienen: la marca `pkt[1]`, los registros del sensor sin Tv, el síntoma sin cambio con la batería fuera y la ausencia de efecto de `+0xc6`. Pero **no son la línea base original**.
* A 1/500, on/off con 834 (0,34–0,38) es casi igual que con 334 en R57 (0,343). Si `+0x88` actuara sobre ambos modos a 1/500 (resultado A de R64), cabría esperar ≈0,49. **No encaja con ninguno de A/B/C sin otra serie en la misma sesión.**
