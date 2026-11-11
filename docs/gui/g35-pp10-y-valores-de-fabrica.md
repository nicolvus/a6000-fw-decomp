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
| Reset con valores de fábrica | gancho en `0x4c0e62`: usa el perfil elegido en el menú (`[this+0x274]` ≤ 10) y, si no, el de la NVRAM; gancho en `0x4c0ea2`: en vez de leer el elemento «default» escribe el valor de `pp_factory.tabla()` (11 perfiles × 31 palabras) |

Valores de fábrica (`pp_factory.py`; dominio de la app): PP1 Movie/Movie · PP2 Still/Still · PP3 ITU709/ITU709 Matrix · PP4 ITU709(800 %)/ITU709 Matrix · PP5 Cine1/Cinema · PP6 Cine2/Cinema · PP7 y PP8 S-Log2/S-Gamut · PP9 S-Log3/S-Gamut3.Cine · **PP10 S-Log3/S-Gamut3** · bloque «Off» Movie/Movie neutro. Resto de parámetros neutros: nivel de Color Mode 4, Black Gamma Range Middle (nivel 0), Knee automático (Sensibilidad Mid, Max Point 4 = 100 %), Point 6, Detail automático (Limit 7, B/W Type3), todo lo demás 0.

## 3. Pruebas (Unicorn sobre la `libObj` parcheada)

Límites a 10 (el selector devuelve 10; 11 cae a la NVRAM); Reset elige el perfil del menú; el valor de cada parámetro sale de la tabla; **bucle real de Reset del PP10**: escribe exactamente los 31 valores de fábrica en los elementos `this+0xab4…` y no lee ningún elemento de defaults. `tests/test_g*.py`: 124 pasan. Auditoría independiente del `.dat` (3.75, `ecb977c3…`): 24/25 (el fallo esperado: `nflasha3` cambia por el parche PP).

## 4. Límites y riesgos (NO verificado)

1. **Los valores de fábrica salen de la documentación de Sony recordada de memoria**, no de este firmware (la tabla real está en la NVRAM de fábrica de la cámara): PP8 igual al PP7, nivel de Color Mode 4, Max Point 4, Point 6 son suposiciones. Se ajustan en `pp_factory.py`.
2. **Reset es por perfil** y hay que pulsarlo en cada uno: el NVRAM ya existente no se reescribe solo. No se añadió «restablecer todos».
3. No se sabe si los elementos de NVRAM que eran los «defaults» del PP1 son **escribibles** (podrían ser de solo lectura): si no lo fueran, PP10 se aplicaría pero no se conservaría tras apagar.
4. Otras comprobaciones de perfil ≤ 9 fuera de `libObj.so` (vistas, `viewUnified2.so`, NVRAM del backup) no se han buscado.
5. PP10 y el «Off» del selector comparten ahora el rango 0–10 de la API del modelo; «Off» sigue siendo el bloque 9.
