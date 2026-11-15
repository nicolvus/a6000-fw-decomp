# G63 — Anti-Flicker Shooting / Flicker Scan (15-11-2026)

Sin cámara, sin CFW construido, sin tocar `scripts/gui/harness/`. Código: `scripts/g63/flicker_scan_patch.py` (cueva), ajuste `flicker_scan` en `scripts/cfw_ajustes.py` (id `0x1070217`, pid `0xF0`, opciones Off/50 Hz/60 Hz), gancho `post` en `scripts/g22/patch_silent_r5.py`, test `tests/test_g63_flicker_scan.py` (Unicorn).

## 1. (a)/(b) Detector y fase: no existe en la A6000
- Cadenas `flicker`/`FLK`/`50Hz`/`60Hz` en `av-cam.bin` 3.21: solo `[ADF]…60Hz` (tiempos de CPU del audio, sin relación), `NTSC60HzCountDownTimer` y trozos binarios `FLK`; ninguna rutina de detección. Igual en el `av-cam` de la A7S y de la A6300.
- La A6300 sí tiene «Anti-flicker Shoot.» (`area_check_data.dat`: `STRID_FUNC_FLICKERLESS_SHOOTING*`; `Caution.odex`: `INH_FACTOR_ID_CAM_SET_FLICKERLESS_MODE_*`; `string_english.uxc`), pero en su `av-cam` tampoco hay cadenas del detector: solo la UI está nombrada. En la A6000 (`libObj.so`/`viewUnified2.so` 3.21) solo aparece `GEN_Icon::startFlicker` (parpadeo de iconos de UI).
- Conclusión: sin detector ni salida (frecuencia, fase, amplitud) en la A6000. Límite: es una búsqueda de cadenas más lo ya documentado (s135: 0 aciertos); no se decompiló el AE de `av-cam` buscando una medición por filas, así que una detección sin cadenas no queda descartada.

## 2. (c) Arranque de la captura: sin medir
Se localizó el único punto donde Silent fija la exposición (la cueva de `patch_silent_r5`, antes de `SetExposure`, `r5` en líneas de 17,135 µs). Insertar una espera de 0–10 ms con resolución < 1 ms exige conocer la fase (§1) y el jitter del disparo; el BULB/temporizador de g55 cuantiza en tramos de 33 ms y no se comprobó si la captura arranca alineada con el VD del sensor. Sin cámara no hay forma de medir latencia ni jitter: **no implementado**.

## 3. Flicker Scan (Silent): implementado
Con el ajuste en 50 Hz (P = 584 líneas = 10,0 ms) o 60 Hz (P = 486 = 8,33 ms), la cueva calcula las líneas n del Tv y, si n ≥ P, usa n = P·redondeo(n/P) (restas, sin `udiv`); luego `r5 = 4252 − n`. Con n < P (más rápido que 1/100 o 1/120) no se toca: las bandas no se pueden evitar con la sola velocidad. Off (o byte fuera de tabla) = Silent sin cambios.
- Cueva 192 B (cabe exacto en `0x43FB7E00…0x43FB7EC0`). Solo bytes del `av-cam` del `.dat`.
- Test (bytes originales: enganche y cueva a cero; Unicorn): 1/60 = 911 líneas → 1168 (50 Hz) o 972 (60 Hz); 1/250, 1/1000, 1/4000 sin cambio; Silent apagado sin tocar; Off idéntico a g38.
- Arnés (overlay y perfil propios `g63`, puerto 8763; qemu parado y perfil borrado): «Flicker Scan: Off» en Ajustes personalizados → CFW pág. 2, lista Off/50 Hz/60 Hz, elegido 50 Hz (`img/g63-flicker-scan-50hz.jpg`); `nvram.json` guarda `"1070217": "01"`. El arnés no ejecuta el consumidor de av-cam (solo la entrada de menú y el guardado).

## 4. Límites
- Sin medir en cámara: la ley E = 17,135 µs·n (R87) y que 584/486 líneas den 10,0/8,33 ms; un error de línea de 1 % descentra el múltiplo ≈ 0,1 ms por periodo y deja bandas residuales.
- El redondeo al más cercano cambia la exposición hasta ±P/2 (p. ej. 1/60 → 20 ms, +0,36 EV); el AE no lo sabe. Alternativa: redondear siempre hacia abajo.
- Solo Silent; con EFCS/mecánico el flicker lo fija la cortina.
