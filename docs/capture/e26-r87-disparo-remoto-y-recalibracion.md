# E26-R87 — Disparo remoto de los tres modos, fallo del Silent del 3.76 y recalibración (11-11-2026)

Continúa [R86](e26-r86-cfw-376-tres-modos-nivelados.md). Etiquetas: **MEDIDO** (cámara, disparos míos por WiFi `192.168.1.18`) · **VERIFICADO** (bytes/emulación).

## 1. App RemoteShutter v9/v9b
* `/mode?v=silent|efcs|mech|menu`: escribe antes de `takePicture` `+0x210` (EFCS, 1 = desactivado) y `+0x238` (Silent) del bloque vivo `0x43EDF684` y los restaura en el callback. Mecánico = (1,0), EFCS = (0,0), Silent = (1,1).
* **Reinicios (E26-R87-APPCRASH, MEDIDO):** dos, siempre tras `/fmt?v=raw`; con `rawjpeg` 80+ disparos sin fallo. Causa: formato solo RAW con la app (nunca usado antes). v9b rechaza `raw` y quita el forzado cada 20 ms de v9 (100 `fork` de la VM por segundo).
* `scripts/camera_tres_modos.py`: tripletas Silent/EFCS/Mecánico por velocidad, ARW por adb.
* EFCS forzado es efectivo: degradado vertical típico de EFCS a 1/2000 (on/off 1,26 → 0,53 por bandas), plano en mecánico.

## 2. El Silent del 3.76 nunca actuaba
Cueva de diagnóstico en RAM (`0x83FB7E00`, contador y valores en `0x83FB7EA0`): el gancho se ejecuta una vez por disparo, pero `cap+0x41d = 0` en el objeto de `0x438c828c` (`r4 = 0x9507f580`) mientras el ajuste vivo `+0x238 = 1`: el copiador de `patch_tristate` escribe en otro objeto. Con la condición sobre el byte vivo `0x43EDF8BC` el Tv leído es correcto (`0x1855` = 1/320, EXIF 1/320) y Silent pasa de 0,232 a 0,013 de media (×17 menos, de ≈ 54 ms a la velocidad pedida).

## 3. Recalibración del Silent (MEDIDO)
Con la constante de R56 reajustada (15,48 µs, 110 líneas) salía 1/250 → 0,73 y 1/500 → 0,40. Exposición efectiva frente a líneas pedidas (7 velocidades, ISO 100 y 800): **E = 17,135 µs·n + 564 µs** (residuo ±10 %). Nuevo `r5 = 4252 − T/17,135`; mínimo electrónico ≈ 0,58 ms (1 línea): 1/2000 y 1/4000 no pueden bajar de ahí (+0,5…+1,3 EV).
Validación en RAM con las constantes nuevas (ISO 800, `analysis`: `~/Desktop/16161111/r87e`):

| Velocidad | Silent / Mecánico | EFCS / Mecánico (tabla R86) |
|---|---|---|
| 1/1250 | 1,10 | 0,99 |
| 1/500 | 1,00 | 0,92 |
| 1/250 | 0,93 | 0,92 |
| 1/100 | 1,09 | 1,03 |
| 1/50 | 1,00 | 1,01 |

## 4. Tabla EFCS R87
Pérdidas con la tabla R86 (remotas) + puntos manuales R86: ≈ 1,0 ms (residuo ±190 µs) hasta x = 2030 µs (1/200) y 0 desde x = 4388 µs (1/125, on/off 1,00 con c ≈ 0). Modelo suavizado: 1001 µs constante y rampa a 0. Tabla `analysis/e26-r85/tabla-r87.json`: `[(2205, 1001), (2240, 1008), (2349, 899), (2457, 1116), (2609, 1008), (5220, 967), (7008, 582)]`; E/T previsto 0,974–1,03. Corrige el −8 % de R86 en 1/500–1/200.

## 5. CFW 3.77
3.75 + `patch_silent_r5` corregido (condición viva, E = 17,135·n + 564). `.dat` `analysis/gui/g22/pkg-377w/pkg-3.77/package-3.77/firmware_packed.dat`, sha256 `87e36b900eb2f02e1f4ea6ec40d77cfafbee395a1055d7ce7fb6195e1605d9fd`. `/usr` igual al 3.75; `av-cam` = `apply_bytes(3.75)`; emulación 1/500 → 4139, 1/250 → 4025, 1/60 → 3341, Silent off sin cambios; auditoría con el mismo perfil que el 3.74 instalado. Sin instalar.

## 6. Límites
* Silent ≥ 1/1600: exposición mínima ≈ 0,58 ms (sobreexpone). EFCS ≥ 1/1000: degradado vertical (R85).
* La cueva de diagnóstico sigue en RAM hasta reiniciar (escribe 24 B en `0x43FB7EA0`, zona libre del hueco).
