# E24-05f — Emisores mss de Darwin de los ocho mensajes Darwin→BIONZ (27-10-2026)

Sesión 100 % estática: sin cámara, sin USB, sin escrituras de RAM/NAND/NVRAM, sin FDAT ni flasheo, sin tocar el watchdog. Continúa [E24-05d](e24-05d-consumidor-estado-darwin-bionz.md) (base `71b262da`). **No autoriza parche ni flasheo; E24-04 no cambia.**

> **Corregido por [E24-05g](e24-05g-ajustes-modo-ocupacion.md):** `0x18a` no es un evento (son flags de la tabla `0x29514`, que aquí estaba leída desalineada 4 B); el `0x17` no lo ordena BIONZ, lo pide Darwin (solo modo 0).


Binario: `darwin_core.bin` 3.21 (SHA-256 `5f2be06d…6bf4`, base `0x4200`). Método: Capstone propio (decisivo, por bytes) sobre las tablas y los manejadores; no se abrió sesión REA (el desensamblado Thumb propio resolvió todas las relaciones). Reproducible: `python scripts/e24_05f/emisores.py` (→ `analysis/e24-05f/emisores.json`) y `pytest tests/test_e24_05f_emisores.py` (16 pruebas sobre instrucciones, tablas y llamadores).

## Veredictos

| | Pregunta | Resp. | Alcance exacto / eslabón faltante |
|---|---|---|---|
| **A** | ¿Emisores de los ocho mensajes localizados? | **SÍ** | Los ocho tienen emisor, constructor y búfer (§2–§3). Cinco salen de la FSM de mensajes (descriptor `0x28dd4`) y dos de la FSM de ajustes (`0x294f8` → `0x29f64`); el `0x17` sale del manejador de cambio de modo `0x125f6` |
| **B** | ¿Se conoce qué estado/evento provoca cada transmisión? | **NO** | Sí para `0x0b` (admisión `0x17f8c`), `0x0d/0x15` (estado de captura 9 u 11), `0x0e/0x10` (estado 31 → FSM `0x296f0` estado 5). **Falta**: qué evento arranca la FSM de ajustes (`0x11/0x14`: arrancadores `0x1a3ec`/`0x1aa28`, sin llamador directo; tabla de eventos `0x295c8`, código `0x18a`) y qué orden BIONZ llega a `0x7c68` → `0x125f6` (`0x17`) |
| **C** | ¿`[0,7,8,9,10]` puede generar los ocho? | **NO (parcial)** | **Demostrado para cinco** (`0x0b,0x0d,0x15,0x0e,0x10`): su código y sus guardas no contienen la compuerta `0x1fe66`, el tipo de bobina, primitivas de motor ni arrancadores de la máquina exterior (§5). **Pendiente** para `0x11,0x14,0x17`: su disparo no está resuelto |
| **D** | ¿Se conserva el orden que exige BIONZ? | **NO (parcial)** | El orden `0x0b < 0x0d < 0x15 < 0x0e < 0x10` está fijado por las listas de la FSM y es idéntico en ambas rutas (§4). `0x11/0x14/0x17` dependen de eventos/órdenes: su posición relativa no está demostrada |
| **E** | ¿Algún mensaje depende obligatoriamente del movimiento mecánico? | **NO demostrado** | Ninguno de los cinco primeros (§5). `0x17` en modo 2 llama `0x1cb0e` (que lee el tipo de bobina `0x20c74`); la lectura que hace `0x0b` (byte 0 = clase de ocupación) depende de que el rearme **haya terminado** si el bit 24 sigue arriba (§6). `0x11/0x14` sin decidir |
| **F** | ¿Alguna espera de BIONZ puede quedar sin respuesta al omitir el rearme? | **NO demostrado** | Para `0x0b,0x0d,0x15,0x0e,0x10` no hay ninguna razón ligada al rearme. Riesgo independiente del rearme: `0x11/0x14` (se envían solo con modo 0–8, `[S+0x2a0]=1` y bit 2 de `[S+0x2a2]`) y `0x17` (solo si BIONZ ordena el cambio de modo) (§7) |
| **G** | ¿Los ocho bastan para completar la captura? | **NO** | No hay prueba de suficiencia: faltan el disparo de tres mensajes, el consumo en BIONZ del byte 0 del `0x0b` (§6) y el paso `0xc5` (§9) |

