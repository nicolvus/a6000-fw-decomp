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
- **Corrección (§9):** el códec no es la causa probable: su repertorio LZ coincide con el de Sony (distancias 1–2, copias solapadas, grupos de 8 literales,
  mismo terminador). Lo que sí violaba era el orden del fichero (§9). Texto original:
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

## 9. Auditoría tras la 3.95 en cámara y correcciones (24-11-2026)
**Dicho por el usuario (3.95):** Fn ya no reinicia; la receta pone estilo y DRO y los grises funcionan; **el balance no cambia**; sigue FN-PP-1 (PP1→PP2 en Fn reinicia);
faltan los iconos.

### 9.1 Balance: `isInhOn` corta la receta (MEDIDO en el arnés)
- Firma real (símbolos de `wrapperWhiteBalance.so`): `setWhiteBalance(ViewBaseProduct*, modo, K, A-B, G-M)`; enum 1 = AWB (el 0 es inválido en sus tablas), `0xc` = K
  (valida 2500–9900), A-B y G-M en −7…7. La receta pasaba bien los argumentos.
- Traza en el arnés (perfil `g111b`, build 3.95, `TRACELIB=viewUnified2.so`): al elegir un look llega `setWhiteBalance(1, 5500, …)`, pasa la validación y
  `WrapperWhiteBalance::isInhOn(1)` devuelve **1**: el setter sale sin escribir (en la NVRAM no aparecen los ids de desplazamiento `0x107027e/f`).
  `isInhOn` pregunta al modelo (`getModelInfo`, factor `0x18c+modo`) y devuelve 1 si la llamada falla o si el factor dice inhibido.
- En el arnés todo el panel Fn sale en gris (inhibición general, ruido conocido), así que la causa exacta en la cámara no está medida; el síntoma coincide.
- **Arreglo:** gancho en el prólogo de `WrapperWhiteBalance::isInhOn` de vu2 (`0x1bfa90`, `films_tramo_wbinh`). El objeto del wrapper es solo la vtable
  (constructor verificado), así que la receta marca el suyo con dos palabras detrás y el gancho devuelve 0 solo para él; el resto de llamadas siguen por el
  prólogo original. Además el selector PP pasa a Off **antes** del balance, el estilo y el DRO.
- Test: `test_wbinh_salta_la_inhibicion_solo_al_objeto_marcado` y el orden nuevo en `test_look_guarda_la_copia…` (Unicorn).
- Comprobación en cámara: con la pantalla de información, el indicador de balance muestra el desplazamiento (p. ej. «AWB A3 G1» con Portra 400).

### 9.2 Iconos: el `.uxc` violaba el orden de Sony (VERIFICADO; que sea la causa del cuelgue: INFERENCIA)
- En `image_cmn_169.uxc` de fábrica, los 6037 registros van **contiguos y en orden de id** desde `base`, y los datos van contiguos tras ellos en el mismo
  orden, cada bloque alineado a 4 con ceros. Sin inversiones.
- El `anade` de G110 (y el de G104, usado en 3.92/`iso`/`todo`) dejaba los registros nuevos al final y en orden **descendente** (50 inversiones), con los datos
  fuera de orden. Un lector que busque por id en la lista ordenada, o que calcule tamaños con el registro siguiente, lee basura → LDEC/GPU colgados.
- **Arreglo:** `uxc_imagenes.anade` reconstruye el fichero con esos invariantes: sin imágenes nuevas devuelve el de fábrica **byte a byte**; con los 50 iconos,
  0 inversiones, datos en orden y alineados, nativos y nuevos se decodifican igual (test `test_imagenes_uxc_ida_y_vuelta`).
- Los iconos solo entran con `build_cfw_film.py --iconos`.

### 9.3 FN-PP-1 (PP1→PP2 en Fn)
Sin cambios: ya estaba en 3.93, sin iconos ni receta, y solo en la franja Fn. No se ha aislado; sigue el plan de G109 §7 (build `pp`+`exfine` sin Film).

## 10. 3.96 en cámara: Fn sigue colgando — auditoría (24-11-2026)
**Dicho por el usuario:** con la 3.96 (iconos en el orden de Sony + arreglo del balance), Fn vuelve a colgar la cámara indefinidamente. El orden del `.uxc`
no era la causa (o no la única).

