# G36 — El selector PP del 3.77 no pasa de PP6: tope de 7 opciones por lista (auditoría, 11-11-2026)

Síntoma (usuario, CFW 3.77 en cámara): en la fila «Picture Profile» el cursor no pasa de PP6: al pulsar hacia PP7–PP10 se queda en PP6. La lista tiene 11 opciones (Off, PP1–PP10) y PP6 es la **7.ª**.

## 1. Descartado: la cadena del modelo (`libObj`) acepta PP7–PP10 (VERIFICADO, estático + Unicorn)

Comprobado sobre la `libObj.so` del paquete 3.77 (`analysis/gui/g22/pkg-377w/files/lib/libObj.so`):

| Eslabón | Comprobación | Resultado |
|---|---|---|
| Límite de perfil | `pvt_ActionSetPictureProfile` (`0x4c0a78`): `cmp r8,#0xa; bls` en `0x4c0ae0`/`0x4c0b08` | admite 0–10 |
| Elementos de NVRAM por perfil | constructor `0x4a9a56` emulado: `[this+0x5dc+(p·31+i)·4]` → perfiles 0–3 en `0x10702f8+p…`, 4–9 en `0x107062b+(p−4)…`, PP10 en `0x1070631…`; contrastados con el volcado `20261105-volcado-total-nvram` (`pmca.backup`) | los 11 bloques existen, 1 B, `attr = 0` (escribibles) |
| Valores de fábrica de PP7–PP10 (`pp_factory`) → VALUEID | `App2Obj` (`0x4b46b8`) emulado: Gamma y Color Mode | acepta 0–11 en ambos (S-Log2/3, S-Gamut, S-Gamut3(.Cine)) |
| `CamMsgConv` del mensaje `0x75ae` (`0x9b3200`) | emulado con los 31 parámetros de cada perfil 0–10 | mismo resultado en los 11 perfiles: Color (`0x9673`) y Gamma (`0x967a`) convierten sin error |
| Tablas parcheadas | `0x9b3274` (Color, 12 VALUEID) y `0x9b36f4` (Gamma, 12) | correctas |

Nada en la ruta del modelo distingue PP6 de PP7: el fallo no está en `libObj` ni en la NVRAM.

## 2. Causa: la lista de opciones de la UI no pasa de la 7.ª (VERIFICADO en cámara + estructura)

- **Cámara (usuario):** el cursor se detiene en la 7.ª opción (PP6) de una lista de 11.
- **Estructura (`viewUnified2.so` fw 3.21 + `analysis/gui/settings-sweep.json`):** todos los pids nuevos del PP usan la clase **Normal** (caso de factoría 0 en `ELEM_VU2` `0x3A5E1C`, la de `REF_NORMAL = 0x12`). En el firmware de Sony esa clase la usan **67 ajustes y ninguno pasa de 5 opciones**; todos los ajustes con más de 7 (Drive Mode 32, ISO 48, Language 33, Zebra 9, Phase Detection AF 8…) tienen **clase propia**. La lista de la clase Normal nunca se ejercita por encima de 7 en el firmware original.
- Coincide con el tope de 6 filas por página del menú (G29 §6): la UI de la A6000 no desplaza estas listas.

## 3. Alcance en el 3.77 (25 de 34 filas tienen más de 7 opciones)

Con el tope de 7, solo se alcanzan las 7 primeras opciones de cada fila:

| Fila | Opciones | Última alcanzable | Inalcanzable |
|---|---|---|---|
| Picture Profile | 11 | PP6 | PP7–PP10 |
| Copy / Reset | 10 | PP7 | PP8–PP10 |
| Gamma | 10 | ITU709 | ITU709(800%), S-Log2, S-Log3 |
| Color Mode | 9 | S-Gamut | S-Gamut3.Cine, S-Gamut3 |
| Black Level | 31 | −9 | −8…+15 |
| Black Gamma Level, Color Phase, Color Depth ×6, Detail Level | 15 | −1 | 0…+7 |
| Saturation | 16 | −2 | −1…+7 |
| WB LB/CC/R/B | 19 | −3 | −2…+9 |
| Knee Point / Knee Slope | 13 / 11 | 6 / +1 | 7–12 / +2…+5 |
| Detail Limit, Detail Crispening, Color Mode Level | 8 | 6 / 6 / 7 | 7 / 7 / 8 |