## 1. Capas: contenido, solicitud y transferencia

Un descriptor mss existente no implica envío: hay tres capas separadas.

1. **Contenido** — `0x1edd4(idx)` (constructor, `tbb` de 6 casos) escribe el mensaje en el búfer común de transmisión `0x200032cc` (todas las filas Darwin→BIONZ de `0x27c68` lo comparten) y deja una copia en la sombra `0x200036d8 + off` (+`0x320` ID `0x0b`, +`0x33e` `0x0d`, +`0x38a` `0x15`, +`0x38c` `0x0e`).
2. **Solicitud** — `0x1eff6(idx)` (API A; `idx ≤ 5` → `0x12260` = TX, `6..8` → `0x122b0` = armar recepción) y `0x24d4e(idx)` (API B; `0,1` TX, `2,3` RX). La tabla `idx→ID` está en `0x29784` (`0b 0d 15 0e 10 10 0c 16 0f`) y `0x2a704` (`11 14 12 13`). `0x12260/0x122b0` fijan el ID en curso (`[0x20002e10]`) o lo encolan (`0xeb30`) si hay otro en vuelo.
3. **Transferencia física** — `0x121b6` registra el callback `0x12173` (`0x9924`) y lanza `0x9e82`; cuando termina, `0x12172` llama a `0x1239e` (único llamador), que vuelve a registrar el callback y envía el ID en curso con la fila de `0x27c68`. No se trazó el interior de `0x9e82` (hardware del puerto 3): *transferencia efectiva = NO_VERIFICADO*.

## 2. Grafo de producción

```
BIONZ ──0x0c (CaptureStart)──▶ tarea 0x1811a ─▶ 0x17f8c ──[0x17e94→S+0x43]──▶ op 0x16c64: B(0x0b) S(0x0b)
                                                             │                  op 0x16c82: arma RX 0x0c, espera
                                                             ▼
                                              0x1961c elige lista (5) ─▶ motor 0x1e33e
   lista monodisparo [2,9,3,4,10,6,19,20,26,28,31,…]            lista ráfaga [11,12,7,23,5,8,21,…,31,…]
   estado 9 (0x186f0): op 0x16ca4/0x16cd8                       estado 11 (0x18736): op 0x16d2e
      tmo3,5,6 → B/S 0x0d → B/S 0x15 → arma RX 0x16 → RX 0x16     B/S 0x0d → B/S 0x15 → arma RX 0x16 → RX 0x16
   estado 4 (0x18636) → arrancador exterior 0x19998             estado 5 (0x1865a) → arrancador exterior 0x199b8
   …
   estado 31 (0x190fc) ─▶ 0x1e6ba: FSM 0x296f0 lista [13,5,2,3,10,4,6,9,15]
                              estado 5 (0x1ea5c) ─▶ op 0x16e92: B/S 0x0e → (espera) → B/S 0x10   (BUILD 4 y 5, SEND 5)
   [dentro de 0x190fc, después: arrancador exterior 0x199b8 en 0x191ec]
Evento 0x18a (tabla 0x295c8) ─▶ 0x1c0b6 ─▶ 0x19c4c ─▶ 0x1aa28 ┐  FSM de ajustes 0x294f8, listas por modo (0x294a0):
   (o puente 0x17cea ─▶ 0x1a3ec)                                ┘  [0, 1, …, 2, …, 3, 23]: estado 0 → op 0x211d4 → S 0x11;
                                                                   estado 2 → op 0x211fc → S 0x14; 1 y 3 arman RX 0x12/0x13
BIONZ ─orden─▶ despachador 0x7c68 ─▶ 0x125f6(modo 0/1/2) ─▶ 0x12260(0x17)                 (cambio de modo)
```

## 3. Los ocho mensajes

Estados de la FSM de mensajes (`0x28df0`, 50 estados; `BUILD`=`0x1edd4`, `SEND`=`0x1eff6`): `0 BUILD(0)`, `1 SEND(0)`, `7 BUILD(1)`, `8 SEND(1)`, `9 BUILD(2)`, `10 SEND(2)`, `15 BUILD(3)`, `16 SEND(3)`, `22 BUILD(4)`, `23 BUILD(5)`, `24 SEND(5)`; la fase fija el plazo con `0x16df8(fase, 0x7148)` y, si vence, `0x16dc0` registra el fallo por `0x16558`.

