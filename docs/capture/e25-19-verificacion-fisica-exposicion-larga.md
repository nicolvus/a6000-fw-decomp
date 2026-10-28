# E25-19 — Verificación física de la exposición larga (solo lectura, T053)

**Fecha:** 28-10-2026 · **Cámara:** Sony ILCE-6000 / IMX210, fw 3.23 con Darwin B1a · **Alcance:** fotos normales por RemoteShutter +
lectura de RAM por telnet. Sin escrituras en RAM/NVRAM/NAND, sin parches, sin hooks, sin BULB, sin ráfagas.
Etiquetas: **O** observado en la cámara · **E** emulación · **I** inferencia · **N** no obtenido.

## 1. Decisión

**C — hipótesis contradicha (con límite).** En fotos normales de 1/30 s a 30 s el registro de foto **no lleva el plan nativo**:
`svd=0`, `shd=1`, `r5=1`, `ShutMode=3`, `record+0xf0=0` y `record+0xd8/da/dc=0` en **todas** las muestras (6 velocidades, 289 lecturas
repartidas antes, durante y después de cada exposición). Las exposiciones de 20 s y 30 s salen bien (EXIF, luminancia, duración), así que
el mecanismo real de la exposición larga **no pasa por `svd`/VTS del registro**. Límite: `cap` no pudo localizarse con cadena demostrada
(§4), de modo que **no se observó lo que recibe `SetExposure`** ni el motivo concreto de que el productor `0x4383fa40` no se ejecute.

## 2. Conexión y procedimiento

| Dato | Valor |
|---|---|
| PC | `wlan0` 192.168.1.6/24, ruta por 192.168.1.1 (en T052 era 192.168.0.13) |
| Cámara | 192.168.1.29 (MAC fc:c2:de:3a:5d:5c), telnet 23 (root, `Linux 3.0.27_nl-rt106 armv7l`; no hay `id`), RemoteShutter `v8b` en 8080 |
| Identificación | no por el puerto: los 2 sitios de T050 (`0x836d6fb6=91f80990`, `0x836d7000=28125ffa85fe`) y los 6 punteros GOT de T052-A coinciden byte a byte, antes y después (8/8 ✓ en cada comprobación) |
| Lectura RAM | `dd if=/dev/mem bs=2 … 2>/dev/null \| chroot /android /system/bin/hd /proc/self/fd/0` (la cámara no tiene `base64`; el `rd` de `camera_silent.py` escribe un temporal y **no se usó**). Sin `of=`, sin ficheros en la cámara. Una sola ida y vuelta por instantánea |
| Latencia | 60–80 ms por región; 295–450 ms por instantánea ligera (6 objetos) durante el disparo |
| Controles | `/ss?n=&d=`, `/shoot`, `/status`, `/info`, `/log`, `/jpg?i=`; sin `/burst`, sin `/nr` |
| Disparos | **7** normales: 1/30 ×2, 1/8, «1», 4, «15», 30. Ninguno repetido por fallo; el primer 1/30 lo marcó «abortado» mi controlador por esperar `ready` cuando la cámara responde `done …` (el disparo fue válido y se conserva) |
| Salud tras cada disparo | `/status` = `done …`, `bursting=false`, telnet vivo, originales intactos, 0 líneas nuevas de `dmesg` con error: **7/7** |

El controlador dispara y, con un hilo aparte, lee `record_a/b`, `settings`, `imager`, `gate_b` y el predicado desde 0,3 s antes del
`/shoot` hasta 2 s después de que `/status` deja de ser `shooting`. Cada lectura lleva su hora (`t_epoch`).

## 3. Resultados físicos

| Pedido | Tv `settings+0x162` | EXIF | Duración /shoot→listo | `/log` ms | shd | svd | VTS | r5 | ShutMode | lineas / d8,da,dc | Lum JPEG |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1/30 | 5376 | 1/30 | 3,3 s | 1365 | 1 | **0** | 4176 | 1 | 3 | 0 / 0 | 11,9 |
| 1/8 | 4864 | 1/8 | 3,6 s | 1515 | 1 | **0** | 4176 | 1 | 3 | 0 / 0 | 27,5 |
| «1» | 4011 | **1,3 s** | 5,1 s | 3020 | 1 | **0** | 4176 | 1 | 3 | 0 / 0 | 112,1 |
| 4 | 3584 | 4 s | 8,7 s | 5692 | 1 | **0** | 4176 | 1 | 3 | 0 / 0 | 178,1 |
| «15» | 2987 | **20 s** | 23,3 s | 21593 | 1 | **0** | 4176 | 1 | 3 | 0 / 0 | 243,1 |
| 30 | 2816 | 30 s | 35,1 s | 33451 | 1 | **0** | 4176 | 1 | 3 | 0 / 0 | 249,8 |

