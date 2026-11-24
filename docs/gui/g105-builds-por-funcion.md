# G105 — Auditoría del CFW 3.92 tras «reinicio y no enciende» y una build por función sobre la base Silent (24-11-2026)

Incidente: con el CFW Film 3.92 recién instalado (PP-1), el usuario pulsó la tecla izquierda (asignada a «Brillo de monitor»); la cámara se reinició y no volvió a encender.
Petición posterior: una build por cada función añadida, todas sobre la base Silent y con el mismo número de versión, usando el re-flasheo de `pmca-re-reloaded`.

## 1. Auditoría del 3.92 instalado

**Lo instalado es lo construido (VERIFICADO).**
- `.dat` `d6291386…d344` = `build/cfw_film392/pkg-3.92/package-3.92/firmware_packed.dat`.
- Importado al arnés (`pkgdat/dat-3.92-6ce0a87a`): los 31 ficheros de su `/usr` son idénticos a `build/cfw_film392/files`.
- Con el código actual, `build_files(pp=True)` reproduce los 31 ficheros byte a byte.

**La vía de la tecla izquierda no falla en el arnés (MEDIDO).**
- Perfil `b392f`: `/usr` del 3.92 con el av-cam de fábrica, la misma NVRAM con «Func. botón izquierd. = Brillo de monitor».
- La tecla izquierda abre «Brillo de monitor» (vista de `viewUnified8.so`, que el CFW no toca). Se ajusta, se confirma y se cancela sin cuelgue.
- Solo escribe la NVRAM `0x1070939` (4 B). A av-cam le llegan `0x4049`, `0x4043` y `0x405c`, las mismas órdenes que en el arranque.
- Con el av-cam del 3.92 (perfil `brillo392`), el arnés arrancó en el estado inhibido ya conocido (G104 §8.5: solo «P», teclas sin efecto), así que la cadena con ese núcleo no se pudo ejercitar.

**Estático: nada del 3.92 toca la vía de brillo (VERIFICADO en bytes).**
- `CautionConfig.so`: las 13 relocaciones cambiadas son las 12 listas Fn y la de la rueda. Los símbolos cambiados son los 3 de Silent. Los nodos de brillo y de teclas personalizadas no cambian.
- `viewUnified2.so`: los tramos cambiados son las 12 tablas Fn, la rueda, `WrapperIso` y los segmentos nuevos. `viewUnified4.so`: despachador Fn y vista ISO. `viewUnified7.so`: cueva de la rueda.
- `image_cmn_169.uxc`: 18 registros nuevos (formato `0xe0` de la A7S). Se reubican los 5 947 desplazamientos `0xc0`; los 90 `0xc8` no apuntan a datos. Ningún `.so` referencia los ids nuevos salvo la tabla ISO.
- Núcleo (`av-cam`), por capas reconstruidas: PP 640 tramos (33 887 B, hueco G18), Film 63 tramos (`ZONA_A` hasta `0x43be3dc4` + 7 ganchos), ISO 52 tramos (cueva `0x43be4310`, tabla EXIF en `ZONA_B` + 3 ganchos). No se solapan entre sí ni con las celdas de Film (`ZONA_A[0]…+0x10`).
- Gancho ISO→Sv `0x43b074f2`: la función guarda `lr` (`push {r3,lr}`) y `r1` se recarga justo después; la cueva es correcta.

**Estado de la cámara al auditar:**
- USB: la última conexión de la cámara fue a las 00:19:36. Después solo aparece la sonda SWD (otra placa, serie `E6698030DF5F7736`, conectada a las 00:26 y 00:31).
- SWD (una lectura, sin paradas): `cannot read IDR`. BIONZ sin alimentación, o los hilos no llegan.
- Batería: 49 % a las 22:54 del 23-11 (pruebas de carga USB). Después hubo instalación del oficial 3.91 y del 3.92 con la cámara encendida.

