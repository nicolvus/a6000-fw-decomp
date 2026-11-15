# G43 — Lista ISO hasta 51200: parche del menú hecho y probado en el arnés; la UI oculta 32000+ por el MAX (16-11-2026; PARCIAL, sin CFW)

Continúa [G42](g42-iso-consumidor.md).

> Actualización G44: la inyección del MAX en el arnés NO funciona con tipo 4/`0x1002` ([G44](g44-iso-arnes-inyeccion.md)); §4 sigue vigente salvo el punto 1. Mismo mecanismo que [G39](g39-extra-fine-menu.md), con un obstáculo más.

## 1. Listas de nodos y rama de la A6000
`CmnViewSettingNodeISOSensitivity::_getSubNode` (`CautionConfig.so+0x107d7c`, fw 3.21) lee el **mismo id `0x1070316`** (lectura de Backup, tipo de modelo) que Calidad (G39), hace `tbb` sobre `byte-1` (0..0x1d; otro → `Default`) y carga dos literales GOT (nodos, NumOf). Las matrices son de punteros con relocaciones; los nodos se construyen en tiempo de carga (`.bss`).

| Lista | Nodos | Contenido (último valor) | Bytes de tipo |
|---|---|---|---|
| `Default` | 35 | MFNR, AUTO, 50…**51200**, AUTOMAX_MR, AUTOMIN_MR | 2-15, 20, 22, >0x1e |
| `Type09` | 24 | … 16000 | 23 |
| `Type10` | 19 | … 3200 | 17 |
| `Type11` | 9 | 100…3200 | 16, 18, 19 |
| `Type12` | 27 | MFNR, AUTO, 100…**25600** | 29 |
| `TypeAmntEntry` / `Mid` | 11 / 31 | …16000 / …32000 | 21 / 26 |
| `TypeDSCEntry` / `Mid` | 11 / 25 | …6400 / …12800 | 24 / (n/a en esta tabla) |
| `TypeEmnt` | 30 | MFNR, AUTO, 50…25600 | 25, 27, 28, 30 |
| `TypeVG` | 9 | 100…25600 | 1 |

Solo `Default` llega a 51200 sin MFNR (los nodos 32000/40000/51200 son de esa lista). **Rama de la A6000**: su menú real empieza en AUTO,100 y acaba en 25600 (capturas) y es compatible con la máscara de tipos de G39 (`{1,21,23,24,29,30}`): por la forma de la lista es `Type12` (byte 29, caso `0x107e16`). El valor numérico del byte NO se leyó (la lectura va por Backup; no hay volcado accesible aquí): es inferencia por contenido, no medida.

## 2. Parche
`scripts/gui/iso_list_patch.py ENTRADA.so SALIDA.so`: 8 B en `0x107e80/0x107e84` (literales del caso 29: `0x171c,0x2ac0` → `0x16f8,0x9578` de `Default`); valida los de `Default`, rechaza otros, idempotente. Test `tests/test_iso_list_patch.py`. Mismos offsets en el `CautionConfig.so` de Sony 3.21 y en el del CFW 3.81.
Cadena aguas abajo (de G41/G42, sin cambios): `getIso` acepta hasta `0x26` (51200), conversores de `libObj` hasta `0x29`, tabla de av-cam hasta `0x2c`; por tanto 32000/40000/51200 (`0x24..0x26`) no necesitan ampliar `wrapperIso`. `iso_max_patch.py` (MAX `0x29`) solo hace falta para >51200; para 51200 basta que el MAX recibido sea `0x26` (el que Sony emite con MFNR).

## 3. Prueba en el arnés (overlay propio, perfiles `g43a/b/c`, sin tocar `scripts/gui/harness/`)
Ruta: MENU → Cámara pág. 4 → ISO. 
* Antes (Sony 3.21): `docs/gui/img/g43-iso-antes-25600.png`; la lista termina en 25600 (AUTO, 100…25600).
* Con el parche (solo caso 29) y con una variante que fuerza `Default` en los 9 casos: **la lista visible sigue acabando en 25600** (`docs/gui/img/g43-iso-lista-default-sin-max.png`, 2 pulsaciones desde el final de 25600 vuelven al tope). Tampoco aparecen 50/64/80, que `Default` sí trae: la UI **oculta los nodos fuera de [MIN, MAX]**, y el arnés no recibe ningún MAX de ISO (G41 §4: `ae.py` no lo emite; el almacén queda en su valor inicial, rango estándar 25600). No se puede ver 51200 hasta que el MAX llegue como `0x26`.

## 4. Pendiente (ISO-A, actualizado)
1. Prueba 51200: copia de `ae.py` en directorio propio (o cambio del arnés, que no se tocó) que inyecte el MAX `0x26` (clave `0x1f0` de un mensaje que acepte `0x4db7c4`) y verifique que 32000/40000/51200 aparecen y se pueden elegir; comprobar si el nodo sale gris (en tal caso, MAX o parche de la comprobación).
2. Confirmar el valor del byte `0x1070316` de la A6000 (volcado de Backup o traza en el arnés) para asegurar que el caso 29 es el correcto; si no lo fuera, el parche alternativo es forzar `Default` en todos los casos (probado que carga).
3. 64000/80000/102400: sin cambios respecto a G42 §2/§4 (nodos + `Properties` + `PropertyList` + lista nueva, enum `WRAPPER_ISO` > `0x4e`, `getIso`/`setIso`/`convertValueToProcessValueId`); no intentado en esta sesión.