Comunes a todas (**O**): período de línea `record+0xc` = **4096** (Q8), suelo `+0x1c` = 1, factor `imager+0x4b8` = 1, predicado
`[0x43deb360+0x10]` = 0, `record_b` entero a cero, `imager+0x504` = 2 (otro objeto, **no** `cap+0x504`).
`Tv = 4096 − 256·log2(t)` se cumple en las seis filas. La cámara redondeó los pedidos «1» → 1,3 s y «15» → 20 s (pasos de 1/3 EV).
`record+0xc..+0x6d` se actualiza ~1,0–2,2 s después del `/shoot`, es decir **durante** la exposición en 4, 15 y 30 s (n_durante = 24, 77, 119),
y queda estable después. Evidencia cruda: `analysis/e25-19/disparos-*.json`, resumen `resumen.json`, matriz `matriz.json`, JPEG `jpeg-metricas.json`
(solo métricas; no se versionan fotos).

### Plan calculado frente a plan observado (`analysis/e25-19/matriz.json`)

El productor real `0x4383fa40` (emulado, E25-18) con **los parámetros leídos** (período 4096, VTS 4176, predicado 1) daría:

| Velocidad | shd nativo | svd nativo | VTS d8/da/dc | Observado |
|---|---|---|---|---|
| 1/30 | 6399 | 1 | 4176 | shd 1, svd 0, d8..dc 0 |
| 1/8 | 4177 | 1 | 7813/4176/4176 | ídem |
| 1,3 s | 4177 | 18 | 7683/4176/4176 | ídem |
| 4 s | 4177 | 59 | 7793/4176/4176 | ídem |
| 20 s | 4177 | 301 | 5990/4176/4176 | ídem |
| 30 s | 4177 | 478 | 8049/4176/4176 | ídem |

Cinco niveles, sin mezclar: (1) nativo antes de normalizar = tabla; (2) normalizado propuesto (E25-18) = no comparable porque cambia con el
VTS/período reales; (3) **observado en RAM** = `shd=1,svd=0,r5=1,ShutMode=3`; (4) lo que recibiría `SetExposure` = **N** (requiere `cap`;
si `0x4383fd6c` copiara `record+0x64..0x73` a `cap+0x64c`, recibiría svd=0, **I**); (5) lo confirmado en el controlador = **N**.

## 4. Cadena de punteros de `cap`: NO demostrada (bloqueo estático, no contradicción)

Hecho (V por bytes, volcado del 20-10 y REA): `0x43b1e854`, `0x43b1e7f2` y `0x438c828c` obtienen `cap` con `0x43ae75dc` = `ldr r0,[r0]`;
su `r0` es el objeto de flujo **M** que reciben los estados `0x43b1ae2b…` (`[M+0x23]` = subestado, `[M]` = `cap`; también
`0x437eba9c`, que usa `cap+0x4ae0..0x4ae8`). Esos estados se invocan como *functors* de una tabla estática de **239 entradas de 0x14 B**
en `.bss` (`0x43edcfd0…0x43ede268`; cada registro `{0, thunk 0x43afb3bb, 0, estado, 0}`, thunk `ldr r3,[r0,#8]; blx r3`), que se
inicializa en la función de arranque `0x437eb…` (13 funtores por GOT; el resto por `base+0x14·k`). Los estados no tienen llamadores ni
punteros directos en `av-cam`, y **no se halló el sitio que invoca el functor con M** ni quién guarda M. Un puntero global a M/`cap` no
aparece en los GOT enumerados. Elegir `cap` por coincidencia de valores (`cap+0x5cc=4096`, `cap+0x5e0=4176`, …) estaba prohibido como
validación y no se hizo: **no se leyó ninguna dirección candidata** en la cámara. Siguiente paso concreto: localizar el invocador del
functor (`ldr rX,[fn]; mov r0,fn; mov r1,M; blx rX`) y la construcción de M (¿`StateMgr` de `libmprctrl`?).

