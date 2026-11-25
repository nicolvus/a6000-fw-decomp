# G111 — Film 3.94: receta aplicada por la GUI, grises con un look o un PP, e iconos propios en el menú Fn (24-11-2026)

Implementa FILM-9 y FILM-10 (diagnóstico en [G110](g110-film-receta-wb-no-aplica.md)) y, a petición del usuario, iconos propios para Film y el selector PP
en el menú Fn. Build `pp + film + exfine` (la mezcla `sin_iso`) con el arreglo de Extra fine de `dad3c8f2`.
Código: `scripts/lut/userland/films.c` (`films_antes`, `films_gris`, trampolines), `scripts/lut/film_userland.py` (`VU2`, `receta_gui`, `patch_vu2`),
`scripts/gui/uxc_imagenes.py`, `scripts/gui/iconos_film.py` + `scripts/gui/iconos/`, `build_pp_menu.ICONOS`, `build_cfw_film.iconos_fn/pids_film`.
Tests: `tests/test_g111_film_gui.py` (4, Unicorn) y `tests/test_g97_films.py` adaptado.

## 1. Receta en el hilo de la GUI (FILM-9)
- **Dónde:** gancho en `CmnViewProcessDataMgr::setValue(pid, valor)` de la copia de vu2 (`0x1b460e`; nombre y vtable comprobados en el gestor con
  símbolos `cmn_view_processDataMgr.so`). Es la función por la que el menú, la franja Fn y la rueda guardan cualquier valor. El trampolín llama a
  `films_antes(gestor, pid, valor)` **antes** del `setValue` original, así que el hilo de Film, que lee la fila después, ya encuentra la copia en el blob.
- **Qué hace al elegir un look** (pid de una fila de Film o de la lista única):
  1. si no hay copia del usuario, la guarda en el blob (`OFF_REC`, `struct copia`): balance con `WrapperWhiteBalance::getWhiteBalance(…, 0)` (el actual),
     estilo/contraste/saturación/nitidez de sus ids de Backup actuales (los de RecipeLab), DRO con `WrapperDroHdr::getDroHdr(…, 0)`, índice del selector PP;
  2. pone la receta con los mismos setters que la GUI:
     - `WrapperWhiteBalance::setWhiteBalance(vbp, modo, K, A-B, G-M)`: modo 1 = AWB, `0xc` = temperatura (tablas de ranuras del propio wrapper); el
       wrapper ya invierte G-M al guardarlo, como RecipeLab;
     - `WrapperCreativeStyle::setCreativeStyle(vbp, estilo, 0, contraste, saturación, nitidez)`, igual que la llama el menú Fn (`0x19b104`); estilo del
       Backup → enum por las tablas de ranuras por estilo (`1,2,11,12,13,3,4…`);
     - DRO por su conversor (`0x19177c`) + `setValue(0x18, …)`: `setDroHdr` no sirve con DRO en gris (su `isInhOn` consulta `isGrayedOut(0x18)`);
     - selector PP a Off (`setValue(pid PP, 0)`).
- **Al volver a Off:** devuelve la copia por los mismos setters y la borra. **EV ya no se toca** (exposición libre, G110 §4 ter).
- **El hilo de Film** ya no escribe ajustes nativos; al reescribir el blob conserva la copia (`OFF_REC`).

## 2. Grises (FILM-10)
Gancho en `isGrayedOut(pid)` (`0x1b4696`), encadenado delante del gris de EFCS con Silent (G30): `films_gris` decide o deja seguir la cadena.
- Con un look activo: DRO/HDR (`0x18`), Estilo creativo (`0x19`), Efecto de imagen (`0x1a`) y todos los pids del Picture Profile; Balance (`0x17`) solo en
  los looks con kelvin fijo. Pids nativos sacados del factory de elementos (`CmnViewElementFactory::factoryElement`) con sus nombres.
