# E24-05d — Consumidor BIONZ del estado de Darwin y cierre de captura (27-10-2026)

Sesión 100 % offline: sin cámara, sin USB, sin escrituras de RAM/NAND/NVRAM, sin FDAT ni flasheo, sin tocar el watchdog. Continúa [E24-05](e24-05-upd-y-rearme.md) y [E24-05a](e24-05a-captura-fin-bionz-darwin.md) (base `763d795a`). **No autoriza parche ni flasheo; E24-04 no cambia.**

Binarios: `av-cam.bin` (SHA-256 `b60c845c…56bb9`, base `0x43541000`) y `darwin_core.bin` 3.21 (SHA-256 `5f2be06d…6bf4`, base `0x4200`). Método: Capstone propio sobre ambos (decisivo, por bytes) + REA/Ghidra sobre `av-cam.bin` (sesión única, cerrada) para llamadores y pseudocódigo. REA y Ghidra comparten motor: sus coincidencias no cuentan como validación independiente de lo que Capstone ya verifica. Reproducible: `python scripts/e24_05d/transport.py` (→ `analysis/e24-05d/transport.json`) y `pytest tests/test_e24_05d_consumidor.py` (10 pruebas).

## Veredictos

| | Pregunta | Resp. | Alcance exacto / eslabón faltante |
|---|---|---|---|
| **A** | ¿Se identificó qué mensaje transporta el estado de Darwin a BIONZ? | **SÍ, con corrección** | Transporte completo de los **ocho** mensajes Darwin→BIONZ (IDs `0x0b,0x0d,0x0e,0x10,0x11,0x14,0x15,0x17`): fila CAIF → receptor → buzón → espera (§1). El de mayor carga y consumido junto con el `0x0b` en la fase de captura es el ID `0x10` (336 B, `(3,5)`). **Corrección:** el «bloque de estado» de E24-05a (`0x6c78`: máscara + anillo) **no es un mensaje**: es una instantánea del registro de fallos (§3). El contenido de los IDs `0x0d/0x10/0x11` y su emisor en Darwin siguen sin trazar (NO_VERIFICADO) |
| **B** | ¿Se identificó la función que consume el bit 24, o la señal alternativa? | **NO** | **Contradicción demostrada para la hipótesis de E24-05a:** Darwin no exporta la máscara. Sus únicos lectores (`0xd294`) son `0x6ca0/0x6ca8` (instantánea de fallos) y `0x17eba` (admisión interna); los 9 usuarios del literal `0x20002bd0` están todos en `0xd098–0xd368` (§3). BIONZ no puede leerla por el canal mss. Señal alternativa: los mensajes esperados por orden (§2), pero **cuál** equivale a «fin» no se ha fijado (falta el emisor Darwin de cada ID) |
| **C** | ¿Se identificaron los receptores BIONZ de los eventos `0x90/0xe0/0xf0`? | **NO** | Los eventos solo se escriben en anillos internos de Darwin (`0x16adc` → `0x20000680`; `0x1e5f2` → anillo de `0x20003bdc+0x58`); el único lector hallado del primero es la copia `0x16bca` de la instantánea de fallos. No hay mensaje que los lleve; el segundo anillo no se ha rastreado hasta el final |
| **D** | ¿Se identificó qué desbloquea una captura en BIONZ? | **SÍ** | Cada paso de la captura es una función `0x438c2xxx` que llama a `caif_recv(sub)` (`0x437db9f0`): **bloquea hasta recibir el siguiente mensaje del buzón y exige que sea el esperado** (§2). Desbloqueo = llegada, en orden, del mensaje de esa subclase. Límite: la correspondencia «mensaje ↔ fin de captura» no está fijada |
| **E** | ¿Se conoce el plazo y la reacción ante timeout? | **SÍ (acotado)** | `caif_recv` espera con `r2 = -1` (`mov.w r2,#-1` en `0x437dba2e`): **sin plazo**; si llega otro mensaje, libera el bloque y devuelve error `-4` (§4). Plazos finitos de BIONZ ligados a la captura: 100×1 tick (`0x438c2826`) y 0x3e8 (`0x438d0ba0`), sin relación demostrada con Darwin. Unidades de `0x5dc0/0x7148`: no determinadas |
| **F** | ¿`[0,7,8,9,10]` produce las condiciones que BIONZ exige? | **NO** | BIONZ exige mensajes (§2), no el bit 24 ni los eventos. Falta el eslabón: qué estado/evento de la máquina de 49 estados dispara el envío de cada ID y si depende de la lista exterior. Compatible con las esperas de Darwin (E24-05a) pero no demostrado frente a BIONZ |
| **G** | ¿Hay condición adicional de posición mecánica? | **NO (no demostrado)** | Sin dependencia hallada en el camino mss. Pero el paso `0xc5` (`0x438c27f0`) sondea hasta 100 veces `0x436e845c`/`0x436e86dc`, que según una variable de modo devuelven un estado interno de captura (`0x436e5710`, `0x43ada048`): su origen físico no se ha resuelto |