**Descartado (VERIFICADO):**
- Formato del `.uxc`: con la reconstrucción de §9.2, campos de registro (`0x1a05`, formato `0xc0000000`, tamaño 70×35, desplazamiento), alineación a 4,
  orden, inicio de registros LZPT dentro de los datos, salida por registro (4096 + resto) y bytes tras el terminador son idénticos en forma a los de Sony.
- Códec: el mismo `tpzl.encode_lz` comprime las páginas cambiadas del TPZL de `nflasha15` que el hardware descomprime en cada arranque de cualquier CFW;
  histogramas de longitudes/distancias del mismo repertorio. Los ids nuevos no se solapan con ninguna otra biblioteca `image_*.uxc`.
- Enlace: las opciones nativas del Estilo creativo llevan exactamente las propiedades `1` y `4` con el mismo id (`CautionConfig` `0x1575d4`).
- **Arnés (perfil `g111d`, build 3.96, `LDECLOG`):** con «Film Simulation» asignado al panel Fn, el panel **dibuja el icono propio** (marco de película
  «OFF», `img/g111-fn-icono-film-arnes.png`) sin cuelgue; la GUI pide al LDEC `{longitud, destino, capacidad = 160·35, registros = 2, canal 3, paso 0xa0}`,
  los mismos parámetros que para «Std.».

**Conclusión:** el fallo depende del hardware (LDEC/GPU reales, memoria de texturas o algo que el arnés no emula) y no se puede aislar en estático.
Lo único distinto entre 3.95 (bien) y 3.96 (cuelga) son los iconos: `image_cmn_169.uxc` y las propiedades `1`/`4` en `CautionConfig`, vu2, vu4 y vu7.

**Para aislarlo (necesita la cámara):**
1. Captura por SWD durante el cuelgue (detener la CPU y leer PC/LR); con la cámara apagada el DP no responde (probado).
2. Bisección: build con las propiedades apuntando a imágenes **nativas** (sin tocar el `.uxc`): si cuelga, el problema es el enlace en nuestros nodos;
   si no, son nuestros datos de imagen en el hardware.

## 11. Cuelgues 3.96/3.98 por el gancho de `isInhOn`; balance en gris (24-11-2026)
- **Registro del kernel en vivo por AHB-AP** (sin detener la CPU; `analysis/camera-dumps/20261124-cam394-swd/klog_mon.py`, base `bz_mon.py` de R59):
  `log_buf_len`/`log_buf` en VA `0x4037c760`, `log_end` en `0x40395290` (kallsyms del kernel 3.21 + `emit_log_char`); PA = VA + `0x40000000`.
  Detener la CPU por SWD cada 250 ms produce «Error de cámara» (no repetir); un acceso de 8 bits por `mem_ap` bloquea el AHB-AP hasta apagar la cámara.
- **3.98 (iconos nativos, MEDIDO):** Fn abre bien; **cuelga al entrar en AWB**. El kernel no registra nada antes del reinicio (cuelgue de espacio de usuario + vigilancia).
- **Causa (VERIFICADO en estático):** el gancho `films_tramo_wbinh` (§9.1) leía `[this+8]`; los llamadores de Sony de `WrapperWhiteBalance::isInhOn` pasan
  `this` sacado de campos de objetos (`[r9+0x2c]` en vu4, `[r4+0x124]` en vu7), que pueden ser nulos porque el original no usa `this`.
  Es también la causa probable del cuelgue de la 3.96 al pulsar Fn (la casilla AWB del panel). La 3.94 (sin este gancho) colgaba por el `.uxc` desordenado (§9.2).
- **Arreglo:** el gancho solo lee la marca si `this` está en la pila del hilo (`0 ≤ this − sp < 4 KB`, donde vive el objeto de `pon`); nulos y punteros
  de campos siguen por el `isInhOn` original sin tocarlos (test con `this` = 0, 0x10 y fuera de la pila).
- **Decisión del usuario:** la receta **fuerza** el balance (looks lo más reales posible) y con cualquier look activo el balance queda **en gris** (no se
  cambia a mano en ningún look; antes solo en los de kelvin fijo).
