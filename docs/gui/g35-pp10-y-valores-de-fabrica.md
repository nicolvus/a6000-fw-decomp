# G35 — PP10 y valores de fábrica por perfil (CFW 3.75, construido, sin instalar) (11-11-2026)

Continúa [G34](g34-auditoria-estatica-pp-nucleo.md). **Solo estática + Unicorn**: nada probado en cámara ni instalado. Código: `scripts/gui/patch_libobj_ppeco.py` (ganchos y límites), `scripts/gui/pp_factory.py` (tabla), `scripts/gui/pp_menu_spec.py` (PP10 en el selector, Copy y Reset), `tests/test_g30_libobj_ppeco.py` (+5 pruebas), `tests/test_g23_pp_menu.py`.

## 1. Hallazgos en `libObj.so` (VERIFICADO con bytes)

- El objeto de modelo guarda, para cada parámetro de cada perfil, un **identificador de elemento de NVRAM** (no el valor): `[this+0x5dc + (perfil·31 + i)·4]` = perfiles «actuales» 0–9, y a continuación `[this+0xab4 + …]` = otros 10 bloques de elementos de «valores por defecto», y en `0xf8c` el elemento del perfil actual. `0x5dc + 10·0x7c = 0xab4`: **un perfil 10 sale gratis**: sus 31 elementos son los del primer bloque de «defaults».
- `pvt_ActionSetPictureProfile` (`0x4c0a78`), Copy (`0x4b4140`), el proceso de confirmación (`0x4b73a0`), la lectura `getModelInfo 0x4a` (`0x4a7820`) y Reset (`0x4c0e14`) limitan el perfil a ≤ 9. La A6300 usa el 9 como bloque neutro de «Off».
- `Reset` leía el elemento «default» de cada parámetro y lo escribía en el actual, **sobre el perfil actual de la NVRAM (`0xf8c`)**, que esta CFW no actualiza (G30): el perfil elegido en el menú vive en `[this+0x274]`.

## 2. Qué se hizo

| Cambio | Detalle |
|---|---|
| Límites ≤ 9 → ≤ 10 | 5 bytes en `0x4a7860`, `0x4b4184`, `0x4b73de`, `0x4c0ae0`, `0x4c0b08`; el gancho del selector (`cmp #10`) |
| **PP10** | menú: Off (9), PP1–PP9 (0–8), **PP10 (10)**, también en Copy y Reset. Almacenamiento = los 31 elementos que eran los «defaults» del PP1 |
| **Valores de fábrica desde el primer arranque** | `ppinit` (cueva de `libObj`, se llama desde la lectura `getModelInfo 0x4a`, la del selector): si el elemento-marca (bloque 1 de «defaults», `this+0xab4+0x7c`, ya sin uso) no vale `0x5A`, escribe la marca y después los 341 valores de `pp_factory.tabla()` en los elementos de NVRAM de los 11 perfiles. Una sola vez (la marca queda en NVRAM) y una vez por arranque (bandera en RAM; el segmento de la cueva pasa a RWX). Si la lectura o la escritura de la marca fallan, no toca nada y reintenta en la siguiente llamada |
| Reset con valores de fábrica | gancho en `0x4c0e62`: usa el perfil elegido en el menú (`[this+0x274]` ≤ 10) y, si no, el de la NVRAM; gancho en `0x4c0ea2`: en vez de leer el elemento «default» escribe el valor de `pp_factory.tabla()` (11 perfiles × 31 palabras) |

**Reset** no es un botón de un solo valor: su fila deja elegir el PP (PP1…PP10) y restablece ese perfil a los valores de fábrica de la tabla; sigue disponible, pero ya no hace falta para tener los valores iniciales.

Valores de fábrica (`pp_factory.py`; dominio de la app): PP1 Movie/Movie · PP2 Still/Still · PP3 ITU709/ITU709 Matrix · PP4 ITU709(800 %)/ITU709 Matrix · PP5 Cine1/Cinema · PP6 Cine2/Cinema · PP7 y PP8 S-Log2/S-Gamut · PP9 S-Log3/S-Gamut3.Cine · **PP10 S-Log3/S-Gamut3** · bloque «Off» Movie/Movie neutro. Resto de parámetros neutros: nivel de Color Mode 4, Black Gamma Range Middle (nivel 0), Knee automático (Sensibilidad Mid, Max Point 4 = 100 %), Point 6, Detail automático (Limit 7, B/W Type3), todo lo demás 0.

## 3. Pruebas (Unicorn sobre la `libObj` parcheada)