## 1. Mapa de transporte Darwin → BIONZ (VERIFICADO por bytes salvo nota)

**Tabla de despacho CAIF de BIONZ.** Índice `0x43c90100` (13 columnas: `[13·clase + subclase]`, usado por `0x436ba44c/0x32c/0x37c/0x3e4`) → filas de 16 B en `0x43fe87f0` `{n, +4, +8, +0xc}`. La clase de la tabla mss de Darwin (`0x27c68`, byte 0 del código) y su subclase (byte 1) indexan esa misma tabla; el ID `0x0c` coincide con el constructor `0x43acabac` (`sp[1]=3`, `sp[2]=1`, longitud `0x16`, traza `0x122`, `bl 0x436ba234`). Las filas con `n=2` son **Darwin→BIONZ** (`+4` = reserva de buffer, `+8` = receptor); las de `n=1` son BIONZ→Darwin (receptor por defecto `0x43acac32`, que solo registra error).

| ID | Dir. | Long. | `(clase,sub)` | Reserva `+4` | Receptor `+8` | Traza |
|---|---|---|---|---|---|---|
| `0x0b` | D→B | 7 | (3,0) | `0x436b8bc4` | `0x436b8c2c` | `0x121` CaptureRequest |
| `0x0c` | B→D | 22 | (3,1) | — | constructor `0x43acabac` | `0x122` CaptureStartRes |
| `0x0d` | D→B | 75 | (3,2) | `0x436b8cb0` | `0x436b8d18` | `0x127` |
| `0x0e` | D→B | 2 | (3,3) | `0x436b8e88` | `0x436b8ef0` | `0x129` ExposureReady |
| `0x0f` | B→D | 2 | (3,4) | — | emisor `0x436b8aec` | `0x12a` ExposureEndNotify |
| `0x10` | D→B | 336 | (3,5) | `0x436b8f74` | `0x436b8fe8` | `0x12e` |
| `0x11` | D→B | 16 | (3,6) | `0x436b9158` | `0x436b91c4` | `0x123` CaptureSettingNotfy |
| `0x12`,`0x13` | B→D | 4, 10 | (3,7),(3,8) | — | emisores `0x436b88e8`, `0x436b8864` | `0x124`, `0x126` |
| `0x14` | D→B | 2 | (3,9) | `0x436b9248` | `0x436b92b0` | `0x125` |
| `0x15` | D→B | 2 | (3,10) | `0x436b8d9c` | `0x436b8e04` | `0x137` |
| `0x16` | B→D | 210 | (3,11) | — | emisor `0x436b88a8` | `0x138` |
| `0x17` | D→B | 6 | (3,12) | `0x436b906c` | `0x436b90d4` | `0x13e` |

Los nombres de traza vienen de la tabla `0x43fe8138` (S54); las longitudes de esa tabla no coinciden siempre con las del ID, así que el nombre es solo una etiqueta del fabricante, no una prueba de contenido.

**Receptor típico** (p. ej. `0x436b8fe8`, ID `0x10`): `0x436b8838` comprueba el buzón de destino `[0x43e77284]`; copia el descriptor de 8 B (cabecera + longitud) al bloque reservado por la función `+4` (variable por ID: `0x43e7726c…0x43e77294`; el bloque recibe la carga a partir de `+8`, tamaño `max(len,10)`); `osal_snd_msg` (`0x4356120c`) lo publica en `[0x43e77284]`; traza. Si no hay buzón/bloque: error `0x2015` y retorno -1. El ID de buzón lo fija la orden `0x20` (`0x436b943c`, abierta por la API `0x43acab62` ← `0x437db980`; cierre `0x21`) a partir del manejador que crea `0x437dbc18`.