| ID | Long. | Emisor (función / estado) | Constructor y búfer | Disparo (estado/evento) | Orden relativo | Mecánica / sensores | Posibles omisiones |
|---|---|---|---|---|---|---|---|
| `0x0b` | 7 | op `0x16c64` (estados 0–1 de la FSM) ← `bl` en `0x17f9e` de la admisión `0x17f8c` | caso 0 (`0x1ee08`): `[0]` clase de ocupación (`0x1828e` ← `S+0x43`); `[1]` modo `S+0x26b` (`0x1a95a`) con bit 1 = bit de ráfaga `S+0x44.b0`; `[2..5]` u32 de `0x20000620`; `[6]` salida de `0x241d2`. TX `0x200032cc`, sombra `+0x320` | Llegada del `0x0c`; en cada vuelta del bucle de `0x1811a` (por toma de ráfaga) | 1.º (antes de `0x1961c`) | Solo indirecta: `S+0x43` sale de la máscara de ocupación (§6) | Ninguna guarda entre la entrada y el envío; el prefijo de `0x17f8c` solo llama `0x1e5b4`, `0x17e94`, `0x16c64` |
| `0x0d` | 75 | op `0x16ca4/0x16cd8` (estado 9) o `0x16d2e` (estado 11) | caso 1 (`0x1ee62`): `[0..1]` u16 de `0x241b6`, `[2..74]` de `0x241e4` (cero si falla). Sombra `+0x33e` | Estado de captura 9 (monodisparo) u 11 (ráfaga) | 2.º, antes de `0x15` | `0x241b6/0x241e4`: no trazados | Variante `0x16ca4` vs `0x16cd8` por `[S+0x46].b0`: solo cambia el tiempo (`tmo` 3,5,6) |
| `0x15` | 2 | mismo op | caso 2 (`0x1eea2`): `0x241e8`, `0x241ec`. Sombra `+0x38a` | idem | 3.º, tras `0x0d` | no trazada | idem |
| `0x0e` | 2 | op `0x16e92` (estados 15–16) desde FSM `0x296f0` estado 5 (`0x1ea5c`) | caso 3 (`0x1eec4`): `[0]` = `S+0x45` (`0x182ac`), `[1]=0`. Sombra `+0x38c` | Estado de captura 31 → `0x1e6ba` (las cinco listas) | 4.º | `S+0x45`: origen no trazado | Solo si la FSM `0x296f0` llega al estado 5 (le precede el 13: espera) |
| `0x10` | 336 | mismo op (estados 22–24) | casos 4 y 5 (`0x1eda2`, `0x1ed72`): copia desde la sombra `0x20003a66`; se envía una vez (`SEND(5)`) | idem | 5.º, tras `0x0e` | no trazada | idem |
| `0x11` | 16 | FSM `0x29f64` estado 0 (`0x21275`) vía op `0x211d4` ← `0x1ac26` (estado 0 de la FSM de ajustes) | copia `0x2122a`→`0x24d72` desde `0x20003962−6…` | FSM `0x294f8` solo si modo ∈ 0..8, `[S+0x2a0]=1`, `[S+0x2a2]` bit 2 | Antes de `0x14` (lista `[0,1,…,2,…]`) | no trazada | Modos 9 y 10: lista `[21,23]`/`[22,23]`, sin envío |
| `0x14` | 2 | FSM `0x29f64` estado 2 (`0x2129b`) vía `0x211fc` ← `0x1ac82` | `0x24daa` | idem | tras el `0x11` | no trazada | idem |
| `0x17` | 6 | `0x125f6` (`0x12748→0x1274a`) tras vaciar 2 B y `0xcea2` (dos u16 de `0x16906/0x1690a`) | búfer de `0x12302(0x17)` | Orden de cambio de modo (0/1/2) por `0x7c68` | Respuesta a la orden; no pertenece a la secuencia de captura | Modo 2 llama `0x1cb0e` (lee `0x20c74`); modos 0/1 llaman `0xe5cc/0xcb2a/0xe64a…` (no trazados) | Si BIONZ no ordena el cambio, no se emite |