- Con un PP distinto de Off: las filas de Film y la lista única.
- No hecho: poner el Efecto de imagen en Off al elegir un look (solo queda en gris); su dominio de valores no está verificado.

## 3. Iconos propios (`image_cmn_169.uxc`)
- **Formato descifrado** (G104 lo daba por desconocido):
  - datos en `base + 4·t + 4 + desplazamiento` (relativo al propio registro; G104 lo tomaba relativo a `base + 4` y solo acertaba con la primera imagen:
    por eso sus iconos ISO no salían);
  - registros LZPT (`0xF0`/`0x0F`) que descomprime el LDEC por hardware (`/dev/ldec`, ya emulado en el arnés);
  - salida RGBA4444: formato `0xc0` en filas de ancho redondeado a 16 (las 5 947 de `image_cmn_169`), formato `0xe0` en mosaico Morton 8×8 (las 38 de
    `image_Fn_Menu_169`). Verificado decodificando todas.
- **Iconos:** 39 de Film (Off + 38: marco de película con la abreviatura) y 11 del selector PP (PP OFF, PP1…PP10), 70×35 como «Std.» (`0xc7a6`), blancos
  con contorno oscuro. Codificados con `tpzl.encode_lz` en registros de 4096 B (el formato que acepta el LDEC) y añadidos en ranuras que ninguna biblioteca
  referencia.
- **Enlace:** propiedades `1` y `4` de cada opción del nodo (las que lleva cada opción del Estilo creativo nativo).

## 4. Build 3.94 (`build/cfw_func394/sin_iso`)
`build_cfw_film.py build/cfw_func394/sin_iso --version 3.94 --funciones pp,film,exfine`:
- `.dat` sha256 `2e21cf7b60b65ae6a88d0828581498b9d0495d349a61aad050fb54ce0e7f2f44`;
- `audit_package_nflasha15 --darwin-v3 --sin-wbi --bionz-g22` = `todo_ok` (0 violaciones LDEC, sumas 65/65);
- lleva `libmprctrl.so` con el arreglo de Extra fine de `dad3c8f2`. Sin instalar.

## 5. Arnés
Perfil `analysis/gui/g22/harness/live/g111a` (live.py, build 3.94 con `--pkg`; arranque en frío ≈ 3 min). Menú y teclas funcionan; abre en Ajustes
personalizados, página 4, «Film Simulation» (3 filas: Kodak, Fujifilm, Fujifilm Sim).
- **Verificado:** elegir Kodak ▸ Portra 400 guarda la fila (`0x1070210` = 6) y el ACK (`0x1070219` = 6) y el gancho de `setValue` **sí corre**: las ranuras de
  Retrato quedan escritas en la NVRAM (`0x1070738/745/752` = −1, −1, 0), o sea el orden de parámetros de `setCreativeStyle` inferido es el correcto.
- **No verificado / sin explicar:** el panel Fn sigue mostrando «Std. ±0 ±0 ±0», «AWB» y «D-RANGE», y no se ven en gris; los ids de Backup del balance y del DRO
  no se han identificado en `nvram.json`, así que no se sabe si `setWhiteBalance` y el `setValue(0x18)` llegaron a escribir. Hipótesis (sin medir): el arnés no
  ejecuta `av-cam`/`libObj` y el panel Fn repinta desde el modelo, que no contesta; la falta de cambio en pantalla sería entonces del arnés y no de la receta.
- **Siguiente paso:** trazar en caliente `WrapperWhiteBalance::setWhiteBalance` (`0x1bfb61`) y `isGrayedOut` (`0x1b4696`) con el perfil `g111a`, o probar en la cámara.

## 6. Límites
- Que los setters lleguen al ISP (y que el look final se parezca a la película) solo se puede ver en la cámara.
- Orden contraste/saturación/nitidez de `setCreativeStyle`: INFERIDO del orden de Sony; ver §5.
- La LUT de cada look se ajustó sobre JPEG Estándar sin desplazamiento de balance: con la receta encima puede pasarse (G110 §5).

