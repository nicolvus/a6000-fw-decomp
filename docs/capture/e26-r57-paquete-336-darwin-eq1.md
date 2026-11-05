# E26-R57 — 3.36: la compuerta de Darwin solo cierra con `pkt[0x0e] == 1`

Fecha: 04-11-2026. Continúa [R56](e26-r56-paquete-333-envio-inline.md) §8. **Construido y verificado offline; NO instalado (requiere autorización expresa).**

Etiquetas: **MEDIDO** · **INFERENCIA** · **NO VERIFICADO**.

## 1. Por qué (INFERENCIA)

Con el 3.35 el mecánico (EFCS activado) sale negro desde 1/1000 y, con disparos a 1/2000, la cámara a veces se reinicia (`WDT:RSTREQ`, petición de reset de otro procesador). Con el disparador físico también sale negro. La auditoría de R56 §8 deja dos únicos cambios frente a Sony: BIONZ (40 B: `pkt[0x0e]` = ajuste EFCS en el envío y en el paquete de la foto) y Darwin (22 B: compuerta en `0x4318` que apaga bobinas y motor si `[0x20003716]` ≠ 0). La prueba en RAM con el código de Sony en BIONZ no sirvió (`pkt[0x0e]` = `0xff` ≠ 0 también cierra la compuerta). Hipótesis: a velocidades altas `cap+0x41c` (copiado sin normalizar) vale algo distinto de 0/1 y la compuerta apaga las bobinas. **NO VERIFICADO en cámara:** no se pudo leer `pkt[0x0e]` (la lectura SWD de `0x83f91e20` durante el disparo apagó la cámara y el reinicio borró el buffer).

## 2. Cambio

Solo Darwin (`patch_darwin.PATCHES_EQ1`, `build.py --eq1`): la cueva de `0x4318` pasa de 14 B a 16 B (los 16 B eran ceros de la tabla de vectores):

`ldr r2,=0x20003716; ldrb r2,[r2]; cmp r2,#1; bne +; movs r0,#0; bx lr; b.w 0x1b080`

Cierra (devuelve 0) solo con el flag == 1 (Electronic); cualquier otro valor ejecuta la ruta de Sony. Con 0/1 el comportamiento es el del 3.35. BIONZ no cambia respecto al 3.35.

## 3. Pruebas (offline)

* `tests/test_e26_r57_darwin_eq1.py` (7): emulación Unicorn de la cueva con flag 0, 1, 2, 0x80, 0xff (solo 1 cierra); el 3.35 cerraba con 0xff; parche reversible y limitado a sus sitios.
* `verify_325c.py` → `verify-336.json`: 36/36 (acepta 3.36; Darwin puede diferir del 3.25). Tests afectados: 81 en verde.
* Paquete `analysis/e25-27/artifacts-336/package-3.36/firmware_packed.dat` (`d45bf672dc1ab5bf…`, no versionado); `darwin_core` `121fd07ec5819e6c…`.

## 4. Pendiente

Instalar (con autorización) y probar mecánico a 1/2000 y 1/4000, y electrónico (que no regrese). Si sigue negro, la compuerta no es la causa y el siguiente candidato es el propio mecánico fuera del parche (comparar con el 3.32 oficial).

## 5. Resultado en cámara (04-11-2026, MEDIDO por el usuario) — cierra la hipótesis

* **3.36** (instalado y confirmado con `pmca-console info`): el mecánico (EFCS activado) sigue negro desde 1/1000. La compuerta de Darwin no era la causa.
* **3.37 = contenido oficial de Sony** (`build_326.py 0x37`, manifiesto `manifest-recuperacion-337.json`, 8/8; instalado 3.36 → 3.37): **EFCS desactivado → foto correcta con obturador mecánico completo; EFCS activado → foto negra entera.** Sin ningún parche nuestro. El fallo de «mecánico negro» del 3.35/3.36 era el modo **EFCS activado** de esta cámara, no el firmware modificado.
* Consecuencia: en el firmware de Sony, EFCS desactivado = obturador mecánico completo. En nuestro 3.35/3.38, EFCS desactivado = Electronic (`pkt[0x0e]=1`). La referencia correcta para igualar la exposición electrónica es **EFCS desactivado en el 3.37 (mecánico completo)**; las calibraciones de R56 §7 se hicieron contra EFCS activado (primera cortina electrónica), que puede diferir a velocidades altas.
* NO VERIFICADO: por qué EFCS activado sale negro en el firmware original (calibración perdida en la recuperación, hardware del sensor/Darwin o ajuste de fábrica); a qué velocidades.

