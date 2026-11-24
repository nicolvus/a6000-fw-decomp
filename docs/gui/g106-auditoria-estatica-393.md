# G106 — Auditoría estática de los fallos de las builds 3.93 (24-11-2026)

Fallos vistos por el usuario en la cámara con las builds por función de [G105](g105-builds-por-funcion.md):

| Build | Fallo |
|---|---|
| `pp` | el selector de perfil no llega a PP7–PP10 |
| `film` | botones «pegados» (p. ej. el obturador); el usuario cree que no cargaban todos los looks |
| `exfine` | con Calidad «Extra fine»: «sin espacio en la tarjeta» y cuelgue |
| `iso` | bucle de reinicios al arrancar |

Por orden del usuario, todo el análisis es estático: no se usó la cámara salvo las tres respuestas suyas de §1.

## 1. Picture Profile: no hay tope de 7; falla la confirmación con S-Gamut

**Datos de la cámara (usuario, build `pp`):**
- «Black Level» recorre los 31 valores (−15…+15) y el valor se guarda.
- La lista muestra 6 filas y se desplaza.
- En el menú y en la lista Fn se ven PP7–PP10. Al elegir PP7, la cámara muestra PP6 (el último perfil elegido).
- Con PP1, Gamma = S-Log2 se queda.
- Color Mode = S-Gamut se mantiene hasta pasar por la reproducción; después vuelve al valor anterior.

**Conclusión: la lista vertical no tiene tope.** Se refuta G36 §2: el «tope de 7» venía solo del selector PP y no de la clase Normal. G102 §1 acertaba.
- Por eso no se parte ninguna fila: Film sigue con una fila por marca y PP con filas enteras (petición del usuario).

**Patrón observado:**
- `ppinit` (G35) carga PP7–PP10 con S-Log2/S-Log3 y Color Mode S-Gamut, S-Gamut3.Cine o S-Gamut3 (`pp_factory.PERFILES`).
- PP1–PP6 no llevan ningún S-Gamut. PP4 lleva ITU709(800%) y funciona.

**Verificado en bytes del `libObj` del paquete `pp`:**
- Con valores 0–11, `App2Obj` acepta Color Mode y Gamma (Unicorn).
- `Obj2App`, parcheado por `patch_libobj_pp.patch_color`, devuelve 8–11 para B&W y los S-Gamut, y para Gamma convierte 0x585/0x480/0x481.
- Los 7 límites «perfil ≤ 10» y los tres ganchos de `patch_libobj_ppeco` están aplicados.
- `pvt_ActionSetPictureProfile` (`0x4c0a78`) no aborta por los valores del perfil: el segundo bucle reescribe las 31 banderas.
- Solo guarda `[this+0x274]` (lo que lee el menú) si `0x4bcc54`, el envío de la secuencia, devuelve 0.
- `pvt_ActionSetPictureProfileCmp` (`0x4b7230`, respuesta 0x75af del núcleo):
  - escribe en NVRAM cada parámetro cuyo `Obj2App` funcione;
  - omite los que fallan;
  - escribe siempre el perfil actual (`[this+0xf8c]`).
- Elementos NVRAM de los 11 perfiles (volcado `20261122-lutsd385b`): los 341 existen, con 1 B y `attr = 0`.
- El desempaquetador 0x4066 del núcleo (`0x43802a28`) copia el número de perfil sin comprobarlo.
- El núcleo PP ya admite tipos de color hasta 11 (`0x437aa816`: `cmp #0xa`).

**NO_VERIFICADO (no se cierra en estático):**
- Qué rechaza el envío o la respuesta cuando el perfil o el valor lleva S-Gamut.
- Candidatos:
  - la conversión de la respuesta del núcleo (LIRO → VALUEID de Color Mode, ruta de `CamMsgConv` no localizada);
  - un rechazo del núcleo, que `0x4bcc54` devolviera de forma síncrona.
- Encaja con los dos síntomas:
  - con PP7 no se guarda `[this+0x274]`;
  - con S-Gamut por fila, el eco pinta el valor, pero la NVRAM no lo recibe.
- El arnés no lo reproduce: su av-cam está emulado y no guarda el perfil elegido (perfil `pp7t` con los valores de `ppinit`: ni PP6 se queda).

## 2. Film

**Looks que «no cargaban»:**
- Sin tope en la lista, las filas por marca (15/14/9 looks) son válidas.
- No se halló en estático otra causa. La cadena blob → ACK → LUT/curva es la de G98/G99, cubierta por `tests/test_g97_films.py` (22 verdes).

**Botones pegados, sospecha NO_VERIFICADA:**
- El gancho `maquina` del núcleo (`0x437a2502`) lee el ACK del Backup en cada pasada de la tarea de imagen, también con Film en Off.
- El hilo userland lee 9 ids cada 0,3 s y relee el blob de 16 KB cada 3 s.
- Para aislarlo se hacen dos builds (§5):
  - `film_ui`: menú e hilo, sin capa de núcleo;
  - `film_nucleo`: capa de núcleo sin menú ni hilo; el ACK queda a 0, pero el gancho sigue leyéndolo.