Consecuencias que explica: (a) PP7–PP10 no se eligen (este informe); (b) **S-Log2/S-Log3 «sin diferencia visible»** desde el 3.67 (G30-C, G32-C): por la fila Gamma no se pueden elegir (posiciones 9–10); (c) en los ajustes centrados en 0 el valor neutro y los positivos son inalcanzables: puede explicar parte de G33-A («no hacen nada visible, salvo Saturación»).

## 4. Arreglo (opciones consideradas; elegida la 1)

1. **Partir cada fila en grupos de ≤ 7 opciones** con la misma clave (p. ej. «Picture Profile», «Picture Profile 7-10»; «Black Level −15…−9», …): 34 → 76 filas, 13 páginas de 6. Mínimo y dentro del comportamiento comprobado; queda sin probar cómo pinta una fila el valor actual cuando no está entre sus opciones.
2. **Menos opciones por ajuste numérico** (pasos de 2, rango recortado): pocas filas, pierde resolución.
3. **Clase con desplazamiento** (reutilizar la de un ajuste de Sony con lista larga): sin las filas extra, pero cada clase lleva su propia lógica de modelo; requiere RE de la vista y es lo de mayor riesgo.

No verificado: el mecanismo exacto del tope dentro de la vista (no localizado en el código); que el tope sea 7 en las filas numéricas (deducido; comprobable abriendo Black Level y viendo si el cursor para en −9).

## 5. CFW 3.78: filas partidas en grupos de ≤ 7 (construido, sin instalar)

Elegida la opción 1 (usuario). `build_pp_menu.partir()` (lo llama `configurar`, después de las opciones S-Log/S-Gamut/Copy/Reset) parte cada ajuste de más de
`pp_menu_spec.OPCIONES_POR_LISTA = 7` opciones en filas **equilibradas** con la misma clave, evento y lectura; la etiqueta indica el tramo («Black Level -15/-10»).
Resultado: **76 filas en 13 páginas de 6**, pids `0xE9…0x134`; `pid_space.PID_MAX` sube de `0x110` a `0x140` (`0xA0 << 1`, inmediato válido de `cmp.w`).

| Ajuste | Filas |
|---|---|
| Picture Profile | `Off/PP4`, `PP5/PP10` |
| Copy, Reset | `PP1/PP5`, `PP6/PP10` |
| Gamma | `Movie/Cine3`, `Cine4/S-Log3` |
| Color Mode | `Movie/Pro`, `ITU709 Matrix/S-Gamut3` |
| Black Level | 5 filas de 6–7 valores |
| 15 valores (BG Level, Phase, Color Depth ×6, Detail Level) / 16 (Saturation) / 19 (WB) | 3 filas cada uno |
| Knee Point (13), Knee Slope (11), 8 valores (Detail Limit/Crispening, Color Mode Level) | 2 filas cada uno |

Paquete `analysis/gui/g22/pkg-378w/pkg-3.78/package-3.78/firmware_packed.dat`, sha256 `33a4dc68e2963680559a6d2fde242add912e9cc46a199366b7b00e8a9d62a010`.
Frente al 3.77 solo cambian `viewUnified2.so`, `CautionConfig.so` y los textos (`libObj.so` y `base-pp.tar`/`nflasha3` idénticos, sha256 comparados).
Pruebas: `tests/test_g2*.py tests/test_g3*.py` 106 pasan (nueva `test_g36_ninguna_fila_pasa_de_7_opciones_y_se_conservan_todas`). Auditoría independiente
(`analysis/gui/g22/audit-3.78.json`): 22/24, los mismos dos fallos esperados y el mismo aviso de `fsck` (contadores de bloques libres) que el 3.76 instalado.

NO verificado (cámara): qué muestra cada fila cuando el valor actual pertenece a la otra fila del mismo ajuste (puede quedar sin marca o marcar la 1.ª opción);
que el tope sea también 7 en las filas numéricas (se cubre igualmente al partir).

## 6. Instalación (11-11-2026, MEDIDO; autorizada por el usuario: «Sí, instálalo»)