`ppinit`: primer arranque (marca + 341 valores exactos, PP10 con S-Log3), marca ya puesta (nada se toca), fallo de lectura/escritura de la marca (nada se aplica, bandera a 0), segunda llamada (sin trabajo). Límites a 10 (el selector devuelve 10; 11 cae a la NVRAM); Reset elige el perfil del menú; el valor de cada parámetro sale de la tabla; **bucle real de Reset del PP10**: escribe exactamente los 31 valores de fábrica en los elementos `this+0xab4…` y no lee ningún elemento de defaults. `tests/test_g*.py`: 124 pasan. Auditoría independiente del `.dat` (3.75, `faf23dc7…`): 24/25 (el fallo esperado: `nflasha3` cambia por el parche PP).

## 4. Límites y riesgos (NO verificado)

1. **Los valores de fábrica salen de la documentación de Sony recordada de memoria**, no de este firmware (la tabla real está en la NVRAM de fábrica de la cámara): PP8 igual al PP7, nivel de Color Mode 4, Max Point 4, Point 6 son suposiciones. Se ajustan en `pp_factory.py`.
2. La inicialización sobrescribe **una vez** los valores que hubiera en la NVRAM de los 11 perfiles (cualquier ajuste previo del usuario se pierde en ese primer arranque). Las filas del menú pueden mostrar el valor anterior hasta volver a elegir el perfil (leen estados en caché). Si la NVRAM no admite la escritura del elemento-marca, no se aplica nada.
3. No se sabe si los elementos de NVRAM que eran los «defaults» del PP1 son **escribibles** (podrían ser de solo lectura): si no lo fueran, PP10 se aplicaría pero no se conservaría tras apagar.
4. Otras comprobaciones de perfil ≤ 9 fuera de `libObj.so` (vistas, `viewUnified2.so`, NVRAM del backup) no se han buscado.
5. PP10 y el «Off» del selector comparten ahora el rango 0–10 de la API del modelo; «Off» sigue siendo el bloque 9.

## 5. Otros límites ≤ 9 en el 3.80 (auditoría estática, 12-11-2026)

Barrido capstone de `pkg-380w`: `libObj.so`, `viewUnified2.so` y `CautionConfig.so` (las únicas bibliotecas que cambia el CFW). Busca `cmp`/`cmn #9` o `#0xa` a ±40 instrucciones de las claves `0x274…0x276`. En el `/usr` de fábrica (fw3.21, 175 bibliotecas), solo `libObj.so` contiene «PictureProfile».

| Sitio | Qué es | Veredicto |
|---|---|---|
| `libObj` `0x4db4b4` y `0x4db4dc` (`cmp.w r8,#9`, bytes `b8f1090f`) | **`pvt_SetParamParamPictureProfile`** (`0x4db454`; cadenas `targetPpNo`, `Bkup_Read Err1/2`). Lee el perfil de la clave `0x274`; si es > 9, usa el de la NVRAM (`[this+0xf8c]`, que el CFW no actualiza, G30) y, si ese también es > 9, da error. Después lee los 31 elementos `this+0x5dc + pp·0x7c` y los convierte con `ChangeParamApp2Obj` | **Rompe PP10**: con PP10 elegido se envían los parámetros de otro perfil. G35 no lo había parcheado |
| `libObj` `0x9e03c0…0x9e991a` (19 sitios), `0x952ea4`, `0x966c84` | comprobaciones de **rango de id de clave** (`id − 0x21f ≤ 9`) | no tienen que ver con el perfil |
| `libObj` `0x8eb674`; `0x13d858` y `0x596886` (`#0xa`) | `add r1, sp, #0x274` (desplazamiento de pila) / otras claves | no tienen que ver con el perfil |
| `viewUnified2` `0x143fb8`, `0x14674a` (`#0xa`) | árboles `switch` id → clave | no tienen que ver con el perfil |

**Parche propuesto (no construido)**: añadir a `patch_libobj_ppeco.BOUNDS` `(0x4DB4B4, "b8f1090f", "b8f10a0f")` y `(0x4DB4DC, "b8f1090f", "b8f10a0f")`, con la misma codificación que `0x4c0ae0`/`0x4c0b08`. Con 10, `0x5dc + 10·0x7c = 0xab4` lee los elementos de PP10. También hay que ampliar `tests/test_g30_libobj_ppeco.py` con los dos sitios. Va en la integración conjunta (G33-B §10), junto con el resto de `patch_libobj_ppeco`.

NO_VERIFICADO: si `pvt_SetParamParamPictureProfile` es la ruta que envía los parámetros al núcleo al elegir el perfil o una ruta paralela a `pvt_ActionSetPictureProfile` (`0x4c0a78`, ya parcheada). El barrido es heurístico (solo cerca de las claves): un límite que reciba el perfil por argumento, lejos de `0x274`, no aparecería.

