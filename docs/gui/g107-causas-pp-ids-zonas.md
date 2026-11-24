# G107 — Causa de PP7–PP10/S-Gamut, ids libres, «zonas libres» del núcleo e ISO en el arnés (24-11-2026)

Continúa [G106](g106-auditoria-estatica-393.md). Por orden del usuario, todo es estático o en el arnés: no se ha instalado nada.

## 1. PP7–PP10 y S-Gamut: el validador de órdenes de `libObj` los rechaza (VERIFICADO)

**Mecanismo.**
- Toda orden a la cámara pasa por `PreTypeCheck` (`0xa3a9xx…0xa3ac90`), que valida cada PARAMID enumerado con `EnumValueCheck` (`0xa3a21c`).
- La lista de cada PARAMID está en su definición de tipo: `0x95aca8` → `0xaf4c1c` → registro de 12 B en `0xfde034 + 12·(PARAMID − 0x9500)`, con formato `{tipo, clase | cuenta<<16, lista}`; la clase 4 es enumerado.
- Ejecutado con Unicorn sobre la `libObj` 3.21 de fábrica:

| PARAMID | Lista admitida |
|---|---|
| `PP_COLOR_MODE_TYPE` `0x9673`, `_SET` `0x9692` | los 8 Color Mode nativos (STD…CINEMA) |
| `PP_GAMMA_TYPE` `0x9685`, `_SET` `0x96a4` | los 12 Gamma nativos (incluye S-Log2 `0x480` e ITU709(800%) `0x481`) |

- Fuera quedan B&W, S-Gamut, S-Gamut3, S-Gamut3.Cine, S-Log3 (`0x585`) y HLG, y la orden con cualquiera de ellos no sale («ValueCheck ERROR»).
- Encaja con todo lo medido en la cámara (G106 §1):
  - PP7/PP8 llevan S-Gamut y PP9/PP10 llevan S-Log3 con S-Gamut3(.Cine) (`pp_factory`): no se eligen, y la selección se queda en PP6;
  - Color Mode = S-Gamut en una fila: el eco lo pinta, pero no llega al núcleo ni a la NVRAM, y vuelve al valor anterior tras la reproducción;
  - S-Log2 sí está en la lista, y por eso se guarda.
- Los demás ajustes del menú PP están dentro de sus rangos de validación (clase 3, mín./máx.), comprobado uno a uno.

**Segundo defecto, de la misma ruta.** El CFW usaba para B&W `0x504` y para S-Gamut `0x505`, los VALUEID de la A7S. En la `libObj` de la A6000:
- `0x504` es `VALUEID_NO_SET`, el centinela de «sin valor», comparado en 5480 sitios;
- `0x505` es `VALUEID_COMP_RESULT_OK`, el resultado que llevan las respuestas (p. ej. `0x482950`).

**Arreglo:**
- `scripts/gui/pp_valuecheck_patch.py`: listas nuevas (nativa + las del CFW) en un segmento RW añadido con `rueda_film._anade`. Cada registro con la lista nativa pasa a apuntar a la nueva, con su cuenta. El puntero lleva relocación RELATIVE, y se comprueba. Es idempotente.
- `patch_libobj_pp.COLOR`: B&W = `0x589`, S-Gamut = `0x58A`, ids libres tras HLG `0x586–0x588`, como ya eran `0x583–0x585`. Ese VALUEID solo vive dentro de `libObj`; al núcleo va el índice 0–11.
- Lo aplica `build_pp_menu` cuando hay Gamma o Color ampliados.
- En la `libObj` final de la build `pp` (tras `ppeco`), Color Mode admite 12 valores y Gamma 13.

**Tests:**
- `tests/test_g107_pp_valuecheck.py`: la `libObj` de fábrica rechaza los valores del CFW; tras el arreglo, la definición real (Unicorn) los admite; y B&W/S-Gamut no son centinelas.
- `test_g26_color_libobj.py` actualizado.

**Sin verificar en cámara:** elegir PP7–PP10 y que S-Gamut y S-Log3 se guarden.

**Menú PP:** `pp_menu_spec.OPCIONES_POR_LISTA` pasa de 7 a 99. Era el valor por defecto de `--max-opciones` y de `configurar()`, todavía con el «tope G36» que G106 refutó: una build lanzada sin la opción habría partido las filas. La partición solo se hace si se pide (test de G36 con `maximo=7`).

## 2. Ids «libres» que eran de Picture Profile (G106-ID, VERIFICADO y corregido)

- Los ids de PP no aparecen como literal: los calcula `libObj` (`0x4a9a56`). El criterio de G56 («sin literal») no los detecta.
- De los 12 ids del hueco `0x1070208…0x1070219`, son parámetros PP:
  - `0x1070212…15` (parámetro 24 de PP1–PP4);
  - `0x1070208/09` (parámetro 21 de PP1/PP2; los usa S&Q, `ID_LIBRES_2`).