- Build 3.99: `--iconos` (orden de Sony) + receta con balance forzado (gancho corregido) + balance en gris con cualquier look.

## 12. 3.99 no arranca; build 4.00 = 3.95 + balance en gris (24-11-2026)
- **3.99** (iconos propios ordenados + gancho `isInhOn` con comprobación de pila): instalada por USB («Done»); **se cuelga y no arranca** (dicho por el usuario).
  Causa sin aislar: los dos cambios respecto a la 3.98 (que arrancaba) son el `.uxc` con iconos propios y la comprobación de pila del gancho.
- **Por orden del usuario, sin más arreglos:** build **4.00** = 3.95 (que funcionaba) + balance en gris con cualquier look; sin iconos, sin gancho de
  `isInhOn` (la receta llama a `setWhiteBalance` como en la 3.95: si el modelo lo inhibe, el balance no cambia). Único fichero distinto de la 3.95:
  `lib/viewUnified2.so`. `.dat` sha256 `102cd2f9…`, auditoría `todo_ok`.

## 13. Build 4.01 = 3.98 + balance en gris con cualquier look (25-11-2026)
- **Aclaración del usuario:** la base buena es la **3.98** (el gancho funcionaba: la receta fuerza el balance); solo faltaba que el balance no se pueda
  cambiar a mano mientras haya un Film Sim activo (libre con Film en Off), y que los looks sigan aplicando su balance.
- **4.01** = fuentes de la 3.98 (`films.c`/`film_userland.py` de `3a2ca282`, gancho `isInhOn` con marca sin comprobación de pila) + `--iconos-nativos`
  (`.uxc` intacto) + `films_gris`: balance (pid `0x17`) en gris con cualquier look. El cuelgue de la 3.98 era al **entrar** en AWB; en gris ya no se entra.
  La 3.99 (que no arrancó) además llevaba el `.uxc` con iconos propios y la comprobación de pila; ninguno de los dos va en la 4.01.

## 14. 4.01 en cámara; los vídeos no se reproducen en la cámara (25-11-2026)
- **4.01 instalada** por SWD + USB («Done» al segundo intento); el usuario confirma que **funciona**.
- **FILM-PB-1 (usuario):** los vídeos se graban y se ven en el PC, pero la cámara no los reproduce.
- **Auditoría estática (sin causa todavía):**
  - `libmprctrl.so` (EXFINE): sus dos ganchos están en la ruta de fotos (`CalcStillData_JPG`, `GetStillDataInfo`). El ELF solo amplía el primer `PT_LOAD`
    (`0x31bd0` → `0x31d28`), sin solaparse con el segundo (`0x32000`).
  - `av-cam` Film: la LUT (`FUN_4381d294`) solo cambia la tabla si Sony ya tiene una 3D-LUT activa. La curva (`FUN_43854718`/`a28`/`fec`, `FUN_43b098c0`)
    y la máquina (`FUN_437a24fc`) solo actúan con un look activo (ACK ≠ 0).
  - Quedan sin descartar: el núcleo Silent/PP de `av-cam` y los parches de la GUI (`vu2`/`vu4`/`vu7`, `libObj`, `CautionConfig`).
- **Usuario:** con Film y PP en Off tampoco se reproducen (las fotos sí); sospecha de Silent.
- Revisado contra Sony (`av-cam`, 42 zonas cambiadas): los parches de Silent (`0x438d01ae` envío a Darwin, `0x43841472` paquete de la foto, copiador
  `0x43845f2e`, lectores `0x4384219e`/`0x43842270`, cueva r5 `0x438c82fe`) están en rutas de captura; el ajuste usa la cadena nativa y dormida de Sony
  (`0x291` → LIRO `0x40e3` → `+0x238`). Sin causa estática; quedan también Darwin v3 y el paquete sin `nflasha5` (arranque en frío).
- **Bisección:** build **4.02 = solo Silent** (`--funciones ''`, sin Film/PP/EXFINE), `.dat` `c2a60f55…`, auditoría `todo_ok`. Si en la 4.02 los vídeos
  no se reproducen, el fallo está en Silent o en la base (Darwin v3 / sin WBI); si se reproducen, en las capas Film/PP/EXFINE aunque estén en Off.