## 7. Incidente 3.94 en cámara: Fn → reinicio en bucle (24-11-2026, dicho por el usuario; auditoría estática)
- **Hechos:** instalada por USB (`pmca-console firmware … --flash --confirm`, 3.93 → 3.94, «Done», `analysis/gui/g22/install-3.94.log`). Arrancó; al pulsar Fn
  se reinició y quedó en bucle. Después no aparece por USB (ni `07c4` ni `03e2`).
- **Factor común (VERIFICADO en `build/`):** todas las builds que reescriben `share/app/image_cmn_169.uxc` han fallado en la cámara y ninguna de las que lo dejan de fábrica:

| Build | `image_cmn_169.uxc` | Resultado en cámara |
|---|---|---|
| 3.92 `cfw_film392` | modificado (iconos ISO, G104) | reinicio con «Brillo de monitor» y no enciende (INC-392) |
| 3.93 `iso` | modificado | bucle al arrancar (G105 §7) |
| 3.93 `todo` | modificado | bucle al arrancar (G109 §4) |
| 3.93 `film`, `exfine`, `pp`, `sin_iso` | de fábrica | arrancan |
| 3.94 `sin_iso` | modificado (50 iconos, §3) | Fn (que pinta los iconos nuevos) → bucle |

  Esto debilita la atribución del bucle de `iso`/`todo` solo al gancho `isInhOn` (G108 §1, medida en el arnés).
- **El códec no reproduce a Sony (VERIFICADO):** recodificar con `uxc_imagenes.codifica` 400 iconos nativos de `image_cmn_169` del 3.21 da 0/400 iguales
  (p. ej. `0xc000`: 511 B de Sony frente a 424 B; cambian los campos de cabecera del registro LZPT). El arnés descomprime por software (`tpzl._inflate_segment`)
  y acepta los dos; el LDEC por hardware nunca había recibido un flujo de `encode_lz` dentro de un `.uxc`.
- **Causa probable (INFERENCIA, sin medir):** el LDEC por hardware cuelga o corrompe al decodificar un registro del `.uxc` modificado → cuelgue y reinicio
  por vigilancia. Por qué sigue en bucle tras el primer arranque bueno: NO_VERIFICADO.
- **Recuperación:** batería fuera ≥ 30 s y encender sin tocar Fn; si no aparece por USB, actualizador forzado por SWD (R48, como G105 §4/§7) e instalar
  una build con `image_cmn_169.uxc` de fábrica (`sin_iso` 3.93 con `--reflash`, o una 3.95 = 3.94 sin `iconos_fn`).
- **Regla nueva:** no volver a instalar un `.uxc` modificado hasta que `codifica` reproduzca los bytes de Sony (o use registros `0x0F` almacenados sin LZ).

## 8. Build 3.95 sin iconos: recuperación por SWD e instalación (24-11-2026, MEDIDO)
- `build_cfw_film.CON_ICONOS = False`: `image_cmn_169.uxc` queda de fábrica (no va en `files/`); el resto igual que la 3.94 (receta por la GUI, grises, Extra fine).
  `build/cfw_func395/sin_iso`, `.dat` sha256 `fcf58a3046964d06e2d03a15154e3e372286bc2f0379617777b2250cbacf5b80`; auditoría `todo_ok` (0 violaciones LDEC, sumas bien).
- Recuperación: actualizador forzado por SWD (R48, `analysis/camera-dumps/20261124-cam394-swd/p1.log`, dos veces: se reinició sin querer la primera).
  Dos `updater response error`; ciclo de energía → volvió sola al actualizador (`03e2`) → `Done` (`install-3.95.log`).
- **Verificado:** arranque normal (`07c4`), `pmca-console info` = **3.95**.
- **Falta (cámara):** pulsar Fn (sin iconos nuevos no debería reiniciar si §7 es la causa) y probar Film ▸ Portra 400: estilo, balance, DRO y grises.