Copia estable de los últimos valores: BIONZ **no** conserva una copia: el bloque llega por buzón y se libera tras consumirlo (`0x435612ec`); el último valor existe solo mientras el consumidor no lo libere.

## 2. Consumidores y grafo de espera (VERIFICADO)

`caif_recv` (`0x437db9f0`; REA lo confirma: `FUN_43561260(*piVar3,&local_1c,0xffffffff,…)`): recibe un bloque del buzón con timeout `-1`; comprueba la etiqueta `[bloque-4] == 0x1502c7`; exige `bloque[1]==3` (clase) y `bloque[2]==sub` esperada, y guarda el puntero en la tabla de la fase (`obj+0x4ad8`, `+0x20…+0x3c`). Todo error libera el bloque y devuelve negativo (`-2` sin buzón o etiqueta errónea, `-4` subclase inesperada o fuera de rango, `-5` sin tabla de huecos).

| sub | ID | Hueco | Espera (llamada) | Función de fase |
|---|---|---|---|---|
| 12 | `0x17` | `+0x34` | `0x438d0be4` | `0x438c24bc` (inicio) |
| 2 y 10 | `0x0d`, `0x15` | `+0x24`, `+0x28` | `0x438d06e4` | `0x438c27f0` (fase `0xc5`; luego sondeo ≤100 ticks) |
| 3 | `0x0e` | `+0x2c` | `0x438d08e8` | `0x438c289c` (fase `0xc8`; luego espera de indicadores `0x13`) |
| 5 | `0x10` | `+0x30` | `0x438d0b44` | `0x438c2964` (fase `0xcc/0xcd`) → `0x438407a0(obj, ctx, ID0x0b, ID0x10)` |
| 6 | `0x11` | `+0x38` | `0x438d050c` | `0x438cc56c` |
| 9 | `0x14` | `+0x3c` | `0x438d060c` | `0x438cc7c8`, `0x438ccb0e` |
| 0 | `0x0b` | `+0x20` | dentro de `0x438d025c` | inicio de captura |

`0x438407a0` consume la carga del ID `0x10`: bits de `[+0x17]`, tres `u16` en `+0x18/0x1a/0x1c` y bytes `+0x1e/+0x1f` (copiados a variables de captura; `0x4384085c` según el modo). Ningún campo es la máscara de ocupación. El **orden estricto** (cada espera exige su subclase) es la condición de desbloqueo; no hay tabla de «reintentos».

## 3. Corrección de E24-05a §4.4: el «bloque de estado» es una instantánea del registro de fallos

* `0x6c78` (callback `0x6c79`) está en la lista `0x26d24 = [0x69c3, 0x6c79]`, que invoca `0x6ba4` (`0x6bca…0x6bd6`). `0x6ba4` solo tiene un llamador: **`0x45b2`**, dentro de `0x45a8` (guardado de los 14 registros y llamada; es la entrada de excepción). Las regiones `0x26d2c…` son los registros «KNL/STACK logsize» (`[ERR]KNL logsize`, `[ERR]STACK logsize`, cadenas en `0x6b20–0x6b80`).
* La máscara `0xd294` solo la leen `0x6ca0/0x6ca8` (esa instantánea) y `0x17eba` (admisión del paquete `0x0c`). `0x16bca` (copia del anillo) solo se llama desde `0xcf0e → 0x6ce0` (la misma instantánea).
* Los 17 usuarios del buffer de salida mss `0x200032cc` están en `0x11bde–0x12330` y no referencian la máscara ni las regiones.
* Consecuencia: **E24-05a atribuyó a un mensaje (IDs `0x0d/0x10/0x11`) un contenido (máscara + anillo) que no se transporta**; la coincidencia `0x150` ≈ ID `0x10` era de tamaño. Límite: no se descarta que BIONZ lea RAM de Darwin por otro canal (órdenes de lectura); no se ha encontrado ninguno.

## 4. Tabla de tiempos