- **4.02 (solo Silent) instalada:** los vídeos **tampoco** se reproducen (usuario). El fallo está en Silent o en la base, no en Film/PP/EXFINE.
- **Inventario de la 4.02 frente a Sony 3.21:**
  - `av-cam` (8 zonas): paquete de la foto `0x43841472`, lectores `0x4384219e`/`0x43842270`, copiador `0x43845f34` (+`0x43845f9f`), r5 `0x438c82fe`,
    envío a Darwin `0x438d01a2`, cueva `0x43fb7e00`. Todo en rutas de captura.
  - `darwin_core.bin` (5 zonas): cueva en los vectores 70/76 (`0x4318`/`0x4330`, a cero en Sony), R82 `0x18d7a` (146 B), compuertas `bl` en `0x1fe6c`
    (motor) y `0x20c78` (bobina), que leen `S+0x3e` = `pkt[0x0e]`.
  - Paquete sin `nflasha5` (WBI, arranque en frío).
  - Userland: nodo Silent en `CautionConfig.so`; `viewUnified2.so` con `add_menu_entry`, descriptor de Silent (pid `0x12`) y `pid_space` (tablas ELEM/D
    reubicadas, EFCS en gris); `libObj.so` con el eco del setter de Silent (`0x686de6`/`0x686dfa`); textos.
- **Bisección 2:** build **4.03 = núcleo de la 4.02 + `/usr` de Sony** (`nflasha15` original: sin menú Silent ni parches de userland), Darwin v3, sin
  `nflasha5`. `.dat` `3d16faf5…`. Auditoría: todo OK salvo «solo cambian los miembros previstos», que es lo esperado (la `nflasha15` es la de Sony).
  Si reproduce → el fallo está en el userland de Silent; si no → en el núcleo (`av-cam`/Darwin) o en la falta de `nflasha5`.
- **Auditoría completa de Silent frente a la reproducción (25-11-2026, estático):** ningún parche de Silent está en la ruta de reproducción.
  - `av-cam`: el envío `0x438d0064` reescribe `pkt[0x0e]` en todo paquete `0x0c` a Darwin, pero Darwin de Sony no tiene lectores de `S+0x3e`
    (E25-25); solo lo leen nuestras compuertas (motor `0x1fe6c`, bobina `0x20c78`), que con Silent en Off (0) siguen la ruta de Sony. La cueva r5
    (`0x43fb7e00`) cuelga de la secuencia de foto `0x438c828c` y sale sin tocar nada si el byte vivo `0x43EDF684+0x238` ≠ 1.
  - `libObj`: el setter parcheado `0x686d10` tiene un solo llamador (`0x689f08`), que solo atiende la clave `0x291` de Silent.
  - `viewUnified2`: `D[0x12]` de Sony es el descriptor sin modelo de AfTrackingSpeed (G28, inerte); `pid_space` solo amplía el rango y copia tablas.
  - **El único cambio global de todas las builds desde la 3.52 es el arranque en frío (sin `nflasha5`)**: Sony siempre reanuda el WBI (modo 11) y la
    capa de medios tiene modo propio para él (`MprIf::SnapShotBootInit`, «Snapshotboot mode», `createSnapshot` en `libmpr.so`). La bisección 4.02/4.03 no
    lo separa: las dos van sin `nflasha5`. «Es Silent» sigue sin demostrar.
- **Build de control 4.04 = Sony 3.21 intacto salvo `nflasha5`** (`build_package_nflasha15.py` sobre `fw321/firmware.tar` y la `nflasha15` de Sony,
  `--sin-wbi`, sin Darwin v3). Comparado con el tar de Sony: falta solo `dev/nflasha5` y su línea de `part_image.sum`. `.dat` `9c7b4f46…0872`
  (`build/sony_puro_sin_wbi_404/`, no versionado). La comparación y el criterio de cierre se detallan en §14.1.