## 4b. E25-19b (parcial): cadena estática hasta `cap` derivada; lectura en vivo sin hacer

Hecho **V por bytes** (`scripts/e25_19b_cadena.py`, `tests/test_e25_19b_cadena.py`; `analysis/e25-19b/cadena-estatica.json`):

1. El thunk `0x43afb3ba` (`ldr r3,[r0,#8]; mov r0,r1; blx r3`) llama al estado con `r0 = M`; los estados leen `cap = [M]` (`0x43ae75dc`).
2. El despachador `0x437e534c(id, M)` copia la tabla de 16 pares `{selector, id}` en `0x43ff8fb8` (se alcanza por `ldr/add pc` en `0x437e5374`),
   busca `id` y llama al selector con `M`; el selector (p. ej. `0x437ea034`, id 8) toma `cap=[M]` y elige la entrada de 0x14 B de la tabla de 239
   functors por `[[cap+0x4ae4]+0xc]`. Aclara E25-19 §4: la tabla de 239 es un mapa estado→functor, no contiene `M` (leída en vivo: campos 0, 2 y 4 a cero).
3. `M` sale de una cola: bucle `0x43afbffc(id)` → gestor `E = matriz[id]` (`0x437e50d8`; GOT `0x440267bc` → matriz `0x43ff8f70` de 17 punteros) →
   `0x43afc408(E)` copia 0x70 B del nodo (`nodo+8`) y devuelve su primer campo `M`; `[M+0x1c]` = id de grupo.
4. Los 14 gestores son objetos estáticos en `.bss` (`0x43ed8814…0x43edbe2c`, vptr `0x43fcd320`), con centinela de cola en `E+0x14`. **En vivo (cámara en reposo)**: la matriz coincide
   con el fichero y todas las colas están vacías (autoapuntadas) ⇒ `M` es transitorio y `cap` **no se puede leer en reposo por esta vía**.

No demostrado: quién escribe `[M]=cap` al encolar, ni una lectura de `cap` con mensajes en vuelo. El bloque de control del grupo 10 (`0x43ed8e50`, capacidad `0x64`, función `0x43ae8633`)
liga un puntero `0x43eeafe8` que **no** se toma como `cap` (coincidencia de valor, sin cadena). Tras estas lecturas la cámara dejó de responder (sin ruta a 192.168.1.29; sin que
se escribiera nada). Siguiente paso: con la cámara de nuevo en red, muestrear los centinelas durante un 4 s/30 s (`e25_19b_cadena.py --live` solo lee la matriz y los centinelas; falta el
muestreo con seguimiento de nodo→`M`→`cap`) y buscar el productor de mensajes.

### 4c. Muestreo en vuelo durante un 4 s (`scripts/e25_19b_muestreo.py`, `analysis/e25-19b/muestreo-4s.json`)

13 pasadas (≈0,6 s cada una; los 14 centinelas en 2 lotes de 7 porque >8 regiones desborda la línea del telnet), 1 disparo de 4 s, originales T050 intactos al final.
La única cola no vacía fue la del gestor `0x43edbd9c` (grupos 1–3): un nodo del banco `0x43ed8e5c` cuyo payload es `{0x43eeb028, 0x80000a99, 0x100, thunk 0x43ae8633}`.
**Corrige §4b punto 3**: `0x43eeb028` no es un `M` con `[M]=cap`; es un **objeto functor/evento estático** (`+8` = thunk `0x43afb3bb`, `+0x10` = función de estado, `+0x1c` = paso, `+0x20` = `0x0901ffff`
→ subestado 9 en `+0x23`) y su primer dword (`0x952db580`) no es un puntero. El `cap` llega por el segundo argumento del thunk (`r1`), que el muestreo no capturó.
Observado: de 1,2 s a 4,0 s el evento fue `estado 0x43b1b025, paso 2, sub 9` y a 4,65 s `estado 0x43b1ce6f, paso 3, sub 11`: **la espera de la exposición es un estado de la secuencia,
no un valor de `svd`**. Faltan: la duración de ese estado frente a la velocidad (30 s) y el origen de `r1`. `cap` sigue sin leerse.
El muestreo de 30 s se interrumpió porque el usuario apagó y encendió la cámara a mitad (conexión reiniciada; sin fichero de resultados). Tras el reinicio: originales T050 intactos y `ready`.

