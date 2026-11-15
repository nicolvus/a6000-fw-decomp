# G44 — ISO 51200 en el arnés: la inyección tipo 4/`0x1002` NO mueve el MAX; origen del rango sin localizar (16-11-2026; PARCIAL, sin CFW)

Continúa [G43](g43-iso-lista-51200.md). Sin cambios en `scripts/gui/harness/` ni en `scripts/gui/avcam/ae.py` (copia en `scripts/gui/g44_iso_arnes/`: `ae.py` + `msg_iso(código)`, `arranca.py` lanza `live.py` con esa copia precargada como módulo `ae`, `cli.py` pulsa teclas y captura).

## 1. Prueba (perfil `g44a`, puerto 8631, overlay solo con `CautionConfig.so` parcheado de G43)
* Verificado que el overlay entra: el `initrd.gz` del perfil lleva dos `cam/usr/lib/CautionConfig.so` (base y overlay; `cpio` solo lee el primero).
* `ae.py` copia + mensaje tipo 4, id `0x1002`, struct de `0xd8` B, u32 `+0xc`=1, código `0x26` en `+0x14`, cada 1 s por la cola `0x20002` (misma cabecera osal que 0x2014/0x2023).
* Ruta de teclas útil: MENU → `izquierda` hasta la pestaña de cámara → `abajo` (entra en la lista) → `derecha ×3` (página 4, ISO) → `intro` → `arriba` (envuelve al final). `docs/gui/img/g44-iso-inyeccion-0x26-sin-efecto.png`: **la lista sigue acabando en 25600**, sin 32000/40000/51200 y sin 50/64/80.

## 2. Por qué no basta (VERIFICADO en bytes, `libObj` 3.21)
* El conversor `0x9aa134` (tipo 4, id `0x1002`) solo escribe `ISO_SPEED_RATE 0x951e` (y `0x951a`): los literales `0x1ee..0x1f2` son **valores** de ISO, no claves. No produce MIN/MAX. El brief proponía MIN/MAX por ahí: descartado.
* Los MIN/MAX llegan por el conversor `0x4db7c4` (claves `0x1ee/0x1ef/0x1f0/0x376/0x377` de un `ObjMsg` con lista de campos), llamado desde el manejador `0x4c1240` (ObjMsg `0x3100`:`0x75d0`), que a su vez se llama desde el conmutador grande de `0x4cf7a8…0x4d0000` (caso en `0x4d0000`). Ningún conversor crudo→`ObjMsg` escribe esas claves (las constantes `0x1e6..0x1f8` de `0x4ab0f0`/`0x4d54e4`/`0x9acb08` son códigos/valores de ISO y descriptores de campos). El mensaje crudo que desemboca ahí no está identificado.
* Valor inicial: no hay `movw #0x96fe/0x96ff/0x989e/0x98a1` en el código de inicialización con un 100…25600 evidente. Solo hay un bloque de valores por defecto en `0xa22140…0xa22230` (`libObj`) que pone `0x951e`, `0x96fe`, `0x96ff`, `0x989e`, `0x98a1` a la constante `0x21` (¿«ISO 100»/neutro?; no coincide con un rango 100…25600) y listas de ids en `0xe38ae0`/`0xe578a8`. `CautionConfig.so` no referencia ninguno de esos ids (barrido capstone): el filtro de la UI no los lee directamente (lo hace por otro camino: interfaz de modelo/`getIso`). **Pregunta clave sin resolver**: de dónde sale 100…25600 sin mensajes.
* `TRACEFN=9aa134,4c1240,4db7c4` por `SHIMEXTRA` (perfil `g44b`) no dejó registro accesible: en modo `live.py` solo se guarda `shim.log` para líneas `WL`; hay que usar `run.py`/`WAITLOG` o capturar el serial. No se obtuvo traza.

## 3. Siguiente paso concreto (ISO-A)
1. Ejecutar con `run.py` (no `live.py`) y `TRACEFN=4c1240,4db7c4,4e0ea8,49fc94 TRACEPEEK` para ver quién llama a `0x4c1240`, con qué ObjMsg, y qué valor (`r1/r2`) guarda `0x49fc94` en `0x96ff` en el arranque. De ahí sale el rango inicial real.
2. Con el id del mensaje que llega al conmutador `0x4cf7a8` (índice del caso `0x4d0000`), inyectar ese mensaje (o, solo para la prueba, parchear el valor inicial de `0x96ff` en una copia de `libObj`, opción B).
3. Confirmar 32000/40000/51200 y 50/64/80 visibles y que el valor llega a av-cam (`entra` en `avcam.jsonl`).