- **Auditoría estática exhaustiva (25-11-2026, 8 tareas de un subagente; notas fuera del repo):**
  - Inventario 4.02 vs Sony por bytes: 6 miembros del tar; `av-cam` 233 B en 8 zonas (único fichero cambiado de `nflasha3`); Darwin 5 rangos;
    `nflasha15` solo `libObj`, `CautionConfig`, `viewUnified2` y 25 `string_*.uxc`; falta `nflasha5`.
  - Descartados: globales de MPR en frío (`MprCtrl::Init` → `MprIf::Create` `0x712530` fija lo mismo que `SnapShotBootInit`); `0x438d0064` es
    `[EN->CA] CAP_SETTING` (solo captura); Darwin: la cueva `0x4318`/`0x4330` ocupa vectores 70–73/76 a cero y solo se habilitan IRQ 0–31; compuertas
    solo con llamadores del obturador; R82 solo desde `0x190fc` (captura); `viewUnified2`: 5 páginas de Custom Settings +1 entrada cada una,
    `.rel.dyn` con las 91 744 relocaciones de Sony intactas, PT_LOAD sin solapes; `CautionConfig` solo listas de Silent; `.uxc`: 109 000 textos iguales.
  - WBI de Sony: 37 módulos con los mismos parámetros que inserta el frío (solo `wlanMemoryAllocator` extra, Wi-Fi). Sin módulo ni proceso solo-WBI.
  - **Sin causa estática.** Quedan: arranque en frío (lo que la instantánea trae hecho: mapa `DmmConfig*.bin`, RAM) y, en teoría, pids `0xE9–0x120`
    de `pid_space` (ningún pid de reproducción recuperado). Lo decide la cámara: 4.04 y, si reproduce, 4.03.

### 14.1 Verificación de los dos pendientes (offline)

- **PID 0xE9–0x120:** lectura del ELF de 4.02 siguiendo los literales PC-relativos de `getElement` e `initProcessDataElement`: ELEM = `0x6f3c50`, D = `0x6f40d4`. En las 233 entradas originales, ELEM coincide íntegramente con Sony y en D cambia solo `0x12` (Silent). Las 56 entradas nuevas de D son nulas y las 56 de ELEM usan la clase Normal. Esto descarta un descriptor nuevo de vídeo en 4.02. Sigue abierta una regresión del gestor si algún llamador antes rechazado entrega un ID de ese intervalo, o si falla el acceso a las tablas reubicadas. No hay una traza de reproducción que lo señale.
- **DMM y arranque:** REA sobre `dmm.ko` de Sony identifica los parámetros `DmmConfig` y `DmmConfigExtra`, y la ruta por defecto del extra `/setting/DmmConfigExtra.bin` (`0x307f2`). En las secciones 0082/0099 del WBI se lee `DmmConfig=/usr/share/dmm/DmmConfig.bin` y en 1032 también se lee `DmmConfig=/setting/DmmConfig.bin`. Son cadenas presentes en RAM archivada y por sí solas no identifican la configuración efectiva, las reservas ni la RAM disponible. `libmpr.so` contiene diagnósticos diferenciables de reserva (`[MemInfo]DMM Alloc failed...`), demultiplexado (`ER_MOVIE_DECODER_DEMUX_ERROR_STREAM`) y decodificador (`ER_MOVIE_DECODER_HW_ERROR`).
- **Control 4.04 verificado:** comparación por SHA-256 del contenido de todos los miembros regulares de ambos tar. Se omite únicamente `dev/nflasha5` y se elimina su línea de `part_image.sum`. SHA-256 del DAT: `9c7b4f46491dcb030a69c3810d21429afcffdc9867b840969d914808fe510872`.
- **Criterio de cierre:** comparar en la misma cámara el mismo clip de la misma SD con Sony 3.21 reanudando WBI (confirmar BootMode 11) y con 4.04 en frío (confirmar modo de arranque). Solo si Sony con WBI reproduce y 4.04 falla se aísla el modo de arranque. Eso todavía no identifica DMM, el estado de su pool ni la RAM Linux. Si ambas reproducen, 4.03 distingue núcleo de userland al compararla con 4.02. Si ambas fallan, revisar visibilidad por formato e indexación, y distinguir clip ausente de fallo al pulsar Play. Registrar si hay miniatura, audio, pantalla negra, aviso o cuelgue, y la primera línea de error de DMM/MPR tras pulsar Play. Comparar los parámetros DMM efectivos y `/proc/meminfo` entre arranques si hay acceso de lectura. G11 §11 explica por qué restaurar directamente el WBI de Sony sobre el `/usr` modificado arrastra su TOC y caché antiguos.

