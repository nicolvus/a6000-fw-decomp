# E24-05g — Cierre de los mensajes de ajustes, cambio de modo y ocupación (27-10-2026)

Sesión 100 % estática: sin cámara, sin USB, sin escrituras de RAM/NAND/NVRAM, sin FDAT ni flasheo, sin tocar el watchdog ni comprobaciones mecánicas. Continúa [E24-05f](e24-05f-emisores-mss-darwin.md) (base `76477396`). **No autoriza parche ni flasheo; E24-04 no cambia.**

Binarios: `darwin_core.bin` 3.21 (SHA-256 `5f2be06d…0bf4`, base `0x4200`) y `av-cam.bin` (BIONZ, base `0x43541000`). Método: Capstone propio sobre ambos (decisivo, por bytes); no se abrió sesión REA (el desensamblado propio resolvió todas las relaciones). Reproducible: `python scripts/e24_05g/ajustes_modo.py` (→ `analysis/e24-05g/ajustes_modo.json`) y `pytest tests/test_e24_05g_ajustes_modo.py` (15 pruebas nuevas; las 16 de E24-05f no se duplican y siguen pasando).

## Veredictos

| | Pregunta | Resp. | Alcance exacto / eslabón faltante |
|---|---|---|---|
| **A** | ¿Origen del evento `0x18a` identificado? | **SÍ, con corrección** | `0x18a` **no es un evento**: son los *flags* de las filas 22/23 de la tabla `{manejador,flags}` que empieza en `0x29514` (E24-05f leyó la tabla desalineada 4 B). El arranque real de la FSM de ajustes son **dos** disparadores, ambos en Darwin (§1). Falta (otro firmware): qué escribe BIONZ en el bloque 10 de la trama `0x31` |
| **B** | ¿Está demostrado cuándo y por qué se envían `0x11/0x14`? | **SÍ para las condiciones de Darwin; NO para su cumplimiento en una captura real** | Condiciones exactas por bytes (§1.3). Los valores de entrada salen de campos que escribe BIONZ (carga del `0x0c`, bloques 3/8/10 de la trama `0x31`): *evidencia insuficiente*, no contradicción. Pendiente: constructor BIONZ de la carga del `0x0c` (`0x437db8d6`→`0x436b8a50`) |
| **C** | ¿Identificada la orden BIONZ que dispara `0x17`? | **NO — contradicción demostrada** | No existe tal orden: la petición de cambio de modo la publica **Darwin a sí mismo** (`0x1b290` → buzón 3 → tarea `0x7b24` → `0x125f6`). Productores identificados (§2). Lo pedido «orden BIONZ→Darwin» queda refutado: el único código que acaba en `0x17` (el 0) lo pide el estado 27 |
| **D** | ¿`0x17` puede completarse sin movimiento mecánico? | **SÍ** | Solo el modo 0 emite `0x17` (`0x1274a`, dentro de `0x126b0`); su cierre de llamadas y el del estado 27 no contienen compuerta, bobinas, motor ni arrancadores (§2.4). Los modos 1/2 no emiten `0x17` (el 2 sí llega a la interfaz del mecanismo `0x1cb0e`). Límite: el modo 0 intercambia tramas con BIONZ (`0x11f22`) y su temporización no está medida |
| **E** | ¿Se conoce el significado del byte 0 de `0x0b` para BIONZ? | **SÍ** | Función `0x438c2538` (paso `0xc0`): clase 0 acepta; clase 1 reintenta (≤19) con sondeo; clase 2 o reintentos agotados → ruta de error (§3). Límite: el estado de error `0x43ae7636(obj,1)` no se siguió hasta su recuperación |
| **F** | ¿La secuencia sin rearme conserva las respuestas de una captura individual? | **NO (evidencia insuficiente)** | Los mensajes `0x0b,0x0d,0x15,0x0e,0x10,0x17(modo 0)` salen sin tocar la compuerta. Pero: (i) la espera del estado 31 depende de la entrada GPIO P29 (`0x1ec9c`); (ii) al salir de esa espera Darwin puede escribir P4E (`0x2041e`→`0x20d00`), también con `0x1fe66=0`; (iii) la correspondencia modo Darwin ↔ tipo BIONZ no está cerrada (§4.2) |
| **G** | ¿Lo mismo para una ráfaga? | **NO (evidencia insuficiente)** | Igual que F; además la toma siguiente depende de que la clase del `0x0b` sea 0 (§3.3) y de que el bit 24 baje (E24-05f §6, estado exterior 9, presente en ambas listas) |
| **H** | ¿Dependencia mecánica adicional que impida completar la captura sin rearme? | **NO demostrada (evidencia insuficiente)** | Candidatas concretas, ninguna demostrada bloqueante: P29 (§2.3), `0x2041e`→P4E (§2.3), modo 2 (`0x1cb0e`). Ninguna es el rearme |

