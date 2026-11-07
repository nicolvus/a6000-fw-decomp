# G02/G04 — Recursos de texto, colores y tablas de menú (estático, 07-11-2026)

**Base**: firmware 3.21 extraído (`…/nflasha15_unpacked_unpacked/`, rootfs ext2). **Método**: REA (`viewUnified2.so`,
`cmn_menuTableUtil.so`; Ghidra carga con base +0x10000 respecto a `nm`/vaddr del ELF) + lectura de bytes + Capstone.
**Estado**: nivel 2–3 de la matriz del [README](README.md) para textos y colores (cambio en copia local, **sin** probar
en cámara). Ninguna escritura en cámara.

## 1. Las tres peticiones, resumidas

| Objetivo | Dónde vive | Estado | Dificultad |
|---|---|---|---|
| 1. Colores / diseño | `color_cmn.uxc` (276 B), `style_cmn.uxc`, `LayoutMaster_Menu.uxc`, `view*.uxc`, `image_*.uxc` | Colores: formato visto (INFERENCIA); layouts/estilos sin descifrar | Colores baja; layout media; iconos (`image_*`, 25 MB) sin estudiar |
| 2. Textos | `share/app/string_<idioma>.uxc` (66 idiomas) | **Formato VERIFICADO** y editor de ida y vuelta (`scripts/gui/uxc_strings.py`) | Baja |
| 3. Opciones nuevas | Tablas `CmnViewMenuItemStruct` en `.data` de `viewUnified*.so` + código que reacciona | Estructura del ítem VERIFICADA; añadir ítems = parchear `.so` | Alta (G7: el ajuste debe llegar al *middleware*) |

Todo es sustitución en la partición `/usr` (rootfs); **no** en `av-cam.bin`. Reversibilidad y verificación de integridad
siguen sin determinar (G8): sin esa respuesta no se escribe nada.

## 2. `string_<idioma>.uxc` (VERIFICADO)

```
0x00 'uxc\x07'  u32 0  u16 8  u16 H  u32 (cuenta de ranuras | indicadores; cuenta = &0x1fff)
0x10 tabla de `cuenta` u16 (english: 5 958): ranura k = id-0xe000, 0xffff = vacía,
     valor = (offset del registro - base)/4,  base = 0x10 + 2*cuenta
base registros: u16 id | u16 0x1e04 | texto UTF-8 | NUL | relleno a múltiplo de 4
```

- `string_english.uxc`: 4 360 registros; el índice reproduce las 4 360 entradas sin un fallo; `build(parse(x)) == x` byte a byte.
- El campo u32 de la cabecera **no es una suma de verificación** (probados CRC32/Adler/suma sobre tres ficheros): es la cuenta con indicadores
  (INFERENCIA). Un fichero editado no necesita recalcular nada más que el índice.
- Límite: el índice es de 16 bits en unidades de 4 B → ≤ 262 140 B de registros (english usa 208 KB). Para idiomas mayores (p. ej. `string_thai`, 488 KB) el
  esquema de ranuras puede cambiar: **NO_VERIFICADO**, no se ha parseado ningún otro idioma.
- Algunos textos llevan caracteres de la zona privada (``…): son glifos de icono incrustados; respetarlos al editar.

## 3. Ítem de menú (`CmnViewMenuItemStruct`, 0x28 B) (VERIFICADO)

Accesores en `libObj.so` (`CmnViewMenuData::getId` `0x1256cd`: `[+8]`; `getOptionNum` `0x1257bf`: `[+0x20]`; `getOptionString`:
`[+0x24]`; `getText` indexa `base + 0x28*i`). Tabla real: `DAT_004cc938` de `viewUnified2.so` (Creative Style, 19 ítems; la
inicializa `FUN_0027a050` → `CmnMenuTableUtil::initMenuData`):

| Offset | Contenido | Ejemplo (ítem 1) |
|---|---|---|
| `+0x00` | puntero a subítems (cabecera: `0x4bc640`) o 0 | 0 |
| `+0x04` | contador (cabecera: `0x13` = 19 ítems) | 0 |
| `+0x08` | id del ítem | `0x13` |
| `+0x0c` | recurso de texto `0x0204eXXX`; `&0xffff` = id en `string_*.uxc` | `0x204e126` → «Standard» |
| `+0x10` | recurso de icono | `0x205c869` |
| `+0x14` | recurso de texto de ayuda | `0x204e232` → «Standard style that supports wide…» |
| `+0x18` | icono de ayuda | `0x205c80e` |
| `+0x1c` | indicadores | `0x200` |

Cadena verificada: ítem → id de texto → `string_english.uxc` (tres ítems comprobados en el test). Por tanto **cambiar el nombre de una
opción = editar un registro**, y **añadir una opción = ampliar esta tabla y su contador en el `.so` + registros nuevos** (las vistas
cargan las tablas por puntero; falta ver si hay topes fijos de ítems por página, p. ej. el bucle `0x13` de `FUN_0027a050`).

## 4. Colores `color_cmn.uxc` (INFERENCIA)

Mismo contenedor: tabla u16 (30 ranuras) y registros de 8 B `u8 id | 40 09 3a | R G B A` (`#000000FF`, `#DDDDDDFF`, `#00000099`…). Son
RGBA directos: la modificación de colores es trivial **si** el motor no los copia a otro sitio al arrancar. Sin probar.

## 5. Sesiones REA

`analysis/rea-independent/run/g1.sock` (`cmn_menuTableUtil.so`, 12 s) y `g2.sock` (`viewUnified2.so`, 263 s en frío). Argumentos de apertura:
**sin** `"format"` (con `"format":"elf"` el demonio abre en silencio sin binario). Socket con ruta corta y relativa (`AF_UNIX` ≤ 108 B).

## 6. Siguiente

1. G8 antes que nada: ¿`/usr` escribible, hay verificación de integridad en el arranque o en el paquete de actualización, y hay vuelta atrás sin UI? (lectura de `boot-and-recovery.md` y del actualizador; luego, con autorización, prueba por `adb`).
2. G2: parsear `color_cmn`, `style_cmn`, `viewSettingMenu.uxc` (4,9 KB) y `LayoutMaster_Menu.uxc`; confirmar si hay tope de ítems.
3. G4: volcar todas las tablas de `viewUnified2/4/7` (buscar ítems con cabecera `{ptr, n}`), y localizar la del menú Setup/Shooting.
4. G7: ruta ajuste → `libMWF/libBizFw` para una opción nueva con efecto real.