### 14.2 Conexión entre arranque, DMM y decodificación AVC

**Camino del decodificador verificado en el `av-cam.bin` oficial 3.21.** REA sobre la sesión persistente y comprobación de las instrucciones Thumb originales. Los llamadores `0x4391565c`/`0x4391569c` pasan por `AvcDecVideoZimaAccessor::AllocWorkMemory` (`0x43915e20`) antes de continuar con `0x43915c8c`. Para el cambio a tipo 1, `0x43915e20 → 0x4391bd58 → 0x4392117c`. El último pide unidades DMM según su rama. Ejemplos: `0x2A1` en `0x43921270` y `0x2A0` en `0x439212e4`. Para `0x2A0` exige al menos `0x65800` bytes (415 744) en `0x439212ea`. Los tipos elegidos dependen del estado del decodificador. Una devolución insuficiente sale por error antes de completar la inicialización.

**Contrato de reserva comprobado en ejecución aislada.** `0x43b3c988 → 0x43b2e39c → 0x4390c630` emite el comando 1 (Open) con el tipo solicitado y componente `0x1111`. En el otro extremo, `dmm.ko:dmm_ctrl_OpenUnitHdlr` (`.text+0x609c`) llama a `dmm_unit_ctrl_Open`. Se ejecutaron por separado los bytes originales de `0x43b3c988`, `0x4392117c` y `0x43915e20` en Unicorn con respuestas sintéticas en sus dependencias. Open con éxito entregó handle, dirección y tamaño. Un error de transporte o de estado hizo que devolviera `0xffffffff` sin escribir esas salidas. Con un extent de `0x657ff` para `0x2A0`, el backend devolvió `0x83000000`; con `0x65800` avanzó a pedir `0x29F`. El error del backend hizo que `AllocWorkMemory` ejecutara la limpieza y devolviera `0xffff0001`. Los dos llamadores propagan el resultado y solo continúan al abrir el decodificador si es cero.

**Dónde cambia el estado DMM.** El initrd normal contiene `/usr/kmod/dmm.ko` y el argumento `DmmConfig=/setting/DmmConfig.bin` en `sbin/init` (offsets de fichero `0x29a3`/`0x29b4`). Al inicializar el módulo, `dmm_module_InitModule → GetConfigData → dmm_ctrl_Init` configura las tablas y puede inicializar unidades de arranque. `GetConfigData` usa el fichero configurado por el parámetro en la rama del búfer de inicialización; un fallo de apertura sigue la salida de error. Al reanudar, `dmm_module_ResumeModule` llama a `dmm_ctrl_HotPlugPwrDwnUnit` y `dmm_unit_ctrl_ResumeUnit`. Esas funciones recorren reservas y estados persistidos, copian y liberan extents cuando corresponde, sin recargar el mapa principal por `GetConfigData`. Se verificaron los destinos en las relocalizaciones ARM del módulo original. El estado de arranque que consulta DMM se lee de Backup en `dmm_ctrl_Init`; no se ha igualado ese valor interno con el BootMode de Loader3.

El volcado de la cámara del 20-10 registra un `DmmConfig.bin` de 97 544 bytes. El log histórico 3.98 registra eventos UDIF de suspensión y reanudación DMM, pero carece de una reserva de vídeo asociada a un intento de Play. Tampoco basta la cadena «Snapshotboot mode» de `libmpr.so`: su referencia `0x651b0e` pertenece al comando diagnóstico `Resume ... <HOT|SNAP>`. `MprIf::SnapShotBootInit` sí existe (`0x71ce64 → 0x712010`), aunque estas referencias por sí solas no enlazan su parámetro con el fallo de Play.