### 4d. Muestreo en vuelo durante un 30 s (`analysis/e25-19b/muestreo-30s.json`)

53 pasadas, 0 errores, originales T050 intactos antes y después, cámara `ready`. El evento (ahora en `0x43eeafa8`: es un banco de eventos, no una dirección fija) estuvo en
`estado 0x43b1b025, paso 2, sub 9` desde 1,06 s hasta ≈ 32,5 s y pasó entonces a `0x43b1ce6f, paso 3`; a 33,1 s aparecen eventos `0x435503b1` en los gestores `0x43edbd3c/6c/fc`
(fin de captura, lectura). Con 4 s el paso 2 duró ≈ 3,1 s (1,2 → ≈ 4,3 s): **el estado `0x43b1b025` dura lo que la exposición** (≈ T + 1 s de preparación),
así que la exposición larga se sostiene en esa espera de la secuencia, no en `svd`/VTS del registro. Sigue sin demostrarse `cap` ni lo que recibe `SetExposure`;
falta desensamblar `0x43b1b024` (quién sale de la espera: temporizador, evento de sensor o contador) y el origen de `r1`.

### 4e. Estado `0x43b1b025` desensamblado (V por bytes)

`0x43b1b024` lee el subestado `[M+0x23]` (`0x43afdf16`) y salta por `tbh` (12 entradas) a un manejador por subestado: 0→`0x437ed9c4`, 1→`0x438c27f0`, 2→`0x438c8474`,
3→`0x438c23f4`, 4→`0x43b1e854`, 5→`0x43b1d93c`, 6→`0x438c89a8`, 7→`0x437f2540`, 8→`0x437f00a4`, **9→`0x438c289c`**, 10→`0x43b1e878`, 11→`0x437ed568`; otro valor devuelve 5.
El manejador del subestado 9 (el observado durante toda la exposición) **no espera**: obtiene `cap=[M]` (`0x43ae75dc`), anota hitos (`0x43ae769a(cap,0xc8)`), lee el estado de un registro
(`0x43560e00(0x13)`, bit 15), compara `[[cap+0x4ad0]+0x1d]` con `0x436e86dc()`, llama a `0x437f9a64`/`0x438d0958`/`0x437c1178` y **devuelve 0**. Por tanto el tiempo que la secuencia pasa en
paso 2/sub 9 no es un bucle de este manejador: la máquina queda parada hasta un **evento externo** que la haga avanzar (el que termina la exposición) y que no se ha identificado
(temporizador, interrupción del imager o contador). Sigue sin leerse `cap`; el siguiente paso útil es leer en vuelo `cap+0x4ad0`/`0x4b80` y localizar al productor del evento de fin (quien encola paso 3/sub 11).

### 4f. Productor del evento de fin: no hallado; lectura corregida de lo observado (V por bytes + I)

- El bucle `0x43afbffc` entrega un evento solo si la compuerta `0x43afbf68(E, M, flag)` → `0x437e6224` → `0x43afc544` lo acepta (usa `cap+0x5488`, `cap+0x5490`, `cap+0x4b64` y `0x437e4fd8`);
  si no, el evento se difiere en una matriz de 5 ranuras de 0x14 B. Los envíos (`0x437e519c`, `0x437e515a`) no tienen llamadores directos (se llaman por puntero).
- **Corrección de §4c/4d (I)**: el evento visto de 1,06 a ≈ 32,5 s es el **pendiente** (siguiente en la cola), no el que se ejecuta. Que permanezca en cola toda la exposición indica que el
  hilo despachador está ocupado en un manejador anterior (o la compuerta lo difiere) hasta el fin de la exposición; no que el manejador del subestado 9 espere (§4e: devuelve 0). El manejador
  bloqueante no se ha identificado (candidatos: los de los subestados 2 y 8, `0x438c8474`, `0x437f00a4`).
- Dato nuevo en `StartExposure` (`0x438c828c`, tras el prólogo ya conocido): calcula `[cap+0x570]` a partir de `[cap+0x56c]` y de `0x43ad90b6/0x436c2270/0x436c28d0`
  (`(n+1)·K / (1000·[cap+0x56c] / x)`, entradas en bruto: cuentas de línea/tiempo) y lo registra con `cap+0x4b64`; también usa `cap+0x740` (si ≠ 0 conserva `[cap+0x570]`) y `cap+0x504`.
  Campos a leer cuando `cap` esté demostrado: `cap+0x56c`, `0x570`, `0x1d8`, `0x1e0`, `0x4b64`, `0x5488`, `0x5490`.

