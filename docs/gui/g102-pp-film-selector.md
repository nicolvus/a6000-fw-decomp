# G102 — Picture Profile en el CFW Film: cada ajuste en una sola fila con todas sus opciones, Film Simulation por marca y listas en el menú Fn y la rueda (23-11-2026; código y tests, CFW sin construir)

Petición: activar el menú PP en el CFW Film y mejorar la selección de perfiles, modos y valores. La del 3.77/3.78 era mala.
El usuario lo concretó: **sin filas partidas**, «Picture Profile» de Off a PP10 en una sola categoría.
También pidió que la carpeta «Film» pase a llamarse «Film Simulation», con una fila por marca y todos sus estilos dentro, y que no se construya todavía el CFW.
Código:
- `scripts/gui/build_cfw_film.py --pp` (`--max-opciones`, 99 por defecto);
- `build_pp_menu.configurar(fn_pp=True, maximo=…)` y `pp_menu_spec.FN_COMPLETOS`/`PARTES`;
- generalizados `fn_lut_menu`, `fn_lut_listas` y `rueda_film`.

Tests: `tests/test_g102_pp_film.py`. Sin cámara.

## 1. El «tope de 7 opciones» no está en la interfaz (MEDIDO en el arnés)
- **Antes:** G36 dedujo, por lo visto en la cámara con el 3.77 (el cursor se quedaba en PP6), que la lista vertical de la clase Normal no pasaba de la 7.ª opción.
  Por eso el 3.78 y el 3.79 partían las filas: «Off/PP4», «PP5/PP10», «Black Level −15/−10»…
- **Medido en el arnés G22** (`im.elf` 3.21 con el `/usr` y el `av-cam` del propio `.dat`, perfil `g102j`), con filas enteras:
  - «Picture Profile» abre la lista Off…PP10 y el cursor baja hasta **PP10**; la lista se desplaza con 6 visibles y barra lateral.
  - «Gamma» (10 opciones) y «Black Level» (31) **dan la vuelta**: 12 pulsaciones acaban en Cine1 y 32 en −14, o sea que se recorren enteras.
  - Capturas en el directorio temporal de la sesión, no guardadas en el repositorio.
- **La interfaz no tiene tope.** Los métodos de la clase Normal (`cmn_view_processDataMgr.so`: `isValueDisable`/`isValueGrayedOut` devuelven 0) tampoco limitan nada.
  - Lo visto en la cámara con el 3.77 queda **sin explicar**: NO_VERIFICADO, quizá un lado del modelo que el arnés no reproduce.
  - Si la cámara volviera a pararse en la 7.ª, las mismas listas completas están también en el menú Fn y en la rueda (§2).

## 2. Qué llevará el 3.92 (`build_cfw_film.py SALIDA --version 3.92 --pp`, sin construir)
**Menú «Picture Profile»:** 32 filas en 6 páginas de 6, una por ajuste, cada una con todas sus opciones; sin Copy/Reset.
- **Picture Profile:** Off, PP1–PP10.
- **Gamma:** Movie, Still, Cine1–Cine4, ITU709, ITU709(800%), S-Log2, S-Log3.
- **Color Mode:** Movie, Still, Cinema, Pro, ITU709 Matrix, Black & White, S-Gamut, S-Gamut3.Cine, S-Gamut3.
- **Valores numéricos:** rango completo del validador: Black Level −15…+15, ±7, WB ±9, Saturation −8…+7, Knee Point 0–12, etc.

Con `--max-opciones 7` se vuelve al modo partido, ahora con grupos con nombre («Gamma» / «Gamma Log», «Picture Profile 7-10»).

**Carpeta «Film Simulation»** (antes «Film»): una fila por marca con Off + todos sus estilos.
- **Kodak:** 15 estilos.
- **Fujifilm:** 14 estilos.
- **Fujifilm Sim:** 9 estilos.

Sustituye a las 8 filas «Kodak 1…Fuji Sim 2». La numeración de los 38 looks, las recetas y los blobs no cambian (`film_userland.FILAS`).
La lista única del menú Fn y de la rueda se llama también «Film Simulation».

**Menú Fn:** las mismas listas en franja horizontal, asignables a cualquiera de las 12 casillas:
- Film Simulation (39);
- Picture Profile, Gamma, Color Mode;
- Black Level, Black Gamma Level, Saturation, Color Phase, Detail Level y Knee Point.