**Veredicto.** Hay una cadena causal de software comprobada: la forma de inicializar o reanudar DMM puede afectar las unidades que abren el decodificador AVC, y un Open fallido o un extent insuficiente impide iniciar ese decodificador. Falta demostrar que el estado de la cámara difiere para alguna de esas unidades y provoca el fallo observado. No hay evidencia de que falte todo el mapa, de que el archivo sea distinto o de que falte RAM general de Linux. La grabación correcta es compatible con un fallo en las reservas específicas del decodificador.

**Captura discriminante, solo lectura y con autorización física.** Con el mismo clip AVC en ambos arranques, comparar el primer Open tras Play y su respuesta (tipo, estado, handle, tamaño). El driver publica `/proc/udm/dmm_info`, `dmm_units`, `dmm_extents`, `dmm_reserve` y `dmm_log`. Capturar las tablas antes y después, junto con el error del decodificador. Un Open o tamaño inválido solo en frío, seguido por `0xffff0001`, confirmaría el mecanismo para esa sesión. Si el decodificador supera esa fase, seguir demultiplexado, audio y presentación.

### 14.3 Cadena integrada sobre los paquetes 4.01 y 4.02

Se extrajo AV-CAM.BIN de los tar de ambas builds con `avcam_fuente.avcam_de` y se ejecutó el mismo recorrido de instrucciones que Sony desde `0x4391569c`. La réplica conserva las llamadas nativas a `AllocWorkMemory`, su backend, la construcción de Open, la validación de la respuesta y la propagación del retorno. El límite simulado se desplazó desde el backend al transporte OSAL de mensajes. El parser del flujo, los objetos iniciales, las respuestas DMM, la limpieza de las dependencias externas y la apertura posterior se controlan. El código `0x43915c8c` se marca como alcanzado y devuelve cero en el arnés; no se ejecuta el decodificado del archivo ni el controlador del kernel.

Evidencia reproducible: `scripts/gui/avcam/replay_playback_dmm.py AV_CAM_BIN CASO`; las 12 ejecuciones y hashes están en `analysis/gui/film-pb-replay.json`. El script valida el resultado y la llegada a la apertura mediante asserts. Las trazas de cada caso coinciden entre Sony, 4.01 y 4.02.

| Respuesta OSAL/DMM controlada | Unidades abiertas por la cadena | Retorno al llamador | Apertura posterior alcanzada |
|---|---|---|---|
| Correcta, tamaños suficientes | 0x2A0, 0x29F, 0x92041 | 0 | Sí |
| Tamaño 0x657FF en la primera unidad | 0x2A0 | 0xFFFF0001 | No |
| Estado DMM negativo | 0x2A0 | 0xFFFF0001 | No |
| Error de transporte | 0x2A0 | 0xFFFF0001 | No |

En el caso de tamaño insuficiente, el chequeo es `0x439212ea`, el backend pasa por `0x43921230`, se ejecuta la limpieza y `0x43915e94` devuelve el error superior. Los otros dos casos también propagan el fallo hasta el mismo llamador.

**Resultado respecto al incidente:** el fallo físico sigue sin reproducirse con sus entradas reales. El ensayo anterior de §14.2 inyectaba respuestas en funciones aisladas; este ensayo las integra hasta el transporte OSAL y compara el CFW afectado con Sony. Los tres binarios avanzan con las mismas respuestas suficientes y fallan con las mismas respuestas insuficientes. Esto verifica la dependencia y el punto de propagación, sin atribuir todavía el fallo de la cámara al arranque. Faltan su estado DMM al pulsar Play y el tipo de decodificador elegido por el clip real. El arnés no deduce que el arranque en frío genere esas respuestas.

## 15. Iconos centrados y estado de los iconos para la futura build (25-11-2026)
**Petición:** el icono no queda centrado; corregirlo y dejar aquí cómo quedan los iconos para una build futura. Nada instalado.

### 15.1 Causa del descentrado (MEDIDO en el arnés)
- El panel Fn dibuja la imagen de la opción **arriba de la casilla y centrada en horizontal**. Medido en el arnés: casilla de 105×61 px; el icono de 70×35
  quedaba con el centro en y = 324 frente a 336,5 de la casilla (13 px alto).