## 1. Origen de `0x11` y `0x14` (parte A)

### 1.1 Corrección de la tabla `0x295c8`

`0x1ba00` (llamado desde `0x7e38`/`0x7f84` en la tarea `0x7de2`) indexa `0x29514 + 8·fila` (`fila < 0x2c`) y usa `[+0]` como manejador (`blx r0`, `0x1baa4`) y `[+4]` como *flags* (bits 3–4, 5–7, 8, 9, 10 llaman a rutinas distintas). Filas 22 y 23 = `{0x1b137, 0x18a}` y `{0x1b123, 0x18a}`; fila 24 = `{0x1c0b7, 0x717}`. El manejador `0x1c0b6` (→ `0x19c4c` → `0x1aa28`) es el de la **fila 24**, no del «evento `0x18a`». Prueba: `test_0x18a_son_flags_…`, `test_manejador_fila24_…`.

### 1.2 Grafo (VERIFICADO por bytes)

```
BIONZ ─trama 0x31 (CRC)─▶ 0x11f58/0x11f22 ─▶ 0x12330 ─▶ 0x124a6: copia bloques T2 (0x28198) y ejecuta la lista de ganchos 0x282fc (0x127b8)
   gancho 0x1c04c (0x28324): si T2[10].byte4 bit3 (0x125da(10)) y el pestillo 0x20002e96.b7 (0x1bb82(7)) está a 0
        └▶ 0x1c02c: publica {tipo 2, código 0x18} en el buzón 2 y fija el pestillo (0x1bb24(7,1)); si el bit cae, lo borra
tarea 0x7de2 (buzón 2) ─▶ 0x1ba00(fila 24) ─▶ manejador 0x1c0b6 ─▶ 0x19c4c ─▶ 0x1aa28  [arrancador 1]

tarea 0x1811a (por toma):  0x17f8c (0x0b/espera 0x0c) ─▶ 0x196b6 ─▶ 0x17cee ─▶ 0x17c26 ─▶ 0x1a3ec [arrancador 2] ─▶ 0x1961c (estados de captura)
                                                    ambos instalan la lista de la tabla 0x294a0 en el descriptor 0x294f8 y ejecutan 0x1e33e
```

* **Arrancador 1 (`0x1aa28`, por evento de trama):** `S+0x2a0` = bit 7 de `[0x20003945]` (`0x1aa40`); `S+0x2a2` se rellena desde `[0x20003944]` y su **bit 2 se fuerza a 1** (`orr #4`, `0x1aa68`), así que la comprobación `S+0x2a2.b2` (`0x1aab8`) no discrimina; el modo es `0x1a004(0x20003978)` → `S+0x2a8`. `0x20003944` es la copia (`0x1a204`→`0x21174`, 12 B) del bloque 8 de la trama (`0x24d42` = `0x125da(8)`; la frecuencia de refresco es INFERENCIA).
* **Arrancador 2 (`0x1a3ec`, por disparo):** `0x17c26` arma 8 B desde la carga del `0x0c` (`S+0x31`, `S+0x32`, `S+0x3d`…) en `S+0x258`; ejecuta la FSM solo si `S+0x258 == 1` y `S+0x25a.b2` (bit 7 de `S+0x31`, o `[0x20000416] == 0`, `0x1a4a8`); modo = `0x1a004(0x20003930)` (o el override `[0x20000415]`).
* `S+0x2a0/0x2a2` no tienen más escritores que `0x1aa28` (ningún otro acceso `#0x2a0/#0x2a2`; los literales `0x20003978/7a` no existen).

### 1.3 Condiciones de emisión y momento