### 4g. E25-19b (cierre estático parcial): compuerta decodificada, M identificado, `cap` sin dirección (V por bytes salvo nota)

Reproducible: `scripts/e25_19b_dis.py`, `e25_19b_callers.py`, `e25_19b_calls.py`; `tests/test_e25_19b_compuerta.py`. Cámara **fuera de red** (192.168.1.29 sin respuesta): **ninguna prueba física en esta ronda**, nada modificado.

**P0 — M.** En el bucle `0x43afbffc`, `r4 = 0x43afc408(E)` es el **primer dword del elemento de 0x70 B** de la cola (`{M, …, byte +8 = pendiente, byte +9, 5 ranuras de 0x14 B desde +0xc}`). Ese `r4` es el `M` de la compuerta `0x43afbf68(id=[M+0x1c], M, flag)` (`cap=[M]` en `0x43afbf74`; accede a `cap+0x5488/0x5490/0x4b64`) y de `0x437e534c(id, M)` → selector(M) → `0x43afb408(M, functor…)`, que **escribe** el functor en `M+8..M+0x1c`; es decir, **A = SÍ**: `M` lo pasa `0x43afbffc` (su `r4`), que lo toma del elemento de cola. `M` es un objeto de flujo persistente (en vivo `0x43eeafa8`: `+8`=thunk `0x43afb3bb`, `+0x10`=estado, `+0x1c`=id, `+0x23`=subestado) y `0x43afc0ae(M, cb)` solo le añade *callbacks* (`0x437e5ec0` rellena las ranuras). **B = NO**: no se halló quién escribe `[M]=cap`; además la muestra en vuelo daba `[M]=0x952db580` y `[M+4]=0x43e9d788` (en `.bss`), que no concuerdan con `cap=[M]` para un evento aún no entregado; no se resuelve sin leer `M` en un instante de entrega.

**P1 — Compuerta (`0x43afc544`, 1 = acepta/entrega; 0 = difiere en la lista `E+4`).** Con `flag=0` difiere si: la lista diferida `E+4` no está vacía (`0x43afbfd6`), `[E+0x24]≠0` (**bloqueado**, `0x43afc15a`), no se cumple `[E+0x2d] < [E+0x2c]` (**en vuelo ≥ máximo**, `0x43afc160`), o `0x43afc4f6` halla una entrada pendiente con `[+9]==byte(cap+0x5490)` y `[+8]==0`; si no, acepta (`0x437e6224` incrementa `[E+0x2d]` con `0x43afc172` y guarda el evento en las 5 ranuras). `[E+0x24]` solo cambia con `Block(id)=0x437e52b0` (único llamador `0x437de594`, grupo **6**) y `Unblock(id)=0x437e54b4` (único llamador `0x437de134`, que además drena con `0x43afbffc`). El manejador `0x437de518` es un estado de fin de cuadro: usa `cap` y el contador `[cap+0x1d8]` frente a `[cap+0x4b68]-1`, y publica el código 9/7 con `0x4372a50c`. La cola observada (`0x43edbd9c`, grupos 1–3) **no es la del grupo 6**, así que ese bloqueo no explica por sí solo el diferimiento observado. Decremento de `[E+0x2d]`: no hay más escritores en este rango que `0x437e533a`/`0x437e5e1a` (no revisados a fondo). **G = NO demostrado** (hay mecanismo de diferimiento; no se ha medido `[E+0x24/0x2c/0x2d]` en vivo: `scripts/e25_19b_compuerta.py` queda listo, solo lectura, para la próxima conexión).

**Subestados 2 y 8 (E, F).** `0x438c8474` (0x1e8 B hasta el retorno; 29 llamadas) y `0x437f00a4` (≈0x100 B; 15 llamadas): la única llamada directa común es `0x43ae75dc` (cap) y hitos `0x43ae769a`; las restantes son accesos a sensor/registro (`0x436d6118/62e4/61a4/64c8`, `0x437f8990`, `0x43b7af68`) y *logs* (`0x43902718`). **Ninguna llamada a una primitiva de espera identificada**; sin embargo no se rastrearon los callees a profundidad ni se identificaron las primitivas de espera (`osal_wai_sem_tmo`/`osal_rcv_msg_tmo`) en `av-cam.bin`, de modo que **E = NO demostrado, F = NO demostrado** (no se prueba su ausencia).