- `cfw_ajustes.ID_LIBRES[2..5]` pasan a `0x107020C…0x107020F`, del mismo hueco y fuera de los 341 ids de PP. Los demás índices no cambian.
- Afecta a la fila «Fujifilm Sim» de Film y a los ajustes de Focus Bracket e intervalómetro.
- Test `test_cfw_ajustes.py::test_ids_libres_no_son_de_picture_profile`.
- **Queda:** S&Q (`ID_LIBRES_2`) choca con PP si algún día van juntos; no hay más ids no-PP en el hueco.

## 3. `ZONA_A` y `ZONA_B` del núcleo no son huecos: son tablas a cero (VERIFICADO)

G72 las dio por libres porque estaban a cero en el fichero y en vivo, sin literales absolutos ni `movw/movt`. Pero el núcleo referencia sus datos con desplazamientos relativos al PC (`ldr rX,[pc]; add rX,pc`), y con ese barrido aparecen sus dueños.

**`ZONA_A` (`0x43be3b28…0x43be4330`):**
- Es la tabla T1 de estabilización (módulo `CAMERA_IS`/EIS): 1025 `u16`.
- La lee `0x43705a34`: `i ≤ 0x400 → T1[i]`, con `i` = valor >> 4.
- Le siguen T2 (`0x43be432a`, 513×3 entradas, `0x437059fc`) y T3 (`0x43be4f30`).
- Su lectura multiplica la corrección (`0x43703064`) en un modo EIS (`[obj+0x2c] == 1`).
- La cueva ISO cae en T1[1012…1020]; el código y las celdas de Film, en T1[8…≈0x14e], que además cambian en marcha.

**`ZONA_B` (`0x43c1ff24…0x43c20c8c`):**
- Son dos tablas `s16` de 6×13×11 (1716 B cada una: `0x43c1ff22`, `0x43c205d6`) con sus ejes, descritas en `0x438f6fa4` (dimensiones 1, 6, 13, 11).
- Las usa el procesado YC de captura `BOKS` (`job_YC_SetCapBoks`, interpolación `0x43881290`).
- La tabla EXIF de ISO pisa las entradas 1–96 de la primera; las tablas LUT de G73 y la cueva S&Q también están aquí.

**Efecto:**
- En fábrica, las tablas valen 0 y el resultado es nulo. Con el CFW, la estabilización en ese modo y el YC de captura reciben valores basura.
- No explica un bucle de arranque: la ruta EIS depende del modo y BOKS es de captura.

**El hueco G18 sí está libre:** 0 referencias relativas al PC ni `adr`. Libre en todas las builds: `0x43fb7990…0x43fb7c00`.

**Arreglo pendiente (ZONA-1):** reubicar ISO, Film, LUT, HLG y S&Q. En G18 no cabe todo con PP; hace falta un rediseño (datos con `malloc` y solo código en G18).

## 4. ISO: el arnés con la NVRAM del usuario arranca (MEDIDO)

- Arnés rehecho (`setup.sh` con el volcado `20261122-lutsd385b`) con el `/usr` de la build `iso` y su av-cam (`--avcam-de`, perfil `iso393nv1122`).
- Llega a la pantalla de disparo (ISO 1000), sin fallos en la consola ni en la traza del núcleo.
- **Límite:** el av-cam del arnés solo hace el arranque; la exposición automática la emite `ae.py`, así que la ruta ISO → Sv del núcleo no corre.

**Descartado en estático:**
- La cueva ISO→Sv es equivalente a la de fábrica para los códigos que existen (≤ `0x2c`; MFNR `0x3a…`).
- `isInhOn` está bien: la función hace `subs r1,#1` al entrar.
- `image_cmn_169.uxc`: las 5947 imágenes originales conservan sus datos y es el mismo fichero que el 3.92.
- El bloque 0 restaurado de `nflasha15` solo cambia contadores (`build_nflasha15` lo comprueba con `assert`).

**Sigue abierto:** la causa del bucle. Lo que falta por ejercitar es lo que solo hace el hardware: la exposición automática real con la cueva ISO, y la NVRAM actual, que no es la del 22-11.

## 5. Builds reconstruidas (3.93; `audit_package_nflasha15 --darwin-v3 --sin-wbi --bionz-g22` = `todo_ok`)

| Build | Cambio | `.dat` sha256 |
|---|---|---|
| `pp` | §1: validador ampliado, B&W/S-Gamut fuera de los centinelas | `a5054e6f220ba96b32c201d825c51f08c212ba55ea2a0faea70f0c1e0c527264` |
| `film` | §2: «Fujifilm Sim» en `0x107020C` | `ae3c6babd323c83c8336e6c08468edd3db9e7e1a33686ebcd99b7c747bf929fc` |
| `film_ui` | §2 | `606331ed53b1aea97bf1d05913fa88687b55f78bb03b0cefebcfa70ba097aeaf` |

`exfine`, `iso`, `iso_ui`, `iso_nucleo` y `film_nucleo` no cambian (G106 §5).