La FSM de ajustes (`0x294f8`) corre por la lista de la tabla `0x294a0` de su modo: claves **0–8** contienen el estado 0 (`0x11`, op `0x211d4`) y el 2 (`0x14`, op `0x211fc`) y arman la espera de `0x12/0x13` (estados 1/3). Claves **9 y 10**: `[21,23]`/`[22,23]`, sin envío (modo 10 = «sin ajuste»: es el valor por defecto de `0x1a004`).

* **Por disparo:** el arrancador 2 se ejecuta en cada vuelta del bucle de `0x1811a`, después de `0x0b` y antes de la FSM de captura. Envía `0x11/0x14` si los campos del `0x0c` de BIONZ dan `S+0x258 == 1`, `S+0x25a.b2` y modo ≤ 8.
* **Por cambio de ajuste:** el arrancador 1 se ejecuta una vez por cada subida del bit 3 del bloque 10 (pestillo).
* **No se envían en cada captura de forma incondicional**; tampoco dependen de la compuerta `0x1fe66` (cierres: `starter_evento`, `starter_disparo` sin compuerta, bobinas ni arrancadores).
* **Comparación 0x1fe66=0 / convencional:** idéntica; los arrancadores, la tabla de modos y las listas no leen la compuerta.
* **Sensores:** sin leva, ADC ni motor en ninguno de los dos cierres. Dependen solo de datos recibidos de BIONZ.

## 2. Origen del mensaje `0x17` (parte B)

### 2.1 Cadena solicitud → proceso → respuesta (VERIFICADO)

`0x125f6(modo)` solo tiene un llamador, `0x7c68`, en la tarea `0x7b24`: recibe del buzón 3 (`svc 0x21`) un mensaje `{tipo, código}`; tipo 1 = trama recibida (`0x11f58`), tipo 2 = cambio de modo con `código = modo` (`0x7c66`: `ldrh r0,[r4,#2]`). Productores del tipo 2: `0x1b290(código)` (`0x1b2a4`), llamado sólo desde `0xd34e` y `0x1f02a`.

| Código | Productor | Cuándo |
|---|---|---|
| **0** | `0x1f02a` ← estado 27 (`0x175a0`) de la FSM de mensajes, lista de la operación `0x16e92` `[48,15,16,47,20,21,22,23,24,47,25,26,27,28,50]` | **En cada captura, justo después del `0x10` (estado 24)**; el estado 28 (`0x175bc`) espera su fin con `0x1f030` (`0x1b2aa(5)`) y plazo `0x7148` |
| **2** (sin `0x17`) | `0xd34e(0)` en `0x1909a`, dentro de `0x18fa0` (espera del estado 31 con `S+0x32 == 0`) | Solo si la espera de `0x16c44` supera dos umbrales de tiempo (`0x3d090` y `0x61a8`) |
| **1** (sin `0x17`) | `0xd34e(1)` en `0x18f6e`, dentro de `0x18d6e` (espera del estado 31 con `S+0x32 != 0`) | Idem (umbral `0x7a120`/`0x61a8`) |

Respuesta: el modo 0 recorre `0x11bdc`/`0x11de8` (envía trama `0x30`), `0x11ef6`+`0x11f22` (recibe y verifica trama `0x31`), `0xe64a`, `0xcb2a`, `0xe572`, arma/borra el temporizador `0x8f16` y publica `0x17` por `0x12260(0x17)` (6 B: dos ceros + `0xcea2`).

**Corrige E24-05f** (§3 fila `0x17`: «no pertenece a la secuencia de captura»; §7: «depende de que BIONZ ordene»): el `0x17` (solo modo 0) es parte de cada captura y lo pide Darwin; los modos 1 y 2 terminan en `0x126a0` sin emitirlo. BIONZ lo espera en el paso de inicio `0x438c2474` (`0x438d0be4`, subclase 12).

### 2.2 Tres caminos de modo