**Conclusión:**
- No se encontró defecto del CFW en la vía de la tecla.
- Causa del reinicio: NO_VERIFICADO. Lo que no se ha ejercitado es el núcleo del 3.92 en hardware: las capas PP del 3.81 (S-Log3, B&W, Hi-Light) y la ISO nunca corrieron en la cámara.
- Las builds por función de §2 sirven para aislarlo.

**Recuperación, por orden (sin escribir nada):**
1. Desconectar la sonda SWD del USB del PC: con lecturas SWD durante el encendido la cámara no arrancó en 5 ciclos el 17-11.
2. Quitar la batería ≥ 30 s.
3. Cargarla (cámara apagada con USB o cargador externo) y encender sin USB.
4. Si sigue sin encender: probar sin objetivo.
5. Si BIONZ no arranca: vía SWD de R48/R49, que fuerza el actualizador de fábrica en RAM y reinstala por USB.

## 2. Una build por función (`build_cfw_film.py --funciones`)

**Base común = Silent.**
- Menú Silent antes del EFCS, descriptor de tres estados con el EFCS en gris si Silent está activo, textos de la A6300.
- `libObj` con el eco de Silent.
- Núcleo 3.38 + tres estados + Silent calibrado (R87).
- Darwin v3, sin `nflasha5`.

**Funciones** (cada build = base + una):

| Build | Añade | `.dat` sha256 |
|---|---|---|
| `base` | nada (solo Silent) | `bb17e1c048be125b22b0a85aaf7cb84b8215d2e91153cd5c282f3fb63bd39e34` |
| `film` | carpeta Film Simulation, Film en el menú Fn y en la rueda (valor 9), hilo userland en `viewUnified2`, `film_patch` en el núcleo | `713d3009dfcf1f16dd6249e6561e85d3b0d8950314ef7bd91b4343ec557c228a` |
| `pp` | menú Picture Profile (una fila por ajuste), listas PP en el menú Fn y el selector en la rueda (valor 9), `libObj` con eco PP, núcleo PP del 3.81 | `979d46b2a8e70e639e0ca421dbb2aa285ad9aecfc139960f640a40b8785af271` |
| `exfine` | «Extra fine» en Calidad (4 B de `CautionConfig.so`) | `0e03ca9c7efe3e4ca4545982b44a9725f3059d913f3035fc633d6189a681ad19` |
| `iso` | pantalla ISO hasta 204800 (`viewUnified4`, `WrapperIso`, `libObj`, textos e iconos de la A7S), `iso_avcam_patch` en el núcleo | `64324e05700f65db2526e95389523c39618305f4df233cbac286b237b608ff1e` |

- **Ficheros:** `build/cfw_func393/<build>/pkg-3.93/package-3.93/firmware_packed.dat`. Registros en `build/cfw_func393-<build>.log` y `.audit.json`.
- **Comprobaciones:**
  - las cinco pasan la auditoría independiente `--darwin-v3 --sin-wbi --bionz-g22` con 31/31; el auditor reconoce ahora los núcleos por función;
  - `tests/test_g105_builds_por_funcion.py` (5): cada función toca solo sus ficheros y el núcleo suma solo sus capas;
  - regresión G101–G103: 23 verdes;
  - sin `--funciones`, la salida del 3.92 es idéntica (31/31).
- **Sin probar:** ninguna se ha arrancado en el arnés ni en la cámara.
- **Recomendación para aislar el fallo:** primero `base`, luego `exfine`, `film`, `iso` y `pp`. En cada una, repetir la tecla izquierda con «Brillo de monitor».

## 3. Mismo número de versión para todas: re-flasheo de `pmca-re-reloaded`