**Hallazgo aparte (VERIFICADO): los «ids libres» de g56 no lo son.**
- `cfw_ajustes.ID_LIBRES[2..5]` (`0x1070212…0x1070215`) son el parámetro 24 (Color Depth G) de PP1–PP4 en el modelo de la A6000 (`modelo.Tablas().pp_ids`).
- En una build con Film y PP a la vez (como el 3.92), la fila «Fujifilm Sim» (`ID_LIBRES[2]` = `0x1070212`) comparte NVRAM con Color Depth G de PP1.
- El ACK (`[8]`) y la lista única (`[9]`) no coinciden con ningún parámetro PP.
- No afecta a las builds de una sola función. Queda en PENDIENTES.

## 3. Extra fine: tamaños EXFINE a 0 en la NVRAM (VERIFICADO) y arreglo

**Causa:**
- En el volcado de la cámara, los BKID `BKID_IMAGING_DATSZ_*_EXFINE_{TGT,MAX}` valen 0. STD y FINE no: JPG M 3:2 STD 2792/4468, FINE 4188/6701.
- `MprCtrlStillMgr::GetStillDataInfo` (`libmprctrl.so 0x17650`) lee el TGT por calidad (índice interno de 3: STD, FINE, EXFINE) con `BackupLib::GetEepData`.
- Con 0, el contador de fotos restantes da 0 y la cámara dice «sin espacio».
- El núcleo lee los mismos BKID: tabla de ids del Backup en `0x43ffae24…`.

**Arreglo (`scripts/gui/exfine_size_patch.py`):**
- Gancho en `0x17742`, tras leer el TGT.
- Si la calidad es EXFINE (argumento de pila `[r7+0x48]` = 2) y el TGT es 0:
  - TGT = TGT_FINE × 3/2 y MAX = MAX_FINE × 2;
  - los guarda con `BackupLib::SetEepData`, para que el núcleo vea lo mismo. Solo se escribe lo que valía 0.
- Ids, comprobados en las 43 entradas EXFINE de las tres tablas: TGT_FINE = TGT + 2, MAX_FINE = TGT + 1, MAX = TGT − 1.
- El código va en la cola a cero del primer `PT_LOAD` (`0x31bd0…`), que se amplía.

**Pruebas:**
- `tests/test_g106_exfine_size.py` (2): la relación de ids, y el gancho emulado con Unicorn.
  - Con EXFINE y TGT 0, deriva y guarda 6282/13402 para JPG M 3:2.
  - Con FINE o TGT ≠ 0, no toca nada.
  - El parche es idempotente.
- La build `exfine` lleva ahora `lib/libmprctrl.so` parcheado.

**INFERENCIA:** los factores 3/2 (TGT) y 2 (MAX, margen por si el codificador lo usa como tope de búfer) no salen de Sony.

**Sin verificar en cámara:** que el disparo en Extra fine ya no se cuelgue y el tamaño real del JPEG.

## 4. ISO: bucle de reinicios

- **La capa ISO del núcleo es idéntica byte a byte** sobre Silent y sobre PP+Film, la del 3.92 que arrancaba: 52 tramos, mismos bytes.
  - Las zonas libres A y B están a cero en todos los núcleos base.
- En el arnés, la build `iso` con su propio av-cam arranca la interfaz completa.
  - Pero el arnés no ejecuta el núcleo de imagen y usa una NVRAM distinta de la del usuario.
- Sin causa estática.
- Hipótesis NO_VERIFICADA: valores ISO o ISO AUTO ampliados guardados en la NVRAM, usados en el arranque por una ruta del núcleo que la capa no engancha (solo engancha ajuste → Sv y la tabla EXIF).
- Para aislarlo: `iso_ui` (interfaz sin núcleo) e `iso_nucleo` (núcleo sin interfaz).

## 5. Builds nuevas (todas 3.93, base Silent, `build_cfw_film.py --funciones`)

`BISECCION` añade `film_ui`, `film_nucleo`, `iso_ui` e `iso_nucleo`; `film` = `film_ui` + `film_nucleo` e `iso` = `iso_ui` + `iso_nucleo`.

| Build | Qué lleva | `.dat` sha256 |
|---|---|---|
| `exfine` | Silent + «Extra fine» en Calidad + `libmprctrl` con tamaños EXFINE (§3) | `bec11dc52810574d2e965357c7c385bd2fdc247830ce85723ff021902028dac5` |
| `film_ui` | Silent + menú Film Simulation, Fn, rueda e hilo userland; núcleo sin capa Film | `7a4e3a74ced5d814db8c1d0d493ece7a927871f139317329d96051b87d0bf6fd` |
| `film_nucleo` | Silent + capa Film del núcleo; sin menú ni hilo (ACK a 0) | `757a8adc35b207d499bdc330b0c4387f99d88a538db16b5242f308575095e5a4` |
| `iso_ui` | Silent + pantalla ISO, `WrapperIso`, `libObj`, textos e iconos; núcleo sin capa ISO | `fe589c1a1a6ba91bf37acab8a66423f3f2ded1bd7ff838000685ba9dcb49e914` |
| `iso_nucleo` | Silent + capa ISO del núcleo; sin interfaz ISO | `86040977296dc08c6116be4244b13267f4638afcd4a374253b4ed07a50073150` |

**Comprobaciones:**
- Las cinco pasan la auditoría independiente `--darwin-v3 --sin-wbi --bionz-g22` (`todo_ok`).
- Tests: G97, G103, G105, G106 → 28 verdes.

**Orden sugerido en cámara:**
1. `exfine`: Extra fine y contador de fotos.
2. `iso_ui` e `iso_nucleo`: cuál reinicia.
3. `film_ui` y `film_nucleo`: cuál deja los botones pegados.