`pmca-console firmware --flash --confirm …/package-3.78/firmware_packed.dat`: primer intento «unexpected response (device returned more data than requested)» al pasar
a modo actualizador (`054c:03e2`), como en el 3.76; segundo, con la cámara ya en ese modo, `Done`. Arranca normal (`054c:07c4`) y `pmca-console info` da **firmware 3.78**.
Registros `analysis/gui/g22/install-3.78.log` y `install-3.78b.log`. Falta la prueba funcional del menú (PP7–PP10, S-Log2/S-Log3, valores positivos).

## 7. El 3.78 se cuelga al entrar en Picture Profile (usuario, 11-11-2026)

Sin red ni registros de la cámara: causa NO determinada. Respecto al 3.77 (entra bien) solo cambian dos cosas fuera de lo probado:
- **13 páginas** en la carpeta (3.77: 6). En el firmware de Sony las carpetas propias tienen ≤ 2 páginas y los nodos de `_INIT_70` (`viewUnified2.so`,
  407 llamadas a `CmnViewSettingNode(…, n, …)`) usan n ≤ 8 salvo uno de 16: no hay ninguna carpeta con más de 8 hijos de este tipo. Hipótesis principal.
- **pids hasta `0x134`** (3.77: hasta `0x10A`, ya > `0xFF`); las tres comprobaciones de pid están parcheadas (`pid_space`), y la búsqueda de otros topes
  `0xE8/0xE9` en el código no da un consumidor claro. Hipótesis secundaria.
`libObj.so`, `nflasha3` y los textos (163 ranuras libres asignadas) no explican un cuelgue al abrir la carpeta. Reversión: reinstalar el 3.77 (`pkg-377w`).

## 8. CFW 3.79: ≤ 7 opciones y ≤ 6 páginas (construido, sin instalar)

Elegido por el usuario («6 págs, sin Copy/Reset»). `build_pp_menu.partir()` ahora: quita Copy y Reset del menú (la `libObj` sigue igual: `ppinit` ya carga los
valores de fábrica); reduce cada ajuste **numérico** de más de 7 valores a 7 repartidos por todo el rango con los extremos (`_reducir`; si falta el neutro de
`pp_factory.NEUTRO`, sustituye al más cercano); y parte en dos filas los enumerados largos. `PID_MAX` vuelve a `0x110`.

| Fila | Valores |
|---|---|
| Picture Profile | `Off/PP4` (Off, PP1–PP4) · `PP5/PP10` (PP5–PP10) |
| Gamma | `Movie/Cine3` · `Cine4/S-Log3` (Cine4, ITU709, ITU709(800%), S-Log2, S-Log3) |
| Color Mode | `Movie/Pro` · `ITU709 Matrix/S-Gamut3` (ITU709 Matrix, B&W, S-Gamut, S-Gamut3.Cine, S-Gamut3) |
| Black Level | −15, −10, −5, 0, +5, +10, +15 |
| ±7 (BG Level, Phase, Color Depth ×6, Detail Level) | −7, −5, −2, 0, +2, +5, +7 |
| WB LB/CC/R/B | −9, −6, −3, 0, +3, +6, +9 |
| Saturation | −8, −6, −3, 0, +2, +4, +7 |
| Knee Point / Knee Slope | 0–12 de 2 en 2 / −5, −3, −2, 0, +2, +3, +5 |
| Color Mode Level / Detail Limit / Crispening | 1, 2, 4–8 / 0, 1, 2, 4–7 / 0, 1, 2, 4–7 |

**35 filas, 6 páginas, pids `0xE9…0x10B`** (3.77: 34 filas, 6 páginas, hasta `0x10A`). `.dat` `analysis/gui/g22/pkg-379w/pkg-3.79/package-3.79/firmware_packed.dat`,
sha256 `04b414c90dba6fb4d01ba0d162ac4bdb0931c8c29e5d14dec6e32799eaf44a67`; `libObj.so` y `base-pp.tar` idénticos al 3.77. 106 pruebas (la de G36 reescrita);
auditoría 22/24 con los mismos fallos esperados y aviso de `fsck` que el 3.76/3.78. Sin probar en cámara.