`pmca-console` 1.12.0 (instalado) trae `firmware --reflash`. Código revisado en `masterflai/pmca-re-reloaded`, `crates/pmca-app/src/firmware.rs`:
1. Lee la versión instalada y reescribe la versión declarada del FDAT a la instalada + 1, el mínimo que pasa el filtro del actualizador. Necesita la clave FDAT.
2. Flashea.
3. Por modo servicio escribe la versión real en `/setting/updater/dat4` (`[minor, major]`). Necesita las claves de servicio («Senser»). Si se corta, `--restore-version` o `--set-version` lo terminan.

Por eso las cinco builds van todas numeradas **3.93**:
- La primera (desde el 3.92 instalado) entra con una actualización normal.
- Las siguientes se cambian entre sí con `--reflash`, y la cámara vuelve a informar 3.93.

Uso (instalar exige autorización expresa en cada caso):

```
pmca-console firmware build/cfw_func393/base/pkg-3.93/package-3.93/firmware_packed.dat --flash --confirm
pmca-console firmware build/cfw_func393/film/pkg-3.93/package-3.93/firmware_packed.dat --flash --confirm --reflash
```

**Límites:**
- `--reflash` no se ha usado todavía en esta cámara.
- Si el paso 2 se corta, la cámara queda informando la versión subida hasta que se ejecute `--restore-version`.
- Nada de esto sirve mientras la cámara no encienda (§1).

## 4. Recuperación e instalación de la build `film` (24-11-2026, MEDIDO)

- **La cámara volvió a encender sola** (09:29, modo normal `07c4`, `pmca-console info` = 3.92), tras estar cargando apagada (`054c:0994`), sin SWD ni escritura alguna. El «no enciende» del incidente fue transitorio; su causa sigue NO_VERIFICADA (batería baja o bloqueo hasta corte de energía).
- **Actualización normal 3.92 → 3.93 (`film`) desde el sistema en marcha: no entra al actualizador.** Dos intentos: la cámara se reinicia y vuelve a modo normal (`07c4`), `pmca-console` agota la espera.
- **Actualizador forzado por SWD** (`analysis/e26-recovery/r48_updater_swd.cfg`, como R49 §7): `chk updater` dos veces con `r0` → 0, BootMode 3, entrada al actualizador en 405 ms; enumeró `054c:03e2`. Registro `analysis/camera-dumps/20261124-inc392-swd/p1.log`.
- **Instalación:** primer intento `device returned more data than requested`; el segundo, `updater response error`, y el canal quedó trabado (como R49 §8). Ciclo de energía con el interruptor → volvió sola al actualizador (`03e2`) → `Done`.
- **Verificado:** arranque normal (`07c4`), `pmca-console info` = **3.93**. Registro `install-3.93-film.log`.
- **Falta (cámara):** probar Film Simulation y la tecla izquierda «Brillo de monitor» con esta build.

## 5. Botones «pegados» con `film` e instalación de `exfine` por USB (24-11-2026, MEDIDO)

- **Con `film` 3.93** el usuario observó que los botones quedan «pegados» (p. ej. el obturador). Sin reproducir ni aislar: NO_VERIFICADO si viene de la capa Film o de la base Silent.
- **Claves de `pmca-console`:** `--reflash` falló con «key material … not set up». `keys import` solo acepta URL https o **ficheros** locales (no carpetas); se importaron desde los `.py` de `references/fwtool`, `references/pmca` y `~/.local/share/Sony-PMCA-RE` → las cuatro clases presentes.
- **Instalación `exfine` por USB, sin SWD:** `firmware … --flash --confirm --reflash` desde el CFW `film` en marcha → 3.93 → 3.94 declarada, entró al actualizador, `Done`. La restauración de versión agotó la espera del modo servicio; `firmware --restore-version` aparte la completó («real version again: 3.93»).
- **Verificado:** arranque normal (`07c4`), `pmca-console info` = **3.93**. Registro `analysis/camera-dumps/20261124-inc392-swd/install-3.93-exfine.log`.
- **Falta (cámara):** comprobar si los botones siguen pegados con `exfine` (base + Extra fine, sin Film): si no, el fallo es de Film.