## 6. 3.38 = contenido del 3.35 con versión superior

El actualizador solo acepta versiones mayores: tras el 3.37 hay que subir. `build.py --inline --version 3.38` → `analysis/e25-27/artifacts-338/package-3.38/firmware_packed.dat` (`3e77f0a1…`); `av-cam` y `darwin_core` idénticos a los del 3.35; `verify-338.json` 36/36. No instalado.

## 7. NVRAM: restauración completa del volcado «A» (04-11-2026) — NO arregla EFCS activado

* Comparación propiedad a propiedad (`senser_backup_compare.py`): volcado «A» (20-oct 18:48, fw 3.21, antes de las pruebas; `silent-nvram-20261020/1-base_flash.bin`, SHA-256 `db9e7324…`) frente al posterior a la recuperación (3-nov, fw 3.26): 16 102 propiedades, **58 distintas**, casi todas ajustes de usuario (`0x107…`) y contadores (`0x3c…`, disparos 3042 → 3361). Pérdidas con «A» ≠ fábrica y B = fábrica: `0x30100` (512 B, tabla decreciente de 56 B en «A», ceros después), `0xd50086`, `0x3c0373-75` y algunos `0x107…`. `0x30081`/`0x3012c` cambian (p. ej. `0x1600` → `0x1280`). Semántica de `0x3…` NO VERIFICADA.
* Volcado de seguridad previo (fw 3.37): `analysis/camera-dumps/20261104-nvram-337-previo/` (difiere 575 B del de 3.26).
* `senser_backup_restore.py` con «A» (cabecera no igual, como el 20-oct): verificación en memoria correcta y sincronizado a flash (`Done`).
* **Resultado (usuario, tras reiniciar): igual que antes** — EFCS activado negro desde 1/1000. El NVRAM (al menos lo restaurado de «A») **no es la causa**.
* Descartado hasta aquí: BIONZ `pkt[0x0e]` (§8 R56), compuerta de Darwin (§5), parches nuestros (3.37 oficial), NVRAM «A». Pendiente: modelo cuantitativo de la pérdida de exposición con EFCS activado (inferencia de ~1,2–2 ms constantes, R56/R57), hardware del obturador o datos de ajuste fuera del BK4.

## 8. Medida de la pérdida de exposición con EFCS activado (3.37 oficial, 04-11-2026, MEDIDO)

Serie del usuario con el 3.37: M, f/3,5, ISO 12800, escena fija; EFCS activado `DSC03482` (1/60) y `DSC03496–03503`; EFCS desactivado `DSC03505–03514` (1/60 … 1/1500). Media RAW sin negro; razón on/off normalizada por la de 1/60–1/125 (1,067, deriva de escena); pérdida δ = T·(1 − razón).

| Velocidad | T (ms) | on | off | razón | δ (ms) |
|---|---|---|---|---|---|
| 1/60 | 16,67 | 1950,2 | 1799,8 | 1,016 | −0,26 |
| 1/90 | 11,11 | 1331,7 | 1254,4 | 0,995 | 0,05 |
| 1/125 | 8,00 | 899,0 | 852,3 | 0,989 | 0,09 |
| 1/200 | 5,00 | 594,3 | 695,6 | 0,801 | 1,00 |
| 1/250 | 4,00 | 369,2 | 506,0 | 0,684 | 1,26 |
| 1/350 | 2,86 | 200,7 | 340,8 | 0,552 | 1,28 |
| 1/500 | 2,00 | 86,9 | 237,8 | 0,343 | 1,31 |
| 1/750 | 1,33 | 12,6 | 161,5 | 0,073 | 1,24 |
| 1/1000 | 1,00 | −6,3 | 113,4 | −0,052 | ≥ 1,05 |