Todas las filas «RX» (`0x0c`, `0x16`, `0x0f`, `0x12`, `0x13`) son respuestas de BIONZ que Darwin espera: `0x0c` tras `0x0b` (`0x16c82`, fase `0x41`), `0x16` tras `0x0d/0x15` (estados 11–12, fase `0x59`), `0x12`/`0x13` tras `0x11`/`0x14`. Un `0x0f` no lo espera el op de `0x0e`/`0x10`.

## 4. Relación mensaje ↔ estado y orden por ruta

| Posición | Mensaje | Fase de captura | Momento |
|---|---|---|---|
| Antes de `0x1961c` | `0x0b` | admisión | **Antes de la captura**; en ráfaga se repite por toma |
| Estado 9/11 (índice 1/0 de la lista) | `0x0d`, `0x15` | previo a la máquina exterior | **Antes** de cualquier fase electrónica o mecánica |
| Estado 4/5 | — (arrancan la máquina exterior: `0x19998` / `0x199b8`) | rearme/«exposición» exterior | Sin mensajes |
| Estado 31 (`0x190fc`) | `0x0e`, `0x10` | tras 4/10/6/19/20/26/28 (monodisparo) o 5/8/21…30 (ráfaga) | **Después** de la fase electrónica y de la máquina exterior iniciada en 4/5; antes del segundo arrancador `0x199b8` (en `0x191ec`) |
| Evento `0x18a` / orden de modo | `0x11`, `0x14` / `0x17` | independientes | **Independientes del mecanismo** (disparo por evento/orden) |

Posiciones comprobadas en las cinco listas: `pos(9|11) < pos(4|5) < pos(31)` (prueba `test_every_capture_list_contains_a_sender_and_state_31`). Los nombres de traza del firmware no se usaron para inferir fases.

## 5. Matriz convencional (`0x1fe66 = 4`, hipótesis) vs sin rearme (`0x1fe66 = 0`)

La compuerta solo elige la lista de la **máquina exterior** (`L1/L2/L3|L0` frente a `L0 = [0,7,8,9,10]`) y la interior; las listas de los 49 estados y la FSM de mensajes no la leen. El cierre de llamadas directas de los manejadores emisores (estados 9, 11, FSM `0x296f0` estados 13 y 5, estados de la FSM de mensajes que construyen/envían, FSM `0x294f8`/`0x29f64` estados 0 y 2) **no alcanza** `0x1fe66`, `0x1f5a2`, `0x20c74`, `0x1fe32/50/86/b6` ni `0x1984e/0x19998/0x199b8` (se tratan como hojas el registro de fallos `0x16558` y el motor genérico `0x1e33e/0x1e234/…`).

| ID | Convencional | Sin rearme | Condición de envío | Evidencia |
|---|---|---|---|---|
| `0x0b` | ENVÍO DEMOSTRADO ESTÁTICAMENTE | ENVÍO DEMOSTRADO ESTÁTICAMENTE | Recibir el `0x0c` y entrar en `0x17f8c` | prefijo `0x17f8c–0x17fb6`: solo `0x1e5b4,0x17e94,0x16c64,0x16c7e,0x16c82`; contenido depende de `S+0x43` |
| `0x0d` | ENVÍO CONDICIONAL | ENVÍO CONDICIONAL | Pasar la admisión y completar el estado 2 (monodisparo); estado 11 en ráfaga es el primero | lista contiene 9 u 11 en las 5; op `0x16ca4/0x16cd8/0x16d2e` |
| `0x15` | ENVÍO CONDICIONAL | ENVÍO CONDICIONAL | Igual que `0x0d` (inmediatamente después) | idem |
| `0x0e` | ENVÍO CONDICIONAL | ENVÍO CONDICIONAL | Que los estados anteriores al 31 completen (en convencional incluyen espera de levas/motor; en sin rearme no) y la FSM `0x296f0` llegue al 5 | `0x190fc` en las 5 listas; `0x1e6ba` lista `[13,5,…]`; estado 13 = solo espera |
| `0x10` | ENVÍO CONDICIONAL | ENVÍO CONDICIONAL | Igual que `0x0e` (en el mismo op) | op `0x16e92` estados 22–24 |
| `0x11` | NO DEMOSTRADO | NO DEMOSTRADO | Evento `0x18a` o puente `0x17cea` + modo 0–8, `[S+0x2a0]=1`, `[S+0x2a2]` bit 2 | arrancadores sin `bl` directo; tabla `0x295c8` |
| `0x14` | NO DEMOSTRADO | NO DEMOSTRADO | Igual que `0x11` | idem |
| `0x17` | NO DEMOSTRADO | NO DEMOSTRADO | Orden de cambio de modo recibida por `0x7c68` | `0x125f6` ← `0x7c68` |

