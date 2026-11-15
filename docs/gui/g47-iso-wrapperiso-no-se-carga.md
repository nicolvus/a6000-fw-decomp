# G47 — ISO: `wrapperIso.so` NO se carga en el arnés; el mapeo del valor actual vive en `cmn_view_processDataMgr.so` (15-11-2026; PARCIAL, sin CFW)

Continúa [G46](g46-iso-getsubnode-no-construye-menu.md) §4. Sin cambios en `scripts/gui/harness/`; perfil propio `g47a` (puerto 8647), borrado al acabar, `qemu` detenido y huérfanos `g43a/b/c` borrados.

## 1. Hipótesis «la lista sale de `wrapperIso`»: FALSADA en el arnés
* Símbolos de `wrapperIso.so` (3.21): `WrapperIso::getIso` (`+0x1cb0`, 2104 B), `setIso` (`+0x270c`, 3324 B), `convertValueToProcessValueId` (`+0x24e8`), `isInhOn` (`+0x26c2`), `getInstance` de `CmnViewProcessDataMgr` (`+0x1c20`). No hay `getIsoRange/getMin/getMax/getList`: no expone rango ni lista.
* Arranque en frío con `SHIMEXTRA` (`WLALL=1`, `TRACELIB=wrapperIso.so`, `TRACEFN2=` esas entradas) y apertura del menú ISO (ruta: `menu`, `derecha` hasta pág. 4, `intro`): **el shim no registra ningún `dlopen` de `wrapperIso`** (145 `dlopen` en `shim.log`: libObj, viewUnified2/4/8, CautionConfig, libs de infra; ninguna `wrapper*`). Además ninguna biblioteca del `stage/cam` lo tiene en `NEEDED` ni cadena `wrapperIso`/`wrapper%s`. Conclusión: en el arnés el menú ISO se construye **sin** `wrapperIso`; su `getIso` no puede ser el tope visible aquí (la cámara real podría cargarlo desde otro proceso, p. ej. ScalarDaemon/Wi-Fi: no medido).
* Captura: `img/g47-iso-menu-arnes-auto-lista.png` (menú ISO abierto; lista AUTO, 100…, sin 50/64/80 ni 32000+).

## 2. Hallazgo útil: mapeo del valor ISO actual (`cmn_view_processDataMgr.so`)
`CmnViewProcessDataElementCustomIsoSensitivity` (clase que sí usa viewUnified2: `ACT_ISOSensitivity`, `ViewIsoSensitivity` en viewUnified4):
* `getValue(int&)` en `+0x68308` (568 B): lee valor de proceso (`+0x4cd7c` claves `0x1f4/0x1f5/0x1f6`) y lo convierte por cadena `cmp`: códigos `0x3a..0x45,0x48` → ids `0x22..0x2e` (tabla `mappingValIsoSensitivity` `+0x923c4`, 13 filas de 12 B: id, nodo `0x10708c4`, código) y `0x08..0x26` → ids `1..0x20`; **un código > `0x26` devuelve 0 (sin valor)** (`cmp r0,#0x26 ; bne → movs r5,#0`, `+0x684fc`). Es otro tope en `0x26`, independiente de libObj/wrapperIso; ISO-B/51200 exige ampliarlo (códigos `0x27..0x29` → ids `0x21..`).
* `getValueChild(int,int&)` `+0x67df4` busca en esa tabla por (id, nodo).
* Esta es la tercera cadena con tope `0x26` (junto a `wrapperIso::getIso` y el conversor libObj `0x4db7c4`), todas por tabla/cadena lineal, no por rango MIN/MAX.

## 3. Lo que NO se consiguió
* Traza de `cmn_view_processDataMgr.so` (`TRACELIB`, `TRACEFN2=68308,67df4,682a4,67e9c`): **sin línea `TRACELIB … base` en `shim.log`** pese a `WLALL=1` y a que `harness.env` lleva las variables. La trampa no se arma: el binario del shim compilado probablemente es anterior al código `TRACELIB` de `sonyshim.c` (cambios sin commit de otra sesión). **Pendiente de arnés** (no se edita aquí): recompilar/verificar el shim o usar `SETHOOK`.
* No se aplicó parche de MAX ni de tabla: sin el constructor de la lista identificado, un parche sería a ciegas. No hay captura con 51200.

## 4. Siguiente paso (ISO-A)
1. Con el shim verificado (línea `TRACELIB … base`), trazar `getValue`/`getValueChild`/`isGrayedOutWithReason` y los widgets `ACT_ISOSensitivity`/`LG_viewisosensitivity` (viewUnified4) al abrir el menú; buscar quién genera las filas (`viewUnified4`, `LayoutST_ISO_SENSITIVITY_SETTING`).
2. Parchear la cadena de `getValue` (`+0x684fc`) para `0x27..` y probar con inyección de código `0x26/0x27` desde `ae.py` (copia propia).