* **Pérdida constante δ = 1,27 ± 0,03 ms** desde 1/250 hasta 1/750; **0 a 1/125 y más lentas**; 1,0 ms a 1/200 (transición). Con T ≤ δ no llega luz → negro (≥ 1/1000).
* **Gradiente vertical:** a 1/500 la razón on/off baja de 0,43 (arriba) a 0,22 (abajo) → δ ≈ 1,2 ms arriba y ≈ 1,6 ms abajo; a 1/750 de 0,16 a −0,19. **Sin gradiente horizontal** (columnas 0,34–0,40). La exposición con EFCS desactivado es lineal con T (tasa ≈ 110–125/ms), así que la referencia es buena.
* **INFERENCIA:** hay un desajuste de temporización entre el barrido electrónico de la primera cortina (sensor, BIONZ) y el disparo de la segunda cortina mecánica (Darwin): desfase ≈ 1,2 ms más deriva ≈ 0,4 ms a lo largo del cuadro (velocidad de barrido distinta). Coincide en orden de magnitud con la calibración electrónica de R56 §7 (línea 16,73 µs frente a 15,2 µs medidos antes y 97 filas ≈ 1,6 ms de desfase): podría ser la misma causa (tiempo de línea real del sensor distinto del que supone el firmware). NO VERIFICADO.
* Esto descarta una avería «de todo o nada»: el obturador mecánico y el barrido electrónico funcionan; falla su sincronización a T ≲ 5 ms.

## 9. Análisis estático del EFCS activado (primera pasada, 04-11-2026)

Fuentes: `av-cam.bin` 3.21 con Capstone + docs E24-05/E25-EFCS. Solo lectura, sin REA (no disponible en la sesión).

* **El paquete `0x0c` a Darwin no lleva el tiempo de exposición** (E24-05h-dependencias §3): `pkt[2..3]` = `0x1600` solo selecciona la variante de espera (≥ `0xb00`), `pkt[0xc]` el tipo, `pkt[1]`/`pkt[0xd]` clase y modo. Por tanto el instante de cierre de la segunda cortina no sale de ese paquete: lo gobiernan el aviso de fin (`0x0e` de Darwin) o el temporizador de host (`cap+0x74f`, en µs) y las listas de estados de Darwin. El NVRAM tampoco alimenta `pkt[2..3]` en el sentido de tiempo (la propiedad `0x30081` con `0x1600`/`0x1280` coincide numéricamente pero la variante de espera no cambia con ese valor: ≥ `0xb00` en ambos).
* **Productor nativo `0x4383fa40`** (186 B, desensamblado): convierte µs a líneas con `0x4382fac8`/`0x4382fa94` (15,2 µs/línea = 3891/256), calcula `sb` = líneas de exposición y `sl` = `r8 − sb` con `r8 = max([record+0x1c] + sb, [record+0x20]=VTS)`; escribe `record+0x64` (r5) = `sl`, `+0x68` = svd, `+0x6c/+0x6d` = 0. **No hay ninguna constante de latencia de cortina en la función**: el desplazamiento que perdería 1,27 ms tendría que venir de `[record+0x1c]` (o de Darwin / del hardware).
* Candidatos para la causa, por orden de comprobación: (1) escritores de `record+0x1c` (origen de ese desplazamiento; no localizados aquí); (2) tiempo de línea real del sensor frente a 15,2 µs (R56 §7 midió 16,73 µs en el modo electrónico); (3) latencia/recorrido de la cortina trasera en hardware.
* Pendiente (necesita REA o SWD en vivo): escritores de `record+0x1c` y su fuente; valores de `record+0x1c/+0x20/+0x64` en un disparo EFCS a 1/500 y 1/125 por SWD con la ventana de `cap` (el 3.38 permite hacerlo con telnet/adb; el 3.37 no).

## 10. Análisis estático con REA: origen del desplazamiento del plan de exposición (04-11-2026)

REA (demonio `session_daemon.py`, `av-cam.bin`, listo en ~8 min; decompilados con `batch_decompile`):

* `FUN_437f87ac(cap)` (único llamador de `0x43841070`, en `0x437f8816`): si `[global+0x24] == 1` llama al **planificador del modo EFCS** `0x43841070(cap+0x1198, cap+0x20, &cap+0x5c8, …)`; si no, al planificador normal `0x437b3b08`. La selección por ese global es el punto donde el firmware elige el camino «EFCS».
* `0x43841070` copia el **descriptor `cap+0x5c8`** (12 palabras) al registro de exposición: `record+0x18 ← desc[4]`, **`record+0x1c ← desc[5]` (`cap+0x5dc`)**, `record+0x20 ← desc[6]` (`cap+0x5e0` = VTS), etc. Es decir, `record+0x1c` (el desplazamiento reinicio→lectura que `0x4383fa40` usa como línea base de `r5`) **no se calcula: viene del descriptor de modo del sensor**.
* El mismo `0x43841070` lee bytes de **variables globales de ajuste** (`DAT_43841924…43841948`: pares alto/bajo que, si no son cero, **sobrescriben** `record+0x64/+0x68/+0x6a/+0x6e/+0x70/+0x72`) — ganchos de depuración/ajuste, cero en reposo (NO VERIFICADO su valor en esta unidad).
* Aún sin localizar: el escritor de `cap+0x5dc` (rellena el descriptor), y si su valor depende de la unidad (NVRAM/sensor) o solo del modo.
* Conclusión parcial: el código no resta ninguna latencia de cortina; el desplazamiento de 1,27 ms (+ gradiente) tendría que estar en `cap+0x5dc` o en el hardware. Con el 3.38 (telnet) se puede leer `cap` en un disparo EFCS y comparar `cap+0x5dc/+0x5e0` a 1/125 y 1/500.

