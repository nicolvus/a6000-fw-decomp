# S61 — flujo de mensajes de la tarea `0x43806e38` (A6000)

20-10-2026. SHA `b60c845c…bb9`. Pruebas: `tests/test_s61_imx210.py` (`MessageFlow`, `SyncContext`, `Tbh`).

## Corrección TBH (S60-Sol)

`0x43806a04: tbh [pc, r2, lsl #1]`; en Thumb **PC = dirección + 4 = `0x43806a08`** (tabla inmediata). `analysis/s60/sol/trace_payload.py` usaba `0x43806a04` (−4). Corregido (`table + 2·off`) y `tests/test_s60_sol.py` actualizado: caso 4 → `0x43806c28`, caso 10 → `0x43806d06` (los destinos antiguos `…c24/…d02` caían dentro de la instrucción anterior). Independiente del script: `Tbh.test_tbh_instruction_and_pc_base` decodifica los 12 destinos desde los bytes y exige el prólogo de manejador `ldr r2,[pc]; ldr r6,[r3,r2]; ldrb.w r3,[r6,#0x40]`. Los informes S60 no se tocan (ya citaban `…c28/…d06`).

## Mapa caso → llamadas (VERIFICADO, bytes)

| Caso | Llamadas | Papel |
|---|---|---|
| 0 | `0x43b01026` | emisor tipo 1 (rol 1, 0x564 B) |
| 1 | `0x43b00cd0`, `0x43806668` | acuse |
| 3 | `0x43b00fe6` (rol 1), `0x43b00fa4` (rol 2) | **petición 3 → respuesta tipo 4** (0x54 B / 0x18 B) |
| 4 | `0x43b00dac`, `0x43b00d94`, `0x438065fc` | recibe tipo 4 → copia a `obj+0xd64…` + acuse |
| 6 | `0x43b00e74`, `0x43b00e9a` | registra id de secuencia (`obj+0x2d4…`) |
| 7 | `0x43b00d78`, `0x43b00d1a`, `0x43b00ec0` | — |
| 9 | `0x43b00f62` (rol 1), `0x43b00f22` (rol 2) | **petición 9 → respuesta tipo 10** (0x5e0 B / 0x28 B) |
| 10 | `0x43b00dac`, `0x43b00cd0`, `0x43b00d94`, `0x43806590` | recibe tipo 10 → copia + acuse |

`obj+0x568` (rol 1 ó 2) elige la variante; si no coincide el emisor no envía. Tipo = `rol + k` (4 = 1+3 = 2+2; 10 = 1+9 = 2+8), comprobado en `MessageFlow.test_reply_emitters`.

## Productores de peticiones

* **Tipo 9 — localizado.** `0x43b00ed8` (método sin puntero en datos; REA no lo reconoce) elige `0x43806398` (rol 1) o `0x4380632c` (rol 2) según el rol (`obj+0x568`) y campos del 2.º argumento (`(arg+8)+0x26c` rol 1, `+0x224` rol 2); ambos envían tipo `8+1 = 9` con `obj+0x56c ← 1` (pendiente) por `0x438061c4` (pool/cola **`0x3030f`**). **Único llamador directo: `0x437907a6` dentro de `0x4378fef4` = `HS_Main`** (cadenas `[CAMERA_MAIN_SYNC]: HS_Main: …`, `TC::Last1st/Last2nd`, `BONOBO flg timeout`), tras el paso `TC::Last2nd` y con guarda `[glob+0x1ac0+0x1f]==1 && 0x43b00cba(obj)≠0`. Es decir, la petición 9 se emite una vez por ciclo V del manejador de sincronía principal (CÓDIGO; temporización real NO demostrada).
* **Tipo 6 — localizado.** `0x43806288(obj, kind)` (thunks `0x43ae8434/50/6c`, kind 0/1/3; llamadores `0x43af0cb0`, `0x4384cc76`, `0x437d5296`). No es 3 ni 9.
* **Tipo 3 — NO LOCALIZADO.** Los envoltorios locales `0x438061c4` (tipos 6, 9), `0x43806400` (1, 4, 10) y `0x438064c8` (acuses) no producen 3; ningún literal `0x3030f/0x8003030f` fuera de `0x43805900..0x43806f00`. Puede ser un caso latente o un emisor que obtiene el id por otra vía.
* **Publicación.** `0x43b00dd4` (copia `obj+0xd64→db4`, publica `+0xdd0`) tiene un único llamador, `0x43792f62` dentro de `0x43792a0c` = manejador `VD_Pre`/`HS3` (`[IMAGING_REL]`, `VD_Pre: start delayed`), con guarda `0x43b00cba(obj)`. Orden estático por V: `HS_Main` (pet. 9) → tarea (caso 9) → respuesta 10 → tarea (caso 10) copia a staging → siguiente `VD_Pre` publica. **INFERENCIA fuerte** (orden de código, no traza).

## Handles `0x8003030f` / `0x3030f`

`0x438061c4` y `0x438064c8` reservan y envían con `0x3030f`; `0x43806400` reserva y envía con `0x8003030f` pero estampa el origen `0x3030f` (`0x43b00b42(buf,0x3030f)`); la tarea receptora espera solo `0x3030f` (`0x43561260`, timeout −1) y atiende casos 4/10 que solo ese camino genera ⇒ `0x8003030f` actúa como **alias del mismo buzón** (INFERENCIA; el significado del bit 31 está en el OSAL de `liro.ko`, no recuperado). `0x80030001` (otro buzón) lo usa `0x43805870`.

## ¿Mismo intercambio de captura?

NO demostrado. Los mensajes pertenecen al ciclo V del sincronizador (no a una captura concreta); no hay dependencia de modo fotográfico localizada (el emisor no consulta `0x0B/0x2F`).