* **Modo 0 (`0x126b0`):** `0x11bdc`, `0x11de8`, `0x122b0(0x18,0)`, `0xe64a(0)`, `0xcb2a`, aviso al buzón 4, temporizador, trama, `0x122b0(0x18,1)`, trama, `0xe572(0)`, `0x17` (`0x1274a`, único `0x12260` de la función).
* **Modo 1 (`0x1263c`):** `0xe5cc`, `0xcb2a`, `0x8e7e`, aviso al buzón 4, temporizador, `0xcb2a`, `0x11bdc/0x11de8`, `0x122b0(0x18,1)`, `0x11ef6`, `0x11f22` y salida (`0x126a0`): **no emite `0x17`**.
* **Modo 2 (`0x1262e`):** `0x1cb0e(1)`, `0x1cebe`, `0xd044` y luego el modo 1 (tampoco emite `0x17`). `0x1cb0e` consulta `0xcf14(4)`, `0x1c384(modo)` y la interfaz del mecanismo `0x1cfc4 → 0x19798 → 0x20048`; **NO_VERIFICADO** si mueve las cortinas (leer el tipo no equivale a moverlas).

### 2.3 Dependencias de hardware halladas (no son el rearme)

> **Corregido por [E24-05h](e24-05h-dependencias-finales-captura.md):** la espera por P29 es solo la variante `S+0x32=0`; con `S+0x32≠0` (visto en T022) el estado 31 espera la FSM ADC-B. Con `0x20c74=0` `0x20d00` no escribe P4E.

* **P29:** la salida de la espera del estado 31 es `0x16c44 = !0x1ec9c()`, y `0x1ec9c` lee el bit-band `0x124` (`0x51c6`) = PDIR2 b9 = **P29**. Decodificación `puerto = off//0x80`, `bit = (off%0x80)//4` (idéntica a la de `fm3-gpio-shutter-mapping.md`). Otro lector: `0x7c8a`. La red de P29 no consta (E11). Si la espera no termina, se repite cada umbral la petición de modo 2/1.
* **`0x2041e` → P4E:** al salir de la espera (`0x190e4` / `0x18e84` → `0x19932`), si `0x19b9e() != 0` (`S+0x170.b0 == 0` y `S+0x444.b4 == 0`) se llama `0x2041e(0)`, que invoca `0x20d00`: con `0x20c74() != 0` escribe `0x51c0(0x238, 1)` = **P4E (2ND_CURTAIN_MG)** y arranca la FSM del subsistema ADC (`0x29d90`). La compuerta `0x1fe66` solo aparece en `0x201b0` (guarda `S+0x150`); **no condiciona el `0x20d00`**. No se determinó el sentido eléctrico del `1`.

### 2.4 Cierres de llamadas (tabla de `ajustes_modo.json`)

| Raíz | Funciones | Compuerta / motor / cortina / arrancadores |
|---|---|---|
| arrancador 1, arrancador 2 | 41 / 12 | ninguno |
| estado 27 (`0x175a0`), estado 28 (`0x175bc`) | 21 / 11 | ninguno |
| modo 0, modo 1 | 207 / 216 | ninguno |
| modo 2 | 277 | `0x20c74` |
| esperas del estado 31 (`0x18fa0`, `0x18d6e`) | 244 | `0x1fe66`, `0x20c74`, `0x20c4a`, `0x20cb2`, `0x20d00`, `0x20d26` |

Límite: cierre sobre `bl/b.w` directos (barrido lineal; aristas espurias posibles por datos entre funciones); no resuelve llamadas por puntero.

## 3. Byte 0 del `0x0b` (parte C)

* **Productor Darwin** (E24-05f §6, comprobado): `0x1828e(S+0x43)` → 0 si `S+0x43 = 0`; 2 si es `1`, `0x10` o `0xfe`; 1 en otro caso. Bit 24 ⇒ código `0x16` ⇒ **clase 1**. Las máscaras de `P4B` (`0x5407f`, `0x5444f`, `0x800` en `0xd116/0xd18e`) **no incluyen el bit 24**: la ocupación por rearme no baja a ninguna línea, solo viaja en este byte.
* **Consumidor BIONZ:** `0x438c2538` (paso `0xc0`) espera la subclase 0 con `0x438d025c` (`caif_recv`, sin plazo) y lee `byte0` en `0x438c25be`:
  * **clase 0** → `0x438c2682`: pone a cero el contador de reintentos `[obj+0x750]` y sigue (`0x438c2728`);
  * **bit 0 (clase 1)** → si `[obj+0x4b95]`, `[obj+0x4c]`, `[obj+0x4b70]` o `[obj+0x5ca5]` es distinto de 0 y el contador `≤ 0x13`: traza, incrementa el contador, `0x438d033c(obj,1)` (reenvía el `0x0c`, subclase 1), sondea `0x4372a73c(0x13)` hasta `0x3e8` veces con `0x43560cc8(1)` y devuelve **1** (reintento);
  * **otro (clase 2) o reintentos/prerequisitos agotados** → `0x438c277c`: `0x43ae769a(obj,0xf7)`, traza del byte, `0x43ae7636(obj,1)` (estado de error) y salida normal de la función.