## 11. Escritores de `cap+0x5dc` y corrección de la calibración electrónica (05-11-2026)

* **`cap+0x5dc` no es un dato por unidad.** Los ~12 inicializadores de modo del sensor (p. ej. `0x435496d8…0x43549706`, `0x4354fd16…0x4354fd30`) escriben el descriptor `cap+0x5c8…0x5dc` con **`cap+0x5dc = [cap+0x28]`** (o un valor de pila devuelto por la consulta de modo `0x4381c04c`) y `cap+0x5d8 = [cap+0x24]`: geometría del modo del sensor, igual en toda A6000. El firmware no lee NVRAM ni OTP para ese desplazamiento. **Por tanto el desfase de 1,27 ms con EFCS activado no sale de datos de esta unidad que el firmware use**; descartado también NVRAM como fuente → queda hardware (cortina trasera o reloj/lectura del sensor) o una variable global de ajuste no nula (`DAT_43841924…`, sin medir).
* **Corrección importante de R56 §7:** la calibración electrónica (línea 16,73 µs y 97 filas de desfase) se hizo contra una referencia **EFCS activado**, que pierde 1,27 ms a ≤ 1/250 (§8). A 1/250 la referencia estaba un 32 % baja, lo que sesga la pendiente. El 15,2 µs/línea del firmware (3891/256, verificado en T046 con la 3.23) puede ser correcto. **Hay que recalibrar contra EFCS desactivado del 3.37** (serie `DSC03505–03514`, ISO 12800, 1/60–1/1500) con una serie electrónica equivalente en el 3.38.

## 12. Comparación de la NAND: 20-oct (3.21, EFCS funcionaba según el usuario) frente a 5-nov (3.37) (05-11-2026, MEDIDO)

Volcado actual de solo lectura con `updater_nand_dump.py` (`SOLO_PARTICIONES=1`, `analysis/camera-dumps/nand-20261105/`, sin escrituras) comparado con `nand-20261020/`:

| Partición | Resultado | Lectura |
|---|---|---|
| `nflasha5`, `6`, `7`, `11`, `15`, `16` | **idénticas** | warm boot, rootfs, /usr, Android system: sin cambios |
| `nflasha1` (8 B), `18` (72 B), `23` (7 B) | contadores `0x019d → 0x0052`, `0x0197 → 0x004e` | contadores de borrado de página, sin significado funcional |
| `nflasha3` (22 bloques) | versión/sumas del 3.37 reetiquetado | esperado |
| `nflasha2` | `Backup.bin` actual = «A» con 1023 B distintos en el cuerpo (contadores/uso) | **la restauración del NVRAM persistió en flash** |
| `nflasha4` («MPR», base de datos de contenidos de `libmpr`: miniaturas/DCF) | datos reubicados | actividad normal de fotos; no es calibración |
| `nflasha10` (FAT16: `CONFIG~1.SPE`, `IMAGES`, `KIKILOG.DAT`, `H1`, `H2`, `T0.TXT`), `nflasha17` (/android/data) | datos de usuario/log | esperado |

* **Conclusión:** nada de lo que hay en la NAND explica la pérdida de 1,27 ms del EFCS activado. Con firmware, Darwin (reescrito en cada actualización), NVRAM y NAND iguales al estado de entonces, el cambio tiene que estar fuera de la NAND.
* **Candidatos restantes (NO VERIFICADOS):** (1) memoria no volátil propia de Darwin (el actualizador **reescribe `darwin_core` siempre** y el primer intento del 3.25 acabó en `0x1063`/«NG» de Darwin; los datos `[0x20000050+canal]` y `[0x200002c0+canal]` de la compuerta/tipo de mecanismo no se leen de la NAND); (2) hardware tocado al abrir la cámara para soldar la sonda SWD (cable plano del obturador, contactos de bobina); (3) OTP/fusibles del SoC o del sensor. Leer la flash de Darwin requiere acceso físico a `CN4906` (pines 11/12, R52 §8).
