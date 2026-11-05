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
