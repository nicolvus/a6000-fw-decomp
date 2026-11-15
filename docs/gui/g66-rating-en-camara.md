# G66 — Rating de fotografías en cámara (parcial: sin Rating latente; la escritura en sitio solo cubre Orientation)

Fecha 15-11-2026. Estático sobre firmware 3.21 (`nflasha15`), `libmpr.so` (sha256 `9a74a3bb42836559…`, Thumb-2, VA = offset en el primer LOAD, literales absolutos) con Capstone; comparado con α6300 2.01 y A7S 3.20. Sin cámara, sin CFW construido, sin tocar `scripts/gui/harness/`; no se arrancó qemu (por tanto no hay perfil que borrar).

## (a) ¿Rating latente? NO
- Búsqueda de `Rating|RATING|Star(s)|xmp:|RatingPercent` en todos los binarios de nflasha15/16 de 3.21, α6300 y A7S: solo coincidencias ajenas (`PANELEVF_EVF_ADJ_TEMP_STAR*`, `sa_star.bin`, teclas `STAR`, `clocksource_change_rating`). En α6300 aparece `MTP_PROPERTY_RATING` en `libmtp.so` (Android genérico, sin uso en la UI Sony).
- `string_english.uxc` (4 360 entradas en 3.21, 5 415 en α6300; `uxc_strings.py dump`): ninguna cadena con rating/star/favorite/mark (solo «Protect», «Rotate»). A7S: el formato `.uxc` difiere (el parser falla), pero `grep` de palabra «rating» no da nada.
- Constantes 0x4746 / 0x4749 como inmediatos en `libmpr.so`: 0 coincidencias (barrido lineal, orientativo).
- Consecuencia: no hay menú ni nodos para otro modelo que cambiar por lista (patrón G39/G58 no aplicable).

## (b) Proteger (plantilla del flujo)
- `MprIf::Protect` (`0x722efd`, 24 B) solo reenvía por PLT (`0x11e894`) a la implementación (cadena de comandos `ProtectCmd`, `dcf_If::ProtectContent`, `SetEntryIdList`).
- La escritura real es un `Chmod` FAT del fichero en el bucle `[IFO]` de `libmpr.so` `0x5d1400–0x5d1528`: lee el estado (`GetEntryStat`), compara con el byte `bProtect` de la entrada (`[r4+0x17]`) y registra «Chmod Protect ON/OFF» (`0x5d14de`/`0x5d14e2`, cadenas `0x8c9e9c`/`0x8c9ede`). El bit va en el atributo del fichero; el índice lo lee de ahí (no hay DB aparte de «protegido»).
- Cadenas de error: `ProtectCmd : Ifo Protect Error`, `Err ProtectContent …`. Sirve de plantilla para el flujo menú → comando → atributo, pero Rating necesita 5 valores dentro del fichero, no un bit de atributo.

## (c) Reescritura de cabecera EXIF: existe, pero solo valores ya presentes
- `MprIf::ChangeRotationAngle` (`0x722521`) → rutina de ficheros `0x384490` (push) con cadenas «Err ChangeRotationAngle dfs::Stat/Seek/Write/Close/Chmod ec»: hace `Chmod` (quita solo-lectura), parsea el EXIF (`0x384184`), llama a `0x373ae0`, hace `Seek` + `Write` del valor y restaura el atributo. Evidencia: ref. a «Ratate Tag is None» en `0x3845d4`, «dfs::Seek» `0x3845fe`, «dfs::Write» `0x384612`.
- `0x373ae0` recorre las tablas de entradas IFD0 (`ctx+0x5948`) y de miniatura (`ctx+0x5978`) comparando el id con **`0x112`** (`cmp.w r1,#0x112` en `0x373b0c` y `0x373b9a`), exige tipo 3 (SHORT) y cuenta ≠ 0, y sobrescribe 2 bytes in situ. Si no hay tag: «Err Orientation Tag None!» (`0x373c16`) → error `0x12800007`. **No inserta etiquetas ni mueve el IFD.**
- Otra vía: `MprIf::ModifyExifInfo` (`0x722311`; GPS/«copiar EXIF»): reconstruye el APP1 completo (`MakeAppOne` `0x389ba2`/`0x38a2e0`, `MakeAppOneForRaw` `0x38aa58`, `CompareModelName` `0x38a754`, búsqueda DQT/EOI `0x388ce6`). Es un motor de reescritura total desde `ExifSrcInfoArea`; añadir ahí 0x4746 exige localizar el generador de IFD0 de `MakeAppOne` (no hecho).
- Muestras reales (JPEG `DSC03721.jpg`, ARW `DSC03779.ARW`, A6000): IFD0 JPEG = 12 entradas (`0x10e,10f,110,112,11a,11b,11c,128,131,132,13b,8769`); ARW = 18 entradas. **Ninguna lleva 0x4746/0x4749.** Único hueco aprovechable sin reorganizar: `0x13b` (Artist, ASCII, cuenta 1 = vacío) en JPEG, que es contiguo en orden (0x132 < 0x4746 < 0x8769); en ARW no existe. Reutilizarlo borraría un Artist real y no cubre RAW ni 0x4749.

## Veredicto: PARCIAL (no implementado)
Factible, pero excede una sesión: hace falta (1) entrada «Valoración» 0–5 en el menú de reproducción (nodo + ids `.uxc` + gestor en `libObj`), (2) escritor que **inserte** tags (la ruta de Rotar solo sobrescribe), y (3) icono de estrellas en la vista de reproducción. Verificable hoy: ausencia de código latente, rutas de Proteger/Rotar, tabla de tags. No verificable en el arnés: la reproducción no tiene código de tecla verificado (`g22-emulador-uso.md`, «Límites») y av-cam/BIONZ no escribe SD desde la UI; por eso no se entró en reproducción ni hay captura.

## Diseño propuesto (por fases, ver PENDIENTES RATING-1/2/3)
1. **Escritor**: opción A (mínima, solo JPEG con Artist vacío): reutilizar la ranura `0x13b` → `0x4746` SHORT; opción B (general): parchear el generador de IFD0 de `MakeAppOne` para emitir 0x4746/0x4749 y regrabar con `ModifyExifInfo`. Prueba: Unicorn sobre `libmpr.so` con un JPEG real + test de bytes originales.
2. **Menú**: entrada nueva «Valoración» (0–5) en el menú de reproducción, añadiendo (nunca sustituyendo), siguiendo `add_menu_entry.py`/`menu_tables.py`.
3. **Pantalla**: icono/«★n» en la vista de reproducción.