**P2 — Temporizador (I = NO).** Solo lo ya conocido: `StartExposure` (`0x438c828c`) calcula `[cap+0x570]` a partir de `[cap+0x56c]`; no se localizó dónde se programa el temporizador ni quién recibe su fin. `0x8000`/BULB lo emiten callbacks de temporizador (E25-18). **P3/P4 no realizadas** (cámara sin red; `cap` sin dirección): J = NO, K = NO, D = NO, C = NO, L = NO (no se modificó nada).

**Decisión: D — bloqueo concreto.** Falta (1) quién escribe `[M]=cap` al crear/encolar el objeto de flujo: observar `M` (p. ej. `0x43eeafa8`) **en el instante de entrega** o hallar el constructor que llama a `0x43afb408`/stores en `M+0` (el productor de los envíos `0x437e515a/0x437e519c` se llama por puntero); (2) leer en vuelo `[E+0x24/0x2c/0x2d]` de los 14 gestores en una foto de 4 s (`e25_19b_compuerta.py`) para decidir diferimiento por compuerta frente a manejador ocupado; (3) rastrear los callees de `0x438c8474`/`0x437f00a4` hasta las primitivas de espera.

### 4h. E25-19b (cámara en red): la compuerta difiere por límite de vuelo; candidatos y `M` revisados

Reproducible: `scripts/e25_19b_compuerta.py --confirm-readonly --speed 4` (una foto normal; solo lecturas `/dev/mem`; `analysis/e25-19b/compuerta-4s.json`, reposo en `compuerta-reposo.json`), `scripts/e25_19b_esperas.py` (`analysis/e25-19b/esperas.json`), `tests/test_e25_19b_compuerta.py`. Originales T050/GOT íntegros antes y después; 1 disparo; nada escrito.

**Compuerta completa (V por bytes).** `0x43afc544(E, b=byte(cap+0x5490), flag, u=0x437e4fd8(..))` con `flag=0` devuelve 0 (difiere) si: lista diferida `[E+0xc]≠0`; `[E+0x24]≠0`; `[E+0x2d] ≥ [E+0x2c]`; o `[E+0x2e]≠0` y hay en la cola `E+0x14` una entrada con `[+8]==0` y `[+9]==b`. Si no difiere, acepta si `[E+0x28]==u` **o** `[E+0x2d]==0`. Constructor `0x437e5300`: `[E+0x2c]=1`, `[E+0x2d]=0`, `[E+0x2e]=0` (los 14 gestores en reposo: `max=1`, `en_vuelo=0`, `habilitado=0`, sin diferidas). La entrada solo se libera con `Complete(E, M)` (`0x437e6098`, vía `0x437e611c`, llamada desde `0x437e5638` y `0x437e577a`) que marca `[entrada+8]=1` y llama a `Done(E)=0x437e5de8` (único decremento: `en_vuelo-1`, con registro de error si ya es 0).

**Medición (4 s, 15 muestras ≈ 0,5 s).** Antes del disparo todo en reposo. De **1,16 s a 5,24 s** el gestor del grupo 1 (`E=0x43edbd9c`) tiene `en_vuelo=1 ≥ max=1`, `bloqueado=0`, diferidas 0, `habilitado=0` y **un evento pendiente** (`M=0x43eeb0e8`, `[+8]=0`): motivo `difiere:limite_vuelo` (≈ 4,08 s, la exposición). A 5,24 s la ranura se libera y el mismo `M` aparece pendiente en el gestor `0x43edbe2c` (grupo 9) hasta ≈ 6,08 s, también por límite de vuelo; luego todo vuelve a reposo (en 6,08 s dos gestores suben `max` a 2). El `E+0x24` nunca se activó (coherente con que `Block` solo lo llama el grupo 6).

