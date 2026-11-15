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

## 4. Medición G45 (15-11-2026; perfil propio `g45a`, `live.py` con `SHIMEXTRA="WAITLOG=1000000 TRACEREP=1 TRACEMAX=8 TRACEFN=…"`; `run.py` no sirve para pulsar teclas, y en `live.py` las trazas salen por `WAITLOG` a `shim.log`, no por la consola)
* Overlay: `CautionConfig.so` con el parche del caso 29 (G43) en `/usr/lib` (el `/lib/CautionConfig.so` del base es un enlace a `../usr/lib`, así que basta). Ruta de teclas verificada: `menu` abre en Ajustes pág. 5; `izquierda ×7` llega a Cámara pág. 5; `izquierda`, `intro` abre ISO.
* Resultado visual: `docs/gui/img/g45-iso-menu-caso29-sin-50-64-80.png`: la lista es `[ISO AUTO multi-frame] AUTO, 100, 125, 160…` (hasta 25600 al envolver): **sin 50/64/80 pese al parche**.
* Trazas (libObj): al arranque `0x4db7c4` se llama una vez (r3=1) y `0x49fc94` (escritor de id→valor) ~128+ veces con ids `0x95bd,0x95df,0x98a4,0x9844,0x9533…` (el rango `0x96fe/0x96ff/0x989e/0x98a1` aún sin aislar: `TRACEMAX` solo imprime 1-8 y potencias de 2). En una ejecución previa `0x4c1240` (r1=`0x2008340`) + `0x4db7c4` (r3=0) dispararon una vez al operar el menú; en la segunda, tras abrir ISO, no.
* `_getSubNode` (`CautionConfig+0x107d7c`) con `TRACELIB=CautionConfig.so TRACEFN2=107d7c`: **sin disparo**. No distingue H1/H2: no está confirmado que `TRACELIB` armara la trampa (su `LOG` no se reenvía sin `WLALL`).
* Conclusión: **H1 vs H2 SIN resolver**. Lo único medido: el parche de caso 29 no cambia la lista visible. Si la A6000 no usa el caso 29 (byte `0x1070316` sin medir) el parche no actúa (H2 parcial); si lo usa, 50/64/80 quedan ocultos por MIN (H1).

## 5. Siguiente paso (ISO-A, ≤ 3 pruebas)
1. Discriminar sin trazas: pareja de literales de otro caso de `_getSubNode` en TODOS los casos (pares en `0x107e60..0x107e8c`: `(0x4748,0x2e80)`, `(0x9704,0x7d24)`, `(0x9c4c,0x5160)`, `(0x8904,0x64a8)`) y ver si el menú cambia: si cambia ⇒ la función se usa y se filtra (H1); si no ⇒ H2 (otro nodo, p. ej. `viewIso*.uxc`).
2. Armar la traza de `107d7c` con `WLALL=1` (para ver `TRACELIB … base`) y `TRACEDEREF`.
3. Aislar `0x49fc94` para `r2∈{0x96fe,0x96ff,0x989e,0x98a1}` (subir `TRACEMAX` solo para esa traza) y leer su valor.