* **Primera toma / siguiente:** la primera admite con bit 24 a 0 (clase 0). En ráfaga, la siguiente toma reenvía `0x0b`; si el bit 24 sigue arriba se produce clase 1 y BIONZ reintenta hasta 19 veces antes de caer a error. **BIONZ no comprueba físicamente el rearme**: solo lee esta clase.
* **Sin rearme (`0x1fe66=0`):** el bit 24 se baja en el estado exterior 9 de `[0,7,8,9,10]` (E24-05f §6), así que la clase esperada es 0; si no llegara a bajar, el resultado es el mismo que en la ruta convencional: reintento y después error. No hay recuperación ni cancelación demostradas.
* **Paso `0xc5`** (`0x438c27f0`): sondea `0x436e845c`/`0x436e86dc` (estado interno de captura de BIONZ, vía `0x436e5710`/`0x43ada048`) hasta 100 veces y **continúa aunque no se cumpla** (traza y salto a `0x438c2844`); no bloquea y no es de Darwin.

## 4. Contrato de comunicación (partes D y E)

### 4.1 Tres secuencias

| Secuencia | Darwin envía | BIONZ solicita/espera | Condición | Cambia con `0x1fe66=0` |
|---|---|---|---|---|
| **Cambio de modo / inicialización** | `0x17` tras la petición de modo (códigos 0/1/2); `0x11/0x14` si el bit 3 del bloque 10 sube y modo ≤ 8 | BIONZ espera `0x17` en el paso `0x438c2474`; para ajustes espera `0x11` (`0x438cc4b4`) y `0x14` (`0x438cc7a0`) según su tipo | evento de trama / modo | Nada: ningún camino lee la compuerta |
| **Captura individual** | `0x0b` → (arrancador 2: `0x11`,`0x14` si procede) → `0x0d`,`0x15` → … → `0x0e` → `0x10` → petición modo 0 → `0x17` | `0x0b` (clase) → envía `0x0c` → `0x0d`,`0x15` (paso `0xc5`) → `0x0e` (`0xc8`) → `0x10` (`0xcc/0xcd`) → `0x17` | por toma | Cambia solo la lista exterior de la máquina de 49 estados (menos esperas de leva/motor); el orden de los mensajes no cambia |
| **Captura continua** | lo anterior por toma; estado 11 en vez de 9 emite `0x0d/0x15` | igual; la clase del `0x0b` de la toma n+1 depende del bit 24 | por toma | idem |

Dependencia de **protocolo:** orden estricto por subclase (`caif_recv` descarta y devuelve `-4` ante otra subclase), clase del `0x0b`, tramas `0x30/0x31` del modo 0. Dependencia **mecánica:** modo 2 (`0x1cb0e`), espera del estado 31 (P29) y `0x2041e`→P4E, rearme (E24-05).

### 4.2 Desajuste a seguir

BIONZ espera `0x11` solo en `0x438cc4b4` y `0x14` solo en `0x438cc7a0` (tipos `[obj+0x23]` 0 y 1/3/5 por la tabla `0x43b1c6e6 = [4,19,9,19,14,19,24,29]`), mientras que Darwin emite ambos para todos sus modos 0–8. No está probada la correspondencia entre el modo de `0x1a004` y el tipo de BIONZ (dispatchers `0x43b1c6d6` y `0x43afdf34`); un mensaje no esperado se descarta con `-4` en la siguiente espera. Es igual en ambas rutas (no depende del rearme).

## 5. Matriz de riesgos de bloqueo