Cada nodo Fn usa el mismo ajuste (pid) que su fila del menú.

**Rueda de control:** ISO, Balance, Estilo creativo, Efecto, **Film Simulation** (9), **Picture Profile** (10), No definido.

**Núcleo y `libObj`:** los del 3.81 debajo de Film y del Silent calibrado:
- curvas S-Log2, S-Log3 e ITU709(800%);
- S-Gamut3 y S-Gamut3.Cine, B&W y Hi-Light;
- tono Black/Knee/Detail;
- `libObj` con Gamma y Color ampliados y eco PP.

PP y Film no comparten ningún byte del núcleo (0 bytes en común entre sus diferencias).

## 3. Mecanismo (generalización de G86/G100/G101)
- **`viewUnified4.so`:**
  - el `tbh` del despachador Fn tenía 10 valores sin uso (`0x1a–0x1f`, `0x23`, `0x26–0x28`);
  - los 18 bloques contiguos de 8 B (`0xdd0fe…0xdd18e`) pasan a 4 B más un cuerpo común, y caben 16 nuevos;
  - el valor k-ésimo lleva al hijo 39 + k (SRNum `0x27 + k`); la raíz Fn pasa de 38 a 48 hijos.
- **`CautionConfig.so` / `viewUnified2.so`:**
  - en las 12 listas de asignación hay 10 opciones nuevas antes de «No definido»;
  - usan ids `0xf` que el A6000 no usa: ShootMode y 20–26, 32–34 en la ranura 1, +1 en las demás;
  - en las 12 tablas opción→valor esos ids pasan a valer los 10 valores nuevos.
- **Rueda:** la cueva de G101 compara con cada valor (9, 10) y carga su nodo. El pid `0xdc` pasa a 7 opciones con la tabla `[8, 0xb, 0xd, 0xe, 0, 9, 10]`.

## 4. Pruebas
- **Unicorn y estático** (`tests/test_g102_pp_film.py`):
  - **Spec:** una fila por ajuste con todas las opciones, ≤ 6 páginas y nodos Fn sobre los mismos ajustes. En modo tope 7, grupos con nombre y copias completas.
  - **Despachador con 10 hijos:** los valores nuevos dan SRNum `0x27…0x30` y los 38 originales no cambian. Ninguna opción del A6000 usa los ids libres.
  - **Rueda con dos valores, en las tres vistas:** 9 y 10 cargan su nodo; los demás valores dan lo mismo que el original.
  - **Ficheros del 3.92:**
    - los 10 hijos Fn llevan al pid y a la lista de valores esperados, con sus textos;
    - las 12 ranuras ofrecen las 10 opciones con su valor;
    - la rueda lista Film y Picture Profile y lleva a los hijos 39 y 40.
  - **Auditoría de modos:**
    - cada valor de cada fila del menú PP pasa el validador `App2Obj` de la `libObj` del paquete;
    - el selector no pasa de 10.
- **Regresión:** PP (G22–G38), Fn (G86/G87), Film (G97, adaptados a las filas por marca) y rueda (G101).
- **Paquete:**
  - el primer 3.92 (menú partido) pasó la auditoría `--darwin-v3 --sin-wbi --bionz-g22` 29/29;
  - `audit_package_nflasha15` reconoce el núcleo `build_cfw_film.bionz_pp`.
- **Pendiente:** el 3.92 definitivo no está construido, a petición del usuario. Las pruebas sobre ficheros del paquete se saltan hasta construirlo.
- **Arnés (3.92 con filas enteras y la carpeta Film anterior):**
  - la carpeta «Picture Profile» abre sin cuelgue, con 6 páginas;
  - las listas largas se recorren (§1);
  - la carpeta «Film» abre;
  - el panel Fn abre.
- **Límites del arnés:**
  - Elegir un perfil no se queda: vuelve a Off y no sale ninguna orden hacia `av-cam`. Las órdenes de modelo repetidas fallan en el arnés (G75 T1/T38), así que no se ha podido medir allí la escritura.
  - En la cámara (3.73–3.77) el selector sí escribía.
  - No se ha navegado en el arnés la asignación de la rueda ni la de las casillas Fn. Solo está comprobada en Unicorn.
