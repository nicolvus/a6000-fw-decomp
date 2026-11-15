# G42 — ISO expandido por el CONSUMIDOR: parche del MAX en `libObj` hecho; la UI exige además enum, setIso y nodos (16-11-2026; PARCIAL, sin CFW, sin captura)

Estrategia (decidida por el usuario): no buscar el emisor en `av-cam`; `libObj` sustituye el MAX recibido por `0x29` (102400). Continúa [G41](g41-iso-expandido-409600.md).

## 1. Parche de `libObj` (HECHO, probado por bytes y Unicorn)
* Conversor `0x4db7c4` (3.21): `0x42ac00(msg, 0x1f0, &[r7+0x38])` lee el **código ISO máximo**; `0x4e0ea8` lo convierte y `0x49fc94(…, 0x96ff, …)` lo guarda (`PARAMID_ISO_SPEED_RATE_MAX`). El almacén es genérico, el parche va en el conversor, antes de `0x4e0ea8` (que además guarda el valor ya recortado con `0x4a5836`).
* `scripts/gui/iso_max_patch.py ENTRADA.so SALIDA.so`: 14 B en `0x4db86e` (antes el aviso «Invalid ObjMsg» del campo: `cbz; ldr; add.w; add; bl`) → `ldr r1,[r7,#0x38]; sub.w r2,r1,#0x26; cmp r2,#3; it lo; movlo r1,#0x29; str r1,[r7,#0x38]`. Códigos `0x26..0x28` → `0x29`; el resto no cambia. **Sin cueva** (no hay relleno en `.text` de `libObj` cerca; se reutiliza código de log). Valida bytes originales y ancla; idempotente. Tamaño igual.
* Test `tests/test_iso_max_patch.py` (3 verdes): bytes/idempotencia/rechazo, desensamblado capstone y ejecución Unicorn del fragmento para los 75 códigos `0..0x4a`.
* No se toca el rango estándar (`0x377` → `0x98a1`, normalmente `0x23`): no sube al valor nuevo; quien lo necesite aplica la misma plantilla en `0x4db954`.
* Límite: el log de error de ese campo desaparece (solo diagnóstico).

## 2. Por qué NO basta (hallazgos de esta sesión; el parche NO es seguro solo)
1. **`wrapperIso::getIso` (`wrapperIso.so+0x1cb0`)**: con MAX `0x29` cae a `0x247e` (error). Hay que añadir `0x27..0x29` en las tres cadenas. La de «actual» (`0x1d3c…0x1fa6`) es lineal `ui = k + 0x28` para `k = 8…0x26` (31 casos × 8 B), por lo que se puede comprimir para liberar sitio sin cueva; la de mín./máx. (`0x2440…0x2472`, ids `0x11…0x1f` y `0x21…0x2f`) llena el rango de ids: `0x30` choca con la serie de «actual». Hace falta un enum `WRAPPER_ISO` nuevo (> `0x4e`; `0x4f` es el centinela «sin valor»).
2. **`WrapperIso::convertValueToProcessValueId` (`+0x24ea`)** rechaza ids `> 0x4d` (`cmp r1,#0x4d; bhi`, `tbh`): ampliar tabla; y `setIso` igual.
3. **El menú ISO es una lista estática de nodos** en `CautionConfig.so` (`CmnViewSettingNodeISOSensitivity::_getSubNode`, `+0x107d7c`, elige `cmnViewSettingNodesISOSensitivity{Default,Type09,Type10,Type11,Type12,TypeAmnt*,TypeDSC*,TypeEmnt,TypeVG}` por un byte de tipo de modelo vía `0x101c20`). Las listas llegan como mucho a `51200` (`Default`: `…25600, 32000, 40000, 51200, ISOAUTOMAX_MR, ISOAUTOMIN_MR`). **No existen nodos `cmnViewSettingNodeISOSensitivity64000/80000/102400`** (solo hay nodos `…MultiFrameNoiseReduct102400`, de la lista de Multi Frame NR). Hay que crear nodo (40 B) + `Properties` (8 B) + `PropertyList` (96 B) por valor y una lista nueva, y un id de valor de proceso que `libmprctrl`/`libObj` acepten.
4. Cadenas: **ya existen** en `string_english.uxc` (CFW 3.59): `ISO 64000` (`0xef9b`), `ISO 80000` (`0xef30`), `ISO 102400` (`0xef8b`), también `ISO 204800` (`0xeff4`), `40000`/`32000`/`51200`. No falta texto; faltan nodos, enum y proceso.
5. Efecto con 32000/40000/51200: la lista `Default` ya tiene esos nodos; con MAX `0x26` el menú los mostraría si el tipo de modelo de la A6000 apunta a esa lista (tipo del A6000 en `0x101c20`: **no determinado**).

## 3. Arnés
No se hicieron capturas: el MAX no llega (`ae.py` no emite ISO, G41 §8) y, aunque llegara, la UI no tiene nodos >51200. Con el parche solo se vería el cierre de `getIso` en error. Lo único útil en el arnés sería inyectar un mensaje tipo 4 id `0x1002` (código en `+0x14`) desde una copia de `ae.py` y comprobar el menú con la lista `Default`; no hecho.

## 4. Más allá de 102400 (solo documentado)
`0x2a..0x2c` (128000/160000/204800 en la tabla de `av-cam`): `0x4e0ea8` devuelve 0 para `k=0x2a` y `tbb` de `0x4e41c4` topa en `0x2a` (G41 §7): ampliar ambas tablas, enum de UI, nodos. 409600 (`0x2f`): además 3 entradas nuevas en `0x43bc48e0` (hoy acotada a `0x2c` por `movs r1,#0x2c` en `0x437b403e`), ganancia no leída.

## 5. Pendiente
ISO-A (actualizado en `docs/PENDIENTES.md`): tipo de modelo del A6000 en `0x101c20`; enum/`getIso`/`setIso`/`convertValueToProcessValueId`; nodos CautionConfig 64000/80000/102400; prueba en arnés con `ae.py` copiado.
