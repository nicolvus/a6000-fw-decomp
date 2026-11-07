# E26-R73 — `0x30087` no gobierna la temporización del sensor; los ganchos del planificador EFCS son variables de depuración del grupo 2 (07-11-2026, estático, REA)

Sigue a [R72](e26-r72-parametros-efcs-bionz-30087-y-config-darwin.md). REA abierto de nuevo con `REA_GHIDRA_STARTUP_TIMEOUT_MS=3600000`, `GHIDRA_MAXMEM=4G` y un vigilante de RSS de 7 GB: listo en 487 s, todas las descompilaciones terminaron, sin presión de memoria (≈ 8,9 GB libres). Llamadas de una en una.

## 1. Corrección de R72 §1: lectores equivocados

* El registro del planificador EFCS `0x43841070` es el bloque que devuelve `0x4383fb6c(modo, índice)`. Se pone a cero con **0x158 bytes**, así que `+0x156` (= `puVar14[0xab]`) es su último campo.
* Los «consumidores» de R72 (`0x4384095c`, `0x4385d874`) leen `+0x156` de **otra estructura**: la de información de captura, con campos de exposición en el dominio APEX (sesgo `0x1000`, límites ±`0x800`; leen hasta `+0x162`). No consumen el valor de `0x30087`.
* Lectores reales de ese registro, por `0x4383fb6c`: `0x4383fd6c` envía `+0x64…+0x78` y `+0x7a` (`0x5c` B) al bloque de exposición del sensor, **sin `+0x156`**. `0x43840150`, `0x438403e4` y `0x438d07f8` no leen `+0x156` como halfword.

## 2. A dónde va `0x30087+0xa0..` (VERIFICADO, REA)

* Justo después de escribir `puVar14[0xab]`, el planificador llama a `FUN_437b0810(…, param_12 = cap+0x1198+0x2bc, …, param_14 = registro)`. Su última línea es `*(param_12 + 0x2b4) = *(registro + 0x156)`.
* `cap+0x1198+0x2bc = cap+0x1454` es la estructura de 0x6b0 bytes que `0x438d07f8` copia desde y hacia `[…]+0x4bc` (`memcpy(…, 0x6b0)`). Es la **StillInfo** que se pasa al lado Linux para procesar la imagen (ABI `StillInfo Linux 0x6b0`, RESEARCH_TASKS).
* **Conclusión:** el valor por modo de `0x30087` (90/166/150) **no entra en la programación del sensor** (línea de reinicio, VTS, `sl`). Viaja como parámetro de procesado de la imagen. **No es la palanca del adelanto del reinicio**, y R72 §1 queda corregido. Su uso exacto en Linux está fuera del alcance de `av-cam`.

## 3. Los ganchos que pueden sobrescribir `record+0x64` (`sl`) y otros campos (VERIFICADO)

* Los bytes `0x43f9b3a2`, `0x43f9b451`/`0x43f9b434`, `0x43f9b3d0`, `0x43f9b422`/`0x43f9b3fd`, `0x43f9b41b`/`0x43f9b3d8` y `0x43f9b3f3`/`0x43f9b37c` pertenecen a una **tabla de 615 punteros a variables de un byte**, `0x4400041c–0x44000db4`.
* `FUN_437b4d80` la registra con `FUN_4378a3a8(2, tabla, 0x267)` en un catálogo por grupos (`0x43ff22b0`, entradas de 12 B `{grupo, tabla, n}`).
* El único acceso al catálogo es `FUN_43788e64(…, grupo, …)`, que lee o escribe una variable (`param_2 == 0xff` = lectura). **No tiene llamadores directos**: es un manejador de órdenes, el protocolo de ajuste o depuración.
* Los ganchos también se leen en `0x4383c91e`/`0x4383cb0c` (planificador normal) y en `0x43841722…` (EFCS). Ningún código de arranque los inicializa y en la imagen valen 0. **Solo cambian si una herramienta de servicio los escribe en RAM**, no persisten (INFERENCIA fuerte).
* Su valor en ejecución sigue sin leerse. Basta una lectura SWD de solo lectura de `0x83f9b37c…0x83f9b4a9`.

## 4. Estado

* **E26-R72-30087: CERRADO**. No es temporización del sensor (§2).
* Ganchos de depuración: **CERRADO con límite**. Solo se escriben por orden de servicio y son volátiles. Una lectura SWD los confirmaría.
* Sin cambios: E26-R66-RESET (PARCIAL) y E26-R72-DARWIN-CFG.
* Lo que sigue gobernando el reinicio electrónico en el BIONZ es `0x4383fa40`: `sl = max([rec+0x1c] + sb, VTS) − sb`, con `[rec+0x1c] = cap+0x5dc`, la geometría del modo del sensor (R57 §10–11). Ninguno de esos datos es por unidad y no ha cambiado desde el 20-10. En estático no queda en el BIONZ ninguna fuente de la pérdida que dependa de esta unidad.