**Candidatos (P1).** Wrappers OSAL de `av-cam.bin` = `ldr r3,[API]; ldr r3,[r3,#0x14]; ldr.w r3,[r3,#OFF]`, con `OFF = tabla de liro.ko + 0x24`: `osal_wai_sem_tmo` `0x435611b8`, `osal_sig_sem` `0x435611d4`, `osal_snd_msg` `0x4356120c`, `osal_rcv_msg_tmo` `0x43561260`. Por llamadas directas (profundidad 6): `0x438c8474` alcanza `wai_sem_tmo` (`→0x437f8990→0x437b43b4→0x4382dcfc→0x4382d820→0x4393ac98`, acceso a sensor/bus, `r1=-1`), `sig_sem` y `snd_msg`; `0x437f00a4` alcanza `wai_sem_tmo` (`→0x43787180→0x43785338→0x436cead4`, `r1=-1`: bloqueo infinito de un semáforo/mutex), `rcv_msg_tmo` (`→0x437fafac→0x437873a4→0x43ae7d2e→0x439037c0→0x43ae07c0`, `r2=-1`, infinito), `sig_sem` y `snd_msg`. **Los dos contienen esperas alcanzables, pero son helpers genéricos (bus del sensor, mutex, recepción de cola) a 4–6 llamadas; no se demuestra que alguna sostenga la exposición** (la rama tomada no se trazó; no hay ejecución).

**`M` (P2).** El `M` de la cola es un objeto de banco `{[M]=enlace, [M+4]=.bss, +8=thunk 0x43afb3bb, +0x10=estado, +0x1c=id, +0x23=sub}` y **`[M]` no es `cap` en lo observado**: `[M]` enlaza otros objetos tipo functor (`0x43eeb0e8→0x43ee1b64→0x43ee3674→0x43fcd4c0`, que acaba en una vtable; `[x+0x4ae4]` no es una tabla de estados); la muestra previa `0x952db580` apuntaba a otro objeto de la misma clase. El thunk `0x43afb3ba` pasa a la función de estado su **segundo** argumento (`mov r0,r1`), no `M`; el objeto con `[obj]=cap` es ese argumento, que sigue sin identificarse. `cap` no se leyó.

| | Respuesta |
|---|---|
| A. ¿La compuerta difiere durante la exposición? | **SÍ (M)**: 1,16–5,24 s, grupo 1, `en_vuelo=1 ≥ max=1`, 1 evento pendiente |
| B. ¿Condición exacta? | **SÍ** para esta captura: `[E+0x2d] ≥ [E+0x2c]` (única rama activa: sin diferidas, sin bloqueo, `habilitado=0`) |
| C. ¿Espera bloqueante en los candidatos? | Alcanzable (infinita, vía helpers) en ambos; **no demostrado que sea la que ocupa la exposición** |
| D. ¿Hilo/manejador que mantiene ocupada la ejecución? | **NO**: se sabe qué evento ocupa la ranura (el entregado antes de 1,16 s), no cuál es ni por qué no se completa |
| E. ¿Verdadero `M`? | Parcial: el `M` de la cola es un objeto de banco (id 2, sub 9); el objeto con `[obj]=cap` **NO** |
| F. ¿`[M]=cap`? | **NO** (refutado para el `M` observado) |
| G. ¿`cap` leído en foto? | **NO** |
| H. ¿shd/svd de `SetExposure`? | **NO** |
| I. ¿Mecanismo de 30 s? | **NO**; solo: la ranura de vuelo dura ≈ la exposición (30 s no se repitió: sin pregunta nueva) |
| J. ¿Finalización electrónica independiente? | **NO** hay evidencia |

Dependencia única restante: identificar el **argumento real de la función de estado** (el que cumple `[arg]=cap`), p. ej. el valor de `r1` en el `blx` del thunk en el instante de entrega del evento de la ranura en vuelo (se necesita un punto de observación fuera de lo no intrusivo, o el escritor estático del segundo argumento en `0x437e534c`/`0x43afb408`), y el llamador de `Complete(E,M)` para ese evento.

## 5. Respuestas