| Dónde | Valor | Unidad | Reacción | Estado |
|---|---|---|---|---|
| `caif_recv` | `-1` (`0xffffffff`) | — | sin plazo; subclase errónea → `-4` | VERIFICADO bytes; semántica del 3.er argumento de `0x43561260` = INFERENCIA fuerte (de 80 llamadores: 48 `-1`, 22 `0`, 2 `0x3e8`, 1 `0xf`) |
| Fase `0xc5` (`0x438c2826`) | 100 iteraciones × `0x43560cc8(1)` | tick del SO | registro y continúa | VERIFICADO; unidad del tick NO medida |
| Espera `0x438d0ba0` | `0x3e8` (indicador `0x400000`) | NO determinada | registro | VERIFICADO bytes |
| Darwin: fase `0x16df8/0x16dc0` | variable | tick de Darwin | evento cat 2/`0x30` → operación 5 (E24-05a) | VERIFICADO (E24-05a) |
| Darwin: estados 0/7 | `0x5dc0` / `0x7148` | NO determinada | — | NO determinado; sin relación demostrada con las esperas de BIONZ |

## 5. Matriz comparativa (estática; lo no trazado se marca)

| | Convencional | Compuerta `0x1fe66=0` | Error | Ráfaga |
|---|---|---|---|---|
| Inicio | ID `0x0c` (admitido si máscara = 0) | idéntico | idéntico | `S+0x44.b0=1`: lista `0x28fa8/0x28fca` |
| Lista exterior | `0,2,3,6,9,10`/`0,4,5,6,9,10` | `0,7,8,9,10` | — | idem convencional |
| Máscara/bit 24 | sube al arrancar, baja en estado 9 | idéntico | puede quedar subido si el rearme no termina → rechazo cat 2/`0x51` | idéntico por toma |
| Eventos `0x90/0xe0/0xf0` | anillos de Darwin | idéntico | evento 1 + `S+0x9c` | `0x90` por toma |
| Mensajes a BIONZ | `0x0b,0x0d,0x0e,0x10,0x11,0x14,0x15,0x17` en orden | **no trazado** (emisor Darwin) | **no trazado** | **no trazado** |
| Receptor/espera BIONZ | `caif_recv` por fase (§2) | idéntico (código BIONZ) | espera sin plazo | idéntico |
| Plazos | §4 | §4 | tiempo de fase de Darwin → op. 5 | §4 |
| Operación 5 | solo por `0x17f8c`/`0x16dc0`/orden `0x3e` | idéntico (E24-05a) | sí | idéntico |

**Idéntico entre rutas**: el código de BIONZ (esperas por orden, sin plazo) y los dos sitios de la operación 5. **Cambia** (según E24-05/05a): la lista exterior y los estados que mueven el motor. **No demostrado**: qué mensajes emite Darwin cuando no hay rearme.

## 6. Candidatos descartados y límites

* `0x4379b6ac` (citado en el encargo) no es un receptor CAIF: es el interior de una rutina de configuración por canal (`strb [..+0x33]`, tablas `0x703cc0…`), sin relación con el buzón. Descartado tras desensamblar `0x4379b6ac–0x4379b7ea`.
* `0x12b` ExposureEndRes no es un mensaje de Darwin: `0x436b89e0` publica en la tarea CA un evento interno de tipo `0x12` (dos variables comparadas en `0x436bc1cc`). `0x131` ReleaseLock: ninguna llamada de traza con ese código en `av-cam` (el barrido solo halló las listadas); no se investigó más.
* El emisor de cada ID Darwin→BIONZ en `darwin_core` no está trazado: `0x1239e` se alcanza solo desde el callback `0x12172` (registrado por `0x9924`, `0x123ca`).
* Sin respaldo por REA de las rutinas Thumb sembradas a mano (REA devolvió llamadores incompletos); lo decisivo está verificado con Capstone.
* Ausencia de evidencia no se toma como imposibilidad: el cierre de captura podría depender de los emisores de Darwin aún no leídos.

## 7. Correcciones verificadas

1. E24-05a §4.4 y §9 (INFERENCIA «regiones `0x26d2c` viajan en `0x0d/0x10/0x11`») → **refutada**; es el registro de fallos.
2. E24-05a veredictos C/D: la señal que BIONZ espera no es el bit 24 ni los eventos; son mensajes mss en orden (el mapa queda en §1–§2).
3. Pendiente nuevo E24-05f: emisores de Darwin de los ocho IDs y su disparo en la máquina de 49 estados.
