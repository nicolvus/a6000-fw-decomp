# S101 — selector del tipo de mecanismo y consumidores de los campos de ajuste (A6000 vs A7S) — 21-10-2026

Línea del obturador electrónico. Agrupa el trabajo que en los commits aparece etiquetado como S70/S71/S72 (esos números los usaron en paralelo otros hitos: EIS, FC/FRC, WLAN). Todo es análisis estático (capstone sobre `av-cam.bin` A6000 fw3.21 y A7S fw3.20, más `darwin_core.bin` de A6000/A7S/A6300); **no se ha tocado la cámara** y **S51 se mantiene** (no parchear).

Informes: [consumidores de `+0x238`/`+0x280` y Darwin](../../analysis/s101_shutter_type/block238/block238_consumers.md) · [recorrido de los 12 puntos y selector de tipo](../../analysis/s101_shutter_type/pending/report.md) · [grafo de módulos](../../analysis/s101_shutter_type/graph/module_graph.md) · [plan de pruebas físicas](physical-test-plan.md). Tests: `tests/test_s101_block238.py`, `tests/test_s101_pending.py` (11).

## Verificado (bytes)

1. **`+0x238` (SilentShutter, comando `0x40e3`) y `+0x280` (comando `0x402e`) del bloque `0x43edf684` son solo escritura** en `av-cam.bin`: 62 referencias PC-relativas, todas en `0x43802000–0x43805000`; los accesores `0x43804de8`/`0x43804c38` no van seguidos de accesos a esos campos. Explica S64 (forzarlos no cambió el obturador).
2. **Darwin no fija nunca el tipo de mecanismo.** En A6000, A7S y A6300 `darwin_core.bin` tiene tres lectores de `[0x20000000+ch+0x50]` y ningún escritor; el `__scatterload` solo inicializa `0x20002a00+`; la tabla de mensajes del host (`0x27c68`, 13 entradas) y la categoría `0x2d` (9 manejadores) no lo escriben. El bootloader `0x0–0x41ff` del FM3 no está en el firmware.
3. **Selector de tipo en A7S:** `cap+0x78c = 0x4379ec04(...)`; tipo 2 ⟸ byte `[X+0x7a]≠0` ⇒ `cap+0x748 = 1`.
4. **Selector de tipo en A6000 (nuevo):** `0x4379316a`, `tbb` sobre `[G+0x808]&7` con `G=0x43e9b548` (instantánea de S64): 1 ⇒ tipo 2; 2..6 ⇒ tipo 1; resto ⇒ 0, guardado en `G+0x784` (`0x43e9bccc`). En la imagen ambos valen 0 ⇒ tipo 0 por defecto. No existe el camino por el byte `+0x7a` ni se escribe bandera alguna tras el tipo.
5. **Nadie escribe `G+0x805..0x80e` con acceso directo** (barrido PIC completo; solo lectores `0x43790ac6`, `0x43790654`, `0x43790ee6`, `0x437904a8`, `0x43793106/60`); las petición-constructoras `0x4385a630`, `0x4385a924`, `0x43b2335e` son etapas de captura de tablas de etapas.
6. **Bloque `+0xdd0` (12 u16 de S58):** lo escribe el constructor `0x437b1048` byte a byte desde estado de captura.
7. `Backup 0x3e0005` (cadena de 24 B) solo lo leen dos sitios (`0x437dbed4`, `0x437dbff4`); `0x437881a8` es la llamada de init de arranque; `0x43802614` es el comando `0x402e`.
8. **Rectificado:** la copia en bloque `0x438acc24`/`0x4389efc2` (`0x740←0x133`, `0x748←0x13d`) tiene mapa idéntico en A6000 y A7S; no es la estructura de captura desplazada de S52, que sigue vigente.

## Inferencia

- La diferencia A6000/A7S no está en el código de Darwin que lee el tipo, sino en el **valor suministrado**: la A7S lo deriva de la opción Silent (`+0x7a`), la A6000 de `[G+0x808]&7`, que por defecto es 0 y no tiene escritor directo (lo rellena una ruta por puntero, candidata `0x43868a30`).
- Un tipo 2 en A6000 no bastaría por sí solo: Darwin A6000 descarta el bit `0x20` del paquete CAIF (S53).

## No verificado

Qué ajuste gobierna `G+0x808`; si `G` es la estructura que rellenan las etapas de captura; el contenido del bootloader de Darwin; si forzar `G+0x808=1` cambia el tipo y el obturador (pruebas **P1–P8** del [plan físico](physical-test-plan.md), ninguna ejecutada); siglas ADF/IDT/VDF/etc. (no deducibles de los binarios).

## Próximo

Ejecutar P0–P2 y P7 del plan con autorización; en estático, seguir el destino `r5` de las etapas `0x4385a630`/`0x438e67dc`/`0x43b2335e` hasta su origen.
