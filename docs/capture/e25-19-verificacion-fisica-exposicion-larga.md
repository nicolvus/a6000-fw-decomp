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