No hay celdas «NO ALCANZABLE». **Qué cambia entre rutas**: solo el tiempo y la probabilidad de error antes de llegar al estado 31 (la máquina exterior convencional espera levas/motor; E24-05) y los sondeos `0x1ff2a/0x1ffbe/0x20018`. **Idéntico**: qué funciones construyen los contenidos, el orden de los cinco mensajes, la dependencia de ADC (ninguna hallada en el camino emisor) y la de sensores de leva (ninguna en el camino emisor; en la máquina exterior convencional sí, antes del estado 31).

## 6. Corrección de E24-05d (veredicto B): el estado de ocupación **sí** viaja, decodificado, en el byte 0 del `0x0b`

`0x17f8c` ejecuta `0x17e94` (decodifica la máscara `0x20002bd0` en un código, `S+0x43`) y **antes de seguir** envía el `0x0b`; el caso 0 del constructor guarda en `[0]` el resultado de `0x1828e`: `0` si `S+0x43 = 0`; `2` si es `1`, `0x10` o `0xfe`; `1` en cualquier otro caso. El bit 24 (rearme sin terminar) se decodifica como `0x16` (`busy_bit_decode` de E24-05a) → byte 0 = `1`. La máscara sin decodificar sigue sin exportarse (E24-05d §3 se mantiene), pero **su clase llega a BIONZ en cada `0x0b`**. Con el estado exterior 9 (`0xd18e(0x01000000)`, presente en `L0` y en `L1/L2/L3`) el bit baja al terminar la lista exterior, así que la siguiente toma envía clase 0 en ambas rutas si la lista llegó al final. Qué hace BIONZ con la clase (manejador de la subclase 0, `0x438d025c`) no se ha leído: pendiente.

## 7. Posibles bloqueos de BIONZ (contrato `caif_recv`, sin plazo, subclase estricta — E24-05d §2)

| Espera de BIONZ | Mensaje | Productor en Darwin | ¿La ruta sin rearme llega a él? | Si no llega / llega otro ID | Cancelación independiente |
|---|---|---|---|---|---|
| inicio, sub 12 | `0x17` | `0x125f6` (orden de modo) | Independiente del rearme; depende de que BIONZ ordene el cambio | espera sin plazo | no hallada |
| sub 0 | `0x0b` | admisión `0x17f8c` | Sí (sin guardas de mecanismo) | un ID distinto antes → `-4` | no hallada |
| fase `0xc5`, sub 2 y 10 | `0x0d`, `0x15` | estado 9/11 | Sí, en este orden | `0x15` antes de `0x0d` → `-4`; no ocurre: ambos van seguidos en el mismo op | no hallada |
| fase `0xc8`, sub 3 | `0x0e` | estado 31 → FSM `0x296f0` estado 5 | Sí, si los estados previos completan | espera sin plazo si el 31 no se alcanza (p. ej. fallo previo) | no hallada |
| fase `0xcc/0xcd`, sub 5 | `0x10` | idem, justo después de `0x0e` | idem | idem | no hallada |
| sub 6 / sub 9 | `0x11` / `0x14` | FSM de ajustes | **No demostrado** (evento `0x18a`, modo 0–8, banderas) | espera sin plazo | no hallada |

Darwin también espera a BIONZ (`0x0c`, `0x16`, `0x12`, `0x13`) con plazo `0x7148 × 0x1388` unidades del temporizador `0x93e6` (unidad no medida); al vencer, `0x16dc0` registra el fallo (`0x16558`, clase 2, código `0x30`) y el estado reintenta con `0x1e3d2(…,0xc8)`. La semántica exacta de `FAIL` (`0x1e4c2`) frente a reintento no se resolvió. No se propone falsificar mensajes ni eliminar comprobaciones.