| # | Pregunta | Respuesta |
|---|---|---|
| 1 | ¿Telnet? | **SÍ** (192.168.1.29:23) |
| 2 | ¿RemoteShutter? | **SÍ** (`v8b`, `/info`, `/status`, `/ss`, `/shoot`, `/log`, `/jpg`) |
| 3 | ¿`cap` con cadena verificable? | **NO** — observación no obtenida (§4); sin contradicción |
| 4 | ¿Registro real de una foto? | **SÍ** (`record_a`; `record_b` siempre 0) |
| 5 | ¿VTS 4219, 4266 u otro? | **Otro: 4176** en las seis velocidades (O) |
| 6 | ¿Período 3891 Q8? | **NO: 4096 Q8** (16,0 µs). Contradice la referencia 15,2 µs (T044/T046/T047); puede ser otro modo del registro o un valor por defecto: **sin resolver** |
| 7 | ¿Predicado? | Byte = 0 en las 289 lecturas ⇒ predicado 1 (cuadro extra) **como se esperaba**; su efecto no se observa porque el productor no corre |
| 8 | ¿A 1 s svd=14 o 15? | **NO: svd=0** (el pedido «1» fue 1,3 s: nativo 18). Contradicción real de la hipótesis para el registro |
| 9 | `cap+0x504` | **N** (`cap`); no confundir con `imager+0x504 = 2` |
| 10 | ¿svd a `SetExposure`? | **N** directo; si la copia `record→cap+0x64c` ocurre, 0 (I) |
| 11 | ¿Planificador conserva VTS dinámico? | **NO**: `d8/da/dc = 0`, `lineas = 0`; no hay VTS dinámico en el registro |
| 12 | ¿A 4 s svd coherente con el productor? | **NO**: observado 0, productor 59 |
| 13 | ¿Las largas terminan bien? | **SÍ** (20 s y 30 s, JPEG completo, cámara libre y estable) |
| 14 | ¿Integración electrónica continua? | **NO demostrada**: la exposición larga funciona, pero el mecanismo (electrónico, cortina abierta u otro, con B1a) no se identificó. Observación no obtenida |
| 15 | Diferencia plan/uso | tabla §3: el plan existe como cálculo (E); en la foto real el registro lleva los valores por defecto (`shd=1, svd=0, r5=1, ShutMode=3`) |
| 16 | ¿Qué falta para 1/15–30 s Silent? | (a) localizar `cap` y observar `SetExposure`; (b) entender cómo sale la exposición de 20–30 s con `svd=0` (¿contador de pasos `cap+0x740`/`4b9c`?, ¿ruta de cortina?); (c) recalibrar `silent_plan.py` con período 4096 y VTS 4176; (d) prueba multicuadro reversible |
| 17 | ¿Avanzar a una prueba reversible? | **No todavía**: E25-20 (hook) queda condicionado a (a) y (c). La ruta rápida (≤1/30) sigue sin base física nueva |
| 18 | ¿Cámara estable? | **SÍ**: 7 disparos, 0 anomalías, originales intactos al final |

## 6. Anomalías y límites

- Período 4096 y VTS 4176 no coinciden con 3891/4219 del repositorio; `silent_plan.py` sigue parametrizado con los antiguos (la matriz del §3 usa los reales).
- Datos de un solo banco (A); `record_b` siempre cero, de modo que el selector `[cap+0x1b8]&1` no se leyó pero A es el que cambia con cada Tv.
- Tv se actualiza 1,0–2,2 s tras `/shoot` con resolución de muestreo ~0,3–0,45 s; los campos transitorios más rápidos podrían escapar a la lectura.
- Los JPEG de 1616×1080 son vista previa: solo se usan como evidencia auxiliar (luminancia ↑ con la exposición; 20 s y 30 s saturan 55 %/75 %).
- 15 s y «1» s no son velocidades que la cámara use tal cual (20 s y 1,3 s).
- La duración total incluye 1,4–3,4 s de procesado; la NR de larga exposición no se tocó.

## 7. Recomendación para E25-20 y la prueba multicuadro

1. **E25-19b (solo lectura, estático):** demostrar la cadena `GOT/objeto → M → cap` (invocador del functor, constructor de M) y leer entonces
   `cap+0x504/0x64c/0x650/0x740/0x4b9c` en un 4 s y un 30 s para saber qué recibe `SetExposure` y qué mueve la exposición larga.
2. Recalibrar E25-18 con período 4096/VTS 4176 (o aclarar si el registro es de otro modo) antes de diseñar el hook.
3. Solo entonces E25-20 (hook reversible con guardián); el BULB sigue fuera hasta contar con un mecanismo documentado de inicio y fin.

Reproducción: `scripts/e25_19_readonly.py --confirm-readonly`, `scripts/e25_19_test.py --confirm-readonly --speeds 1/30 1/8 1 4`,
`scripts/e25_19_matriz.py`; pruebas `tests/test_e25_19_readonly.py`.
