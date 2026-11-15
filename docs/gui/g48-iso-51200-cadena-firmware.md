# G48 — ISO 51200 (`0x26`): cadena de parches del firmware probada en Unicorn; el tope visible es la lista estática, no el MAX (15-11-2026; PARCIAL, sin CFW, sin cámara)

Continúa [G47](g47-iso-wrapperiso-no-se-carga.md), [G46](g46-iso-getsubnode-no-construye-menu.md), [G42](g42-iso-consumidor.md). Regla del usuario: solo ficheros del `.dat` replicables en la A6000; prueba = Unicorn sobre bytes reales. Sin arnés, sin CFW.

## 1. A — Quién fija 25600 en la cámara real (estático)
* La lista visible (MFNR, AUTO, 100…25600) es `cmnViewSettingNodesISOSensitivityType12`, elegida por `CmnViewSettingNodeISOSensitivity::_getSubNode` (`CautionConfig.so+0x107d7c`) con el tipo de modelo (`0x101c20`, `tbb` 30 casos): **tipo 29 = Type12** (el id 29 está en la máscara `0x61a00002` que G39 ya usaba para la A6000). Decodificado el `tbb`: 1 VG, 2–15/20/22 Default, 16/18/19 Type11, 17 Type10, 21 AmntEntry, 23 Type09, 24 DSCEntry, 25/27/28/30 Emnt, 26 AmntMid, 29 Type12.
* `Default` = 35 filas: MFNR, AUTO, 50…25600, **32000, 40000, 51200**, ISOAUTOMAX_MR, ISOAUTOMIN_MR. Las listas no filtran por MIN/MAX: no hay nada en el firmware que lo haga fuera de `libObj`: el inmediato `0x96ff/0x98a1` solo aparece en `libObj.so` (79 usos) de las 157 `.so` (barrido con `llvm-objdump`). Las vistas (`viewUnified2/4/7`, `cmn_view_processDataMgr`) no leen MIN/MAX de ISO.
* Los nodos de la lista llevan el id de valor en su `PropertyList`: 25600=`0x1d`, 32000=`0x1e`, 40000=`0x1f`, **51200=`0x20`**. Coincide con `CustomIsoSensitivity::getValue` (`+0x68308`): códigos `0x23..0x26` → ids `0x1d..0x20` (cadena `cmp` ya completa hasta `0x26`) y con `setValue` (`+0x68598`, `tbh` ids `0..0x2e`). **El tope `0x26` de `getValue` no bloquea 51200** (G47 lo daba como tope; solo bloquea `0x27..`, o sea ISO-B).
* `mappingValIsoSensitivity` (13 filas, ids `0x22..0x2e` = códigos `0x3a..0x45,0x48`) es de los ISO multi-frame; no hay que tocarla para 51200.
* Cómo cuadra con G45/G46 (el arnés no cambiaba la lista): estático dice que `_getSubNode` sí elige la lista en la cámara; si en el arnés `0x101c20` falla, la función sale sin fijar lista (`cmp r0,#0; bne` a `0x107e2e`) y la lista viene de otro sitio. No medido; la verificación en cámara lo decide.

## 2. B — Parches (ambos en `.dat`, con test de bytes originales e idempotencia)
1. `scripts/gui/iso_list_patch.py` (G43, ya existía): caso 29 Type12 → Default, 8 B en `CautionConfig.so`. Suficiente para mostrar 32000/40000/51200 (y 50/64/80, que la A6000 podría no admitir: **riesgo**, ver §4).
2. `scripts/gui/iso_max_patch.py --51200` (nuevo): variante del parche de `libObj+0x4db86e` que fuerza el MAX de ISO `0x23..0x28` → `0x26` (antes solo `0x26..0x28` → `0x29`, que con `getIso` ≤ `0x26` rompe). El parche sin flag sigue siendo el de G42 (102400). Hace falta solo si `libObj` recorta el ISO a `PARAMID_ISO_SPEED_RATE_MAX` (no demostrado; en MFNR `av-cam` ya envía `0x26`). Si no recorta, es inocuo.
* `wrapperIso::getIso` ya admite hasta `0x26`: no hay que parchearlo para 51200.

## 3. C — Pruebas Unicorn (`tests/test_iso_51200_unicorn.py`, 7 casos verdes + los 4 previos)
* libObj `NEW51`: para los 75 códigos `0..0x4a`, `0x23..0x28` → `0x26`, el resto intacto; bytes originales validados e idempotente.
* `getValue` (cadena real `0x6839c..0x6850e`): `0x23→0x1d`, `0x24→0x1e`, `0x25→0x1f`, `0x26→0x20` con éxito; `0x27` → «sin valor» (límite ISO-B).
* `_getSubNode` real con el parche de lista (tipo de modelo 29 inyectado en `0x107d94`, GOT/ABS32 resueltos): `n=35`, filas `…, 25600, 32000, 40000, 51200, ISOAUTOMAX_MR, ISOAUTOMIN_MR`.
* No probado: `blx` externos de `getValue` completo (aislamos solo la cadena de decisión), ni `setValue`/`av-cam` reales.

## 4. D — 102400 (`0x27..0x29`), no hecho; lo que falta
1. `getValue`: añadir `0x27..0x29` → ids `0x21..0x23` choca con los ids `0x22..0x2e` ya usados por la tabla multi-frame (`mappingValIsoSensitivity`): hay que elegir ids libres (p. ej. > `0x2e`) y ampliar `getValue`, `setValue` (`tbh` hasta `0x2e`) y `convertProcValToModelVal` (`+0x68540`, `0x22..0x2e`).
2. `wrapperIso`: `getIso` (`+0x1cb0`; cadenas de G42 §2), `setIso` y `convertValueToProcessValueId` (`cmp #0x4d`), enum `WRAPPER_ISO` > `0x4e`.
3. `CautionConfig`: nodos `64000/80000/102400` (nodo 40 B + `Properties` 8 B + `PropertyList` 96 B) y una lista nueva; cadenas ya existen (`0xef9b`, `0xef30`, `0xef8b`).
4. `libObj`: `iso_max_patch.py` sin flag (→ `0x29`) solo cuando 1–3 estén.

## 5. Riesgos y verificación en cámara
* Default añade 50/64/80: si la A6000 no admite <100, las filas aparecerán (posiblemente grises por `isInhOn`) o `av-cam` las rechazará. Alternativa más fina: lista propia (Type12 + 3 nodos), pendiente.
* No se sabe si `av-cam` acepta fijar 51200 fuera de MFNR (MAX normal `0x23`): lo decide la cámara. Criterio de cierre: verificar en cámara que 51200 se elige y se aplica (EXIF/visor).