| Riesgo | Mecanismo | Rearme | Evidencia | Estado |
|---|---|---|---|---|
| BIONZ espera `0x17` sin plazo | Darwin no completa el modo 0 (tramas `0x31` sin respuesta, plazo `0x7148`) | No | §2.1 | Abierto: plazos en tick de Darwin sin medir |
| Espera del estado 31 sin fin | P29 no cambia; solo reintenta modo 2/1 | No (hardware) | §2.3 | NO_VERIFICADO (red de P29, E11) |
| Clase 1 persistente | bit 24 no baja entre tomas → ≤19 reintentos y error | Sí (indirecto) | §3 | Depende del estado exterior 9 |
| Modo 2 (`0x1cb0e`) | acceso a la interfaz del mecanismo tras agotar umbrales | Posible | §2.2 | NO_VERIFICADO |
| `0x2041e` → P4E | escritura de salida al terminar la espera | No (con tipo ≠ 0) | §2.3 | Sentido eléctrico NO_VERIFICADO |
| Mensaje no esperado | `0x11/0x14` sin espera en BIONZ → `-4` | No | §4.2 | Abierto |
| `FAIL` de la FSM | bit 7 de `ctx+0x10` (`0x1e4c2`); su consumo en `0x1e33e` | No | §6 | Pendiente |

## 6. Dependencias adicionales (parte E, acotada)

* **Paso `0xc5`:** resuelto en §3 (no bloquea; estado interno de BIONZ).
* **`0x1e4c2`/`0x1e3d2`:** `0x1e4aa` fija el bit 6 de `ctx+0x10` (hecho), `0x1e4c2` el bit 7 (**FAIL**), `0x1e4f6` borra el 6; `0x1e3d2(ctx,2,t)` borra el bit 11, fija el 2 y guarda el plazo. Qué hace `0x1e33e` con el bit 7 no se resolvió: **pendiente `0x1e33e`**. El estado 26 (`0x17564`) cae en FAIL si `S+0x14` no tiene los bits 1 y 2 (escritores `0x17024`, `0x17044`).
* No se amplió a exposición electrónica, EFCS ni IMX210.

## 7. Pendientes que deja la sesión

1. Productor BIONZ de la carga del `0x0c` (`0x437db8d6`→`0x436b8a50`) y del bloque 10 de la trama `0x31` (decide B).
2. Correspondencia modo Darwin (`0x1a004`) ↔ tipo BIONZ (`0x43afdf16`, tablas `0x43b1c6e6`, `0x43afdf44`).
3. Consumo del bit 7 de `ctx+0x10` en `0x1e33e` y semántica del estado de error `0x43ae7636(obj,1)`.
4. Red de P29 (`0x124` PDIR2 b9) y sentido de `0x20d00`; E11.
5. Contenido del modo 2 (`0x1cb0e`/`0x1cfc4`) y plazos de las tramas del modo 0.

## 8. Evidencia reproducible

| Hecho | Prueba |
|---|---|
| `0x18a` = flags de filas 22/23; manejador en la fila 24 | `test_0x18a_son_flags_…`, `test_manejador_fila24_…` |
| `{2,0x18}` desde `0x1c02c`; gancho `0x1c04c` | `test_publicador_del_mensaje_2_0x18`, `test_gancho_0x1c04c_…`, `test_ganchos_se_ejecutan_…` |
| Compuertas de `0x1aa28`; arrancador por disparo | `test_starter_evento_gates_…`, `test_starter_por_disparo_…` |
| Modos 0–8 con `0x11/0x14`, 9/10 sin | `test_modos_0_a_8_…` |
| `0x17` autopedido; estado 27 tras el 24 | `test_0x17_lo_pide_darwin_a_si_mismo` |
| Cierres sin compuerta/bobinas (modo 0/1, estados 27/28, arrancadores) y con ella (modo 2, estado 31) | `test_0x125f6_modo0_…`, `test_modo2_y_espera_…` |
| P29 | `test_espera_estado31_sale_por_una_entrada_gpio` |
| BIONZ: esperas y byte 0 | `test_bionz_esperas_y_byte0`, `test_bionz_clasifica_byte0_del_0x0b` |

Límites: cierre sobre `bl/b.w` directos; no se ejecuta ni emula nada; la ausencia de evidencia no se toma como imposibilidad. Las pruebas de triaje preexistentes no se corrigieron ni se ejecutaron en esta sesión salvo las de E24-05f y E24-05g (30 aprobadas).