- Los ajustes nativos de **icono simple** (Modo de medición `0xc45b`, Efecto `0xc52b`) llevan **solo la propiedad `1`** con una imagen de **70×60** y el
  dibujo centrado (filas 11…48). Es el tamaño más común de `image_cmn_169.uxc` (1 095 imágenes).
- El patrón que copiamos en G110 (propiedades `1` y `4` con 70×35) es el del **Estilo creativo**, que deja el icono arriba porque debajo la cámara pinta
  «±0 ±0 ±0».

### 15.2 Arreglo
- `iconos_film.py`: dibujo de 70×35 dentro de una imagen de **70×60 transparente, centrado** (centro del dibujo en (34,5; 30), el nativo en (34; 29,5)).
  Los 50 PNG de `scripts/gui/iconos/` regenerados.
- `build_pp_menu.build_nodes`: cada opción con icono lleva **solo la propiedad `1`** (sin la `4`).
- Test `test_iconos_70x60_centrados_y_solo_propiedad_1` (los 50 iconos y los nodos generados).
- **Arnés** (perfil `g111e`, build de prueba `build/g111_iconos_centrados`, 4.90, **solo para el arnés: no instalar**; `.dat` `810c1fe7…`):
  la casilla «Film Simulation» del panel Fn muestra el marco «OFF» centrado como los iconos nativos ([captura](img/g111-fn-icono-centrado.png): arriba
  70×35, abajo 70×60). En ese perfil había un PP activo, así que Film sale en gris y no se pudo girar la franja (regla de FILM-10).

### 15.3 Cómo funcionan los iconos (resumen para la futura build)
1. **Formato de `image_cmn_169.uxc`** (`uxc_imagenes.py`, §3):
   - registros de 20 B en orden de id;
   - datos en `base + 4·t + 4 + desplazamiento`;
   - LZPT (`tpzl.encode_lz`, registros de 4096 B, el formato del LDEC);
   - salida RGBA4444 en filas de ancho redondeado a 16 (formato `0xc0`).
2. **Orden de Sony** (§9.2): `uxc_imagenes.anade` reconstruye el fichero con registros y datos en orden de id, alineados a 4. Sin imágenes nuevas devuelve
   el de fábrica byte a byte.
3. **Imágenes:** `scripts/gui/iconos/film_00…38.png` (Off + 38 looks) y `pp_00…10.png` (PP OFF, PP1…PP10), 70×60, generadas con `iconos_film.py`
   (la build solo lee los PNG).
4. **Enlace:** propiedad `1` = `0x0205xxxx` con el id de imagen en cada opción de las filas de Film, la lista única y el selector PP
   (`build_pp_menu.ICONOS`, rellenado por `build_cfw_film.iconos_fn`).
5. **Opciones de build:**
   - `--iconos`: iconos propios (añade las 50 imágenes);
   - `--iconos-nativos`: bisección, los nodos apuntan a imágenes de Sony con el `.uxc` intacto;
   - sin opción: sin iconos (como la 4.01 instalada).

### 15.4 Estado en la cámara y qué falta
| Build | Iconos | Resultado |
|---|---|---|
| 3.94 | propios, `.uxc` fuera de orden | Fn → bucle |
| 3.96 | propios en orden + gancho `isInhOn` | Fn cuelga (por el gancho en la casilla AWB, §11) |
| 3.98 | nativos (`--iconos-nativos`) | Fn bien; cuelga al entrar en AWB (gancho) |
| 3.99 | propios en orden + gancho con comprobación de pila | no arranca, sin aislar |
| 4.01 (instalada) | ninguno | funciona |

- **Nunca se ha probado en la cámara una build cuyo único cambio sean los iconos propios.** La 3.99 mezclaba los iconos con otro cambio del gancho.
- **Siguiente paso para la build futura:** 4.01 + `--iconos` (nada más) y, sin la 3.99 aislada, con la recuperación por SWD a mano (R48). Si arranca y el
  Fn abre: iconos propios centrados resueltos. Si no: probar `--iconos-nativos` sobre la 4.01 para separar los datos de imagen del enlace.
- Arnés: sin cuelgues con iconos propios en 3.94, 3.96 ni en esta prueba, porque no emula el LDEC/GPU reales (§10).