## 8. Ráfaga y errores

* **Ráfaga** (`S+0x44.b0 = 1`, listas `0x28fa8/0x28fca`): `0x0b` por toma (bucle `0x18164`); el emisor de `0x0d/0x15` pasa a ser el estado 11 (sin esperas `tmo`); `0x0e/0x10` siguen en el estado 31; el arrancador exterior del estado 5 es `0x199b8`. Idéntico en ambas rutas.
* **Errores**: sin envío de `0x0b` si no hay recepción del `0x0c`; clase de ocupación ≠ 0 en `0x0b` si el bit 24 u otro sigue arriba; tiempo de fase vencido → fallo registrado (no cancela por sí mismo la espera de BIONZ). Operación 5: sin cambios respecto a E24-05a.

## 9. Paso `0xc5` (BIONZ) — no investigado

Se aplicó el límite de la sesión: el sondeo `0x436e845c/0x436e86dc` (paso `0xc5` en `0x438c27f0`) **no** se analizó; permanece abierto (E24-05g).

## 10. Pendientes que deja la sesión (E24-05g)

1. Origen del evento `0x18a` (tabla `0x295c8`; arrancadores `0x1a3ec`, `0x1aa28`) y del banderín `[S+0x2a0]/[S+0x2a2]`: define si `0x11/0x14` se emiten en una captura.
2. Orden de BIONZ que llega a `0x7c68` → `0x125f6` y modos de captura; contenido mecánico de los modos 0/1 (`0xe5cc,0xcb2a,0xe64a,0x1b096`).
3. Consumo en BIONZ del byte 0 del `0x0b` (manejador sub 0, `0x438d025c`).
4. Semántica de `FAIL`/reintento del motor (`0x1e4c2`, `0x1e3d2`) y qué ocurre con la lista si un estado previo al 31 falla.
5. Paso `0xc5`: `0x436e845c/0x436e86dc`.
6. Contenido de `0x241b6/0x241e4/0x241e8/0x241ec/0x241d2` y origen de `S+0x45`.

## 11. Evidencia reproducible

| Hecho | Dónde | Prueba |
|---|---|---|
| Ocho filas Darwin→BIONZ y longitudes | `0x27c68` | `test_mss_table_lengths_of_the_eight_tx_ids` |
| Tablas `idx→ID` | `0x29784`, `0x2a704` | `test_index_to_id_tables` |
| Sitios de `SEND`/`RX` con índice constante | `0x17142…0x17530`, `0x21284…0x212f6` | `test_every_send_site_maps_…` |
| Roles BUILD/SEND de la FSM de mensajes | `0x28df0` | `test_message_fsm_roles_build_then_send` |
| `0x0b` en la admisión, sin motor ni compuerta | `0x17f8c–0x17fb6` | `test_admission_sends_0x0b_then_waits_0x0c` |
| `0x0d/0x15` en estados 9 y 11 | `0x16ca4`, `0x16cd8`, `0x16d2e` | `test_0x0d_0x15_sent_by_capture_states_9_and_11` |
| `0x0e/0x10` en el estado 31 | `0x1e6ba`, `0x16e92`, `0x1ea5c` | `test_0x0e_0x10_sent_by_fsm_c_state_5_…` |
| Orden en las cinco listas | `0x28f88…0x28fca` | `test_every_capture_list_contains_a_sender_and_state_31` |
| Sin compuerta/motor en el cierre emisor | cierre de llamadas | `test_sender_code_does_not_reach_gate_motor_or_outer_starters` |
| Modos de la FSM de ajustes | `0x294a0` | `test_fsm_d_sends_0x11_0x14_only_for_modes_0_to_8` |
| `0x17` ← `0x7c68` | `0x125f6` | `test_0x17_is_emitted_by_the_mode_switch_handler` |
| Byte 0 del `0x0b` = clase de ocupación | `0x1828e`, `0x1ee14`, `0x17f9a` | `test_0x0b_byte0_is_the_decoded_busy_class` |

Límites: el cierre de llamadas es sobre `bl`/`b.w` directos (los llamadores por puntero de función —tabla de eventos— no se resuelven); `FAIL` y plazos no se interpretan; no se ejecuta ni emula nada. La ausencia de evidencia no se toma como imposibilidad.
